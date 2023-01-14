import pytest

from automaton.actions import (TurnOnAction, TurnOffAction, SwitchAction,
        ExecuteCodeAction)

import testdata.custom_code

class _test_device(object): name = 'device_name'
_test_action_name = (
        (TurnOnAction(_test_device), 'turn_on_action device_name'),
        (TurnOffAction(_test_device), 'turn_off_action device_name'),
        (SwitchAction(_test_device), 'switch_action device_name'),
        (
            ExecuteCodeAction('testdata.custom_code.custom_function', {}),
            'execute_code_action testdata.custom_code.custom_function',
        ),
)

@pytest.mark.parametrize('action,expect', _test_action_name)
def test_action_name(action, expect, patch_gosundpy):
    assert expect == action.name, 'wrong name found for action'

def test_turn_on_action(mock_device):
    action = TurnOnAction(mock_device)
    action.run()
    assert action.device.turn_on_called, 'device.turn_on not called'

def test_turn_off_action(mock_device):
    action = TurnOffAction(mock_device)
    action.run()
    assert action.device.turn_off_called, 'device.turn_off not called'

def test_switch_action(mock_device):
    action = SwitchAction(mock_device)
    action.run()
    assert action.device.switch_called, 'device.switch not called'

_test_execute_code_action_called = []
_test_execute_code_action_context = {'hello': True, 'goodbye': False}
def _test_execute_code_action_test_method(context):
    _test_execute_code_action_called.append(True)
    assert context == _test_execute_code_action_context, 'wrong context given'

def test_execute_code_action():
    action = ExecuteCodeAction(
            'actions_test._test_execute_code_action_test_method',
            _test_execute_code_action_context,
    )
    action.run()
    assert len(_test_execute_code_action_called) == 1, 'custom code method was not called'
