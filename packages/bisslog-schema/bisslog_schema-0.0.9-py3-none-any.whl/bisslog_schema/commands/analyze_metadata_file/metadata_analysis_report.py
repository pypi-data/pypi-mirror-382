"""Class to represent an analysis report."""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class MetadataAnalysisReport:
    """
    Class to represent an analysis report.

    Attributes
    ----------
    critical_validation_count : int
        The number of critical validation issues found during the analysis.
    warning_validation_count : int
        The number of warning validation issues found during the analysis.
    errors : List[str]
        A list of error messages encountered during the analysis.
    warnings : List[str]
        A list of warning messages encountered during the analysis.
    sub_reports : List[MetadataAnalysisReport]
        A list of sub-reports generated as part of the analysis.
    """
    critical_validation_count: int
    warning_validation_count: int
    errors: List[str]
    warnings: List[str]
    sub_reports: Dict[str, List['MetadataAnalysisReport']]

    def print_errors(self) -> None:
        """Prints all error messages, including those from sub-reports."""
        for error in self.errors:
            print(error)

        for sub_reports in self.sub_reports.values():
            for sub_report in sub_reports:
                sub_report.print_errors()

    def print_warnings(self) -> None:
        """Prints all warning messages, including those from sub-reports."""
        for warning in self.warnings:
            print(warning)

        for sub_reports in self.sub_reports.values():
            for sub_report in sub_reports:
                sub_report.print_warnings()

    def total_critical_validations(self) -> int:
        """Calculates the total number of critical validations, including sub-reports.

        Returns
        -------
        int
            The total number of critical validations."""
        n = self.critical_validation_count
        for sub_reports in self.sub_reports.values():
            for sub_report in sub_reports:
                n += sub_report.total_critical_validations()
        return n

    def total_warning_validations(self) -> int:
        """Calculates the total number of warning validations, including sub-reports.

        Returns
        -------
        int
            The total number of warning validations."""
        n = self.warning_validation_count
        for sub_reports in self.sub_reports.values():
            for sub_report in sub_reports:
                n += sub_report.total_warning_validations()
        return n

    def critical_errors_count(self) -> int:
        """Counts the total number of critical errors, including sub-reports.

        Returns
        -------
        int
            The total number of critical errors."""
        n = len(self.errors)
        for sub_reports in self.sub_reports.values():
            for sub_report in sub_reports:
                n += sub_report.critical_errors_count()
        return n

    def warning_errors_count(self) -> int:
        """Counts the total number of warning errors, including sub-reports.

        Returns
        -------
        int
            The total number of warning errors."""
        n = len(self.warnings)
        for sub_reports in self.sub_reports.values():
            for sub_report in sub_reports:
                n += sub_report.warning_errors_count()
        return n
