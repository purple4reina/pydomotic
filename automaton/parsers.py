import logging
import os
import re
import yaml

from .actions import (TurnOnAction, TurnOffAction, SwitchAction,
        ExecuteCodeAction)
from .components import Component
from .context import Context
from .exceptions import AutomatonConfigParsingError
from .providers.noop import NoopProvider
from .triggers import (AQITrigger, TimeTrigger, IsoWeekdayTrigger,
        RandomTrigger, SunriseTrigger, SunsetTrigger, TemperatureTrigger,
        WebhookTrigger)

logger = logging.getLogger(__name__)

def parse_yaml(config_file=None, s3=None):
    data = _get_config_data(config_file, s3)
    return parse_raw_yaml(data)

def parse_raw_yaml(raw_conf):
    conf = yaml.safe_load(raw_conf) if raw_conf else {}
    context = Context.from_yaml(conf.get('triggers', {}))
    context.providers = _parse_providers(conf.get('providers', {}))
    context.devices = _parse_devices(conf.get('devices', {}), context.providers)
    components = _parse_components(conf.get('automations', {}), context)
    return components, context

def _get_config_data(config_file, s3):
    if config_file:
        with open(config_file) as f:
            return f.read()
    elif s3:
        # TODO: test
        return _get_config_from_s3(s3)
    logger.info('no config file or s3 data provided, skipping')

def _get_config_from_s3(s3):
    # TODO: test
    try:
        bucket, key = s3
    except:
        raise AutomatonConfigParsingError('malformed s3 object: '
                'expecting tuple like (bucket, key)')

    try:
        import boto3
        client = boto3.client('s3')
        response = client.get_object(Bucket=bucket, Key=key)
        logger.debug('configuration successfully fetched from s3')
        return response['Body'].read()
    except Exception as e:
        logger.warning('unable to fetch configuration from s3: '
                f'[{e.__class__.__name__}] {e}')
        return None

def _parse_providers(providers_conf):
    providers = {
            'noop': NoopProvider(),
    }
    for name, provider in providers_conf.items():
        logging.info(f'preparing provider {name}')
        if name == 'gosund':
            providers['gosund'] = _parse_gosund_provider(provider)
        elif name == 'noop':
            pass  # already added
        elif name == 'fujitsu':
            providers['fujitsu'] = _parse_fujitsu_provider(provider)
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

def _parse_fujitsu_provider(provider):
    for key in ('username', 'password'):
        if key not in provider:
            raise AutomatonConfigParsingError(
                    f'provider fujitsu requires key "{key}"')

    username = _parse_string(provider['username'])
    password = _parse_string(provider['password'])

    from .providers.fujitsu import FujitsuProvider
    return FujitsuProvider(username, password)

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
            devices[name] = provider.get_device(device_id, name)
        except Exception as e:
            raise AutomatonConfigParsingError(
                    f'unable to get device "{name}": {e}')
    return devices

def _parse_components(automations, context):
    components = []
    for name, automation in automations.items():
        logger.info(f'preparing automation {name}')
        if not automation.get('enabled', True):
            continue
        for num, component in enumerate(automation.get('components', [])):
            component_name = f'{name} {num}'
            ifs = component.get('if') or {}
            thens = component.get('then') or {}
            elses = component.get('else') or {}
            logger.info(f'adding component {component_name}')
            components.append(Component(
                name=component_name,
                ifs=_parse_triggers(ifs, context),
                thens=_parse_actions(thens, context),
                elses=_parse_actions(elses, context),
                enabled=True,
            ))
    return components

def _parse_triggers(ifs, context):
    triggers = []
    for trigger_type, trigger_value in ifs.items():
        logger.debug(f'adding {trigger_type} trigger')
        triggers.append(_parse_trigger(trigger_type, trigger_value, context))
    return triggers

