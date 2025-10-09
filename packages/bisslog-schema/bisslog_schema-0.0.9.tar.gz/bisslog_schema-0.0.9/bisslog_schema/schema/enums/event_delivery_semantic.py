"""
Defines event delivery semantics used across the application.
"""

from enum import Enum
from typing import Optional

_value_to_member_map_ = {}


class EventDeliverySemantic(Enum):
    """Defines the delivery semantics for event transmission.

    Attributes
    ----------
    AT_MOST_ONCE : EventDeliverySemantic
        Events are delivered at most once, without retries in case of failure.
    AT_LEAST_ONCE : EventDeliverySemantic
        Events are delivered at least once, allowing possible duplicates.
    EXACTLY_ONCE : EventDeliverySemantic
        Events are delivered exactly once, ensuring no duplication or loss.
    """

    AT_MOST_ONCE = "at-most-once"
    AT_LEAST_ONCE = "at-least-once"
    EXACTLY_ONCE = "exactly-once"

    def __new__(cls, value):
        obj = object.__new__(cls)
        obj.val = value
        _value_to_member_map_[value] = obj
        return obj

    @classmethod
    def from_value(cls, value: str) -> Optional["EventDeliverySemantic"]:
        """Returns the corresponding EventDeliverySemantic member for a given value.

        Parameters
        ----------
        value : str
            The string representation of the delivery semantic.

        Returns
        -------
        EventDeliverySemantic
            The corresponding enumeration member.

        Raises
        ------
        ValueError
            If no matching EventDeliverySemantic is found.
        """
        return _value_to_member_map_.get(value)
