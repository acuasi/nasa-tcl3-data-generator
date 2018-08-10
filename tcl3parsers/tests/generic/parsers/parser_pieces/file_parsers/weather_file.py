from datetime import datetime
import helpers.constants as constants

def weather_file(model, fileName):
    with open(fileName, "r") as weather_file:
        headers = weather_file.readline().split(",")

        for line in weather_file:
            # Split by commas and strip leading and trailing whitespaces
            row = [item.strip() for item in line.split(",")]
            dt_string = row[headers.index("Time of Intercept")]
            ts = datetime.strptime(dt_string,
                                   "%d %B %Y %H:%M:%S").isoformat(timespec="milliseconds") + "Z"
            temp = float(row[headers.index("Outside Temp")].strip().split(" ")[0])
            pressure = float(row[headers.index("Barometer")])
            wind_speed = float(row[headers.index("Wind Speed")].strip().split(" ")[0]) * constants.KTS_TO_FT
            wind_dir = float(row[headers.index("Wind Direction")])
            wx = {"temp": temp, "pressure": pressure, "windspeed": wind_speed, "windDir": wind_dir}
            wx_zones = {"ts": ts, "wxBvlosLandingZone1Data": wx, "wxBvlosLandingZone2Data": wx, "wxBvlosLandingZone3Data": wx}
            model["wxBvlosLandingZone"].append(wx_zones)
    return model
