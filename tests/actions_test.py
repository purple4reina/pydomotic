import pytest

from automaton.actions import TurnOnAction, TurnOffAction

_test_action_interface = (
        (TurnOnAction(None), 'turn_on_action'),
        (TurnOffAction(None), 'turn_off_action'),
)

@pytest.mark.parametrize('instance,exp_name', _test_action_interface)
def test_action_interface(instance, exp_name):
    assert instance.name == exp_name, 'wrong value for name found'
    assert hasattr(instance, 'run'), 'instance does not have attr run'
    assert callable(instance.run), 'instance.run is not callable'

def test_turn_on_action(mock_device):
    action = TurnOnAction(mock_device)
    action.run()
    assert action.device.turn_on_called, 'device.turn_on not called'

def test_turn_off_action(mock_device):
    action = TurnOffAction(mock_device)
    action.run()
    assert action.device.turn_off_called, 'device.turn_off not called'
