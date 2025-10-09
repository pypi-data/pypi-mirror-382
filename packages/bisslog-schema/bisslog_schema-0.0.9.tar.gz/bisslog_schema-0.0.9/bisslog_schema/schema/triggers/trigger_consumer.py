"""Module defining trigger consumer configuration class"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .trigger_mappable import TriggerMappable
from .trigger_options import TriggerOptions
from ...schema.enums.event_delivery_semantic import EventDeliverySemantic
from ...commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport

expected_keys = ("event", "context")


@dataclass
class TriggerConsumer(TriggerOptions, TriggerMappable):
    """Options for configuring a consumer trigger (e.g., queue consumer).

    Attributes
    ----------
    queue : str, optional
        The name of the queue.
    partition : str, optional
        The partition key if applicable.
    delivery_semantic : EventDeliverySemantic
        The delivery semantic for the trigger.
    max_retries : int, optional
        Maximum number of retries.
    retry_delay : int, optional
        Delay between retries in seconds.
    dead_letter_queue : str, optional
        The name of the dead letter queue.
    batch_size : int, optional
        The size of the batch for processing messages.
    """
    queue: str = None
    partition: Optional[str] = None
    delivery_semantic: EventDeliverySemantic = EventDeliverySemantic.AT_LEAST_ONCE
    max_retries: Optional[int] = None
    retry_delay: Optional[int] = None
    dead_letter_queue: Optional[str] = None
    batch_size: Optional[int] = None

    @staticmethod
    def _validate_delivery_semantic(delivery_semantic: Any) -> EventDeliverySemantic:
        """
        Validate the `delivery_semantic` field.

        Parameters
        ----------
        delivery_semantic : EventDeliverySemantic
            The delivery semantic value to validate.

        Returns
        -------
        EventDeliverySemantic
            The validated delivery semantic value.
        """
        if delivery_semantic is None:
            return EventDeliverySemantic.AT_LEAST_ONCE
        if isinstance(delivery_semantic, str):
            semantic = EventDeliverySemantic.from_value(delivery_semantic)
            if semantic is None:
                valid_values = [e.value for e in EventDeliverySemantic]
                raise ValueError(
                    f"Invalid 'delivery_semantic' value. Must be one of: {valid_values}."
                )
            return semantic

        if isinstance(delivery_semantic, EventDeliverySemantic):
            return delivery_semantic

        raise TypeError("The 'delivery_semantic' field must be a string"
                        " or an instance of EventDeliverySemantic.")

    @classmethod
    def analyze(cls, data: Dict[str, Any], trigger_keyname: str,
                use_case_name: str)  -> MetadataAnalysisReport:
        """Analyze the trigger consumer options.

        Parameters
        ----------
        data : dict
            Dictionary containing the trigger options.
        use_case_name : str
            The name of the use case for which the trigger options are being analyzed.
        trigger_keyname
            The key name of the trigger in the use case configuration.

        Returns
        -------
        MetadataAnalysisReport
            A report indicating whether the trigger consumer options are valid or not.
        """
        report = cls.analyze_source_prefix(data.get("mapper"), expected_keys)

        validations = [
            (cls._validate_required_str_field, "queue", data.get("queue")),
            (cls._validate_optional_str_field, "partition", data.get("partition")),
            (cls._validate_delivery_semantic, data.get("delivery_semantic")),
            (cls._validate_optional_int_field, "max_retries", data.get("max_retries"), 0),
            (cls._validate_optional_int_field, "retry_delay", data.get("retry_delay"), 0),
            (cls._validate_optional_str_field, "dead_letter_queue", data.get("dead_letter_queue")),
            (cls._validate_optional_int_field, "batch_size", data.get("batch_size"), 0),
        ]
        errors = cls._run_validations(
            trigger_keyname, use_case_name, validations)
        report.critical_validation_count += len(validations)
        report.errors += errors
        return report

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TriggerConsumer":
        """Deserialize a dictionary into a TriggerConsumer instance.

        Parameters
        ----------
        data : dict
            Dictionary containing the trigger options.

        Returns
        -------
        TriggerConsumer
            An instance of a subclass implementing TriggerConsumer."""

        mapper: Optional[Dict[str, str]] = data.get("mapper")
        cls.verify_source_prefix(mapper, expected_keys)

        return cls(
            queue=cls._validate_required_str_field("queue", data.get("queue")),
            partition=cls._validate_optional_str_field("partition", data.get("partition")),
            delivery_semantic=cls._validate_delivery_semantic(data.get("delivery_semantic")),
            max_retries=cls._validate_optional_int_field("max_retries", data.get("max_retries"), 0),
            retry_delay=cls._validate_optional_int_field("retry_delay", data.get("retry_delay"), 0),
            dead_letter_queue=cls._validate_optional_str_field(
                "dead_letter_queue", data.get("dead_letter_queue")),
            batch_size=cls._validate_optional_int_field("batch_size", data.get("batch_size"), 0),
            mapper=mapper,
        )
