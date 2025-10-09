"""
Module for inspecting and resolving use case objects from Python modules.

This module defines `ModuleUseCaseObjectInspector`, which extends the base inspector
to locate, validate, and extract use case objects or construct objects from classes from a given
module. It supports both standard variable naming conventions and fallback strategies.
"""

from typing import Callable, Optional, Any

from .use_case_module_inspector import UseCaseModuleInspector


class UseCaseObjectModuleInspector(UseCaseModuleInspector):
    """Inspects a Python module to resolve a callable use case object or class.

    This class supports standard naming conventions and deep inspection logic to
    detect decorated functions or classes that represent executable use cases.

    Methods
    -------
    __call__(module_path, *, var_name_in_module=None)
        Loads and resolves the use case object from a given module path.
    """

    @classmethod
    def _find_use_case_obj_standard(cls, module,
                                    use_case_keyname: str) -> Optional[Callable[..., Any]]:
        """Find the use case object in the module using standard naming conventions.

        Parameters
        ----------
        module : ModuleType
            The Python module to inspect.
        use_case_keyname : str
            The inferred or expected base name for the use case object.

        Returns
        -------
        Optional[Callable[..., Any]]
            The matched use case object, if found.
        """
        for suggested_var_name in cls._generate_var_name_suggestions(use_case_keyname):
            if hasattr(module, suggested_var_name):
                attr = getattr(module, suggested_var_name)
                if attr is None:
                    continue
                if attr.__module__ != module.__name__ or not cls._is_use_case_object(attr):
                    continue
                return attr
        return None

    @classmethod
    def _deep_search_of_object(cls, module: object) -> Optional[Callable[..., Any]]:
        """Analyze the module to find a use case object or class using relaxed inspection.

        This method acts as a fallback when standard naming resolution fails.
        It checks for decorated use case objects and valid class candidates.

        Parameters
        ----------
        module : ModuleType
            The Python module to inspect.

        Returns
        -------
        Optional[Callable[..., Any]]
            A resolved use case object or instance, or None if not found.
        """
        class_obj = None
        for attr in vars(module).values():
            if not cls._is_same_module(attr, module):
                continue
            if cls._is_use_case_class(attr):
                class_obj = attr
                continue
            if cls._is_use_case_object(attr):
                return attr
        if class_obj is not None:
            return cls._generate_object_from_class(class_obj)
        return None

    @staticmethod
    def _generate_object_from_class(class_object: type) -> Callable:
        """Instantiate a class to produce a callable use case object.

        Parameters
        ----------
        class_object : type
            A class that implements a callable use case.

        Returns
        -------
        Callable
            An instance of the class, expected to be callable.
        """
        return class_object()

    def __call__(self, module_path: str, *,
                 var_name_in_module: Optional[str] = None) -> Optional[Callable[..., Any]]:
        """Load and inspect a module to resolve a use case object or class.

        If a variable name is specified, it is used directly; otherwise, standard naming
        conventions and deep inspection are applied.

        Parameters
        ----------
        module_path : str
            The Python import path or file path to the module.
        var_name_in_module : Optional[str], optional
            The explicit variable name to use in the module (default is None).

        Returns
        -------
        Optional[Callable[..., Any]]
            The resolved use case object or class instance, or None if not found.

        Raises
        ------
        AttributeError
            If the specified variable is not found or is not a valid use case object.
        """
        module, use_case_keyname = self._load_module(module_path)
        if var_name_in_module:
            if not hasattr(module, var_name_in_module):
                raise AttributeError(
                    f"Use case object not found in module with var name {var_name_in_module}"
                )
            obj = getattr(module, var_name_in_module)
            if not self._is_use_case_object(obj):
                raise AttributeError(
                    f"Use case object in var name {var_name_in_module} is not a use case object"
                )
            return obj
        res = self._find_use_case_obj_standard(module, use_case_keyname)
        if res is not None:
            return res
        return self._deep_search_of_object(module)
