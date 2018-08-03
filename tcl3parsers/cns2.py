"""Generate CNS2 json file for NASA UTM TCL3."""
import csv
import json
from datetime import datetime
import math

import cns2_structure as cns2

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
    return datetime.utcfromtimestamp(unix_ts).isoformat(timespec="milliseconds")+".000Z"

def parseMissionInsightFile(mi_file_name):
    """Parses the Mission Insight file adds to the cns2 data JSON"""
    with open(mi_file_name, "r") as mission_insight_file:
        mi_reader = csv.DictReader(mission_insight_file)
        for row in mi_reader:
            mi_dict = row
        time = mi_dict["SUBMIT_TIME"]
        date = mi_dict["DATE"]
        cns2.data["basic"]["uvin"] = mi_dict["UVIN"]
        cns2.data["basic"]["gufi"] = mi_dict["OPERATION_GUFI"]
        cns2.data["basic"]["submitTime"] = date + "T" + time
        cns2.data["basic"]["ussInstanceID"] = mi_dict["USS_INSTANCE_ID"]
        cns2.data["basic"]["ussName"] = mi_dict["USS_NAME"]

def emptyFieldIfNull(field):
    """Get rid of the 'None' default value so that data can be appended"""
    cns2.data[field] = [] if cns2.data[field] == [None] else cns2.data[field]

def parseDataFlashFile(dataflash_file_name):
    """Parse arducopter dataflash log file (.log format) and add to cns2 data JSON"""
    radio_count = 0
    arm_flag = 0
    boot_ts_flag = 0
    with open(dataflash_file_name, "r") as dataflash_file:
        gps = {"sys_time": 0, "gps_ms": 0, "gps_wk": 0, "lat": 0, "lon": 0, "alt": 0}
        emptyFieldIfNull('contingencyLanding')
        emptyFieldIfNull('contingencyCause')
        emptyFieldIfNull('contingencyResponse')

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
                cns2.data['plannedContingency']["plannedContingencyLandingPoint_deg"] = cl_point
                cns2.data['plannedContingency']["plannedContingencyLandingPointAlt_ft"] = cl_point_alt

            # 1 Hz
            if row[0] == "RAD":
                # Create 60 second loop for reporting default contingency values
                loopTime = 60
                if radio_count == loopTime - 1:
                    ts = sys_ts_converter(int(row[1]), boot_ts)
                    cns2.data["contingencyLanding"].append({
                        "ts": ts,
                        "contingencyLandingPoint_deg": cl_point,
                        "contingencyLandingPointAlt_ft": cl_point_alt
                    })
                    cns2.data["contingencyCause"].append({
                        "ts": ts,
                        "contingencyCause_nonDim": [0]
                    })
                    cns2.data["contingencyResponse"].append({
                        "ts": ts,
                        "contingencyResponse_nonDim": 0
                    })
                radio_count = (radio_count + 1) % loopTime

def formRadarRecordJSON(ts, uasTruthEcefXCoordinate_ft, uasTruthEcefYCoordinate_ft, uasTruthEcefZCoordinate_ft, estimatedTruthPositionError95Prct_in):
    """Takes parameters and puts them into a JSON"""
    radarRecord = {
        "ts": ts,
        "uasTruthEcefXCoordinate_ft": uasTruthEcefXCoordinate_ft,
        "uasTruthEcefYCoordinate_ft": uasTruthEcefYCoordinate_ft,
        "uasTruthEcefZCoordinate_ft": uasTruthEcefZCoordinate_ft,
        "estimatedTruthPositionError95Prct_in": estimatedTruthPositionError95Prct_in
    }
    return radarRecord

def gps_to_ecef(lat, lon, alt):
    """GPS latitude, longitude, and altitude to Earth Centered Earth Fixed position in feet"""
    rad_lat = lat * (math.pi / 180.0)
    rad_lon = lon * (math.pi / 180.0)

    a = 6378137.0
    finv = 298.257223563
    f = 1 / finv
    e2 = 1 - (1 - f) * (1 - f)
    v = a / math.sqrt(1 - e2 * math.sin(rad_lat) * math.sin(rad_lat))

    x = (v + alt) * math.cos(rad_lat) * math.cos(rad_lon) * M_TO_FT
    y = (v + alt) * math.cos(rad_lat) * math.sin(rad_lon) * M_TO_FT
    z = (v * (1 - e2) + alt) * math.sin(rad_lat) * M_TO_FT

    return x, y, z

def dmsToDD(degreesMinsSeconds):
    """Degrees, Minutes, Seconds to Decimal Degrees"""
    direction = degreesMinsSeconds[-1]
    degreesMinsSeconds = degreesMinsSeconds[:-1]

    degreesMins = degreesMinsSeconds[:degreesMinsSeconds.find('.') - 2]

    seconds = float(degreesMinsSeconds[degreesMinsSeconds.find('.') - 2:])
    mins = int(degreesMins[-2:])
    degrees = int(degreesMins[:-2])

    decDeg = round(degrees + round(mins/60, 4) + round(seconds/3600, 4), 4)

    if direction != 'N' and direction != 'E':
        decDeg *= -1

    return decDeg


def formRadarRecord(radarRecord):
    """Parse an individual record of the radar file and return it as a JSON"""
    ts = radarRecord['Time of Intercept']
    ts = datetime.strptime(ts, '%d %B %Y %H:%M:%S')
    ts = datetime.strftime(ts, '%Y-%m-%dT%H:%M:%S.000Z')

    gpsLatitude = dmsToDD(radarRecord['Latitude'])
    gpsLongitude = dmsToDD(radarRecord['Longitude'])

    gpsAltitude = float(radarRecord['Altitude'].replace('(ft)', '').strip())
    uasTruthEcefXCoordinate_ft, uasTruthEcefYCoordinate_ft, uasTruthEcefZCoordinate_ft = gps_to_ecef(gpsLatitude, gpsLongitude, gpsAltitude)

    # TODO: Is this the estimatedTruthPositionError95Prct_in?
    confidenceLevel = radarRecord['Confidence Level']

    return formRadarRecordJSON(ts, uasTruthEcefXCoordinate_ft, uasTruthEcefYCoordinate_ft, uasTruthEcefZCoordinate_ft, confidenceLevel)

def parseRadarFile(radar_file_name):
    """Parses the radar file and adds uasTruth fields to cns2 data JSON"""

    cns2.data['uasTruth'] = []
    with open(radar_file_name, "r") as radarFile:
        radarRecords = csv.DictReader(radarFile)
        for radarRecord in radarRecords:
            cns2.data['uasTruth'].append(formRadarRecord(radarRecord))

def generate(mi_file_name, dataflash_file_name, field_vars_file_name, radar_file_name, outfile_name):
    """Generate cns2 json file.

    Args:
        mi_file_name            (str): Name of the mission insight file.        [.csv]
        dataflash_file_name     (str): Name of the dataflash log file           [.log]
        field_vars_file_name    (str): Name of the field variables file.(UNUSED)[.csv]
        radar_file_name         (str): Name of the radar file.                  [.csv]
        outfile_name            (str): Name of the output file to be created.   [e.g. 'CNS2.json']

    Returns:
        None
    """

    parseMissionInsightFile(mi_file_name)
    parseDataFlashFile(dataflash_file_name)
    parseRadarFile(radar_file_name)

    outfile = open(outfile_name, "w")
    json.dump(cns2.data, outfile, indent=4)
    outfile.close()
