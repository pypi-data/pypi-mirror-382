"""
This module defines an enumeration representing various types of external
interactions within a ports and adapters (hexagonal) architecture.
"""
from enum import Enum
from typing import Optional, Tuple

_value_to_member_map_ = {}


class TypeExternalInteraction(Enum):
    """Enumeration that represents different types of external interactions
    a system might perform, such as accessing a database, notifying
    another service, or interacting with an external file system.

    Each enum member is defined with a primary identifier and a tuple of aliases
    that can be used for matching input strings to the appropriate member."""
    DATABASE = "database", ("db", "repository")
    NOTIFIER = "notifier", ("notif",)
    EXTERNAL_FILE_SYSTEM = "external_file_system", ("sftp", "ssh")
    PUBLISHER = "publisher", ("pub", "pubsub", "pub/sub")
    EXTERNAL_SYSTEM = "external_system", ("service",)

    UNKNOWN = "unknown", ("unknown",)


    def __init__(self, main_identifier: str, aliases: Tuple[str]):
        self.main_identifier = main_identifier
        self.aliases = aliases

    @staticmethod
    def from_str(value: str) -> Optional["TypeExternalInteraction"]:
        """Converts from string to TypeExternalInteraction

        Parameters
        ----------
        value: str
            String value to get the member

        Returns
        -------
        TypeExternalInteraction"""
        for trigger in TypeExternalInteraction:
            if trigger.main_identifier == value:
                return trigger
            if value in trigger.aliases:
                return trigger
        return None
