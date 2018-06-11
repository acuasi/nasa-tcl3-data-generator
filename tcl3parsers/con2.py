"""Generate CON2 json file for NASA UTM TCL3."""
import csv
import json
from datetime import datetime

LEAP_SECS = 37
GPS_EPOCH_OFFSET = 315964800
GPS_LEAP_OFFSET = LEAP_SECS - 19

M_TO_FT = 3.28
KTS_TO_FT = 1.68781

def sys_boot_time(sys_time, gps_ms, gps_wks):
    """Use GPS time and system us time to calculate boot start time as a UTC timestamp.

    Args:
        sys_time    (int): System time of Arducopter autopilot in ms.
        gps_ms      (int): GPS time since last week in ms. 
        gps_wks     (int): Number of GPS weeks since epoch.

    Returns:
        boot_ts     (int): Timestamp of system since boot in seconds.
        """    gps_ts = round(gps_ms / 1000 + gps_wks * 86400 * 7)
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
    """    unix_ts = (sys_time / 1.0E6) + boot_ts
    return datetime.utcfromtimestamp(unix_ts).isoformat(timespec="milliseconds")+"Z"

def generate(mi_file_name, df_file_name, field_vars_file_name, outfile_name):
    """Generate con2 json file.
    
    Args:
        mi_file_name            (str): Name of the mission insight file.        [.csv]
        df_file_name            (str): Name of the dataflash log file           [.log]
        field_vars_file_name    (str): Name of the field variables file.        [.csv]
        outfile_name            (str): Name of the output file to be created.   [e.g. 'CNS1.json'] 

    Returns:
        None
    """

    #pylint: disable=too-many-statements
    #pylint: disable=too-many-locals
    #pylint: disable=too-many-branches
    # Set up json objects
    con2_data = {}
    ftype = "CON2"
    pdf = "UTM-ACUASI-CON-2.pdf"
    kml = "UTM-ACUASI-CON-2.kml"
    basic = {}
    declared_emerg = []
    emergency_initiation_time = []
    emergency_completion_time = []
    contin_cause = []
    contin_response = []
    planned_contin = {}
    contin_landing = []
    contin_loiter_type = [None]
    contin_loiter_alt = [None]
    contin_loiter_rad = [None]

    boot_ts_flag = 0
    arm_flag = 0

    gps = {"sys_time": 0, "gps_ms": 0, "gps_wk": 0, "lat": 0, "lon": 0, "alt": 0}

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


    with open(field_vars_file_name, "r") as field_vars_file:
        _ = field_vars_file.readline()
        for line in field_vars_file:
            row = line.split(",")

            if row[0] == "declaredEmergency":
                declared_emerg.append({"ts": row[1], "declaredEmergency": row[2]})

            if row[0] == "emergencyInitiationTime":
                emergency_initiation_time.append(row[1])

            if row[0] == "emergencyCompletionTime":
                emergency_completion_time.append(row[1])

            if row[0] == "contingencyCause":
                causes = row[2].rstrip("\n").split(" ")
                causes_l = []
                for cause in causes:
                    causes_l.append(int(cause))
                contin_cause.append({"ts": row[1], "contingencyCause_nonDim": causes_l})

            if row[0] == "contingencyResponse":
                contin_response.append({"ts": row[1], "contingencyResponse_nonDim": int(row[2])})


    with open(df_file_name, "r") as dataflash_file:
        for line in dataflash_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            if row[0] == "EV":
                if row[2] == "10" or row[2] == "15":
                    arm_flag = 1

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

                if arm_flag:
                    planned_contin["plannedContingencyLandingPoint_deg"] = [{"lat": gps["lat"],
                                                                             "lon": gps["lon"]}]
                    planned_contin["plannedContingencyLandingPointAlt_ft"] = [gps["alt"]]
                    planned_contin["plannedContingencyLoiterAlt_ft"] = [None]
                    planned_contin["plannedContingencyLoiterRadius_ft"] = [None]

            # Check for "landing complete" event ID
            if row[0] == "EV" and row[2] == "18":
                ts = sys_ts_converter(int(row[1]), boot_ts)
                cl = {}
                cl["ts"] = ts
                cl["contingencyLandingPoint_deg"] = [{"lat": gps["lat"], "lon": gps["lon"]}]
                cl["contingencyLandingPointAlt_ft"] = [gps["alt"]]
                contin_landing.append(cl)

    con2_data["fType"] = ftype
    con2_data["basic"] = basic
    con2_data["UTM-TCL3-DMP-RevF-CONPDF"] = pdf
    con2_data["UTM-TCL3-DMP-RevF-CONKML"] = kml
    con2_data["declaredEmerg"] = declared_emerg
    con2_data["emergencyInitiationTime"] = emergency_initiation_time
    con2_data["emergencyCompletionTime"] = emergency_completion_time
    con2_data["contingencyCause"] = contin_cause
    con2_data["contingencyResponse"] = contin_response
    con2_data["plannedContingency"] = planned_contin
    con2_data["contingencyLanding"] = contin_landing
    con2_data["contingencyLoiterType"] = contin_loiter_type
    con2_data["contingencyLoiterAlt"] = contin_loiter_alt
    con2_data["contingencyLoiterRadius"] = contin_loiter_rad

    outfile = open(outfile_name, "w")
    json.dump(con2_data, outfile, indent=4)
    outfile.close()
