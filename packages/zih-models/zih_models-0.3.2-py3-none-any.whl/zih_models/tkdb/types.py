from enum import StrEnum


class PhoneNumberType(StrEnum):
    """all possible types for a phone number"""

    PERSONAL = "personal"
    FUNCTIONAL = "functional"
    EXTERNAL = "external"
    BLOCKED = "blocked"
    LEGACY = "legacy"
