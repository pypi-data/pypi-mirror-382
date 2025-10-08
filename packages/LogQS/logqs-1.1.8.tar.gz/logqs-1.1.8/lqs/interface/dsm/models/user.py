from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from lqs.interface.base.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)


class User(CommonModel):
    _repr_fields = ("id", "username")

    username: str
    role_id: Optional[UUID]
    admin: bool
    disabled: bool
    managed: bool
    external_id: Optional[str]
    context: Optional[dict]

    # Profile Fields
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    job_title: Optional[str]
    language: Optional[str]
    time_zone: Optional[str]
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]

    profile_picture: Optional[str]
    freshdesk_contact_id: Optional[int]

    _profile_fields = (
        "first_name",
        "last_name",
        "phone",
        "company",
        "job_title",
        "language",
        "time_zone",
        "address_line_1",
        "address_line_2",
        "city",
        "state",
        "postal_code",
        "country",
    )


class UserInternal(User):
    cognito_id: Optional[str]
    google_id: Optional[str]
    microsoft_id: Optional[str]
    apple_id: Optional[str]
    amazon_id: Optional[str]
    facebook_id: Optional[str]
    linkedin_id: Optional[str]
    github_id: Optional[str]
    stripe_customer_id: Optional[str]

    cookies_accepted_at: Optional[datetime]
    terms_accepted_at: Optional[datetime]
    privacy_accepted_at: Optional[datetime]
    marketing_accepted_at: Optional[datetime]


class UserDataResponse(DataResponseModel[User]):
    pass


class MeDataResponse(DataResponseModel[User]):
    data: Optional[User]


class UserListResponse(PaginationModel[User]):
    pass


class UserCreateRequest(BaseModel):
    username: str
    role_id: Optional[UUID] = None
    admin: bool = False
    disabled: bool = False
    managed: bool = False
    external_id: Optional[str] = None
    password: Optional[str] = None  # note: this is virtual
    context: Optional[dict] = None

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    language: Optional[str] = None
    time_zone: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class UserUpdateRequest(BaseModel):
    username: str = optional_field
    role_id: Optional[UUID] = optional_field
    admin: bool = optional_field
    disabled: bool = optional_field
    external_id: Optional[str] = optional_field
    password: Optional[str] = optional_field  # note: this is virtual
    context: Optional[dict] = optional_field

    first_name: Optional[str] = optional_field
    last_name: Optional[str] = optional_field
    phone: Optional[str] = optional_field
    company: Optional[str] = optional_field
    job_title: Optional[str] = optional_field
    language: Optional[str] = optional_field
    time_zone: Optional[str] = optional_field
    address_line_1: Optional[str] = optional_field
    address_line_2: Optional[str] = optional_field
    city: Optional[str] = optional_field
    state: Optional[str] = optional_field
    postal_code: Optional[str] = optional_field
    country: Optional[str] = optional_field
