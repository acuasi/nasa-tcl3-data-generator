"""Provides tests for saa2.py."""
import json
import saa2

STD_PATH = "/home/samuel/SpiderOak Hive/ACUASI/NASA TO6/Data Management/"
MI_FILE_NAME = "./example_files/mission_insight.csv"
SAA2_TI_NAME = "./example_files/saa2-field-values-ti.csv"
SAA2_TD_NAME = "./example_files/saa2-field-values-td.csv"
OUTFILE_NAME = "saa2_data.json"

saa2.generate(MI_FILE_NAME, SAA2_TI_NAME, SAA2_TD_NAME, OUTFILE_NAME)

JSON_OBJS = set(["fType", "basic", "geoFence"])

BASIC = set(["uvin", "gufi", "submitTime", "ussInstanceID", "ussName"])

GEOFENCE = set(["geoFenceAvailable_nonDim", "geoFenceStartTime", "geoFenceEndTime",
                "geoFenceType_nonDim", "geoFenceMinAltitude_ft", "geoFenceMaxAltitude_ft",
                "geoFenceCircularPointLat_deg", "geoFenceCircularPointLon_deg",
                "geoFenceCircularRadius_ft", "geoFenceEnable", "geoFenceDynamicPolygonPoint"])

f = open(OUTFILE_NAME, "r")
saa2_data = json.load(f)

def test_json_objs():
    """Verify all high-level JSON objects exist in output file."""
    keys = set()
    for key in saa2_data:
        keys.add(key)
    assert not bool(keys ^ JSON_OBJS)

def test_basic_vars():
    """Verify all required 'basic' variables are present in output file."""
    keys = set()
    for key in saa2_data["basic"]:
        keys.add(key)
    assert not bool(keys ^ BASIC)

def test_geofence_vars():
    """Verify all required 'geofence' variables are present in output file."""
    keys = set()
    for key in saa2_data["geoFence"]:
        keys.add(key)
    print(keys ^ GEOFENCE)
    assert not bool(keys ^ GEOFENCE)
