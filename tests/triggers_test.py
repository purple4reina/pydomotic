import datetime
import pytest

from automaton.triggers import (AQITrigger, IsoWeekdayTrigger, TimeTrigger,
        RandomTrigger, SunriseTrigger, SunsetTrigger)

test_time = datetime.datetime(1982, 2, 4, 10, 20)

def test_aqi_trigger_fires(mock_aqi_sensor):
    mock_aqi_sensor.aqi = 200
    def check_func(aqi):
        return aqi > 100
    trigger = AQITrigger(check_func, sensor=mock_aqi_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'
    assert mock_aqi_sensor.get_aqi_called, 'sensor.get_aqi not called'

def test_aqi_trigger_does_not_fire(mock_aqi_sensor):
    mock_aqi_sensor.aqi = 50
    def check_func(aqi):
        return aqi > 100
    trigger = AQITrigger(check_func, sensor=mock_aqi_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'
    assert mock_aqi_sensor.get_aqi_called, 'sensor.get_aqi not called'

def test_isoweekday_trigger_fires(patch_datetime):
    patch_datetime(test_time)
    trigger = IsoWeekdayTrigger(4, 5, 6, 7)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_isoweekday_trigger_does_not_fire(patch_datetime):
    patch_datetime(test_time)
    trigger = IsoWeekdayTrigger(1, 2, 3)
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_time_trigger_fires(patch_datetime):
    patch_datetime(test_time)
    trigger = TimeTrigger((10, 20))
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_time_trigger_fires_multiple_times_given(patch_datetime):
    patch_datetime(test_time)
    trigger = TimeTrigger((11, 30), (10, 20))
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_time_trigger_does_not_fire_different_hour(patch_datetime):
    patch_datetime(test_time)
    trigger = TimeTrigger((11, 20))
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_time_trigger_does_not_fire_different_minute(patch_datetime):
    patch_datetime(test_time)
    trigger = TimeTrigger((10, 30))
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_random_trigger_fires(patch_random):
    patch_random(0.5)
    trigger = RandomTrigger(0.75)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_random_trigger_does_not_fire(patch_random):
    patch_random(0.5)
    trigger = RandomTrigger(0.25)
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_sunrise_trigger_fires(patch_datetime, mock_sun_sensor):
    delta = datetime.timedelta(hours=1, minutes=15)
    patch_datetime(test_time + delta)
    mock_sun_sensor.sunrise = test_time
    trigger = SunriseTrigger(delta, sensor=mock_sun_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'
    assert mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise not called'
    assert not mock_sun_sensor.get_sunset_called, 'sensor.get_sunset called'

def test_sunrise_trigger_does_not_fire(patch_datetime, mock_sun_sensor):
    delta = datetime.timedelta(hours=1, minutes=15)
    patch_datetime(test_time)
    mock_sun_sensor.sunrise = test_time
    trigger = SunriseTrigger(delta, sensor=mock_sun_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'
    assert mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise not called'
    assert not mock_sun_sensor.get_sunset_called, 'sensor.get_sunset called'

def test_sunset_trigger_fires(patch_datetime, mock_sun_sensor):
    delta = datetime.timedelta(hours=1, minutes=15)
    patch_datetime(test_time + delta)
    mock_sun_sensor.sunset = test_time
    trigger = SunsetTrigger(delta, sensor=mock_sun_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'
    assert mock_sun_sensor.get_sunset_called, 'sensor.get_sunset not called'
    assert not mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise called'

def test_sunset_trigger_does_not_fire(patch_datetime, mock_sun_sensor):
    delta = datetime.timedelta(hours=1, minutes=15)
    patch_datetime(test_time)
    mock_sun_sensor.sunset = test_time
    trigger = SunsetTrigger(delta, sensor=mock_sun_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'
    assert mock_sun_sensor.get_sunset_called, 'sensor.get_sunset not called'
    assert not mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise called'
