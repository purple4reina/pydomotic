import requests

from .utils import cache_value

class AQISensor(object):

    aqi_url = 'https://www.airnowapi.org/aq/observation/latLong/current'

    def __init__(self, api_key, latitude, longitude, cache_aqi=True):
        self.location = (latitude, longitude)
        self.params = {
                'latitude': latitude,
                'longitude': longitude,
                'api_key': api_key,
                'format': 'application/json',
        }
        if cache_aqi:
            self.get_aqi = cache_value(seconds=60*60)(self.get_aqi)

    def get_aqi(self):
        try:
            resp = requests.get(self.aqi_url, params=self.params)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise AQISensorError(
                    f'error getting current aqi: [{e.__class__.__name__}] {e}')
        aqi = None
        try:
            for d in data:
                if d['ParameterName'] != 'PM2.5':
                    continue
                aqi = d['AQI']
                break
        except Exception as e:
            raise AQISensorError(
                    f'malformed response json [{e.__class__.__name__}] {e}')
        if aqi is None:
            raise AQISensorError(
                    f'unable to find aqi for location {self.location}')
        return aqi

    # TODO: __str__

class AQISensorError(Exception):
    pass

class SunSensor(object):

    def get_sunrise(self):
        # TODO: implement
        import datetime
        return datetime.datetime.now()

    def get_sunset(self):
        # TODO: implement
        import datetime
        return datetime.datetime.now()

    # TODO: __str__
