"""Generate CON5 json file for NASA UTM TCL3."""
import csv
import json

def generate(mi_file_name, outfile_name):
    """Generate con5 json file.

    Args:
        mi_file_name            (str): Name of the mission insight file.    [.csv]
        df_file_name            (str): Name of the dataflash log file       [.log]
        outfile_name            (str): Name of the output file to be created. [e.g. 'CON1.json']

    Returns:
        None
    """
    # Set up json objects
    ftype = "CON5"
    basic = {}
    boundary_dist = []
    airspace_status = []
    con5_data = {}

    with open(mi_file_name, "r") as mi_file:
        mi_reader = csv.DictReader(mi_file)
        for row in mi_reader:
            mi_dict = row

    time = mi_dict["SUBMIT_TIME"]
    date = mi_dict["DATE"]
    basic["uvin"] = mi_dict["UVIN"]
    basic["gufi"] = mi_dict["OPERATION_GUFI"]
    basic["submitTime"] = date + "T" + time
    basic["ussInstanceID"] = mi_dict["USS_INSTANCE_ID"]
    basic["ussName"] = mi_dict["USS_NAME"]

    con5_data["fType"] = ftype
    con5_data["basic"] = basic
    con5_data["distFromBoundary"] = boundary_dist
    con5_data["unauthorizedAirspaceStatus"] = airspace_status

    outfile = open(outfile_name, "w")
    json.dump(con5_data, outfile, indent=4)
    outfile.close()
