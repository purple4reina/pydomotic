import datetime
import os
import pytest

from automaton.actions import TurnOnAction, TurnOffAction, ExecuteCodeAction
from automaton.components import Component
from automaton.context import Context
from automaton.parsers import (parse_yaml, _parse_providers,
        _parse_gosund_provider, _parse_fujitsu_provider, _parse_string,
        _parse_devices, _parse_components, _parse_triggers, _parse_aqi_trigger,
        _parse_time_trigger, _parse_weekday_trigger, _parse_random_trigger,
        _parse_timedelta, _parse_sunrise_trigger, _parse_sunset_trigger,
        _parse_temp_trigger, _parse_actions, _parse_method_name,
        AutomatonConfigParsingError)
from automaton.providers.fujitsu import FujitsuProvider
from automaton.providers.gosund import GosundProvider
from automaton.providers.noop import NoopProvider, NoopDevice
from automaton.sensors import SunSensor, TimeSensor
from automaton.triggers import (AQITrigger, TimeTrigger, IsoWeekdayTrigger, RandomTrigger,
        SunriseTrigger, SunsetTrigger, TemperatureTrigger, WebhookTrigger)

import testdata.custom_code

_test_context = Context.from_yaml({
        'aqi': {'api_key': '123abc'},
        'location': {'latitude': 40.689, 'longitude': -74.044},
        'timezone': 'America/Los_Angeles',
        'weather': {'api_key': 'abc123'},
})
_test_device_name_1 = 'device-1'
_test_device_name_2 = 'device-2'
_test_device_name_3 = 'switch-A'
_test_device_name_4 = 'switch-B'
_test_device_name_5 = 'sensor-A'
_test_device_name_6 = 'sensor-B'
_test_device_1 = NoopDevice(_test_device_name_1, _test_device_name_1)
_test_device_2 = NoopDevice(_test_device_name_2, _test_device_name_2)
_test_device_3 = NoopDevice(_test_device_name_3, _test_device_name_3)
_test_device_4 = NoopDevice(_test_device_name_4, _test_device_name_4)
_test_device_5 = NoopDevice(_test_device_name_5, _test_device_name_5)
_test_device_6 = NoopDevice(_test_device_name_6, _test_device_name_6)
_test_context.devices = {
        _test_device_name_1: _test_device_1,
        _test_device_name_2: _test_device_2,
        _test_device_name_3: _test_device_3,
        _test_device_name_4: _test_device_4,
        _test_device_name_5: _test_device_5,
        _test_device_name_6: _test_device_6,
}

def _relative_to_full_path(path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, path)

_test_parse_yaml_expect = [
        Component(
            name='air-purifier 0',
            ifs=[AQITrigger],
            thens=[TurnOnAction],
            elses=[TurnOffAction],
        ),
        Component(
            name='party-light 0',
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOnAction],
            elses=[],
        ),
        Component(
            name='party-light 1',
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOffAction],
            elses=[],
        ),
        Component(
            name='floor-lamp 0',
            ifs=[SunsetTrigger],
            thens=[TurnOnAction],
            elses=[],
        ),
        Component(
            name='floor-lamp 1',
            ifs=[TimeTrigger],
            thens=[TurnOnAction, TurnOnAction],
            elses=[],
        ),
        Component(
            name='floor-lamp 2',
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOffAction],
            elses=[],
        ),
        Component(
            name='floor-lamp 3',
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOffAction],
            elses=[],
        ),
        Component(
            name='floor-lamp 4',
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOffAction],
            elses=[],
        ),
        Component(
            name='floor-lamp 5',
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOffAction],
            elses=[],
        ),
        Component(
            name='edge-cases 0',
            ifs=[],
            thens=[],
            elses=[],
        ),
        Component(
            name='temperature 0',
            ifs=[TemperatureTrigger],
            thens=[],
            elses=[],
        ),
        Component(
            name='webhooks 0',
            ifs=[IsoWeekdayTrigger, WebhookTrigger],
            thens=[TurnOnAction],
            elses=[],
        ),
        Component(
            name='webhooks 1',
            ifs=[IsoWeekdayTrigger, WebhookTrigger],
            thens=[TurnOnAction],
            elses=[],
        ),
        Component(
            name='webhooks 2',
            ifs=[WebhookTrigger, IsoWeekdayTrigger],
            thens=[TurnOffAction],
            elses=[],
        ),
        Component(
            name='ranges 0',
            ifs=[AQITrigger, IsoWeekdayTrigger, TimeTrigger, SunriseTrigger,
                SunsetTrigger, TemperatureTrigger],
            thens=[],
            elses=[],
        ),
        Component(
            name='sensors 0',
            ifs=[TemperatureTrigger, AQITrigger],
            thens=[],
            elses=[],
        ),
        Component(
            name='custom-code 0',
            ifs=[],
            thens=[ExecuteCodeAction, ExecuteCodeAction],
            elses=[],
        ),
]

