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

def generate(mi_file_name, field_vars_file_name, outfile_name):
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
        field_vars = json.load(field_vars_file)

    con2_data["fType"] = ftype
    con2_data["basic"] = basic
    con2_data["UTM-TCL3-DMP-RevF-CONPDF"] = pdf
    con2_data["UTM-TCL3-DMP-RevF-CONKML"] = kml

    for key in field_vars:
        con2_data[key] = field_vars[key]

    outfile = open(outfile_name, "w")
    json.dump(con2_data, outfile, indent=4)
    outfile.close()
