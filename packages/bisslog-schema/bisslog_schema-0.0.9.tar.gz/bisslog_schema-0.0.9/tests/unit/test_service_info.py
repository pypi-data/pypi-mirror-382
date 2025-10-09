import pytest
from bisslog_schema.schema.service_info import ServiceInfo
from bisslog_schema.schema.use_case_info import UseCaseInfo


def test_service_info_valid_data():
    """Tests the creation of a ServiceInfo instance with valid data."""
    data = {
        "name": "OrderService",
        "description": "Handles order processing",
        "type": "API",
        "tags": {"domain": "ecommerce"},
        "service_type": "REST",
        "team": "Order Team",
        "use_cases": {
            "create_order": {
                "name": "Create Order",
                "description": "Handles order creation",
                "tags": {"priority": "high"}
            }
        }
    }
    instance = ServiceInfo.from_dict(data)
    assert instance.name == "OrderService"
    assert instance.description == "Handles order processing"
    assert instance.type == "API"
    assert instance.tags == {"domain": "ecommerce"}
    assert instance.service_type == "REST"
    assert instance.team == "Order Team"
    assert "create_order" in instance.use_cases
    assert isinstance(instance.use_cases["create_order"], UseCaseInfo)


def test_service_info_missing_name():
    """Tests that missing the 'name' field raises a ValueError."""
    data = {
        "description": "Handles order processing",
        "tags": {"domain": "ecommerce"}
    }
    with pytest.raises(ValueError, match="The 'name' field is required and must be a string."):
        ServiceInfo.from_dict(data)


def test_service_info_invalid_tags():
    """Tests that an invalid 'tags' field raises a ValueError."""
    data = {
        "name": "OrderService",
        "tags": "invalid_tags"
    }
    with pytest.raises(ValueError, match="The 'tags' field must be a dictionary."):
        ServiceInfo.from_dict(data)


def test_service_info_invalid_use_cases():
    """Tests that an invalid 'use_cases' field raises a ValueError."""
    data = {
        "name": "OrderService",
        "use_cases": "invalid_use_cases"
    }
    with pytest.raises(ValueError, match="The 'use_cases' field must be a dictionary."):
        ServiceInfo.from_dict(data)


def test_service_info_invalid_use_case_data():
    """Tests that invalid use case data raises a ValueError."""
    data = {
        "name": "OrderService",
        "use_cases": {
            "create_order": "invalid_data"
        }
    }
    with pytest.raises(ValueError, match="Use case data for 'create_order' must be a dictionary."):
        ServiceInfo.from_dict(data)


def test_service_info_use_case_creation_error():
    """Tests that an error when creating a UseCaseInfo raises a ValueError."""
    data = {
        "name": "OrderService",
        "use_cases": {
            "create_order": {
                "name": 123  # Invalid value for the name
            }
        }
    }
    with pytest.raises(ValueError, match="Error creating UseCaseInfo for 'create_order': The 'name' must be a string."):
        ServiceInfo.from_dict(data)