_test_parse_yaml_expect_context_dict = {
        'devices': {
            'switch-A': NoopDevice,
            'bulb-A': NoopDevice,
            'bulb-B': NoopDevice,
            'bulb-C': NoopDevice,
            'sensor-A': NoopDevice,
            'sensor-B': NoopDevice,
            'sensor-C': NoopDevice,
            'sensor-D': NoopDevice,
            'sensor-E': NoopDevice,
        },
        'time_sensor': TimeSensor,
}

def test_parse_yaml():
    expect_comps, expect_context_dict = (
            _test_parse_yaml_expect, _test_parse_yaml_expect_context_dict)

    config_fullpath = _relative_to_full_path('./testdata/full.yml')
    actual_comps, actual_context = parse_yaml(config_fullpath)

    assert len(actual_comps) == len(expect_comps), (
            'wrong number of components returned')
    for actual, expect in zip(actual_comps, expect_comps):
        assert isinstance(actual, Component), 'wrong type returned'
        assert actual.name == expect.name, 'wrong name returned'
        assert actual.enabled, 'action should be enabled'
        assert len(actual.ifs) == len(expect.ifs), 'wrong number of ifs'
        for trigger, exp_cls in zip(actual.ifs, expect.ifs):
            assert isinstance(trigger, exp_cls), 'wrong trigger class'
        assert len(actual.thens) == len(expect.thens), 'wrong number of thens'
        for action, exp_cls in zip(actual.thens, expect.thens):
            assert isinstance(action, exp_cls), 'wrong thens class'
        assert len(actual.elses) == len(expect.elses), 'wrong number of elses'
        for action, exp_cls in zip(actual.elses, expect.elses):
            assert isinstance(action, exp_cls), 'wrong elses class'

    def assert_key_name_and_value_class(exp, act):
        if isinstance(act, dict):
            assert len(act) == len(exp), 'wrong number of items in context'
            for exp_key, act_key in zip(exp, act):
                assert act_key == exp_key, 'wrong key name returned'
                assert_key_name_and_value_class(exp[exp_key], act[act_key])
            return
        assert isinstance(act, exp), 'wrong class type found'

    actual_context_dict = actual_context.context
    assert len(actual_context_dict) == len(expect_context_dict), (
            'wrong size context dict returned')
    assert_key_name_and_value_class(expect_context_dict, actual_context_dict)

_test__TriggersConf = (
        ({}, Exception, Exception, Exception, Exception),
        ([], Exception, Exception, Exception, Exception),
        ({'location': None}, Exception, Exception, Exception, Exception),
        ({'location': [123, 456]}, Exception, Exception, Exception, Exception),
        ({'location': {'latitude': None, 'longitude': None}}, Exception,
            Exception, Exception, Exception),
        ({'location': {'latitude': [123], 'longitude': [456]}}, Exception,
            Exception, Exception, Exception),
        ({'location': {'latitude': '123', 'longitude': '456'}}, Exception,
            Exception, Exception, Exception),
        ({'location': {'latitude': 123, 'longitude': 456}}, 123, 456,
            Exception, Exception),
        ({'location': {'latitude': 123.4, 'longitude': 456.7}}, 123.4, 456.7,
            Exception, Exception),
        ({'aqi': None}, Exception, Exception, Exception, Exception),
        ({'aqi': ['abc123']}, Exception, Exception, Exception, Exception),
        ({'aqi': 'abc123'}, Exception, Exception, Exception, Exception),
        ({'aqi': {'api_key': None}}, Exception, Exception, Exception, Exception),
        ({'aqi': {'api_key': ['abc123']}}, Exception, Exception, Exception,
            Exception),
        ({'aqi': {'api_key': 12345}}, Exception, Exception, Exception,
            Exception),
        ({'aqi': {'api_key': 'abc123'}}, Exception, Exception, 'abc123',
            Exception),
        ({'timezone': None}, Exception, Exception, Exception, Exception),
        ({'timezone': 'America/Los_Angeles'}, Exception, Exception, Exception,
            'America/Los_Angeles'),
)

@pytest.mark.parametrize('raw_yml,exp_lat,exp_long,exp_api_key,exp_tz',
        _test__TriggersConf)
