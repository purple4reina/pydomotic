import datetime
import inspect
import random

from .sensors import TimeSensor

class AQITrigger(object):

    def __init__(self, check_func, aqi_sensor=None, api_key=None,
            latitude=None, longitude=None):
        from .sensors import AQISensor
        self.check_func = check_func
        self.aqi_sensor = aqi_sensor or AQISensor(api_key, latitude, longitude)

    def check(self):
        aqi = self.aqi_sensor.get_aqi()
        return self.check_func(aqi)

class IsoWeekdayTrigger(object):

    # TODO: test timezone

    def __init__(self, *isoweekdays, time_sensor=None):
        self.isoweekdays = isoweekdays
        self.time_sensor = time_sensor or TimeSensor()

    def check(self):
        now = self.time_sensor.get_current_datetime()
        return now.isoweekday() in self.isoweekdays

class TimeTrigger(object):

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

class RandomTrigger(object):

    def __init__(self, probability):
        self.probability = probability

    def check(self):
        return random.random() < self.probability

class SunTrigger(object):

    # TODO: test timezone

    def __init__(self, timedelta, time_sensor=None, sun_sensor=None):
        from .sensors import SunSensor
        self.timedelta = timedelta
        self.time_sensor = time_sensor or TimeSensor()
        self.sun_sensor = sun_sensor or SunSensor(tzinfo=self.time_sensor.tzinfo)
        self.sun_sensor_method = getattr(self.sun_sensor,
                self.sun_sensor_method_name)

    def check(self):
        sun_time = self.sun_sensor_method()
        check_time = sun_time + self.timedelta
        now = self.time_sensor.get_current_datetime()
        return now.hour == check_time.hour and now.minute == check_time.minute

class SunriseTrigger(SunTrigger):

    sun_sensor_method_name = 'get_sunrise'

class SunsetTrigger(SunTrigger):

    sun_sensor_method_name = 'get_sunset'
