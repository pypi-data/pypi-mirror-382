import pytest
from bisslog_schema.schema.use_case_info import UseCaseInfo
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo
from bisslog_schema.schema.external_interaction import ExternalInteraction
from bisslog_schema.schema.enums.criticality import CriticalityEnum


def test_use_case_info_valid_data():
    """Tests the creation of a UseCaseInfo instance with valid data."""
    data = {
        "keyname": "CreateOrder",
        "name": "CreateOrder",
        "description": "Handles order creation",
        "tags": {"priority": "high"},
        "triggers": [{"type": "http", "options": {"method": "POST"}}],
        "criticality": "HIGH",
        "actor": "Customer",
        "external_interactions": [{"type": "db", "keyname": "orders", "operation": "save_order",
                                   "description": "Saves order to DB", }]
    }
    instance = UseCaseInfo.from_dict(data)
    assert instance.name == "CreateOrder"
    assert instance.description == "Handles order creation"
    assert instance.tags == {"priority": "high"}
    assert len(instance.triggers) == 1
    assert isinstance(instance.triggers[0], TriggerInfo)
    assert instance.criticality == CriticalityEnum.HIGH
    assert instance.actor == "Customer"
    assert len(instance.external_interactions) == 1
    assert isinstance(instance.external_interactions[0], ExternalInteraction)


def test_use_case_info_missing_name():
    """Tests that a missing 'name' field raises a ValueError."""
    data = {
        "description": "Handles order creation",
        "keyname": "CreateOrder",
        "tags": {"priority": "high"}
    }
    with pytest.raises(ValueError, match="The 'name' field is required and must be a string."):
        UseCaseInfo.from_dict(data)


def test_use_case_info_invalid_criticality():
    """Tests that an invalid 'criticality' value raises a ValueError."""
    data = {
        "keyname": "CreateOrder",
        "name": "CreateOrder",
        "criticality": "INVALID"
    }
    with pytest.raises(ValueError, match="Invalid criticality value: INVALID"):
        UseCaseInfo.from_dict(data)


def test_use_case_info_invalid_triggers():
    """Tests that an invalid 'triggers' field raises a ValueError."""
    data = {
        "keyname": "CreateOrder",
        "name": "CreateOrder",
        "triggers": "invalid_triggers"
    }
    with pytest.raises(ValueError, match="The 'triggers' field must be a list."):
        UseCaseInfo.from_dict(data)


def test_use_case_info_invalid_external_interactions():
    """Tests that an invalid 'external_interactions' field raises a ValueError."""
    data = {
        "keyname": "CreateOrder",
        "name": "CreateOrder",
        "external_interactions": "invalid_interactions"
    }
    with pytest.raises(ValueError, match="Invalid external interactions data ->"):
        UseCaseInfo.from_dict(data)


def test_use_case_info_trigger_creation_error():
    """Tests that an error during TriggerInfo creation raises a ValueError."""
    data = {
        "keyname": "CreateOrder",
        "name": "CreateOrder",
        "triggers": [{"type": None}]
    }
    with pytest.raises(ValueError, match="The 'type' field is required."):
        UseCaseInfo.from_dict(data)


def test_use_case_info_external_interaction_creation_error():
    """Tests that an error during ExternalInteraction creation raises a ValueError."""
    data = {
        "keyname": "CreateOrder",
        "name": "CreateOrder",
        "external_interactions": [{"type": "invalid_type"}]
    }
    with pytest.raises(ValueError, match="Error processing an external interaction ->"):
        UseCaseInfo.from_dict(data)
