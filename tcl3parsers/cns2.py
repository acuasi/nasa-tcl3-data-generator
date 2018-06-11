"""Generate CNS2 json file for NASA UTM TCL3."""
import sys
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
    """Use GPS time and system us time to calculate boot start time as a UTC timestamp.

    Args:
        sys_time    (int): System time of Arducopter autopilot in ms.
        gps_ms      (int): GPS time since last week in ms. 
        gps_wks     (int): Number of GPS weeks since epoch.

    Returns:
        boot_ts     (int): Timestamp of system since boot in seconds.
        """
    gps_ts = round(gps_ms / 1000 + gps_wks * 86400 * 7)
    utc_ts = gps_ts + GPS_EPOCH_OFFSET + GPS_LEAP_OFFSET
    sys_ts = sys_time / 1.0E6
    boot_ts = utc_ts - sys_ts
    return boot_ts

def sys_ts_converter(sys_time, boot_ts):
    """Convert system time to UTC ISO8601 timestamp.
    
    Args:
        sys_time        (int): System time of Arducopter autopilot in ms.
        boot_ts         (int): Timestamp of system since boot in seconds.

    Returns:
        sys_ts          (str): ISO8601 formatted timestamp of current system time.
    """
    unix_ts = (sys_time / 1.0E6) + boot_ts
    return datetime.utcfromtimestamp(unix_ts).isoformat(timespec="milliseconds")+"Z"

