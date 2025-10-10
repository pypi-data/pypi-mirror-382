"""base helper things for all schemas"""

from enum import StrEnum
from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, Field


class ChangeAction(StrEnum):

    CREATED = "created"
    DELETED = "deleted"
    MODIFIED = "modified"


class FieldDiffObject[T](BaseModel):
    old: T
    new: T


type FieldDiff[T] = FieldDiffObject[T] | None

TABLE = Literal[
    "functional_numbers",
    "phone_numbers_v2",
    "personal_numbers",
    "users_v2",
    "external_numbers",
]


class UIDisplaySpecials(StrEnum):
    USER = "user"
    OU = "ou"
    TELEPHONE_NUMBER_LINK = "telephone_number_link"
    PERSONAL_NUMBER_LINK = "personal_number_link"
    FUNCTIONAL_NUMBER_LINK = "functional_number_link"


Login = Annotated[
    str, Field(json_schema_extra={"ui_display": UIDisplaySpecials.USER})
]
OU = Annotated[
    str, Field(json_schema_extra={"ui_display": UIDisplaySpecials.OU})
]
TelephoneNumber = Annotated[
    str,
    Field(
        json_schema_extra={
            "ui_display": UIDisplaySpecials.TELEPHONE_NUMBER_LINK
        }
    ),
]
PersonalNumber = Annotated[
    str,
    Field(
        json_schema_extra={
            "ui_display": UIDisplaySpecials.PERSONAL_NUMBER_LINK
        }
    ),
]
FunctionalNumber = Annotated[
    str,
    Field(
        json_schema_extra={
            "ui_display": UIDisplaySpecials.FUNCTIONAL_NUMBER_LINK
        }
    ),
]


class BaseSchemaModel(BaseModel):
    """Base model with table classvar"""

    table: ClassVar[TABLE]
    action: ClassVar[ChangeAction] = ChangeAction.CREATED

    def get_user_logins(self) -> set[str]:
        return set()

    def get_ous(self) -> set[str]:
        return set()


class BaseDiffSchemaModel(BaseSchemaModel):
    """base for all diff models"""

    action: ClassVar[ChangeAction] = ChangeAction.MODIFIED

    def has_changes(self) -> bool:
        for field in type(self).model_fields:
            if getattr(self, field) is not None:
                return True
        return False


class BaseDeleteSchemaModel(BaseSchemaModel):
    """base for all delete models"""

    action: ClassVar[ChangeAction] = ChangeAction.DELETED
