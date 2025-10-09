import pytest

from bisslog_schema.schema.enums.event_delivery_semantic import EventDeliverySemantic
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo
from bisslog_schema.schema.triggers.trigger_http import TriggerHttp
from bisslog_schema.schema.triggers.trigger_websocket import TriggerWebsocket
from bisslog_schema.schema.triggers.trigger_consumer import TriggerConsumer
from bisslog_schema.schema.triggers.trigger_schedule import TriggerSchedule
from bisslog_schema.schema.enums.trigger_type import TriggerEnum


def test_trigger_http_from_dict():
    data = {"method": "GET", "authenticator": None, "path": "/test", "apigw": "my-api"}
    trigger_http = TriggerHttp.from_dict(data)
    assert trigger_http.method == "GET"
    assert trigger_http.authenticator is None
    assert trigger_http.path == "/test"
    assert trigger_http.apigw == "my-api"

def test_trigger_websocket_from_dict():
    data = {"routeKey": "sendMessage"}
    trigger_ws = TriggerWebsocket.from_dict(data)
    assert trigger_ws.route_key == "sendMessage"

def test_trigger_consumer_from_dict():
    data = {"queue": "my-queue", "partition": "0"}
    trigger_consumer = TriggerConsumer.from_dict(data)
    assert trigger_consumer.queue == "my-queue"
    assert trigger_consumer.partition == "0"
    assert trigger_consumer.delivery_semantic == EventDeliverySemantic.AT_LEAST_ONCE

def test_trigger_schedule_from_dict():
    data = {"cronjob": "0 12 * * *"}
    trigger_schedule = TriggerSchedule.from_dict(data)
    assert trigger_schedule.cronjob == "0 12 * * *"

def test_trigger_enum_from_str_valid():
    assert TriggerEnum.from_str("http") == TriggerEnum.HTTP
    assert TriggerEnum.from_str("websocket") == TriggerEnum.WEBSOCKET
    assert TriggerEnum.from_str("consumer") == TriggerEnum.CONSUMER
    assert TriggerEnum.from_str("schedule") == TriggerEnum.SCHEDULE

def test_trigger_enum_from_str_invalid():
    assert TriggerEnum.from_str("invalid") is None

def test_trigger_from_dict_http():
    data = {
        "type": "http",
        "options": {
            "method": "POST",
            "authenticator": "token",
            "path": "/submit",
            "apigw": "api-123"
        }
    }
    trigger = TriggerInfo.from_dict(data.copy())
    assert trigger.type == TriggerEnum.HTTP
    assert isinstance(trigger.options, TriggerHttp)
    assert trigger.options.method == "POST"
    assert trigger.options.authenticator == "token"
    assert trigger.options.path == "/submit"
    assert trigger.options.apigw == "api-123"

def test_trigger_from_dict_missing_type_defaults_to_http():
    data = {
        "method": "GET",
        "authenticator": "none",
        "path": "/",
        "apigw": "api"
    }
    trigger = TriggerInfo.from_dict({"options": data})
    assert trigger.type == TriggerEnum.HTTP
    assert isinstance(trigger.options, TriggerHttp)

def test_trigger_from_dict_customized_type():
    data = {"type": "customized", "foo": "bar"}
    trigger_info = TriggerInfo.from_dict(data.copy())
    assert trigger_info.type == "customized", "Invalid trigger type should not be set"
    assert isinstance(trigger_info.options, dict)
    assert trigger_info.options == {}
    data = {"type": "customized", "foo": "bar", "options": {"bar": "baz"}}
    trigger_info = TriggerInfo.from_dict(data.copy())
    assert trigger_info.type == "customized", "Invalid trigger type should not be set"
    assert isinstance(trigger_info.options, dict)
    assert trigger_info.options == {"bar": "baz"}


def test_trigger_from_dict_null():
    data = {
        "type": None,
    }
    with pytest.raises(ValueError, match="The 'type' field is required and must be a string."):
        TriggerInfo.from_dict(data.copy())