def _parse_trigger(typ, value, context, sensor=None):
    if typ == 'aqi':
        trigger = _parse_aqi_trigger(value, context, sensor=sensor)
    elif typ == 'time':
        trigger = _parse_time_trigger(value, context, sensor=sensor)
    elif typ == 'weekday':
        trigger = _parse_weekday_trigger(value, context, sensor=sensor)
    elif typ == 'random':
        trigger = _parse_random_trigger(value, context, sensor=sensor)
    elif typ == 'sunrise':
        trigger = _parse_sunrise_trigger(value, context, sensor=sensor)
    elif typ == 'sunset':
        trigger = _parse_sunset_trigger(value, context, sensor=sensor)
    elif typ == 'temp':
        trigger = _parse_temp_trigger(value, context, sensor=sensor)
    elif typ == 'webhook':
        # TODO: test _parse_triggers
        trigger = _parse_webhook_trigger(value, context, sensor=sensor)
    elif typ in context.devices:
        if sensor:
            raise AutomatonConfigParsingError('nested sensor confs not allowed')
        trigger = _parse_sensor(typ, value, context)
    else:
        raise AutomatonConfigParsingError(f'unknown trigger type "{typ}"')
    return trigger

_ranged_value_re = re.compile(r'(<|>|==|<=|>=)?\s*(\d+\.?\d*)')
def _parse_ranged_values(value, typ):
    if not isinstance(value, (str, int, float)):
        raise AutomatonConfigParsingError(
                f'invalid {typ} trigger value "{value}", expecting value like '
                '">100", "<100", or "100"')

    def _ranged_func(start, end):
        return lambda a: a >= start and a <= end

    def _relative_func(op, num):
        if op == '>':
            return lambda a: a > num
        elif op == '<':
            return lambda a: a < num
        elif op == '==':
            return lambda a: a == num
        elif op == '>=':
            return lambda a: a >= num
        elif op == '<=':
            return lambda a: a <= num
        elif op == None:
            return lambda a: a == num

    _check_funcs = []
    for val in str(value).split(','):
        val = val.strip().lower()
        ranged_val = val.split('-')

        if len(ranged_val) == 1:
            m = _ranged_value_re.fullmatch(ranged_val[0].strip())
            if not m:
                raise AutomatonConfigParsingError(
                        f'invalid {typ} trigger value "{val}", expecting value like '
                        '">100", "<100", or "100"')
            _check_func =_relative_func(m.group(1), float(m.group(2)))

        elif len(ranged_val) == 2:
            try:
                start_val = float(ranged_val[0])
                end_val = float(ranged_val[1])
                _check_func = _ranged_func(start_val, end_val)
            except:
                raise AutomatonConfigParsingError(
                        f'invalid {typ} trigger value "{val}", expecting value '
                        'like "80-100"')

        else:
            raise AutomatonConfigParsingError(f'unknown {typ} "{val}')

        _check_funcs.append(_check_func)
    return lambda a: any(fn(a) for fn in _check_funcs)

def _parse_aqi_trigger(value, context, sensor=None):
    _check_func = _parse_ranged_values(value, 'aqi')
    return AQITrigger(_check_func, api_key=context.aqi_api_key,
            latitude=context.latitude, longitude=context.longitude,
            aqi_sensor=sensor)

_time_re = re.compile(r'(10|11|12|[1-9]):([0-5][0-9])\s*([ap]m)')
def _parse_time_trigger(value, context, sensor=None):
    def _parse_single_time(time):
        m = _time_re.fullmatch(time)
        if not m:
            raise AutomatonConfigParsingError(
                    f'unknown time "{time}", expecting time like "HH:MMam"')
        hour, minute = int(m.group(1)), int(m.group(2))
        if hour == 12:
            hour = 0
        if m.group(3) == 'pm':
            hour += 12
        return 60*hour + minute

    times = []
    for time in value.split(','):
        time = time.strip().lower()
        ranged_time = time.split('-')
        start_time = _parse_single_time(ranged_time[0].strip())
        if len(ranged_time) == 1:
            end_time = start_time + 1
        elif len(ranged_time) == 2:
            end_time = _parse_single_time(ranged_time[1].strip()) + 1
        else:
            raise AutomatonConfigParsingError(
                    f'unknown time "{time}", expecting time like '
                    '"HH:MMam-HH:MMam"')
        for minute in range(start_time, end_time):
            times.append(minute)
    return TimeTrigger(times, time_sensor=sensor or context.time_sensor)

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

