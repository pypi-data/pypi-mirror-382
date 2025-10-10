"""Telephone number history schema"""

from zih_models.tkdb.types import PhoneNumberType

from .base import (
    BaseDeleteSchemaModel,
    BaseDiffSchemaModel,
    BaseSchemaModel,
    FieldDiff,
)

"""
!!! NEVER Change the type of a Column/Attribute of this models so the history never breaks !!!
"""


class TelephoneNumber(BaseSchemaModel):

    telephone_number: str
    telephone_type: PhoneNumberType
    partition: str | None
    assignment: str | None
    use: str | None
    comment: str | None

    table = "phone_numbers_v2"


class TelephoneNumberDiff(BaseDiffSchemaModel):

    telephone_type: FieldDiff[PhoneNumberType] = None
    partition: FieldDiff[str | None] = None
    assignment: FieldDiff[str | None] = None
    use: FieldDiff[str | None] = None
    comment: FieldDiff[str | None] = None

    table = "phone_numbers_v2"


class TelephoneNumberDelete(BaseDeleteSchemaModel):
    """delete model"""

    table = "phone_numbers_v2"
