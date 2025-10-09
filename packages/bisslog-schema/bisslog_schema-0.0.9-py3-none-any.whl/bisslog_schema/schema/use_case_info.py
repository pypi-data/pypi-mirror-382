"""
Module to define the UseCaseInfo class, which models use case metadata for a service,
including criticality, triggers, and actor details.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Any, Dict
from json import dumps

from ..commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport
from .entity_info import EntityInfo
from .enums.criticality import CriticalityEnum
from .external_interaction import ExternalInteraction
from .triggers.trigger_info import TriggerInfo


@dataclass
class UseCaseInfo(EntityInfo):
    """
    Represents a use case with metadata including triggers, criticality, and associated actor.

    Attributes
    ----------
    triggers : List[TriggerInfo]
        A list of triggers that initiate the use case.
    criticality : Optional[Union[str, CriticalityEnum, int]]
        The criticality level of the use case. Defaults to MEDIUM.
    actor : Optional[str]
        The primary actor that interacts with the use case.
    external_interactions : List[ExternalInteraction]
        A list of external interactions associated with the use case.
    """
    keyname: str = None
    triggers: List[TriggerInfo] = field(default_factory=list)
    criticality: Optional[Union[str, CriticalityEnum, int]] = CriticalityEnum.MEDIUM
    actor: Optional[str] = None
    external_interactions: List[ExternalInteraction] = field(default_factory=list)

    @classmethod
    def analyze(cls, data: dict) -> MetadataAnalysisReport:
        """
        Validates the provided data against the UseCaseInfo schema.

        Parameters
        ----------
        data : dict
            The data to validate.

        Returns
        -------
        MetadataAnalysisReport
            The summary of the analysis

        Raises
        ------
        ValueError
            If validation fails.
        """
        metadata_analysis_report = super().analyze(data)
        keyname = data["keyname"]

        # Validate main fields
        validated_data, errors = cls._validate_main_fields(data, data.get("name") or keyname)

        # Process sub-reports
        sub_reports = cls._process_sub_reports(validated_data, keyname)

        # Update the report
        metadata_analysis_report.critical_validation_count += len(cls._get_validations_list())
        metadata_analysis_report.errors += errors
        metadata_analysis_report.sub_reports.update(sub_reports)
        return metadata_analysis_report

    @classmethod
    def _get_validations_list(cls) -> list:
        """Return the list of validations to perform."""
        return [
            (cls._validate_triggers, "triggers"),
            (cls._parse_criticality, "criticality"),
            (lambda x: cls._validate_optional_str_field("actor", x), "actor"),
            (cls._validate_external_interaction_field, "external_interactions"),
        ]

    @classmethod
    def _validate_main_fields(cls, data: dict, keyname: str) -> tuple:
        """Validate the main fields of the use case."""
        validated_data = {}
        errors = []

        for validate_func, field_name in cls._get_validations_list():
            field_value = data.get(field_name,
                                   CriticalityEnum.MEDIUM if field_name == "criticality" else [])
            try:
                validated_data[field_name] = validate_func(field_value)
            except (TypeError, ValueError) as e:
                msg = f"UseCaseInfo '{keyname}' error: {e.args[0]}"
                errors.append(msg)

        return validated_data, errors

    @classmethod
    def _process_sub_reports(cls, validated_data: dict, keyname: str) -> dict:
        """Process and validate sub-reports for triggers and external interactions."""
        sub_reports = {"triggers": [], "external_interactions": []}

        # Process triggers
        triggers = validated_data.get("triggers", [])
        for i, trigger in enumerate(triggers):
            sub_reports["triggers"].append(TriggerInfo.analyze(trigger, keyname, i))

        # Process external interactions
        external_interactions = validated_data.get("external_interactions", [])
        if external_interactions is not None:
            for i, interaction in enumerate(external_interactions):
                sub_reports["external_interactions"].append(
                    ExternalInteraction.analyze(interaction, keyname)
                )

        return sub_reports

    @classmethod
    def from_dict(cls, data: dict) -> "UseCaseInfo":
        """
        Creates a UseCaseInfo instance from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary containing use case information.

        Returns
        -------
        UseCaseInfo
            An instance populated with the provided data.

        Raises
        ------
        ValueError
            If required fields are missing or invalid.
        """
        triggers = cls._parse_triggers(cls._validate_triggers(data.get("triggers", [])))
        criticality = cls._parse_criticality(data.get("criticality", CriticalityEnum.MEDIUM))
        external_interactions = cls._parse_external_interactions(
            data.get("external_interactions", [])
        )

        return cls(
            keyname=data["keyname"],
            name=cls._validate_required_str_field("name", data.get("name")),
            description=cls._validate_description(data.get("description")),
            type=cls._validate_type(data.get("type")),
            tags=cls._validate_tags(data.get("tags", {})),
            triggers=triggers,
            external_interactions=external_interactions,
            criticality=criticality,
            actor=cls._validate_optional_str_field("actor", data.get("actor")),
        )

    @classmethod
    def _validate_triggers(cls, triggers: Any) -> list:
        """
        Validates the `triggers` field.

        Parameters
        ----------
        triggers : Any
            The triggers value to validate.

        Returns
        -------
        list
            The validated triggers value.

        Raises
        ------
        ValueError
            If the triggers are not a list or if any trigger is invalid
        """
        if not isinstance(triggers, (list, tuple)):
            raise ValueError("The 'triggers' field must be a list.")
        for trigger in triggers:
            if not isinstance(trigger, dict):
                raise ValueError("Each trigger must be a dictionary.")
        return triggers

    @staticmethod
    def _parse_triggers(triggers_data: list) -> List[TriggerInfo]:
        """Parses and validates the triggers data."""
        triggers = []

        for t in triggers_data:
            try:
                triggers.append(TriggerInfo.from_dict(t))
            except Exception as e:
                raise e
        return triggers

    @staticmethod
    def _parse_criticality(criticality: Union[str, int, CriticalityEnum]) -> CriticalityEnum:
        """Parses and validates the criticality value."""
        if isinstance(criticality, (int, float)):
            return CriticalityEnum.get_from_int_val(criticality)
        if isinstance(criticality, str) and criticality.upper() in CriticalityEnum.__members__:
            return CriticalityEnum[criticality.upper()]
        if isinstance(criticality, CriticalityEnum):
            return criticality
        raise ValueError(f"Invalid criticality value: {criticality}")

    @classmethod
    def _validate_external_interaction_field(
            cls, external_interactions_data: Any) -> Optional[List[Dict[str, Any]]]:
        """
        Validates the `external_interactions` field.

        Parameters
        ----------
        external_interactions_data : Any
            The external interactions value to validate.

        Returns
        -------
        Optional[List[Dict[str, Any]]]
            The validated external interactions value.

        Raises
        ------
        ValueError
            If the external interactions are not a list or if any interaction is invalid.
        """
        if external_interactions_data is None:
            return None
        if isinstance(external_interactions_data, (list, tuple)):
            for ei_data in external_interactions_data:
                if not isinstance(ei_data, dict):
                    raise ValueError("Each external interaction must be a dictionary.")
            external_interactions = external_interactions_data
        elif isinstance(external_interactions_data, dict):
            external_interactions = []
            for key, ei_data in external_interactions_data.items():
                if not isinstance(ei_data, dict):
                    raise ValueError("Each external interaction must be a dictionary.")
                ei_data["keyname"] = key
                external_interactions.append(ei_data)
        else:
            raise ValueError("Invalid external interactions data -> "
                             f"{dumps(external_interactions_data)}")
        return external_interactions

    @classmethod
    def _parse_external_interactions(
            cls, external_interactions_data: Union[list, dict]) -> List[ExternalInteraction]:
        """Parses and validates the external interaction data."""
        ext_interactions = cls._validate_external_interaction_field(external_interactions_data)

        if ext_interactions is None:
            return []

        new_ext_interactions_parsed = []
        for ei_data in external_interactions_data:
            try:
                new_ext_interactions_parsed.append(ExternalInteraction.from_dict(ei_data))
            except Exception as e:
                raise ValueError(f"Error processing an external interaction -> {e}") from e
        return new_ext_interactions_parsed
