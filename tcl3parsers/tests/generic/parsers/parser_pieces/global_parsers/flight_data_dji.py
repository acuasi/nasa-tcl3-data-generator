"""Creates FLIGHT_DATA json file from DJI Binary log file and litchi telemetry file."""
import csv
import json
import helpers.constants as constants

def flight_data_dji(model, files):
    # Set up data structures
    ac_flight_plan = []
    waypoint = {}
    uas_state = []
    state_value = {}

    wp_count = 1

    with open(files["LITCHI"], "r") as litchi_file:
        headers = litchi_file.readline().strip().split(",")

        for line in litchi_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            # Format timestamp to ISO8601 standard
            dt = row[headers.index("datetime(utc)")]
            timestamp = dt.split(" ")[0] + "T" + dt.split(" ")[1] + "Z"

            sensor = ["vehiclePositionLat_deg"]
            value = float(row[headers.index("latitude")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["vehiclePositionLon_deg"]
            value = float(row[headers.index("longitude")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["vehiclePositionAlt_ft"]
            value = float(row[headers.index("altitude(feet)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["aboveTerrainAltitude_ft"]
            value = float(row[headers.index("altitude(feet)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["groundSpeed_ftPerSec"]
            value = float(row[headers.index("speed(mph)")]) * constants.MPH_TO_FPS
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["groundCourse_deg"]
            yaw = int(row[headers.index("yaw(deg)")])
            if yaw < 0:
                yaw = yaw + 360
            value = yaw
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["numGpsSatellitesInView_nonDim"]
            value = int(row[headers.index("satellites")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["pitch_deg"]
            value = int(row[headers.index("pitch(deg)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["roll_deg"]
            value = int(row[headers.index("roll(deg)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["yaw_deg"]
            value = int(row[headers.index("yaw(deg)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["batteryVoltage_v"]
            value = float(row[headers.index("voltage(v)")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["batteryCurrent_a"]
            value = float(row[headers.index("currentCurrent")]) * -constants.MA_TO_A
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["aircraftAirborneState_nonDim"]
            value = int(row[headers.index("isflying")])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}

            empty_values = [
                "lateralNavPositionError_ft",
                "verticalNavPositionError_ft",
                "lateralNavVelocityError_ftPerSec",
                "verticalNavVelocityError_ftPerSec",
                "hdop_nonDim",
                "vdop_nonDim",
                "velNorth_ftPerSec",
                "velEast_ftPerSec",
                "velDown_ftPerSec",
                "trueAirspeed_ftPerSec",
                "velDown_ftPerSec",
                "numGpsSat_nonDim"
            ]

            for sensor in empty_values:
                state_value = {"ts": timestamp, "sensor": [sensor], "value": None}
                uas_state.append(state_value)

    with open(files["WAYPOINTS"], "r") as waypoints_file:
        headers = waypoints_file.readline().strip().split(",")

        for line in waypoints_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            sensor = ["targetWaypointLat_deg"]
            value = float(row[headers.index('latitude')])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["targetWaypointLon_deg"]
            value = float(row[headers.index('longitude')])
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)
            sensor = ["targetWaypointAlt_ft"]
            value = float(row[headers.index('altitude(m)')]) * constants.M_TO_FT
            state_value = {"ts": timestamp, "sensor": sensor, "value": [value]}
            uas_state.append(state_value)

            empty_sensors = [
                "targetGroundSpeed_ftPerSec",
                "targetAirSpeed_ftPerSec",
                "minDistToDefinedAreaLateralBoundary_ft",
                "minDistToDefinedAreaVerticalBoundary_ft"
            ]

            for sensor in empty_sensors:
                state_value = {"ts": timestamp, "sensor": [sensor], "value": None}
                uas_state.append(state_value)

            wp_speed = float(row[headers.index('speed(m/s)')]) * constants.M_TO_FT
            waypoint = {"wpTime": None,
                        "wpAlt_ft": float(row[headers.index('altitude(m)')]) * constants.M_TO_FT,
                        "hoverTime_sec": 0, "wpLon_deg": float(row[headers.index('longitude')]),
                        "wpLat_deg": float(row[headers.index('latitude')]),
                        "wpSequenceNum_nonDim": wp_count, "wpType_nonDim": 1,
                        "wpTargetAirSpeed_ftPerSec": wp_speed, "wpTargetGroundSpeed_ftPerSec": None}
            ac_flight_plan.append(waypoint)
            wp_count += 1

    model["aircraftFlightPlan"] = ac_flight_plan
    model["uasState"] = uas_state

    return model
