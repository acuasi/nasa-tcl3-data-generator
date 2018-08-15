"""This file contains custom helper functions used in files in the parser_pieces folder"""

from datetime import datetime

from helpers import constants

def sys_boot_time(sys_time, gps_ms, gps_wks):
    """Use GPS time and system us time to calculate boot start time as a UTC timestamp.

    Args:
        sys_time    (int): System time of Arducopter autopilot in ms.
        gps_ms      (int): GPS time since last week in ms.
        gps_wks     (int): Number of GPS weeks since epoch.

    Returns:
        boot_ts     (int): Timestamp of system since boot in seconds.
        """
    gps_ts = round(gps_ms / 1000 + gps_wks * 86400 * 7)
    utc_ts = gps_ts + constants.GPS_EPOCH_OFFSET + constants.GPS_LEAP_OFFSET
    sys_ts = sys_time / 1.0E6
    boot_ts = utc_ts - sys_ts
    return boot_ts

def unix_ts_converter(sys_time, boot_ts):
    return (sys_time / 1.0E6) + boot_ts

def sys_ts_converter(sys_time, boot_ts):
    """Convert system time to UTC ISO8601 timestamp.

    Args:
        sys_time        (int): System time of Arducopter autopilot in ms.
        boot_ts         (int): Timestamp of system since boot in seconds.

    Returns:
        sys_ts          (str): ISO8601 formatted timestamp of current system time.
    """
    unix_ts = unix_ts_converter(sys_time, boot_ts)
    return datetime.utcfromtimestamp(unix_ts).isoformat(timespec="milliseconds")+"Z"

def lat_lon_converter(lat, lon):
    """Convert lat and lon from radar degrees minutes decimal seconds string to a decimal degrees
    float value.

    Args:
        lat (string): The latitude in the format '1475131.986W'
        lon (string): The longitude in the format '645117.514N'

    Returns:
        location (tuple, float): The converted values in the format (64.8412343, -147.7432143)
    """
    lat_dir = lat[-1]
    lon_dir = lon[-1]
    lat = lat[:-1]
    lon = lon[:-1]
    lat_dd = round(float(lat[0:2]) + float(lat[2:4])/60 + float(lat[4:])/3600, 7)
    lon_dd = round(float(lon[0:3]) + float(lon[3:5])/60 + float(lon[5:])/3600, 7)

    if lat_dir == "S":
        lat_dd = lat_dd * -1
    if lon_dir == "W":
        lon_dd = lon_dd * -1

    return lat_dd, lon_dd
