import pytest
from bisslog_schema.schema.triggers.trigger_consumer import TriggerConsumer
from bisslog_schema.schema.enums.event_delivery_semantic import EventDeliverySemantic


def test_trigger_consumer_valid_data():
    """Tests the creation of a TriggerConsumer instance with valid data."""
    data = {
        "queue": "test-queue",
        "partition": "partition-1",
        "delivery_semantic": "at-least-once",
        "max_retries": 3,
        "retry_delay": 1000,
        "dead_letter_queue": "dlq-queue",
        "batch_size": 10
    }
    consumer = TriggerConsumer.from_dict(data)
    assert consumer.queue == "test-queue"
    assert consumer.partition == "partition-1"
    assert consumer.delivery_semantic == EventDeliverySemantic.AT_LEAST_ONCE
    assert consumer.max_retries == 3
    assert consumer.retry_delay == 1000
    assert consumer.dead_letter_queue == "dlq-queue"
    assert consumer.batch_size == 10


def test_trigger_consumer_invalid_queue():
    """Tests that an invalid 'queue' value raises a ValueError."""
    data = {"queue": 123}
    with pytest.raises(TypeError, match="The 'queue' must be a string."):
        TriggerConsumer.from_dict(data)


def test_trigger_consumer_invalid_max_retries():
    """Tests that a negative 'max_retries' value raises a ValueError."""
    data = {"max_retries": -1, "queue": "test-queue"}
    with pytest.raises(ValueError, match="The 'max_retries' field must be greater or equal than 0"):
        TriggerConsumer.from_dict(data)


def test_trigger_consumer_invalid_retry_delay():
    """Tests that a negative 'retry_delay' value raises a ValueError."""
    data = {"retry_delay": -100, "queue": "test-queue"}
    with pytest.raises(ValueError, match="The 'retry_delay' field must be greater or equal than 0"):
        TriggerConsumer.from_dict(data)


def test_trigger_consumer_invalid_batch_size():
    """Tests that a negative 'batch_size' value raises a ValueError."""
    data = {"batch_size": -5, "queue": "test-queue"}
    with pytest.raises(ValueError, match="The 'batch_size' field must be greater or equal than 0"):
        TriggerConsumer.from_dict(data)


def test_trigger_consumer_invalid_dead_letter_queue():
    """Tests that an invalid 'dead_letter_queue' value raises a ValueError."""
    data = {"dead_letter_queue": 123, "queue": "test-queue"}
    with pytest.raises(ValueError, match="The 'dead_letter_queue' field must be a string if provided."):
        TriggerConsumer.from_dict(data)
