"""
This module defines data structures for representing Bisslog setup and runtime
configuration metadata.

It provides classes used for introspection, metadata extraction, and validation
of setup functions and runtime-specific configuration functions. These structures
enable static analysis and cross-module interoperability between setup logic
and runtime targets.
"""
import warnings

from dataclasses import dataclass, field
from typing import Optional, Dict

from bisslog_schema.setup.runtime_type import RuntimeType


@dataclass
class BisslogSetupFunction:
    """
    Represents a globally registered Bisslog setup function.

    Attributes
    ----------
    module : str
        The name of the module where the function is defined.
    function_name : str
        The name of the function.
    n_params : int
        The number of parameters the function accepts.
    """
    module: str
    function_name: str
    n_params: int


@dataclass
class BisslogRuntimeConfig:
    """
    Represents a runtime-specific configuration function.

    Attributes
    ----------
    module : str
        The name of the module where the function is defined.
    function_name : str
        The name of the function.
    """
    module: str
    function_name: str


@dataclass
class BisslogSetup:
    """
    Holds both the global setup function and the runtime-specific configurations.

    This class is used to aggregate metadata and enable lookups or validations
    involving setup and runtime-targeted functions.

    Attributes
    ----------
    setup_function : Optional[BisslogSetupFunction]
        Metadata for the global setup function, if defined.
    runtime : Dict[RuntimeType, BisslogRuntimeConfig]
        Mapping of runtime environments to their corresponding config metadata.
    """
    setup_function: Optional[BisslogSetupFunction] = None
    runtime: Dict[str, BisslogRuntimeConfig] = field(default_factory=dict)

    def add_runtime_config(self, runtime: str, module: str, function_name: str):
        """
        Add a new runtime-specific configuration to the setup structure.

        Parameters
        ----------
        runtime : Union[RuntimeType, str]
            The runtime environment to associate with this config.
        module : str
            The name of the module where the function is located.
        function_name : str
            The name of the function.

        Raises
        ------
        ValueError
            If the runtime is already registered.
        """

        try:
            runtime = RuntimeType(runtime)
        except ValueError:
            warnings.warn(f"Unknown runtime type: {runtime!r}. Proceeding with raw value.",
                          RuntimeWarning)

        if runtime in self.runtime:
            raise ValueError(f"Runtime {runtime} already exists in the setup.")
        self.runtime[runtime] = BisslogRuntimeConfig(module=module, function_name=function_name)
