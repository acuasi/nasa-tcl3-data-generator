import csv
import math

from datetime import datetime
import helpers.constants as constants

def uasTruth(files):
    """Parses the radar file and adds uasTruth fields to cns2 data JSON"""
    radar_file_name = files['RADAR_FILE']
    uasTruthVariable = []
    with open(radar_file_name, "r") as radarFile:
        radarRecords = csv.DictReader(radarFile)
        for radarRecord in radarRecords:
            uasTruthVariable.append(formRadarRecord(radarRecord))

    return uasTruthVariable

def formRadarRecordJSON(ts, uasTruthEcefXCoordinate_ft, uasTruthEcefYCoordinate_ft, uasTruthEcefZCoordinate_ft, estimatedTruthPositionError95Prct_in):
    """Takes parameters and puts them into a JSON"""
    radarRecord = {
        "ts": ts,
        "uasTruthEcefXCoordinate_ft": uasTruthEcefXCoordinate_ft,
        "uasTruthEcefYCoordinate_ft": uasTruthEcefYCoordinate_ft,
        "uasTruthEcefZCoordinate_ft": uasTruthEcefZCoordinate_ft,
        "estimatedTruthPositionError95Prct_in": estimatedTruthPositionError95Prct_in
    }
    return radarRecord

def gps_to_ecef(lat, lon, alt):
    """GPS latitude, longitude, and altitude to Earth Centered Earth Fixed position in feet"""
    rad_lat = lat * (math.pi / 180.0)
    rad_lon = lon * (math.pi / 180.0)

    a = 6378137.0
    finv = 298.257223563
    f = 1 / finv
    e2 = 1 - (1 - f) * (1 - f)
    v = a / math.sqrt(1 - e2 * math.sin(rad_lat) * math.sin(rad_lat))

    x = (v + alt) * math.cos(rad_lat) * math.cos(rad_lon) * constants.M_TO_FT
    y = (v + alt) * math.cos(rad_lat) * math.sin(rad_lon) * constants.M_TO_FT
    z = (v * (1 - e2) + alt) * math.sin(rad_lat) * constants.M_TO_FT

    return x, y, z

def dmsToDD(degreesMinsSeconds):
    """Degrees, Minutes, Seconds to Decimal Degrees"""
    direction = degreesMinsSeconds[-1]
    degreesMinsSeconds = degreesMinsSeconds[:-1]

    degreesMins = degreesMinsSeconds[:degreesMinsSeconds.find('.') - 2]

    seconds = float(degreesMinsSeconds[degreesMinsSeconds.find('.') - 2:])
    mins = int(degreesMins[-2:])
    degrees = int(degreesMins[:-2])

    decDeg = round(degrees + round(mins/60, 4) + round(seconds/3600, 4), 4)

    if direction != 'N' and direction != 'E':
        decDeg *= -1

    return decDeg


def formRadarRecord(radarRecord):
    """Parse an individual record of the radar file and return it as a JSON"""
    ts = radarRecord['Time of Intercept']
    ts = datetime.strptime(ts, '%d %B %Y %H:%M:%S')
    ts = datetime.strftime(ts, '%Y-%m-%dT%H:%M:%S.000Z')

    gpsLatitude = dmsToDD(radarRecord['Latitude'])
    gpsLongitude = dmsToDD(radarRecord['Longitude'])

    gpsAltitude = float(radarRecord['Altitude'].replace('(ft)', '').strip())
    uasTruthEcefXCoordinate_ft, uasTruthEcefYCoordinate_ft, uasTruthEcefZCoordinate_ft = gps_to_ecef(gpsLatitude, gpsLongitude, gpsAltitude)

    # TODO: Is confidenceLevel the estimatedTruthPositionError95Prct_in?
    # confidenceLevel = radarRecord['Confidence Level'].strip()
    # if confidenceLevel:
    #     confidenceLevel = float(confidenceLevel)
    # else:
    #     confidenceLevel = 0

    estimatedTruthPositionError95Prct_in = None

    return formRadarRecordJSON(ts, uasTruthEcefXCoordinate_ft, uasTruthEcefYCoordinate_ft, uasTruthEcefZCoordinate_ft, estimatedTruthPositionError95Prct_in)
