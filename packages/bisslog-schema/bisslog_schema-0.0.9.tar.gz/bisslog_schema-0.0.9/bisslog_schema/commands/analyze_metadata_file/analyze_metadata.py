"""
Module for analyzing metadata files and generating analysis reports.

This module provides functionality to read metadata files in various formats
(e.g., YAML, JSON) and analyze their contents to produce a `MetadataAnalysisReport`.
"""
from typing import Optional, Dict, Any

import sys

from .metadata_analysis_report import MetadataAnalysisReport
from ...schema.read_metadata import read_metadata_file
from ...schema.service_info import ServiceInfo


def generate_report(path: str, *, format_file: str = "yaml",
                    encoding: str = "utf-8") -> MetadataAnalysisReport:
    """Generate a metadata analysis report from a given file.

    Parameters
    ----------
    path : str
        Path to the metadata file to analyze.
    format_file : str, optional
        Format of the metadata file (default is "yaml").
    encoding : str, optional
        Encoding to use when reading the file (default is "utf-8").

    Returns
    -------
    MetadataAnalysisReport
        The generated analysis report containing validation results.
    """
    data = read_metadata_file(path, format_file=format_file, encoding=encoding)
    return ServiceInfo.analyze(data)

def format_number_to_str(number: float) -> str:
    """Format a float number to a string with minimal decimal places.

    Parameters
    ----------
    number : float
        The number to format.

    Returns
    -------
    str
        The formatted number as a string with:
        - No decimal places if it's an integer after rounding to 2 decimals
        - Trailing zeros and decimal point removed otherwise
    """
    rounded = round(number, 2)
    if rounded.is_integer():
        return str(int(rounded))
    return str(rounded).rstrip('0').rstrip('.')


def print_and_generate_summary(metadata_analysis_report: MetadataAnalysisReport) -> Dict[str, Any]:
    """Print the summary of the metadata analysis report.

    Parameters
    ----------
    metadata_analysis_report : MetadataAnalysisReport
        The metadata analysis report to print.
    """
    n_errors = metadata_analysis_report.critical_errors_count()
    n_warnings = metadata_analysis_report.warning_errors_count()
    total_critical_validations = metadata_analysis_report.total_critical_validations()
    total_warning_validations = metadata_analysis_report.total_warning_validations()

    print("Report of metadata file service")
    print("-" * 80)
    if n_errors > 0:
        print("Errors:")
        metadata_analysis_report.print_errors()
        print("-" * 80)
    if n_warnings > 0:
        print("Warnings:")
        metadata_analysis_report.print_warnings()
        print("-" * 80)

    print(f"Found {n_errors} errors of {total_critical_validations}"
          f" and {n_warnings} warnings of {total_warning_validations}.")
    percentage_warnings = (1 - (n_warnings / total_warning_validations)) * 10 \
        if total_warning_validations > 0 else 10
    msg = "Your metadata file "
    if n_errors > 0:
        msg += "is not OK for production because of critical errors"
        if n_warnings > 0:
            msg += " and "
    if n_warnings > 0:
        msg += f"has been rated at {format_number_to_str(percentage_warnings)}/10 on warnings."

    print(msg)
    return {
        "n_errors": n_errors, "n_warnings": n_warnings,
        "critical_validation_count": total_critical_validations,
        "warning_validation_count": total_warning_validations
    }

def analyze_command(
        path: str, *, format_file: str = "yaml", encoding: str = "utf-8",
        min_warnings: Optional[int] = None) -> MetadataAnalysisReport:
    """Analyze a metadata file and print its contents.

    Parameters
    ----------
    path : str
        The path to the metadata file.
    format_file : str, default="yaml"
        The format of the metadata file (yaml or json).
    encoding : str, default="utf-8"
        The encoding of the metadata file.
    min_warnings : Optional[int], default=None
        The minimum index of warnings to trigger a warning message.
    """
    metadata_analysis_report = generate_report(path, format_file=format_file, encoding=encoding)
    summary = print_and_generate_summary(metadata_analysis_report)
    if summary["n_errors"] > 0:
        sys.exit(1)

    percentage_warnings = ((1 - (summary["n_warnings"] / summary["warning_validation_count"])) *
                           10) if summary["warning_validation_count"] > 0 else 10
    if min_warnings is not None and percentage_warnings < min_warnings:
        sys.exit(1)

    return metadata_analysis_report
