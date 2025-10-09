"""
Module providing the BaseObjSchema class for schema validation.

This module defines the BaseObjSchema class, which includes utility methods
for validating various types of fields, such as strings, booleans, and integers.
These methods ensure that the fields meet the required constraints and provide
consistent error handling across schema classes.
"""
from abc import ABCMeta
from typing import Optional


class BaseObjSchema(metaclass=ABCMeta):
    """Base class for all schema classes."""

    @staticmethod
    def _validate_optional_str_field(field_name: str, value: Optional[str]) -> Optional[str]:
        """
        Validate the optional string field.

        Parameters
        ----------
        field_name: str
            The field name to validate.
        value : Optional[str]
            The service type value to validate.

        Returns
        -------
        Optional[str]
            The validated service type value.

        Raises
        ------
        ValueError
            If the service type is not a string.
        """

        if value is not None and (not isinstance(value, str) or not value):
            raise ValueError(f"The '{field_name}' field must be a string if provided.")
        return value

    @staticmethod
    def _validate_required_str_field(field_name: str, value: Optional[str]) -> str:
        """
        Validate the required string field.

        Parameters
        ----------
        field_name: str
            The field name to validate.
        value : Optional[str]
            The service type value to validate.

        Returns
        -------
        str
            The validated service type value.

        Raises
        ------
        ValueError
            If the service type is not a string or its none-empty.
        """

        if value is None:
            raise ValueError(f"The '{field_name}' field is required and must be a string.")
        if not isinstance(value, str):
            raise TypeError(f"The '{field_name}' must be a string.")
        if not value:
            raise ValueError(f"The '{field_name}' field is required and must "
                             f"be a non-empty string.")
        return value

    @staticmethod
    def _validate_boolean_field(field_name: str, value: Optional[bool]) -> bool:
        """
        Validate the optional boolean field.

        Parameters
        ----------
        field_name: str
            The field name to validate.
        value : Optional[bool]
            The service type value to validate.

        Returns
        -------
        bool
            The validated service type value.

        Raises
        ------
        ValueError
            If the service type is not a string.
        """
        if value is not None and not isinstance(value, bool):
            raise ValueError(f"The '{field_name}' field must be a boolean if provided.")
        return value or False

    @staticmethod
    def _validate_optional_int_field(
            field_name: str, value: Optional[int], lower_limit: Optional[int] = None,
            upper_limit:  Optional[int] = None) -> Optional[int]:
        """
        Validate the optional integer field.

        Parameters
        ----------
        field_name: str
            The field name to validate.
        value : Optional[int]
            The service type value to validate.
        lower_limit : Optional[int]
            The lower limit for the integer value.
        upper_limit : Optional[int]
            The upper limit for the integer value.

        Returns
        -------
        Optional[int]
            The validated service type value.

        Raises
        ------
        ValueError
            If the service type is not a string.
        """
        if value is not None:
            if isinstance(value, str) and value.isdigit():
                value = int(value)

            if not isinstance(value, int):
                raise ValueError(f"The '{field_name}' field must be a integer if provided.")
            if lower_limit is not None and value < lower_limit:
                raise ValueError(f"The '{field_name}' field must be greater"
                                 f" or equal than {lower_limit}")
            if upper_limit is not None and value > upper_limit:
                raise ValueError(f"The '{field_name}' field must be less or "
                                 f"equal than {upper_limit}")

        return value
