import pytest

from automaton.handlers import LambdaHandler

def test_lambda_handler___call__(mock_enabled_component,
        mock_disabled_component):
    handler = LambdaHandler(config_file=None)
    handler.components = [mock_enabled_component, mock_disabled_component]
    handler()
    assert mock_enabled_component.run_called, 'enabled component.run not called'
    assert not mock_disabled_component.run_called, 'disabled component.run called'
