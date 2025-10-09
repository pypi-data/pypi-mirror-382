"""Module defining trigger configuration abstract class"""
from abc import ABCMeta
from typing import Dict, Any, List, Tuple

from ..base_obj_schema import BaseObjSchema
from ...commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport


class TriggerOptions(BaseObjSchema, metaclass=ABCMeta):
    """Abstract base class for trigger-specific options.

    All trigger option classes must implement the from_dict method for deserialization."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TriggerOptions":
        """Deserialize a dictionary into a TriggerOptions instance.

        Parameters
        ----------
        data : dict
            Dictionary containing the trigger options.

        Returns
        -------
        TriggerOptions
            An instance of a subclass implementing TriggerOptions."""
        raise NotImplementedError("from_dict not implemented")

    @classmethod
    def analyze(cls, data: Dict[str, Any], trigger_keyname: str,
                use_case_name: str) -> MetadataAnalysisReport:
        """Analyze the trigger options and return a dictionary of results.

        Parameters
        ----------
        data : dict
            Dictionary containing the trigger options.
        trigger_keyname: str
            The key name of the trigger in the use case configuration.
        use_case_name : str
            The name of the use case for which the trigger options are being analyzed.

        Returns
        -------
        dict
            A dictionary containing the analysis results."""
        raise NotImplementedError("analyze not implemented")

    @classmethod
    def _run_validations(cls, trigger_keyname: str, use_case_name: str,
                         validations: List[Tuple]) -> List[str]:
        """Run simple validations and return a list of error messages.

        Parameters
        ----------
        validations : list of tuples
            A list of tuples containing validation functions and their arguments.
        trigger_keyname : str
            The key name of the trigger in the use case configuration.
        use_case_name : str
            The name of the use case for which the trigger options are being analyzed.

        Returns
        -------
        list of str
            A list of error messages."""
        errors = []
        for validation in validations:
            validator, *args = validation
            try:
                validator(*args)
            except (ValueError, TypeError) as e:
                errors.append(f"{cls.__name__} '{trigger_keyname}' on "
                              f"use case '{use_case_name}' error: {e.args[0]}")
        return errors
