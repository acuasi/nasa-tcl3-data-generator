"""Provides tests for cns1.py variables."""
import sys
import json
sys.path.append("/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/tcl3parsers")
from tcl3parsers import cns1

MI_FILE_NAME = "./example_files/cns1/mission_insight.csv"
DF_FILE_NAME = "./example_files/cns1/flight.log"
FIELD_VARS_NAME = "./example_files/cns1/field_vars.csv"
OUTFILE_NAME = "./example_files/cns1/cns1_data.json"

cns1.generate(MI_FILE_NAME, DF_FILE_NAME, FIELD_VARS_NAME, OUTFILE_NAME)

JSON_OBJS = set(["fType", "UTM-TCL3-DMP-RevF-CNSPDF", "basic", "plannedContingency",
                 "cns1TestType", "contingencyCause", "contingencyResponse", "contingencyLoiterAlt",
                 "contingencyLoiterType", "contingencyLoiterRadius", "contingencyLanding",
                 "maneuverCommand", "timeManeuverCommandSent", "estimatedTimeToVerifyManeuver",
                 "timeManeuverVerification", "primaryLinkDescription", "redundantLinkDescription",
                 "timePrimaryLinkDisconnect", "timeRedundantLinkSwitch"])

BASIC = set(["uvin", "gufi", "submitTime", "ussInstanceID", "ussName"])

PLANNED_CONTIN = set(["plannedContingencyLandingPoint_deg", "plannedContingencyLandingPointAlt_ft",
                      "plannedContingencyLoiterAlt_ft", "plannedContingencyLoiterRadius_ft"])
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

def test_json_objs():
    """Verify all high-level JSON objects exist in output file."""
    keys = set()
    for key in cns1_data:
        keys.add(key)
    print(keys ^ JSON_OBJS)
    assert not bool(keys ^ JSON_OBJS)

def test_basic_vars():
    """Verify all required 'basic' variables are present in output file."""
    keys = set()
    for key in cns1_data["basic"]:
        keys.add(key)
    assert not bool(keys ^ BASIC)

def test_planned_contin():
    """Verify all required 'plannedContingency' variables are present in output file."""
    keys = set()
    for key in cns1_data["plannedContingency"]:
        keys.add(key)
    print(keys ^ PLANNED_CONTIN)
    assert not bool(keys ^ PLANNED_CONTIN)

def test_cns1_test_type():
    """Verify all required 'cns1TestType' variables are present in output file."""
    keys = set()
    for key in cns1_data["cns1TestType"][0]:
        keys.add(key)
    print(keys ^ CNS1_TEST_TYPE)
    assert not bool(keys ^ CNS1_TEST_TYPE)

def test_contin_cause():
    """Verify all required 'contingencyCause' variables are present in output file."""
    keys = set()
    for key in cns1_data["contingencyCause"][0]:
        keys.add(key)
    print(keys ^ CONTIN_CAUSE)
    assert not bool(keys ^ CONTIN_CAUSE)

def test_contin_response():
    """Verify all required 'contingencyResponse' variables are present in output file."""
    keys = set()
    for key in cns1_data["contingencyResponse"][0]:
        keys.add(key)
    print(keys ^ CONTIN_RESPONSE)
    assert not bool(keys ^ CONTIN_RESPONSE)

# def test_contin_loiter_alt():
#     """Verify all required 'contingencyLoiterAlt' variables are present in output file."""
#     keys = set()
#     for key in cns1_data["contingencyLoiterAlt"][0]:
#         keys.add(key)
#     print(keys ^ CONTIN_LOITER_ALT)
#     assert not bool(keys ^ CONTIN_LOITER_ALT)
#
# def test_contin_loiter_type():
#     """Verify all required 'contingencyLoiterType' variables are present in output file."""
#     keys = set()
#     for key in cns1_data["contingencyLoiterType"][0]:
#         keys.add(key)
#     print(keys ^ CONTIN_LOITER_TYPE)
#     assert not bool(keys ^ CONTIN_LOITER_TYPE)
#
# def test_contin_loiter_rad():
#     """Verify all required 'contingencyLoiterRadius' variables are present in output file."""
#     keys = set()
#     for key in cns1_data["contingencyLoiterRadius"][0]:
#         keys.add(key)
#     print(keys ^ CONTIN_LOITER_RAD)
#     assert not bool(keys ^ CONTIN_LOITER_RAD)

def test_contingency_landing():
    """Verify all required 'contingencyLanding' variables are present in output file."""
    keys = set()
    for key in cns1_data["contingencyLanding"][0]:
        keys.add(key)
    print(keys ^ CONTIN_LANDING)
    assert not bool(keys ^ CONTIN_LANDING)

def test_man_cmd():
    """Verify all required 'maneuverCommand' variables are present in output file."""
    keys = set()
    for key in cns1_data["maneuverCommand"][0]:
        keys.add(key)
    print(keys ^ MAN_CMD)
    assert not bool(keys ^ MAN_CMD)

def test_man_cmd_sent():
    """Verify all required 'timeManeuverCommandSent' variables are present in output file."""
    keys = set()
    for key in cns1_data["timeManeuverCommandSent"][0]:
        keys.add(key)
    print(keys ^ TIME_MAN_CMD_SENT)
    assert not bool(keys ^ TIME_MAN_CMD_SENT)

def test_est_time_man():
    """Verify all required 'estimatedTimeToVerifyManeuver' variables are present in output file."""
    keys = set()
    for key in cns1_data["estimatedTimeToVerifyManeuver"][0]:
        keys.add(key)
    print(keys ^ EST_TIME_MAN)
    assert not bool(keys ^ EST_TIME_MAN)

def test_time_man_cmd_verify():
    """Verify all required 'timeManeuverVerification' variables are present in output file."""
    keys = set()
    for key in cns1_data["timeManeuverVerification"][0]:
        keys.add(key)
    print(keys ^ TIME_MAN_CMD_VERIFY)
    assert not bool(keys ^ TIME_MAN_CMD_VERIFY)

def test_prim_link():
    """Verify all required 'primaryLinkDescription' variables are present in output file."""
    keys = set()
    for key in cns1_data["primaryLinkDescription"][0]:
        keys.add(key)
    print(keys ^ PRIM_LINK)
    assert not bool(keys ^ PRIM_LINK)

def test_redun_link():
    """Verify all required 'redundantLinkDescription' variables are present in output file."""
    keys = set()
    for key in cns1_data["redundantLinkDescription"][0]:
        keys.add(key)
    print(keys ^ REDUN_LINK)
    assert not bool(keys ^ REDUN_LINK)

def test_time_prim_link_discon():
    """Verify all required 'timePrimaryLinkDisconnect' variables are present in output file."""
    keys = set()
    for key in cns1_data["timePrimaryLinkDisconnect"][0]:
        keys.add(key)
    print(keys ^ TIME_PRIM_LINK_DISCON)
    assert not bool(keys ^ TIME_PRIM_LINK_DISCON)

def test_time_redun_link_switch():
    """Verify all required 'timeRedundantLinkSwitch' variables are present in output file."""
    keys = set()
    for key in cns1_data["timeRedundantLinkSwitch"][0]:
        keys.add(key)
    print(keys ^ TIME_REDUN_LINK_SWITCH)
    assert not bool(keys ^ TIME_REDUN_LINK_SWITCH)
