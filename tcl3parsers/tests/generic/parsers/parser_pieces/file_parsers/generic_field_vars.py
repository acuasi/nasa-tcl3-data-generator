import csv

def generic_field_vars(model, fileName):
    with open(fileName, "r") as field_vars_file:
        fieldVars = csv.DictReader(field_vars_file)
        for fieldVar in fieldVars:
            fieldVar = {field: value for field, value in fieldVar.items() if field and value}
            if 'Value' in fieldVar and fieldVar['Variable'] in model.keys():
                success, fieldVar['Value'] = maybeNumber(fieldVar['Value'])
                if success and fieldVar['Value'] == 0:
                    fieldVar['Value'] = {}
                elif not success:
                    success, fieldVar['Value'] = maybeGetLatLonDict(fieldVar['Value'])

                if isinstance(model[fieldVar['Variable']], list):
                    model[fieldVar['Variable']].append(fieldVar['Value'])
                else:
                    model[fieldVar['Variable']] = fieldVar['Value']
    return model

def maybeNumber(value):
    try:
        value = float(value)
        if value == int(value):
            value = int(value)
    except ValueError:
        return False, value
    return True, value

def maybeGetLatLonDict(value):
    try:
        if " " in value:
            potentialLatLon = value.split(" ")
        if " " not in value or len(potentialLatLon) != 2:
            return False, value

        lat = float(potentialLatLon[0])
        lon = float(potentialLatLon[1])
        if lat < -90 or lat > 90 or lon < -180 or lon > 180:
            raise ValueError('Not Lat Lon')
    except:
        return False, value

    latLonDict = {
        "lat": lat,
        "lon": lon
    }

    return True, latLonDict
