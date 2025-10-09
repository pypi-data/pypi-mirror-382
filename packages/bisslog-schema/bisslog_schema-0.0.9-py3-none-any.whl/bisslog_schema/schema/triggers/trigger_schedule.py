"""Module defining trigger schedule configuration class"""
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any

from ...commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport

try:
    from zoneinfo import available_timezones

    _ZONE_INFO_AVAILABLE = True
except ImportError:
    try:
        from backports.zoneinfo import available_timezones

        _ZONE_INFO_AVAILABLE = True
    except ImportError:
        available_timezones = None
        _ZONE_INFO_AVAILABLE = False

from .trigger_options import TriggerOptions


@dataclass
class TriggerSchedule(TriggerOptions):
    """
    Options for configuring a scheduled (cron) trigger.

    Attributes
    ----------
    cronjob : str
        Cron expression specifying the schedule.
    event : Any, optional
        Event data associated with the trigger.
    timezone : str, optional
        Timezone for the schedule.
    description : str, optional
        Description of the trigger.
    retry_policy : str, optional
        Retry policy for the trigger.
    max_attempts : int, optional
        Maximum number of retry attempts.
    """
    cronjob: str
    event: Optional[Any] = None
    timezone: Optional[str] = None
    description: Optional[str] = None
    retry_policy: Optional[str] = None
    max_attempts: Optional[int] = None

    @classmethod
    def validate_timezone(cls, timezone: Any) -> str:
        """
        Validate the `timezone` field.

        Parameters
        ----------
        timezone : Any
            The timezone value to validate.

        Returns
        -------
        str
            The validated timezone value.

        Raises
        ------
        ValueError
            If the timezone is not a valid string or not recognized.
        """
        if timezone is not None:
            if not isinstance(timezone, str):
                raise ValueError("The 'timezone' field must be a string if provided.")
            cls.validate_tz_on_standard(timezone)
        return timezone

    @staticmethod
    def normalize_timezone(tz: str) -> str:
        """
        Normalize a timezone string, including aliases like 'UTC', 'GMT+5', etc.

        Parameters
        ----------
        tz : str
            Input timezone string.

        Returns
        -------
        str
            Normalized timezone string compatible with IANA.

        Raises
        ------
        ValueError
            If the timezone is invalid or cannot be normalized.
        """
        tz = tz.strip()
        if tz.upper() == "UTC":
            return "Etc/UTC"
        if tz.upper() == "GMT" or tz.upper() == "GMT+0":
            return "Etc/GMT"

        gmt_match = re.fullmatch(r"GMT([+-])(\d{1,2})", tz.upper())
        if gmt_match:
            sign, hours = gmt_match.groups()
            inverted_sign = "-" if sign == "+" else "+"
            return f"Etc/GMT{inverted_sign}{hours}"
        return tz

    @classmethod
    def validate_tz_on_standard(cls, timezone: str) -> str:
        """
        Check if the timezone is valid.

        Parameters
        ----------
        timezone : str
            The timezone value to validate.

        Returns
        -------
        str
            The validated timezone value.

        Raises
        ------
        ValueError
            If the timezone is not recognized.
        """
        tz_normalized = cls.normalize_timezone(timezone)
        if _ZONE_INFO_AVAILABLE and tz_normalized not in available_timezones():
            raise ValueError(f"Invalid timezone string: {timezone}")
        return timezone

    @classmethod
    def analyze(cls, data: Dict[str, Any], trigger_keyname: str,
                use_case_name: str) -> MetadataAnalysisReport:
        """
        Analyze the trigger Schedule options.

        Parameters
        ----------
        data : dict
            Dictionary containing the trigger options.
        trigger_keyname : str
            The key name of the trigger in the use case configuration.
        use_case_name
            The name of the use case for which the trigger options are being analyzed.

        Returns
        -------
        MetadataAnalysisReport
            Analysis report for the trigger schedule.
        """
        validations = [
            (cls._validate_required_str_field, "cronjob", data.get("cronjob")),
            (cls.validate_timezone, data.get("timezone")),
            (cls._validate_optional_str_field, "description", data.get("description")),
            (cls._validate_optional_str_field, "retry_policy", data.get("retry_policy")),
            (cls._validate_optional_int_field, "max_attempts", data.get("max_attempts"), 0),
        ]

        errors = cls._run_validations(trigger_keyname, use_case_name, validations)

        return MetadataAnalysisReport(len(validations), 0, errors, [], {})

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TriggerSchedule":
        """Deserialize a dictionary into a TriggerSchedule instance.

        Parameters
        ----------
        data : dict
            Dictionary containing the trigger options.

        Returns
        -------
        TriggerSchedule
            An instance of TriggerSchedule.

        Raises
        ------
        ValueError
            If any field fails validation."""
        cronjob = cls._validate_required_str_field("cronjob", data.get("cronjob"))
        timezone = cls.validate_timezone(data.get("timezone"))
        description = cls._validate_optional_str_field("description", data.get("description"))
        retry_policy = cls._validate_optional_str_field("retry_policy", data.get("retry_policy"))
        max_attempts = cls._validate_optional_int_field("max_attempts", data.get("max_attempts"), 0)

        return cls(cronjob=cronjob, event=data.get("event"), timezone=timezone,
                   description=description, retry_policy=retry_policy, max_attempts=max_attempts)
