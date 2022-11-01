import astral
import astral.sun
import datetime
import requests
import zoneinfo

from .utils import cache_value

class AQISensor(object):

    aqi_url = 'https://www.airnowapi.org/aq/observation/latLong/current'

    def __init__(self, api_key, latitude, longitude):
        self.location = (latitude, longitude)
        self.params = {
                'latitude': latitude,
                'longitude': longitude,
                'api_key': api_key,
                'format': 'application/json',
        }

    @cache_value(seconds=60*60)
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

class AQISensorError(Exception):
    pass

class SunSensor(object):

    # TODO: test timezone

    def __init__(self, latitude=0, longitude=0, tzinfo=datetime.timezone.utc):
        self.observer = astral.Observer(latitude=latitude, longitude=longitude)
        self.tzinfo = tzinfo

    def get_sunrise(self):
        return astral.sun.sunrise(self.observer, tzinfo=self.tzinfo)

    def get_sunset(self):
        return astral.sun.sunset(self.observer, tzinfo=self.tzinfo)

class TimeSensor(object):

    # TODO: test
    # TODO: change patch_datetime to mock_time_sensor

    def __init__(self, latitude=None, longitude=None):
        self.latitude = latitude
        self.longitude = longitude
        self._tzinfo = None

    def _get_timezone(self):
        # TODO: implement
        return 'America/Los_Angeles'

    def get_current_datetime(self):
        return datetime.datetime.now(tzinfo=self.tzinfo)

    @property
    def tzinfo(self):
        if self._tzinfo is None:
            if self.latitude is None or self.longitude is None:
                self._tzinfo = datetime.timezone.utc
            else:
                self._tzinfo = zoneinfo.ZoneInfo(self._get_timezone())
        return self._tzinfo