def test__TriggersConf(raw_yml, exp_lat, exp_long, exp_api_key, exp_tz):
    context = Context.from_yaml(raw_yml)

    def _test_property(prop_name, expect):
        should_raise = expect is Exception
        try:
            actual = getattr(context, prop_name)
            assert expect == actual, f'incorrect property {prop_name}'
        except AutomatonConfigParsingError:
            assert should_raise, 'should not have raised an exception'
        else:
            assert not should_raise, 'should have raised an exception'

    def _test_time_sensor():
        loc_missing = exp_lat is Exception and exp_long is Exception
        tz_missing = exp_tz is Exception
        should_raise = loc_missing and tz_missing
        try:
            time_sensor_1 = context.time_sensor
            time_sensor_2 = context.time_sensor
            assert time_sensor_1 is time_sensor_2, (
                    'created more than one TimeSensor')
        except AutomatonConfigParsingError:
            assert should_raise, 'should not have raised an exception'
        else:
            assert not should_raise, 'should have raised an exception'

    _test_property('latitude', exp_lat)
    _test_property('longitude', exp_long)
    _test_property('aqi_api_key', exp_api_key)
    _test_property('timezone', exp_tz)
    _test_time_sensor()

_test__parse_providers = (
        ({}, {'noop': NoopProvider}, False),
        ({'purple': None}, {}, True),
        (
            {
                'gosund': {
                    'username': 'username',
                    'password': 'password',
                    'access_id': 'access_id',
                    'access_key': 'access_key',
                },
            },
            {'noop': NoopProvider, 'gosund': GosundProvider},
            False,
        ),
        (
            {'noop': None},
            {'noop': NoopProvider},
            False,
        ),
        (
            {
                'gosund': {
                    'username': 'username',
                    'password': 'password',
                    'access_id': 'access_id',
                    'access_key': 'access_key',
                },
                'noop': None,
            },
            {'noop': NoopProvider, 'gosund': GosundProvider,},
            False,
        ),
)

@pytest.mark.parametrize('providers,expects,raises', _test__parse_providers)
def test__parse_providers(providers, expects, raises, monkeypatch):
    monkeypatch.setattr('gosundpy.Gosund.__init__', lambda *a: None)
    try:
        actuals = _parse_providers(providers)
    except AutomatonConfigParsingError:
        assert raises, 'should not have raised'
        return
    else:
        assert not raises, 'should have raised'

    assert len(expects) == len(actuals), 'wrong number of providers returned'
    for (act_name, act_prov), (exp_name, exp_prov) in zip(
            actuals.items(), expects.items()):
        assert act_name == exp_name, 'wrong name returnd for provider'
        assert isinstance(act_prov, exp_prov), 'wrong provider class returned'

_test__parse_gosund_provider = (
        ({}, True),
        (
            {
                'password': 'password',
                'access_id': 'access_id',
                'access_key': 'access_key',
            }, True,
        ),
        (
            {
                'username': 'username',
                'access_id': 'access_id',
                'access_key': 'access_key',
            }, True,
        ),
        (
            {
                'username': 'username',
                'password': 'password',
                'access_key': 'access_key',
            }, True,
        ),
        (
            {
                'username': 'username',
                'password': 'password',
                'access_id': 'access_id',
            }, True,
        ),
        (
            {
                'username': 'username',
                'password': 'password',
                'access_id': 'access_id',
                'access_key': 'access_key',
            }, False,
        ),
)

@pytest.mark.parametrize('provider,raises', _test__parse_gosund_provider)
def test__parse_gosund_provider(provider, raises, monkeypatch):
    monkeypatch.setattr('gosundpy.Gosund.__init__', lambda *a: None)
    try:
        actual = _parse_gosund_provider(provider)
        assert isinstance(actual, GosundProvider)
    except AutomatonConfigParsingError:
        assert raises, 'should not have raised'
    else:
        assert not raises, 'should have raised'

_test__parse_fujitsu_provider = (
        ({}, True),
        ({'password': 'password'}, True),
        ({'username': 'username'}, True),
        ({'username': 'username', 'password': 'password'}, False),
)

@pytest.mark.parametrize('provider,raises', _test__parse_fujitsu_provider)
def test__parse_fujitsu_provider(provider, raises):
    try:
        actual = _parse_fujitsu_provider(provider)
        assert isinstance(actual, FujitsuProvider)
    except AutomatonConfigParsingError:
        assert raises, 'should not have raised'
    else:
        assert not raises, 'should have raised'

