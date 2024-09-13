from pydomotic.providers.airthings import AirthingsProvider, AirthingsDevice
from pydomotic.providers.base import DeviceGroup
from pydomotic.providers.ecobee import EcobeeProvider, EcobeeDevice
from pydomotic.providers.fujitsu import FujitsuProvider, FujitsuDevice
from pydomotic.providers.moen import MoenProvider, MoenDevice
from pydomotic.providers.noop import NoopProvider, NoopDevice
from pydomotic.providers.tuya import TuyaProvider, TuyaDevice

def test_fujitsu_provider(patch_fujitsu):
    patch_provider = patch_fujitsu.provider
    patch_device = patch_fujitsu.device

    usr, pwd, tkn, dsn, name, desc = 'usr', 'pwd', 'tkn', 'dsn', 'name', 'desc'

    provider = FujitsuProvider(usr, pwd, tokenpath=tkn)
    assert patch_provider.username == usr, 'wrong username'
    assert patch_provider.password == pwd, 'wrong password'
    assert patch_provider.tokenpath == tkn, 'wrong tokenpath'

    device = provider.get_device(dsn, name, desc)
    assert patch_device == patch_fujitsu.device, 'wrong device'
    assert patch_device.dsn == dsn, 'wrong dsn'
    assert patch_device.api == provider.fujitsu, 'wrong api'
    assert device.name == f'fujitsu_device {name}', 'wrong name'
    assert device.device_name == name, 'wrong device_name'
    assert device.device_description == desc, 'wrong device_description'

    device.turn_on()
    assert patch_device.turn_on_called, 'device.turn_on not called'

    device.turn_off()
    assert patch_device.turn_off_called, 'device.turn_off not called'

    device.switch()
    assert not patch_device.switch_called, 'device.switch called'

def test_fujitsu_device(patch_fujitsu):
    name, desc = 'device_name', 'device_description'
    device = FujitsuDevice(patch_fujitsu.device, name, desc)
    assert device.device == patch_fujitsu.device, 'wrong device'
    assert device.name == f'fujitsu_device {name}', 'wrong  name'
    assert device.device_name == name, 'wrong device_name'
    assert device.device_description == desc, 'wrong device_description'

    device.turn_on()
    assert patch_fujitsu.device.turn_on_called, 'device.turn_on not called'

    device.turn_off()
    assert patch_fujitsu.device.turn_off_called, 'device.turn_off not called'

    device.switch()
    assert not patch_fujitsu.device.switch_called, 'device.switch called'

def test_tuya_provider(patch_gosundpy):
    usr, pwd, a_id, a_key, name, desc = 'usr', 'pwd', 'id', 'key', 'name', 'desc'
    provider = TuyaProvider(usr, pwd, a_id, a_key)
    assert patch_gosundpy.username == usr, 'wrong username'
    assert patch_gosundpy.password == pwd, 'wrong password'
    assert patch_gosundpy.access_id == a_id, 'wrong access_id'
    assert patch_gosundpy.access_key == a_key, 'wrong access_key'
    assert patch_gosundpy.cache_secs == None, 'wrong caching value'
    assert patch_gosundpy.timeout == None, 'wrong timeout value'

    device = provider.get_device('id', name, desc)
    assert device.device == patch_gosundpy.provider.device, 'wrong device'
    assert device.name == f'tuya_device {name}', 'wrong name'
    assert device.device_name == name, 'wrong device_name'
    assert device.device_description == desc, 'wrong device_description'

    device.turn_on()
    assert device.device.turn_on_called, 'device.turn_on not called'

    device.turn_off()
    assert device.device.turn_off_called, 'device.turn_off not called'

    device.switch()
    assert device.device.switch_called, 'device.switch not called'

    device.current_temperature()
    assert device.device.get_temperature_called, 'device.current_temperature not called'

def test_tuya_provider_device_status_cache(patch_gosundpy):
    cache_secs = None
    provider = TuyaProvider('u', 'p', 'ai', 'ak',
            status_cache_seconds=cache_secs)
    assert patch_gosundpy.cache_secs == cache_secs, 'wrong caching value'

    cache_secs = 50
    provider = TuyaProvider('u', 'p', 'ai', 'ak',
            status_cache_seconds=cache_secs)
    assert patch_gosundpy.cache_secs == cache_secs, 'wrong caching value'

