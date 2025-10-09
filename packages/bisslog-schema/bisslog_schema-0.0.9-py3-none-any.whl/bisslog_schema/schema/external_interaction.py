"""
This module defines a data structure for representing external interactions
in a system, such as database access or external service calls.
"""
from dataclasses import dataclass
from typing import Optional, Any, Dict, Union, Tuple, List

from .base_obj_schema import BaseObjSchema
from ..commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport
from .enums.type_external_interaction import TypeExternalInteraction


@dataclass
class ExternalInteraction(BaseObjSchema):
    """Represents a single external interaction, including its type, operation,
    and a standardized interaction type if resolvable.

    Attributes
    ----------
    keyname : str
        Unique key or identifier for the interaction. For example, marketing_division
    type_interaction : str, optional
        Raw string representing the type of interaction (e.g., "db", "sftp"). For example, database
    operation : str, optional
        Specific operation or action being performed. For example, get_last_sales_from_client
    type_interaction_standard : TypeExternalInteraction, optional
        Standardized type resolved from `type_interaction` using aliases."""
    keyname: str
    type_interaction: Optional[str] = None
    operation: Optional[Union[str, List[str]]] = None
    description: Optional[str] = None
    type_interaction_standard: Optional[TypeExternalInteraction] = None

    @classmethod
    def analyze(cls, data: Dict[str, Any], keyname: Optional[str] = None) -> MetadataAnalysisReport:
        """
        Validate the provided data against the ServiceInfo schema.

        Parameters
        ----------
        data : dict
            The data to validate.
        keyname : str, optional
            Keyname for the interaction.

        Returns
        -------
        MetadataAnalysisReport
            The summary of the analysis

        Raises
        ------
        ValueError
            If validation fails.
        """

        validations = [
            (lambda x: cls._validate_required_str_field("keyname", x),
             "keyname", data.get("keyname") or keyname),
            (cls._validate_operation, "operation", data.get("operation")),
            (lambda x: cls._validate_optional_str_field("description", x),
             "description", data.get("description")),
            (lambda x: cls._validate_optional_str_field("type_interaction", x),
             "type_interaction", data.get("type_interaction")),

        ]

        warnings = []
        errors = []

        validated_data = {}
        for func, field_name, *args in validations:
            try:
                validated_data[field_name] = func(*args)
            except (TypeError, ValueError) as e:
                msg = (f"ExternalInteraction '{keyname}' error: "
                       f"{e.args[0]}")
                errors.append(msg)

        type_interaction = validated_data.get("type_interaction")
        type_interaction_standard = TypeExternalInteraction.from_str(type_interaction) is None
        if type_interaction is not None and type_interaction_standard:
            warnings.append(f"ExternalInteraction '{keyname}' warning: "
                            f"The 'type_interaction' field is not standard.")


        return MetadataAnalysisReport(len(validations), 1, errors, warnings, {})

    @classmethod
    def from_dict(cls, data: Dict[str, Any],
                  keyname: Optional[str] = None) -> "ExternalInteraction":
        """
        Deserialize a dictionary into an ExternalInteraction instance.

        Parameters
        ----------
        data : dict
            Dictionary containing the external interaction information.
        keyname : str, optional
            Keyname for the interaction.

        Returns
        -------
        ExternalInteraction
            An instance of ExternalInteraction.
        """
        keyname = cls._validate_required_str_field("keyname", data.get("keyname") or keyname)
        operation = cls._validate_operation(data.get("operation"))
        type_int, type_int_standard = cls._get_type_interaction(data.get("type_interaction"))
        description = cls._validate_optional_str_field(
            "description", data.get("description") or data.get("desc"))

        return cls(keyname=keyname, type_interaction=type_int, operation=operation,
                   description=description, type_interaction_standard=type_int_standard)

    @staticmethod
    def _validate_operation(operation: Any) -> Optional[Union[str, List[str]]]:
        """Validates the operation field."""
        if operation and not (
            isinstance(operation, str) or
            (isinstance(operation, list) and all(isinstance(op, str) for op in operation))
        ):
            raise TypeError("The 'operation' must be a string or a list of strings.")
        return operation

    @classmethod
    def _get_type_interaction(cls, type_interaction: Optional[str])\
            -> Tuple[Optional[str], Optional[TypeExternalInteraction]]:
        """Processes and resolves the type_interaction field."""
        type_interaction_standard = None
        cls._validate_optional_str_field(
            "type_interaction", type_interaction)
        if type_interaction is not None:
            type_interaction_standard = TypeExternalInteraction.from_str(type_interaction)
        return type_interaction, type_interaction_standard
