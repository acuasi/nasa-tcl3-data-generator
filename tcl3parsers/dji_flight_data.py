"""Creates FLIGHT_DATA json file from DJI Binary log file and litchi telemetry file."""
import csv
import json

M_TO_FT = 3.28
MPH_TO_FPS = 1.46667
MA_TO_A = .001


def generate(mi_file_name, litchi_file_name, waypoints_file_name, outfile_name):
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

    # Set up data structures
    flight_data = {}
    basic = {}
    aux_op = {}
    ac_flight_plan = []
    waypoint = {}
    uas_state = []
    state_value = {}

    wp_count = 1

    # Open files and parse data
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
    takeoff_weight = float(ac_specs_dict[mi_dict["VEHICLE_DESIGNATION"].strip()]["weight_lbs"])
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

    with open(litchi_file_name, "r") as litchi_file:
        headers = litchi_file.readline().strip().split(",")

        for line in litchi_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            # Format timestamp to ISO8601 standard
            dt = row[headers.index("datetime(utc)")]
            timestamp = dt.split(" ")[0] + "T" + dt.split(" ")[1] + "Z"

            sensor = ["vehiclePositionLat_deg"]
            value = float(row[headers.index("latitude")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["vehiclePositionLon_deg"]
            value = float(row[headers.index("longitude")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["vehiclePositionAlt_ft"]
            value = float(row[headers.index("altitude(feet)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["aboveTerrainAltitude_ft"]
            value = float(row[headers.index("altitude(feet)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["indicatedAirspeed_ftPerSec"]
            value = None
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["trueAirspeed_ftPerSec"]
            value = None
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["groundSpeed_ftPerSec"]
            value = float(row[headers.index("speed(mph)")]) * MPH_TO_FPS
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["groundCourse_deg"]
            yaw = int(row[headers.index("yaw(deg)")])
            if yaw < 0:
                yaw = yaw + 360
            value = yaw
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["numGpsSatellitesInView_nonDim"]
            value = int(row[headers.index("satellites")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["numGpsSat_nonDim"]
            value = None
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["pitch_deg"]
            value = int(row[headers.index("pitch(deg)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["roll_deg"]
            value = int(row[headers.index("roll(deg)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["yaw_deg"]
            value = int(row[headers.index("yaw(deg)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["batteryVoltage_v"]
            value = float(row[headers.index("voltage(v)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["batteryCurrent_a"]
            value = float(row[headers.index("currentCurrent")]) * -MA_TO_A
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["aircraftAirborneState_nonDim"]
            value = int(row[headers.index("isflying")])
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

            sensor = ["hdop_nonDim"]
            value = None
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["vdop_nonDim"]
            value = None
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["velNorth_ftPerSec"]
            value = None
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["velEast_ftPerSec"]
            value = None
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["velDown_ftPerSec"]
            value = None
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)

    with open(waypoints_file_name, "r") as waypoints_file:
        headers = waypoints_file.readline().strip().split(",")

        for line in waypoints_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            sensor = ["targetWaypointLat_deg"]
            value = float(row[headers.index('latitude')])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["targetWaypointLon_deg"]
            value = float(row[headers.index('longitude')])
            state_value = {"ts": timestamp, "sensor": sensor, "value": value}
            uas_state.append(state_value)
            sensor = ["targetWaypointAlt_ft"]
            value = float(row[headers.index('altitude(m)')]) * M_TO_FT
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

            wp_speed = float(row[headers.index('speed(m/s)')]) * M_TO_FT
            waypoint = {"wpTime": None,
                        "wpAlt_ft": float(row[headers.index('altitude(m)')]) * M_TO_FT,
                        "hoverTime_sec": 0, "wpLon_deg": float(row[headers.index('longitude')]),
                        "wpLat_deg": float(row[headers.index('latitude')]),
                        "wpSequenceNum_nonDim": wp_count, "wpType_nonDim": 1,
                        "wpTargetAirSpeed_ftPerSec": wp_speed, "wpTargetGroundSpeed_ftPerSec": None}
            ac_flight_plan.append(waypoint)
            wp_count += 1

    flight_data["fType"] = "FLIGHT_DATA"
    flight_data["basic"] = basic
    flight_data["auxiliaryUASOperation"] = aux_op
    flight_data["aircraftFlightPlan"] = ac_flight_plan
    flight_data["uasState"] = uas_state

    outfile = open(outfile_name, "w")
    json.dump(flight_data, outfile, indent=4)
    outfile.close()
