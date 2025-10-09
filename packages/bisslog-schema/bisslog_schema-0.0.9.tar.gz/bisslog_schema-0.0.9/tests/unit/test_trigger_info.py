import pytest
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo
from bisslog_schema.schema.triggers.trigger_http import TriggerHttp
from bisslog_schema.schema.enums.trigger_type import TriggerEnum


def test_valid_trigger_info_with_http_dict():
    """Test creation of TriggerInfo using HTTP trigger type with options as a dictionary."""
    data = {
        "type": "http",
        "options": {
            "method": "GET",
            "path": "/users"
        }
    }

    trigger_info = TriggerInfo.from_dict(data)

    assert isinstance(trigger_info, TriggerInfo)
    assert trigger_info.type == TriggerEnum.HTTP
    assert isinstance(trigger_info.options, TriggerHttp)
    assert trigger_info.options.method == "GET"
    assert trigger_info.options.path == "/users"


def test_valid_trigger_info_with_trigger_options_instance():
    """Test creation of TriggerInfo using TriggerOptions instance directly."""
    options = TriggerHttp(method="POST", path="/create")
    data = {
        "type": "http",
        "options": options
    }

    trigger_info = TriggerInfo.from_dict(data)

    assert isinstance(trigger_info, TriggerInfo)
    assert trigger_info.options == options
    assert trigger_info.type == TriggerEnum.HTTP


def test_missing_trigger_type_raises_value_error():
    """Test that missing or empty 'type' in input data raises ValueError."""
    data = {
        "type": None,
        "options": {
            "method": "GET"
        }
    }

    with pytest.raises(ValueError, match="The 'type' field is required and must be a string."):
        TriggerInfo.from_dict(data)


def test_invalid_options_type_raises_type_error():
    """Test that a non-dict and non-TriggerOptions 'options' value raises TypeError."""
    data = {
        "type": "http",
        "options": "invalid_options"
    }

    with pytest.raises(TypeError, match="must be a dictionary or an instance of TriggerOptions"):
        TriggerInfo.from_dict(data)


def test_invalid_options_data_raises_value_error():
    """Test that malformed dictionary in 'options' raises ValueError during parsing."""
    data = {
        "type": "http",
        "options": {
            "mapper": {"unknown": "value"}  # This will likely cause .verify_source_prefix to fail
        }
    }

    with pytest.raises(ValueError, match="Error parsing options"):
        TriggerInfo.from_dict(data)
