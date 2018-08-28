"""Provides tests for con2.py values."""
import json
import sys
import re
from tcl3parsers import con2
PATH = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/tcl3parsers"
sys.path.append(PATH)

MI_FILE_NAME = "./example_files/con2/mission_insight.csv"
DF_FILE_NAME = "./example_files/con2/flight.log"
FIELD_VARS_NAME = "./example_files/con2/field_vars.csv"
OUTFILE_NAME = "./example_files/con2/con2_data.json"

con2.generate(MI_FILE_NAME, DF_FILE_NAME, FIELD_VARS_NAME, OUTFILE_NAME)

JSON_OBJ_STR = set(["fType", "UTM-TCL3-DMP-RevF-CONPDF", "UTM-TCL3-DMP-RevF-CONKML"])

JSON_OBJ_DICT = set(["basic", "plannedContingency"])

JSON_OBJ_LISTS = set(["declaredEmerg", "emergencyInitiationTime", "emergencyCompletionTime",
                      "contingencyCause", "contingencyResponse",
                      "contingencyLanding", "contingencyLoiterType", "contingencyLoiterAlt",
                      "contingencyLoiterRadius"])

BASIC = set(["uvin", "gufi", "submitTime", "ussInstanceID", "ussName"])

PLANNED_CONTIN = {"plannedContingencyLandingPoint_deg": [{"lat": type(1.0), "lon": type(1.0)}],
                  "plannedContingencyLandingPointAlt_ft": [type(1)],
                  "plannedContingencyLoiterAlt_ft": [type(1)],
                  "plannedContingencyLoiterRadius_ft": [type(1)]}

PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z")

f = open(OUTFILE_NAME, "r")
CON2_DATA = json.load(f)

def test_json_objs_str():
    """Check json objects with values of type str."""
    for key in JSON_OBJ_STR:
        assert isinstance(CON2_DATA[key], str)

def test_json_objs_dict():
    """Check json objects with values of type dict."""
    for key in JSON_OBJ_DICT:
        assert isinstance(CON2_DATA[key], dict)

def test_json_obj_lists():
    """Check json objects with values of type list."""
    for key in JSON_OBJ_LISTS:
        assert isinstance(CON2_DATA[key], list)

def test_basic_values():
    """Check that 'basic' object values are of type str."""
    for _, value in CON2_DATA["basic"].items():
        assert isinstance(value, str)

def test_declared_emerg():
    """Check values of "declaredEmerg" object."""
    for item in CON2_DATA["declaredEmerg"]:
        for key, value in item.items():
            if key == "ts":
                assert PATTERN.match(value)
            else:
                assert isinstance(value, str)

def test_emerg_times():
    """Check timestamp formats of emergency times."""
    for item in CON2_DATA["emergencyInitiationTime"]:
        print(item)
        if item:
            assert PATTERN.match(item)
        else:
            assert False
    for item in CON2_DATA["emergencyCompletionTime"]:
        if item:
            assert PATTERN.match(item)
        else:
            assert False

def test_contin_cause_response():
    """Contingency variables values."""
    for item in CON2_DATA["contingencyCause"]:
        for key, value in item.items():
            if key == "ts":
                assert PATTERN.match(value)
            elif key == "contingencyCause_nonDim":
                for i in value:
                    assert isinstance(i, int)
            else:
                assert False

    for item in CON2_DATA["contingencyResponse"]:
        for key, value in item.items():
            if key == "ts":
                assert PATTERN.match(value)
            elif key == "contingencyResponse_nonDim":
                assert isinstance(value, int)
            else:
                assert False

def test_planned_contin():
    """Check values of "plannedContingency" keys."""
    for key, value in CON2_DATA["plannedContingency"].items():
        if key == "plannedContingencyLandingPoint_deg":
            for item in value:
                for k, v in item.items():
                    assert isinstance(k, str)
                    assert isinstance(v, float)
        elif key == "plannedContingencyLandingPointAlt_ft":
            for item in value:
                isinstance(item, float)
        elif key == "plannedContingencyLoiterAlt_ft":
            for item in value:
                isinstance(item, (type(None), float))
        elif key == "plannedContingencyLoiterRadius_ft":
            for item in value:
                isinstance(item, (type(None), float))

def test_contingency_landing():
    """Check "contingencyLanding" values."""
    for item in CON2_DATA["contingencyLanding"]:
        for key, value in item.items():
            print(key)
            if key == "ts":
                assert PATTERN.match(value)
            elif key == "contingencyLandingPoint_deg":
                for i in value:
                    for k, v in i.items():
                        assert isinstance(k, str)
                        assert isinstance(v, float)
            elif key == "contingencyLandingPointAlt_ft":
                for i in value:
                    assert isinstance(i, float)
            else:
                assert False

def test_contingency_loiter_type():
    """Check "contignecyLoiterType" values."""
    for item in CON2_DATA["contingencyLoiterType"]:
        if item:
            for key, value in item.items():
                if key == "ts":
                    assert PATTERN.match(value)
                elif key == "contingencyLoiterType_nonDim":
                    assert isinstance(key, str)
                    assert isinstance(value, int)
        else:
            assert isinstance(item, type(None))

def test_contingency_loiter_alt():
    """Check "contignecyLoiterAlt" values."""
    for item in CON2_DATA["contingencyLoiterAlt"]:
        if item:
            for key, value in item.items():
                if key == "ts":
                    assert PATTERN.match(value)
                elif key == "contingencyLoiterAlt_ft":
                    assert isinstance(key, str)
                    for i in value:
                        assert isinstance(i, float)
        else:
            assert isinstance(item, type(None))

def test_contingency_loiter_radius():
    """Check "contignecyLoiterRadius" values."""
    for item in CON2_DATA["contingencyLoiterRadius"]:
        if item:
            for key, value in item.items():
                if key == "ts":
                    assert PATTERN.match(value)
                elif key == "contingencyLoiterRadius_ft":
                    assert isinstance(key, str)
                    for i in value:
                        assert isinstance(i, float)
        else:
            assert isinstance(item, type(None))