def _parse_weekday_trigger(value, context, sensor=None):
    def _parse_single_day(weekday):
        isoweekday = _isoweekdays.get(weekday)
        if isoweekday is None:
            raise AutomatonConfigParsingError(
                    f'"{weekday}" is not a valid weekday')
        return isoweekday

    isoweekdays = []
    for weekday in value.split(','):
        weekday = weekday.strip().lower()
        ranged_weekday = weekday.split('-')
        start_weekday = _parse_single_day(ranged_weekday[0].strip())
        if len(ranged_weekday) == 1:
            end_weekday = start_weekday + 1
        elif len(ranged_weekday) == 2:
            end_weekday = _parse_single_day(ranged_weekday[1].strip()) + 1
            if end_weekday <= start_weekday:
                end_weekday += 7
        else:
            raise AutomatonConfigParsingError(f'unknown weekday "{weekday}"')
        for isoweekday in range(start_weekday, end_weekday):
            isoweekdays.append(isoweekday % 7 or 7)
    return IsoWeekdayTrigger(isoweekdays, time_sensor=sensor or context.time_sensor)

def _parse_random_trigger(value, context, sensor=None):
    probability = float(value)
    return RandomTrigger(probability)

_ranged_timedelta_re = re.compile(r'(-?\d+)((\s*-\s*)(-?\d+))?')
def _parse_timedelta(value):
    timedeltas = []
    for delta in str(value).split(','):
        m = _ranged_timedelta_re.fullmatch(delta.strip())
        if not m:
            raise AutomatonConfigParsingError(
                    f'unknown time delta "{value}", expecting value like '
                    '"60", "60-120", or "2:15"')
        start_delta = int(float(m.group(1)))
        end_delta = int(float(m.group(4) or start_delta))
        for i in range(start_delta, end_delta+1):
            timedeltas.append(i)
    return timedeltas

def _parse_sunrise_trigger(value, context, sensor=None):
    return SunriseTrigger(
            _parse_timedelta(value),
            latitude=context.latitude,
            longitude=context.longitude,
            time_sensor=sensor or context.time_sensor,
    )

def _parse_sunset_trigger(value, context, sensor=None):
    return SunsetTrigger(
            _parse_timedelta(value),
            latitude=context.latitude,
            longitude=context.longitude,
            time_sensor=sensor or context.time_sensor,
    )

def _parse_temp_trigger(value, context, sensor=None):
    _check_func = _parse_ranged_values(value, 'temp')
    if sensor:
        kwargs = {'weather_sensor': sensor}
    else:
        kwargs = {
                'api_key': context.weather_api_key,
                'latitude': context.latitude,
                'longitude': context.longitude,
        }
    return TemperatureTrigger(_check_func, **kwargs)

def _parse_webhook_trigger(value, context, sensor=None):
    # TODO: test _parse_webhook_trigger
    return WebhookTrigger(value, sensor or context.webhook_sensor)

def _parse_sensor(device_name, value, context):
    sensor = context.device_sensor(device_name)
    trigger_type, trigger_value = value.popitem()
    if value:
        raise AutomatonConfigParsingError(
                f'sensor trigger {value} ignored, only one trigger allowed '
                'per sensor config')
    return _parse_trigger(trigger_type, trigger_value, context=context,
            sensor=sensor)

def _parse_actions(thens, context):
    actions = []
    for action_type, action_value in thens.items():
        logger.debug(f'adding {action_type} action')
        if action_type == 'exec':
            for method_name in action_value.split(','):
                method_name = method_name.strip()
                actions.append(ExecuteCodeAction(method_name, context.context))
        else:
            if action_type == 'turn-on':
                cls = TurnOnAction
            elif action_type == 'turn-off':
                cls = TurnOffAction
            elif action_type == 'switch':
                cls = SwitchAction
            else:
                raise AutomatonConfigParsingError(
                        f'unknown action type "{action_type}"')
            for device_name in action_value.split(','):
                device_name = device_name.strip()
                device = context.devices.get(device_name)
                if device is None:
                    raise AutomatonConfigParsingError(
                            f'unknown device name "{device_name}"')
                actions.append(cls(device))
    return actions
