# SPDX-License-Identifier: MIT

"""models for the sharepoint api"""

from enum import IntEnum, StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class SharepointNotFoundError(BaseModel):
    """Return of the api if target not found"""

    detail: Literal["Not Found"] = "Not Found"


class SiteType(StrEnum):
    """possible types of a site"""

    DEFAULT = "default"
    PROJECT = "project"


class Site(BaseModel):
    """Sharepoint Site"""

    SiteUrl: str
    SiteId: str
    Admin1: str | None = None
    Admin2: str | None = None


class Language(StrEnum):
    """site language"""

    GERMAN = "de"
    ENGLISH = "en"


class SharepointLanguageCodes(IntEnum):
    """sharepoint language codes"""

    GERMAN = 1031
    ENGLISH = 1033


LanguageMapper = {
    Language.GERMAN: SharepointLanguageCodes.GERMAN,
    Language.ENGLISH: SharepointLanguageCodes.ENGLISH,
}

LanguageMapperLogList = {
    Language.GERMAN: "Deutsch (Deutschland)",
    Language.ENGLISH: "Englisch (USA)",
}


class PrivacyLevel(StrEnum):
    """privacy level of site"""

    NORMAL = "normal"
    HIGH = "high"


class User(BaseModel):
    """User Object with all Infos Sharepoint needs"""

    login: str
    mail: str


class CreateSiteData(BaseModel):
    """Sharepoint Site data which is used to create a new Site"""

    applicant: User
    head: User
    it_referent: User
    ticket_number: str
    org_id: str
    site_name: str
    url_name: Annotated[str, Field(max_length=10)]
    site_type: SiteType
    purpose: str
    site_language: Language
    privacy_level: PrivacyLevel
    admins: Annotated[list[User], Field(min_length=2, max_length=2)]
