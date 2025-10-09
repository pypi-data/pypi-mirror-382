"""
Module for reading and parsing service metadata files.
"""

import os.path
import importlib
import json
import sys
from typing import Optional

from .service_info import ServiceInfo


def _find_path(path: Optional[str]) -> str:
    """Find the path of the metadata file.

    If a path is provided, it checks if the file exists. If not, it searches
    through a list of default paths.

    Parameters
    ----------
    path : Optional[str]
        The specific file path to read. If None, searches default paths.

    Returns
    -------
    str
        The found file path.

    Raises
    ------
    ValueError
        If the given path does not exist or if no default file is found.
    """
    if path is None:
        # Check if the environment variable is set and use it if available
        path = os.getenv("SERVICE_METADATA_PATH")
    if path is not None:
        if not os.path.isfile(path):
            raise ValueError(f"Path {path} of metadata does not exist")
    else:
        default_path_options = (
            "./metadata.yml",
            "./docs/metadata.yml",
            "./metadata.json",
            "./docs/metadata.json",
            "./metadata.yaml",
            "./docs/metadata.yaml",
        )
        for path_option in default_path_options:
            if os.path.isfile(path_option):
                path = path_option
                break
        if path is None:
            raise ValueError("No compatible default path could be found")
    return path


def read_metadata_file(path: Optional[str] = None, encoding: str = "utf-8",
                       format_file: str = None) -> dict:
    """Read a metadata file from a specified path or default options.

    If a path is provided, the function validates and reads the file. If no path is given,
    it attempts to find a file from a set of default path options.

    Parameters
    ----------
    path : Optional[str], default=None
        The specific file path to read. If None, searches default paths.
    encoding : str, default="utf-8"
        The file encoding to use when reading the file.
    format_file: str, default=None
        Format to read the file (yaml or json). If None, it will be inferred
        from the file extension.

    Returns
    -------
    dict
        The parsed metadata as a dictionary.
    """
    path = _find_path(path)

    with open(path, "r", encoding=encoding) as file:
        if format_file in {"yaml", "yml"} or \
                (format_file is None and path.lower().endswith((".yml", ".yaml"))):
            try:
                yaml = importlib.import_module("yaml")
                data = yaml.safe_load(file)
            except ImportError as e:
                print("Please install PyYAML or bisslog_schema[yaml] to read YAML files.\n"
                      "pip install bisslog_schema[yaml]\n"
                      "or\n"
                      "pip install pyyaml", file=sys.stderr)
                raise e

        elif format_file == "json" or (format_file is None and path.endswith(".json")):
            data = json.load(file)
        else:
            raise ValueError("Unsupported file format: only YAML or JSON are allowed.")

    return data

def read_service_metadata(path: Optional[str] = None, encoding: str = "utf-8") -> ServiceInfo:
    """Read service metadata from a YAML or JSON file and parse it into a ServiceInfo object.

    If a path is provided, the function validates and reads the file. If no path is given,
    it attempts to find a file from a set of default path options.

    Parameters
    ----------
    path : Optional[str], default=None
        The specific file path to read. If None, searches default paths.
    encoding : str, default="utf-8"
        The file encoding to use when reading the file.

    Returns
    -------
    ServiceInfo
        The parsed service metadata as a ServiceInfo object.

    Raises
    ------
    ValueError
        If the given path does not exist or if no default file is found.
    """
    data = read_metadata_file(path, encoding)

    return ServiceInfo.from_dict(data)
