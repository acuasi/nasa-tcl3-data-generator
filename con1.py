"""Generate CON1 json file for NASA UTM TCL3."""
import sys
import csv
import json
from datetime import datetime

LEAP_SECS = 37
GPS_EPOCH_OFFSET = 315964800
GPS_LEAP_OFFSET = LEAP_SECS - 19

M_TO_FT = 3.28
KTS_TO_FT = 1.68781

def sys_boot_time(sys_time, gps_ms, gps_wks):
    """Use GPS time and system us time to calculate boot start time as a UTC timestamp."""
    gps_ts = round(gps_ms / 1000 + gps_wks * 86400 * 7)
    utc_ts = gps_ts + GPS_EPOCH_OFFSET + GPS_LEAP_OFFSET
    sys_ts = sys_time / 1.0E6
    boot_ts = utc_ts - sys_ts
    return boot_ts

def sys_ts_converter(sys_time, boot_ts):
    """Convert system time to UTC ISO8601 timestamp."""
    unix_ts = (sys_time / 1.0E6) + boot_ts
    return datetime.utcfromtimestamp(unix_ts).isoformat(timespec="milliseconds")+"Z"

def generate(mi_file_name, df_file_name, weather_file_name, field_vars_file_name, outfile_name):

    # Set up json objects
    ftype = "CON1"
    pdf = "UTM-ACUASI-CON-1.pdf"

    con1_data = {}
    basic = {}
    planned_bvlos_landing_point = []
    planned_bvlos_landing_point_alt = []
    actual_bvlos_landing_point = []
    landing_offset = []
    along_track_distance = 0
    distance_from_launch_site = 0
    bvlos_landing_zone_size = []
    bvlos_landing_zone_structure = [None]
    bvlos_ladnding_zone_people = [None]
    wx_bvlos_landing_zone = []
    c2 = []
    c2_packet_loss = []

    boot_ts_flag = 0

    gps = {"sys_time": 0, "gps_ms": 0, "gps_wk": 0, "lat": 0, "lon": 0, "alt": 0}

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

    with open(weather_file_name, "r") as weather_file:
        headers = weather_file.readline()

        for line in weather_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]
            ts = row[headers.index("Time of Report")]
            temp = float(row[headers.index("Outside Temp (degrees F)")])
            pressure = float(row[headers.index("Barometer (in)")])
            wind_speed = int(row[headers.index("Wind Speed (kts)")]) * KTS_TO_FT
            wind_dir = int(row[headers.index("Wind Direction (degrees)")])
            wx = {"temp": temp, "pressure": pressure, "windSpeed": wind_speed, "windDir": wind_dir}
            wx_zones = {"ts": ts, "wxBvlosLandingZone1Data": wx, "wxBvlosLandingZone2Data": wx}
            wx_bvlos_landing_zone.append(wx_zones)

    with open(field_vars_file_name, "r") as field_vars_file:
        headers = field_vars_file.readline()
        for line in field_vars_file:
            row = line.split(",")

        if row[0] == "plannedBvlosLandingPoint":
            loc = row[1].split(" ")
            planned_bvlos_landing_point.append({"lat": float(loc[0]), "lon": float(loc[1])})

        if row[0] == "plannedContingencyLandingPointAlt":
            planned_bvlos_landing_point_alt.append(float(row[1]))

        if row[0] == "landingOffset":
            landing_offset.append(float(row[1]))

        if row[0] == "alongTrackDistanceFlown":
            along_track_distance = float(row[1])

        if row[0] == "distanceFromLaunchSite":
            distance_from_launch_site = float(row[1])

        if row[0] == "bvlosLandingZoneSize":
            bvlos_landing_zone_size.append(float(row[1]))


    with open(df_file_name, "r") as dataflash_file:
        for line in dataflash_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            if row[0] == "EV":
                if row[2] == "10" or row[2] == "15":
                    arm_flag = 1

            if row[0] == "GPS":
                gps["sys_time"] = int(row[1])
                gps["gps_ms"] = int(row[3])
                gps["gps_wk"] = int(row[4])
                gps["lat"] = float(row[7])
                gps["lon"] = float(row[8])
                gps["alt"] = float(row[9])
                gps["speed"] = float(row[10]) # m/s
                gps["ground_course"] = float(row[11])
                gps["hdop"] = float(row[6])
                gps["num_sats"] = int(row[5])

                # Check for valid GPS position and time and then calculate timestamp of system boot
                if float(row[7]) != 0 and \
                   float(row[8]) != 0 and \
                   float(row[1]) != 0 and \
                    boot_ts_flag == 0:
                    boot_ts = sys_boot_time(int(gps["sys_time"]), int(gps["gps_ms"]),
                                            int(gps["gps_wk"]))
                    boot_ts_flag = 1

            # Check for "landing complete" event ID
            if row[0] == "EV" and row[2] == "18":
                landing_time = sys_ts_converter(int(row[1]), boot_ts)
                point = {"lat": gps["lat"], "lon": gps["lon"]}
                actual_bvlos_landing_point.append({"ts": landing_time,
                                                   "actualBvlosLandingPoint_deg": [point],
                                                   "actualBvlosLandingPointAlt_ft": [gps["alt"]]})

            # 1 Hz
            if row[0] == "RAD":
                if boot_ts_flag:
                    sys_time = int(row[1])
                    ts = sys_ts_converter(sys_time, boot_ts)
                    c2_rssi_gcs_dbm = (float(row[2]) / 1.9) - 127
                    c2_rssi_aircraft_dbm = (float(row[3]) / 1.9) - 127
                    c2_noise_gcs_dbm = (float(row[5]) / 1.9) - 127
                    c2_noise_aircraft_dbm = (float(row[6]) / 1.9) - 127
                    c2.append({"ts": ts, "c2RssiGcs_dBm": c2_rssi_gcs_dbm,
                               "c2RssiAircraft_dBm": c2_rssi_aircraft_dbm,
                               "c2NoiseGcs_dBm": c2_noise_gcs_dbm,
                               "c2NoiseAircraft_dBm": c2_noise_aircraft_dbm})

                    c2_packet_loss.append({"ts": ts, "c2PacketLossRateGcsPrct_nonDim": None,
                                           "c2PacketLossRateAircraftPrct_nonDim": None})

    con1_data["fType"] = ftype
    con1_data["basic"] = basic
    con1_data["UTM-TCL3-DMP-RevF-CONPDF"] = pdf
    con1_data["plannedBvlosLandingPoint_deg"] = planned_bvlos_landing_point
    con1_data["plannedBvlosLandingPointAlt_ft"] = planned_bvlos_landing_point_alt
    con1_data["actualBvlosLandingPoint"] = actual_bvlos_landing_point
    con1_data["landingOffset_ft"] = landing_offset
    con1_data["alongTrackDistanceFlown_ft"] = along_track_distance
    con1_data["distanceFromLaunchSite_ft"] = distance_from_launch_site
    con1_data["bvlosLandingZoneSize_ft"] = bvlos_landing_zone_size
    con1_data["bvlosLandingZoneStructure_deg"] = bvlos_landing_zone_structure
    con1_data["bvlosLandingZonePeople_deg"] = bvlos_ladnding_zone_people
    con1_data["wxBvlosLandingZone"] = wx_bvlos_landing_zone
    con1_data["c2"] = c2
    con1_data["c2PacketLoss"] = c2_packet_loss

    outfile = open(outfile_name, "w")
    json.dump(con1_data, outfile, indent=4)
    outfile.close()
