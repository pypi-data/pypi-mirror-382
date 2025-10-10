"""models for api"""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Self

from pydantic import BaseModel, Field, model_validator

from zih_models.tkdb.types import PhoneNumberType

from .history_models.base import TABLE, BaseSchemaModel, ChangeAction

TelephoneNumber = Annotated[
    str,
    Field(
        pattern=r"^\+49-\d{1,3}-\d{0,8}-\d{1,12}$",
        examples=[
            "+49-351-463-40000",
            "+49-351-463-50000",
            "+49-351-463-60000",
        ],
    ),
]


class FunctionalPhoneNumber(BaseModel):
    """FunctionalPhone with base information"""

    telephone_number: str
    organizational_unit: str


class FunctionalPhoneNumberWithDetails(FunctionalPhoneNumber):
    """FunctionalPhone with all information for a detailed view"""

    voicemail_user: list[str]
    comment: str | None = None
    category_id: int | None = None
    dod_id: int | None
    created: datetime
    last_modified: datetime
    unused_since: datetime | None


class FunctionalPhoneNumberWrite(FunctionalPhoneNumber):
    """FunctionalPhone with all optional write arguments"""

    telephone_number: TelephoneNumber
    voicemail_user: list[str] | None = None
    comment: str | None = None
    category_id: int | None = None
    dod_id: int


class PersonalPhoneNumberWithDetails(BaseModel):
    telephone_number: str
    comment: str | None = None
    dod_id: int | None
    voicemail: bool
    created: datetime
    last_modified: datetime
    unused_since: datetime | None


class PersonalPhoneNumberWrite(BaseModel):
    telephone_number: TelephoneNumber
    comment: str | None
    voicemail: bool = False
    dod_id: int


class PhoneNumberAssignmentsBase(BaseModel):
    """PhoneNumberAssignments Base class"""

    ipPhone: str | None
    otherIpPhone: list[str]


class PhoneNumberAssignmentsWrite(BaseModel):
    """PhoneNumberAssignments without common_name to write to api and more validation"""

    ipPhone: PersonalPhoneNumberWrite | None
    otherIpPhone: list[PersonalPhoneNumberWrite]
    managerOfPhone: list[FunctionalPhoneNumberWrite]

    @model_validator(mode="after")
    def validate_primary(self) -> Self:
        """validate that ipPhone is required if you want to set otherIpPhones"""
        if self.otherIpPhone and self.ipPhone is None:
            raise ValueError(
                "ipPhone is required if you want to set otherIpPhones"
            )
        return self

    @model_validator(mode="after")
    def check_unique_telephone_number_across_attributes(self) -> Self:
        """validate that ipPhone, otherIpPhones and managerOfPhone dont have duplicated telephone_numbers"""
        personal_numbers: list[
            PersonalPhoneNumberWrite | FunctionalPhoneNumberWrite
        ] = ([self.ipPhone, *self.otherIpPhone] if self.ipPhone else [])
        all_numbers = [
            item.telephone_number
            for item in personal_numbers + self.managerOfPhone
        ]
        if len(all_numbers) != len(set(all_numbers)):
            raise ValueError(
                "Telephone numbers must be unique across ipPhone, otherIpPhones and managerOfPhone."
            )
        return self


class PhoneNumberAssignments(PhoneNumberAssignmentsBase):
    """PhoneNumberAssignments return for api"""

    common_name: str
    managerOfPhone: list[FunctionalPhoneNumber]

    @property
    def telephone_numbers(self) -> list[str]:
        """return all telephone numbers of user. (no numbers where the user is manager)"""
        return (
            [
                self.ipPhone,
                *self.otherIpPhone,
            ]
            if self.ipPhone is not None
            else self.otherIpPhone
        )


class PhoneNumberAssignmentsWithDetails(BaseModel):
    """PhoneNumberAssignments return for api"""

    common_name: str
    ipPhone: PersonalPhoneNumberWithDetails | None
    otherIpPhone: list[PersonalPhoneNumberWithDetails]
    managerOfPhone: list[FunctionalPhoneNumberWithDetails]


class HistoryEntry[
    T: (dict[str, Any], BaseSchemaModel) = dict[str, Any],
    TAction: ChangeAction = ChangeAction,
](BaseModel):

    subject: str | None
    source: str
    timestamp: datetime
    entity_type: TABLE
    entity_identifier: str
    action: TAction
    data: T


class NewPrimaryBody(BaseModel):

    telephone_number: TelephoneNumber


class PhoneNumberDetails(BaseModel):

    id: int
    number: str
    prefix: str
    dial_up: str
    extension: str
    type: PhoneNumberType
    use_id: int | None
    comment: str | None
    assignment: str | None
    partition: str | None
    isdn_system: int | None
    isdn_port: str | None


class PhoneNumbersResponse(BaseModel):

    items: list[PhoneNumberDetails]
    total: int


class AllowedTelephoneFilterFields(StrEnum):
    ID = "id"
    NUMBER = "number"
    PREFIX = "prefix"
    DIAL_UP = "dial_up"
    EXTENSION = "extension"
    TYPE = "type"
    USE_ID = "use_id"
    COMMENT = "comment"
    ASSIGNMENT = "assignment"
    PARTITION = "partition"
    ISDN_SYSTEM = "isdn_system"
    ISDN_PORT = "isdn_port"