_test__parse_string = (
        ('', '', False),
        ('hello', 'hello', False),
        ('${env:MY_EXISTING_ENV_1}', 'value1', False),
        ('hello ${env:MY_EXISTING_ENV_1}', 'hello value1', False),
        ('${env:MY_EXISTING_ENV_1} world', 'value1 world', False),
        ('hello ${env:MY_EXISTING_ENV_1} world', 'hello value1 world', False),
        ('${env:MY_EXISTING_ENV_1} ${env:MY_EXISTING_ENV_2}', 'value1 value2',
            False),
        ('${env:MY_NON_EXISTING_ENV}', '', True),
)

@pytest.mark.parametrize('string,expect,raises', _test__parse_string)
def test__parse_string(string, expect, raises, monkeypatch):
    monkeypatch.setenv('MY_EXISTING_ENV_1', 'value1')
    monkeypatch.setenv('MY_EXISTING_ENV_2', 'value2')
    try:
        assert expect == _parse_string(string)
    except AutomatonConfigParsingError:
        assert raises, 'should not have raised'
    else:
        assert not raises, 'should have raised'

_test__parse_devices = (
        ({}, {}, False),
        ({'switch-A': {}}, {}, True),
        ({'switch-A': {'id': '123abc'}}, {}, True),
        ({'switch-A': {'provider': 'noop'}}, {}, True),
        ({'switch-A': {'provider': 'purple', 'id': '123abc'}}, {}, True),
        (
            {'switch-A': {'provider': 'noop', 'id': '123abc'}},
            {'switch-A': NoopDevice},
            False,
        ),
        (
            {
                'switch-A': {'provider': 'noop', 'id': '123abc'},
                'switch-B': {'provider': 'noop', 'id': '123abc'},
            },
            {
                'switch-A': NoopDevice,
                'switch-B': NoopDevice,
            },
            False,
        ),
)

_test__parse_devices_providers = {
        'noop': NoopProvider(),
}

@pytest.mark.parametrize('devices,expects,raises', _test__parse_devices)
def test__parse_devices(devices, expects, raises):
    try:
        actuals = _parse_devices(devices, _test__parse_devices_providers)
    except AutomatonConfigParsingError:
        assert raises, 'should not have raised'
        return
    else:
        assert not raises, 'should have raised'

    assert len(expects) == len(actuals), 'wrong number of devices returned'
    for (act_name, act_device), (exp_name, exp_device) in zip(
            actuals.items(), expects.items()):
        assert exp_name == act_name, 'wrong device name returned'
        assert isinstance(act_device, exp_device), 'wrong class type returned'

_test__parse_components = (
        ({}, []),
        ({'automation-1': {'enabled': False}}, []),
        ({'automation-2': {'enabled': True}}, []),
        ({'automation-3': {'components': []}}, []),
        (
            {
                'automation-4': {
                    'components': [{}],
                },
            },
            [
                Component(
                    name='automation-4 0',
                    ifs=[],
                    thens=[],
                    elses=[],
                ),
            ],
        ),
        (
            {
                'automation-5': {
                    'enabled': True,
                    'components': [
                        {
                            'if': {'aqi': '>100', 'weekday': 'monday'},
                            'then': {'turn-on': 'switch-A, switch-B'},
                            'else': {'turn-off': 'switch-A, switch-B'},
                        },
                    ],
                },
            },
            [
                Component(
                    name='automation-5 0',
                    ifs=[AQITrigger, IsoWeekdayTrigger],
                    thens=[TurnOnAction, TurnOnAction],
                    elses=[TurnOffAction, TurnOffAction],
                ),
            ],
        ),
        (
            {
                'automation-6': {
                    'components': [
                        {'if': {'aqi': '>100'}},
                    ],
                },
            },
            [
                Component(
                    name='automation-6 0',
                    ifs=[AQITrigger],
                    thens=[],
                    elses=[],
                ),
            ],
        ),
        (
            {
                'automation-7': {
                    'components': [
                        {'if': {'aqi': '>100'}},
                        {'if': {'aqi': '>100'}},
                    ],
                },
            },
            [
                Component(
                    name='automation-7 0',
                    ifs=[AQITrigger],
                    thens=[],
                    elses=[],
                ),
                Component(
                    name='automation-7 1',
                    ifs=[AQITrigger],
                    thens=[],
                    elses=[],
                ),
            ],
        ),
        (
            {
                'automation-8': {
                    'components': [
                        {'if': {'aqi': '>100'}},
                    ],
                },
                'automation-9': {
                    'components': [
                        {'if': {'aqi': '>100'}},
                    ],
                },
            },
            [
                Component(
                    name='automation-8 0',
                    ifs=[AQITrigger],
                    thens=[],
                    elses=[],
                ),
                Component(
                    name='automation-9 0',
                    ifs=[AQITrigger],
                    thens=[],
                    elses=[],
                ),
            ],
        ),
        (
            {
                'automation-10': {
                    'components': [
                        {'if': {'webhook': '/hello'}},
                    ],
                },
                'automation-11': {
                    'components': [
                        {'if': {'aqi': '>100', 'webhook': '/purple'}},
                    ],
                },
            },
            [
                Component(
                    name='automation-10 0',
                    ifs=[WebhookTrigger],
                    thens=[],
                    elses=[],
                ),
                Component(
                    name='automation-11 0',
                    ifs=[AQITrigger, WebhookTrigger],
                    thens=[],
                    elses=[],
                ),
            ],
        ),
        (
            {
                'automation-12': {
                    'components': [{
                        'if': {
                            'sensor-A': {'temp': '60-65'},
                            'sensor-B': {'aqi': '100-200'},
                        },
                    }],
                },
            },
            [
                Component(
                    name='automation-12 0',
                    ifs=[TemperatureTrigger, AQITrigger],
                    thens=[],
                    elses=[],
                ),
            ],
        ),
)

