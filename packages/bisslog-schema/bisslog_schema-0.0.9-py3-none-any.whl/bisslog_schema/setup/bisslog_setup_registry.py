"""
Module for managing setup and runtime configuration registration.

This module defines the BisslogSetupRegistry class, which stores a global setup function
and multiple runtime-specific configuration functions. It allows decorators to register
functions that are later introspected or executed based on runtime context.

Features:
- Support for global setup (`@bisslog_setup`), with a single function allowed.
- Support for runtime-specific configuration (`@bisslog_runtime_config`), with named
  and wildcard-based targeting.
- Metadata inspection for documentation and tooling.
"""
import warnings
import inspect
from typing import Dict, Optional, Callable, Iterable, Tuple, Set

from .runtime_type import RuntimeType
from .setup_metadata import BisslogSetupFunction, BisslogSetup


class BisslogSetupRegistry:
    """
    Registry for managing setup and runtime configuration functions.

    Stores a global setup function (if provided) and mappings of runtime-specific
    configuration functions, including support for wildcard patterns.

    Methods
    -------
    register_setup(func, enabled=True)
        Register a single setup function.
    register_runtime_config(func, runtimes, enabled=True)
        Register one or more runtime-specific configuration functions.
    is_covering_full()
        Check if all RuntimeType options are covered by current registrations.
    get_metadata()
        Return a metadata dictionary describing registered functions.
    run_setup(runtime, *args, **kwargs)
        Execute the appropriate setup or runtime configuration based on context.
    """

    def __init__(self):
        self._setup_function: Optional[Callable] = None
        self._runtime_functions: Dict[str, Callable] = {}
        self._wildcard_runtime_functions: Dict[str, Callable] = {}

    def register_setup(self, func: Callable, enabled: bool = True):
        """
        Register the global Bisslog setup function.

        Only one setup function can be registered. If another is already present,
        a RuntimeError will be raised.

        Parameters
        ----------
        func : Callable
            The function to register as the global setup.
        enabled : bool, optional
            Whether to register the function (default is True).

        Returns
        -------
        Callable
            The same function, unchanged.

        Raises
        ------
        RuntimeError
            If a setup function has already been registered.
        """
        if not enabled:
            return func
        if self._setup_function:
            raise RuntimeError("Only one @bisslog_setup can be defined.")
        self._setup_function = func
        return func

    def _get_wild_card_targets(self,
                               runtimes: Iterable[str]) -> Tuple[Dict[str, Callable], Set[str]]:
        targets = set(RuntimeType)
        for exclusion in runtimes[0].split("-")[1:]:
            try:
                targets.discard(RuntimeType(exclusion))
            except ValueError as err:
                raise ValueError(f"Unknown runtime in exclusion: '{exclusion}'") from err
        return self._wildcard_runtime_functions, targets

    def _get_normal_targets(self, runtimes: Iterable[str]) -> Tuple[Dict[str, Callable], Set[str]]:
        targets = set()
        for r in runtimes:
            if not isinstance(r, str):
                warnings.warn(f"Runtime identifier {r} must be a string. Ignoring it.")
                continue
            if r.startswith("*"):
                raise ValueError("Wildcard '*' must be used alone.")
            if not r.isidentifier():
                raise ValueError(f"Invalid runtime identifier: '{r}'")
            targets.add(r)
        return self._runtime_functions, targets

    def register_runtime_config(self, func: Callable,
                                runtimes: Iterable[str], enabled: bool = True):
        """
        Register a function for one or more runtimes or wildcard configurations.

        Wildcards are supported using syntax like "*-flask" to apply to all runtimes
        except 'flask'.

        Parameters
        ----------
        func : Callable
            The function to register.
        runtimes : List[str]
            One or more runtime identifiers or a wildcard string.
        enabled : bool, optional
            Whether to register the function (default is True).

        Returns
        -------
        Callable
            The same function, unchanged.

        Raises
        ------
        ValueError
            If runtimes are missing or invalid.
        """
        if not enabled:
            return func
        if not runtimes:
            raise ValueError("At least one runtime must be specified.")

        if len(runtimes) == 1 and runtimes[0].startswith("*"):
            registry, targets = self._get_wild_card_targets(runtimes)
        else:
            registry, targets = self._get_normal_targets(runtimes)

        func.__runtime_config__ = True
        func.__runtime_config_available__ = tuple(targets)

        for rt in targets:
            registry[rt] = func
        return func

    def is_covering_full(self) -> bool:
        """
        Check if all RuntimeType values are covered by registered functions.

        Returns
        -------
        bool
            True if all RuntimeType values are represented in either the normal
            or wildcard registries, False otherwise.
        """
        runtime_values = {rt.value for rt in RuntimeType}
        registered_keys = self._runtime_functions.keys() | self._wildcard_runtime_functions.keys()
        return runtime_values == registered_keys

    def get_metadata(self) -> BisslogSetup:
        """
        Return metadata for registered setup and runtime configuration functions.

        Returns
        -------
        dict
            Dictionary with keys:
            - 'setup': BisslogSetupFunction, if defined
            - 'runtime_config': List of BisslogRuntimeConfig entries
        """
        metadata = BisslogSetup()
        if self._setup_function:
            n_params = len(
                self._setup_function.__code__.co_varnames[:
                                                          self._setup_function.__code__.co_argcount]
            )
            metadata.setup_function = BisslogSetupFunction(
                module=self._setup_function.__module__,
                function_name=self._setup_function.__name__,
                n_params=n_params
            )
            return metadata

        all_runtime_funcs = self._wildcard_runtime_functions
        all_runtime_funcs.update(self._runtime_functions)

        for key, func in all_runtime_funcs.items():
            metadata.add_runtime_config(runtime=key, module=func.__module__,
                                        function_name=func.__name__)

        return metadata

    def run_setup(self, runtime: str, *args, **kwargs):
        """
        Execute the registered setup or runtime configuration for a given runtime.

        If a global setup function exists, it is executed immediately with `runtime`
        as its first argument (if accepted). Otherwise, a runtime-specific config
        is used, giving preference to explicitly registered functions.

        Parameters
        ----------
        runtime : str
            The name of the runtime environment.
        *args : Any
            Additional arguments passed to the function.
        **kwargs : Any
            Additional keyword arguments passed to the function.
        """
        if self._setup_function:
            sig = inspect.signature(self._setup_function)
            params = list(sig.parameters.values())

            if len(params) == 0:
                self._setup_function()
            elif len(params) >= 1:
                self._setup_function(runtime)
            else:
                self._setup_function(runtime, *args, **kwargs)
            return  # Skip runtime configs if setup was executed

        func = self._runtime_functions.get(runtime) or self._wildcard_runtime_functions.get(runtime)
        if func:
            func(*args, **kwargs)
