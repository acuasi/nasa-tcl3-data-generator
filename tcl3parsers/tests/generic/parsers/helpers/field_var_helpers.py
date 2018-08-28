import re

dateWithOnlyTime = re.compile(r"([0-9]{2,2}):([0-9]{2,2}):([0-9]{2,2})")
properlyFormedDate = re.compile(r"([0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2})T([0-9]{2,2}:[0-9]{2,2}:[0-9]{2,2})(\.[0-9]{3,4}Z)")
noDoubleDigitDayDateFormat = re.compile(r"([0-9]{4,4}-[0-9]{2,2})-([0-9])(T[0-9]{2,2}:[0-9]{2,2}:[0-9]{2,2}\.[0-9]{3,4}Z)")
noSecondsDateFormat = re.compile(r"([0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}T[0-9]{2,2}:[0-9]{2,2})(\.[0-9]{3,4}Z)")

def maybeNumber(value):
    try:
        tempValue = float(value)
        if tempValue == int(tempValue):
            tempValue = int(value)
    except ValueError:
        return False, value
    return True, tempValue

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
