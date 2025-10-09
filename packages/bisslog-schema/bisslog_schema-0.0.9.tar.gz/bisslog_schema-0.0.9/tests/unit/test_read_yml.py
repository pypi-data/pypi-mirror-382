from unittest.mock import patch

import pytest

from bisslog_schema.schema.enums.criticality import CriticalityEnum
from bisslog_schema.schema.read_metadata import read_service_metadata

def test_read_yml_webhook_example():
    service_data = read_service_metadata("examples/webhook.yml")
    assert service_data.type == "microservice"
    assert service_data.name == "webhook receiver"
    assert service_data.team == "code-infrastructure"

    mapper1 = service_data.use_cases["notifyEventFromWebhookDynamicPlatform"].triggers[0].options.mapper
    assert mapper1 is None

    mapper2 = service_data.use_cases["addEventAdmitted"].triggers[0].options.mapper
    assert mapper2 is not None and isinstance(mapper2, dict) and len(mapper2) == 3

    assert service_data.use_cases["getWebhookEventType"].criticality == CriticalityEnum.VERY_HIGH


def test_read_yml_not_found_defined_path():

    with pytest.raises(ValueError, match=r"Path .+ of metadata does not exist"):
        read_service_metadata("./algo.yml")


def test_read_yml_not_found_non_defined_path():

    with pytest.raises(ValueError, match="No compatible default path could be found"):
        read_service_metadata()


@pytest.mark.parametrize("path_option", ["examples/webhook.yml"])
def test_read_service_metadata(path_option):
    service_data = read_service_metadata("examples/webhook.yml")

    assert service_data.type == "microservice"
    assert service_data.name == "webhook receiver"
    assert service_data.team == "code-infrastructure"

    assert service_data.use_cases["getWebhookEventType"].criticality == CriticalityEnum.VERY_HIGH



def test_yaml_import_error_handling(capsys):
    """Test YAML import error handling with full message verification.

    Verifies
    --------
    - Correct error message is displayed
    - Installation instructions are included
    - Error is properly propagated
    """
    with patch('importlib.import_module') as mock_import:
        mock_import.side_effect = ImportError("No module named 'yaml'")

        with pytest.raises(ImportError):
            read_service_metadata("examples/webhook.yml")

        captured = capsys.readouterr()
        assert "Please install PyYAML" in captured.err
        assert "pip install bisslog_schema[yaml]" in captured.err
        assert "pip install pyyaml" in captured.err
