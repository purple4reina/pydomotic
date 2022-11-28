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
