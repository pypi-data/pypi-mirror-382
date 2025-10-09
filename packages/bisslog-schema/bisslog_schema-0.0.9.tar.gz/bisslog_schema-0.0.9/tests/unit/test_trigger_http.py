import pytest
from bisslog_schema.schema.triggers.trigger_http import TriggerHttp


def test_trigger_http_valid_data():
    """Tests the creation of a TriggerHttp instance with valid data."""
    data = {
        "method": "POST",
        "authenticator": "token",
        "path": "/submit",
        "apigw": "api-123",
        "cacheable": True,
        "allow_cors": True,
        "allowed_origins": ["https://example.com"],
        "content_type": "application/json",
        "timeout": 5000,
        "rate_limit": "100r/s",
        "retry_policy": "exponential"
    }
    trigger_http = TriggerHttp.from_dict(data)
    assert trigger_http.method == "POST"
    assert trigger_http.authenticator == "token"
    assert trigger_http.path == "/submit"
    assert trigger_http.apigw == "api-123"
    assert trigger_http.cacheable is True
    assert trigger_http.allow_cors is True
    assert trigger_http.allowed_origins == ["https://example.com"]
    assert trigger_http.content_type == "application/json"
    assert trigger_http.timeout == 5000
    assert trigger_http.rate_limit == "100r/s"
    assert trigger_http.retry_policy == "exponential"


def test_trigger_http_missing_optional_fields():
    """Tests the creation of a TriggerHttp instance with only required fields."""
    data = {"method": "GET"}
    trigger_http = TriggerHttp.from_dict(data)
    assert trigger_http.method == "GET"
    assert trigger_http.authenticator is None
    assert trigger_http.path is None
    assert trigger_http.apigw is None
    assert trigger_http.cacheable is False
    assert trigger_http.allow_cors is False
    assert trigger_http.allowed_origins is None
    assert trigger_http.content_type is None
    assert trigger_http.timeout is None
    assert trigger_http.rate_limit is None
    assert trigger_http.retry_policy is None


def test_trigger_http_invalid_method_type():
    """Tests that an invalid method type raises a TypeError."""
    data = {"method": 123}
    with pytest.raises(TypeError, match="The 'method' must be a string."):
        TriggerHttp.from_dict(data)


def test_trigger_http_invalid_timeout_type():
    """Tests that an invalid timeout type raises a TypeError."""
    data = {"method": "GET", "timeout": "5000"}
    trigger = TriggerHttp.from_dict(data)
    assert trigger.method == "GET"
    assert trigger.timeout == 5000



def test_trigger_http_invalid_rate_limit_format():
    """Tests that an invalid rate_limit format raises a ValueError."""
    data = {"method": "GET", "rate_limit": "invalid_format"}
    with pytest.raises(ValueError, match="Invalid rate_limit format: 'invalid_format'."):
        TriggerHttp.from_dict(data)


def test_trigger_http_invalid_allowed_origins_type():
    """Tests that an invalid allowed_origins type raises a TypeError."""
    data = {"method": "GET", "allowed_origins": "https://example.com"}
    trigger = TriggerHttp.from_dict(data)
    assert trigger.method == "GET"
    assert trigger.allowed_origins == ["https://example.com"]


def test_trigger_http_empty_data():
    """Tests that missing required fields raises a TypeError."""
    data = {}
    trigger = TriggerHttp.from_dict(data)
    assert trigger.method == "GET"
