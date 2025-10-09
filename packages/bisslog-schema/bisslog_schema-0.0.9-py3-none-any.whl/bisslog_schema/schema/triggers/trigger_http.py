"""Module defining trigger http configuration"""
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union

from .trigger_mappable import TriggerMappable
from .trigger_options import TriggerOptions
from ...commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport

expected_keys = ("path_query", "body", "params", "headers", "context")


@dataclass
class TriggerHttp(TriggerOptions, TriggerMappable):
    """Options for configuring an HTTP trigger.

    Attributes
    ----------
    method : str, optional
        The HTTP method (e.g., GET, POST).
    authenticator : str, optional
        The authentication mechanism associated with the trigger.
    path : str, optional
        The API route path.
    apigw : str, optional
        API Gateway identifier if applicable.
    cacheable : bool
        Indicates whether the route can be cached. Defaults to False.
    allow_cors : bool
        If True, enables CORS headers. Defaults to False.
    allowed_origins : list of str, optional
        List of allowed origins for CORS, if applicable.
    content_type : str, optional
        Expected content type for requests (e.g., application/json).
    timeout : int, optional
        Timeout for the request in milliseconds.
    rate_limit : str or int, optional
        Throttling configuration (e.g., "100r/s" or 100).
    retry_policy : str, optional
        Description or identifier for a retry policy (e.g., "exponential", "none").
    """
    method: Optional[str] = None
    authenticator: Optional[str] = None
    path: Optional[str] = None
    apigw: Optional[str] = None
    cacheable: bool = False

    allow_cors: bool = False
    allowed_origins: Optional[List[str]] = None

    content_type: Optional[str] = None

    timeout: Optional[int] = None # ms
    rate_limit: Optional[Union[str, int]] = None
    retry_policy: Optional[str] = None

    @classmethod
    def analyze(cls, data: Dict[str, Any], trigger_keyname: str,
                use_case_name: str) -> MetadataAnalysisReport:
        """
        Analyze the trigger HTTP options.

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
            (cls._validate_required_str_field, "method", data.get("method")),
            (cls._validate_optional_str_field, "authenticator", data.get("authenticator")),
            (cls._validate_required_str_field, "path", data.get("path")),
            (cls._validate_optional_str_field, "apigw", data.get("apigw")),
            (cls._validate_boolean_field, "cacheable", data.get("cacheable")),
            (cls._validate_boolean_field, "allow_cors", data.get("allow_cors")),
            (cls._validate_allowed_origins, data.get("allowed_origins")),
            (cls._validate_optional_str_field, "content_type", data.get("content_type")),
            (cls._validate_optional_int_field, "timeout", data.get("timeout"), 0),
            (cls._validate_rate_limit, data.get("rate_limit")),
            (cls._validate_optional_str_field, "retry_policy", data.get("retry_policy")),
        ]

        errors = cls._run_validations(trigger_keyname, use_case_name, validations)
        report.critical_validation_count += len(validations)
        report.errors.extend(errors)
        return report

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TriggerHttp":
        """
        Deserialize a dictionary into a TriggerHttp instance.

        Parameters
        ----------
        data : dict
            Dictionary containing the trigger options.

        Returns
        -------
        TriggerHttp
            An instance of TriggerHttp.
        """
        mapper = cls.verify_source_prefix(data.get("mapper"), expected_keys)
        return cls(
            method=cls._validate_required_str_field(
                "method", data.get("method", "GET")).upper(),
            authenticator=data.get("authenticator"),
            path=cls._validate_optional_str_field("path", data.get("path")),
            apigw=cls._validate_optional_str_field("apigw", data.get("apigw")),
            cacheable=cls._validate_boolean_field("cacheable", data.get("cacheable")),
            allow_cors=cls._validate_boolean_field("allow_cors", data.get("allow_cors")),
            allowed_origins=cls._validate_allowed_origins(data.get("allowed_origins")),
            content_type=data.get("content_type"),
            timeout=cls._validate_optional_int_field("timeout", data.get("timeout"), lower_limit=0),
            rate_limit=cls._validate_rate_limit(data.get("rate_limit")),
            retry_policy=cls._validate_optional_str_field("retry_policy", data.get("retry_policy")),
            mapper=mapper,
        )
    @staticmethod
    def _validate_allowed_origins(allowed_origins: Optional[Any]) -> Optional[List[str]]:
        if allowed_origins is None:
            return allowed_origins

        if isinstance(allowed_origins, str):
            return [origin.strip() for origin in allowed_origins.split(",")]

        if (not isinstance(allowed_origins, list) or
                not all(isinstance(item, str) for item in allowed_origins)):
            raise TypeError("The 'allowed_origins' field must be a list of strings.")

        return allowed_origins

    @staticmethod
    def _validate_rate_limit(rate_limit: Any) -> Optional[Union[str, int]]:
        """Validates the rate_limit field."""
        if rate_limit is None:
            return None
        if isinstance(rate_limit, str):
            if not re.fullmatch(r"\d+r/[sm]", rate_limit):
                raise ValueError(
                    f"Invalid rate_limit format: '{rate_limit}'. "
                    "Use formats like '100r/s' or '200r/m'."
                )
        elif not isinstance(rate_limit, int):
            raise TypeError("The 'rate_limit' field must be a string or an integer.")
        return rate_limit
