"""Creates FLIGHT_DATA json file from PTAR tlog file."""
import csv
import json
import helpers.constants as constants

def flightDataPtar(model, files):
    # Set up data structures
    wp_type = 0
    ac_flight_plan = []
    waypoint = {}
    uas_state = []
    state_value = {}
    gps = {"sys_time": 0, "lat": 0, "lon": 0, "alt": 0}

    with open(files["WAYPOINTS"], "r") as wpts:
        _ = wpts.readline()
        for line in wpts:
            row = line.split("\t")

            if row[3] == 16:
                wp_type = 1
            if row[3] == 82:
                wp_type = 0
            else:
                pass

            waypoint = {"wpTime": None, "wpAlt_ft": float(row[10]) * constants.M_TO_FT, "hoverTime_sec": 0,
                        "wpLon_deg": float(row[9]), "wpLat_deg": float(row[8]),
                        "wpSequenceNum_nonDim": int(row[0]), "wpType_nonDim": wp_type,
                        "wpTargetAirSpeed_ftPerSec": None,
                        "wpTargetGroundSpeed_ftPerSec": None}
            ac_flight_plan.append(waypoint)


    with open(files["TLOG"], "r") as tlog_file:
        for line in tlog_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            if row[constants.COL_J] == "mavlink_global_position_int_t":
                timestamp = row[constants.COL_A] + "Z"
                vehicle_pos_lat_deg = row[constants.COL_N]
                value = float(vehicle_pos_lat_deg[:2] + "." + vehicle_pos_lat_deg[2:])
                gps["lat"] = value
                sensor = ["vehiclePositionLat_deg"]
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                vehicle_pos_lon_deg = row[constants.COL_P]
                value = float(vehicle_pos_lon_deg[:4] + "." + vehicle_pos_lon_deg[4:])
                gps["lon"] = value
                sensor = ["vehiclePositionLon_deg"]
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["vehiclePositionAlt_ft"]
                # Alt in mm; convert to feet
                value = float(row[constants.COL_R]) * 0.00328084
                gps["alt"] = value
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["aboveTerrainAltitude_ft"]
                above_takeoff_loc_alt_ft = float(row[constants.COL_T]) * 0.00328084
                value = float(above_takeoff_loc_alt_ft)
                alt = above_takeoff_loc_alt_ft
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

            if row[constants.COL_J] == "mavlink_gps_raw_int_t":
                timestamp = row[constants.COL_A] + "Z"

                sensor = ["hdop_nonDim"]
                value = float(row[constants.COL_T]) / 100.0
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["vdop_nonDim"]
                value = float(row[constants.COL_V]) / 100.0
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["numGpsSatellitesInView_nonDim"]
                value = float(row[constants.COL_AD])
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

            if row[constants.COL_J] == "mavlink_rc_channels_raw_t":
                timestamp = row[constants.COL_A] = "Z"
                pwm = row[constants.COL_N]

            if row[constants.COL_J] == "mavlink_scaled_pressure_t":
                timestamp = row[constants.COL_A] + "Z"

                sensor = ["barometricPressure_psi"]
                # Given mmhg, convert to PSI
                baro = float(row[constants.COL_N]) * 0.0193367778713
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

            if row[constants.COL_J] == "mavlink_radio_t":
                timestamp = row[constants.COL_A] + "Z"

                sensor = ["c2c2RssiAircraft_dBm"]
                value = (float(row[constants.COL_P]) / 1.9) - 127
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["c2RssiGcs_dBm"]
                value = (float(row[constants.COL_R]) / 1.9) - 127
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["c2c2NoiseAircraft_dBm"]
                value = (float(row[constants.COL_V]) / 1.9) - 127
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["c2c2NoiseGcs_dBm"]
                value = (float(row[constants.COL_X]) / 1.9) - 127
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)


                emptySensors = [
                    "lateralNavPositionError_ft",
                    "verticalNavPositionError_ft",
                    "minDistToDefineedAreaLateralBoundary_ft",
                    "minDistToDefineedAreaVerticalBoundary_ft",
                    "indicatedAirspeed_ftPerSec",
                    "targetGroundSpeed_ftPerSec",
                    "velDown_ftPerSec",
                    "velEast_ftPerSec",
                    "velNorth_ftPerSec",
                    "verticalNavVelocityError_ftPerSec",
                    "trueAirspeed_ftPerSec",
                    "targetWaypointLat_deg",
                    "targetWaypointLon_deg",
                    "targetWaypointAlt_ft",
                    "targetAirSpeed_ftPerSec"
                ]

                for sensor in emptySensors:
                    state_value = {"ts": timestamp, "sensor": sensor, "value": None}
                    uas_state.append(state_value)



                sensor = ["aircraftAirborneState_nonDim"]
                if above_takeoff_loc_alt_ft > 2.0:
                    # value = "Airborne"
                    value = 1
                else:
                    # value = "Ground"
                    value = 0
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

            if row[constants.COL_J] == "mavlink_vfr_hud_t":
                timestamp = row[constants.COL_A] + "Z"

                sensor = ["groundSpeed_ftPerSec"]
                # Ground speed converted from m/s to ft/s
                value = float(row[constants.COL_N]) * 3.28084
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                # Using "heading" for this value
                sensor = ["groundCourse_deg"]
                value = float(row[constants.COL_T])
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

            if row[constants.COL_J] == "mavlink_attitude_t":
                timestamp = row[constants.COL_A] + "Z"

                sensor = ["roll_deg"]
                value = float(row[constants.COL_N])
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["pitch_deg"]
                value = float(row[constants.COL_P])
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["yaw_deg"]
                value = float(row[constants.COL_R])
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["rollRate_degPerSec"]
                value = float(row[constants.COL_T])
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["pitchRate_degPerSec"]
                value = float(row[constants.COL_V])
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["yawRate_degPerSec"]
                value = float(row[constants.COL_X])
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)


            if row[constants.COL_J] == "mavlink_raw_imu_t":
                timestamp = row[constants.COL_A] + "Z"

                # Tlog units are mg
                sensor = ["accBodyX_ftPerSec2"]
                value = float(row[constants.COL_N]) * 0.00328084
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["accBodyY_ftPerSec2"]
                value = float(row[constants.COL_P]) * 0.00328084
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["accBodyZ_ftPerSec2"]
                value = float(row[constants.COL_R]) * 0.00328084
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

            if row[constants.COL_J] == "mavlink_sys_status_t":
                timestamp = row[constants.COL_A] + "Z"

                sensor = ["batteryVoltage_v"]
                value = float(row[constants.COL_T]) / 1000.0
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

                sensor = ["batteryCurrent_a"]
                value = float(row[constants.COL_V])
                state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
                uas_state.append(state_value)

    model["aircraftFlightPlan"] = ac_flight_plan
    model["uasState"] = uas_state

    requiredSensors = {
        "aboveTerrainAltitude_ft": False,
        "accBodyX_ftPerSec2": False,
        "accBodyY_ftPerSec2": False,
        "accBodyZ_ftPerSec2": False,
        "acousticSensorAltitude_ft": False,
        "aileronActuatorCommand_nonDim": False,
        "aircraftAirborneState_nonDim": False,
        "aircraftControlMode": False,
        "altitudeUsedByAutopilot_ft": False,
        "angleOfAttack_deg": False,
        "barometricAltitude_ft": False,
        "barometricPressure_psi": False,
        "batteryCurrent_a": False,
        "batteryVoltage_v": False,
        "c2NoiseAircraft_dBm": False,
        "c2NoiseGcs_dBm": False,
        "c2PacketLossRateAircraftPrct_nonDim": False,
        "c2PacketLossRateGcsPrct_nonDim": False,
        "c2RssiAircraft_dBm": False,
        "c2RssiGcs_dBm": False,
        "elevatorActuatorCommand_nonDim": False,
        "flapActuatorCommand_nonDim": False,
        "groundCourse_deg": False,
        "groundSpeed_ftPerSec": False,
        "hdop_nonDim": False,
        "imageSensorAltitude_ft": False,
        "indicatedAirspeed_ftPerSec": False,
        "landingGearActuatorCommand_nonDim": False,
        "laserSensorAltitude_ft": False,
        "lateralNavPositionError_ft": False,
        "lateralNavVelocityError_ftPerSec": False,
        "minDistToDefinedAreaLateralBoundary_ft": False,
        "minDistToDefinedAreaVerticalBoundary_ft": False,
        "motor10ControlThrottleCommand_nonDim": False,
        "motor11ControlThrottleCommand_nonDim": False,
        "motor12ControlThrottleCommand_nonDim": False,
        "motor13ControlThrottleCommand_nonDim": False,
        "motor14ControlThrottleCommand_nonDim": False,
        "motor15ControlThrottleCommand_nonDim": False,
        "motor16ControlThrottleCommand_nonDim": False,
        "motor1ControlThrottleCommand_nonDim": False,
        "motor2ControlThrottleCommand_nonDim": False,
        "motor3ControlThrottleCommand_nonDim": False,
        "motor4ControlThrottleCommand_nonDim": False,
        "motor5ControlThrottleCommand_nonDim": False,
        "motor6ControlThrottleCommand_nonDim": False,
        "motor7ControlThrottleCommand_nonDim": False,
        "motor8ControlThrottleCommand_nonDim": False,
        "motor9ControlThrottleCommand_nonDim": False,
        "numGpsSat_nonDim": False,
        "numGpsSatellitesInView_nonDim": False,
        "opticalSensorAltitude_ft": False,
        "pitchRate_degPerSec": False,
        "pitch_deg": False,
        "radarSensorAltitude_ft": False,
        "rollRate_degPerSec": False,
        "roll_deg": False,
        "rudderActuatorCommand_nonDim": False,
        "sideSlip_deg": False,
        "targetAirSpeed_ftPerSec": False,
        "targetGroundSpeed_ftPerSec": False,
        "targetWaypointAlt_ft": False,
        "targetWaypointLat_deg": False,
        "targetWaypointLon_deg": False,
        "trueAirspeed_ftPerSec": False,
        "vdop_nonDim": False,
        "vehiclePositionAlt_ft": False,
        "vehiclePositionLat_deg": False,
        "vehiclePositionLon_deg": False,
        "velDown_ftPerSec": False,
        "velEast_ftPerSec": False,
        "velNorth_ftPerSec": False,
        "verticalNavPositionError_ft": False,
        "verticalNavVelocityError_ftPerSec": False,
        "yawRate_degPerSec": False,
        "yaw_deg": False
    }

    for entry in model["uasState"]:
        if entry["sensor"][0] in requiredSensors.keys():
            requiredSensors[entry["sensor"][0]] = True

    for requiredSensor, confirmed in requiredSensors.items():
        if not confirmed:
            model["uasState"].append({"ts": timestamp, "sensor": [requiredSensor], "value": None})


    return model
