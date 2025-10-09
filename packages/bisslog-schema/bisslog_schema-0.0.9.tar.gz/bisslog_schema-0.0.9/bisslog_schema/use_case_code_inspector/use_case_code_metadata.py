"""
Use case metadata models.

This module defines frozen dataclasses for representing metadata extracted
from use case implementations, whether they are objects or classes. These
structures are intended to support both runtime and static analysis of
use case definitions.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UseCaseCodeInfo:
    """Base metadata structure for a use case object or class.

    Contains shared information such as the use case name and documentation.

    Attributes
    ----------
    name : str
        The name or identifier of the use case.
    docs : str
        The docstring or documentation associated with the use case.
    """
    name: str
    docs: Optional[str]
    module: Optional[str]
    is_coroutine: bool

@dataclass(frozen=True)
class UseCaseCodeInfoObject(UseCaseCodeInfo):
    """Metadata for a use case object or function instance.

    Extends `UseCaseCodeInfo` by adding the variable name under which the use case
    is defined in the module.

    Attributes
    ----------
    var_name : str
        The name of the variable in the module where the use case is assigned.
    """
    var_name: str

@dataclass(frozen=True)
class UseCaseCodeInfoClass(UseCaseCodeInfo):
    """Metadata for a use case class definition.

    Extends `UseCaseCodeInfo` with the name of the class representing the use case.

    Attributes
    ----------
    class_name : str
        The name of the class implementing the use case.
    """
    class_name: str
