"""Module providing the base EntityInfo data model."""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from .base_obj_schema import BaseObjSchema
from ..commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport


@dataclass
class EntityInfo(BaseObjSchema):
    """Base class representing basic information about an entity.

    Attributes
    ----------
    name : str, optional
        The name of the entity.
    description : str, optional
        A brief description of the entity.
    type : str, optional
        The type or category of the entity.
    tags : dict of str to str, optional
        A dictionary of key-value pairs for tagging the entity. Defaults to an empty dictionary."""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def analyze(cls, data: Dict[str, Any]) -> MetadataAnalysisReport:
        """
        Validate the provided data against the EntityInfo schema.

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
        validations = [
            (cls._validate_name, data.get("name")),
            (cls._validate_description, data.get("description")),
            (cls._validate_type, data.get("type")),
            (cls._validate_tags, data.get("tags", {})),
        ]
        name = data.get("name") or 'unknown'

        errors = []
        warnings = []

        for func, arg in validations:
            try:
                func(arg)
            except (TypeError, ValueError) as e:
                errors.append(f"{cls.__name__} '{name}' error: {e.args[0]}")
        return MetadataAnalysisReport(len(validations), 0, errors, warnings, {})

    @classmethod
    def _validate_name(cls, name: Optional[str]) -> str:
        """
        Validate the `name` field.

        Parameters
        ----------
        name : Optional[str]
            The name value to validate.

        Returns
        -------
        str
            The validated name value.

        Raises
        ------
        ValueError
            If the name is not a non-empty string.
        """
        return cls._validate_optional_str_field("name", name)

    @staticmethod
    def _validate_tags(tags: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate the `tags` field.

        Parameters
        ----------
        tags : Optional[Dict[str, Any]]
            The tags dictionary to validate.

        Returns
        -------
        Dict[str, Any]
            The validated dictionary of tags.

        Raises
        ------
        ValueError
            If the tags are not a dictionary.
        """
        if tags is not None and not isinstance(tags, dict):
            raise ValueError("The 'tags' field must be a dictionary if provided.")
        return tags or {}

    @classmethod
    def _validate_description(cls, description: Optional[str]) -> Optional[str]:
        """
        Validate the `description` field.

        Parameters
        ----------
        description : Optional[str]
            The description value to validate.

        Returns
        -------
        Optional[str]
            The validated description value.

        Raises
        ------
        ValueError
            If the description is not a string.
        """
        return cls._validate_optional_str_field("description", description)

    @classmethod
    def _validate_type(cls, entity_type: Optional[str]) -> Optional[str]:
        """
        Validate the `type` field.

        Parameters
        ----------
        entity_type : Optional[str]
            The type value to validate.

        Returns
        -------
        Optional[str]
            The validated description value.

        Raises
        ------
        ValueError
            If the description is not a string.
        """
        return cls._validate_optional_str_field("entity_type", entity_type)
