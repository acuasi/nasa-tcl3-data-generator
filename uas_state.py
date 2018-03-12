# Convert a csv telemetry log file to the NASA
# UAS state formatted CSV file
#
# File name format: UTM-ACUASI-{dateOfFlight}-{takeoffTime}-UASState.csv
# where dateOfFlight & takeOffTime can be pulled from the name of the tlog file
#
# Values to pass to the script:
# Mission Insight csv, Mission Planner tlog file converted to csv
#
# Read the date from the TLog file
# Split into Date and Time
# Date is Flight Date and Time is Takeoff time

import os
import csv

def state(mission_insight_csv, tlog_csv):

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

    # Initialize unix time stamp to 0
    old_time_unix_usec = 0
    time_unix_usec = 0

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
                if row[COL_J] == "mavlink_system_time_t":
                    # Time in us so convert down to seconds
                    time_unix_usec = float(row[COL_L]) / 1E6
                    # Get GPS seconds by subtracting epoch difference
                    # and then adding 18 leap seconds to the UTC time
                    # Valid for the time these flights happened; may be wrong by
                    # December 2017; update leap_seconds variable if necessary
                    gpsSec_sec = time_unix_usec - 315964800.0 + leap_seconds
                    gpsWeek_wk = int(gpsSec_sec // 604800)

                if row[COL_J] == "mavlink_global_position_int_t":
                    vehiclePositionLat_deg = row[COL_N]
                    vehiclePositionLat_deg = (vehiclePositionLat_deg[:2] + "." +
                                              vehiclePositionLat_deg[2:])
                    vehiclePositionLon_deg = row[COL_P]
                    vehiclePositionLon_deg = (vehiclePositionLon_deg[:4] + "." +
                                              vehiclePositionLon_deg[4:])
                    # Alt in mm; convert to feet
                    gpsAltitude_ft = float(row[COL_R]) * 0.00328084
                    AboveTakeoffLocationAltitude_ft = float(row[COL_T]) * 0.00328084  # noqa

                    # Relative altitude
                    relAlt_ft = float(row[COL_T]) * 0.00328084

                if row[COL_J] == "mavlink_gps_raw_int_t":
                    hdop_nonDim = float(row[COL_T]) / 100.0
                    vdop_nonDim = float(row[COL_V]) / 100.0
                    numGPSSat_nonDim = row[COL_AD]

                if row[COL_J] == "mavlink_scaled_pressure_t":
                    # Given mmhg, convert to PSI
                    barometricPressure_psi = float(row[COL_N]) * 0.0193367778713

                if row[COL_J] == "mavlink_radio_t":
                    # NASA variable asks for "C2 link RSSI measured in dBm at
                    # aircraft, but RSSI is a unitless indicator.
                    # RFD900 RSSI ranges from 0 to 255
                    c2RssiAircraft_dBm = row[COL_P]
                    c2RssiGcs_dBm = row[COL_R]
                    c2NoiseAircraft_dBm = row[COL_V]
                    c2NoiseGcs_dBm = row[COL_X]

                if row[COL_J] == "mavlink_vfr_hud_t":
                    # Ground speed converted from m/s to ft/s
                    groundSpeed_ftPerSec = float(row[COL_N]) * 3.28084
                    # Using "heading" for this value
                    groundCourse_deg = row[COL_T]

                if row[COL_J] == "mavlink_attitude_t":
                    roll_deg = row[COL_N]
                    pitch_deg = row[COL_P]
                    yaw_deg = row[COL_R]
                    rollRate_degPerSec = row[COL_T]
                    pitchRate_degPerSec = row[COL_V]
                    yawRate_degPerSec = row[COL_X]

                if row[COL_J] == "mavlink_raw_imu_t":
                    # Tlog units are mg
                    accBodyX_ftPerSec2 = float(row[COL_N]) * 0.00328084
                    accBodyY_ftPerSec2 = float(row[COL_P]) * 0.00328084
                    accBodyZ_ftPerSec2 = float(row[COL_R]) * 0.00328084

                if row[COL_J] == "mavlink_sys_status_t":
                    batteryVoltage_V = float(row[COL_T]) / 1000.0
                    batteryCurrent_A = row[COL_V]

                if AboveTakeoffLocationAltitude_ft > 2.0:
                    aircraftAirborneState = "Airborne"
                else:
                    aircraftAirborneState = "Ground"

                # Check for second increment on unix time stamp
                # write values every second
                if time_unix_usec - old_time_unix_usec > 1:
                    old_time_unix_usec = time_unix_usec

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
                    # writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                    #                 "aboveTerrainAltitude_ft", EMPTY])
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
                    # writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                    #                 "motor1ControlThrottleCommand", motor1ControlThrottleCommand])
                    # writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                    #                 "motor2ControlThrottleCommand", motor2ControlThrottleCommand])
                    # writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                    #                 "motor3ControlThrottleCommand", motor3ControlThrottleCommand])
                    # writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                    #                 "motor4ControlThrottleCommand", motor4ControlThrottleCommand])
                    # writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                    #                 "motor5ControlThrottleCommand", motor5ControlThrottleCommand])
                    # writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                    #                 "motor6ControlThrottleCommand", motor6ControlThrottleCommand])
                    # writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                    #                 "motor7ControlThrottleCommand", motor7ControlThrottleCommand])
                    # writer.writerow([UVIN, GUFI, gpsWeek_wk, gpsSec_sec,
                    #                 "motor8ControlThrottleCommand", motor8ControlThrottleCommand])
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