@pytest.mark.parametrize('automations,expects', _test__parse_components)
def test__parse_components(automations, expects):
    actuals = _parse_components(automations, _test_context)
    assert len(actuals) == len(expects), 'wrong number of components returned'
    for actual, expect in zip(actuals, expects):
        assert isinstance(actual, Component), 'wrong type returned'
        assert actual.enabled, 'action should be enabled'
        assert actual.name == expect.name, 'wrong name assigned'
        assert len(actual.ifs) == len(expect.ifs), 'wrong number of ifs'
        for trigger, exp_cls in zip(actual.ifs, expect.ifs):
            assert isinstance(trigger, exp_cls), 'wrong trigger class'
        assert len(actual.thens) == len(expect.thens), 'wrong number of thens'
        for action, exp_cls in zip(actual.thens, expect.thens):
            assert isinstance(action, exp_cls), 'wrong thens class'
        assert len(actual.elses) == len(expect.elses), 'wrong number of elses'
        for action, exp_cls in zip(actual.elses, expect.elses):
            assert isinstance(action, exp_cls), 'wrong elses class'

_test__parse_triggers = (
        ({'aqi': '==100'}, [AQITrigger]),
        ({'time': '10:00am'}, [TimeTrigger]),
        ({'weekday': 'monday'}, [IsoWeekdayTrigger]),
        ({'random': 0.25}, [RandomTrigger]),
        ({'sunrise': 120}, [SunriseTrigger]),
        ({'sunset': 120}, [SunsetTrigger]),

        (
            {
                'aqi': '==100',
                'time': '10:00am',
                'weekday': 'monday',
                'random': 0.25,
                'sunrise': 120,
                'sunset': 120,
            },
            [
                AQITrigger,
                TimeTrigger,
                IsoWeekdayTrigger,
                RandomTrigger,
                SunriseTrigger,
                SunsetTrigger,
            ],
        ),
)

@pytest.mark.parametrize('ifs,expect_classes', _test__parse_triggers)
def test__parse_triggers(ifs, expect_classes):
    actual = _parse_triggers(ifs, _test_context)
    assert len(actual) == len(ifs), 'wrong number of triggers returned'
    for trigger, expect_class in zip(actual, expect_classes):
        assert isinstance(trigger, expect_class), 'wrong trigger type returned'

_test__parse_aqi_trigger = (
        ('<10', lambda a: a < 10),
        ('< 10', lambda a: a < 10),
        ('> 10', lambda a: a > 10),
        ('>10', lambda a: a > 10),

        ('==10', lambda a: a == 10),
        ('== 10', lambda a: a == 10),

        ('<=10', lambda a: a <= 10),
        ('>=10', lambda a : a >= 10),
        ('>= 10', lambda a : a >= 10),

        ('10-20', lambda a: a>=10 and a<=20),
        ('30-31,40-41,50,>60', lambda a: (
            (a>=30 and a<=31) or (a>=40 and a<=41) or (a==50) or (a>60))),
        ('100-90', lambda a: False),
        ('<10,>90', lambda a: a < 10 or a > 90),
        ('>66.8', lambda a: a > 66.8),
        ('65.5-66.5', lambda a: a >= 65.5 and a <= 66.5),
        ('65.5', lambda a: a == 65.5),
        (65.5, lambda a: a == 65.5),
        (60, lambda a: a == 60),
)

