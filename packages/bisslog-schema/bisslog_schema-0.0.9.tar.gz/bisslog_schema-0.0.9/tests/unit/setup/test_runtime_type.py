import pytest
from bisslog_schema.setup.runtime_type import RuntimeType


def test_runtime_type_members_exist():
    assert RuntimeType.CLI == "cli"
    assert RuntimeType.FLASK == "flask"
    assert RuntimeType.DJANGO == "django"
    assert RuntimeType.FASTAPI == "fastapi"
    assert RuntimeType.LAMBDA == "lambda"
    assert RuntimeType.RABBITMQ == "rabbitmq"
    assert RuntimeType.KAFKA == "kafka"
    assert RuntimeType.REDIS == "redis"
    assert RuntimeType.CRON == "cron"


def test_runtime_type_instantiation_from_string():
    assert RuntimeType("cli") is RuntimeType.CLI
    assert RuntimeType("flask") is RuntimeType.FLASK
    assert RuntimeType("cron") is RuntimeType.CRON


def test_runtime_type_invalid_value():
    with pytest.raises(ValueError):
        RuntimeType("invalid_runtime")
