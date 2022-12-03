import pytest

from automaton.providers.fujitsu import FujitsuProvider, FujitsuDevice
from automaton.providers.gosund import GosundProvider, GosundDevice
from automaton.providers.noop import NoopProvider, NoopDevice

_test_provider_interface = (
        FujitsuProvider,
        GosundProvider,
        NoopProvider,
)
_test_provider_interface_attrs = (
        'get_device',
)

@pytest.mark.parametrize('provider', _test_provider_interface)
def test_provider_interface(provider):
    for attr in _test_provider_interface_attrs:
        assert hasattr(provider, attr), f'provider requires attr {attr}'

_test_device_interface = (
        FujitsuDevice,
        GosundDevice,
        NoopDevice,
)
_test_device_interface_attrs = (
        'turn_on',
        'turn_off',
        'switch',
)

@pytest.mark.parametrize('device', _test_device_interface)
def test_device_interface(device):
    for attr in _test_device_interface_attrs:
        assert hasattr(device, attr), f'device requires attr {attr}'

def test_fujitsu_provider(patch_fujitsu):
    patch_provider = patch_fujitsu.provider
    patch_device = patch_fujitsu.device

    username, password, tokenpath, dsn = 'usr', 'passwd', '/path', 'dsn'

    provider = FujitsuProvider(username, password, tokenpath=tokenpath)
    assert patch_provider.username == username, 'wrong username'
    assert patch_provider.password == password, 'wrong password'
    assert patch_provider.tokenpath == tokenpath, 'wrong tokenpath'

    device = provider.get_device(dsn)
    assert patch_device == patch_fujitsu.device, 'wrong device'
    assert patch_device.dsn == dsn, 'wrong dsn'
    assert patch_device.api == provider.fujitsu, 'wrong api'

    device.turn_on()
    assert patch_device.turn_on_called, 'device.turn_on not called'

    device.turn_off()
    assert patch_device.turn_off_called, 'device.turn_off not called'

    device.switch()
    assert not patch_device.switch_called, 'device.switch called'

def test_gosund_provider(patch_gosundpy):
    username, password, access_id, access_key = 'usr', 'passwd', 'id', 'key'
    provider = GosundProvider(username, password, access_id, access_key)
    assert patch_gosundpy.username == username, 'wrong username'
    assert patch_gosundpy.password == password, 'wrong password'
    assert patch_gosundpy.access_id == access_id, 'wrong access_id'
    assert patch_gosundpy.access_key == access_key, 'wrong access_key'

    device = provider.get_device('id')
    assert device.device == patch_gosundpy.provider.device, 'wrong device'

    device.turn_on()
    assert device.device.turn_on_called, 'device.turn_on not called'

    device.turn_off()
    assert device.device.turn_off_called, 'device.turn_off not called'

    device.switch()
    assert device.device.switch_called, 'device.switch not called'