def test_tuya_provider_timeout(patch_gosundpy):
    timeout = None
    provider = TuyaProvider('u', 'p', 'ai', 'ak', timeout=timeout)
    assert patch_gosundpy.timeout == timeout, 'wrong timeout value'

    timeout = 50
    provider = TuyaProvider('u', 'p', 'ai', 'ak', timeout=timeout)
    assert patch_gosundpy.timeout == timeout, 'wrong timeout value'

def test_tuya_device(patch_gosundpy):
    name, desc = 'device_name', 'device_description'
    device = TuyaDevice(patch_gosundpy.device, name, desc)
    assert device.device == patch_gosundpy.device, 'wrong device'
    assert device.name == f'tuya_device {name}', 'wrong name'
    assert device.device_name == name, 'wrong device_name'
    assert device.device_description == desc, 'wrong device_description'

    device.turn_on()
    assert patch_gosundpy.device.turn_on_called, 'device.turn_on not called'

    device.turn_off()
    assert patch_gosundpy.device.turn_off_called, 'device.turn_off not called'

    device.switch()
    assert patch_gosundpy.device.switch_called, 'device.switch not called'

def test_noop_provider():
    device_id, name, desc = 'device_id', 'device_name', 'device_description'
    provider = NoopProvider()
    device = provider.get_device(device_id, name, desc)
    assert isinstance(device, NoopDevice), 'wrong device type'
    assert device.device == device_id, 'wrong device_id'
    assert device.name == f'noop_device {name}', 'wrong name'
    assert device.device_name == name, 'wrong device_name'
    assert device.device_description == desc, 'wrong device_description'

def test_airthings_provider(patch_airthings):
    client_id, client_secret, name, desc = 'c_id', 'c_secret', 'name', 'desc'
    provider = AirthingsProvider(client_id, client_secret)
    assert patch_airthings.client_id == client_id, 'wrong client_id'
    assert patch_airthings.client_secret == client_secret, 'wrong client_secret'
    assert patch_airthings.timeout == None, 'wrong timeout value'

    device = provider.get_device('id', name, desc)
    assert device.device == patch_airthings.provider.device, 'wrong device'
    assert device.name == f'airthings_device {name}', 'wrong name'
    assert device.device_name == name, 'wrong device_name'
    assert device.device_description == desc, 'wrong device_description'

    assert device.current_temperature() == patch_airthings.device.temperature, 'wrong temperature'
    assert device.current_humidity() == patch_airthings.device.humidity, 'wrong humidity'
    assert device.current_radon() == patch_airthings.device.radon, 'wrong radon'

def test_airthings_device(patch_airthings):
    name, desc = 'device_name', 'device_description'
    device = AirthingsDevice(patch_airthings.device, name, desc)
    assert device.device == patch_airthings.device, 'wrong device'
    assert device.name == f'airthings_device {name}', 'wrong name'
    assert device.device_name == name, 'wrong device_name'
    assert device.device_description == desc, 'wrong device_description'

    assert device.current_temperature() == patch_airthings.device.temperature, 'wrong temperature'
    assert device.current_humidity() == patch_airthings.device.humidity, 'wrong humidity'
    assert device.current_radon() == patch_airthings.device.radon, 'wrong radon'

def test_airthings_provider_data_cache(patch_airthings):
    cache_secs = None
    provider = AirthingsProvider('id', 'secret', data_cache_seconds=cache_secs)
    assert patch_airthings.cache_secs == cache_secs, 'wrong caching value'

    cache_secs = 50
    provider = AirthingsProvider('id', 'secret', data_cache_seconds=cache_secs)
    assert patch_airthings.cache_secs == cache_secs, 'wrong caching value'

def test_airthings_provider_timeout(patch_airthings):
    timeout = None
    provider = AirthingsProvider('i', 's', timeout=timeout)
    assert patch_airthings.timeout == timeout, 'wrong timeout value'

    timeout = 50
    provider = AirthingsProvider('i', 's', timeout=timeout)
    assert patch_airthings.timeout == timeout, 'wrong timeout value'

