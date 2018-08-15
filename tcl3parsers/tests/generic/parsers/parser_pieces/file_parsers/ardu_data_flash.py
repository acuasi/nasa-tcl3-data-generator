import json
import helpers.system_helpers

def ardu_data_flash(model, fileName):
    """Parse arducopter dataflash log file (.log format) and add to cns data JSON"""
    radio_count = 0
    arm_flag = 0
    boot_ts_flag = 0
    ac_mode = ""
    with open(fileName, "r") as dataflash_file:
        gps = {"sys_time": 0, "gps_ms": 0,
               "gps_wk": 0, "lat": 0, "lon": 0, "alt": 0}
        emptyFieldIfNull('contingencyLanding', model)
        emptyFieldIfNull('contingencyCause', model)
        emptyFieldIfNull('contingencyResponse', model)
        model['plannedContingency']["plannedContingencyLandingPoint_deg"] = []
        model['plannedContingency']["plannedContingencyLandingPointAlt_ft"] = []

        for line in dataflash_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]

            if row[0] == "EV":
                if row[2] == "10" or row[2] == "15":
                    arm_flag = 1

            # 5 Hz
            if row[0] == "GPS":
                gps["sys_time"] = int(row[1])
                gps["gps_ms"] = int(row[3])
                gps["gps_wk"] = int(row[4])
                gps["lat"] = "{0:.7f}".format(float(row[7]))
                gps["lon"] = "{0:.7f}".format(float(row[8]))
                gps["alt"] = float(row[9])
                gps["speed"] = float(row[10])  # m/s
                gps["ground_course"] = float(row[11])
                gps["hdop"] = float(row[6])
                gps["num_sats"] = int(row[5])

                # Check for valid GPS position and time and then calculate timestamp of system boot
                if float(row[7]) != "0" and float(row[8]) != "0" and float(row[1]) != 0 and boot_ts_flag == 0:
                    boot_ts = helpers.system_helpers.sys_boot_time(int(gps["sys_time"]), int(gps["gps_ms"]),
                                                                   int(gps["gps_wk"]))
                    boot_ts_flag = 1

            if arm_flag and boot_ts_flag:
                cl_point = {
                "lat": float(gps["lat"]),
                "lon": float(gps["lon"])
                }
                cl_point_alt = [gps["alt"]]
                model['plannedContingency']["plannedContingencyLandingPoint_deg"].append(cl_point)
                model['plannedContingency']["plannedContingencyLandingPointAlt_ft"].append(cl_point_alt)

            # 1 Hz
            if row[0] == "RAD":
                # Create 60 second loop for reporting default contingency values
                loopTime = 60
                if radio_count == loopTime - 1:
                    ts = helpers.system_helpers.sys_ts_converter(
                        int(row[1]), boot_ts)
                    model["contingencyLanding"].append({
                        "ts": ts,
                        "contingencyLandingPoint_deg": [cl_point],
                        "contingencyLandingPointAlt_ft": cl_point_alt
                    })
                    model["contingencyCause"].append({
                        "ts": ts,
                        "contingencyCause_nonDim": [0]
                    })
                    model["contingencyResponse"].append({
                        "ts": ts,
                        "contingencyResponse_nonDim": 0
                    })
                radio_count = (radio_count + 1) % loopTime

            # Only add timeManeuverVerification if it is in the spec
            if "timeManeuverVerification" in model.keys() and row[0] == "MODE":
                if ac_mode == "Loiter" or ac_mode == "Stabilize":
                    if row[2] == "Auto":
                        ts = helpers.system_helpers.sys_ts_converter(int(row[1]), boot_ts)
                        model["timeManeuverVerification"].append({"ts": ts})

                if ac_mode == "RTL" or ac_mode == "Auto":
                    if row[2] == "Guided":
                        ts = helpers.system_helpers.sys_ts_converter(int(row[1]), boot_ts)
                        model["timeManeuverVerification"].append({"ts": ts})
                ac_mode = row[2]

        return model


def emptyFieldIfNull(field, model):
    """Get rid of the 'None' default value so that data can be appended"""
    if field in model:
        model[field] = [] if model[field] == [None] else model[field]
    return model
