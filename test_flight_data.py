"""Provide tests for flight_data.py."""
import json
import flight_data as fd
# pylint: disable=invalid-name

MI_FILE_NAME = "./example_files/flight_data/mission_insight.csv"
DATAFLASH_FILE_NAME = "./example_files/flight_data/flight.log"
OUTFILE_NAME = "./example_files/flight_data/flight_data.json"

fd.generate(MI_FILE_NAME, DATAFLASH_FILE_NAME, OUTFILE_NAME)

JSON_OBJS = set(["fType", "basic", "auxiliaryUASOperation", "aircraftFlightPlan", "uasState"])

BASIC = set(["uvin", "gufi", "submitTime", "ussInstanceID", "ussName"])

AUX_OP = set(["flightTestCardName", "testIdentifiers", "typeOfOperation", "takeoffWeight_lb",
              "gcsPosLat_deg", "gcsPosLon_deg", "gcsPosAlt_ft", "takeoffPosLat_deg",
              "takeoffPosLon_deg", "takeoffPosAlt_ft", "takeOffTime", "landingPosLat_deg",
              "landingPosLon_deg", "landingPosAlt_ft", "landingTime"])

AC_FP = set(["wpTime", "wpAlt_ft", "hoverTime_sec", "wpLon_deg", "wpLat_deg",
             "wpSequenceNum_nonDim", "wpType_nonDim", "wpTargetAirSpeed_ftPerSec",
             "wpTargetGroundSpeed_ftPerSec"])

UAS_STATE = set(["vehiclePositionLat_deg", "vehiclePositionLon_deg", "vehiclePositionAlt_ft",
                 "barometricAltitude_ft", "barometricPressure_psi", "altitudeUsedByAutopilot_ft",
                 "aboveTerrainAltitude_ft", "laserSensorAltitude_ft", "opticalSensorAltitude_ft",
                 "imageSensorAltitude_ft", "radarSensorAltitude_ft", "acousticSensorAltitude_ft",
                 "indicatedAirspeed_ftPerSec", "trueAirspeed_ftPerSec", "groundSpeed_ftPerSec",
                 "groundCourse_deg", "hdop_nonDim", "vdop_nonDim", "numGpsSatellitesInView_nonDim",
                 "numGpsSat_nonDim", "roll_deg", "pitch_deg", "yaw_deg", "velNorth_ftPerSec",
                 "velEast_ftPerSec", "velDown_ftPerSec", "rollRate_degPerSec",
                 "pitchRate_degPerSec", "yawRate_degPerSec", "accBodyX_ftPerSec2",
                 "accBodyY_ftPerSec2", "accBodyZ_ftPerSec2", "motor1ControlThrottleCommand_nonDim",
                 "motor2ControlThrottleCommand_nonDim", "motor3ControlThrottleCommand_nonDim",
                 "motor4ControlThrottleCommand_nonDim", "motor5ControlThrottleCommand_nonDim",
                 "motor6ControlThrottleCommand_nonDim", "motor7ControlThrottleCommand_nonDim",
                 "motor8ControlThrottleCommand_nonDim", "motor9ControlThrottleCommand_nonDim",
                 "motor10ControlThrottleCommand_nonDim", "motor11ControlThrottleCommand_nonDim",
                 "motor12ControlThrottleCommand_nonDim", "motor13ControlThrottleCommand_nonDim",
                 "motor14ControlThrottleCommand_nonDim", "motor15ControlThrottleCommand_nonDim",
                 "motor16ControlThrottleCommand_nonDim", "aileronActuatorCommand_nonDim",
                 "elevatorActuatorCommand_nonDim", "rudderActuatorCommand_nonDim",
                 "flapActuatorCommand_nonDim", "landingGearActuatorCommand_nonDim",
                 "batteryVoltage_v", "batteryCurrent_a", "angleOfAttack_deg",
                 "sideSlip_deg", "targetWaypointLat_deg", "targetWaypointLon_deg",
                 "targetWaypointAlt_ft", "aircraftControlMode", "targetGroundSpeed_ftPerSec",
                 "targetAirSpeed_ftPerSec", "aircraftAirborneState_nonDim",
                 "minDistToDefinedAreaLateralBoundary_ft",
                 "minDistToDefinedAreaVerticalBoundary_ft", "c2RssiAircraft_dBm",
                 "c2RssiGcs_dBm", "c2NoiseAircraft_dBm", "c2NoiseGcs_dBm",
                 "c2PacketLossRateAircraftPrct_nonDim", "c2PacketLossRateGcsPrct_nonDim",
                 "lateralNavPositionError_ft", "verticalNavPositionError_ft",
                 "lateralNavVelocityError_ftPerSec", "verticalNavVelocityError_ftPerSec"])

f = open(OUTFILE_NAME, "r")
flight_data = json.load(f)

def test_json_objs():
    """Verify all high-level JSON objects exist in output file."""
    keys = set()
    for key in flight_data:
        keys.add(key)
    assert not bool(keys ^ JSON_OBJS)

def test_basic_vars():
    """Verify all required 'basic' variables are present in output file."""
    keys = set()
    for key in flight_data["basic"]:
        keys.add(key)
    assert not bool(keys ^ BASIC)

def test_aux_vars():
    """Verify all required 'auxiliaryUASOperation' variables are present in output file."""
    keys = set()
    for key in flight_data["auxiliaryUASOperation"]:
        keys.add(key)
    assert not bool(keys ^ AUX_OP)

def test_ac_fp_vars():
    """Verify all required 'aircraftFlightPlan' variables are present in output file."""
    keys = set()
    for key in flight_data["aircraftFlightPlan"][0]:
        keys.add(key)
    assert not bool(keys ^ AC_FP)

def test_uas_state_vars():
    """Verify all required variables are present in output file."""
    keys = set()
    for value in flight_data["uasState"]:
        keys.add(value["sensor"][0])
    print(keys ^ UAS_STATE)
    assert not bool(keys ^ UAS_STATE)
