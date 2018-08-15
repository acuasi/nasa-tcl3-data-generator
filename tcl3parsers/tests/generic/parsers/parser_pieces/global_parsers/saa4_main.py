from datetime import datetime
import helpers.constants as constants
import helpers.system_helpers as system_helpers

def saa4_main(model, files):
    geo_fence = {}
    with open(files["TI_FILE"], "r") as saa4_ti:
        headers = saa4_ti.readline().rstrip().split(",")
        values = saa4_ti.readline().rstrip().split(",")

    for i, header in enumerate(headers):
        if header == "geoFenceMinAltitude":
            geo_fence[header + "_ft"] = round(float(values[i]) * constants.M_TO_FT)
        elif header == "geoFenceMaxAltitude":
            geo_fence[header + "_ft"] = round(float(values[i]) * constants.M_TO_FT)
        elif header == "geoFenceCircularRadius":
            geo_fence[header + "_ft"] = round(float(values[i]) * constants.M_TO_FT)
        elif header == "geoFenceStartTime" or header == "geoFenceEndTime":
            geo_fence[header] = [values[i]]
        elif header.startswith("geoFenceCircularPoint"):
            geo_fence[header] = float(values[i])
        else:
            geo_fence[header] = int(values[i])

    geo_fence_enable = []
    geo_fence_dyn_poly = []
    with open(files["TD_FILE"], "r") as saa4_td:
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

    with open(files["RADAR_FILE"], "r") as radar_file:
        headers = radar_file.readline().split(",")
        for line in radar_file:
            # Split by commas and strip leading and trailing whitespaces
            row = ([item.strip() for item in line.split(",")])
            if (row[headers.index("Label")] == "T-362" or
                    row[headers.index("Label")] == "T-189" and
                    float(row[headers.index("Confidence Level")]) > 60.0):

                dt_string = row[headers.index("Time of Intercept")]
                ts = datetime.strptime(dt_string, "%d %B %Y %H:%M:%S").isoformat() + ".000Z"
                lat_string = row[headers.index("Latitude")]
                lon_string = row[headers.index("Longitude")]
                lat, lon = system_helpers.lat_lon_converter(lat_string, lon_string)
                alt = float(row[headers.index("Altitude")])
                speed = float(row[headers.index("Speed")]) * constants.KTS_TO_FT
                intruder = {"ts": ts, "intruderPositionLat_deg": lat,
                            "intruderPositionLon_deg": lon, "intruderPositionAlt_ft": alt,
                            "intruderGroundSpeed_ftPerSec": speed}
                break



    geo_fence["geoFenceEnable"] = geo_fence_enable
    geo_fence["geoFenceDynamicPolygonPoint"] = geo_fence_dyn_poly

    model["geoFence"] = geo_fence
    model["typeOfSaaSensor"] = "Radar"
    model["intruder"].update(intruder)
    for intruderKey in model["intruder"].keys():
        if model["intruder"][intruderKey] == 0:
            model["intruder"][intruderKey] = None
    model["relativeHeadingAtFirstDetection_deg"] = None # Need value
    model["azimuthSensorMin_deg"] = -60
    model["azimuthSensorMax_deg"] = 60
    model["elevationSensorMin_deg"] = -40
    model["elevationSensorMax_deg"] = 40
    model["saaSensorMinSlantRange_ft"] = 10 * constants.M_TO_FT
    model["saaSensorMaxSlantRange_ft"] = 3400 * constants.M_TO_FT
    model["minRcsOfSensor_ft2"] = 10**(-20/10) * constants.M_TO_FT
    model["maxRcsOfSensor_ft2"] = 10**(30/10) * constants.M_TO_FT
    model["updateRateSensor_hz"] = 5
    model["saaSensorAzimuthAccuracy_deg"] = 1
    model["saaSensorAltitudeAccuracy_ft"] = None
    model["horRangeAccuracy_ft"] = None
    model["verRangeAccuracy_ft"] = None
    model["slantRangeAccuracy_ft"] = 3.25 * constants.M_TO_FT
    model["timeToTrack_sec"] = 1.000
    model["probabilityFalseAlarmPrct_nonDim"] = None
    model["probabilityIntruderDetectionPrct_nonDim"] = None
    model["targetTrackCapacity_nonDim"] = 20
    model["dataPacketRatio_nonDim"] = None # V2V so N/A
    model["transmissionDelay_sec"] = None # V2V so N/A
    model["numberOfLostTracks_nonDim"] = None
    model["intruderRadarCrossSection_ft2"] = 0.158
    model["txRadioFrequencyPower_w"] = 538.9

    return model
