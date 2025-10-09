from typing import List
from unittest.mock import patch
from bisslog_schema.commands.analyze_metadata_file.analyze_metadata import analyze_command, generate_report, print_and_generate_summary
from bisslog_schema.commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport
import re

errors_string = """ServiceInfo 'unknown' error: The 'name' field is required and must be a non-empty string.
ServiceInfo 'unknown' error: The 'description' field must be a string if provided.
ServiceInfo 'unknown' error: The 'tags' field must be a dictionary if provided.
UseCaseInfo 'addEventAdmitted' error: Pathhttp '(delete) /webhook/event-type/{uid}' is already used.
TriggerHttp 'unknown-0' on use case 'notifyEventFromWebhookDynamicPlatform' error: The 'method' must be a string.
TriggerHttp 'unknown-0' on use case 'notifyEventFromWebhookDynamicPlatform' error: The 'path' field is required and must be a string.
TriggerHttp 'unknown-1' on use case 'notifyEventFromWebhookDynamicPlatform' error: The 'method' must be a string.
TriggerHttp 'unknown-1' on use case 'notifyEventFromWebhookDynamicPlatform' error: The 'path' field is required and must be a string.
TriggerWebsocket 'webhook-receptor' on use case 'notifyEventFromWebhookDynamicPlatform' error: The 'route_key' field is required and must be a string.
TriggerWebsocket 'websocket-test' on use case 'notifyEventFromWebhookDynamicPlatform' error: The 'route_key' field is required and must be a string.
TriggerSchedule 'schedule-test' on use case 'notifyEventFromWebhookDynamicPlatform' error: The 'cronjob' must be a string.
TriggerConsumer 'consumer-test' on use case 'notifyEventFromWebhookDynamicPlatform' error: The 'queue' field is required and must be a string.
TriggerConsumer 'consumer-test' on use case 'notifyEventFromWebhookDynamicPlatform' error: The 'partition' field must be a string if provided.
TriggerConsumer 'consumer-test' on use case 'notifyEventFromWebhookDynamicPlatform' error: Invalid 'delivery_semantic' value. Must be one of: ['at-most-once', 'at-least-once', 'exactly-once'].
TriggerConsumer 'consumer-test' on use case 'notifyEventFromWebhookDynamicPlatform' error: The 'max_retries' field must be greater or equal than 0
ExternalInteraction 'notifyEventFromWebhookDynamicPlatform' error: The 'operation' must be a string or a list of strings.
ExternalInteraction 'notifyEventFromWebhookDynamicPlatform' error: The 'type_interaction' field must be a string if provided.
UseCaseInfo 'delete webhook event type' error: The 'description' field must be a string if provided.
UseCaseInfo 'delete webhook event type' error: The 'entity_type' field must be a string if provided.
UseCaseInfo 'delete webhook event type' error: Invalid external interactions data -> "algorithm"
TriggerHttp 'unknown-0' on use case 'deleteWebhookEventType' error: The 'cacheable' field must be a boolean if provided.
TriggerHttp 'unknown-0' on use case 'deleteWebhookEventType' error: The 'timeout' field must be a integer if provided.
TriggerHttp 'unknown-0' on use case 'getAllWebhookEventType' error: The 'path' field is required and must be a string.
TriggerInfo 'unknown-0' error on use case 'getWebhookEventType': The 'type' must be a string.
UseCaseInfo 'register webhook event type' error: Each external interaction must be a dictionary.
TriggerHttp 'unknown-0' on use case 'registerWebhookEventType' error: The 'path' field is required and must be a string.
TriggerHttp 'unknown-0' on use case 'updateWebhookEventType' error: The 'path' field is required and must be a string.
TriggerHttp 'unknown-0' on use case 'deleteWebhookPlatformReceiver' error: The 'path' field is required and must be a string.
TriggerHttp 'unknown-0' on use case 'getAllWebhookPlatformReceiver' error: The 'path' field is required and must be a string.
UseCaseInfo 'get webhook platform receiver' error: Each external interaction must be a dictionary.
TriggerHttp 'unknown-0' on use case 'getWebhookPlatformReceiver' error: The 'path' field is required and must be a string.
UseCaseInfo 'register webhook platform receiver' error: Each trigger must be a dictionary.
ExternalInteraction 'registerWebhookPlatformReceiver' error: The 'operation' must be a string or a list of strings.
ExternalInteraction 'registerWebhookPlatformReceiver' error: The 'type_interaction' field must be a string if provided.
TriggerHttp 'unknown-0' on use case 'updateWebhookPlatformReceiver' error: The 'path' field is required and must be a string.""".split("\n")


def get_all_errors(self: MetadataAnalysisReport) -> List[str]:
    """Get all errors from the report."""
    errors = []
    if self.errors is not None:
        errors += self.errors
    for sub_reports in self.sub_reports.values():
        for sub_report in sub_reports:
            errors += get_all_errors(sub_report)
    return errors

def get_all_warnings(self: MetadataAnalysisReport) -> List[str]:
    """Get all errors from the report."""
    warnings = []
    if self.warnings is not None:
        warnings += self.warnings
    for sub_reports in self.sub_reports.values():
        for sub_report in sub_reports:
            warnings += get_all_warnings(sub_report)
    return warnings

def test_analyze_metadata():
    """Tests the analyze_metadata function."""

    for error in errors_string:
        assert not re.match(r"takes \d+ positional arguments but \d+ were given", error), "Error in validations analysis"

    metadata_analysis_report = generate_report("examples/webhook-wrong.yml", encoding="utf-8")
    summary = print_and_generate_summary(metadata_analysis_report)

    errors_collected = get_all_errors(metadata_analysis_report)
    warnings_collected = get_all_warnings(metadata_analysis_report)

    assert summary["n_errors"] == 35
    assert len(errors_collected) == summary["n_errors"]
    assert len(errors_string) == summary["n_errors"]
    assert len(warnings_collected) == summary["n_warnings"] == 1
    assert summary["critical_validation_count"]
    for error in errors_string:
        assert error in errors_collected

def test_analyze_metadata2():
    """Tests the analyze_metadata function."""

    with patch("sys.exit") as mock_exit:
        analyze_command("./examples/webhook-wrong.yml", encoding="utf-8")
        mock_exit.assert_called()

    with patch("sys.exit") as mock_exit:

        report = analyze_command("./examples/webhook.yml", min_warnings=10, encoding="utf-8")

        mock_exit.assert_called()
        assert isinstance(report, MetadataAnalysisReport)
        warnings = get_all_warnings(report)
        assert len(warnings) == 2
        assert ("TriggerInfo 'unknown-0' warning on use case "
                "'notifyEventFromWebhookDynamicPlatform': The 'type' field is"
                " missing on trigger.") in warnings
        assert ("TriggerInfo 'unknown-0' warning on use case 'deleteWebhookEventType': "
                "The 'type' field is missing on trigger.") in warnings

