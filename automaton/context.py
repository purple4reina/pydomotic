import logging

from .exceptions import AutomatonConfigParsingError
from .sensors import TimeSensor, WebhookSensor, DeviceSensor

logger = logging.getLogger(__name__)

class Context(object):

    def __init__(self, latitude, longitude, aqi_api_key, weather_api_key,
                timezone):
        self._aqi_api_key = aqi_api_key
        self._latitude = latitude
        self._longitude = longitude
        self._time_sensor = None
        self._timezone = timezone
        self._weather_api_key = weather_api_key
        self._webhook_sensor = None
        self._device_sensors = {}
        self._context = None
        self.devices = {}

    @staticmethod
    def from_yaml(triggers):
        from .parsers import _parse_string
        try:
            location = triggers.get('location', {})
            latitude = location.get('latitude')
            longitude = location.get('longitude')
        except Exception as e:
            logger.debug('failed to parse location, ignoring: '
                    f'[{e.__class__.__name__}] {e}')
            latitude = longitude = None

        try:
            timezone = triggers.get('timezone')
        except Exception as e:
            logger.debug('failed to parse timezone, ignoring: '
                    f'[{e.__class__.__name__}] {e}')
            timezone = None

        try:
            aqi = triggers.get('aqi', {})
            aqi_api_key = _parse_string(aqi.get('api_key'))
        except Exception as e:
            logger.debug('failed to parse aqi api_key, ignoring: '
                    f'[{e.__class__.__name__}] {e}')
            aqi_api_key = None

        try:
            weather = triggers.get('weather', {})
            weather_api_key = _parse_string(weather.get('api_key'))
        except Exception as e:
            logger.debug('failed to parse weather api_key, ignoring: '
                    f'[{e.__class__.__name__}] {e}')
            weather_api_key = None

        return Context(
                latitude, longitude, aqi_api_key, weather_api_key, timezone)

    @property
    def latitude(self):
        if self._latitude is None:
            raise AutomatonConfigParsingError(
                    'latitude value required for location')
        if not isinstance(self._latitude, (int, float)):
            raise AutomatonConfigParsingError(
                    'latitude must be a number, not '
                    f'{self._latitude.__class__.__name__}')
        return self._latitude

    @property
    def longitude(self):
        if self._longitude is None:
            raise AutomatonConfigParsingError(
                    'longitude value required for location')
        if not isinstance(self._longitude, (int, float)):
            raise AutomatonConfigParsingError(
                    'longitude must be a number, not '
                    f'{self._longitude.__class__.__name__}')
        return self._longitude

    @property
    def timezone(self):
        if self._timezone is None:
            raise AutomatonConfigParsingError('timezone is required')
        if not isinstance(self._timezone, str):
            raise AutomatonConfigParsingError(
                    'timezone must be a string, not '
                    f'{self._timezone.__class__.__name__}')
        return self._timezone

    @property
    def time_sensor(self):
        if self._time_sensor is None:
            if self._timezone is not None:
                self._time_sensor = TimeSensor(timezone=self.timezone)
            elif self._longitude is not None and self._latitude is not None:
                self._time_sensor = TimeSensor(latitude=self.latitude,
                        longitude=self.longitude)
            else:
                raise AutomatonConfigParsingError(
                        'either timezone or latitude/longitude required')
        return self._time_sensor

    @property
    def aqi_api_key(self):
        if not self._aqi_api_key:
            raise AutomatonConfigParsingError('aqi api key required')
        if not isinstance(self._aqi_api_key, str):
            raise AutomatonConfigParsingError(
                    'aqi api_key must be a string, not '
                    f'{self._aqi_api_key.__class__.__name__}')
        return self._aqi_api_key

    @property
    def weather_api_key(self):
        if not self._weather_api_key:
            raise AutomatonConfigParsingError('weather api key required')
        if not isinstance(self._weather_api_key, str):
            raise AutomatonConfigParsingError(
                    'weather api_key must be a string, not '
                    f'{self._aqi_api_key.__class__.__name__}')
        return self._weather_api_key

    @property
    def webhook_sensor(self):
        if self._webhook_sensor is None:
            self._webhook_sensor = WebhookSensor()
        return self._webhook_sensor

    def device_sensor(self, name):
        device = self.devices.get(name, None)
        if device is None:
            raise AutomatonConfigParsingError(f'sensor device {name} not found')
        if not self._device_sensors.get(device.name):
            self._device_sensors[device.name] = DeviceSensor(device)
        return self._device_sensors[device.name]

    @property
    def context(self):
        if not self._context:
            # TODO: make a copy to to pass to action.run?
            self._context = {
                    'devices': self.devices,
                    'time_sensor': self.time_sensor,
            }
        return self._context
