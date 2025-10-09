import pytest
from bisslog_schema.schema.external_interaction import ExternalInteraction


def test_external_interaction_valid_data():
    """Test creating an ExternalInteraction instance with valid data."""
    data = {
        "keyname": "marketing_division",
        "type_interaction": "database",
        "operation": "get_last_sales_from_client",
        "description": "Fetches sales data from the client database."
    }
    instance = ExternalInteraction.from_dict(data)
    assert instance.keyname == "marketing_division"
    assert instance.type_interaction == "database"
    assert instance.operation == "get_last_sales_from_client"
    assert instance.description == "Fetches sales data from the client database."


def test_external_interaction_missing_keyname():
    """Test that missing 'keyname' raises a ValueError."""
    data = {
        "type_interaction": "database",
        "operation": "get_last_sales_from_client"
    }
    with pytest.raises(ValueError, match="The 'keyname' field is required."):
        ExternalInteraction.from_dict(data)


def test_external_interaction_invalid_keyname_type():
    """Test that an invalid 'keyname' type raises a TypeError."""
    data = {
        "keyname": 123,
        "type_interaction": "database",
        "operation": "get_last_sales_from_client"
    }
    with pytest.raises(TypeError, match="The 'keyname' must be a string."):
        ExternalInteraction.from_dict(data)


def test_external_interaction_invalid_operation_type():
    """Test that an invalid 'operation' type raises a TypeError."""
    data = {
        "keyname": "marketing_division",
        "type_interaction": "database",
        "operation": 12345
    }
    with pytest.raises(TypeError, match="The 'operation' must be a string or a list of strings."):
        ExternalInteraction.from_dict(data)



def test_external_interaction_with_list_operations():
    """Test creating an ExternalInteraction instance with a list of operations."""
    data = {
        "keyname": "marketing_division",
        "type_interaction": "database",
        "operation": ["get_sales", "update_sales"],
        "description": "Handles multiple operations."
    }
    instance = ExternalInteraction.from_dict(data)
    assert instance.operation == ["get_sales", "update_sales"]