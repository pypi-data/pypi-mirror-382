"""
Module for inspecting and resolving use case objects or classes within Python modules.

This module defines the abstract base class `ModuleUseCaseInspector`, which provides
utility methods and an interface for locating use case implementations in a given
module. It supports both standard and custom naming conventions for identifying
use case objects or classes, and is intended to be subclassed for concrete resolution
strategies.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
import importlib

from ...utils.to_snake_case import to_snake_case


class UseCaseModuleInspector(ABC):
    """
    Abstract base class for resolving use case code from a given module.

    This class defines the interface and utility methods for locating and identifying
    use case objects or classes within a Python module, supporting both standard and
    custom naming conventions.
    """

    @abstractmethod
    def __call__(self, module_path: str, *,
                 var_name_in_module: Optional[str] = None) -> Any:
        """
        Resolve the use case code for the specified module.

        Parameters
        ----------
        module_path : str
            The import path of the module to inspect.
        var_name_in_module : Optional[str], optional
            The variable name of the use case object in the module, by default None.

        Returns
        -------
        Any
            The resolved use case object or class.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """
        raise NotImplementedError("")  # pragma: no cover

    @staticmethod
    def _is_use_case_object(obj: Any) -> bool:
        """
        Determine if the given object is a use case instance or function.

        Parameters
        ----------
        obj : object
            The object to check.

        Returns
        -------
        bool
            True if the object is a use case instance or function, False otherwise.
        """
        if not isinstance(obj, type) and hasattr(obj, "__is_use_case__"):
            return True
        return False

    @staticmethod
    def _is_same_module(attr, module) -> bool:
        """
        Check if the attribute belongs to the same module.

        Parameters
        ----------
        attr : object
            The attribute to check.
        module : ModuleType
            The module to compare against.

        Returns
        -------
        bool
            True if the attribute belongs to the same module, False otherwise.
        """
        return hasattr(attr, "__module__") and attr.__module__ == module.__name__

    @staticmethod
    def _is_use_case_class(obj) -> bool:
        """
        Determine if the given object is a use case class.

        Parameters
        ----------
        obj : object
            The object to check.

        Returns
        -------
        bool
            True if the object is a use case class, False otherwise.
        """
        if isinstance(obj, type) and hasattr(obj, "__is_use_case__"):
            return True
        return False

    @staticmethod
    def _load_module(module_path: str):
        """
        Load a Python module by its import path.

        Parameters
        ----------
        module_path : str
            The import path of the module to load.

        Returns
        -------
        tuple
            A tuple containing the loaded module and its last path component as a string.
        """
        module = importlib.import_module(module_path)
        return module, module.__name__.split(".")[-1]

    @staticmethod
    def _generate_var_name_suggestions(use_case_keyname: str):
        """
        Generate possible variable name suggestions for a use case.

        Parameters
        ----------
        use_case_keyname : str
            The key name of the use case.

        Yields
        ------
        str
            Suggested variable names for the use case.
        """
        yield use_case_keyname

        if use_case_keyname.islower():
            yield use_case_keyname.upper()
            if not use_case_keyname.endswith("use_case"):
                yield use_case_keyname + "_use_case"
        else:  # could be PascalCase or camelCase
            yield use_case_keyname.capitalize()
            snake_case_uc_name = str(to_snake_case(use_case_keyname))
            if snake_case_uc_name != use_case_keyname:
                yield snake_case_uc_name
                yield snake_case_uc_name.upper()
                yield snake_case_uc_name.lower()
                yield snake_case_uc_name + "_use_case"
                yield snake_case_uc_name.upper() + "_USE_CASE"
