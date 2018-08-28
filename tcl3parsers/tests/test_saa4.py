"""Provides tests for saa4.py."""
import re
import json
TEST_DIR = "/home/samuel/SpiderOak Hive/ACUASI/Code_Repos/nasa-tcl3-data-generator/tcl3parsers/tests/example_files/saa4"

JSON_OBJS = set(["fType", "basic", "geoFence", "typeOfSaaSensor",
                 "relativeHeadingAtFirstDetection_deg", "azimuthSensorMin_deg",
                 "azimuthSensorMax_deg", "elevationSensorMin_deg", "elevationSensorMax_deg",
                 "saaSensorMinSlantRange_ft", "saaSensorMaxSlantRange_ft", "minRcsOfSensor_ft2",
                 "maxRcsOfSensor_ft2", "updateRateSensor_hz", "saaSensorAzimuthAccuracy_deg",
                 "saaSensorAltitudeAccuracy_ft", "horRangeAccuracy_ft", "verRangeAccuracy_ft",
                 "slantRangeAccuracy_ft", "timeToTrack_sec", "probabilityFalseAlarmPrct_nonDim",
                 "probabilityIntruderDetectionPrct_nonDim", "targetTrackCapacity_nonDim",
                 "dataPacketRatio_nonDim", "transmissionDelay_sec", "numberOfLostTracks_nonDim",
                 "intruderRadarCrossSection_ft2", "txRadioFrequencyPower_w", "intruder"])

BASIC = set(["uvin", "gufi", "submitTime", "ussInstanceID", "ussName"])

GEOFENCE = set(["geoFenceAvailable_nonDim", "geoFenceStartTime", "geoFenceEndTime",
                "geoFenceType_nonDim", "geoFenceMinAltitude_ft", "geoFenceMaxAltitude_ft",
                "geoFenceCircularPointLat_deg", "geoFenceCircularPointLon_deg",
                "geoFenceCircularRadius_ft", "geoFenceEnable", "geoFenceDynamicPolygonPoint"])

f = open(TEST_DIR + "/SAA4.json", "r")
saa4_data = json.load(f)
geo_fence = saa4_data["geoFence"]
def test_json_objs():
    """Verify all high-level JSON objects exist in output file."""
    keys = set()
    for key in saa4_data:
        keys.add(key)
    assert not bool(keys ^ JSON_OBJS)

def test_basic_vars():
    """Verify all required 'basic' variables are present in output file."""
    keys = set()
    for key in saa4_data["basic"]:
        keys.add(key)
    assert not bool(keys ^ BASIC)

def test_basic_values():
    """Check that 'basic' object values are of type str."""
    for _, value in saa4_data["basic"].items():
        assert isinstance(value, str)
    assert saa4_data["fType"] == "SAA4"

def test_geofence_vars():
    """Verify all required 'geofence' variables are present in output file."""
    keys = set()
    for key in saa4_data["geoFence"]:
        keys.add(key)
    assert not bool(keys ^ GEOFENCE)

def test_nonlist_values():
    """Check non-list value types."""
    keys = ["geoFenceAvailable_nonDim", "geoFenceType_nonDim", "geoFenceMinAltitude_ft",
            "geoFenceMaxAltitude_ft", "geoFenceCircularPointLat_deg",
            "geoFenceCircularPointLon_deg", "geoFenceCircularRadius_ft"]
    for key in keys:
        assert isinstance(geo_fence[key], (int, float))

def test_times():
    """"Check geoFence start and end time values."""
    for item in geo_fence["geoFenceStartTime"]:
        p = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z")
        m = p.match(item)
        assert m

    for item in geo_fence["geoFenceEndTime"]:
        p = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z")
        m = p.match(item)
        assert m

def test_intruder():
    """Check that intruder values are populated."""
    intruder = saa4_data["intruder"]
    if intruder:
        for key, value in intruder.items():
            assert key and isinstance(value, (int, float, str, type(None)))
    else:
        assert False

def test_geofence_enable():
    """Test geoFenceEnable values."""
    p = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z")
    for item in geo_fence["geoFenceEnable"]:
        for k, v in item.items():
            if k == "ts":
                m = p.match(v)
                assert m
            elif k == "geoFenceEnable_nonDim":
                assert isinstance(v, int)
            else:
                assert False

def test_geofence_polygon_point():
    """Test geoFenceDynamicPolygonPoint values."""
    p = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z")
    variables = geo_fence["geoFenceDynamicPolygonPoint"]
    if variables:
        for item in variables.items():
            if item:
                for key, value in item.items():
                    if key == "ts":
                        m = p.match(value)
                        assert m
                    elif key == "geoFenceDynamicPolygonPoint_deg":
                        for i in value:
                            for k, v in i.items():
                                if k == "lat" or k == "lon":
                                    assert isinstance(v, (float, type(None)))
                                else:
                                    assert False
            else:
                assert isinstance(item, type(None))
