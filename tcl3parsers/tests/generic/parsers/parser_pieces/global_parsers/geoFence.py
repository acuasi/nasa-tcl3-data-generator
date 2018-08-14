import helpers.constants as constants

def geoFence(model, files):
    with open(files["TI_FILE"], "r") as saa2_ti:
        headers = saa2_ti.readline().rstrip().split(",")
        values = saa2_ti.readline().rstrip().split(",")

    geo_fence = {}
    geo_fence_enable = []
    geo_fence_dyn_poly = []
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
            geo_fence[header.replace("_Deg", "_deg")] = float(values[i])
        else:
            geo_fence[header] = int(values[i])

    try:
        with open(files["TD_FILE"], "r") as saa2_td:
            _ = saa2_td.readline()
            # Create structures for json format
            for line in saa2_td:
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
    except FileNotFoundError:
        print("Warning, no Time Dependent Variable File.")

    geo_fence["geoFenceEnable"] = geo_fence_enable
    geo_fence["geoFenceDynamicPolygonPoint"] = geo_fence_dyn_poly if geo_fence_dyn_poly else None
    model["geoFence"] = geo_fence
    return model
