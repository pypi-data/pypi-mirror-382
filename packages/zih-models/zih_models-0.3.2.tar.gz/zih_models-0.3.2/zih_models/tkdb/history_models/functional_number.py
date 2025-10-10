"""Functional number history schema"""

from datetime import datetime
from typing import override

from .base import (
    OU,
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


class FunctionalNumber(BaseSchemaModel):

    telephone_number: TelephoneNumber
    manager_uid: Login
    organizational_unit: OU
    voicemail_user: list[Login]
    unused_since: datetime | None
    category: str | None
    comment: str | None
    dod: str | None

    table = "functional_numbers"

    @override
    def get_user_logins(self) -> set[str]:
        logins = super().get_user_logins()
        logins.update(self.manager_uid, *self.voicemail_user)
        return logins

    @override
    def get_ous(self) -> set[str]:
        ous = super().get_ous()
        ous.add(self.organizational_unit)
        return ous


class FunctionalNumberDiff(BaseDiffSchemaModel):

    organizational_unit: FieldDiff[OU] = None
    voicemail_user: FieldDiff[list[Login]] = None
    unused_since: FieldDiff[datetime | None] = None
    category: FieldDiff[str | None] = None
    comment: FieldDiff[str | None] = None
    dod: FieldDiff[str | None] = None

    table = "functional_numbers"

    @override
    def get_user_logins(self) -> set[str]:
        logins = super().get_user_logins()
        if self.voicemail_user:
            logins.update(*self.voicemail_user.old, *self.voicemail_user.new)
        return logins

    @override
    def get_ous(self) -> set[str]:
        ous = super().get_ous()
        if self.organizational_unit:
            ous.update(
                self.organizational_unit.old, self.organizational_unit.new
            )
        return ous


class FunctionalNumberDelete(BaseDeleteSchemaModel):
    """delete model"""

    table = "functional_numbers"
