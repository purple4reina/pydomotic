import pytest

from automaton.components import Component

def test_component_one_true_if(mock_true_trigger, mock_action_1,
        mock_action_2):
    comp = Component(
            ifs=[mock_true_trigger],
            thens=[mock_action_1],
            elses=[mock_action_2],
    )
    comp.run()
    assert mock_true_trigger.check_called, 'trigger.check not called'
    assert mock_action_1.run_called, 'then action.run not called'
    assert not mock_action_2.run_called, 'else action.run called'

def test_component_one_false_if(mock_false_trigger, mock_action_1,
        mock_action_2):
    comp = Component(
            ifs=[mock_false_trigger],
            thens=[mock_action_1],
            elses=[mock_action_2],
    )
    comp.run()
    assert mock_false_trigger.check_called, 'trigger.check not called'
    assert not mock_action_1.run_called, 'then action.run called'
    assert mock_action_2.run_called, 'else action.run not called'

def test_component_one_true_if_one_false_if(mock_true_trigger,
        mock_false_trigger, mock_action_1, mock_action_2):
    comp = Component(
            ifs=[mock_false_trigger, mock_true_trigger],
            thens=[mock_action_1],
            elses=[mock_action_2],
    )
    comp.run()
    assert mock_false_trigger.check_called, 'false trigger.check not called'
    assert not mock_true_trigger.check_called, 'true trigger.check called'
    assert not mock_action_1.run_called, 'then action.run called'
    assert mock_action_2.run_called, 'else action.run not called'
