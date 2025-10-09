import pytest
from bisslog_schema.setup.bisslog_setup_registry import BisslogSetupRegistry
from bisslog_schema.setup.runtime_type import RuntimeType
from bisslog_schema.setup.setup_metadata import BisslogSetupFunction, BisslogRuntimeConfig


def dummy_setup():
    pass


def dummy_setup_with_runtime(runtime):
    assert runtime in RuntimeType._value2member_map_


def dummy_runtime_config():
    dummy_runtime_config.was_called = True


def dummy_runtime_config_with_args(arg1):
    dummy_runtime_config_with_args.last_arg = arg1


@pytest.fixture
def registry():
    return BisslogSetupRegistry()


def test_register_setup_once(registry):
    registry.register_setup(dummy_setup)
    assert registry._setup_function == dummy_setup


def test_register_setup_twice_raises(registry):
    registry.register_setup(dummy_setup)
    with pytest.raises(RuntimeError):
        registry.register_setup(lambda: None)


def test_register_runtime_config_direct(registry):
    registry.register_runtime_config(dummy_runtime_config, ["flask"])
    assert "flask" in registry._runtime_functions


def test_register_runtime_config_wildcard(registry):
    registry.register_runtime_config(dummy_runtime_config, ["*-flask-django"])
    assert "flask" not in registry._wildcard_runtime_functions
    assert "django" not in registry._wildcard_runtime_functions
    assert "cli" in registry._wildcard_runtime_functions


def test_register_runtime_config_unknown_runtime(registry):
    registry.register_runtime_config(dummy_runtime_config, ["unknown"])
    assert "unknown" in registry._runtime_functions

def test_register_runtime_config_invalid_wildcard(registry):
    with pytest.raises(ValueError):
        registry.register_runtime_config(dummy_runtime_config, ["*-unknown"])


def test_is_covering_full_true(registry):
    for rt in RuntimeType:
        registry._runtime_functions[rt.value] = dummy_runtime_config
    assert registry.is_covering_full() is True


def test_is_covering_full_false(registry):
    registry._runtime_functions[RuntimeType.CLI.value] = dummy_runtime_config
    assert registry.is_covering_full() is False


def test_get_metadata_contains_setup_and_runtime(registry):
    registry.register_setup(dummy_setup)
    registry.register_runtime_config(dummy_runtime_config, ["flask", "cli"])
    metadata = registry.get_metadata()

    assert isinstance(metadata.setup_function, BisslogSetupFunction)
    assert isinstance(metadata.runtime, dict)
    assert all(isinstance(m, BisslogRuntimeConfig) for m in metadata.runtime.values())


def test_run_setup_executes_setup():
    reg = BisslogSetupRegistry()
    flag = {"called": False}

    def setup(runtime):
        flag["called"] = True

    reg.register_setup(setup)
    reg.run_setup("cli")
    assert flag["called"] is True


def test_run_setup_fallback_to_runtime():
    reg = BisslogSetupRegistry()
    dummy_runtime_config.was_called = False
    reg.register_runtime_config(dummy_runtime_config, ["flask"])
    reg.run_setup("flask")
    assert dummy_runtime_config.was_called is True


def test_run_setup_calls_runtime_with_args():
    reg = BisslogSetupRegistry()
    reg.register_runtime_config(dummy_runtime_config_with_args, ["cli"])
    reg.run_setup("cli", "test_arg")
    assert dummy_runtime_config_with_args.last_arg == "test_arg"
