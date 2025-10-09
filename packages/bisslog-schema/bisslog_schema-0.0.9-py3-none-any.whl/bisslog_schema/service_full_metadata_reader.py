"""
Module for loading and resolving service specification data.

This module defines a callable class that reads service metadata declared by the user
and merges it with use case information discovered in the codebase. The result is a
combined structure that can be used for validation, generation, or documentation purposes.
"""

from typing import Optional, Dict, Union, Callable, Any

from .use_case_code_inspector import (extract_use_case_code_metadata,
                                      PackageTreeReader, extract_use_case_obj_from_code)
from .schema.read_metadata import read_service_metadata
from .schema.use_case_info import UseCaseInfo
from .service_metadata_with_code import ServiceInfoWithCode
from .use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfo


class ServiceFullMetadataReader:
    """Loads and resolves the complete service definition by combining metadata and code analysis.

    This class reads a user-supplied metadata file and matches it against use cases found
    in the source code. It returns a single object that consolidates both perspectives."""

    def __init__(self, code_inspector: PackageTreeReader):
        self.code_inspector = code_inspector

    def __call__(self, metadata_file: Optional[str] = None,
                 use_cases_folder_path: Optional[str] = None,
                 *, encoding: str = "utf-8") -> ServiceInfoWithCode:
        """
        Extracts and merges declared service metadata with use case definitions found in code.

        Parameters
        ----------
        metadata_file : str, optional
            Path to the YAML or JSON file that contains the declared service metadata.
        use_cases_folder_path : str, optional
            Directory containing the source files where use cases are implemented.
        encoding : str, default="utf-8"
            Encoding used to read the metadata file.

        Returns
        -------
        ServiceInfoWithCode
            A structure that combines the declared service metadata with
            the implemented use cases discovered in the codebase.

        Raises
        ------
        RuntimeError
            If either the metadata file or use case implementations could not be loaded.
        """
        service_info_metadata = read_service_metadata(metadata_file, encoding=encoding)
        if not service_info_metadata:
            raise RuntimeError(f"Could not read service metadata from {metadata_file}")

        uc_code_metadata = self.code_inspector(use_cases_folder_path)
        if not uc_code_metadata:
            raise RuntimeError(
                f"Could not extract use case code metadata for {use_cases_folder_path}")

        no_code_found = service_info_metadata.use_cases.keys() - uc_code_metadata.keys()
        if no_code_found:
            print("No code was found for the following use case keynames:", no_code_found)

        no_metadata_found = uc_code_metadata.keys() - service_info_metadata.use_cases.keys()
        if no_metadata_found:
            print("No metadata was found for the following use case keynames:", no_metadata_found)

        uc_keyname_code_with_metadata = uc_code_metadata.keys() & service_info_metadata.use_cases.keys()
        print(f"There are {len(uc_keyname_code_with_metadata)} use cases to be loaded")

        new_use_case_code_info: Dict[str, Union[UseCaseCodeInfo, Callable[..., Any]]] = {}
        new_use_case_info: Dict[str, UseCaseInfo] = {}

        for uc_keyname in uc_keyname_code_with_metadata:
            new_use_case_code_info[uc_keyname] = uc_code_metadata[uc_keyname]
            new_use_case_info[uc_keyname] = service_info_metadata.use_cases[uc_keyname]

        service_info_metadata.use_cases = new_use_case_info
        return ServiceInfoWithCode(service_info_metadata, new_use_case_code_info)


# Callable instance for loading service info and code
read_full_service_metadata = ServiceFullMetadataReader(extract_use_case_code_metadata)
read_service_info_with_code = ServiceFullMetadataReader(extract_use_case_obj_from_code)
