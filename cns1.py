"""Generate CNS1 json file for NASA UTM TCL3."""
import csv
import json
from datetime import datetime

LEAP_SECS = 37
GPS_EPOCH_OFFSET = 315964800
GPS_LEAP_OFFSET = LEAP_SECS - 19

M_TO_FT = 3.28
CM_TO_FT = 0.328
MM_TO_FT = 0.00328
PA_TO_PSI = 0.000145038


def sys_boot_time(sys_time, gps_ms, gps_wks):
    """Use GPS time and system us time to calculate boot start time as a UTC timestamp."""
    gps_ts = round(gps_ms / 1000 + gps_wks * 86400 * 7)
    utc_ts = gps_ts + GPS_EPOCH_OFFSET + GPS_LEAP_OFFSET
    sys_ts = sys_time / 1.0E6
    boot_ts = utc_ts - sys_ts
    return boot_ts

def sys_ts_converter(sys_time, boot_ts):
    """Convert system time to UTC ISO8601 timestamp."""
    unix_ts = (sys_time / 1.0E6) + boot_ts
    return datetime.utcfromtimestamp(unix_ts).isoformat(timespec="milliseconds")+"Z"

def generate(mi_file_name, dataflash_file_name):
    """Generate cns1 json file for NASA TCL3 TO6 flights."""
    #pylint: disable=too-many-statements
    #pylint: disable=too-many-locals
    cns1_data = {}
    basic = {}
    planned_contingency = {}
    cns1_test_type = []
    contingency_cause = []
    contingency_response = []
    contingency_loiter_alt = []
    contingency_loiter_type = []
    contingency_loiter_radius = []
    contingency_landing = []
    manuever_command = []
    time_maneuver_command_sent = []
    estimated_time_to_verify_maneuver = []
    time_manuever_verification = []
    primary_link_description = []
    redundant_link_description = []
    time_primary_link_disconnect = []
    time_redundant_link_switch = []

    gps = {"sys_time": 0, "gps_ms": 0, "gps_wk": 0, "lat": 0, "lon": 0, "alt": 0}

    arm_flag = 0
    boot_ts_flag = 0

    ftype = "SAA2"

    with open(mi_file_name, "r") as mi_file:
        mi_reader = csv.DictReader(mi_file)
        for row in mi_reader:
            mi_dict = row

    time = mi_dict["SUBMIT_TIME"]
    date = mi_dict["DATE"]
    basic["uvin"] = mi_dict["UVIN"]
    basic["gufi"] = mi_dict["OPERATION_GUFI"]
    basic["submitTime"] = date + "T" + time
    basic["ussInstanceID"] = mi_dict["USS_INSTANCE_ID"]
    basic["ussName"] = mi_dict["USS_NAME"]

    with open(dataflash_file_name, "r") as dataflash_file:
        for line in dataflash_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            if row[0] == "EV":
                if row[2] == "10" or row[2] == "15":
                    arm_flag = 1

            # 5 Hz
            if row[0] == "GPS":
                gps["sys_time"] = row[1]
                gps["gps_ms"] = row[3]
                gps["gps_wk"] = row[4]
                gps["lat"] = row[7]
                gps["lon"] = row[8]
                gps["alt"] = float(row[9])
                gps["speed"] = float(row[10]) # m/s
                gps["ground_course"] = row[11]
                gps["hdop"] = row[6]
                gps["num_sats"] = row[5]

                # Check for valid GPS position and time and then calculate timestamp of system boot
                if float(row[7]) != 0 and \
                   float(row[8]) != 0 and \
                   float(row[1]) != 0 and \
                    boot_ts_flag == 0:
                    boot_ts = sys_boot_time(int(gps["sys_time"]), int(gps["gps_ms"]),
                                            int(gps["gps_wk"]))
                    boot_ts_flag = 1

            if arm_flag and boot_ts_flag:
                cl_point = "[{},{}]".format(gps["lat"], gps["lon"])
                cl_point_alt = "[{}]".format(str(float(gps["alt"]) * M_TO_FT))
                planned_contingency["plannedContingencyLandingPoint_deg"] = cl_point
                planned_contingency["plannedContingencyLandingPointAlt_ft"] = cl_point_alt
                planned_contingency["plannedContingencyLoiterAlt_ft"] = ""
                planned_contingency["plannedContingencyLoiterRadius_ft"] = ""

            # 1 Hz
            if row[0] == "RAD":
                ts = sys_ts_converter(int(row[1]), boot_ts)
                cl = {"ts": ts, "contingencyLandingPoint_deg": cl_point,
                      "contingencyLandingPointAlt_ft": cl_point_alt}
                contingency_landing.append(cl)
