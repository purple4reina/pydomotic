import pytest

from automaton.actions import TurnOnAction, TurnOffAction

def test_turn_on_action(mock_device):
    action = TurnOnAction(mock_device)
    action.run()
    assert action.device.turn_on_called, 'device.turn_on not called'

def test_turn_off_action(mock_device):
    action = TurnOffAction(mock_device)
    action.run()
    assert action.device.turn_off_called, 'device.turn_off not called'
