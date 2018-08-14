import helpers.constants as constants

def ptar_tlog(model, fileName):
    with open(fileName, "r") as tlog_file:
        tookOff = False
        for line in tlog_file:
            row = [item.strip() for item in line.split(",")]

            if not tookOff and row[constants.COL_J] == "mavlink_global_position_int_t":
                vehicle_pos_lat_deg = row[constants.COL_N]
                latitude = float(vehicle_pos_lat_deg[:2] + "." + vehicle_pos_lat_deg[2:])

                vehicle_pos_lon_deg = row[constants.COL_P]
                longitude = float(vehicle_pos_lon_deg[:4] + "." + vehicle_pos_lon_deg[4:])

                if latitude == 0 or longitude == 0:
                    continue

                model["plannedContingency"]["plannedContingencyLandingPoint_deg"] = [{
                    "lat": float(latitude),
                    "lon": float(longitude)
                }]

                altitude = float(row[constants.COL_R]) * 0.00328084
                model["plannedContingency"]["plannedContingencyLandingPointAlt_ft"] = [altitude]
                tookOff = True

            # This isn't the best way to set contingencyLanding to the last row, but it works
            if tookOff and row[constants.COL_J] == "mavlink_global_position_int_t":
                vehicle_pos_lat_deg = row[constants.COL_N]
                latitude = float(vehicle_pos_lat_deg[:2] + "." + vehicle_pos_lat_deg[2:])

                vehicle_pos_lon_deg = row[constants.COL_P]
                longitude = float(vehicle_pos_lon_deg[:4] + "." + vehicle_pos_lon_deg[4:])

                if latitude == 0 or longitude == 0:
                    continue

                contingencyLandingPoint_deg = {
                    "lat": float(latitude),
                    "lon": float(longitude)
                }

                altitude = float(row[constants.COL_R]) * 0.00328084
                contingencyLandingPointAlt_ft = [altitude]

                timestamp = row[constants.COL_A] + "Z"
                model["contingencyLanding"] = [{
                    "ts": timestamp,
                    "contingencyLandingPoint_deg": [contingencyLandingPoint_deg],
                    "contingencyLandingPointAlt_ft": contingencyLandingPointAlt_ft
                }]
    return model
