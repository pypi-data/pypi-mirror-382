import datetime as dt
from typing import Literal

import pydantic
from pydantic import ConfigDict

from ..utils import File


def to_camel(snake_str: str) -> str:
    first, *others = snake_str.split("_")
    ret = "".join([first.lower(), *map(str.title, others)])
    return ret


class BaseAPIModel(pydantic.BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True, alias_generator=to_camel, populate_by_name=True
    )

    def model_dump(self, **kwargs):
        """Returns camelCased version and removes any non specified optional fields"""
        return super().model_dump(by_alias=True, exclude_unset=True)


class PatchAssetInput(BaseAPIModel):
    category: str | None = None
    code: str | None = None
    photo: File | str | None = None
    make: str | None = None
    model: str | None = None
    size: str | None = None
    location: str | None = None
    status: str | None = None
    condition: str | None = None
    installation_timestamp: dt.datetime | None = None
    expected_life_years: dt.datetime | None = None


class PatchRemarkInput(BaseAPIModel):
    resolved_timestamp: dt.datetime | None = None
    description: str | None = None
    severity: str | None = None
    resolution: str | None = None


class PatchServiceInput(BaseAPIModel):
    name: str | None = None
    due_date: dt.date | None = None
    performed_timestamp: dt.datetime | None = None
    description: str | None = None
    result: str | None = None


class PatchTenantDocumentInput(BaseAPIModel):
    title: str | None = None


class PushContractorInput(BaseAPIModel):
    name: str
    website: str | None = None
    about_us: str | None = None
    industries: list[
        Literal["FIRE", "SECURITY", "MECHANICAL", "ELECTRICAL", "PLUMBING", "ELEVATORS"]
    ]
    services_provided: list[
        Literal[
            "INSPECTION_AND_TESTING",
            "REPAIRS",
            "MAJOR_WORKS",
            "ESM_AUDITING",
            "ANNUAL_CERTIFICATION",
        ]
    ]
    service_areas: str | None = None
    country: Literal["AU", "NZ", "GB", "CA", "US", "IE"]
    business_number: str
    address: str
    email: str
    phone: str
    is_active: bool | None = True
    logo: File | None = None
