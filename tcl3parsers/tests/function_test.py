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

if __name__ == "__main__":
    locs = {("645010.000N", "1475010.000W"): (64.8361111, -147.8361111),
            ("30120N", "147120W"): (30.20000000, -147.20000000)}
    for key, value in locs.items():
        lat, lon = lat_lon_converter(key[0], key[1])
        assert lat == value[0] and lon == value[1]
        # print(lat, value[0])
        # print(lon, value[1])

    print("Success!")
