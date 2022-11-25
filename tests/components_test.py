import logging
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

def test_component_name():
    comp = Component(name='purple')
    assert comp.name == 'purple', 'wrong component name'
    comp = Component()
    assert comp.name == 'unknown', 'wrong component name'

_test_components_logging = (
        (
            True,
            (
                'running component hello',
                'checking trigger __mock_trigger',
                'trigger passes',
                'checking trigger __mock_trigger',
                'trigger passes',
                'all triggers passed',
                'running action __mock_action 1',
            )
        ),
        (
            False,
            (
                'running component hello',
                'checking trigger __mock_trigger',
                'trigger passes',
                'checking trigger __mock_trigger',
                'trigger failed',
                'running action __mock_action 2',
            )
        ),
)

@pytest.mark.parametrize('passes,exp_logs', _test_components_logging)
def test_components_logging(caplog, mock_true_trigger, mock_false_trigger,
        mock_action_1, mock_action_2, passes, exp_logs):
    caplog.set_level(logging.DEBUG)
    comp = Component(
            name='hello',
            ifs=[mock_true_trigger, mock_true_trigger if passes else mock_false_trigger],
            thens=[mock_action_1],
            elses=[mock_action_2],
    )
    comp.run()

    assert len(exp_logs) == len(caplog.record_tuples), 'wrong number of logs'
    for exp_log, (logger, level, message) in zip(exp_logs, caplog.record_tuples):
        assert logger == 'automaton.components', 'wrong logger found'
        assert level == logging.DEBUG, 'wrong level found'
        assert message == exp_log, 'wrong message found'
