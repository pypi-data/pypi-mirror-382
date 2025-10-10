"""User history schema"""

from typing import override

from .base import (
    BaseDeleteSchemaModel,
    BaseDiffSchemaModel,
    BaseSchemaModel,
    FieldDiff,
    FunctionalNumber,
    Login,
    PersonalNumber,
)

"""
!!! NEVER Change the type of a Column/Attribute of this models so the history never breaks !!!
"""


class User(BaseSchemaModel):

    uid: Login
    personal_numbers: list[PersonalNumber]
    functional_numbers: list[FunctionalNumber]

    table = "users_v2"

    @override
    def get_user_logins(self) -> set[str]:
        logins = super().get_user_logins()
        logins.add(self.uid)
        return logins


class UserDiff(BaseDiffSchemaModel):

    personal_numbers: FieldDiff[list[PersonalNumber]] = None
    functional_numbers: FieldDiff[list[FunctionalNumber]] = None

    table = "users_v2"


class UserDelete(BaseDeleteSchemaModel):
    """delete model"""

    table = "users_v2"
