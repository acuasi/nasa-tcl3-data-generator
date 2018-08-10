import helpers.system_helpers as system_helpers

def con1_data_flash(model, fileName):
    with open(fileName, "r") as dataflash_file:
        gps = {}
        boot_ts_flag = 0
        for line in dataflash_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

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
                    boot_ts = system_helpers.sys_boot_time(int(gps["sys_time"]), int(gps["gps_ms"]), int(gps["gps_wk"]))
                    boot_ts_flag = 1

            # Check for "landing complete" event ID
            if row[0] == "EV" and row[2] == "18":
                landing_time = system_helpers.sys_ts_converter(int(row[1]), boot_ts)
                point = {"lat": gps["lat"], "lon": gps["lon"]}
                model["actualBvlosLandingPoint"].append({
                    "ts": landing_time,
                    "actualBvlosLandingPoint_deg": [point],
                    "actualBVLOSLandingPointAlt_ft": [gps["alt"]]
                })

            # 1 Hz
            if row[0] == "RAD":
                if boot_ts_flag:
                    sys_time = int(row[1])
                    ts = system_helpers.sys_ts_converter(sys_time, boot_ts)
                    c2_rssi_gcs_dbm = (float(row[2]) / 1.9) - 127
                    c2_rssi_aircraft_dbm = (float(row[3]) / 1.9) - 127
                    c2_noise_gcs_dbm = (float(row[5]) / 1.9) - 127
                    c2_noise_aircraft_dbm = (float(row[6]) / 1.9) - 127
                    model["c2"].append({
                        "ts": ts,
                        "c2RssiGcs_dBm": c2_rssi_gcs_dbm,
                        "c2RssiAircraft_dBm": c2_rssi_aircraft_dbm,
                        "c2NoiseGcs_dBm": c2_noise_gcs_dbm,
                        "c2NoiseAircraft_dBm": c2_noise_aircraft_dbm
                    })

                    model["c2PacketLoss"].append({
                        "ts": ts,
                        "c2PacketLossRateGcsPrct_nonDim": None,
                        "c2PacketLossRateAircraftPrct_nonDim": None
                    })
    return model
