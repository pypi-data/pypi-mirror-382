"""
Base utilities for analyzing and resolving use case module paths.

This module provides path inspection and resolution logic for identifying
valid Python module paths and use case folders. It includes utilities to
distinguish between dot-paths (`package.module`) and file system paths
(`src/usecases`), supporting both direct and default resolution strategies.

"""

import re
import os
from typing import Optional


class UseCaseCodeAnalyzerBase:
    """
    Base class providing utilities for use case module resolution and path validation.

    This class includes static and class methods for verifying Python module-style
    strings and directory-style paths, and resolving default use case locations.
    """

    @staticmethod
    def _is_python_module_path(path: str) -> bool:
        """Check if the path is a valid Python-style module path (e.g., "package.module").

        Parameters
        ----------
        path : str
            The dot-separated module path to check.

        Returns
        -------
        bool
            True if it is a valid Python module path, False otherwise.
        """
        return bool(re.fullmatch(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$", path))

    @staticmethod
    def _is_path_valid(path: str) -> bool:
        """Check if the path is a valid directory-style path (e.g., "src/usecases").

        Parameters
        ----------
        path : str
            The path to validate.

        Returns
        -------
        bool
            True if the path is a valid directory path, False otherwise.
        """
        return bool(
            re.fullmatch(
                r'^(?:\.*/)?(?:[a-zA-Z_][a-zA-Z0-9_]*/)*[a-zA-Z_][a-zA-Z0-9_]*$',
                path
            )
        )

    @classmethod
    def _find_module_path(cls, path: Optional[str]) -> str:
        """Resolve the dot-separated module path from a given string or default options.

        Parameters
        ----------
        path : Optional[str]
            A path to a module or directory. If None, default locations are searched.

        Returns
        -------
        str
            The resolved module path in dot notation (e.g., 'src.domain.use_cases').

        Raises
        ------
        ValueError
            If the given path is invalid or no suitable path is found.
        """

        if path is None:
            path = os.getenv("BISSLOG_USE_CASES_FOLDER")

        if path is not None:
            if cls._is_python_module_path(path):
                path_folder = "./" + path.replace(".", "/")
                path_module = path
            elif cls._is_path_valid(path):
                path_module = path.replace("/", ".").strip(".")
                path_folder = path
            else:
                raise ValueError(
                    f"Invalid path: '{path}'. Path should be a valid module or folder path.")
            if not os.path.isdir(path_folder):
                raise ValueError(f"Path '{path}' of use cases does not exist")
            return path_module

        defaults = (
            "use_cases", "domain.use_cases", "usecases", "domain.usecases",
            "src.usecases", "src.domain.use_cases", "src.domain.usecases", "src.use_cases"
        )
        for d_path in defaults:
            path_folder = os.path.join(d_path.replace(".", "/"))
            if os.path.isdir(path_folder):
                return d_path

        raise ValueError("Could not find any default path for use cases.")
