"""
Module for runtime analysis of use case modules and objects.

This module provides functionality to inspect, analyze, and resolve use case objects
within a given package or directory structure at runtime.
"""

import os
import importlib.util
from typing import Optional, Callable, Any

from .use_case_analyzer_base import UseCaseCodeAnalyzerBase


class PackageTreeReader(UseCaseCodeAnalyzerBase):
    """
    Analyzes use case modules and resolves use case needs at runtime.

    This class inspects a package tree to find and resolve use case objects,
    supporting dynamic analysis and discovery of use case implementations.
    """

    def __init__(self, inspector: Callable[[str], Any]) -> None:
        self._inspector = inspector

    def __call__(self, path: Optional[str] = None) -> dict:
        """
        Analyze the use case modules in the given path or default locations.

        Parameters
        ----------
        path : Optional[str], optional
            The path or module to analyze. If None, uses default search paths.

        Returns
        -------
        dict
            Dictionary mapping use case names to their resolved objects.
        """
        module_path = self._find_module_path(path)
        return self._collect_objects_from_package(module_path)

    def _collect_objects_from_package(self, package_name: str) -> dict:
        """
        Recursively walk through a package and collect inspected use case objects.

        Parameters
        ----------
        package_name : str
            Name of the package to walk through.

        Returns
        -------
        dict
            Mapping of use case keys to resolved objects.
        """
        response = {}
        spec = importlib.util.find_spec(package_name)
        if not spec or not spec.submodule_search_locations:
            return response

        package_path = spec.submodule_search_locations[0]

        for entry in sorted(os.listdir(package_path)):
            full_path = os.path.join(package_path, entry)

            if self._is_skippable(entry):
                continue

            if os.path.isdir(full_path) and self._is_python_package(full_path):
                subpackage = f"{package_name}.{entry}"
                self._merge_subpackage_objects(response, subpackage)
            elif entry.endswith(".py"):
                module_name = entry[:-3]
                module_path = f"{package_name}.{module_name}"
                self._add_module_object(response, module_name, module_path)

        return response

    def _merge_subpackage_objects(self, result: dict, subpackage_name: str) -> None:
        """
        Recursively analyze a subpackage and merge its results into the main response.

        Parameters
        ----------
        result : dict
            Accumulated results from the parent package.
        subpackage_name : str
            Subpackage name to analyze and merge.
        """
        sub_result = self._collect_objects_from_package(subpackage_name)
        duplicates = set(result).intersection(sub_result)
        if duplicates:
            raise KeyError(f"Duplicate use case impl with keyname {tuple(duplicates)}")
        result.update(sub_result)

    def _add_module_object(self, result: dict, key: str, module_path: str) -> None:
        """
        Inspect a single module and add its object to the result dictionary.

        Parameters
        ----------
        result : dict
            The dictionary to store resolved objects.
        key : str
            Key name for the use case (typically the module name).
        module_path : str
            Full module path to inspect.
        """
        obj = self._inspector(module_path)
        if obj:
            result[key] = obj

    @staticmethod
    def _is_skippable(entry: str) -> bool:
        """
        Determine if a file or directory should be skipped.

        Parameters
        ----------
        entry : str
            The file or directory name.

        Returns
        -------
        bool
            True if the entry should be skipped, False otherwise.
        """
        return entry.startswith("__") or entry.endswith((".pyc", ".pyo"))

    @staticmethod
    def _is_python_package(path: str) -> bool:
        """
        Check if a directory is a Python package.

        Parameters
        ----------
        path : str
            Directory path to check.

        Returns
        -------
        bool
            True if the directory contains an __init__.py file.
        """
        return os.path.exists(os.path.join(path, "__init__.py"))
