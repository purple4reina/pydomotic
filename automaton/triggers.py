import datetime
import inspect
import random

from .exceptions import AutomatonWebhookError
from .sensors import AQISensor, TimeSensor, WeatherSensor
from .utils import Nameable

class AQITrigger(Nameable):

    def __init__(self, check_func, aqi_sensor=None, api_key=None,
            latitude=None, longitude=None):
        self.check_func = check_func
        self.aqi_sensor = aqi_sensor or AQISensor(api_key, latitude, longitude)

    def check(self):
        aqi = self.aqi_sensor.get_aqi()
        return self.check_func(aqi)

class IsoWeekdayTrigger(Nameable):

    # TODO: test timezone

    def __init__(self, *isoweekdays, time_sensor=None):
        self.isoweekdays = isoweekdays
        self.time_sensor = time_sensor or TimeSensor()

    def check(self):
        now = self.time_sensor.get_current_datetime()
        return now.isoweekday() in self.isoweekdays

class TimeTrigger(Nameable):

    # TODO: test timezone

    def __init__(self, *time_tuples, time_sensor=None):
        self.time_tuples = time_tuples
        self.time_sensor = time_sensor or TimeSensor()

    def check(self):
        now = self.time_sensor.get_current_datetime()
        for hour, minute in self.time_tuples:
            if now.hour == hour and now.minute == minute:
                return True
        return False

class RandomTrigger(Nameable):

    def __init__(self, probability):
        self.probability = probability

    def check(self):
        return random.random() < self.probability

class _SunTrigger(Nameable):

    # TODO: test timezone
    # TODO: test lat/long

    def __init__(self, timedelta, latitude=0, longitude=0, time_sensor=None,
            sun_sensor=None):
        from .sensors import SunSensor
        self.timedelta = timedelta
        self.time_sensor = time_sensor or TimeSensor()
        self.sun_sensor = sun_sensor or SunSensor(latitude=latitude,
                longitude=longitude, time_sensor=self.time_sensor)
        self.sun_sensor_method = getattr(self.sun_sensor,
                self.sun_sensor_method_name)

    def check(self):
        sun_time = self.sun_sensor_method()
        check_time = sun_time + self.timedelta
        now = self.time_sensor.get_current_datetime()
        return now.hour == check_time.hour and now.minute == check_time.minute

class SunriseTrigger(_SunTrigger):

    sun_sensor_method_name = 'get_sunrise'

class SunsetTrigger(_SunTrigger):

    sun_sensor_method_name = 'get_sunset'

class TemperatureTrigger(Nameable):

    def __init__(self, check_func, weather_sensor=None, api_key=None,
            latitude=None, longitude=None):
        self.check_func = check_func
        self.weather_sensor = weather_sensor or WeatherSensor(api_key,
                latitude, longitude)

    def check(self):
        temp = self.weather_sensor.current_temperature()
        return self.check_func(temp)

class WebhookTrigger(object):

    def __init__(self, path):
        self.path = path

    def check(self):
        raise AutomatonWebhookError('webhook trigger must not be checked')
