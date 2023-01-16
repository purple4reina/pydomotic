from automaton.providers.fujitsu import FujitsuProvider, FujitsuDevice
from automaton.providers.gosund import GosundProvider, GosundDevice
from automaton.providers.noop import NoopProvider, NoopDevice

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

def test_gosund_provider(patch_gosundpy):
    usr, pwd, a_id, a_key, name, desc = 'usr', 'pwd', 'id', 'key', 'name', 'desc'
    provider = GosundProvider(usr, pwd, a_id, a_key)
    assert patch_gosundpy.username == usr, 'wrong username'
    assert patch_gosundpy.password == pwd, 'wrong password'
    assert patch_gosundpy.access_id == a_id, 'wrong access_id'
    assert patch_gosundpy.access_key == a_key, 'wrong access_key'

    device = provider.get_device('id', name, desc)
    assert device.device == patch_gosundpy.provider.device, 'wrong device'
    assert device.name == f'gosund_device {name}', 'wrong name'
    assert device.device_name == name, 'wrong device_name'
    assert device.device_description == desc, 'wrong device_description'

    device.turn_on()
    assert device.device.turn_on_called, 'device.turn_on not called'

    device.turn_off()
    assert device.device.turn_off_called, 'device.turn_off not called'

    device.switch()
    assert device.device.switch_called, 'device.switch not called'

def test_gosund_device(patch_gosundpy):
    name, desc = 'device_name', 'device_description'
    device = GosundDevice(patch_gosundpy.device, name, desc)
    assert device.device == patch_gosundpy.device, 'wrong device'
    assert device.name == f'gosund_device {name}', 'wrong name'
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
