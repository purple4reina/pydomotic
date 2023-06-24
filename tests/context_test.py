import pytest
import yaml

from automaton.context import Context

_test_context_sensors = (
        ("", ()),
        (
            """
            triggers:
              location:
                latitude: 123
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                longitude: 789
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
            """,
            ('sun_sensor', 'time_sensor'),
        ),
        (
            """
            triggers:
              aqi:
                api_key: abc
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
              aqi:
                api_key: abc
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                longitude: 789
              aqi:
                api_key: abc
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
              aqi:
                api_key: abc
            """,
            ('aqi_sensor', 'sun_sensor', 'time_sensor'),
        ),
        (
            """
            triggers:
              weather:
                api_key: xyz
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
              weather:
                api_key: xyz
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                longitude: 789
              weather:
                api_key: xyz
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
              weather:
                api_key: xyz
            """,
            ('sun_sensor', 'time_sensor', 'weather_sensor'),
        ),
        (
            """
            triggers:
              aqi:
                api_key: abc
              weather:
                api_key: xyz
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
              aqi:
                api_key: abc
              weather:
                api_key: xyz
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                longitude: 789
              aqi:
                api_key: abc
              weather:
                api_key: xyz
            """,
            (),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
              aqi:
                api_key: abc
              weather:
                api_key: xyz
            """,
            ('aqi_sensor', 'sun_sensor', 'time_sensor', 'weather_sensor'),
        ),
        (
            """
            triggers:
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                longitude: 789
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
              timezone: 'America/Los_Angeles'
            """,
            ('sun_sensor', 'time_sensor'),
        ),
        (
            """
            triggers:
              aqi:
                api_key: abc
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
              aqi:
                api_key: abc
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                longitude: 789
              aqi:
                api_key: abc
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
              aqi:
                api_key: abc
              timezone: 'America/Los_Angeles'
            """,
            ('aqi_sensor', 'sun_sensor', 'time_sensor'),
        ),
        (
            """
            triggers:
              weather:
                api_key: xyz
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
              weather:
                api_key: xyz
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                longitude: 789
              weather:
                api_key: xyz
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
              weather:
                api_key: xyz
              timezone: 'America/Los_Angeles'
            """,
            ('sun_sensor', 'time_sensor', 'weather_sensor'),
        ),
        (
            """
            triggers:
              aqi:
                api_key: abc
              weather:
                api_key: xyz
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
              aqi:
                api_key: abc
              weather:
                api_key: xyz
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                longitude: 789
              aqi:
                api_key: abc
              weather:
                api_key: xyz
              timezone: 'America/Los_Angeles'
            """,
            ('time_sensor',),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
              aqi:
                api_key: abc
              weather:
                api_key: xyz
              timezone: 'America/Los_Angeles'
            """,
            ('aqi_sensor', 'sun_sensor', 'time_sensor', 'weather_sensor'),
        ),
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
              aqi:
                api_key: abc
              weather:
                api_key: xyz
                data_cache_seconds: 20
              timezone: 'America/Los_Angeles'
            """,
            ('aqi_sensor', 'sun_sensor', 'time_sensor', 'weather_sensor'),
        ),
)

@pytest.mark.parametrize('yaml_str,expect', _test_context_sensors)
def test_context_sensors(yaml_str, expect):
    conf = yaml.safe_load(yaml_str) if yaml_str else {}
    context = Context.from_yaml(conf.get('triggers'))
    assert expect == tuple(context.sensors.keys()), 'wrong sensors returned'

_test_context_weather_sensor_data_cache_seconds = (
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
              weather:
                api_key: xyz
                data_cache_seconds: 20
            """,
            True,
        ),
        (
            """
            triggers:
              location:
                latitude: 123
                longitude: 789
              weather:
                api_key: xyz
            """,
            False,
        ),
)

@pytest.mark.parametrize('yaml_str,wrapped', _test_context_weather_sensor_data_cache_seconds)
def test_context_weather_sensor_data_cache_seconds(yaml_str, wrapped):
    conf = yaml.safe_load(yaml_str)
    context = Context.from_yaml(conf.get('triggers'))
    weather = context.sensors['weather_sensor']._weather
    assert hasattr(weather, '__wrapped__') is wrapped, 'incorrect wrapping'
    assert hasattr(weather, 'clear_cache') is wrapped, 'incorrect wrapping'
