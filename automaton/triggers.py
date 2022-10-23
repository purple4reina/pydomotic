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

    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute

    def check(self):
        now = datetime.datetime.now()
        return now.hour == self.hour and now.minute == self.minute

    # TODO: __str__

class RandomTrigger(object):

    def __init__(self, probability):
        self.probability = probability

    def check(self):
        return random.random() < self.probability

    # TODO: __str__
