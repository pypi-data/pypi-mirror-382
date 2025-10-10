from .base import BaseSchemaModel, FieldDiffObject
from .external_number import ExternalNumber as ExternalNumberHistorySchema
from .external_number import (
    ExternalNumberDelete as ExternalNumberDeleteHistorySchema,
)
from .external_number import (
    ExternalNumberDiff as ExternalNumberDiffHistorySchema,
)
from .functional_number import (
    FunctionalNumber as FunctionalNumberHistorySchema,
)
from .functional_number import (
    FunctionalNumberDelete as FunctionalNumberDeleteHistorySchema,
)
from .functional_number import (
    FunctionalNumberDiff as FunctionalNumberDiffHistorySchema,
)
from .personal_number import PersonalNumber as PersonalNumberHistorySchema
from .personal_number import (
    PersonalNumberDelete as PersonalNumberDeleteHistorySchema,
)
from .personal_number import (
    PersonalNumberDiff as PersonalNumberDiffHistorySchema,
)
from .telephone_number import TelephoneNumber as TelephoneNumberHistorySchema
from .telephone_number import (
    TelephoneNumberDiff as TelephoneNumberDiffHistorySchema,
)
from .user import User as UserHistorySchema
from .user import UserDiff as UserDiffHistorySchema

__all__ = [
    "BaseSchemaModel",
    "FieldDiffObject",
    "ExternalNumberHistorySchema",
    "ExternalNumberDiffHistorySchema",
    "ExternalNumberDeleteHistorySchema",
    "FunctionalNumberHistorySchema",
    "FunctionalNumberDeleteHistorySchema",
    "FunctionalNumberDiffHistorySchema",
    "PersonalNumberHistorySchema",
    "PersonalNumberDeleteHistorySchema",
    "PersonalNumberDiffHistorySchema",
    "TelephoneNumberHistorySchema",
    "TelephoneNumberDiffHistorySchema",
    "UserHistorySchema",
    "UserDiffHistorySchema",
]
