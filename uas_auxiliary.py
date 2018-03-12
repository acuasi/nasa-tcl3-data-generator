# Convert a csv telemetry log file and waypoint plan to the NASA
# flight plan formatted CSV file
#
# File name format: UTM-ACUASI-dateOfFlight-takeoffTime-AircraftFlightplan.csv
# where dateOfFlight & takeOffTime can be pulled from the name of the tlog file
#
# Values to pass to the script:
# Mission insight csv file, Mission Planner tlog file converted to csv
#
# Read the date from the TLog file
# Split into Date and Time
# Date is Flight Date and Time is Takeoff time

import os
import csv

def auxiliary(mission_insight_csv, tlog_csv, gcs_location):

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

    counter = 0

    EMPTY = ""

    FRAME = 0
    WEIGHT = 1

    take_off_flag = 0

    AboveTakeoffLocationAltitude_ft = 0
    vehiclePositionLat_deg = 0
    vehiclePositionLon_deg = 0
    GPSAltitude_ft = 0

    gcsPosLat_deg = gcs_location['latitude']
    gcsPosLon_deg = gcs_location['longitude']
    gcsPosAlt_ft = gcs_location['altitude']

    # NASA no longer requires us to generate aircraft specifications file for each flight, so we'll need to store
    # data about each configuration in this dictionary. Populate once configurations are finalized
    aircraft = {"N249UA": ['helicopter', 17.0], "N254MH": ['multirotor', 11.2], "N255MH": ['multirotor', 11.4]}

    tlog_name = os.path.basename(tlog_csv)
    tlog_path = os.path.dirname(tlog_csv)

    flight_logs = open(mission_insight_csv, "r")
    tlog_file = open(tlog_csv, "r")
    typeOfoperation = "Live"

    # Get columns and assign to variables
    headers = flight_logs.readline().split(',')

    try:
        UVIN_COL = headers.index("UVIN")
        GUFI_COL = headers.index("GUFI")

    except ValueError:
        print("Please format flights file with proper column names: \
                'UVIN', 'TLOG', 'GUFI' 'WAYPOINT', 'FRAME', 'OPERATION', 'WEIGHT'")



    # Iterate through flight log file and create output file for each log
    for line in flight_logs:

        values = line.split(",")

        date, time = tlog_name.split(' ')
        date = date.replace("-", "")
        time = time.replace("-", "")
        time = time[:4]

        out_file_name = "UTM-ACUASI-" + date + "-" + time + "-AuxiliaryUASOperation.csv"

        # In the highly unlikely chance that two aircraft launched at the
        # exact same second, we name the second one different
        # If three aircraft launched simultaneously--buy lottery tickets
        if not os.path.isfile(out_file_name):
            out_file = open(out_file_name, "w+")
        else:
            out_file_name = "UTM-ACUASI-" + date + "-" + time + "-AuxiliaryUASOperation2.csv"
            out_file = open(out_file_name, "w+")

        UVIN = values[UVIN_COL]
        GUFI = values[GUFI_COL]

        # Placeholder until aircraft dictionary is properly populated with all configuration values
        n_number = "N254MH"

        takeOffWeight_lb = aircraft[n_number][WEIGHT]
        typeOfAirframe = aircraft[n_number][FRAME]
        typeOfoperation = "Live"


        # Write header
        header = "uvin,gufi,variable,value\n"
        out_file.write(header)

        for line in tlog_file:
            row = line.split(",")
            counter += 1

            # The non-standard camelCase naming convention is for easy reference to
            # NASA's variables.

            try:
                if row[COL_J] == "mavlink_global_position_int_t":
                    # Assign this every time there's a non-zero value so it will end up
                    # being the last known GPS location which we assume to be the
                    # landing position
                    if row[COL_N] != 0 and row[COL_P] != 0:
                        landingPosLat_deg = row[COL_N]
                        landingPosLat_deg = landingPosLat_deg[:2] + "." + landingPosLat_deg[2:]
                        landingPosLon_deg = row[COL_P]
                        landingPosLon_deg = landingPosLon_deg[:4] + "." + landingPosLon_deg[4:]
                        landinPosAlt_ft = float(row[COL_R]) * 0.00328084

                    # Check for first non-zero point where altitude is above 50 m
                    # A priori we know the take off position is >100 m above sea level
                    # Assume that to be take-off position
                    if int(row[COL_N]) != 0 and int(row[COL_P]) != 0 and int(row[COL_R]) > 50000 and take_off_flag == 0:
                        takeoffPosLat_deg = row[COL_N]
                        takeoffPosLat_deg = takeoffPosLat_deg[:2] + "." + takeoffPosLat_deg[2:]
                        takeoffPosLon_deg = row[COL_P]
                        takeoffPosLon_deg = takeoffPosLon_deg[:4] + "." + takeoffPosLon_deg[4:]
                        takeoffPosAlt_ft = float(row[COL_R]) * 0.00328084
                        take_off_flag = 1
            except IndexError:
                pass

        writer = csv.writer(out_file, delimiter=',')

        writer.writerow([UVIN, GUFI, "typeOfoperation", typeOfoperation])
        writer.writerow([UVIN, GUFI, "flightTestCardName", EMPTY])
        writer.writerow([UVIN, GUFI, "takeOffWeight_lb", takeOffWeight_lb])
        writer.writerow([UVIN, GUFI, "takeoffPosLat_deg", takeoffPosLat_deg])
        writer.writerow([UVIN, GUFI, "takeoffPosLon_deg", takeoffPosLon_deg])
        writer.writerow([UVIN, GUFI, "takeoffPosAlt_ft", takeoffPosAlt_ft])
        writer.writerow([UVIN, GUFI, "landingPosLat_deg", landingPosLat_deg])
        writer.writerow([UVIN, GUFI, "landingPosLon_deg", landingPosLon_deg])
        writer.writerow([UVIN, GUFI, "landingPosAlt_ft", landinPosAlt_ft])
        writer.writerow([UVIN, GUFI, "gcsPosLat_deg", gcsPosLat_deg])
        writer.writerow([UVIN, GUFI, "gcsPosLon_deg", gcsPosLon_deg])
        writer.writerow([UVIN, GUFI, "gcsPosAlt_ft", gcsPosAlt_ft])
