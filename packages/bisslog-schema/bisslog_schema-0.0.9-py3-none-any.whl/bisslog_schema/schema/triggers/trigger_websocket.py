"""Module defining trigger websocket configuration class."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

from .trigger_mappable import TriggerMappable
from .trigger_options import TriggerOptions
from ...commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport

expected_keys = ("connection_id", "route_key", "body", "headers")


@dataclass
class TriggerWebsocket(TriggerOptions, TriggerMappable):
    """Options for configuring a WebSocket trigger.

    Attributes
    ----------
    route_key : str, optional
        The route key associated with the WebSocket connection."""
    route_key: Optional[str] = None

    @classmethod
    def analyze(cls, data: Dict[str, Any], trigger_keyname: str,
                use_case_name: str) ->  MetadataAnalysisReport:
        """
        Analyze the trigger WebSocket options.

        Parameters
        ----------
        data : dict
            Dictionary containing the trigger options.
        trigger_keyname : str
            The key name of the trigger in the use case configuration.
        use_case_name : str
            The name of the use case for which the trigger options are being analyzed.

        Returns
        -------
        MetadataAnalysisReport
            A report indicating whether the trigger HTTP options are valid or not.
        """
        report = cls.analyze_source_prefix(data.get("mapper"), expected_keys)

        validations = [
            (cls._validate_required_str_field, "route_key", data.get("routeKey")),
        ]
        errors = cls._run_validations(trigger_keyname, use_case_name, validations)
        report.critical_validation_count += len(validations)
        report.errors += errors
        return report


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TriggerWebsocket":
        """Deserialize a dictionary into a TriggerWebsocket instance.

        Parameters
        ----------
        data : dict
            Dictionary containing the trigger options.

        Returns
        -------
        TriggerWebsocket
            An instance of a subclass implementing TriggerWebsocket."""
        mapper: Optional[Dict[str, str]] = data.get("mapper")
        cls.verify_source_prefix(mapper, expected_keys)
        route_key = cls._validate_required_str_field(
            "route_key", data.get("routeKey") or data.get("route_key"))
        return cls(route_key=route_key, mapper=mapper)
