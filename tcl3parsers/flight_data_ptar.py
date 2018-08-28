"""Creates FLIGHT_DATA json file from Arducopter Dataflash log file and waypoints file."""

## TO DO:
## Fix take off and landing logic
## Generate data and run against tests

import csv
import json

LEAP_SECS = 37
GPS_EPOCH_OFFSET = 315964800
GPS_LEAP_OFFSET = LEAP_SECS - 19

M_TO_FT = 3.28
CM_TO_FT = 0.328
MM_TO_FT = 0.00328
PA_TO_PSI = 0.000145038

# Useful constants
COL_A = 0
COL_J = 9
COL_K = 10
COL_L = 11
COL_M = 12
COL_N = 13
COL_O = 14
COL_P = 15
COL_Q = 16
COL_R = 17
COL_S = 18
COL_T = 19
COL_U = 20
COL_V = 21
COL_W = 22
COL_X = 23
COL_Y = 24
COL_Z = 25
COL_AA = 26
COL_AB = 27
COL_AC = 28
COL_AD = 29

def generate(mi_file_name, tlog_file_name, waypoints, outfile_name):
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
    wp_type = ""
    take_off_flag = False
    alt_flag = False

    alt_avg_values = []

    # Set up data structures
    flight_data = {}
    basic = {}
    aux_op = {}
    ac_flight_plan = []
    waypoint = {}
    uas_state = []
    state_value = {}
    gps = {"sys_time": 0, "lat": 0, "lon": 0, "alt": 0}

    with open(mi_file_name, "r") as mi_file:
        mi_reader = csv.DictReader(mi_file)
        for row in mi_reader:
            mi_dict = row

    with open("external_data/aircraft-specs.json", "r") as ac_specs:
        ac_specs_dict = json.load(ac_specs)

    with open("external_data/gcs-locations.json", "r") as gcs_locs:
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

    with open(waypoints, "r") as wpts:
        _ = wpts.readline()
        for line in wpts:
            row = line.split("\t")

            if row[3] == 16:
                wp_type = 1
            if row[3] == 82:
                wp_type = 0
            else:
                pass

            waypoint = {"wpTime": None, "wpAlt_ft": float(row[10]) * M_TO_FT, "hoverTime_sec": 0,
                        "wpLon_deg": row[9], "wpLat_deg": row[8],
                        "wpSequenceNum_nonDim": row[0], "wpType_nonDim": wp_type,
                        "wpTargetAirSpeed_ftPerSec": None,
                        "wpTargetGroundSpeed_ftPerSec": None}
            ac_flight_plan.append(waypoint)


    with open(tlog_file_name, "r") as tlog_file:
        # Initialize unix time stamp to 0
        old_time_unix_usec = 0
        time_unix_usec = 0

        for line in tlog_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            if row[COL_J] == "mavlink_system_time_t":
                # Time in us so convert down to seconds
                time_unix_usec = float(row[COL_L]) / 1E6

            if row[COL_J] == "mavlink_global_position_int_t":
                timestamp = row[COL_A] + "Z"
                vehicle_pos_lat_deg = row[COL_N]
                value = (vehicle_pos_lat_deg[:2] + "." + vehicle_pos_lat_deg[2:])
                gps["lat"] = value
                sensor = ["vehiclePositionLat_deg"]
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                vehicle_pos_lon_deg = row[COL_P]
                value = (vehicle_pos_lon_deg[:4] + "." + vehicle_pos_lon_deg[4:])
                gps["lon"] = value
                sensor = ["vehiclePositionLon_deg"]
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["vehiclePositionAlt_ft"]
                # Alt in mm; convert to feet
                value = float(row[COL_R]) * 0.00328084
                gps["alt"] = value
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["aboveTerrainAltitude_ft"]
                above_takeoff_loc_alt_ft = float(row[COL_T]) * 0.00328084
                value = above_takeoff_loc_alt_ft
                alt = above_takeoff_loc_alt_ft
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                # Average first 10 altitude values
                if len(alt_avg_values) < 10:
                    alt_avg_values.append(alt)
                if len(alt_avg_values) == 10 and not alt_flag:
                    alt_avg = sum(i for i in alt_avg_values)/10.0
                    alt_flag = True

                # Check for significant increase in barometer alt value
                # and motors spinning up
                if len(alt_avg_values) >= 10 and alt_flag:
                    if (alt - alt_avg) > 1.5 \
                    and not take_off_flag:
                        take_off_flag = True
                        aux_op["takeoffPosLat_deg"] = float(gps["lat"])
                        aux_op["takeoffPosLon_deg"] = float(gps["lon"])
                        aux_op["takeoffPosAlt_ft"] = float(gps["alt"])
                        aux_op["takeOffTime"] = timestamp

            if row[COL_J] == "mavlink_gps_raw_int_t":
                timestamp = row[COL_A] + "Z"

                sensor = ["hdop_nonDim"]
                value = float(row[COL_T]) / 100.0
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["vdop_nonDim"]
                value = float(row[COL_V]) / 100.0
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["numGpsSatellitesInView_nonDim"]
                value = row[COL_AD]
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

            if row[COL_J] == "mavlink_rc_channels_raw_t":
                timestamp = row[COL_A] = "Z"
                pwm = row[COL_N]

            if row[COL_J] == "mavlink_scaled_pressure_t":
                timestamp = row[COL_A] + "Z"

                sensor = ["barometricPressure_psi"]
                # Given mmhg, convert to PSI
                baro = float(row[COL_N]) * 0.0193367778713
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

            if row[COL_J] == "mavlink_radio_t":
                timestamp = row[COL_A] + "Z"

                sensor = ["c2c2RssiAircraft_dBm"]
                value = (float(row[COL_P]) / 1.9) - 127
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["c2RssiGcs_dBm"]
                value = (float(row[COL_R]) / 1.9) - 127
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["c2c2NoiseAircraft_dBm"]
                value = (float(row[COL_V]) / 1.9) - 127
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["c2c2NoiseGcs_dBm"]
                value = (float(row[COL_X]) / 1.9) - 127
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

                sensor = ["minDistToDefineedAreaLateralBoundary_ft"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["minDistToDefineedAreaVerticalBoundary_ft"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}

                uas_state.append(state_value)
                sensor = ["indicatedAirspeed_ftPerSec"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["aircraftAirborneState_nonDim"]
                if above_takeoff_loc_alt_ft > 2.0:
                    value = "Airborne"
                else:
                    value = "Ground"
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["targetGroundSpeed_ftPerSec"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["velDown_ftPerSec"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["velEast_ftPerSec"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["velNorth_ftPerSec"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["verticalNavVelocityError_ftPerSec"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["trueAirspeed_ftPerSec"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["targetWaypointLat_deg"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["targetWaypointLon_deg"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["targetWaypointAlt_ft"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["targetAirSpeed_ftPerSec"]
                value = None
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

            if row[COL_J] == "mavlink_vfr_hud_t":
                timestamp = row[COL_A] + "Z"

                sensor = ["groundSpeed_ftPerSec"]
                # Ground speed converted from m/s to ft/s
                value = float(row[COL_N]) * 3.28084
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                # Using "heading" for this value
                sensor = ["groundCourse_deg"]
                value = float(row[COL_T])
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

            if row[COL_J] == "mavlink_attitude_t":
                timestamp = row[COL_A] + "Z"

                sensor = ["roll_deg"]
                value = row[COL_N]
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["pitch_deg"]
                value = row[COL_P]
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["yaw_deg"]
                value = row[COL_R]
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["rollRate_degPerSec"]
                value = row[COL_T]
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["pitchRate_degPerSec"]
                value = row[COL_V]
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["yawRate_degPerSec"]
                value = row[COL_X]
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)


            if row[COL_J] == "mavlink_raw_imu_t":
                timestamp = row[COL_A] + "Z"

                # Tlog units are mg
                sensor = ["accBodyX_ftPerSec2"]
                value = float(row[COL_N]) * 0.00328084
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["accBodyY_ftPerSec2"]
                value = float(row[COL_P]) * 0.00328084
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["accBodyZ_ftPerSec2"]
                value = float(row[COL_R]) * 0.00328084
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

            if row[COL_J] == "mavlink_sys_status_t":
                timestamp = row[COL_A] + "Z"

                sensor = ["batteryVoltage_V"]
                value = float(row[COL_T]) / 1000.0
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

                sensor = ["batteryCurrent_A"]
                value = row[COL_V]
                state_value = {"ts": timestamp, "sensor": sensor, "value": value}
                uas_state.append(state_value)

            # # Check for second increment on unix time stamp
            # # write values every second
            # if time_unix_usec - old_time_unix_usec > 1:
            #     old_time_unix_usec = time_unix_usec


    # Last gps location will be landing location
    aux_op["landingPosLat_deg"] = float(gps["lat"])
    aux_op["landingPosLon_deg"] = float(gps["lon"])
    aux_op["landingPosAlt_ft"] = float(gps["alt"])
    aux_op["landingTime"] = timestamp

    # Build highest-level JSON structure
    flight_data = {"fType": "FLIGHT_DATA", "basic": basic, "auxiliaryUASOperation": aux_op,
                   "aircraftFlightPlan": ac_flight_plan, "uasState": uas_state}

    f_d = open(outfile_name, "w")
    json.dump(flight_data, f_d, indent=4)
