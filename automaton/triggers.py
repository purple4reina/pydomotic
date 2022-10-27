import datetime
import inspect
import random

class AQITrigger(object):

    def __init__(self, check_func, sensor=None):
        from .sensors import AQISensor
        self.check_func = check_func
        self.sensor = sensor or AQISensor()

    def check(self):
        aqi = self.sensor.get_aqi()
        return self.check_func(aqi)

    def __str__(self):
        # TODO: I don't like this
        src = inspect.getsource(self.check_func).split(':')[-1].strip()
        return f'<AQITrigger check_func={src}>'
    __repr__ = __str__

class IsoWeekdayTrigger(object):

    def __init__(self, *isoweekdays):
        self.isoweekdays = isoweekdays

    def check(self):
        now = datetime.datetime.now()
        return now.isoweekday() in self.isoweekdays

    # TODO: __str__

class TimeTrigger(object):

    def __init__(self, *time_tuples):
        self.time_tuples = time_tuples

    def check(self):
        now = datetime.datetime.now()
        for hour, minute in self.time_tuples:
            if now.hour == hour and now.minute == minute:
                return True
        return False

    # TODO: __str__

class RandomTrigger(object):

    def __init__(self, probability):
        self.probability = probability

    def check(self):
        return random.random() < self.probability

    # TODO: __str__

class SunTrigger(object):

    # TODO: tests

    def __init__(self, timedelta, sensor=None):
        from .sensors import SunSensor
        self.timedelta = timedelta
        self.sensor = sensor or SunSensor()
        self.sensor_method = getattr(self.sensor, self.sun_sensor_method)

    def check(self):
        sun_time = self.sensor_method()
        check_time = sun_time + self.timedelta
        now = datetime.datetime.now()
        return now.hour == check_time.hour and now.minute == check_time.minute

class SunriseTrigger(SunTrigger):

    sun_sensor_method = 'get_sunrise'

    # TODO: __str__

class SunsetTrigger(SunTrigger):

    sun_sensor_method = 'get_sunset'

    # TODO: __str__