@pytest.mark.parametrize('value,expect', _test__parse_aqi_trigger)
def test__parse_aqi_trigger(value, expect, mock_aqi_sensor):
    actual = _parse_aqi_trigger(value, _test_context)

    assert actual.aqi_sensor.params['api_key'] == '123abc', 'wrong aqi api key'
    assert actual.aqi_sensor.params['latitude'] == 40.689, 'wrong latitude'
    assert actual.aqi_sensor.params['longitude'] == -74.044, 'wrong longitude'
    assert actual.aqi_sensor.params['format'] == 'application/json', 'wrong format'

    actual.aqi_sensor = mock_aqi_sensor
    for i in range(100):
        mock_aqi_sensor.aqi = i
        assert actual.check() == expect(i), (
                f'wrong value returned by func at index {i}')

        mock_aqi_sensor.aqi = i + 0.5
        assert actual.check() == expect(i + 0.5), (
                f'wrong value returned by func at index {i + 0.5}')

_test__parse_aqi_trigger_failures = (
        '>purple',
        '< green',
        '=10',
        '+10',
        '- 10',
        '> 10 ; assert False',
        '<10-20',
        '10->20',
        '==10-30',
        '10-20-30',
        {'hello': 'world'},
)

@pytest.mark.parametrize('value', _test__parse_aqi_trigger_failures)
def test__parse_aqi_trigger_failures(value):
    try:
        _parse_aqi_trigger(value, _test_context)
    except AutomatonConfigParsingError:
        pass
    else:
        raise AssertionError('should have raised an exception')

_test__parse_time_trigger = (
        ('12:00am', [0], False),
        ('1:00am', [60], False),
        ('2:00am', [120], False),
        ('3:00am', [180], False),
        ('4:00am', [240], False),
        ('5:00am', [300], False),
        ('6:00am', [360], False),
        ('7:00am', [420], False),
        ('8:00am', [480], False),
        ('9:00am', [540], False),
        ('10:00am', [600], False),
        ('11:00am', [660], False),
        ('12:00pm', [720], False),
        ('1:00pm', [780], False),
        ('2:00pm', [840], False),
        ('3:00pm', [900], False),
        ('4:00pm', [960], False),
        ('5:00pm', [1020], False),
        ('6:00pm', [1080], False),
        ('7:00pm', [1140], False),
        ('8:00pm', [1200], False),
        ('9:00pm', [1260], False),
        ('10:00pm', [1320], False),
        ('11:00pm', [1380], False),

        ('1:00AM', [60], False),
        ('1:00 am', [60], False),
        ('1:15am', [75], False),
        ('12:00am,3:15pm', [0, 915], False),

        ('13:00am', None, True),
        ('1:60am', None, True),
        ('1:00', None, True),

        ('6:00am-6:05am', [360, 361, 362, 363, 364, 365], False),
        ('11:59am-12:02pm', [719, 720, 721, 722], False),
        ('2:30pm-2:30pm', [870], False),
        ('12:00am,12:05am-12:07am,12:10am', [0, 5, 6, 7, 10], False),
        ('12:00am - 12:02am', [0, 1, 2], False),

        ('12:00am-', None, True),
        ('12:00am--12:02am', None, True),
        ('6:00am-6:05am-6:10am', None, True),
)

@pytest.mark.parametrize('value,expect,raises', _test__parse_time_trigger)
def test__parse_time_trigger(value, expect, raises):
    try:
        actual = _parse_time_trigger(value, _test_context)
        assert isinstance(actual, TimeTrigger), 'wrong trigger type'
        assert expect == actual.times, 'wrong times found'+str(actual.times)
    except AutomatonConfigParsingError:
        assert raises, 'error should not have been raised'
    else:
        assert not raises, 'error not raised'

_test__parse_weekday_trigger = (
        ('MONDAY', [1], False),
        ('monday', [1], False),
        ('mon', [1], False),
        ('tuesday', [2], False),
        ('tues', [2], False),
        ('tue', [2], False),
        ('wednesday', [3], False),
        ('wed', [3], False),
        ('thursday', [4], False),
        ('thurs', [4], False),
        ('thur', [4], False),
        ('thu', [4], False),
        ('friday', [5], False),
        ('fri', [5], False),
        ('saturday', [6], False),
        ('sat', [6], False),
        ('sunday', [7], False),
        ('sun', [7], False),

        ('mon,tuesday,thur', [1, 2, 4], False),
        ('mon,tu', None, True),

        ('monday-friday', [1, 2, 3, 4, 5], False),
        ('mon-fri', [1, 2, 3, 4, 5], False),
        ('monday - friday', [1, 2, 3, 4, 5], False),
        ('sat-tues', [6, 7, 1, 2], False),
        ('mon-mon', [1], False),
        ('mon-tue,fri,sun', [1, 2, 5, 7], False),
        ('sun-sat', [7, 1, 2, 3, 4, 5, 6], False),
        ('mon-sun', [1, 2, 3, 4, 5, 6, 7], False),
        ('tue-mon', [2, 3, 4, 5, 6, 7, 1], False),
        ('mon-', None, True),
        ('-fri', None, True),
)

