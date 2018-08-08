import json
import csv
import os
from pathlib import Path

def auxiliaryUASOperation(files):
    aux_op = {}
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
    takeoff_weight = float(ac_specs_dict[mi_dict["VEHICLE_DESIGNATION"]]["weight_lbs"])
    num_motors = ac_specs_dict[mi_dict["VEHICLE_DESIGNATION"]]["num_motors"]
    type_of_operation = "Live"

    aux_op["flightTestCardName"] = mi_dict["test_card"]
    aux_op["testIdentifiers"] = [mi_dict["test_identifiers"]]
    aux_op["typeOfOperation"] = type_of_operation
    aux_op["takeoffWeight_lb"] = float(takeoff_weight)
    aux_op["gcsPosLat_deg"] = float(gcs_locs_dict[mi_dict["gcs_location"]]["latitude"])
    aux_op["gcsPosLon_deg"] = float(gcs_locs_dict[mi_dict["gcs_location"]]["longitude"])
    aux_op["gcsPosAlt_ft"] = float(gcs_locs_dict[mi_dict["gcs_location"]]["altitude"])
