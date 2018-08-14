import csv
import helpers.field_var_helpers as field_var

def generic_field_vars(model, fileName):
    with open(fileName, "r") as field_vars_file:
        fieldVars = csv.DictReader(field_vars_file)
        for fieldVar in fieldVars:
            fieldVar = {field: value for field, value in fieldVar.items() if field and value}

            caseHandled, model = hardCodedVariableCases(model, fieldVar)

            if not caseHandled and 'Value' in fieldVar and fieldVar['Variable'] in model.keys():
                success, fieldVar['Value'] = field_var.maybeNumber(fieldVar['Value'])
                if success and fieldVar['Value'] == 0:
                    # fieldVar['Value'] = {}
                    continue
                elif not success:
                    success, fieldVar['Value'] = field_var.maybeGetLatLonDict(fieldVar['Value'])

                caseHandled, model = hardCodedVariableCases(model, fieldVar)

                if not caseHandled and isinstance(model[fieldVar['Variable']], list):
                    model[fieldVar['Variable']].append(fieldVar['Value'])
                else:
                    model[fieldVar['Variable']] = fieldVar['Value']
    return model

def hardCodedVariableCases(model, fieldVar):
    caseHandled = True
    if "Timestamp" not in fieldVar:
        return False, model

    if fieldVar['Variable'] == "declaredEmergency":
        model["declaredEmerg"].append({
            "ts": fieldVar['Timestamp'] if fieldVar['Timestamp'] != '0' else None,
            "declaredEmergency": fieldVar['Value']
        })
    elif fieldVar['Variable'] == "contingencyLoiterAlt_ft":
        model["contingencyLoiterAlt"].append({
            "ts": fieldVar['Timestamp'] if fieldVar['Timestamp'] != '0' else None,
            "contingencyLoiterAlt_ft": [float(fieldVar['Value'].strip('"'))]
        })
    elif fieldVar['Variable'] == "contingencyLoiterRadius_ft":
        model["contingencyLoiterRadius"].append({
            "ts": fieldVar['Timestamp'] if fieldVar['Timestamp'] != '0' else None,
            "contingencyLoiterRadius_ft": [float(fieldVar['Value'])]
        })
    elif fieldVar['Variable'] == "contingencyLoiterType_nonDim":
        model["contingencyLoiterType"].append({
            "ts": fieldVar['Timestamp'] if fieldVar['Timestamp'] != '0' else None,
            "contingencyLoiterType_nonDim": int(fieldVar['Value'])
        })
    elif fieldVar['Variable'] == "contingencyResponse_nonDim":
        model["contingencyResponse"].append({
            "ts": fieldVar['Timestamp'] if fieldVar['Timestamp'] != '0' else None,
            "contingencyResponse_nonDim": int(fieldVar['Value'])
        })
    elif fieldVar['Variable'] == "contingencyCause_nonDim":
        model["contingencyCause"].append({
            "ts": fieldVar['Timestamp'] if fieldVar['Timestamp'] != '0' else None,
            "contingencyCause_nonDim": [int(fieldVar['Value'])]
        })
    else:
        caseHandled = False
    return caseHandled, model
