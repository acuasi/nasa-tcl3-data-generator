"""Creates FLIGHT_DATA json file from Arducopter Dataflash log file and waypoints file."""
import csv
import json
from datetime import datetime

LEAP_SECS = 37
GPS_EPOCH_OFFSET = 315964800
GPS_LEAP_OFFSET = LEAP_SECS - 19

M_TO_FT = 3.28
CM_TO_FT = 0.328
MM_TO_FT = 0.00328
PA_TO_PSI = 0.000145038

EXT_DATA_PATH = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/tcl3parsers"

## TO-DO:
## aux_op:
##   takeoff and landing, location and time
## determine correct units for velocities

def sys_boot_time(sys_time, gps_ms, gps_wks):
    """Use GPS time and system us time to calculate boot start time as a UTC timestamp.

    Args:
        sys_time    (int): System time of Arducopter autopilot in ms.
        gps_ms      (int): GPS time since last week in ms.
        gps_wks     (int): Number of GPS weeks since epoch.

    Returns:
        boot_ts     (int): Timestamp of system since boot in seconds.
    """

    gps_ts = round(gps_ms / 1000 + gps_wks * 86400 * 7)
    utc_ts = gps_ts + GPS_EPOCH_OFFSET + GPS_LEAP_OFFSET
    sys_ts = sys_time / 1.0E6
    boot_ts = utc_ts - sys_ts
    return boot_ts


def sys_ts_converter(sys_time, boot_ts):
    """Convert system time to UTC ISO8601 timestamp.

    Args:
        sys_time        (int): System time of Arducopter autopilot in ms.
        boot_ts         (int): Timestamp of system since boot in seconds.

    Returns:
        sys_ts          (str): ISO8601 formatted timestamp of current system time.
    """

    unix_ts = (sys_time / 1.0E6) + boot_ts
    return datetime.utcfromtimestamp(unix_ts).isoformat(timespec="milliseconds")+"Z"


