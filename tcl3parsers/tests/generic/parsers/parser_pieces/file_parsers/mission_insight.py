"""Creates the "basic" variable from the mission insight's file"""
import csv

def mission_insight(defaultModel, mi_file_name):
    """Parses the Mission Insight file and returns a new model """
    with open(mi_file_name, "r") as mission_insight_file:
        mi_reader = csv.DictReader(mission_insight_file)
        mi_dict = next(mi_reader)

        time = mi_dict["SUBMIT_TIME"]
        date = mi_dict["DATE"]

        basic = {}
        basic["uvin"] = mi_dict["UVIN"]
        basic["gufi"] = mi_dict["OPERATION_GUFI"]
        basic["submitTime"] = date + "T" + time
        basic["ussInstanceID"] = mi_dict["USS_INSTANCE_ID"]
        basic["ussName"] = mi_dict["USS_NAME"]

        defaultModel["basic"] = basic

    return defaultModel
