"""
Module defining the CriticalityEnum enum and associated methods for handling criticality levels.
"""
from enum import Enum
from typing import Optional


class CriticalityEnum(Enum):
    """Enumeration of criticality levels, with associated integer values.

    Members
    -------
    NONE : 0
       Represents no criticality.
    VERY_LOW : 10
       Represents very low criticality.
    LOW : 20
       Represents low criticality.
    MEDIUM : 50
       Represents medium criticality.
    HIGH : 70
       Represents high criticality.
    VERY_HIGH : 90
       Represents very high criticality.
    CRITICAL : 100
       Represents critical level of criticality."""

    NONE = 0
    VERY_LOW = 10
    LOW = 20
    MEDIUM = 50
    HIGH = 70
    VERY_HIGH = 90
    CRITICAL = 100

    @classmethod
    def get_from_int_val(cls, val: int) -> Optional["CriticalityEnum"]:
        """Retrieves the CriticalityEnum member corresponding to the provided integer value.
        This method caches the results for faster lookups on subsequent calls.

        Parameters
        ----------
        val : int
            The integer value representing the criticality level.

        Returns
        -------
        Optional[CriticalityEnum]
            The corresponding CriticalityEnum member, or None if no matching value is found."""

        if hasattr(cls, "_cache_val"):
            return cls._cache_val.get(val)
        new_cache = {}
        for member in cls.__members__.values():
            new_cache[member.value] = member
        cls._cache_val = new_cache
        return new_cache.get(val)
