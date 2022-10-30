import datetime
import os
import pytest

from automaton.actions import TurnOnAction, TurnOffAction
from automaton.components import Component
from automaton.parsers import (parse_yaml, _parse_providers,
        _parse_gosund_provider, _parse_string, _parse_devices,
        _parse_components, _parse_triggers, _parse_aqi_trigger,
        _parse_time_trigger, _parse_weekday_trigger, _parse_random_trigger,
        _parse_timedelta, _parse_sunrise_trigger, _parse_sunset_trigger,
        _parse_actions, AutomatonConfigParsingError)
from automaton.providers.gosund import GosundProvider
from automaton.providers.noop import NoopProvider, NoopDevice
from automaton.sensors import SunSensor
from automaton.triggers import (AQITrigger, TimeTrigger, IsoWeekdayTrigger, RandomTrigger,
        SunriseTrigger, SunsetTrigger)

def _relative_to_full_path(path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, path)

_test_parse_yaml_expect = [
        Component(
            ifs=[AQITrigger],
            thens=[TurnOnAction],
            elses=[TurnOffAction],
        ),
        Component(
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOnAction],
        ),
        Component(
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOffAction],
        ),
        Component(
            ifs=[SunsetTrigger],
            thens=[TurnOnAction],
        ),
        Component(
            ifs=[TimeTrigger],
            thens=[TurnOnAction, TurnOnAction],
        ),
        Component(
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOffAction],
        ),
        Component(
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOffAction],
        ),
        Component(
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOffAction],
        ),
        Component(
            ifs=[IsoWeekdayTrigger, TimeTrigger],
            thens=[TurnOffAction],
        ),
]

def test_parse_yaml():
    expects = _test_parse_yaml_expect
    config_fullpath = _relative_to_full_path('./testdata/full.yml')
    actuals = parse_yaml(config_fullpath)

    assert len(actuals) == len(expects), 'wrong number of components returned'
    for actual, expect in zip(actuals, expects):
        assert isinstance(actual, Component), 'wrong type returned'
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

_test__parse_providers = (
        ({}, {}, False),
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
            {'gosund': GosundProvider},
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
            {'gosund': GosundProvider, 'noop': NoopProvider},
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
        ({'automation-4': { 'components': [{}]}}, [Component()]),
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
                Component(ifs=[AQITrigger]),
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
                Component(ifs=[AQITrigger]),
                Component(ifs=[AQITrigger]),
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
                Component(ifs=[AQITrigger]),
                Component(ifs=[AQITrigger]),
            ],
        ),
)
_test__parse_components_devices = {
        'switch-A': 'device-2',
        'switch-B': 'device-3',
}
_test__parse_components_triggers_conf = {
        'location': {'latitude': 40.689, 'longitude': -74.044},
        'aqi': {'api_key': '123abc'},
}

@pytest.mark.parametrize('automations,expects', _test__parse_components)
def test__parse_components(automations, expects):
    actuals = _parse_components(automations, _test__parse_components_devices,
            _test__parse_components_triggers_conf)
    assert len(actuals) == len(expects), 'wrong number of components returned'
    for actual, expect in zip(actuals, expects):
        assert isinstance(actual, Component), 'wrong type returned'
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
_test__parse_triggers_triggers_conf = {
        'location': {'latitude': 40.689, 'longitude': -74.044},
        'aqi': {'api_key': '123abc'},
}

@pytest.mark.parametrize('ifs,expect_classes', _test__parse_triggers)
def test__parse_triggers(ifs, expect_classes):
    actual = _parse_triggers(ifs, _test__parse_triggers_triggers_conf)
    assert len(actual) == len(ifs), 'wrong number of triggers returned'
    for trigger, expect_class in zip(actual, expect_classes):
        assert isinstance(trigger, expect_class), 'wrong trigger type returned'

