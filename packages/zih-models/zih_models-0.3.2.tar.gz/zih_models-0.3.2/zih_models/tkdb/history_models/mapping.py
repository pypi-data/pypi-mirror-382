"""Version mappings"""

from typing import TypedDict

from .base import (
    TABLE,
    BaseDeleteSchemaModel,
    BaseDiffSchemaModel,
    BaseSchemaModel,
)
from .external_number import (
    ExternalNumber,
    ExternalNumberDelete,
    ExternalNumberDiff,
)
from .functional_number import (
    FunctionalNumber,
    FunctionalNumberDelete,
    FunctionalNumberDiff,
)
from .personal_number import (
    PersonalNumber,
    PersonalNumberDelete,
    PersonalNumberDiff,
)
from .telephone_number import (
    TelephoneNumber,
    TelephoneNumberDelete,
    TelephoneNumberDiff,
)
from .user import User, UserDelete, UserDiff


class TypeEntries(TypedDict):
    simple: type[BaseSchemaModel]
    diff: type[BaseDiffSchemaModel]
    deleted: type[BaseDeleteSchemaModel]


mapping: dict[TABLE, TypeEntries] = {
    "functional_numbers": {
        "simple": FunctionalNumber,
        "diff": FunctionalNumberDiff,
        "deleted": FunctionalNumberDelete,
    },
    "personal_numbers": {
        "simple": PersonalNumber,
        "diff": PersonalNumberDiff,
        "deleted": PersonalNumberDelete,
    },
    "users_v2": {"simple": User, "diff": UserDiff, "deleted": UserDelete},
    "phone_numbers_v2": {
        "simple": TelephoneNumber,
        "diff": TelephoneNumberDiff,
        "deleted": TelephoneNumberDelete,
    },
    "external_numbers": {
        "simple": ExternalNumber,
        "diff": ExternalNumberDiff,
        "deleted": ExternalNumberDelete,
    },
}
