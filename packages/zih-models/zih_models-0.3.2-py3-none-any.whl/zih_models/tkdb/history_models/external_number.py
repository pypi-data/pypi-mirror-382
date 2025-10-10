"""External number history schema"""

from datetime import datetime

from .base import (
    BaseDeleteSchemaModel,
    BaseDiffSchemaModel,
    BaseSchemaModel,
    FieldDiff,
    TelephoneNumber,
)

"""
!!! NEVER Change the type of a Column/Attribute of this models so the history never breaks !!!
"""


class ExternalNumber(BaseSchemaModel):

    telephone_number: TelephoneNumber
    organization: str
    unused_since: datetime | None
    comment: str | None
    dod: str | None

    table = "external_numbers"


class ExternalNumberDiff(BaseDiffSchemaModel):

    unused_since: FieldDiff[datetime | None] = None
    comment: FieldDiff[str | None] = None
    dod: FieldDiff[str | None] = None

    table = "external_numbers"


class ExternalNumberDelete(BaseDeleteSchemaModel):
    """delete model"""

    table = "external_numbers"
