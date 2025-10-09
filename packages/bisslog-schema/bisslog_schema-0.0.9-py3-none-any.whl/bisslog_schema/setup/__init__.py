"""
Module for setup registration and runtime execution in Bisslog.

This module provides decorators and runtime control functions that enable
declarative registration and controlled execution of setup logic across
different runtime environments.

Decorators
----------
- @bisslog_setup(enabled=True):
    Registers a global setup function. Only one such function is allowed.
- @bisslog_runtime_config(*runtimes, enabled=True):
    Registers a function to be executed for specific runtimes, with optional wildcard exclusions.

Functions
---------
- get_setup_metadata():
    Returns structured metadata describing all registered setup and runtime configuration functions.
- run_setup(runtime):
    Executes the registered setup or runtime configuration function for the given runtime.

Behavior
--------
If a global setup function is registered, it is executed exclusively (with optional runtime passed).
If no setup function exists, the runtime configuration matching the input runtime is executed.
Wildcard-based runtime configs are only executed if no explicit match is found.
"""

from .runtime_type import RuntimeType
from .setup_metadata import BisslogSetupFunction, BisslogRuntimeConfig, BisslogSetup

from .bisslog_setup_deco import setup_registry, bisslog_setup, bisslog_runtime_config


def get_setup_metadata() -> BisslogSetup:
    """
    Return complete metadata for setup and runtime configuration functions.

    Returns
    -------
    dict
        A dictionary with keys:
        - 'setup': BisslogSetupFunction or None
        - 'runtime_config': List[BisslogRuntimeConfig]
    """
    return setup_registry.get_metadata()


def run_setup(runtime: str, *args, **kwargs):
    """
    Execute the setup function or matching runtime configuration for the given runtime.

    If a global setup function exists, it is executed immediately (optionally with the
    runtime as a parameter). If no setup is registered, the runtime-specific configuration
    is executed instead. Explicit matches are preferred over wildcard matches.

    Parameters
    ----------
    runtime : str
        The runtime identifier (as a string or RuntimeType enum).

    Raises
    ------
    ValueError
        If the runtime is invalid or unknown.
    """
    setup_registry.run_setup(runtime, *args, **kwargs)


__all__ = ["setup_registry", "bisslog_setup", "bisslog_runtime_config",
           "get_setup_metadata", "run_setup"]
