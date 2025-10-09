"""
This module defines a utility class for mapping external trigger identifiers
to internal domain-specific values, typically used in configuration-based
or event-driven systems.

It also includes validation logic to ensure that mapping keys follow
expected source naming conventions.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Iterable

from ...commands.analyze_metadata_file.metadata_analysis_report import MetadataAnalysisReport


@dataclass
class TriggerMappable:
    """A class that represents a mapping from external trigger values to internal values.

    This can be used in configuration-driven architectures where triggers
    (e.g., event names or message types) from external sources need to be
    translated or normalized into internal values used in the domain logic.

    Attributes
    ----------
    mapper : dict of str to str, optional
        A dictionary mapping external trigger values (keys) to internal representations (values).
        If None, no mapping will be applied."""
    mapper: Optional[Dict[str, str]] = None

    @classmethod
    def verify_source_prefix(cls, mapper: Optional[Dict[str, str]], expected_keys: Iterable[str]):
        """
        Validates that all keys in the provided mapper start with a prefix that is allowed.

        Parameters
        ----------
        mapper : dict of str to str, optional
            The mapping of source paths to values. Keys must start with one of
            the expected prefixes.
        expected_keys : Iterable of str
            A list or set of valid prefixes that the keys in `mapper` are expected to start with.

        Raises
        ------
        ValueError
            If any key in the mapper does not start with a valid prefix from `expected_keys`.
        """

        report = cls.analyze_source_prefix(mapper, expected_keys)
        if report.errors:
            raise ValueError(f"Invalid source prefix in mapper: {report.errors}")
        return mapper

    @classmethod
    def analyze_source_prefix(cls, mapper: Optional[Dict[str, str]],
                              expected_keys: Iterable[str]) -> MetadataAnalysisReport:
        """
        Analyzes the source prefix of the provided mapper.

        Parameters
        ----------
        mapper : dict of str to str, optional
            The mapping of source paths to values. Keys must start with one of
            the expected prefixes.
        expected_keys : Iterable of str
            A list or set of valid prefixes that the keys in `mapper` are expected to start with.

        Returns
        -------
        MetadataAnalysisReport
            A report indicating whether the source prefix is valid or not.
        """
        counter = 0
        errors = []
        if mapper is not None:
            for source_path in mapper:
                counter += 1
                source_prefix = source_path.split(".", 1)[0]
                if source_prefix not in expected_keys:
                    msg = (f"Invalid source path '{source_path}': unknown prefix "
                           f"'{source_prefix}'. Expected one of: {sorted(expected_keys)}.")
                    errors.append(msg)

        return MetadataAnalysisReport(counter, 0, errors, [], {})
