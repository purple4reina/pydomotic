import datetime
import pytest

from automaton.sensors import AQISensor, AQISensorError, SunSensor

@pytest.fixture(autouse=True)
def reset_get_aqi_cache():
    AQISensor.get_aqi.clear_cache()

def test_aqi_sensor_get_aqi(patch_get_requests):
    data = [
            {
                'DateObserved': '2022-10-29 ',
                'HourObserved': 19,
                'LocalTimeZone': 'EST',
                'ReportingArea': 'Northeast Urban',
                'StateCode': 'NJ',
                'Latitude': 40.692,
                'Longitude': -74.187,
                'ParameterName': 'O3',
                'AQI': 13,
                'Category': {'Number': 1, 'Name': 'Good'},
            },
            {
                'DateObserved': '2022-10-29 ',
                'HourObserved': 19,
                'LocalTimeZone': 'EST',
                'ReportingArea': 'Northeast Urban',
                'StateCode': 'NJ',
                'Latitude': 40.692,
                'Longitude': -74.187,
                'ParameterName': 'PM2.5',
                'AQI': 31,
                'Category': {'Number': 1, 'Name': 'Good'},
            },
    ]
    patch_get_requests(False, data)
    sensor = AQISensor('api_key', 'latitude', 'longitude')
    actual = sensor.get_aqi()
    assert actual == 31, 'wrong aqi found'

def test_aqi_sensor_get_aqi_raises(patch_get_requests):
    patch_get_requests(RuntimeError('oops'), [])
    sensor = AQISensor('api_key', 'latitude', 'longitude')
    try:
        sensor.get_aqi()
    except AQISensorError as e:
        exp_err = 'error getting current aqi: [RuntimeError] oops'
        assert str(e) ==  exp_err, 'wrong error raised'
    else:
        raise AssertionError('should have raised')

def test_aqi_sensor_get_aqi_no_data(patch_get_requests):
    patch_get_requests(False, [])
    sensor = AQISensor('api_key', 'latitude', 'longitude')
    try:
        sensor.get_aqi()
    except AQISensorError as e:
        exp_err = "unable to find aqi for location ('latitude', 'longitude')"
        assert str(e) == exp_err, 'wrong error raised'
    else:
        raise AssertionError('should have raised')

def test_sun_sensor_get_sunrise(mock_time_sensor):
    sensor = SunSensor(latitude=45.58, longitude=-122.11,
            time_sensor=mock_time_sensor)
    actual = sensor.get_sunrise()

    assert actual.year == 1982, 'wrong year returned'
    assert actual.month == 2, 'wrong month returned'
    assert actual.day == 4, 'wrong day returned'
    assert actual.hour == 7, 'wrong hour returned'
    assert actual.minute == 26, 'wrong minute returned'

def test_sun_sensor_get_sunset(mock_time_sensor):
    sensor = SunSensor(latitude=45.58, longitude=-122.11,
            time_sensor=mock_time_sensor)
    actual = sensor.get_sunset()

    assert actual.year == 1982, 'wrong year returned'
    assert actual.month == 2, 'wrong month returned'
    assert actual.day == 4, 'wrong day returned'
    assert actual.hour == 17, 'wrong hour returned'
    assert actual.minute == 18, 'wrong minute returned'
