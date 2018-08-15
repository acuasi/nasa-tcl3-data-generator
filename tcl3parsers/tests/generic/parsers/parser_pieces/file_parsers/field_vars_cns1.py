RFD900 = """
The two RFD900 Radio Modems are a high powered 900Mhz, ISM band radio modems
designed for long range communication operating between 902 to 928Mhz at a 57600
baud rate.
"""

UAVCAST = """
The UAVCast is a system designed to provide HD video as well as telemetry over a 4G/LTE
cellular network. The UAVCast Client software will expose the MAVLink channel as a local
TTP server.
"""

PRIM_CMD = """Takeoff in Auto mode and begin flight plan."""

REDUN_CMD = """Fly to POI in Guided mode."""

LINK = {"RFD900": RFD900, "UAVCast": UAVCAST}

def field_vars_cns1(model, fileName):
    PRIMARY = ""
    REDUN = ""
    ac_link = "Primary"
    with open(fileName, "r") as field_vars_file:
        headers = field_vars_file.readline()
        for line in field_vars_file:
            row = [item.strip() for item in line.split(",")]

            if row[0] == "contingencyCause_nonDim":
                variable = "contingencyCause_nonDim"
                value = int(row[1])
                if value:
                    ts = row[2]
                    model["contingencyCause"].append({"ts": ts, variable: [value]})

            elif row[0] == "contingencyResponse_nonDim":
                variable = "contingencyResponse_nonDim"
                value = int(row[1])
                if value:
                    ts = row[2]
                    model["contingencyResponse"].append({"ts": ts, variable: value})

            elif row[0] == "cns1TestType_nonDim":
                variable = "cns1TestType_nonDim"
                value = int(row[1])
                ts = row[2]
                model["cns1TestType"].append({"ts": ts, variable: value})

            elif row[0] == "PrimaryLink":
                PRIMARY = LINK[row[1]].strip()

            elif row[0] == "SecondaryLink":
                REDUN = LINK[row[1]].strip()

            elif row[0] == "timeManeuverCommandSent":
                variable = "timeManeuverCommandSent"
                ts = row[2]
                model["timeManeuverCommandSent"].append({"ts": ts})
                if ac_link == "Primary":
                    model["primaryLinkDescription"].append({"ts": ts, "primaryLinkDescription": PRIMARY})
                    model["maneuverCommand"].append({"ts": ts, "maneuverCommand": PRIM_CMD})
                    value = {"ts": ts, "estimatedTimeToVerifyManeuver_sec": 1.500}
                    model["estimatedTimeToVerifyManeuver"].append(value)
                elif ac_link == "Redundant":
                    model["redundantLinkDescription"].append({"ts": ts, "redundantLinkDescription": REDUN})
                    model["maneuverCommand"].append({"ts": ts, "maneuverCommand": REDUN_CMD})
                    value = {"ts": ts, "estimatedTimeToVerifyManeuver_sec": 0.250}
                    model["estimatedTimeToVerifyManeuver"].append(value)

            elif row[0] == "timePrimaryLinkDisconnect":
                variable = "timePrimaryLinkDisconnect"
                ts = row[2]
                model["timePrimaryLinkDisconnect"].append({"ts": ts})

            elif row[0] == "timeRedundantLinkSwitch":
                if ac_link == "Primary":
                    variable = "timeRedundantLinkSwitch"
                    ts = row[2]
                    model["timeRedundantLinkSwitch"].append({"ts": ts})
                    ac_link = "Redundant"
                else:
                    return False
            else:
                return False

    return model
