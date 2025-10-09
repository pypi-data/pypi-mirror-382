import pytest
from unittest.mock import Mock, patch, ANY

import bisslog_schema.setup.bisslog_setup_deco as decorators

@pytest.fixture
def mock_registry():
    with patch.object(decorators, "setup_registry") as mock:
        mock.register_setup = Mock()
        mock.register_runtime_config = Mock()
        yield mock

def test_bisslog_setup_registers_function(mock_registry):
    @decorators.bisslog_setup(enabled=True)
    def my_setup():
        pass

    mock_registry.register_setup.assert_called_once_with(ANY, enabled=True)

def test_bisslog_setup_disabled(mock_registry):
    @decorators.bisslog_setup(enabled=False)
    def my_disabled_setup():
        pass

    mock_registry.register_setup.assert_called_once_with(ANY, enabled=False)

def test_bisslog_runtime_config_registers_function(mock_registry):
    @decorators.bisslog_runtime_config("flask", "cli", enabled=True)
    def my_config():
        pass

    mock_registry.register_runtime_config.assert_called_once_with(ANY, ["flask", "cli"], enabled=True)

def test_bisslog_runtime_config_disabled(mock_registry):
    @decorators.bisslog_runtime_config("cli", enabled=False)
    def my_disabled_config():
        pass

    mock_registry.register_runtime_config.assert_called_once_with(ANY, ["cli"], enabled=False)

def test_bisslog_runtime_config_with_no_runtimes_raises_if_registry_checks_it(mock_registry):
    mock_registry.register_runtime_config.side_effect = ValueError("No runtimes specified")

    with pytest.raises(ValueError, match="No runtimes specified"):
        @decorators.bisslog_runtime_config(enabled=True)
        def invalid_config():
            pass
