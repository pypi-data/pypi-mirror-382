"""
Module for resolving and extracting metadata from use case code modules.

This module provides a resolver class that inspects Python modules to extract
metadata about use case objects or classes, such as their documentation and variable names.
"""
import asyncio
from typing import Optional, Any, Type

from bisslog.utils.is_free_function import is_free_function

from .use_case_module_inspector import UseCaseModuleInspector
from ..use_case_code_metadata import UseCaseCodeInfo, UseCaseCodeInfoObject, UseCaseCodeInfoClass


class UseCaseMetadataModuleInspector(UseCaseModuleInspector):
    """
    Resolves and extracts metadata for use case objects or classes from a module.

    This class inspects a Python module to find use case objects or classes,
    and builds metadata objects containing their documentation and variable names.
    """

    @staticmethod
    def _build_use_case_info_obj(use_case_keyname: str, module_path: str,
                                 obj: Any, var_name: str) -> UseCaseCodeInfoObject:
        """Build a UseCaseCodeInfo object for a use case instance or function.

        Parameters
        ----------
        use_case_keyname : str
            The key name identifier for the use case.
        obj : Any
            The use case object or function.
        module_path : str
            Path of the module
        var_name : str
            The variable name of the use case in the module.

        Returns
        -------
        UseCaseCodeInfoObject
            The metadata object for the use case, or None if not applicable.
        """
        if is_free_function(obj):
            docs = obj.__doc__
            is_coroutine = asyncio.iscoroutinefunction(obj)
        else:
            docs = obj.entrypoint.__doc__
            is_coroutine = asyncio.iscoroutinefunction(obj.entrypoint)
        return UseCaseCodeInfoObject(use_case_keyname, docs, module_path, is_coroutine, var_name)

    @classmethod
    def _find_use_case_standard(cls, module, use_case_keyname: str,
                                module_path: str) -> Optional[UseCaseCodeInfo]:
        """Find a use case object in the module using standard naming conventions.

        Parameters
        ----------
        module : ModuleType
            The Python module to inspect.
        module_path : str
            Path of the module
        use_case_keyname : str
            The key name identifier for the use case.

        Returns
        -------
        Optional[UseCaseCodeInfo]
            The metadata object for the use case, or None if not found."""
        for suggested_var_name in cls._generate_var_name_suggestions(use_case_keyname):
            if hasattr(module, suggested_var_name):
                attr = getattr(module, suggested_var_name)
                if attr is None:
                    continue
                if attr.__module__ != module.__name__ or not cls._is_use_case_object(attr):
                    continue
                return cls._build_use_case_info_obj(
                    use_case_keyname, module_path, attr, suggested_var_name)
        return None

    @classmethod
    def _deep_search_of_metadata(cls, use_case_keyname: str, module,
                                 module_path: str) -> Optional[UseCaseCodeInfo]:
        """Analyze the module to find use case objects and classes.

        Parameters
        ----------
        use_case_keyname : str
            The key name identifier for the use case.
        module : ModuleType
            The Python module to inspect.
        module_path : str
            Path of the module

        Returns
        -------
        Optional[UseCaseCodeInfo]
            The metadata object for the use case, or None if not found.
        """
        class_obj = None
        for key, attr in vars(module).items():
            if not cls._is_same_module(attr, module):
                continue
            if cls._is_use_case_class(attr):
                class_obj = attr
                continue
            if cls._is_use_case_object(attr):
                return cls._build_use_case_info_obj(use_case_keyname, module_path, attr, key)
        if class_obj is not None:
            return cls._build_use_case_info_class(use_case_keyname, module_path, class_obj)
        return None

    @staticmethod
    def _build_use_case_info_class(use_case_keyname: str, module_path: str,
                                   class_obj: Type) -> UseCaseCodeInfo:
        """Build a UseCaseCodeInfo object for a use case class.

        Parameters
        ----------
        use_case_keyname : str
            The key name identifier for the use case.
        module_path : str
            Path of the module
        class_obj : Type
            The use case class.

        Returns
        -------
        UseCaseCodeInfo
            The metadata object for the use case class.
        """
        new_obj = class_obj()
        docs = new_obj.entrypoint.__doc__
        is_coroutine = asyncio.iscoroutinefunction(new_obj.entrypoint)
        return UseCaseCodeInfoClass(use_case_keyname, docs, module_path, is_coroutine, class_obj.__name__)

    def __call__(self, module_path: str, *,
                var_name_in_module: Optional[str] = None):
        """
        Resolve and extract metadata for a use case object or class from a module.

        Parameters
        ----------
        module_path : str
            The import path of the module to inspect.
        var_name_in_module : Optional[str], optional
            The variable name of the use case in the module (default is None).

        Returns
        -------
        Optional[UseCaseCodeInfo]
            The metadata object for the use case, or None if not found.

        Raises
        ------
        AttributeError
            If the specified variable name does not exist or is not a use case object.
        """
        module, use_case_keyname = self._load_module(module_path)
        if var_name_in_module:

            if not hasattr(module, var_name_in_module):
                raise AttributeError(
                    f"Use case object not found in module with var name {var_name_in_module}")

            obj = getattr(self, var_name_in_module)
            if not self._is_use_case_object(obj):
                raise AttributeError(
                    f"Use case object in var name {var_name_in_module} is not a use case object")
            return self._build_use_case_info_obj(
                use_case_keyname, module_path, obj, var_name_in_module)

        res = self._find_use_case_standard(module, use_case_keyname, module_path)

        if res is None:
            res = self._deep_search_of_metadata(use_case_keyname, module, module_path)

        return res