_test__parse_aqi_trigger = (
        ('<10', lambda a: a < 10),
        ('==10', lambda a: a == 10),
        ('>10', lambda a: a > 10),
)
_test__parse_aqi_trigger_triggers_conf = {
        'location': {'latitude': 40.689, 'longitude': -74.044},
        'aqi': {'api_key': '123abc'},
}

@pytest.mark.parametrize('value,expect', _test__parse_aqi_trigger)
def test__parse_aqi_trigger(value, expect, mock_aqi_sensor):
    actual = _parse_aqi_trigger(value, _test__parse_aqi_trigger_triggers_conf)

    assert actual.sensor.params['api_key'] == '123abc', 'wrong aqi api key'
    assert actual.sensor.params['latitude'] == 40.689, 'wrong latitude'
    assert actual.sensor.params['longitude'] == -74.044, 'wrong longitude'
    assert actual.sensor.params['format'] == 'application/json', 'wrong format'

    actual.sensor = mock_aqi_sensor
    for i in range(100):
        mock_aqi_sensor.aqi = i
        assert actual.check() == expect(i), (
                f'wrong value returned by func at index {i}')

_test__parse_time_trigger = (
        ('12:00am', ((0, 0),), False),
        ('1:00am', ((1, 0),), False),
        ('2:00am', ((2, 0),), False),
        ('3:00am', ((3, 0),), False),
        ('4:00am', ((4, 0),), False),
        ('5:00am', ((5, 0),), False),
        ('6:00am', ((6, 0),), False),
        ('7:00am', ((7, 0),), False),
        ('8:00am', ((8, 0),), False),
        ('9:00am', ((9, 0),), False),
        ('10:00am', ((10, 0),), False),
        ('11:00am', ((11, 0),), False),
        ('12:00pm', ((12, 0),), False),
        ('1:00pm', ((13, 0),), False),
        ('2:00pm', ((14, 0),), False),
        ('3:00pm', ((15, 0),), False),
        ('4:00pm', ((16, 0),), False),
        ('5:00pm', ((17, 0),), False),
        ('6:00pm', ((18, 0),), False),
        ('7:00pm', ((19, 0),), False),
        ('8:00pm', ((20, 0),), False),
        ('9:00pm', ((21, 0),), False),
        ('10:00pm', ((22, 0),), False),
        ('11:00pm', ((23, 0),), False),

        ('1:00AM', ((1, 0),), False),
        ('1:00 am', ((1, 0),), False),
        ('1:15am', ((1, 15),), False),
        ('12:00am,3:15pm', ((0, 0), (15, 15)), False),

        ('13:00am', None, True),
        ('1:60am', None, True),
        ('1:00', None, True),
)

@pytest.mark.parametrize('value,expect,raises', _test__parse_time_trigger)
def test__parse_time_trigger(value, expect, raises):
    try:
        actual = _parse_time_trigger(value)
        assert isinstance(actual, TimeTrigger), 'wrong trigger type'
        assert expect == actual.time_tuples, 'wrong times found'
    except AutomatonConfigParsingError:
        assert raises, 'error should not have been raised'
    else:
        assert not raises, 'error not raised'

_test__parse_weekday_trigger = (
        ('MONDAY', (1,), False),
        ('monday', (1,), False),
        ('mon', (1,), False),
        ('tuesday', (2,), False),
        ('tues', (2,), False),
        ('tue', (2,), False),
        ('wednesday', (3,), False),
        ('wed', (3,), False),
        ('thursday', (4,), False),
        ('thurs', (4,), False),
        ('thur', (4,), False),
        ('thu', (4,), False),
        ('friday', (5,), False),
        ('fri', (5,), False),
        ('saturday', (6,), False),
        ('sat', (6,), False),
        ('sunday', (7,), False),
        ('sun', (7,), False),
        ('mon,tuesday,thur', (1, 2, 4), False),
        ('mon,tu', None, True),
)

