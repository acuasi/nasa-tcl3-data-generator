import os
import csv


class Arducopter():

    # Useful constants for log file columns
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

    def state(self, mission_insight_csv, tlog_csv):

        # Initialize unix time stamp to 0
        old_unix_time = 0
        unix_time = 0

        # Check this variable and update if necessary
        leap_seconds = 18

        AboveTakeoffLocationAltitude_ft = 0

        EMPTY = ""
        c2RssiAircraft_dBm = ""
        c2RssiGcs_dBm = ""
        c2NoiseAircraft_dBm = ""
        c2NoiseGcs_dBm = ""
        numGPSSat_nonDim = ""
        barometricPressure_psi = ""
        accBodyX_ftPerSec2 = ""
        accBodyY_ftPerSec2 = ""
        accBodyZ_ftPerSec2 = ""
        indicatedAirspeed_kts = ""

        tlog_name = os.path.basename(tlog_csv)

        flight_logs = open(mission_insight_csv, "r")
        tlog_file = open(tlog_csv, "r")

        # Get columns and assign to variables
        headers = flight_logs.readline().split(',')

        try:
            UVIN_COL = headers.index("UVIN")
            GUFI_COL = headers.index("GUFI")

        except ValueError:
            print("Invalid Mission Insight file.")

        # Iterate through flight log file and create output file for each log
        for line in flight_logs:

            values = line.split(",")

            date, time = tlog_name.split(' ')
            date = date.replace("-", "")
            time = time.replace("-", "")
            time = time[:4]

            out_file_name = "UTM-ACUASI-" + date + "-" + time + "-UASState.csv"

            # In the highly unlikely chance that two aircraft launched at the
            # exact same second, we name the second one different
            if not os.path.isfile(out_file_name):
                out_file = open(out_file_name, "w+")
            else:
                out_file_name = "UTM-ACUASI-" + date + "-" + time + "-UASState2.csv"
                out_file = open(out_file_name, "w+")

            UVIN = values[UVIN_COL]
            GUFI = values[GUFI_COL]

            # Write header
            header = "uvin,gufi,gpsWeek_wk,gpsSec_sec,variable,value\n"
            out_file.write(header)

            for line in tlog_file:
                row = line.split(",")

                # The non-standard camelCase naming convention is for easy reference to
                # NASA's variables.

                try:
                    if row[Arducopter.COL_J] == "mavlink_system_time_t":
                        # Time in us so convert down to seconds
                        unix_time = float(row[Arducopter.COL_L]) / 1E6

                        # Get GPS seconds by subtracting epoch difference
                        # and then adding 18 leap seconds to the UTC time
                        # Valid for the time these flights happened; may be wrong by
                        # December 2017; update leap_seconds variable if necessary
                        gpsSec_sec = unix_time - 315964800.0 + leap_seconds
                        gpsWeek_wk = int(gpsSec_sec // 604800)

                    if row[Arducopter.COL_J] == "mavlink_global_position_int_t":
                        vehiclePositionLat_deg = row[Arducopter.COL_N]
                        vehiclePositionLat_deg = (vehiclePositionLat_deg[:2] + "." +
                                                  vehiclePositionLat_deg[2:])
                        vehiclePositionLon_deg = row[Arducopter.COL_P]
                        vehiclePositionLon_deg = (vehiclePositionLon_deg[:4] + "." +
                                                  vehiclePositionLon_deg[4:])
                        # Alt in mm; convert to feet
                        gpsAltitude_ft = float(row[Arducopter.COL_R]) * 0.00328084
                        AboveTakeoffLocationAltitude_ft = float(row[Arducopter.COL_T]) * 0.00328084  # noqa

                        # Relative altitude
                        relAlt_ft = float(row[Arducopter.COL_T]) * 0.00328084

                    if row[Arducopter.COL_J] == "mavlink_gps_raw_int_t":
                        hdop_nonDim = float(row[Arducopter.COL_T]) / 100.0
                        vdop_nonDim = float(row[Arducopter.COL_V]) / 100.0
                        numGPSSat_nonDim = row[Arducopter.COL_AD]

                    if row[Arducopter.COL_J] == "mavlink_scaled_pressure_t":
                        # Given mmhg, convert to PSI
                        barometricPressure_psi = float(row[Arducopter.COL_N]) * 0.0193367778713

                    if row[Arducopter.COL_J] == "mavlink_radio_t":
                        # NASA variable asks for "C2 link RSSI measured in dBm at
                        # aircraft, but RSSI is a unitless indicator.
                        # RFD900 RSSI ranges from 0 to 255
                        c2RssiAircraft_dBm = row[Arducopter.COL_P]
                        c2RssiGcs_dBm = row[Arducopter.COL_R]
                        c2NoiseAircraft_dBm = row[Arducopter.COL_V]
                        c2NoiseGcs_dBm = row[Arducopter.COL_X]

                    if row[Arducopter.COL_J] == "mavlink_vfr_hud_t":
                        # Ground speed converted from m/s to ft/s
                        groundSpeed_ftPerSec = float(row[Arducopter.COL_N]) * 3.28084
                        # Using "heading" for this value
                        groundCourse_deg = row[Arducopter.COL_T]

                    if row[Arducopter.COL_J] == "mavlink_attitude_t":
                        roll_deg = row[Arducopter.COL_N]
                        pitch_deg = row[Arducopter.COL_P]
                        yaw_deg = row[Arducopter.COL_R]
                        rollRate_degPerSec = row[Arducopter.COL_T]
                        pitchRate_degPerSec = row[Arducopter.COL_V]
                        yawRate_degPerSec = row[Arducopter.COL_X]

                    if row[Arducopter.COL_J] == "mavlink_raw_imu_t":
                        # Tlog units are mg
                        accBodyX_ftPerSec2 = float(row[Arducopter.COL_N]) * 0.00328084
                        accBodyY_ftPerSec2 = float(row[Arducopter.COL_P]) * 0.00328084
                        accBodyZ_ftPerSec2 = float(row[Arducopter.COL_R]) * 0.00328084

                    if row[Arducopter.COL_J] == "mavlink_sys_status_t":
                        batteryVoltage_V = float(row[Arducopter.COL_T]) / 1000.0
                        batteryCurrent_A = row[Arducopter.COL_V]

                    if AboveTakeoffLocationAltitude_ft > 2.0:
                        aircraftAirborneState = "Airborne"
                    else:
                        aircraftAirborneState = "Ground"

                    # Check for second increment on unix time stamp
                    # write values every second
                    if unix_time - old_unix_time > 1:
                        old_unix_time = unix_time

                        writer = csv.writer(out_file, delimiter=',')

                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "vehiclePositionLat_deg", vehiclePositionLat_deg])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "vehiclePositionLon_deg", vehiclePositionLat_deg])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "vehiclePositionAlt_ft", gpsAltitude_ft])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "gpsAltitude_ft", gpsAltitude_ft])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "barometricAltitude_ft", relAlt_ft])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "barometricPressure_psi", barometricPressure_psi])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "groundSpeed_ftPerSec", groundSpeed_ftPerSec])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "groundCourse_deg", groundCourse_deg])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "hdop_nonDim", int(hdop_nonDim)])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "vdop_nonDim", int(vdop_nonDim)])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "numGPSSat_nonDim", numGPSSat_nonDim])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "roll_deg", roll_deg])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "pitch_deg", pitch_deg])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "yaw_deg", yaw_deg])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "rollRate_degPerSec", rollRate_degPerSec])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "pitchRate_degPerSec", pitchRate_degPerSec])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "yawRate_degPerSec", yawRate_degPerSec])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "accBodyX_ftPerSec2", accBodyX_ftPerSec2])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "accBodyY_ftPerSec2", accBodyY_ftPerSec2])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "accBodyZ_ftPerSec2", accBodyZ_ftPerSec2])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "batteryVoltage_V", batteryVoltage_V])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "batteryCurrent_A", batteryCurrent_A])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "aircraftControlMode", ])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "aircraftAirborneState", aircraftAirborneState])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "c2RssiAircraft_dBm", c2RssiAircraft_dBm])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "c2RssiGcs_dBm", c2RssiGcs_dBm])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "c2NoiseAircraft_dBm", c2NoiseAircraft_dBm])
                        writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                                        "c2NoiseGcs_dBm", c2NoiseGcs_dBm])

                except IndexError:
                    pass

            out_file.close()
            tlog_file.close()
        flight_logs.close()

    def auxiliary(self, mission_insight_csv, tlog_csv, gcs_location):
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
        # Mission Insight file is currently a single line per flight but that may change
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
                    if row[Arducopter.COL_J] == "mavlink_global_position_int_t":
                        # Assign this every time there's a non-zero value so it will end up
                        # being the last known GPS location which we assume to be the
                        # landing position
                        if row[Arducopter.COL_N] != 0 and row[Arducopter.COL_P] != 0:
                            landingPosLat_deg = row[Arducopter.COL_N]
                            landingPosLat_deg = landingPosLat_deg[:2] + "." + landingPosLat_deg[2:]
                            landingPosLon_deg = row[Arducopter.COL_P]
                            landingPosLon_deg = landingPosLon_deg[:4] + "." + landingPosLon_deg[4:]
                            landinPosAlt_ft = float(row[Arducopter.COL_R]) * 0.00328084

                        # Check for first non-zero point where altitude is above 50 m
                        # A priori we know the take off position is >100 m above sea level
                        # Assume that to be take-off position
                        if int(row[Arducopter.COL_N]) != 0 and int(row[Arducopter.COL_P]) != 0 and int(row[Arducopter.COL_R]) > 50000 and take_off_flag == 0:
                            takeoffPosLat_deg = row[Arducopter.COL_N]
                            takeoffPosLat_deg = takeoffPosLat_deg[:2] + "." + takeoffPosLat_deg[2:]
                            takeoffPosLon_deg = row[Arducopter.COL_P]
                            takeoffPosLon_deg = takeoffPosLon_deg[:4] + "." + takeoffPosLon_deg[4:]
                            takeoffPosAlt_ft = float(row[Arducopter.COL_R]) * 0.00328084
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

    def flight(self, mission_insight_csv, waypoints, tlog_csv):
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