@pytest.mark.parametrize('value,expect,raises', _test__parse_weekday_trigger)
def test__parse_weekday_trigger(value, expect, raises):
    try:
        actual = _parse_weekday_trigger(value, _test_context)
        assert isinstance(actual, IsoWeekdayTrigger), 'wrong trigger type'
        assert expect == actual.isoweekdays, 'wrong isoweekdays found'
    except AutomatonConfigParsingError:
        assert raises, 'error should not have been raised'
    else:
        assert not raises, 'error not raised'

_test__parse_random_trigger = (
        (0.5, False),
        (0, False),
        ('1.5', False),
        ('cookies', True),
)

@pytest.mark.parametrize('value,raises', _test__parse_random_trigger)
def test__parse_random_trigger(value, raises):
    try:
        actual = _parse_random_trigger(value, _test_context)
        assert isinstance(actual, RandomTrigger), 'wrong trigger type returned'
        assert actual.probability == float(value), 'wrong probability'
    except ValueError as e:
        assert raises, 'should not have raised error'
    else:
        assert not raises, 'should have raised error'

_test__parse_timedelta = (
        (1, list(range(1, 2)), False),
        ('1', list(range(1, 2)), False),
        (-10, list(range(-10, -9)), False),
        ('-10', list(range(-10, -9)), False),
        ('10-12', list(range(10, 13)), False),
        ('10 - 12', list(range(10, 13)), False),
        ('-2-0', list(range(-2, 1)), False),
        ('-2-1', list(range(-2, 2)), False),
        ('-2 - 1', list(range(-2, 2)), False),
        ('-2 -1', list(range(-2, 2)), False),
        ('-5 - -3', list(range(-5, -2)), False),
        ('1,10-12,15-16',
            list(range(1, 2)) + list(range(10, 13)) + list(range(15, 17)),
            False),
        ('1, 10-12', list(range(1, 2)) + list(range(10, 13)), False),

        (2.5, None, True),
        ('2.5', None, True),
        ('2.5-3.5', None, True),
        ('2hrs', None, True),
        ('>2', None, True),
        ('<2', None, True),
        ('==2', None, True),
        ('10-', None, True),
        ('- 10', None, True),
        ('2:60', None, True),
)

@pytest.mark.parametrize('value,expect,raises', _test__parse_timedelta)
def test__parse_timedelta(value, expect, raises):
    try:
        assert expect == _parse_timedelta(value)
    except AutomatonConfigParsingError:
        raised = True
    else:
        raised = False
    assert raises == raised, 'error handling was wrong'

def test__parse_sunrise_trigger():
    trigger = _parse_sunrise_trigger(10, _test_context)
    assert isinstance(trigger, SunriseTrigger), 'wrong trigger type returnd'
    assert isinstance(trigger.sun_sensor, SunSensor), 'wrong sensor type returned'
    assert trigger.timedeltas == [10], 'wrong timedelta on trigger'

def test__parse_sunrise_trigger_raises():
    value = '2hrs'
    try:
        _parse_sunrise_trigger(value, _test_context)
    except AutomatonConfigParsingError:
        raised = True
    else:
        raised = False
    assert raised, 'should have raised error'

def test__parse_sunset_trigger():
    trigger = _parse_sunset_trigger(10, _test_context)
    assert isinstance(trigger, SunsetTrigger), 'wrong trigger type returnd'
    assert isinstance(trigger.sun_sensor, SunSensor), 'wrong sensor type returned'
    assert trigger.timedeltas== [10], 'wrong timedelta on trigger'

def test__parse_sunset_trigger_raises():
    value = '2hrs'
    try:
        _parse_sunset_trigger(value, _test_context)
    except AutomatonConfigParsingError:
        raised = True
    else:
        raised = False
    assert raised, 'should have raised error'

_test__parse_temp_trigger = (
        ('<10', lambda a: a < 10),
        ('< 10', lambda a: a < 10),
        ('> 10', lambda a: a > 10),
        ('>10', lambda a: a > 10),

        ('==10', lambda a: a == 10),
        ('== 10', lambda a: a == 10),

        ('<=10', lambda a: a <= 10),
        ('>=10', lambda a : a >= 10),
        ('>= 10', lambda a : a >= 10),

        ('10-20', lambda a: a>=10 and a<=20),
        ('30-31,40-41,50,>60', lambda a: (
            (a>=30 and a<=31) or (a>=40 and a<=41) or (a==50) or (a>60))),
        ('100-90', lambda a: False),
        ('<10,>90', lambda a: a < 10 or a > 90),
        ('>66.8', lambda a: a > 66.8),
        ('65.5-66.5', lambda a: a >= 65.5 and a <= 66.5),
        ('65.5', lambda a: a == 65.5),
        (65.5, lambda a: a == 65.5),
        (60, lambda a: a == 60),
)

