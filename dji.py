import csv  # noqa
import datetime
import json
"""Contains DJI Class with methods for parsing aircraft log files
and creating specific files for the NASA UTM TCL3 campaign.
"""

# Handle leap seconds somehow
# One option:
# import wget
# download this file: https://www.ietf.org/timezones/data/leap-seconds.list
# parse to find most recent leap second number

FRAME = 0
WEIGHT = 1


class InvalidLog(Exception):
    """Create custom exeception."""

    pass


class Dji():
    """Methods for parsing DJI csv-converted binary log files."""

    leap_seconds = 18

    def state(self, dji_csv_log_file, mission_insight_file):
        """Create UASState JSON file for NASA UTM TCL3.

        Args:
            param1 (string): Path name for DJI CSV log file.
            param2 (string): Path name for Mission Insight file.

        Returns:
            null
        """
        aircraftAirborneState = "Ground" # noqa

        f = open(dji_csv_log_file, "r")
        m = open(mission_insight_file, "r")

        # Read values from Mission Insight File
        mi_headers = m.readline().split(",")

        try:
            UVIN_COL = mi_headers.index("UVIN") # noqa
            GUFI_COL = mi_headers.index("GUFI") # noqa

        except ValueError:
            raise InvalidLog("Invalid Mission Insight log.")

        mi_values = m.readline().split(",")

        UVIN = mi_values[UVIN_COL] # noqa
        GUFI = mi_values[GUFI_COL] # noqa

        # Read headers and create a map bewteen header name and column number
        header_map = {}
        headers = f.readline()
        headers_list = headers.split(",")
        for header in headers_list:
            header_map[header] = headers_list.index(header)

        # Loop through file looking for two conditions:
        # * Non-empty string for GPS Time
        # * GPS Time > 0, indicating GPS lock
        for line in f:
            values_list = line.split(",")
            gps_time = values_list[header_map["GPS:Time"]]
            if gps_time and int(gps_time) > 0:
                break
            else:
                raise InvalidLog("No GPS lock.")

        # Get string value of valid gps date time
        gps_date_timestamp = values_list[header_map["GPS:dateTimeStamp"]]

        # Create a date time object from the string value
        gps_date = datetime.datetime.strptime(gps_date_timestamp,
                                              "%Y-%m-%dT%H:%M:%SZ")
        unix_time = gps_date.timestamp()
        gpsSec = unix_time - 315964800.0 + self.leap_seconds # noqa
        gpsWeek = int(gpsSec // 604800) # noqa

        # Date time is in ISO 8601 format; convert for NASA file name
        date, time = gps_date_timestamp.split("T")
        date = date.replace("-", "")
        time = time.replace("-", "").replace(":", "")[:-3]

        file_name = "UTM-ACUASI-{}-{}-UASState.csv".format(date, time)
        csvfile = open(file_name, "w")
        wr = csv.writer(csvfile, delimiter=",")
        header = "uvin,gufi,gpsWeek_wk,gpsSec_sec,variable,value\n"
        wr.writerow(header)

        # Loop through the rest of the file, convert parameters as required and
        # write to output file
        for line in f:
            values_list = line.split(",")
            vehiclePositionLat_deg = values_list[header_map["GPS:Lat"]] # noqa
            vehiclePositionLon_deg = values_list[header_map["GPS:Lon"]] # noqa
            vehiclePositionAlt_ft = values_list[header_map["relativeHeight"]] # noqa
            gpsAltitude_ft = values_list[header_map["GPS:heightMSL"]] # noqa
            hdop_nonDim = values_list[header_map["GPS:DOP:H"]] # noqa
            numGPSvis = values_list[header_map["GPS:Visible:GPS"]] # noqa
            numGLNASvis = values_list[header_map["GPS:Visible:GLNAS"]] # noqa
            numGpsSat_nonDim = numGPSvis + numGLNASvis # noqa
            roll_deg = values_list[header_map["Roll"]]
            pitch_deg = values_list[header_map["Pitch"]]
            yaw_deg = values_list[header_map["Yaw"]]
            mtr1CntrlThrtlCmd = values_list[header_map["Motor:PPMrecv:RFront"]] # noqa
            mtr2CntrlThrtlCmd = values_list[header_map["Mtr:PMrev:LFront"]] # noqa
            mtr3CntrlThrtlCmd = values_list[header_map["Motor:PPMrecv:LBack"]] # noqa
            mtr4CntrlThrtlCmd = values_list[header_map["Motor:PPMrecv:RBack"]] # noqa
            batteryVoltage_V = values_list[header_map["Battery:volts:total"]] # noqa
            batteryCurrent_A = values_list[header_map["Battery:current"]] # noqa

            if vehiclePositionAlt_ft > 3:
                aircraftAirborneState = "Airborne" # noqa

            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "vehiclePositionLat_deg", vehiclePositionLat_deg])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "vehiclePositionLon_deg", vehiclePositionLon_deg])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "gpsAltitude", gpsAltitude_ft])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "hdop_nonDim", hdop_nonDim])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "numGpsSat_nonDim", numGpsSat_nonDim])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "roll_deg", roll_deg])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "pitch_deg", pitch_deg])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "yaw_deg", yaw_deg])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "motor1ControlThrottleCommand",
                         mtr1CntrlThrtlCmd])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "motor2ControlThrottleCommand",
                         mtr2CntrlThrtlCmd])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "motor3ControlThrottleCommand",
                         mtr3CntrlThrtlCmd])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec,
                        "motor4ControlThrottleCommand",
                         mtr4CntrlThrtlCmd])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec, "batteryVoltage_V",
                        batteryVoltage_V])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec, "batteryCurrent_A",
                        batteryCurrent_A])
            wr.writerow([UVIN, GUFI, gpsWeek, gpsSec, "aircraftAirborneState",
                        aircraftAirborneState])

        f.close()

    def auxiliary(self, dji_csv_log_file, mission_insight_file, gcs_location):
        """Create the UASAuxiliary file for NASA UTM TCL3.

        Args:
            param1 (string): Path name for DJI CSV log file.
            param2 (string): Path name for Mission Insight file.
            param2 (dict): GCS location: lat, lon and altitude.

        Returns:
            null
        """
        takeoff = False

        f = open(dji_csv_log_file, "r")
        m = open(mission_insight_file, "r")

        # Read values from Mission Insight File
        mi_headers = m.readline().split(",")

        try:
            UVIN_COL = mi_headers.index("UVIN") # noqa
            GUFI_COL = mi_headers.index("GUFI") # noqa

        except ValueError:
            raise InvalidLog("Invalid Mission Insight log.")

        mi_values = m.readline().split(",")

        UVIN = mi_values[UVIN_COL] # noqa
        GUFI = mi_values[GUFI_COL] # noqa

        # NASA no longer requires us to generate aircraft specifications file
        # for each flight, so we'll need to store data about each configuration
        # in this dictionary. Populate from configuration file once finalized.
        aircraft = {"N249UA": ['helicopter', 17.0],
                    "N254MH": ['multirotor', 11.2],
                    "N255MH": ['multirotor', 11.4]
                    }

        # Placeholder until aircraft dictionary is properly populated with all
        # configuration values
        n_number = "N254MH"

        typeOfOperation = "Live"                         # noqa
        takeOffWeight_lb = aircraft[n_number][WEIGHT]    # noqa
        typeOfAirframe = aircraft[n_number][FRAME]       # noqa
        gcsPosLat_deg = gcs_location['latitude']         # noqa
        gcsPosLon_deg = gcs_location['longitude']        # noqa
        gcsPosAlt_ft = gcs_location['altitude']          # noqa
        # Change this once drop-down menu added to GUI
        testIdentifiers = "CNS1"

        # Read headers and create a map bewteen header name and column number
        header_map = {}
        headers = f.readline()
        headers_list = headers.split(",")
        for header in headers_list:
            header_map[header] = headers_list.index(header)

        for line in f:
            values_list = line.split(",")
            flight_mode = values_list[header_map["flyCState"]]
            gps_lat = values_list[header_map["GPS:Lat"]]
            gps_lon = values_list[header_map["GPS:Lon"]]
            gps_alt = values_list[header_map["GPS:heightMSL"]]

            if "takeoff" in flight_mode.lower() and not takeoff:
                takeoffPosLat_deg = gps_lat             					# noqa
                takeoffPosLon_deg = gps_lon             					# noqa
                takeoffPosAlt_ft = gps_alt              					# noqa
            	takeoffTime = values_list[header_map[GPS:dateTimeStamp]]    # noqa
                takeoff = True

            # Assign every time there's a non-zero value so it ends
            # up being the last known GPS location which we assume to be
            # the landing location
            if gps_lat != 0 and gps_lon != 0:
                landingPosLat_deg = gps_lat             					# noqa
                landingPosLon_deg = gps_lon             					# noqa
                landingPosAlt_deg = gps_alt             					# noqa
                landingTime = values_list[header_map[GPS:dateTimeStamp]]    # noqa

        aux_values["typeOfOperation"] = typeOfoperation
        aux_values["flightTestCardName"] = flightTestCardName
        aux_values["testIdentifiers"] = testIdentifiers
        aux_values["takeOffWeight_lb"] = takeOffWeight_lb
        aux_values["takeOffTime"] = takeoffTime
        aux_values["takeoffPosLat_deg"] = takeoffPosLat_deg
        aux_values["takeoffPosLon_deg"] = takeoffPosLon_deg
        aux_values["takeoffPosAlt_ft"] = takeoffPosAlt_ft
        aux_values["landingTime"] = landingTime
        aux_values["landingPosLat_deg"] = landingPosLat_deg
        aux_values["landingPosLon_deg"] = landingPosLon_deg
        aux_values["landingPosAlt_ft"] = landingPosAlt_deg
        aux_values["gcsPosLat_deg"] = gcsPosAlt_ft
        aux_values["gcsPosLon_deg"] = gcsPosLon_deg
        aux_values["gcsPosAlt_ft"] = gcsPosAlt_ft

    def flight(self, dji_csv_log_file, mission_insight_file, waypoints):
        """Create the UASFlight file for NASA UTM TCL3.

        Args:
            param1 (string): Path name for DJI CSV log file.
            param2 (string): Path name for Mission Insight file.
            param3 (string): Path name for Waypoints file.

        Returns:
            null
        """
