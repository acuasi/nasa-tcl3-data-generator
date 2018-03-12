# Convert a csv telemetry log file and waypoint plan to the NASA
# flight plan formatted CSV file
#
# File name format: UTM-ACUASI-dateOfFlight-takeoffTime-AircraftFlightplan.csv
# where dateOfFlight & takeOffTime can be pulled from the name of the tlog file
#
# Values to pass to the script:
# Mission Insight file, Mission Planner waypoint file, Mission Planner tlog file in csv format
#
# Read the date from the TLog file
# Split into Date and Time
# Date is Flight Date and Time is Takeoff time
# For each waypoint get:
# wp #, wpType, Lat, Lon, Alt, delay time

import os
import csv

def flight(mission_insight_csv, waypoints, tlog_csv):

    tlog_name = os.path.basename(tlog_csv)
    waypoint_name = os.path.basename(waypoints)

    mission_insight_file = open(mission_insight_csv, "r")
    waypoint_file = open(waypoints, "r")

    # Get columns and assign to variables
    headers = mission_insight_file.readline().split(',')

    try:
        UVIN_COL = headers.index("UVIN")
        GUFI_COL = headers.index("GUFI")

    except ValueError:
        print("Invalid Mission Insight file.")

    # Iterate through Mission Insight file and create output file for each log
    # Keep for loop for the moment, but Mission Insight file likely will be separate
    # file for each flight so ultimately won't need for loop
    for line in mission_insight_file:

        values = line.split(",")

        date, time = tlog_name.split(' ')
        date = date.replace("-", "")
        time = time.replace("-", "")
        time = time[:4]

        out_file_name = "UTM-ACUASI-"+date+"-"+time+"-AircraftFlightPlan.csv"

        # In the highly unlikely chance that two aircraft launched at the
        # exact same second, we name the second one different
        if not os.path.isfile(out_file_name):
            out_file = open(out_file_name, "w+")
        else:
            out_file_name = "UTM-ACUASI-"+date+"-"+time+"-AircraftFlightPlan.csv"
            out_file = open(out_file_name, "w+")

        UVIN = values[UVIN_COL]
        GUFI = values[GUFI_COL]

        try:
            # Get header line out of the way
            waypoint_file.readline()

            for line in waypoint_file:
                row = line.split("\t")

                # Only use waypoint types, not commands
                # '16' is for 'fly-over' waypoints
                # '82' indicates spline or 'fly-by' points
                if row[3] == '16':

                    wpType_nonDim = 1
                    wpSequence_num = row[0]
                    wpLat_deg = row[8]
                    wpLon_deg = row[9]
                    wpAlt_ft = float(row[10]) * 3.28

                if row[3] == '82':

                    wpType_nonDim = 0
                    wpSequence_num = row[0]
                    wpLat_deg = row[8]
                    wpLon_deg = row[9]
                    wpAlt_ft = float(row[10]) * 3.28

                writer = csv.writer(out_file, delimiter=',')

                writer.writerow([UVIN, GUFI, wpSequence_num, wpType_nonDim, wpLat_deg,
                                wpLon_deg, wpAlt_ft, "", "", "", "", ""])

        except FileNotFoundError:
            print("File " + waypoint_name + " not found, skipping.")
            pass
