import csv
import json
import os
from pathlib import Path
import helpers.system_helpers as system_helpers
import helpers.constants as constants

def flight_data_ardu(model, files):
    """Global parser for generating flight_data, primarily from the dataflash file"""
    with open(files["MI_FILE"], "r") as mi_file:
        mi_reader = csv.DictReader(mi_file)
        for row in mi_reader:
            mi_dict = row

    aircraft_specs_file = os.path.join(Path(__file__).parents[5], "external_data/aircraft-specs.json")

    with open(aircraft_specs_file, "r") as ac_specs:
        ac_specs_dict = json.load(ac_specs)

    num_motors = ac_specs_dict[mi_dict["VEHICLE_DESIGNATION"]]["num_motors"]
    pwm_thresh = 1200

    take_off_flag = 0
    boot_ts_flag = 0
    baro_flag = 0

    baro_avg_values = []

    boot_ts = 0

    # Set up data structures
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
    cmd = {"sys_time": 0, "timestamp": "0", "CTot": "0", "CNum": "0", "CId": "0", "Lat": "0",
           "Lon": "0", "Alt": "0"}
    msg = ""
    mode = ""
    wp_type = ""
    ac_cntrl_mode = {"Stabilize": 0, "AltHold": 0, "Loiter": 0, "Auto": 1, "Avoid_ADSB": 1,
                     "RTL": 1, "Guided": 2, "Land": 1}

    with open(files["DF_FILE"], "r") as dataflash_file:
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
                    boot_ts = system_helpers.sys_boot_time(int(gps["sys_time"]), int(gps["gps_ms"]),
                                                           int(gps["gps_wk"]))
                    boot_ts_flag = 1

                if boot_ts_flag:
                    timestamp = system_helpers.sys_ts_converter(int(gps["sys_time"]), boot_ts)
                    sensors = list(set([
                        "vehiclePositionLat_deg",
                        "vehiclePositionLon_deg",
                        "vehiclePositionAlt_ft",
                        "groundSpeed_ftPerSec",
                        "groundCourse_deg",
                        "hdop_nonDim",
                        "vdop_nonDim",
                        "numGpsSatellitesInView_nonDim",
                        "numGpsSat_nonDim"
                    ]))

                    for sensor in sensors:
                        if sensor == "vehiclePositionLat_deg":
                            value = [gps["lat"]]
                        elif sensor == "vehiclePositionLon_deg":
                            value = [gps["lon"]]
                        elif sensor == "vehiclePositionAlt_ft":
                            value = [gps["alt"] * constants.M_TO_FT]
                        elif sensor == "groundSpeed_ftPerSec":
                            value = [gps["speed"] * constants.M_TO_FT]
                        elif sensor == "groundCourse_deg":
                            value = [gps["ground_course"]]
                        elif sensor == "hdop_nonDim":
                            value = [gps["hdop"]]
                        elif sensor == "numGpsSatellitesInView_nonDim":
                            value = [gps["num_sats"]]
                        else:
                            value = None

                        state_value = {"ts": timestamp, "sensor": [sensor], "value": value}
                        uas_state.append(state_value)

            # 1 Hz
            if row[0] == "RAD":
                if boot_ts_flag:
                    sys_time = int(row[1])
                    timestamp = system_helpers.sys_ts_converter(sys_time, boot_ts)

                    sensors = list(set([
                        "c2RssiGcs_dBm",
                        "c2RssiAircraft_dBm",
                        "c2NoiseGcs_dBm",
                        "c2NoiseAircraft_dBm",
                        "c2PacketLossRateGcsPrct_nonDim",
                        "c2PacketLossRateAircraftPrct_nonDim",
                        "aircraftAirborneState_nonDim",
                        "indicatedAirspeed_ftPerSec",
                        "trueAirspeed_ftPerSec",
                        "groundSpeed_ftPerSec",
                        "aileronActuatorCommand_nonDim",
                        "elevatorActuatorCommand_nonDim",
                        "rudderActuatorCommand_nonDim",
                        "flapActuatorCommand_nonDim",
                        "landingGearActuatorCommand_nonDim",
                        "angleOfAttack_deg",
                        "sideSlip_deg",
                        "targetGroundSpeed_ftPerSec",
                        "targetAirSpeed_ftPerSec",
                        "minDistToDefinedAreaLateralBoundary_ft",
                        "minDistToDefinedAreaVerticalBoundary_ft",
                        "lateralNavPositionError_ft",
                        "verticalNavPositionError_ft",
                        "lateralNavVelocityError_ftPerSec",
                        "verticalNavVelocityError_ftPerSec",
                        "radarSensorAltitude_ft",
                        "acousticSensorAltitude_ft"
                    ]))

                    for i in range(num_motors, 16):
                        sensors.append("motor" + str(i + 1) + "ControlThrottleCommand_nonDim")

                    for sensor in sensors:
                        if sensor == "c2RssiGcs_dBm":
                            value = [(float(row[2]) / 1.9) - 127]
                        elif sensor == "c2RssiAircraft_dBm":
                            value = [(float(row[3]) / 1.9) - 127]
                        elif sensor == "c2NoiseGcs_dBm":
                            value = [(float(row[5]) / 1.9) - 127]
                        elif sensor == "c2NoiseAircraft_dBm":
                            value = [(float(row[6]) / 1.9) - 127]
                        elif sensor == "aircraftAirborneState_nonDim":
                            value = [1] if take_off_flag else [0]
                        else:
                            value = None

                        state_value = {"ts": timestamp, "sensor": [sensor], "value": value}
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
                    sys_time = int(baro["sys_time"])
                    timestamp = system_helpers.sys_ts_converter(sys_time, boot_ts)

                    sensors = list(set([
                        "barometricAltitude_ft",
                        "barometricPressure_psi",
                        "altitudeUsedByAutopilot_ft",
                        "aboveTerrainAltitude_ft",
                        "laserSensorAltitude_ft",
                        "opticalSensorAltitude_ft",
                        "imageSensorAltitude_ft"
                    ]))

                    for sensor in sensors:
                        if sensor == "barometricAltitude_ft":
                            value = [baro["alt"] * constants.M_TO_FT]
                        elif sensor == "barometricPressure_psi":
                            value = [baro["pressure"] * constants.PA_TO_PSI]
                        elif sensor == "altitudeUsedByAutopilot_ft":
                            value = [baro["alt"] * constants.M_TO_FT]
                        else:
                            value = None

                        state_value = {"ts": timestamp, "sensor": [sensor], "value": value}
                        uas_state.append(state_value)

            if row[0] == "RCOU":
                rcout["sys_time"] = row[1]
                for i in range(num_motors):
                    rcout["motor" + str(i+1)] = int(row[i+2])

                if boot_ts_flag:
                    sys_time = int(rcout["sys_time"])
                    timestamp = system_helpers.sys_ts_converter(sys_time, boot_ts)

                    for i in range(num_motors):
                        motorName = "motor" + str(i+1)
                        sensor = [motorName + "ControlThrottleCommand_nonDim"]
                        value = [rcout[motorName]]

                        state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                        uas_state.append(state_value)

            if row[0] == "ATT":
                att["sys_time"] = int(row[1])
                att["roll"] = float(row[3])
                att["pitch"] = float(row[5])
                att["yaw"] = float(row[7])

                if boot_ts_flag:
                    sys_time = float(att["sys_time"])
                    timestamp = system_helpers.sys_ts_converter(sys_time, boot_ts)

                    sensors = list(set([
                        "roll_deg",
                        "pitch_deg",
                        "yaw_deg"
                    ]))

                    for sensor in sensors:
                        value = [att[sensor[:-4]]]
                        state_value = {"ts": timestamp, "sensor": [sensor], "value": value}
                        uas_state.append(state_value)

            if row[0] == "NKF1":
                nkf1["sys_time"] = int(row[1])
                nkf1["vel_north"] = float(row[5])
                nkf1["vel_east"] = float(row[6])
                nkf1["vel_down"] = float(row[7])

                if boot_ts_flag:
                    sys_time = float(nkf1["sys_time"])
                    timestamp = system_helpers.sys_ts_converter(sys_time, boot_ts)

                    sensors = list(set([
                        "velNorth_ftPerSec",
                        "velEast_ftPerSec",
                        "velDown_ftPerSec"
                    ]))

                    for sensor in sensors:
                        # Format: vel_[north|east|down]
                        nkf1_key = sensor[:sensor.find("_")].lower().replace("vel", "vel_")
                        value = [float(nkf1[nkf1_key]) * constants.M_TO_FT]
                        state_value = {"ts": timestamp, "sensor": [sensor], "value": value}
                        uas_state.append(state_value)

            if row[0] == "CURR":
                curr["sys_time"] = int(row[1])
                curr["voltage"] = float(row[2])
                curr["current"] = float(row[3])

                if boot_ts_flag:
                    sys_time = float(curr["sys_time"])
                    timestamp = system_helpers.sys_ts_converter(sys_time, boot_ts)

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
                    sys_time = float(row[1])
                    timestamp = system_helpers.sys_ts_converter(sys_time, boot_ts)

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
                acc1["sys_time"] = row[1]
                acc1["acc_x"] = row[5]
                acc1["acc_y"] = row[6]
                acc1["acc_z"] = row[7]

                if boot_ts_flag:
                    sys_time = float(acc1["sys_time"])
                    timestamp = system_helpers.sys_ts_converter(sys_time, boot_ts)
                    sensor = ["accBodyX_ftPerSec2"]
                    value = [float(acc1["acc_x"]) * constants.M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["accBodyY_ftPerSec2"]
                    value = [float(acc1["acc_y"]) * constants.M_TO_FT]
                    state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                    uas_state.append(state_value)
                    sensor = ["accBodyZ_ftPerSec2"]
                    value = [float(acc1["acc_z"]) * constants.M_TO_FT]
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
                    cmd["Alt"] = float(row[11])* constants.M_TO_FT

                    # UAS State values
                    timestamp = system_helpers.sys_ts_converter(int(cmd["sys_time"]), boot_ts)
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
                    elif cmd["CId"] == 82:
                        wp_type = 0
                    else:
                        wp_type = None

                    waypoint = {"wpTime": timestamp, "wpAlt_ft": cmd["Alt"], "hoverTime_sec": 0,
                                "wpLon_deg": cmd["Lon"], "wpLat_deg": cmd["Lat"],
                                "wpSequenceNum_nonDim": cmd["CNum"], "wpType_nonDim": wp_type,
                                "wpTargetAirSpeed_ftPerSec": None,
                                "wpTargetGroundSpeed_ftPerSec": None}
                    ac_flight_plan.append(waypoint)

            if row[0] == "MODE":
                if boot_ts_flag:
                    mode = row[2]
                    timestamp = system_helpers.sys_ts_converter(float(row[1]), boot_ts)
                    sensor = ["aircraftControlMode"]
                    try:
                        value = [ac_cntrl_mode[mode]]
                        state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                        uas_state.append(state_value)
                    except KeyError:
                        pass

            # Check for significant increase in barometer alt value
            # and motors spinning up
            if len(baro_avg_values) > 10 and baro_flag:
                if (baro["alt"] - baro_avg) > 1.5 and rcout["motor1"] > pwm_thresh and take_off_flag == 0:
                    take_off_flag = 1
                    aux_op["takeoffPosLat_deg"] = float(gps["lat"])
                    aux_op["takeoffPosLon_deg"] = float(gps["lon"])
                    aux_op["takeoffPosAlt_ft"] = float(gps["alt"])
                    takeoff_time = system_helpers.sys_ts_converter(int(baro["sys_time"]), boot_ts)
                    aux_op["takeOffTime"] = takeoff_time

            # Check for "landing complete" event ID
            if row[0] == "EV" and row[2] == "18":
                aux_op["landingPosLat_deg"] = float(gps["lat"])
                aux_op["landingPosLon_deg"] = float(gps["lon"])
                aux_op["landingPosAlt_ft"] = float(gps["alt"])
                landing_time = system_helpers.sys_ts_converter(int(baro["sys_time"]), boot_ts)
                aux_op["landingTime"] = landing_time

    # If no waypoints were used for flight, populate with "None"
    if not ac_flight_plan:
        ac_flight_plan.append(None)

    model["auxiliaryUASOperation"].update(aux_op)
    model["aircraftFlightPlan"] = ac_flight_plan if ac_flight_plan and ac_flight_plan[0] is not None else None
    model["uasState"] = uas_state

    return model
