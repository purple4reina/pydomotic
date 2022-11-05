import logging
import os
import re
import datetime
import yaml

from .actions import TurnOnAction, TurnOffAction
from .components import Component
from .providers.noop import NoopProvider
from .sensors import TimeSensor
from .triggers import (AQITrigger, TimeTrigger, IsoWeekdayTrigger,
        RandomTrigger, SunriseTrigger, SunsetTrigger)

logger = logging.getLogger(__name__)

def parse_yaml(config_file):
    with open(config_file) as f:
        conf = yaml.safe_load(f)
    triggers_conf = _TriggersConf.from_yaml(conf.get('triggers', {}))
    providers = _parse_providers(conf.get('providers', {}))
    devices = _parse_devices(conf.get('devices', {}), providers)
    components = _parse_components(conf.get('automations', {}), devices,
            triggers_conf)
    return components

class _TriggersConf(object):

    def __init__(self, latitude, longitude, aqi_api_key):
        self._latitude = latitude
        self._longitude = longitude
        self._time_sensor = None
        self._aqi_api_key = aqi_api_key

    @staticmethod
    def from_yaml(triggers):
        try:
            location = triggers.get('location', {})
            latitude = location.get('latitude')
            longitude = location.get('longitude')
        except Exception as e:
            logger.warning('failed to parse location, ignoring: '
                    f'[{e.__class__.__name__}] {e}')
            latitude = longitude = None

        try:
            aqi = triggers.get('aqi', {})
            aqi_api_key = _parse_string(aqi.get('api_key'))
        except Exception as e:
            logger.warning('failed to parse aqi api_key, ignoring: '
                    f'[{e.__class__.__name__}] {e}')
            aqi_api_key = None

        return _TriggersConf(latitude, longitude, aqi_api_key)

    @property
    def latitude(self):
        if self._latitude is None:
            raise AutomatonConfigParsingError(
                    'latitude value required for location')
        if not isinstance(self._latitude, (int, float)):
            raise AutomatonConfigParsingError(
                    'latitude must be a number, not '
                    f'{self._latitude.__class__.__name__}')
        return self._latitude

    @property
    def longitude(self):
        if self._longitude is None:
            raise AutomatonConfigParsingError(
                    'longitude value required for location')
        if not isinstance(self._longitude, (int, float)):
            raise AutomatonConfigParsingError(
                    'longitude must be a number, not '
                    f'{self._longitude.__class__.__name__}')
        return self._longitude

    @property
    def time_sensor(self):
        if self._time_sensor is None:
            self._time_sensor = TimeSensor(self.latitude, self.longitude)
        return self._time_sensor

    @property
    def aqi_api_key(self):
        if not self._aqi_api_key:
            raise AutomatonConfigParsingError('aqi api key required')
        if not isinstance(self._aqi_api_key, str):
            raise AutomatonConfigParsingError(
                    'aqi api_key must be a string, not '
                    f'{self._aqi_api_key.__class__.__name__}')
        return self._aqi_api_key

def _parse_providers(providers_conf):
    providers = {}
    for name, provider in providers_conf.items():
        logging.info(f'preparing provider {name}')
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
        logger.info(f'preparing device {name}')
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

def _parse_components(automations, devices, triggers_conf):
    components = []
    for name, automation in automations.items():
        logger.info(f'preparing automation {name}')
        if not automation.get('enabled', True):
            continue
        for num, component in enumerate(automation.get('components', [])):
            name = f'{name} {num}'
            ifs = component.get('if', {})
            thens = component.get('then', {})
            elses = component.get('else', {})
            logger.info(f'adding component {name}')
            components.append(Component(
                name=name,
                ifs=_parse_triggers(ifs, triggers_conf),
                thens=_parse_actions(thens, devices),
                elses=_parse_actions(elses, devices),
            ))
    return components

def _parse_triggers(ifs, triggers_conf):
    triggers = []
    for trigger_type, trigger_value in ifs.items():
        trigger_type = trigger_type.lower()
        logger.debug(f'adding {trigger_type} trigger')
        if trigger_type == 'aqi':
            parser = _parse_aqi_trigger
        elif trigger_type == 'time':
            parser = _parse_time_trigger
        elif trigger_type == 'weekday':
            parser = _parse_weekday_trigger
        elif trigger_type == 'random':
            parser = _parse_random_trigger
        elif trigger_type == 'sunrise':
            parser = _parse_sunrise_trigger
        elif trigger_type == 'sunset':
            parser = _parse_sunset_trigger
        else:
            raise AutomatonConfigParsingError(
                    f'unknown trigger type "{trigger_type}"')
        triggers.append(parser(trigger_value, triggers_conf))
    return triggers

_aqi_value_re = re.compile(r'(<|>|==)\s*(\d+)')
def _parse_aqi_trigger(value, triggers_conf):
    m = _aqi_value_re.fullmatch(value)
    if not m:
        raise AutomatonConfigParsingError(
                f'invalid aqi trigger value "{value}", expecting value like '
                '">100", "<100", or "==100"')
    num = int(m.group(2))
    if m.group(1) == '>':
        _check_func = lambda a: a > num
    elif m.group(1) == '<':
        _check_func = lambda a: a < num
    elif m.group(1) == '==':
        _check_func = lambda a: a == num

    return AQITrigger(_check_func, api_key=triggers_conf.aqi_api_key,
            latitude=triggers_conf.latitude, longitude=triggers_conf.longitude)

_time_re = re.compile(r'(10|11|12|[1-9]):([0-5][0-9])\s*([ap]m)')
def _parse_time_trigger(value, triggers_conf):
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
    return TimeTrigger(*times, time_sensor=triggers_conf.time_sensor)

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

def _parse_weekday_trigger(value, triggers_conf):
    isoweekdays = []
    for weekday in value.split(','):
        weekday = weekday.strip().lower()
        isoweekday = _isoweekdays.get(weekday)
        if isoweekday is None:
            raise AutomatonConfigParsingError(
                    f'"{weekday}" is not a valid weekday')
        isoweekdays.append(isoweekday)
    return IsoWeekdayTrigger(*isoweekdays,
            time_sensor=triggers_conf.time_sensor)

def _parse_random_trigger(value, triggers_conf):
    probability = float(value)
    return RandomTrigger(probability)

def _parse_timedelta(value):
    if isinstance(value, (int, float)):
        return datetime.timedelta(minutes=int(value))
    raise AutomatonConfigParsingError(
            f'unknown time delta "{value}", expecting value like "2:15" '
            'or integer minutes')

def _parse_sunrise_trigger(value, triggers_conf):
    return SunriseTrigger(_parse_timedelta(value),
            time_sensor=triggers_conf.time_sensor)

def _parse_sunset_trigger(value, triggers_conf):
    return SunsetTrigger(_parse_timedelta(value),
            time_sensor=triggers_conf.time_sensor)

def _parse_actions(thens, devices):
    actions = []
    for action_type, device_names in thens.items():
        logger.debug(f'adding {action_type} action')
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
