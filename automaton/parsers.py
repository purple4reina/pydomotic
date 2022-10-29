import os
import re
import datetime
import yaml

from .actions import TurnOnAction, TurnOffAction
from .components import Component
from .providers.noop import NoopProvider
from .triggers import (AQITrigger, TimeTrigger, IsoWeekdayTrigger,
        RandomTrigger, SunriseTrigger, SunsetTrigger)

# TODO: add debug logging

def parse_yaml(config_file):
    with open(config_file) as f:
        conf = yaml.safe_load(f)
    providers = _parse_providers(conf.get('providers', {}))
    devices = _parse_devices(conf.get('devices', {}), providers)
    components = _parse_components(conf.get('automations', {}), devices)
    return components

def _parse_providers(providers_conf):
    providers = {}
    for name, provider in providers_conf.items():
        if name == 'gosund':
            providers['gosund'] = _parse_gosund_provider(provider)
        elif name == 'noop':
            providers['noop'] = NoopProvider()
        else:
            raise AutomatonConfigParsingError(f'unknown provider "{name}"')
    return providers

def _parse_gosund_provider(provider):
    for key in ('username', 'password', 'access_id', 'access_key'):
        if key not in provider:
            raise AutomatonConfigParsingError(
                    f'provider gosund requires key "{key}"')

    username = _parse_string(provider['username'])
    password = _parse_string(provider['password'])
    access_id = _parse_string(provider['access_id'])
    access_key = _parse_string(provider['access_key'])

    from .providers.gosund import GosundProvider
    return GosundProvider(username, password, access_id, access_key)

_env_re = re.compile(r'\$\{env:(.*?)\}')
def _parse_string(string):
    def _replace_env(m):
        key = m.group(1)
        val = os.environ.get(m.group(1))
        if val is None:
            raise AutomatonConfigParsingError(
                    f'expected environment variable "{key}" not found')
        return val
    return _env_re.sub(_replace_env, string)

def _parse_devices(devices_conf, providers):
    devices = {}
    for name, device in devices_conf.items():
        provider_name = device.get('provider')
        if provider_name is None:
            raise AutomatonConfigParsingError(
                    f'no provider given for device "{name}"')
        provider = providers.get(provider_name)
        if provider is None:
            raise AutomatonConfigParsingError(
                    f'device "{name}" expected provider "{provider_name}" '
                    'not found')
        device_id = device.get('id')
        if device_id is None:
            raise AutomatonConfigParsingError(
                    f'no id given for device "{name}"')
        try:
            devices[name] = provider.get_device(device_id)
        except Exception as e:
            raise AutomatonConfigParsingError(
                    f'unable to get device "{name}": {e}')
    return devices

def _parse_components(automations, devices):
    components = []
    for name, automation in automations.items():
        if not automation.get('enabled', True):
            continue
        for component in automation.get('components', []):
            ifs = component.get('if', {})
            thens = component.get('then', {})
            elses = component.get('else', {})
            components.append(Component(
                ifs=_parse_triggers(ifs),
                thens=_parse_actions(thens, devices),
                elses=_parse_actions(elses, devices),
            ))
    return components

def _parse_triggers(ifs):
    triggers = []
    for trigger_type, trigger_value in ifs.items():
        trigger_type = trigger_type.lower()
        if trigger_type == 'aqi':
            triggers.append(_parse_aqi_trigger(trigger_value))
        elif trigger_type == 'time':
            triggers.append(_parse_time_trigger(trigger_value))
        elif trigger_type == 'weekday':
            triggers.append(_parse_weekday_trigger(trigger_value))
        elif trigger_type == 'random':
            triggers.append(_parse_random_trigger(trigger_value))
        elif trigger_type == 'sunrise':
            triggers.append(_parse_sunrise_trigger(trigger_value))
        elif trigger_type == 'sunset':
            triggers.append(_parse_sunset_trigger(trigger_value))
        else:
            raise AutomatonConfigParsingError(
                    f'unknown trigger type "{trigger_type}"')
    return triggers

def _parse_aqi_trigger(value):
    def _check_func(aqi):
        return eval(f'aqi {value}')
    return AQITrigger(_check_func)

_time_re = re.compile(r'(10|11|12|[1-9]):([0-5][0-9])\s*([ap]m)')
def _parse_time_trigger(value):
    times = []
    for time in value.split(','):
        time = time.strip().lower()
        m = _time_re.fullmatch(time)
        if not m:
            raise AutomatonConfigParsingError(
                    f'unknown time "{time}", expecting time like "HH:MMam"')
        hour, minute = int(m.group(1)), int(m.group(2))
        if hour == 12:
            hour = 0
        if m.group(3) == 'pm':
            hour += 12
        times.append((hour, minute))
    return TimeTrigger(*times)

_isoweekdays = {
        'monday': 1,
        'mon': 1,
        'tuesday': 2,
        'tues': 2,
        'tue': 2,
        'wednesday': 3,
        'wed': 3,
        'thursday': 4,
        'thurs': 4,
        'thur': 4,
        'thu': 4,
        'friday': 5,
        'fri': 5,
        'saturday': 6,
        'sat': 6,
        'sunday': 7,
        'sun': 7,
}

def _parse_weekday_trigger(value):
    isoweekdays = []
    for weekday in value.split(','):
        weekday = weekday.strip().lower()
        isoweekday = _isoweekdays.get(weekday)
        if isoweekday is None:
            raise AutomatonConfigParsingError(
                    f'"{weekday}" is not a valid weekday')
        isoweekdays.append(isoweekday)
    return IsoWeekdayTrigger(*isoweekdays)

def _parse_random_trigger(value):
    probability = float(value)
    return RandomTrigger(probability)

def _parse_timedelta(value):
    if isinstance(value, (int, float)):
        return datetime.timedelta(minutes=int(value))
    raise AutomatonConfigParsingError(
            f'unknown time delta "{value}", expecting value like "2:15" '
            'or integer minutes')

def _parse_sunrise_trigger(value):
    return SunriseTrigger(_parse_timedelta(value))

def _parse_sunset_trigger(value):
    return SunsetTrigger(_parse_timedelta(value))

def _parse_actions(thens, devices):
    actions = []
    for action_type, device_names in thens.items():
        for device_name in device_names.split(','):
            device_name = device_name.strip()
            device = devices.get(device_name)
            if device is None:
                raise AutomatonConfigParsingError(
                        f'unknown device name "{device_name}"')
            if action_type == 'turn-on':
                actions.append(TurnOnAction(device))
            elif action_type == 'turn-off':
                actions.append(TurnOffAction(device))
            else:
                raise AutomatonConfigParsingError(
                        f'unknown action type "{action_type}"')
    return actions

class AutomatonConfigParsingError(Exception):
    pass
