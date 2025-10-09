import pytest
from bisslog_schema.schema.triggers.trigger_schedule import TriggerSchedule


def test_trigger_schedule_valid_data():
    """Tests the creation of a TriggerSchedule instance with valid data."""
    data = {
        "cronjob": "0 0 * * *",
        "event": {"key": "value"},
        "timezone": "UTC",
        "description": "Daily job",
        "retry_policy": "exponential",
        "max_attempts": 5
    }
    schedule = TriggerSchedule.from_dict(data)
    assert schedule.cronjob == "0 0 * * *"
    assert schedule.event == {"key": "value"}
    assert schedule.timezone == "UTC"
    assert schedule.description == "Daily job"
    assert schedule.retry_policy == "exponential"
    assert schedule.max_attempts == 5


def test_trigger_schedule_missing_cronjob():
    """Tests that a missing 'cronjob' field raises a ValueError."""
    data = {}
    with pytest.raises(ValueError, match="The 'cronjob' field is required and must be a string."):
        TriggerSchedule.from_dict(data)


def test_trigger_schedule_invalid_cronjob():
    """Tests that an invalid 'cronjob' value raises a ValueError."""
    data = {"cronjob": 123}
    with pytest.raises(TypeError, match="The 'cronjob' must be a string."):
        TriggerSchedule.from_dict(data)


def test_trigger_schedule_invalid_timezone():
    """Tests that an invalid 'timezone' value raises a ValueError."""
    data = {"cronjob": "0 0 * * *", "timezone": 123}
    with pytest.raises(ValueError, match="The 'timezone' field must be a string if provided."):
        TriggerSchedule.from_dict(data)


def test_trigger_schedule_invalid_description():
    """Tests that an invalid 'description' value raises a ValueError."""
    data = {"cronjob": "0 0 * * *", "description": 123}
    with pytest.raises(ValueError, match="The 'description' field must be a string if provided."):
        TriggerSchedule.from_dict(data)


def test_trigger_schedule_invalid_retry_policy():
    """Tests that an invalid 'retry_policy' value raises a ValueError."""
    data = {"cronjob": "0 0 * * *", "retry_policy": 123}
    with pytest.raises(ValueError, match="The 'retry_policy' field must be a string if provided."):
        TriggerSchedule.from_dict(data)


def test_trigger_schedule_invalid_max_attempts():
    """Tests that a negative 'max_attempts' value raises a ValueError."""
    data = {"cronjob": "0 0 * * *", "max_attempts": -1}
    with pytest.raises(ValueError, match="The 'max_attempts' field must be greater or equal than 0"):
        TriggerSchedule.from_dict(data)

@pytest.mark.parametrize("input_tz,expected", [
    ("UTC", "Etc/UTC"),
    ("utc", "Etc/UTC"),
    ("GMT", "Etc/GMT"),
    ("GMT+0", "Etc/GMT"),
    ("GMT+3", "Etc/GMT-3"),
    ("GMT-2", "Etc/GMT+2"),
    ("America/Bogota", "America/Bogota")
])
def test_normalize_timezone_valid_cases(input_tz, expected):
    """Tests that various timezone aliases normalize to expected IANA values."""
    normalized = TriggerSchedule.normalize_timezone(input_tz)
    assert normalized == expected


def test_validate_tz_on_standard_with_valid_iana():
    """Tests that a valid IANA timezone like 'America/Bogota' passes validation."""
    tz = "America/Bogota"
    result = TriggerSchedule.validate_tz_on_standard(tz)
    assert result == tz