def generate(mi_file_name, dataflash_file_name, outfile_name):
    """Generate flight data json file.

    Args:
        mi_file_name            (str): Name of the mission insight file.        [.csv]
        df_file_name            (str): Name of the dataflash log file           [.log]
        outfile_name            (str): Name of the output file to be created.   ['FLIGHT_DATA.json']

    Returns:
        None
    """

    # pylint: disable=too-many-statements
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    pwm_thresh = 1200

    take_off_flag = 0
    boot_ts_flag = 0
    baro_flag = 0

    baro_avg_values = []

    boot_ts = 0

    # Set up data structures
    flight_data = {}
    basic = {}
    aux_op = {}
    ac_flight_plan = []
    waypoint = {}
    uas_state = []
    state_value = {}
    gps = {"sys_time": 0, "gps_ms": 0, "gps_wk": 0, "lat": 0, "lon": 0, "alt": 0}
    baro = {"sys_time": 0, "alt": 0}
    rcout = {"sys_time": 0, "motor1": 0, "motor2": 0, "motor3": 0, "motor4": 0}
    att = {"sys_time": 0, "roll": "0", "pitch": "0", "yaw": "0"}
    nkf1 = {"sys_time": 0, "vel_north": "0", "vel_east": "0", "vel_down": "0"}
    acc1 = {"sys_time": 0, "acc_x": "0", "acc_y": "0", "acc_z": "0"}
    curr = {"sys_time": 0, "voltage": "0", "current": "0"}
    # rate = {"sys_time": 0, "roll_rate": "0", "pitch_rate": "0", "yaw_rate": "0"}
    cmd = {"sys_time": 0, "timestamp": "0", "CTot": "0", "CNum": "0", "CId": "0", "Lat": "0",
           "Lon": "0", "Alt": "0"}
    msg = ""
    mode = ""
    wp_type = ""
    ac_cntrl_mode = {"Stabilize": 0, "AltHold": 0, "Loiter": 0, "Auto": 1, "Avoid_ADSB": 1,
                     "RTL": 1, "Guided": 2, "Land": 1}

    with open(mi_file_name, "r") as mi_file:
        mi_reader = csv.DictReader(mi_file)
        for row in mi_reader:
            mi_dict = row

    with open(EXT_DATA_PATH + "/external_data/aircraft-specs.json", "r") as ac_specs:
        ac_specs_dict = json.load(ac_specs)

    with open(EXT_DATA_PATH + "/external_data/gcs-locations.json", "r") as gcs_locs:
        gcs_locs_dict = json.load(gcs_locs)

    # Get aircraft N number from mi_dict and use that to get take-off weight from
    # aircraft specs file
    takeoff_weight = float(ac_specs_dict[mi_dict["VEHICLE_DESIGNATION"]]["weight_lbs"])
    num_motors = ac_specs_dict[mi_dict["VEHICLE_DESIGNATION"]]["num_motors"]
    type_of_operation = "Live"

    basic["uvin"] = mi_dict["UVIN"]
    basic["gufi"] = mi_dict["OPERATION_GUFI"]
    basic["submitTime"] = mi_dict["DATE"] + "T" + mi_dict["SUBMIT_TIME"]
    basic["ussInstanceID"] = mi_dict["USS_INSTANCE_ID"]
    basic["ussName"] = mi_dict["USS_NAME"]

    aux_op["flightTestCardName"] = mi_dict["test_card"]
    aux_op["testIdentifiers"] = [mi_dict["test_identifiers"]]
    aux_op["typeOfOperation"] = type_of_operation
    aux_op["takeoffWeight_lb"] = float(takeoff_weight)
    aux_op["gcsPosLat_deg"] = float(gcs_locs_dict[mi_dict["gcs_location"]]["latitude"])
    aux_op["gcsPosLon_deg"] = float(gcs_locs_dict[mi_dict["gcs_location"]]["longitude"])
    aux_op["gcsPosAlt_ft"] = float(gcs_locs_dict[mi_dict["gcs_location"]]["altitude"])


    with open(dataflash_file_name, "r") as dataflash_file:
        for line in dataflash_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            # 5 Hz
            if row[0] == "GPS":
                gps["sys_time"] = int(row[1])
                gps["gps_ms"] = int(row[3])
                gps["gps_wk"] = int(row[4])
                gps["lat"] = float(row[7])
                gps["lon"] = float(row[8])
                gps["alt"] = float(row[9])
                gps["speed"] = float(row[10]) # m/s
                gps["ground_course"] = float(row[11])
                gps["hdop"] = float(row[6])
                gps["num_sats"] = int(row[5])

                # Check for valid GPS position and time and then calculate timestamp of system boot
                if float(row[7]) != 0 and \
                   float(row[8]) != 0 and \
                   float(row[1]) != 0 and \
                    boot_ts_flag == 0:
                    boot_ts = sys_boot_time(int(gps["sys_time"]), int(gps["gps_ms"]),
                                            int(gps["gps_wk"]))
                    boot_ts_flag = 1

                if boot_ts_flag:
                    timestamp = sys_ts_converter(int(gps["sys_time"]), boot_ts)
                    sensor = ["vehiclePositionLat_deg"]
                    value = [gps["lat"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["vehiclePositionLon_deg"]
                    value = [gps["lon"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["vehiclePositionAlt_ft"]
                    value = [gps["alt"] * M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["groundSpeed_ftPerSec"]
                    value = [gps["speed"] * M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["groundCourse_deg"]
                    value = [gps["ground_course"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["hdop_nonDim"]
                    value = [gps["hdop"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["vdop_nonDim"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["numGpsSatellitesInView_nonDim"]
                    value = [gps["num_sats"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["numGpsSat_nonDim"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

            # 1 Hz
            if row[0] == "RAD":
                if boot_ts_flag:
                    sys_time = int(row[1])
                    timestamp = sys_ts_converter(sys_time, boot_ts)
                    sensor = ["c2RssiGcs_dBm"]
                    value = [(float(row[2]) / 1.9) - 127]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["c2RssiAircraft_dBm"]
                    value = [(float(row[3]) / 1.9) - 127]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["c2NoiseGcs_dBm"]
                    value = [(float(row[5]) / 1.9) - 127]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["c2NoiseAircraft_dBm"]
                    value = [(float(row[6]) / 1.9) - 127]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["c2PacketLossRateGcsPrct_nonDim"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["c2PacketLossRateAircraftPrct_nonDim"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

                    if take_off_flag:
                        sensor = ["aircraftAirborneState_nonDim"]
                        value = [1]
                    else:
                        sensor = ["aircraftAirborneState_nonDim"]
                        value = [0]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

                    # Write empty strings for parameters we can't provide values for
                    # Use current timestamp in state_value
                    sensor = ["indicatedAirspeed_ftPerSec"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["trueAirspeed_ftPerSec"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["groundSpeed_ftPerSec"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

                    for i in range(num_motors, 16):
                        sensor = ["motor" + str(i + 1) + "ControlThrottleCommand_nonDim"]
                        value = None
                        state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                        uas_state.append(state_value)

                    sensor = ["aileronActuatorCommand_nonDim"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["elevatorActuatorCommand_nonDim"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["rudderActuatorCommand_nonDim"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["flapActuatorCommand_nonDim"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["landingGearActuatorCommand_nonDim"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["angleOfAttack_deg"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["sideSlip_deg"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["targetGroundSpeed_ftPerSec"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["targetAirSpeed_ftPerSec"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["minDistToDefinedAreaLateralBoundary_ft"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["minDistToDefinedAreaVerticalBoundary_ft"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["lateralNavPositionError_ft"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["verticalNavPositionError_ft"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["lateralNavVelocityError_ftPerSec"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["verticalNavVelocityError_ftPerSec"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["radarSensorAltitude_ft"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["acousticSensorAltitude_ft"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)


            if row[0] == "BARO":
                baro["sys_time"] = int(row[1])
                baro["alt"] = float(row[2])
                baro["pressure"] = float(row[3]) #Pascals

                # Average first 10 barometer altitude values
                if len(baro_avg_values) <= 10:
                    baro_avg_values.append(float(row[2]))
                if len(baro_avg_values) > 10 and baro_flag == 0:
                    baro_avg = sum(i for i in baro_avg_values)/10.0
                    baro_flag = 1

                if boot_ts_flag:
                    state_value["ts"] = sys_ts_converter(int(baro["sys_time"]), boot_ts)
                    sensor = ["barometricAltitude_ft"]
                    value = [baro["alt"] * M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["barometricPressure_psi"]
                    value = [baro["pressure"] * PA_TO_PSI]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["altitudeUsedByAutopilot_ft"]
                    value = [baro["alt"] * M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["aboveTerrainAltitude_ft"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["laserSensorAltitude_ft"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["opticalSensorAltitude_ft"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["imageSensorAltitude_ft"]
                    value = None
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

            if row[0] == "RCOU":
                rcout["sys_time"] = row[1]
                for i in range(num_motors):
                    rcout["motor" + str(i+1)] = int(row[i+2])

                if boot_ts_flag:
                    state_value["ts"] = sys_ts_converter(int(rcout["sys_time"]), boot_ts)
                    for i in range(num_motors):
                        sensor = ["motor" + str(i+1) + "ControlThrottleCommand_nonDim"]
                        value = [rcout["motor" + str(i+1)]]
                        state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                        uas_state.append(state_value)

            if row[0] == "ATT":
                att["sys_time"] = int(row[1])
                att["roll"] = float(row[3])
                att["pitch"] = float(row[5])
                att["yaw"] = float(row[7])

                if boot_ts_flag:
                    state_value["ts"] = sys_ts_converter(float(att["sys_time"]), boot_ts)
                    sensor = ["roll_deg"]
                    value = [att["roll"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["pitch_deg"]
                    value = [att["pitch"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["yaw_deg"]
                    value = [att["yaw"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

            if row[0] == "NKF1":
                nkf1["sys_time"] = int(row[1])
                nkf1["vel_north"] = float(row[5])
                nkf1["vel_east"] = float(row[6])
                nkf1["vel_down"] = float(row[7])

                if boot_ts_flag:
                    state_value["ts"] = sys_ts_converter(float(nkf1["sys_time"]), boot_ts)
                    sensor = ["velNorth_ftPerSec"]
                    value = [float(nkf1["vel_north"]) * M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["velEast_ftPerSec"]
                    value = [float(nkf1["vel_east"]) * M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["velDown_ftPerSec"]
                    value = [float(nkf1["vel_down"]) * M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

            if row[0] == "CURR":
                curr["sys_time"] = int(row[1])
                curr["voltage"] = float(row[2])
                curr["current"] = float(row[3])

                if boot_ts_flag:
                    state_value["ts"] = sys_ts_converter(float(curr["sys_time"]), boot_ts)
                    sensor = ["batteryVoltage_v"]
                    value = [curr["voltage"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["batteryCurrent_a"]
                    value = [curr["current"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

            if row[0] == "RATE":
                if boot_ts_flag:
                    state_value["ts"] = sys_ts_converter(float(row[1]), boot_ts)
                    sensor = ["rollRate_degPerSec"]
                    value = [float(row[4])]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["pitchRate_degPerSec"]
                    value = [float(row[7])]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["yawRate_degPerSec"]
                    value = [float(row[10])]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

            if row[0] == "IMU":
                nkf1["sys_time"] = row[1]
                nkf1["acc_x"] = row[5]
                nkf1["acc_y"] = row[6]
                nkf1["acc_z"] = row[7]

                if boot_ts_flag:
                    timestamp = sys_ts_converter(float(acc1["sys_time"]), boot_ts)
                    sensor = ["accBodyX_ftPerSec2"]
                    value = [float(acc1["acc_x"]) * M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["accBodyY_ftPerSec2"]
                    value = [float(acc1["acc_y"]) * M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["accBodyZ_ftPerSec2"]
                    value = [float(acc1["acc_z"]) * M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

            if row[0] == "MSG":
                msg = row[2]

            if row[0] == "CMD":
                if msg != "New mission":
                    cmd["sys_time"] = int(row[1])
                    cmd["CTot"] = int(row[2])
                    cmd["CNum"] = int(row[3])
                    cmd["CId"] = int(row[4])
                    cmd["Lat"] = float(row[9])
                    cmd["Lon"] = float(row[10])
                    cmd["Alt"] = float(row[11])* M_TO_FT

                    # UAS State values
                    timestamp = sys_ts_converter(int(cmd["sys_time"]), boot_ts)
                    sensor = ["targetWaypointLat_deg"]
                    value = [cmd["Lat"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["targetWaypointLon_deg"]
                    value = [cmd["Lon"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["targetWaypointAlt_ft"]
                    value = [cmd["Alt"]]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)

                    # aicraftFlightPlan values
                    if cmd["CId"] == 16:
                        wp_type = 1
                    if cmd["CId"] == 82:
                        wp_type = 0
                    waypoint = {"wpTime": timestamp, "wpAlt_ft": cmd["Alt"], "hoverTime_sec": 0,
                                "wpLon_deg": cmd["Lon"], "wpLat_deg": cmd["Lat"],
                                "wpSequenceNum_nonDim": cmd["CNum"], "wpType_nonDim": wp_type,
                                "wpTargetAirSpeed_ftPerSec": None,
                                "wpTargetGroundSpeed_ftPerSec": None}
                    ac_flight_plan.append(waypoint)

            if row[0] == "MODE":
                if boot_ts_flag:
                    mode = row[2]
                    timestamp = sys_ts_converter(float(row[1]), boot_ts)
                    sensor = ["aircraftControlMode"]
                    try:
                        value = ac_cntrl_mode[mode]
                        state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                        uas_state.append(state_value)
                    except KeyError:
                        pass

            # Check for significant increase in barometer alt value
            # and motors spinning up
            if len(baro_avg_values) > 10 and baro_flag:
                if (baro["alt"] - baro_avg) > 1.5 \
                and rcout["motor1"] > pwm_thresh \
                and take_off_flag == 0:
                    take_off_flag = 1
                    aux_op["takeoffPosLat_deg"] = float(gps["lat"])
                    aux_op["takeoffPosLon_deg"] = float(gps["lon"])
                    aux_op["takeoffPosAlt_ft"] = float(gps["alt"])
                    takeoff_time = sys_ts_converter(int(baro["sys_time"]), boot_ts)
                    aux_op["takeOffTime"] = takeoff_time

            # Check for "landing complete" event ID
            if row[0] == "EV" and row[2] == "18":
                aux_op["landingPosLat_deg"] = float(gps["lat"])
                aux_op["landingPosLon_deg"] = float(gps["lon"])
                aux_op["landingPosAlt_ft"] = float(gps["alt"])
                landing_time = sys_ts_converter(int(baro["sys_time"]), boot_ts)
                aux_op["landingTime"] = landing_time

    # If no waypoints were used for flight, populate with "None"
    if not ac_flight_plan:
        ac_flight_plan.append(None)

    # Build highest-level JSON structure
    flight_data = {"fType": "FLIGHT_DATA", "basic": basic, "auxiliaryUASOperation": aux_op,
                   "aircraftFlightPlan": ac_flight_plan, "uasState": uas_state}

    f_d = open(outfile_name, "w")
    json.dump(flight_data, f_d, indent=4)


if __name__ == "__main":
    STD_PATH = "/home/samuel/SpiderOak Hive/ACUASI/NASA TO6/Data Management/"

    MI_FILE_NAME = "./example_files/mission_insight.csv"
    DATAFLASH_FILE_NAME = STD_PATH + "Example Log Files/SAA2 Flights April 5/flight.log"
    OUTFILE_NAME = "flight_data.json"
    generate(MI_FILE_NAME, DATAFLASH_FILE_NAME, OUTFILE_NAME)
