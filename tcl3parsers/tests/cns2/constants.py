"""Declares constants used in CNS1 testing"""

import sys
import os
TCL3PARSERS_PATH = os.path.dirname(os.path.realpath("../"))
sys.path.append(TCL3PARSERS_PATH)

MI_FILE_NAME = TCL3PARSERS_PATH + "/tests/example_files/cns2/mission_insight.csv"
DF_FILE_NAME = TCL3PARSERS_PATH + "/tests/example_files/cns2/flight.log"
FIELD_VARS_NAME = TCL3PARSERS_PATH + "/tests/example_files/cns2/field_vars.csv"
# RADAR_FILE_NAME = TCL3PARSERS_PATH + "/tests/example_files/cns2/radar_file.csv"
OUTFILE_NAME = TCL3PARSERS_PATH + "/tests/example_files/cns2/cns2_data.json"
#
# # Constants used in value_tests
# JSON_OBJ_STR = set([
#     "fType",
#     "UTM-TCL3-DMP-RevF-CNSPDF"
# ])
#
# JSON_OBJ_DICT = set([
#     "basic",
#     "plannedContingency"
# ])
#
# JSON_OBJ_LISTS = set([
#     "cns1TestType",
#     "contingencyCause",
#     "contingencyResponse",
#     "contingencyLanding",
#     "maneuverCommand",
#     "timeManeuverCommandSent",
#     "estimatedTimeToVerifyManeuver",
#     "timeManeuverVerification",
#     "primaryLinkDescription",
#     "redundantLinkDescription",
#     "timePrimaryLinkDisconnect",
#     "timeRedundantLinkSwitch"
# ])
#
# BASIC = set([
#     "uvin",
#     "gufi",
#     "submitTime",
#     "ussInstanceID",
#     "ussName"
# ])
#
# PLANNED_CONTIN = {
#     "plannedContingencyLandingPoint_deg": [
#         {
#             "lat": type(1.0),
#             "lon": type(1.0)
#         }
#     ],
#     "plannedContingencyLandingPointAlt_ft": [type(1)],
#     "plannedContingencyLoiterAlt_ft": [type(1)],
#     "plannedContingencyLoiterRadius_ft": [type(1)]
# }
#
# CNS1_TEST_TYPE = set([
#     "ts",
#     "cns1TestType_nonDim"
# ])
#
# CONTIN_CAUSE = set([
#     "ts",
#     "contingencyCause_nonDim"
# ])
#
# CONTIN_RESPONSE = set([
#     "ts",
#     "contingencyResponse_nonDim"
# ])
#
# CONTIN_LOITER_ALT = set([
#     "ts",
#     "contingencyLoiterAlt_ft"
# ])
#
# CONTIN_LOITER_TYPE = set([
#     "ts",
#     "contingencyLoiterType_nonDim"
# ])
#
# CONTIN_LOITER_RAD = set([
#     "ts",
#     "contingencyLoiterRadius_ft"
# ])
#
# CONTIN_LANDING = set([
#     "ts",
#     "contingencyLandingPointAlt_ft",
#     "contingencyLandingPoint_deg"
# ])
#
# MAN_CMD = set([
#     "ts",
#     "maneuverCommand"
# ])
#
# TIME_MAN_CMD_SENT = set([
#     "ts"
# ])
#
# EST_TIME_MAN = set([
#     "ts",
#     "estimatedTimeToVerifyManeuver_sec"
# ])
#
# TIME_MAN_CMD_VERIFY = set([
#     "ts"
# ])
#
# PRIM_LINK = set([
#     "ts",
#     "primaryLinkDescription"
# ])
#
# REDUN_LINK = set([
#     "ts", "redundantLinkDescription"
# ])
#
# TIME_PRIM_LINK_DISCON = set([
#     "ts"
# ])
#
# TIME_REDUN_LINK_SWITCH = set([
#     "ts"
# ])
#
# # Constants used in variable_tests
# JSON_OBJS = set([
#     "fType",
#     "UTM-TCL3-DMP-RevF-CNSPDF",
#     "basic",
#     "plannedContingency",
#     "cns1TestType",
#     "contingencyCause",
#     "contingencyResponse",
#     "contingencyLoiterAlt",
#     "contingencyLoiterType",
#     "contingencyLoiterRadius",
#     "contingencyLanding",
#     "maneuverCommand",
#     "timeManeuverCommandSent",
#     "estimatedTimeToVerifyManeuver",
#     "timeManeuverVerification",
#     "primaryLinkDescription",
#     "redundantLinkDescription",
#     "timePrimaryLinkDisconnect",
#     "timeRedundantLinkSwitch"
# ])
#
# PLANNED_CONTIN_KEYS = set(PLANNED_CONTIN.keys())
