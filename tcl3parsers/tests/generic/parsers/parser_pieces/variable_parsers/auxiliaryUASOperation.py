import json
import csv
import os
import itertools
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
    vehicle_designation = mi_dict["VEHICLE_DESIGNATION"].strip()
    takeoff_weight = float(ac_specs_dict[vehicle_designation]["weight_lbs"])
    type_of_operation = "Live"

    aux_op["flightTestCardName"] = mi_dict["test_card"]
    aux_op["testIdentifiers"] = [mi_dict["test_identifiers"]]
    aux_op["typeOfOperation"] = type_of_operation
    aux_op["takeoffWeight_lb"] = float(takeoff_weight)

    if "gcs_location" in mi_dict and mi_dict["gcs_location"] in gcs_locs_dict:
        gcs_location = mi_dict["gcs_location"]
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
    return aux_op

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
