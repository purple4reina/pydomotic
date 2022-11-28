import datetime
import pytest

from automaton.triggers import (AQITrigger, IsoWeekdayTrigger, TimeTrigger,
        RandomTrigger, SunriseTrigger, SunsetTrigger, TemperatureTrigger,
        WebhookTrigger)

test_time = datetime.datetime(1982, 2, 4, 10, 20)

_test_trigger_interface = (
        (AQITrigger(lambda a: a > 100), 'aqi_trigger'),
        (IsoWeekdayTrigger(), 'iso_weekday_trigger'),
        (TimeTrigger(), 'time_trigger'),
        (RandomTrigger(0.5), 'random_trigger'),
        (SunriseTrigger(120), 'sunrise_trigger'),
        (SunsetTrigger(120), 'sunset_trigger'),
        (TemperatureTrigger(lambda t: t > 100, api_key='abc123'),
            'temperature_trigger'),
        (WebhookTrigger('/full/path'), 'webhook_trigger'),
)

@pytest.mark.parametrize('instance,exp_name', _test_trigger_interface)
def test_trigger_interface(instance, exp_name):
    assert instance.name == exp_name, 'wrong value for name found'
    assert hasattr(instance, 'check'), 'instance does not have attr check'
    assert callable(instance.check), 'instance.check is not callable'

def test_aqi_trigger_fires(mock_aqi_sensor):
    mock_aqi_sensor.aqi = 200
    def check_func(aqi):
        return aqi > 100
    trigger = AQITrigger(check_func, aqi_sensor=mock_aqi_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'
    assert mock_aqi_sensor.get_aqi_called, 'sensor.get_aqi not called'

def test_aqi_trigger_does_not_fire(mock_aqi_sensor):
    mock_aqi_sensor.aqi = 50
    def check_func(aqi):
        return aqi > 100
    trigger = AQITrigger(check_func, aqi_sensor=mock_aqi_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'
    assert mock_aqi_sensor.get_aqi_called, 'sensor.get_aqi not called'

def test_isoweekday_trigger_fires(mock_time_sensor):
    trigger = IsoWeekdayTrigger(4, 5, 6, 7, time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_isoweekday_trigger_does_not_fire(mock_time_sensor):
    trigger = IsoWeekdayTrigger(1, 2, 3, time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_time_trigger_fires(mock_time_sensor):
    trigger = TimeTrigger((10, 20), time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_time_trigger_fires_multiple_times_given(mock_time_sensor):
    trigger = TimeTrigger((11, 30), (10, 20), time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_time_trigger_does_not_fire_different_hour(mock_time_sensor):
    trigger = TimeTrigger((11, 20), time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_time_trigger_does_not_fire_different_minute(mock_time_sensor):
    trigger = TimeTrigger((10, 30), time_sensor=mock_time_sensor)
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

def test_sunrise_trigger_fires(mock_time_sensor, mock_sun_sensor):
    delta = datetime.timedelta(hours=1, minutes=15)
    mock_sun_sensor.sunrise = test_time - delta
    trigger = SunriseTrigger(delta, time_sensor=mock_time_sensor,
            sun_sensor=mock_sun_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'
    assert mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise not called'
    assert not mock_sun_sensor.get_sunset_called, 'sensor.get_sunset called'

def test_sunrise_trigger_does_not_fire(mock_time_sensor, mock_sun_sensor):
    delta = datetime.timedelta(hours=1, minutes=15)
    mock_sun_sensor.sunrise = test_time
    trigger = SunriseTrigger(delta, time_sensor=mock_time_sensor,
            sun_sensor=mock_sun_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'
    assert mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise not called'
    assert not mock_sun_sensor.get_sunset_called, 'sensor.get_sunset called'

def test_sunset_trigger_fires(mock_time_sensor, mock_sun_sensor):
    delta = datetime.timedelta(hours=1, minutes=15)
    mock_sun_sensor.sunset = test_time - delta
    trigger = SunsetTrigger(delta, time_sensor=mock_time_sensor,
            sun_sensor=mock_sun_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'
    assert mock_sun_sensor.get_sunset_called, 'sensor.get_sunset not called'
    assert not mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise called'

def test_sunset_trigger_does_not_fire(mock_time_sensor, mock_sun_sensor):
    delta = datetime.timedelta(hours=1, minutes=15)
    mock_sun_sensor.sunset = test_time
    trigger = SunsetTrigger(delta, time_sensor=mock_time_sensor,
            sun_sensor=mock_sun_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'
    assert mock_sun_sensor.get_sunset_called, 'sensor.get_sunset not called'
    assert not mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise called'

def test_temp_trigger_fires(mock_weather_sensor):
    mock_weather_sensor.temp = 104
    def check_func(temp):
        return temp > 100
    trigger = TemperatureTrigger(check_func, weather_sensor=mock_weather_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'
    assert mock_weather_sensor.current_temperature_called, (
            'sensor.current_temperature not called')

def test_aqi_trigger_does_not_fire(mock_weather_sensor):
    mock_weather_sensor.temp = 50
    def check_func(temp):
        return temp > 100
    trigger = TemperatureTrigger(check_func, weather_sensor=mock_weather_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'
    assert mock_weather_sensor.current_temperature_called, (
            'sensor.current_temperature not called')
