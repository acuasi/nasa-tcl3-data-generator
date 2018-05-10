"""Provides tests for con1.py values."""
import json
import sys
import re
from tcl3parsers import con1
PATH = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/tcl3parsers"
sys.path.append(PATH)

MI_FILE_NAME = "./example_files/con1/mission_insight.csv"
DF_FILE_NAME = "./example_files/con1/flight.log"
FIELD_VARS_NAME = "./example_files/con1/field_vars.csv"
WEATHER_FILE_NAME = "./example_files/con1/weather_file.csv"
OUTFILE_NAME = "./example_files/con1/con1_data.json"

con1.generate(MI_FILE_NAME, DF_FILE_NAME, WEATHER_FILE_NAME, FIELD_VARS_NAME, OUTFILE_NAME)

JSON_OBJ_STR = set(["fType", "UTM-TCL3-DMP-RevF-CONPDF"])

JSON_OBJ_DICT = set(["basic"])

JSON_OBJ_LISTS = set(["plannedBvlosLandingPoint_deg", "actualBvlosLandingPoint", "landingOffset_ft",
                      "bvlosLandingZoneSize_ft", "bvlosLandingZoneStructure_deg",
                      "bvlosLandingZonePeople_deg", "wxBvlosLandingZone", "c2", "c2PacketLoss"])

BASIC = set(["uvin", "gufi", "submitTime", "ussInstanceID", "ussName"])

PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z")

f = open(OUTFILE_NAME, "r")
CON1_DATA = json.load(f)

def test_json_objs_str():
    """Check json objects with values of type str."""
    for key in JSON_OBJ_STR:
        assert isinstance(CON1_DATA[key], str)

def test_json_objs_dict():
    """Check json objects with values of type dict."""
    for key in JSON_OBJ_DICT:
        assert isinstance(CON1_DATA[key], dict)

def test_basic_values():
    """Check that 'basic' object values are of type str."""
    for _, value in CON1_DATA["basic"].items():
        assert isinstance(value, str)

def test_list_floats():
    """Check that lists with floast have correct value types."""
    values = ["plannedBvlosLandingPointAlt_ft", "landingOffset_ft", "bvlosLandingZoneSize_ft"]
    for value in values:
        for item in CON1_DATA[value]:
            assert isinstance(item, float)

def test_actual_bvlos_landing():
    """Check values for "actualBvlosLandingPoint"."""
    for item in CON1_DATA["actualBvlosLandingPoint"]:
        for key, value in item.items():
            if key == "ts":
                assert PATTERN.match(value)
            elif key == "actualBvlosLandingPoint_deg":
                for i in value:
                    for k, v in i.items():
                        assert isinstance(k, str)
                        assert isinstance(v, float)
            elif key == "actualBvlosLandingPointAlt_ft":
                for i in value:
                    assert isinstance(i, float)
            else:
                assert False

def test_floats():
    """Check values for variables with float values."""
    variables = ["alongTrackDistanceFlown_ft", "distanceFromLaunchSite_ft"]
    for variable in variables:
        assert isinstance(CON1_DATA[variable], float)

def test_bvlos_zone():
    """Check values of "bvlosLandingZoneStructure_deg" and "bvlosLandingZonePeople_deg"."""
    variable = CON1_DATA["bvlosLandingZoneStructure_deg"]
    if variable:
        for item in variable:
            for key, value in item.items():
                assert isinstance(key, str)
                assert isinstance(value, float)

    variable = CON1_DATA["bvlosLandingZonePeople_deg"]
    if variable:
        for item in variable:
            for key, value in item.items():
                assert isinstance(key, str)
                assert isinstance(value, float)

def test_landing_zone_weather():
    """Check values of "wxBvlosLandingZone"."""
    variable = CON1_DATA["wxBvlosLandingZone"]
    for item in variable:
        for key, value in item.items():
            if key == "ts":
                assert PATTERN.match(value)
            elif (key == "wxBvlosLandingZone1Data" or key == "wxBvlosLandingZone2Data" or
                  key == "wxBvlosLandingZone3Data"):
                for k, v in value.items():
                    assert isinstance(k, str)
                    assert isinstance(v, float)
            else:
                assert False

def test_c2():
    """Check values of "c2"."""
    variable = CON1_DATA["c2"]
    for item in variable:
        for key, value in item.items():
            if key == "ts":
                assert PATTERN.match(value)
            elif (key == "c2RssiAircraft_dBm" or key == "c2RssiGcs_dBm" or
                  key == "c2NoiseAircraft_dBm" or key == "c2NoiseGcs_dBm"):
                assert isinstance(value, float)
            else:
                assert False

def test_c2_packet_loss():
    """Check values of "c2PacketLoss"."""
    variable = CON1_DATA["c2PacketLoss"]
    for item in variable:
        for key, value in item.items():
            if key == "ts":
                assert PATTERN.match(value)
            elif (key == "c2PacketLossRateAircraftPrct_nonDim" or
                  key == "c2PacketLossRateGcsPrct_nonDim"):
                assert isinstance(value, type(None))
            else:
                assert False
