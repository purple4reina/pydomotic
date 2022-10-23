import pytest

from automaton.devices import SwitchDevice, LightBulbDevice

def test_switch_device_turn_on(mock_provider):
    name = 'my device'
    device = SwitchDevice(name, mock_provider)
    device.turn_on()
    assert mock_provider.turn_on_called, 'provider.turn_on not called'
    assert device.name == name, 'device has wrong name'

def test_switch_device_turn_off(mock_provider):
    name = 'my device'
    device = SwitchDevice(name, mock_provider)
    device.turn_off()
    assert mock_provider.turn_off_called, 'provider.turn_off not called'
    assert device.name == name, 'device has wrong name'

def test_light_bulb_device_turn_on(mock_provider):
    name = 'my device'
    device = LightBulbDevice(name, mock_provider)
    device.turn_on()
    assert mock_provider.turn_on_called, 'provider.turn_on not called'
    assert device.name == name, 'device has wrong name'

def test_light_bulb_device_turn_off(mock_provider):
    name = 'my device'
    device = LightBulbDevice(name, mock_provider)
    device.turn_off()
    assert mock_provider.turn_off_called, 'provider.turn_off not called'
    assert device.name == name, 'device has wrong name'
