import csv
import itertools


def dji_litchi(model, fileName):
    tookOff = False
    with open(fileName, "r") as litchi:
        litchi_reader = csv.DictReader(litchi)
        for currentRow, nextRow in pairwise(litchi_reader):
            currentTimeStamp = currentRow["datetime(utc)"].replace(" ", "T")
            if currentRow["flightmode"] == "TakeOff" and nextRow["flightmode"] != "TakeOff":
                tookOff = True
                model["plannedContingency"]["plannedContingencyLandingPoint_deg"].append({
                    "lat": float(currentRow["latitude"]),
                    "lon": float(currentRow["longitude"])
                })
                model["plannedContingency"]["plannedContingencyLandingPointAlt_ft"].append(float(currentRow["altitude(feet)"]))
            if tookOff and currentRow["isMotorsOn"] == "1" and nextRow["isMotorsOn"] == "0":
                contingencyLandingPoint_deg = {
                    "lat": float(nextRow["latitude"]),
                    "lon": float(nextRow["longitude"])
                }

                contingencyLandingPointAlt_ft = [float(nextRow["altitude(feet)"])]

                model["contingencyLanding"].append({
                    "ts": currentTimeStamp,
                    "contingencyLandingPoint_deg": [contingencyLandingPoint_deg],
                    "contingencyLandingPointAlt_ft": contingencyLandingPointAlt_ft
                })

    return model


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
