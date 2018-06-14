"""Generate CON4 json file for NASA UTM TCL3."""
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
    ftype = "CON4"
    pdf = "UTM-ACUASI-CON-4.pdf"
    kml = ""
    basic = {}
    con4_data = {}

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


    con4_data["fType"] = ftype
    con4_data["basic"] = basic
    con4_data["UTM-TCL3-DMP-RevF-CONPDF"] = pdf
    con4_data["UTM-TCL3-DMP-RevF-CONKML"] = kml

    outfile = open(outfile_name, "w")
    json.dump(con4_data, outfile, indent=4)
    outfile.close()
