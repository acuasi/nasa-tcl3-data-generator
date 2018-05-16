"""Generate SAA2 json file for NASA UTM TCL3."""
import sys
import csv
import json

M_TO_FT = 3.28

def generate(mi_file_name, saa2_ti_name, saa2_td_name, outfile_name):
    """Generate saa2 json file for NASA TCL3 TO6 flights."""
    #pylint: disable=too-many-statements
    #pylint: disable=too-many-locals
    #pylint: disable=too-many-branches
    saa2_data = {}
    basic = {}
    geo_fence = {}
    geo_fence_enable = []
    geo_fence_dyn_poly = None

    ftype = "SAA2"

    try:
        with open(mi_file_name, "r") as mi_file:
            mi_reader = csv.DictReader(mi_file)
            for row in mi_reader:
                mi_dict = row
    except FileNotFoundError:
        print("Error: No Time Independent File!")
        sys.exit(1)

    time = mi_dict["SUBMIT_TIME"]
    date = mi_dict["DATE"]
    basic["uvin"] = mi_dict["UVIN"]
    basic["gufi"] = mi_dict["OPERATION_GUFI"]
    basic["submitTime"] = date + "T" + time
    basic["ussInstanceID"] = mi_dict["USS_INSTANCE_ID"]
    basic["ussName"] = mi_dict["USS_NAME"]

    with open(saa2_ti_name, "r") as saa2_ti:
        headers = saa2_ti.readline().rstrip().split(",")
        values = saa2_ti.readline().rstrip().split(",")

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

    try:
        with open(saa2_td_name, "r") as saa2_td:
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
    geo_fence["geoFenceDynamicPolygonPoint"] = geo_fence_dyn_poly

    saa2_data["fType"] = ftype
    saa2_data["basic"] = basic
    saa2_data["geoFence"] = geo_fence

    outfile = open(outfile_name, "w")
    json.dump(saa2_data, outfile, indent=4)
    outfile.close()

if __name__ == "__main__":
    STD_PATH = "/home/samuel/SpiderOak Hive/ACUASI/NASA TO6/Data Management/"
    MI_FILE_NAME = "./Example_Files/mission_insight.csv"
    SAA2_TI_NAME = "./Example_Files/saa2-field-values-ti.csv"
    SAA2_TD_NAME = "./Example_Files/saa2-field-values-td.csv"
    OUTFILE_NAME = "saa2_data.json"
    generate(MI_FILE_NAME, SAA2_TI_NAME, SAA2_TD_NAME, OUTFILE_NAME)
