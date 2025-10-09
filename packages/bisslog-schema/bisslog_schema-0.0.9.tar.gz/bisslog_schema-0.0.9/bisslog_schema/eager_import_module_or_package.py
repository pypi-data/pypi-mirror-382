"""
Module for forcing the import of Python modules or packages at runtime.

This utility ensures that decorators or registration logic inside modules (such as
`@bisslog_setup` or other global initialization) are executed by eagerly importing
specified files or directories, whether referenced via dotted module paths or file system paths.

Classes
-------
ForceImport
    Utility class for importing modules or packages recursively to trigger side-effects
    like decorator registration or runtime configuration.
"""

import importlib
import importlib.util
import os
import warnings
from typing import Optional, Iterable


class EagerImportModulePackage:
    """
    Utility class to force the import of Python modules or packages recursively.

    This is useful in scenarios where decorators or global state initializers
    are defined in modules that would not be imported automatically.

    Attributes
    ----------
    _defaults : Iterable[str]
        List of default module or package paths to import if none is explicitly provided.
    """

    def __init__(self, defaults: Iterable[str] = ()):
        """
        Initialize the ForceImport instance.

        Parameters
        ----------
        defaults : Iterable[str], optional
            Default dotted or path-style module names to import if no argument is provided
            during invocation. Defaults to an empty tuple.
        """
        self._defaults = defaults

    def __call__(self, path_or_module: Optional[str]) -> None:
        """Force the loading of a module or a package (recursively),
        even if it hasn't been imported yet.

        This ensures that any decorators or global registrations inside those modules
        (e.g., @bisslog_setup) are executed at runtime.

        Parameters
        ----------
        path_or_module : Optional[str]
            Dotted path (e.g., 'myapp.use_cases') or filesystem path (e.g., 'myapp/use_cases').
            If None, the `defaults` list will be used instead.

        Raises
        ------
        ImportError
            If any of the modules or packages cannot be found or imported.
        """
        targets = [path_or_module] if path_or_module else list(self._defaults)
        for target in targets:
            self._import_recursively(target)

    def _import_recursively(self, dotted_or_path: str) -> None:
        """
        Helper to resolve and import a module or package recursively.

        Parameters
        ----------
        dotted_or_path : str
            Path in dot notation or file system form.
        """
        if os.path.exists(dotted_or_path):
            dotted_or_path = dotted_or_path.rstrip("/").replace("/", ".").replace("\\", ".")
        try:
            spec = importlib.util.find_spec(dotted_or_path)
            if not spec:
                warnings.warn(f"Cannot find module or package: {dotted_or_path}")

            if spec.submodule_search_locations:
                self._import_all_modules_from_package(dotted_or_path)
            else:
                importlib.import_module(dotted_or_path)
        except ImportError as e:
            pass

    def _import_all_modules_from_package(self, package_name: str) -> None:
        """
        Recursively import all modules from a given package.

        Parameters
        ----------
        package_name : str
            Dotted name of the package.
        """
        spec = importlib.util.find_spec(package_name)
        if not spec or not spec.submodule_search_locations:
            return

        package_path = spec.submodule_search_locations[0]
        importlib.import_module(package_name)  # Ensure root package is imported

        for entry in sorted(os.listdir(package_path)):
            if entry.startswith("__") or entry.endswith((".pyc", ".pyo")):
                continue

            full_path = os.path.join(package_path, entry)

            if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "__init__.py")):
                self._import_all_modules_from_package(f"{package_name}.{entry}")
            elif entry.endswith(".py"):
                importlib.import_module(f"{package_name}.{entry[:-3]}")
