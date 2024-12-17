#!/usr/bin/python3 -u

import json
import time

import requests
from prometheus_client import start_http_server, Gauge

timestamp = Gauge('dwd_timestamp', 'Timestamp in unix time', ['station_id'])
temperature = Gauge('dwd_temperature', 'Temperature in °C', ['station_id'])
sunshine = Gauge('dwd_sunshine', 'Amount of sunshine in min/h', ['station_id'])
precipitation = Gauge('dwd_precipitation', 'Precipitation in mm/h', ['station_id'])
pressure = Gauge('dwd_pressure', 'Air pressure in hPa', ['station_id'])
humidity = Gauge('dwd_humidity', 'Humidity in %H', ['station_id'])
dew_point = Gauge('dwd_dew_point', 'Dew point in °C', ['station_id'])
cloud_cover_total = Gauge('cloud_cover_total', 'Cloud cover 0-8', ['station_id'])
total_snow = Gauge('dwd_total_snow', 'Amount of snow in cm', ['station_id'])
wind_speed_max = Gauge('dwd_wind_speed_max', 'Max. wind speed in km/h', ['station_id'])
wind_direction_mean = Gauge('dwd_wind_direction_mean', 'Mean wind direction in degrees', ['station_id'])
wind_speed_mean = Gauge('dwd_wind_speed_mean', 'Mean wind speed in km/h', ['station_id'])

def is_valid(station, value) -> bool:
    return value in station and station[value] is not None and station[value] < 32767

def main():
    print("DWD exporter v0.2\n")
    station_ids = 'E298,10400,10113'
    server_port = 3825

    print("Station ids: " + str(station_ids) + "\n")
    print("Port       : " + str(server_port) + "\n")

    start_http_server(server_port)
    while True:
        response = json.loads(requests.get('https://app-prod-ws.warnwetter.de/v30/currentMeasurements?stationIds='
                                           + station_ids).content.decode('UTF-8'))

        for st_id in response['data']:
            station = response['data'][st_id]
            timestamp.labels(station_id=st_id).set(station['time'])
            if is_valid(station, 'temperature'):
                temperature.labels(station_id=st_id).set(station['temperature'] / 10.0)
            if is_valid(station, 'sunshine'):
                sunshine.labels(station_id=st_id).set(station['sunshine'] / 10.0)
            if is_valid(station, 'precipitation'):
                precipitation.labels(station_id=st_id).set(station['precipitation'] / 10.0)
            if is_valid(station, 'pressure'):
                pressure.labels(station_id=st_id).set(station['pressure'] / 10.0)
            if is_valid(station, 'humidity'):
                humidity.labels(station_id=st_id).set(station['humidity'] / 10.0)
            if is_valid(station, 'dew_point'):
                dew_point.labels(station_id=st_id).set(station['dewPoint'] / 10.0)
            if is_valid(station, 'cloudCoverTotal') and station['cloudCoverTotal'] <= 8:
                cloud_cover_total.labels(station_id=st_id).set(station['cloudCoverTotal'])
            if is_valid(station, 'totalSnow'):
                total_snow.labels(station_id=st_id).set(station['totalSnow'] / 10.0)
            if is_valid(station, 'windspeedmax'):
                wind_speed_max.labels(station_id=st_id).set(station['windspeedmax'] / 10.0)
            if is_valid(station, 'winddirectionmean'):
                wind_direction_mean.labels(station_id=st_id).set(station['winddirectionmean'] / 10.0)
            if is_valid(station, 'windspeedmean'):
                wind_speed_mean.labels(station_id=st_id).set(station['windspeedmean'] / 10.0)

        time.sleep(300)

if __name__ == "__main__":
    main()