def test_moen_provider(patch_moen):
    usr, pwd, name, desc = 'usr', 'pwd', 'name', 'desc'
    provider = MoenProvider(usr, pwd)
    assert patch_moen.username == usr, 'wrong username'
    assert patch_moen.password == pwd, 'wrong password'

    device = provider.get_device(patch_moen.device_id, name, desc)
    assert isinstance(device, MoenDevice), 'wrong device type'
    assert isinstance(device.device, MoenDevice.API), 'wrong device type'
    assert device.device.device_id == patch_moen.device_id, 'wrong device_id'
    assert device.device.flo == patch_moen.provider, 'wrong flo'

    device.turn_on()
    assert patch_moen.open_valve_called, 'flo.open_valve not called'
    device.turn_off()
    assert patch_moen.close_valve_called, 'flo.close_valve not called'

    mode, params = 'away', {'param': 'value'}
    device.set_mode(mode, params)
    assert patch_moen.set_mode_called_args == (patch_moen.location_id, mode, params), (
            'flo.set_mode not called with correct args')

def test_ecobee_provider(patch_ecobee):
    app_key, refresh_token, name, desc = 'app_key', 'refresh_token', 'name', 'desc'
    provider = EcobeeProvider(app_key, refresh_token)
    assert patch_ecobee.app_key == app_key, 'wrong app_key'
    assert patch_ecobee.refresh_token == refresh_token, 'wrong refresh_token'

    device = provider.get_device('id', name, desc)
    assert device.device == patch_ecobee.provider.device, 'wrong device'
    assert device.name == f'ecobee_device {name}', 'wrong name'
    assert device.device_name == name, 'wrong device_name'
    assert device.device_description == desc, 'wrong device_description'

    device.turn_on()
    assert device.device.turn_fan_on_called, 'device.turn_on not called'

    device.turn_off()
    assert device.device.turn_fan_off_called, 'device.turn_off not called'

    device.current_temperature()
    assert device.device.get_temperature_called, 'device.current_temperature not called'

def test_ecobee_device(patch_ecobee):
    name, desc = 'device_name', 'device_description'
    device = EcobeeDevice(patch_ecobee.device, name, desc)
    assert device.device == patch_ecobee.device, 'wrong device'
    assert device.name == f'ecobee_device {name}', 'wrong name'
    assert device.device_name == name, 'wrong device_name'
    assert device.device_description == desc, 'wrong device_description'

    device.turn_on()
    assert patch_ecobee.device.turn_fan_on_called, 'device.turn_on not called'

    device.turn_off()
    assert patch_ecobee.device.turn_fan_off_called, 'device.turn_off not called'

    device.current_temperature()
    assert patch_ecobee.device.get_temperature_called, 'device.get_temperature not called'

def test_device_group(mock_devices):
    group = DeviceGroup(mock_devices, 'group_name')
    assert len(group.devices) == len(mock_devices), 'wrong number of devices'
    assert group.name == 'device_group group_name', 'wrong name'

    group.turn_on()
    for device in mock_devices:
        assert device.turn_on_called, 'device.turn_on not called'

    group.turn_off()
    for device in mock_devices:
        assert device.turn_off_called, 'device.turn_off not called'

    group.switch()
    for device in mock_devices:
        assert device.switch_called, 'device.switch not called'

    try:
        group.non_existent_method()
        assert False, 'non_existent_method should raise AttributeError'
    except AttributeError:
        pass

    mock_devices[0].purple_called = False
    mock_devices[1].purple_called = False
    mock_devices[2].purple_called = False

    mock_devices[0].purple = lambda: setattr(mock_devices[0], 'purple_called', True)

    try:
        group.purple()
        assert False, 'device.purple should raise AttributeError'
    except AttributeError:
        for device in mock_devices:
            assert not device.purple_called, 'device.purple called'

    mock_devices[1].purple = lambda: setattr(mock_devices[1], 'purple_called', True)
    mock_devices[2].purple = lambda: setattr(mock_devices[2], 'purple_called', True)

    group.purple()
    for device in mock_devices:
        assert device.purple_called, 'device.purple not called'
