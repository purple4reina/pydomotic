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

    @cache_value(minutes=15)
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

    def __init__(self, latitude, longitude, time_sensor):
        self.observer = astral.Observer(latitude=latitude, longitude=longitude)
        self.time_sensor = time_sensor or TimeSensor(
                latitude=latitude, longitude=longitude)

    @cache_value(hours=12)
    def get_sunrise(self):
        now = self.time_sensor.get_current_datetime()
        return astral.sun.sunrise(self.observer, date=now,
                tzinfo=self.time_sensor.tzinfo)

    @cache_value(hours=12)
    def get_sunset(self):
        now = self.time_sensor.get_current_datetime()
        return astral.sun.sunset(self.observer, date=now,
                tzinfo=self.time_sensor.tzinfo)

class TimeSensor(object):

    # TODO: test

    def __init__(self, latitude=None, longitude=None, timezone=None):
        if latitude is None and longitude is None and timezone is None:
            raise TypeError('timezone or latitude/longitude required')
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        self._tzinfo = None

    def _get_timezone(self):
        if self.timezone:
            return self.timezone
        import timezonefinder
        return timezonefinder.TimezoneFinder().timezone_at(
                lng=self.longitude, lat=self.latitude)

    def get_current_datetime(self):
        return datetime.datetime.now(tz=self.tzinfo)

    @property
    def tzinfo(self):
        # TODO: test
        if self._tzinfo is None:
            if self.timezone or (
                    self.latitude is not None and self.longitude is not None):
                self._tzinfo = zoneinfo.ZoneInfo(self._get_timezone())
            else:
                self._tzinfo = datetime.timezone.utc
        return self._tzinfo

class WeatherSensor(object):

    def __init__(self, api_key, latitude, longitude):
        import pyowm
        self.owm_mgr = pyowm.OWM(api_key).weather_manager()
        self.location = (latitude, longitude)

    @cache_value(minutes=5)
    def _weather(self):
        return self.owm_mgr.weather_at_coords(*self.location).weather

    def current_temperature(self):
        # returns float with 2 decimal points
        return self._weather().temperature('fahrenheit').get('temp')

class WebhookSensor(object):

    def __init__(self):
        self.path = None
        self.method = None

    def set_webhook_request(self, event):
        # TODO: test setting request from various event types
        http = event.get('requestContext', {}).get('http', {})
        self.path = http.get('path')
        self.method = http.get('method')

class DeviceSensor(object):

    def __init__(self, device):
        self.device = device

    def __getattr__(self, attr):
        if attr == 'device':
            return self.device
        if attr in dir(self.device):
            return getattr(self.device, attr)
        return super().__getattr__(self, attr)
