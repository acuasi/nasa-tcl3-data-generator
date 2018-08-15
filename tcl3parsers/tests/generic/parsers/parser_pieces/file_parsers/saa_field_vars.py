import csv
import re
import helpers.field_var_helpers as field_var

def saa_field_vars(model, fileName):
    with open(fileName, "r") as field_vars_file:
        fieldVars = csv.DictReader(field_vars_file)
        for fieldVar in fieldVars:
            model, targetFound = searchModel(model, fieldVar["Variable"], fieldVar["Value"], fileName=fileName)
            if not targetFound:
                print("Field Variable [", fieldVar["Variable"], "] not found in expected JSON, skipping...")

    return model

def searchModel(model, targetName, targetValue, targetFound=False, fileName=""):
    for masterVariable, innerScope in model.items():
        if masterVariable == targetName:
            model, hardCodedVariableMatch = checkHardCodedMatches(model, targetName, targetValue)
            if hardCodedVariableMatch:
                return model, True

            if targetValue != "Null" and targetValue != "null":
                if masterVariable == "intruderVelNorth_ftPerSec":
                    print(masterVariable, targetName, targetValue)
                convertedToNumber, targetValue = field_var.maybeNumber(targetValue)

                if not convertedToNumber and field_var.noDoubleDigitDayDateFormat.match(targetValue):
                    # date in (incorrect) format: YYYY-MM-DTHH:MM:SS.000Z
                    noDoubleDigitDayInDate = field_var.noDoubleDigitDayDateFormat.match(targetValue)
                    targetValue = noDoubleDigitDayInDate.group(1) + "-0" + noDoubleDigitDayInDate.group(2) + noDoubleDigitDayInDate.group(3)
                elif not convertedToNumber and field_var.noSecondsDateFormat.match(targetValue):
                    # date in (incorrect) format: YYYY-MM-DD22:00.000Z
                    noSecondsInDate = field_var.noSecondsDateFormat.match(targetValue)
                    targetValue = noSecondsInDate.group(1) + ":00" + noSecondsInDate.group(2)
                elif not convertedToNumber and field_var.dateWithOnlyTime.match(targetValue):
                    dateMatchFromFileName = re.match(r".*([0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}).*", fileName)
                    if dateMatchFromFileName:
                        targetValue = dateMatchFromFileName.group(1) + "T" + targetValue + ".000Z"
                    else:
                        print("ERROR: Field Var:", targetName ,"contains an improperly formed date that can't be corrected.")
                        return model, True
            else:
                return model, True

            if isinstance(model[masterVariable], list):
                model[masterVariable].append(targetValue)
            else:
                model[masterVariable] = targetValue

            return model, True
        elif isinstance(innerScope, dict):
            model[masterVariable], targetFound = searchModel(model[masterVariable], targetName, targetValue, targetFound, fileName)
            if targetFound:
                return model, targetFound

    return model, targetFound

def checkHardCodedMatches(model, targetName, targetValue):
    matchedCase = True
    if targetName == "geoFenceType_nonDim" and targetValue.lower() == "cylinder":
        model[targetName] = 0
    else:
        matchedCase = False

    return model, matchedCase