def generate(mi_file_name, dataflash_file_name, field_vars_file_name, radar_file_name, outfile_name):
    """Generate cns2 json file.
    
    Args:
        mi_file_name            (str): Name of the mission insight file.        [.csv]
        dataflash_file_name     (str): Name of the dataflash log file           [.log]
        field_vars_file_name    (str): Name of the field variables file.        [.csv]
        radar_file_name         (str): Name of the radar file.                  [.csv]
        outfile_name            (str): Name of the output file to be created.   [e.g. 'CNS1.json'] 

    Returns:
        None
    """
    #pylint: disable=too-many-statements
    #pylint: disable=too-many-locals
    #pylint: disable=too-many-branches
    cns2_data = {}
    basic = {}
    planned_contingency = {}
    cns2_test_type = []
    contingency_cause = []
    contingency_response = []
    contingency_loiter_alt = None
    contingency_loiter_type = None
    contingency_loiter_radius = None
    contingency_landing = []
    maneuver_command = []
    time_maneuver_command_sent = []
    est_time_verify_maneuver = []
    time_manuever_verification = []
    primary_link_description = []
    redundant_link_description = []
    time_primary_link_disconnect = []
    time_redundant_link_switch = []
    ac_mode = ""
    ac_link = "Primary"

    radio_count = 0

    gps = {"sys_time": 0, "gps_ms": 0, "gps_wk": 0, "lat": 0, "lon": 0, "alt": 0}

    arm_flag = 0
    boot_ts_flag = 0

    ftype = "CNS2"
    pdf = "UTM-ACUASI-CNS-2.pdf"

    # Generate dictionary with mission insight headers and values
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

    # Parse field variables file
    with open(field_vars_file_name, "r") as field_vars_file:
        _ = field_vars_file.readline()
        for line in field_vars_file:
            row = [item.strip() for item in line.split(",")]

            if row[0] == "contingencyCause_nonDim":
                variable = "contingencyCause_nonDim"
                value = int(row[1])
                if value:
                    ts = row[2]
                    contingency_cause.append({"ts": ts, variable: [value]})

            elif row[0] == "contingencyResponse_nonDim":
                variable = "contingencyResponse_nonDim"
                value = int(row[1])
                if value:
                    ts = row[2]
                    contingency_response.append({"ts": ts, variable: value})

            elif row[0] == "cns1TestType_nonDim":
                variable = "cns1TestType_nonDim"
                value = int(row[1])
                ts = row[2]
                cns2_test_type.append({"ts": ts, variable: value})

            elif row[0] == "PrimaryLink":
                PRIMARY = LINK[row[1]].strip()

            elif row[0] == "SecondaryLink":
                REDUN = LINK[row[1]].strip()

            elif row[0] == "timeManeuverCommandSent":
                variable = "timeManeuverCommandSent"
                ts = row[2]
                time_maneuver_command_sent.append({"ts": ts})
                if ac_link == "Primary":
                    primary_link_description.append({"ts": ts, "primaryLinkDescription": PRIMARY})
                    maneuver_command.append({"ts": ts, "maneuverCommand": PRIM_CMD})
                    value = {"ts": ts, "estimatedTimeToVerifyManeuver_sec": 1.500}
                    est_time_verify_maneuver.append(value)
                elif ac_link == "Redundant":
                    redundant_link_description.append({"ts": ts, "redundantLinkDescription": REDUN})
                    maneuver_command.append({"ts": ts, "maneuverCommand": REDUN_CMD})
                    value = {"ts": ts, "estimatedTimeToVerifyManeuver_sec": 0.250}
                    est_time_verify_maneuver.append(value)

            elif row[0] == "timePrimaryLinkDisconnect":
                variable = "timePrimaryLinkDisconnect"
                ts = row[2]
                time_primary_link_disconnect.append({"ts": ts})

            elif row[0] == "timeRedundantLinkSwitch":
                if ac_link == "Primary":
                    variable = "timeRedundantLinkSwitch"
                    ts = row[2]
                    time_redundant_link_switch.append({"ts": ts})
                    ac_link = "Redundant"
                else:
                    print("ERROR: Invalid link logic.")
                    sys.exit(0)

            else:
                print("ERROR: Invalid variable.")
                sys.exit(0)

    # Parse arducopter dataflash log file (.log format)
    with open(dataflash_file_name, "r") as dataflash_file:
        for line in dataflash_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            if row[0] == "EV":
                if row[2] == "10" or row[2] == "15":
                    arm_flag = 1

            # 5 Hz
            if row[0] == "GPS":
                gps["sys_time"] = int(row[1])
                gps["gps_ms"] = int(row[3])
                gps["gps_wk"] = int(row[4])
                gps["lat"] = float(row[7])
                gps["lon"] = float(row[8])
                gps["alt"] = float(row[9])
                gps["speed"] = float(row[10]) # m/s
                gps["ground_course"] = float(row[11])
                gps["hdop"] = float(row[6])
                gps["num_sats"] = int(row[5])

                # Check for valid GPS position and time and then calculate timestamp of system boot
                if float(row[7]) != 0 and \
                   float(row[8]) != 0 and \
                   float(row[1]) != 0 and \
                    boot_ts_flag == 0:
                    boot_ts = sys_boot_time(int(gps["sys_time"]), int(gps["gps_ms"]),
                                            int(gps["gps_wk"]))
                    boot_ts_flag = 1

            if arm_flag and boot_ts_flag:
                cl_point = [{"lat": gps["lat"], "lon": gps["lon"]}]
                cl_point_alt = [gps["alt"]]
                # cl_point = "[{},{}]".format(gps["lat"], gps["lon"])
                # cl_point_alt = "[{}]".format(float(gps["alt"]) * M_TO_FT)
                planned_contingency["plannedContingencyLandingPoint_deg"] = cl_point
                planned_contingency["plannedContingencyLandingPointAlt_ft"] = cl_point_alt
                planned_contingency["plannedContingencyLoiterAlt_ft"] = None
                planned_contingency["plannedContingencyLoiterRadius_ft"] = None

            # 1 Hz
            if row[0] == "RAD":
                # Create 60 second loop for reporting default contingency values
                if radio_count > 59:
                    ts = sys_ts_converter(int(row[1]), boot_ts)
                    cl = {"ts": ts, "contingencyLandingPoint_deg": cl_point,
                          "contingencyLandingPointAlt_ft": cl_point_alt}
                    contingency_landing.append(cl)
                    contingency_cause.append({"ts": ts, "contingencyCause_nonDim": [0]})
                    contingency_response.append({"ts": ts, "contingencyResponse_nonDim": 0})
                    radio_count = 0

                radio_count += 1

            if row[0] == "MODE":
                if ac_mode == "Loiter" or ac_mode == "Stabilize":
                    if row[2] == "Auto":
                        ts = sys_ts_converter(int(row[1]), boot_ts)
                        time_manuever_verification.append({"ts": ts})

                if ac_mode == "RTL" or ac_mode == "Auto":
                    if row[2] == "Guided":
                        ts = sys_ts_converter(int(row[1]), boot_ts)
                        time_manuever_verification.append({"ts": ts})
                ac_mode = row[2]

    # PARSE RADAR FILE
    # TO BE WRITTEN
    # Calculate UAS truth object from radar data
    # E.g.
        #   "uasTruth": [
        # {
        #   "ts": "2018-03-24T00:47:02.814Z",
        #   "uasTruthEcefXCoordinate_ft": 13782808.4,
        #   "uasTruthEcefYCoordinate_ft": 565813.648,
        #   "uasTruthEcefZCoordinate_ft": 15682742.78,
        #   "estimatedTruthPositionError95Prct_in": 9.13
        # },

    # Build cns2 json data structure
    cns2_data["fType"] = ftype
    cns2_data["UTM-TCL3-DMP-RevF-CNSPDF"] = pdf
    cns2_data["basic"] = basic
    cns2_data["plannedContingency"] = planned_contingency
    cns2_data["cns2TestType"] = cns2_test_type
    cns2_data["contingencyCause"] = contingency_cause
    cns2_data["contingencyResponse"] = contingency_response
    cns2_data["contingencyLoiterAlt"] = contingency_loiter_alt
    cns2_data["contingencyLoiterType"] = contingency_loiter_type
    cns2_data["contingencyLoiterRadius"] = contingency_loiter_radius
    cns2_data["contingencyLanding"] = contingency_landing
    cns2_data["maneuverCommand"] = maneuver_command
    cns2_data["timeManeuverCommandSent"] = time_maneuver_command_sent
    cns2_data["estimatedTimeToVerifyManeuver"] = est_time_verify_maneuver
    cns2_data["timeManeuverVerification"] = time_manuever_verification
    cns2_data["primaryLinkDescription"] = primary_link_description
    cns2_data["redundantLinkDescription"] = redundant_link_description
    cns2_data["timePrimaryLinkDisconnect"] = time_primary_link_disconnect
    cns2_data["timeRedundantLinkSwitch"] = time_redundant_link_switch

    outfile = open(outfile_name, "w")
    json.dump(cns2_data, outfile, indent=4)
    outfile.close()