@pytest.mark.parametrize('value,expect', _test__parse_temp_trigger)
def test__parse_temp_trigger(value, expect, mock_weather_sensor):
    actual = _parse_temp_trigger(value, _test_context)

    assert actual.weather_sensor.location == (40.689, -74.044) , (
            'wrong weather sensor location')
    assert actual.weather_sensor.owm_mgr.API_key == 'abc123', (
            'wrong weather api key')

    actual.weather_sensor = mock_weather_sensor
    for i in range(100):
        mock_weather_sensor.temp = i
        assert actual.check() == expect(i), (
                f'wrong value returned by func at index {i}')

        mock_weather_sensor.temp = i + 0.5
        assert actual.check() == expect(i + 0.5), (
                f'wrong value returned by func at index {i+0.5}')

_test__parse_temp_trigger_failures = (
        '>purple',
        '< green',
        '=10',
        '+10',
        '- 10',
        '> 10 ; assert False',
        '<10-20',
        '10->20',
        '==10-30',
        '10-20-30',
        {'hello': 'world'},
)

@pytest.mark.parametrize('value', _test__parse_temp_trigger_failures)
def test__parse_temp_trigger_failures(value):
    try:
        _parse_temp_trigger(value, _test_context)
    except AutomatonConfigParsingError:
        pass
    else:
        raise AssertionError('should have raised an exception')

_test__parse_actions_tests = (
        (
            {
                'turn-on': _test_device_name_1,
            },
            [
                TurnOnAction(_test_device_1),
            ],
            False,
        ),
        (
            {'turn-off': _test_device_name_2},
            [TurnOffAction(_test_device_2)],
            False,
        ),
        (
            {
                'turn-on': _test_device_name_1,
                'turn-off': _test_device_name_2,
            },
            [
                TurnOnAction(_test_device_1),
                TurnOffAction(_test_device_2),
            ],
            False,
        ),
        (
            {'do-something': _test_device_name_2},
            [],
            True,
        ),
        (
            {'turn-on': 'some wrong device'},
            [],
            True,
        ),
        (
            {'exec': 'testdata.custom_code.custom_function'},
            [ExecuteCodeAction(
                testdata.custom_code.custom_function,
                _test_context.context,
            )],
            False,
        ),
        (
            {'exec': 'testdata.custom_code.custom_function,testdata.custom_code.custom_function'},
            [
                ExecuteCodeAction(
                    testdata.custom_code.custom_function,
                    _test_context.context,
                ),
                ExecuteCodeAction(
                    testdata.custom_code.custom_function,
                    _test_context.context,
                ),
            ],
            False,
        ),
        (
            {'exec': 'testdata.custom_code.non_existent_function'},
            [],
            True,
        ),
        (
            {'exec': 'testdata.non_existent_module.custom_code'},
            [],
            True,
        ),
        (
            {'exec': 'print'},
            [],
            True,
        ),
)

@pytest.mark.parametrize('thens,expect,raises', _test__parse_actions_tests)
def test__parse_actions(thens, expect, raises):
    try:
        actual = _parse_actions(thens, _test_context)
    except AutomatonConfigParsingError:
        actual = []
        raised = True
    else:
        raised = False

    assert len(expect) == len(actual), 'wrong number of actions returned'
    assert raises == raised, 'exception raising was wrong'

    def assert_turn_on_off_actions(expect, actual):
        assert expect.device == actual.device, 'wrong device found on action'

    def assert_execute_code_action(expect, actual):
        assert expect.execute_method == actual.execute_method, (
                'wrong execution method on action')
        assert expect.context == actual.context, 'wrong context found on action'

    for exp, act in zip(expect, actual):
        if isinstance(exp, (TurnOnAction, TurnOffAction)):
            assert_turn_on_off_actions(exp, act)
        elif isinstance(exp, ExecuteCodeAction):
            assert_execute_code_action(exp,act)
        else:
            raise AssertionError(f'expectation {exp} not found')
        assert exp.name == act.name, 'wrong action name'

def test__parse_method_name():
    expect = testdata.custom_code.custom_function
    actual = _parse_method_name('testdata.custom_code.custom_function')
    assert expect == actual, 'wrong method returned'
