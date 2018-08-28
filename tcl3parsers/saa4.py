"""Generate SAA4 json file for NASA UTM TCL3."""
import csv
import json
from datetime import datetime

M_TO_FT = 3.28
KTS_TO_FT_PER_SEC = 1.68781

def lat_lon_converter(lat, lon):
    """Convert lat and lon from radar degrees minutes decimal seconds string to a decimal degrees
    float value.

    Args:
        lat (string): The latitude in the format '1475131.986W'
        lon (string): The longitude in the format '645117.514N'

    Returns:
        location (tuple, float): The converted values in the format (64.8412343, -147.7432143)
    """
    lat_dir = lat[-1]
    lon_dir = lon[-1]
    lat = lat[:-1]
    lon = lon[:-1]
    lat_dd = round(float(lat[0:2]) + float(lat[2:4])/60 + float(lat[4:])/3600, 7)
    lon_dd = round(float(lon[0:3]) + float(lon[3:5])/60 + float(lon[5:])/3600, 7)

    if lat_dir == "S":
        lat_dd = lat_dd * -1
    if lon_dir == "W":
        lon_dd = lon_dd * -1

    return lat_dd, lon_dd

def generate(mi_file_name, saa4_ti_name, saa4_td_name, radar_file_name, outfile_name):
    """Generate saa4 json file.

    Args:
        mi_file_name            (str): Name of the mission insight file.                    [.csv]
        saa4_ti_name            (str): Name of the time independent field variables file    [.log]
        saa4_td_name            (str): Name of the time dependent field variables file      [.log]
        radar_file_name         (str): Name of the radar file.                              [.csv]
        outfile_name            (str): Name of the output file to be created.               [e.g. 'SAA4.json']

    Returns:
        None
    """

    #pylint: disable=too-many-statements
    #pylint: disable=too-many-locals
    #pylint: disable=too-many-branches
    saa4_data = {}
    basic = {}
    geo_fence = {}
    geo_fence_enable = []
    geo_fence_dyn_poly = None
    intruder = {}

    ftype = "SAA4"

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

    with open(saa4_ti_name, "r") as saa4_ti:
        headers = saa4_ti.readline().rstrip().split(",")
        values = saa4_ti.readline().rstrip().split(",")

    for i, header in enumerate(headers):
        if header == "geoFenceMinAltitude":
            geo_fence[header + "_ft"] = round(float(values[i]) * M_TO_FT)
        elif header == "geoFenceMaxAltitude":
            geo_fence[header + "_ft"] = round(float(values[i]) * M_TO_FT)
        elif header == "geoFenceCircularRadius":
            geo_fence[header + "_ft"] = round(float(values[i]) * M_TO_FT)
        elif header == "geoFenceStartTime" or header == "geoFenceEndTime":
            geo_fence[header] = [values[i]]
        elif header.startswith("geoFenceCircularPoint"):
            geo_fence[header] = float(values[i])
        else:
            geo_fence[header] = int(values[i])

    with open(saa4_td_name, "r") as saa4_td:
        _ = saa4_td.readline()
        # Create structures for json format
        for line in saa4_td:
            row = line.rstrip().split(",")
            variable = row[0]
            timestamp = row[1]
            value = row[2]
            if variable == "geoFenceEnable":
                geo_fence_value = {"ts": timestamp, "geoFenceEnable_nonDim": int(value)}
                geo_fence_enable.append(geo_fence_value)
            if variable == "geoFenceDynamicPolygonPoint":
                polygon = []
                # Parse out lat, lon values
                locs = value.replace("(", "").replace(")", "").split(":")
                for i in range(0, len(locs), 2):
                    point = {"lat": float(locs[i]), "lon": float(locs[i+1])}
                    polygon.append(point)
                geofence_polygon = {"ts": timestamp, "geoFenceDynamicPolygonPoint_deg": polygon}
                geo_fence_dyn_poly.append(geofence_polygon)

    with open(radar_file_name, "r") as radar_file:
        headers = radar_file.readline().split(",")
        for line in radar_file:
            # Split by commas and strip leading and trailing whitespaces
            row = ([item.strip() for item in line.split(",")])
            if (row[headers.index("Label")] == "T-362" or
                    row[headers.index("Label")] == "T-189" and
                    float(row[headers.index("Confidence Level")]) > 60.0):

                dt_string = row[headers.index("Time of Intercept")]
                ts = datetime.strptime(dt_string, "%d %B %Y %H:%M:%S").isoformat() + "Z"
                lat_string = row[headers.index("Latitude")]
                lon_string = row[headers.index("Longitude")]
                lat, lon = lat_lon_converter(lat_string, lon_string)
                alt = float(row[headers.index("Altitude")])
                speed = float(row[headers.index("Speed")]) * KTS_TO_FT_PER_SEC
                intruder = {"ts": ts, "intruderPositionLat_deg": lat,
                            "intruderPositionLon_deg": lon, "intruderPositionAlt_ft": alt,
                            "intruderGroundSpeed_ftPerSec": speed,
                            "intruderVelNorth_ftPerSec": None, "intruderVelEast_ftPerSec": None,
                            "intruderVelDown_ftPerSec": None, "intruderGroundCourse_deg": None}
                break



    geo_fence["geoFenceEnable"] = geo_fence_enable
    geo_fence["geoFenceDynamicPolygonPoint"] = geo_fence_dyn_poly

    saa4_data["fType"] = ftype
    saa4_data["basic"] = basic
    saa4_data["geoFence"] = geo_fence
    saa4_data["typeOfSaaSensor"] = "Radar"
    saa4_data["intruder"] = intruder
    saa4_data["relativeHeadingAtFirstDetection_deg"] = None # Need value
    saa4_data["azimuthSensorMin_deg"] = -60
    saa4_data["azimuthSensorMax_deg"] = 60
    saa4_data["elevationSensorMin_deg"] = -40
    saa4_data["elevationSensorMax_deg"] = 40
    saa4_data["saaSensorMinSlantRange_ft"] = 10 * M_TO_FT
    saa4_data["saaSensorMaxSlantRange_ft"] = 3400 * M_TO_FT
    saa4_data["minRcsOfSensor_ft2"] = 10**(-20/10) * M_TO_FT
    saa4_data["maxRcsOfSensor_ft2"] = 10**(30/10) * M_TO_FT
    saa4_data["updateRateSensor_hz"] = 5
    saa4_data["saaSensorAzimuthAccuracy_deg"] = 1
    saa4_data["saaSensorAltitudeAccuracy_ft"] = None
    saa4_data["horRangeAccuracy_ft"] = None
    saa4_data["verRangeAccuracy_ft"] = None
    saa4_data["slantRangeAccuracy_ft"] = 3.25 * M_TO_FT
    saa4_data["timeToTrack_sec"] = 1.000
    saa4_data["probabilityFalseAlarmPrct_nonDim"] = None
    saa4_data["probabilityIntruderDetectionPrct_nonDim"] = None
    saa4_data["targetTrackCapacity_nonDim"] = 20
    saa4_data["dataPacketRatio_nonDim"] = None # V2V so N/A
    saa4_data["transmissionDelay_sec"] = None # V2V so N/A
    saa4_data["numberOfLostTracks_nonDim"] = None
    saa4_data["intruderRadarCrossSection_ft2"] = 0.158
    saa4_data["txRadioFrequencyPower_w"] = 538.9

    outfile = open(outfile_name, "w")
    json.dump(saa4_data, outfile, indent=4)
    outfile.close()
