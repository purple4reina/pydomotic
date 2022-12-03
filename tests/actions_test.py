import pytest

from automaton.actions import TurnOnAction, TurnOffAction, SwitchAction

_test_action_name = (
        (TurnOnAction, 'turn_on_action device_name'),
        (TurnOffAction, 'turn_off_action device_name'),
        (SwitchAction, 'switch_action device_name'),
)

@pytest.mark.parametrize('cls,expect', _test_action_name)
def test_action_name(cls, expect):
    inst = cls(None, 'device_name')
    assert expect == inst.name

def test_turn_on_action(mock_device):
    action = TurnOnAction(mock_device, '')
    action.run()
    assert action.device.turn_on_called, 'device.turn_on not called'

def test_turn_off_action(mock_device):
    action = TurnOffAction(mock_device, '')
    action.run()
    assert action.device.turn_off_called, 'device.turn_off not called'

def test_switch_action(mock_device):
    action = SwitchAction(mock_device, '')
    action.run()
    assert action.device.switch_called, 'device.switch not called'
