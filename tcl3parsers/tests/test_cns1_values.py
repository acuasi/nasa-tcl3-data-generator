"""Provides tests for cns1.py values."""
import json
import sys
from tcl3parsers import cns1
PATH = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/tcl3parsers"
sys.path.append(PATH)

MI_FILE_NAME = "./example_files/cns1/mission_insight.csv"
DF_FILE_NAME = "./example_files/cns1/flight.log"
FIELD_VARS_NAME = "./example_files/cns1/field_vars.csv"
OUTFILE_NAME = "./example_files/cns1/cns1_data.json"

cns1.generate(MI_FILE_NAME, DF_FILE_NAME, FIELD_VARS_NAME, OUTFILE_NAME)

JSON_OBJ_STR = set(["fType", "UTM-TCL3-DMP-RevF-CNSPDF"])

JSON_OBJ_DICT = set(["basic", "plannedContingency"])

JSON_OBJ_LISTS = set(["cns1TestType", "contingencyCause", "contingencyResponse",
                      "contingencyLoiterAlt", "contingencyLoiterType",
                      "contingencyLoiterRadius", "contingencyLanding", "maneuverCommand",
                      "timeManeuverCommandSent", "estimatedTimeToVerifyManeuver",
                      "timeManeuverVerification", "primaryLinkDescription",
                      "redundantLinkDescription", "timePrimaryLinkDisconnect",
                      "timeRedundantLinkSwitch"])

BASIC = set(["uvin", "gufi", "submitTime", "ussInstanceID", "ussName"])

PLANNED_CONTIN = {"plannedContingencyLandingPoint_deg": [{"lat": type(1.0), "lon": type(1.0)}],
                  "plannedContingencyLandingPointAlt_ft": [type(1)],
                  "plannedContingencyLoiterAlt_ft": [type(1)],
                  "plannedContingencyLoiterRadius_ft": [type(1)]}
CNS1_TEST_TYPE = set(["ts", "cns1TestType_nonDim"])
CONTIN_CAUSE = set(["ts", "contingencyCause_nonDim"])
CONTIN_RESPONSE = set(["ts", "contingencyResponse_nonDim"])
CONTIN_LOITER_ALT = set(["ts", "contingencyLoiterAlt_ft"])
CONTIN_LOITER_TYPE = set(["ts", "contingencyLoiterType_nonDim"])
CONTIN_LOITER_RAD = set(["ts", "contingencyLoiterRadius_ft"])
CONTIN_LANDING = set(["ts", "contingencyLandingPointAlt_ft", "contingencyLandingPoint_deg"])
MAN_CMD = set(["ts", "maneuverCommand"])
TIME_MAN_CMD_SENT = set(["ts"])
EST_TIME_MAN = set(["ts", "estimatedTimeToVerifyManeuver_sec"])
TIME_MAN_CMD_VERIFY = set(["ts"])
PRIM_LINK = set(["ts", "primaryLinkDescription"])
REDUN_LINK = set(["ts", "redundantLinkDescription"])
TIME_PRIM_LINK_DISCON = set(["ts"])
TIME_REDUN_LINK_SWITCH = set(["ts"])

f = open(OUTFILE_NAME, "r")
cns1_data = json.load(f)

def test_json_objs_str():
    """Check json objects with values of type str."""
    for key in JSON_OBJ_STR:
        assert isinstance(cns1_data[key], str)

def test_json_objs_dict():
    """Check json objects with values of type dict."""
    for key in JSON_OBJ_DICT:
        assert isinstance(cns1_data[key], dict)

def test_json_obj_lists():
    """Check json objects with values of type list."""
    for key in JSON_OBJ_LISTS:
        assert isinstance(cns1_data[key], list)

def test_basic_values():
    """Check that 'basic' object values are of type str."""
    for _, value in cns1_data["basic"].items():
        assert isinstance(value, str)

def test_planned_contin_values():
    """Check that 'plannedContingency' object vavlues of type list."""
    for _, value in cns1_data["plannedContingency"].items():
        assert isinstance(value, (list, type(None)))

def test_timestamps():
    """Check that all timestamp values are of type str."""
    for var in JSON_OBJ_LISTS:
        for item in cns1_data[var]:
            try:
                for key, value in item.items():
                    if key == "ts":
                        assert isinstance(value, str)
            # Catch 'loiter' lists that are of type None
            except AttributeError:
                assert isinstance(item, type(None))

def test_planned_contin():
    """Check values of "plannedContingency" keys."""
    for key, value in cns1_data["plannedContingency"].items():
        if key == "plannedContingencyLandingPoint_deg":
            for k, v in value[0].items():
                assert isinstance(k, str)
                assert isinstance(v, float)
        else:
            assert isinstance(value[0], (float, type(None)))

def test_nonlist_values():
    """Check non-list value types."""
    keys = ["cns1TestType", "contingencyResponse", "contingencyLoiterType",
            "estimatedTimeToVerifyManeuver"]
    for key in keys:
        for item in cns1_data[key]:
            try:
                for k, v in item.items():
                    if k != "ts":
                        assert isinstance(v, (int, float))

            # Catch 'loiter' lists that are of type None
            except AttributeError:
                assert isinstance(item, type(None))

def test_list_values():
    """Check non-list value types."""
    keys = ["contingencyCause", "contingencyLoiterAlt", "contingencyLoiterRadius"]
    for key in keys:
        for item in cns1_data[key]:
            try:
                for k, v in item.items():
                    if k != "ts":
                        assert isinstance(v[0], (int, float))

            # Catch 'loiter' lists that are of type None
            except AttributeError:
                assert isinstance(item, type(None))

def test_str_values():
    """Check non-list value types."""
    keys = ["maneuverCommand", "primaryLinkDescription", "redundantLinkDescription"]
    for key in keys:
        for item in cns1_data[key]:
            try:
                for k, v in item.items():
                    if k != "ts":
                        assert isinstance(v[0], str)

            # Catch 'loiter' lists that are of type None
            except AttributeError:
                assert isinstance(item, type(None))
