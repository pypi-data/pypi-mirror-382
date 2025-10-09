"""Module defining trigger conceptual information class"""
from dataclasses import dataclass
from typing import Dict, Any, Union, Optional

from ..base_obj_schema import BaseObjSchema
from ...commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport
from ..enums.trigger_type import TriggerEnum
from .trigger_options import TriggerOptions


@dataclass
class TriggerInfo(BaseObjSchema):
    """Represents a complete trigger configuration including its type and specific options.

    Attributes
    ----------
    type : TriggerEnum|str
        The type of the trigger (e.g., HTTP, WebSocket).
    options : TriggerOptions
        The configuration options specific to the trigger type.
    keyname  : Optional[str]
        The keyname of the trigger, used for identification.
    """
    type: Union[TriggerEnum, str]
    options: Union[TriggerOptions, Dict[str, Any]]
    keyname: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TriggerInfo":
        """
        Creates a TriggerInfo instance from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary containing the trigger configuration.

        Returns
        -------
        TriggerInfo
            An instance of TriggerInfo.

        Raises
        ------
        ValueError
            If required fields are missing or invalid.
        """
        # Validate and parse the trigger type
        trigger_type = cls._validate_type(data.get("type", "http"))

        # Validate and parse the options
        options = cls._validate_options(data.get("options", {}))

        # Validate and parse the keyname
        key_name = cls._validate_optional_str_field("keyname", data.get("keyname"))


        if (trigger_type is not None and isinstance(trigger_type, TriggerEnum)
                and isinstance(options, dict)):
            try:
                options = trigger_type.cls.from_dict(options)
            except Exception as e:
                raise ValueError("Error parsing options for trigger"
                                 f" type '{trigger_type}': {e}") from e

        return TriggerInfo(type=trigger_type, options=options, keyname=key_name)

    @classmethod
    def analyze(cls, data: Dict[str, Any], use_case_name: str,
                index_trigger: int = None) -> MetadataAnalysisReport:
        """Analyze the trigger information.

        Parameters
        ----------
        data : Dict[str, Any]
            The trigger data to analyze.
        use_case_name : str
            The name of the parent use case.
        index_trigger : int, optional
            The index of the trigger if no keyname is provided.

        Returns
        -------
        MetadataAnalysisReport
            The analysis report containing validation results.
        """
        keyname = data.get("keyname", f"unknown-{index_trigger}")
        validations = cls._get_validations_list(data)
        warnings = cls._check_for_warnings(data, keyname, use_case_name)
        data_validated, errors = cls._validate_data(validations, keyname, use_case_name)
        sub_reports = cls._generate_sub_reports(data_validated, keyname, use_case_name)

        return MetadataAnalysisReport(len(validations), 1, errors, warnings, sub_reports)

    @classmethod
    def _get_validations_list(cls, data: Dict[str, Any]) -> list:
        """Return the list of validations to perform."""
        return [
            ("type", cls._validate_type, data.get("type", "http")),
            ("options", cls._validate_options, data.get("options", {})),
            ("keyname", lambda x: cls._validate_optional_str_field("keyname", x),
             data.get("keyname")),
        ]

    @classmethod
    def _check_for_warnings(cls, data: Dict[str, Any], keyname: str, use_case_name: str) -> list:
        """Check for and return any warnings in the data."""
        warnings = []
        if "type" not in data:
            warnings.append(
                f"TriggerInfo '{keyname}' warning on use case '{use_case_name}': "
                f"The 'type' field is missing on trigger."
            )
        return warnings

    @classmethod
    def _validate_data(cls, validations: list,
                       keyname: str, use_case_name: str) -> tuple:
        """Validate the trigger data and return validated data and errors."""
        data_validated = {}
        errors = []

        for name, validate_func, value in validations:
            try:
                data_validated[name] = validate_func(value)
            except (TypeError, ValueError) as e:
                msg = (f"TriggerInfo '{keyname}' error on use case"
                       f" '{use_case_name}': {e.args[0]}")
                errors.append(msg)

        return data_validated, errors

    @classmethod
    def _generate_sub_reports(cls, data_validated: Dict[str, Any],
                              keyname: str, use_case_name: str) -> dict:
        """Generate sub-reports for trigger options if applicable."""
        sub_reports = {}
        trigger_type = data_validated.get("type")
        options = data_validated.get("options")

        if (trigger_type is not None and isinstance(trigger_type, TriggerEnum)
                and isinstance(options, dict)):
            sub_reports["options"] = [
                trigger_type.cls.analyze(options, keyname, use_case_name)
            ]

        return sub_reports

    @classmethod
    def _validate_type(cls, type_str: Optional[str]) -> TriggerEnum:
        """
        Validates and parses the trigger type.

        Parameters
        ----------
        type_str: Optional[str]
            The trigger type string to validate.

        Returns
        -------
        TriggerEnum
            The parsed trigger type.

        Raises
        ------
        ValueError
            If the 'type' field is missing or invalid.
        """
        type_str = cls._validate_required_str_field("type", type_str)
        type_obj = TriggerEnum.from_str(type_str)
        if type_obj is None:
            type_obj = type_str
        return type_obj

    @staticmethod
    def _validate_options(
            options: Dict[str, Any]) -> Union[TriggerOptions, Dict[str, Any]]:
        """
        Validates and parses the trigger options.

        Parameters
        ----------
        options: Dict[str, Any]
            The trigger options to validate.

        Returns
        -------
        Union[TriggerOptions, Dict[str, Any]]
            The parsed trigger options.

        Raises
        ------
        TypeError
            If the 'options' field is not a dictionary or TriggerOptions instance.
        ValueError
            If there is an error parsing the options for the trigger type.
        """
        if not isinstance(options, (dict, TriggerOptions)):
            raise TypeError("The 'options' field must be a dictionary "
                            "or an instance of TriggerOptions.")
        return options
