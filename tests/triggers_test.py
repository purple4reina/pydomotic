import datetime

from pydomotic.triggers import (AQITrigger, IsoWeekdayTrigger, TimeTrigger,
        DateTrigger, CronTrigger, RandomTrigger, SunriseTrigger, SunsetTrigger,
        TemperatureTrigger)

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
    trigger = AQITrigger(check_func, api_key=None, latitude=None,
            longitude=None, aqi_sensor=mock_aqi_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'
    assert mock_aqi_sensor.get_aqi_called, 'sensor.get_aqi not called'

def test_isoweekday_trigger_fires(mock_time_sensor):
    trigger = IsoWeekdayTrigger((4, 5, 6, 7), time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_isoweekday_trigger_does_not_fire(mock_time_sensor):
    trigger = IsoWeekdayTrigger((1, 2, 3), time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_time_trigger_fires(mock_time_sensor):
    trigger = TimeTrigger([620], time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_time_trigger_fires_multiple_times_given(mock_time_sensor):
    trigger = TimeTrigger([680, 620], time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_time_trigger_does_not_fire_different_hour(mock_time_sensor):
    trigger = TimeTrigger([680], time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_time_trigger_does_not_fire_different_minute(mock_time_sensor):
    trigger = TimeTrigger([630], time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_date_trigger_fires(mock_time_sensor):
    trigger = DateTrigger([datetime.date(1982, 2, 4)],
            time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_date_trigger_fires_multiple_dates_given(mock_time_sensor):
    trigger = DateTrigger([datetime.date(1982, 1, 1), datetime.date(1982, 2, 4)],
            time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_date_trigger_does_not_fire_different_year(mock_time_sensor):
    trigger = DateTrigger([datetime.date(2020, 2, 4)],
            time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_date_trigger_does_not_fire_different_month(mock_time_sensor):
    trigger = DateTrigger([datetime.date(1982, 3, 4)],
            time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_date_trigger_does_not_fire_different_day(mock_time_sensor):
    trigger = DateTrigger([datetime.date(1982, 2, 12)],
            time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'

def test_cron_trigger_fires(mock_time_sensor):
    trigger = CronTrigger('20 10 * * *', time_sensor=mock_time_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'

def test_cron_trigger_does_not_fire(mock_time_sensor):
    trigger = CronTrigger('20 11 * * *', time_sensor=mock_time_sensor)
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

def test_sunrise_trigger_fires(mock_time_sensor, mock_sun_sensor, test_datetime):
    mock_sun_sensor.sunrise = test_datetime - datetime.timedelta(minutes=75)
    trigger = SunriseTrigger([75], time_sensor=mock_time_sensor,
            sun_sensor=mock_sun_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'
    assert mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise not called'
    assert not mock_sun_sensor.get_sunset_called, 'sensor.get_sunset called'

def test_sunrise_trigger_does_not_fire(mock_time_sensor, mock_sun_sensor, test_datetime):
    mock_sun_sensor.sunrise = test_datetime
    trigger = SunriseTrigger([75], time_sensor=mock_time_sensor,
            sun_sensor=mock_sun_sensor)
    fires = trigger.check()
    assert not fires, 'trigger fired'
    assert mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise not called'
    assert not mock_sun_sensor.get_sunset_called, 'sensor.get_sunset called'

def test_sunset_trigger_fires(mock_time_sensor, mock_sun_sensor, test_datetime):
    mock_sun_sensor.sunset = test_datetime - datetime.timedelta(minutes=75)
    trigger = SunsetTrigger([75], time_sensor=mock_time_sensor,
            sun_sensor=mock_sun_sensor)
    fires = trigger.check()
    assert fires, 'trigger did not fire'
    assert mock_sun_sensor.get_sunset_called, 'sensor.get_sunset not called'
    assert not mock_sun_sensor.get_sunrise_called, 'sensor.get_sunrise called'

def test_sunset_trigger_does_not_fire(mock_time_sensor, mock_sun_sensor, test_datetime):
    mock_sun_sensor.sunset = test_datetime
    trigger = SunsetTrigger([75], time_sensor=mock_time_sensor,
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
