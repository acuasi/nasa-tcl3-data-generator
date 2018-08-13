import json
import csv
import os
import itertools
from pathlib import Path

import helpers.constants as constants

def auxiliaryUASOperation(files):
    aux_op = {
        "typeOfOperation": None,
        "flightTestCardName": None,
        "testIdentifiers": None,
        "takeoffWeight_lb": None,
        "takeOffTime": None,
        "takeoffPosLat_deg": None,
        "takeoffPosLon_deg": None,
        "takeoffPosAlt_ft": None,
        "landingTime": None,
        "landingPosLat_deg": None,
        "landingPosLon_deg": None,
        "landingPosAlt_ft": None,
        "gcsPosLat_deg": None,
        "gcsPosLon_deg": None,
        "gcsPosAlt_ft": None
    }
    with open(files["MI_FILE"], "r") as mi_file:
        mi_reader = csv.DictReader(mi_file)
        for row in mi_reader:
            mi_dict = row

    aircraft_specs_file = os.path.join(Path(__file__).parents[5], "external_data/aircraft-specs.json")
    with open(aircraft_specs_file, "r") as ac_specs:
        ac_specs_dict = json.load(ac_specs)

    aircraft_gcs_locations_file = os.path.join(Path(__file__).parents[5], "external_data/gcs-locations.json")
    with open(aircraft_gcs_locations_file, "r") as gcs_locs:
        gcs_locs_dict = json.load(gcs_locs)

    # Get aircraft N number from mi_dict and use that to get take-off weight from
    # aircraft specs file
    vehicle_designation = mi_dict["VEHICLE_DESIGNATION"].strip()
    takeoff_weight = float(ac_specs_dict[vehicle_designation]["weight_lbs"])
    type_of_operation = "Live"

    aux_op["flightTestCardName"] = mi_dict["test_card"]
    aux_op["testIdentifiers"] = [mi_dict["test_identifiers"]]
    aux_op["typeOfOperation"] = type_of_operation
    aux_op["takeoffWeight_lb"] = float(takeoff_weight)

    # Fixes human error where no space is between location name
    for location in gcs_locs_dict:
        if "gcs_location" in mi_dict and mi_dict["gcs_location"].strip() == location.replace(" ", ""):
            mi_dict["gcs_location"] = location

    if "gcs_location" in mi_dict and mi_dict["gcs_location"].strip() in gcs_locs_dict:
        gcs_location = mi_dict["gcs_location"].strip()
        aux_op["gcsPosLat_deg"] = float(gcs_locs_dict[gcs_location]["latitude"])
        aux_op["gcsPosLon_deg"] = float(gcs_locs_dict[gcs_location]["longitude"])
        aux_op["gcsPosAlt_ft"] = float(gcs_locs_dict[gcs_location]["altitude"])


    if "LITCHI" in files:
        with open(files["LITCHI"], "r") as litchi:
            litchi_reader = csv.DictReader(litchi)
            for currentRow, nextRow in pairwise(litchi_reader):

                if currentRow["flightmode"] == "TakeOff" and nextRow["flightmode"] != "TakeOff":
                    aux_op["takeOffTime"] = currentRow["datetime(utc)"].replace(" ", "T")
                    aux_op["takeoffPosLat_deg"] = float(currentRow["latitude"])
                    aux_op["takeoffPosLon_deg"] = float(currentRow["longitude"])
                    aux_op["takeoffPosAlt_ft"] = float(currentRow["altitude(feet)"])
                if currentRow["isMotorsOn"] == "1" and nextRow["isMotorsOn"] == "0":
                    aux_op["landingTime"] = nextRow["datetime(utc)"].replace(" ", "T")
                    aux_op["landingPosLat_deg"] = float(nextRow["latitude"])
                    aux_op["landingPosLon_deg"] = float(nextRow["longitude"])
                    aux_op["landingPosAlt_ft"] = float(nextRow["altitude(feet)"])
    elif "TLOG" in files:
        with open(files["TLOG"], "r") as tlog:
            alt_avg_values = []
            take_off_flag = False
            alt_flag = False

            for row in tlog:
                row = [item.strip() for item in row.split(",")]

                timestamp = row[constants.COL_A] + "Z"
                vehicle_pos_lat_deg = row[constants.COL_N]
                vehicle_pos_lon_deg = row[constants.COL_P]
                alt = ""

                if row[constants.COL_J] == "mavlink_global_position_int_t":
                    aux_op["landingPosLat_deg"] = float(vehicle_pos_lat_deg[:2] + "." + vehicle_pos_lat_deg[2:])
                    aux_op["landingPosLon_deg"] = float(vehicle_pos_lon_deg[:4] + "." + vehicle_pos_lon_deg[4:])
                    aux_op["landingPosAlt_ft"] = float(row[constants.COL_R]) * 0.00328084
                    aux_op["landingTime"] = timestamp
                    alt = float(row[constants.COL_T]) * 0.00328084
                    alt_avg = 0
                    if len(alt_avg_values) < 10:
                        alt_avg_values.append(alt)

                    if len(alt_avg_values) == 10 and not alt_flag:
                        alt_avg = sum(i for i in alt_avg_values)/10.0
                        alt_flag = True

                    if len(alt_avg_values) >= 10 and alt_flag:
                        if (alt - alt_avg) > 1.5 and not take_off_flag:
                            take_off_flag = True
                            aux_op["takeoffPosLat_deg"] = float(vehicle_pos_lat_deg[:2] + "." + vehicle_pos_lat_deg[2:])
                            aux_op["takeoffPosLon_deg"] = float(vehicle_pos_lon_deg[:4] + "." + vehicle_pos_lon_deg[4:])
                            aux_op["takeoffPosAlt_ft"] = float(row[constants.COL_R]) * 0.00328084
                            aux_op["takeOffTime"] = timestamp

    return aux_op

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
