"""Personal number history schema"""

from datetime import datetime
from typing import override

from .base import (
    BaseDeleteSchemaModel,
    BaseDiffSchemaModel,
    BaseSchemaModel,
    FieldDiff,
    Login,
    TelephoneNumber,
)

"""
!!! NEVER Change the type of a Column/Attribute of this models so the history never breaks !!!
"""


class PersonalNumber(BaseSchemaModel):

    telephone_number: TelephoneNumber
    user_common_name: Login
    primary: bool
    voicemail: bool
    unused_since: datetime | None
    comment: str | None
    dod: str | None

    table = "personal_numbers"

    @override
    def get_user_logins(self) -> set[str]:
        logins = super().get_user_logins()
        logins.add(self.user_common_name)
        return logins


class PersonalNumberDiff(BaseDiffSchemaModel):

    primary: FieldDiff[bool] = None
    voicemail: FieldDiff[bool] = None
    unused_since: FieldDiff[datetime | None] = None
    comment: FieldDiff[str | None] = None
    dod: FieldDiff[str | None] = None

    table = "personal_numbers"


class PersonalNumberDelete(BaseDeleteSchemaModel):
    """delete model"""

    table = "personal_numbers"
