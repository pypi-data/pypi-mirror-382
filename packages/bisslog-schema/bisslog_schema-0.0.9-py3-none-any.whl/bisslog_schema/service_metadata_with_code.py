"""
Module for representing a complete service definition enriched with source code metadata.

This module defines a dataclass that merges user-declared service information (e.g., from
a YAML or JSON file) with implementation details discovered at runtime from the codebase.

The resulting structure can be used for validation, consistency checks, code generation,
or documentation of the service, ensuring alignment between declared contracts and real logic.

Classes
-------
ServiceInfoWithCode
    Encapsulates the full service definition, combining declared metadata, discovered use cases,
    and associated setup configuration metadata.
"""
from dataclasses import dataclass
from typing import Dict, Union, Callable, Any

from .schema.service_info import ServiceInfo
from .use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfo


@dataclass
class ServiceInfoWithCode:
    """Combines user-declared service metadata with use cases discovered in the source code.

    This structure is used to validate, align, or document the service definition by comparing
    declared metadata against the actual implementation found in code.

    Attributes
    ----------
    declared_metadata : ServiceInfo
        The service information provided explicitly by the user (e.g., via a YAML or JSON spec).
    discovered_use_cases : Dict[str, UseCaseCodeInfo]
        Use cases detected from the source code implementation.
    """
    declared_metadata: ServiceInfo
    discovered_use_cases: Dict[str, Union[UseCaseCodeInfo, Callable[..., Any]]]