@pytest.mark.parametrize('value,expect,raises', _test__parse_weekday_trigger)
def test__parse_weekday_trigger(value, expect, raises):
    try:
        actual = _parse_weekday_trigger(value)
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
        actual = _parse_random_trigger(value)
        assert isinstance(actual, RandomTrigger), 'wrong trigger type returned'
        assert actual.probability == float(value), 'wrong probability'
    except ValueError as e:
        assert raises, 'should not have raised error'
    else:
        assert not raises, 'should have raised error'

_test__parse_timedelta = (
        (1, datetime.timedelta(minutes=1), False),
        (2.5, datetime.timedelta(minutes=2), False),
        (-10, datetime.timedelta(minutes=-10), False),
        ('2hrs', None, True),
)

@pytest.mark.parametrize('value,expect,raises', _test__parse_timedelta)
def test_parse_timedelta(value, expect, raises):
    try:
        assert expect == _parse_timedelta(value)
    except AutomatonConfigParsingError:
        raised = True
    else:
        raised = False
    assert raises == raised, 'error handling was wrong'

def test__parse_sunrise_trigger():
    value = 10
    trigger = _parse_sunrise_trigger(value)
    assert isinstance(trigger, SunriseTrigger), 'wrong trigger type returnd'
    assert isinstance(trigger.sensor, SunSensor), 'wrong sensor type returned'
    exp_delta = datetime.timedelta(minutes=value)
    assert trigger.timedelta == exp_delta, 'wrong timedelta on trigger'

def test__parse_sunrise_trigger_raises():
    value = '2hrs'
    try:
        _parse_sunrise_trigger(value)
    except AutomatonConfigParsingError:
        raised = True
    else:
        raised = False
    assert raised, 'should have raised error'

def test__parse_sunset_trigger():
    value = 10
    trigger = _parse_sunset_trigger(value)
    assert isinstance(trigger, SunsetTrigger), 'wrong trigger type returnd'
    assert isinstance(trigger.sensor, SunSensor), 'wrong sensor type returned'
    exp_delta = datetime.timedelta(minutes=value)
    assert trigger.timedelta == exp_delta, 'wrong timedelta on trigger'

def test__parse_sunset_trigger_raises():
    value = '2hrs'
    try:
        _parse_sunset_trigger(value)
    except AutomatonConfigParsingError:
        raised = True
    else:
        raised = False
    assert raised, 'should have raised error'

_test__parse_actions_device_name_1 = 'name 1'
_test__parse_actions_device_name_2 = 'name 2'
_test__parse_actions_device_1 = 'test device 1'
_test__parse_actions_device_2 = 'test device 2'
_test__parse_actions_tests = (
        (
            {
                'turn-on': _test__parse_actions_device_name_1,
            },
            [
                TurnOnAction(_test__parse_actions_device_1),
            ],
            False,
        ),
        (
            {'turn-off': _test__parse_actions_device_name_2},
            [TurnOffAction(_test__parse_actions_device_2)],
            False,
        ),
        (
            {
                'turn-on': _test__parse_actions_device_name_1,
                'turn-off': _test__parse_actions_device_name_2,
            },
            [
                TurnOnAction(_test__parse_actions_device_1),
                TurnOffAction(_test__parse_actions_device_2),
            ],
            False,
        ),
        (
            {'do-something': _test__parse_actions_device_name_2},
            [],
            True,
        ),
        (
            {'turn-on': 'some wrong device'},
            [],
            True,
        ),
)
_test__parse_actions_devices = {
    _test__parse_actions_device_name_1: _test__parse_actions_device_1,
    _test__parse_actions_device_name_2: _test__parse_actions_device_2,
}

@pytest.mark.parametrize('thens,expect,raises', _test__parse_actions_tests)
def test__parse_actions(thens, expect, raises):
    try:
        actual = _parse_actions(thens, _test__parse_actions_devices)
    except AutomatonConfigParsingError:
        actual = []
        raised = True
    else:
        raised = False

    assert len(expect) == len(actual), 'wrong number of actions returned'
    assert raises == raised, 'exception raising was wrong'
    for i in range(len(actual)):
        assert expect[i].device == actual[i].device, 'wrong device found on action'
