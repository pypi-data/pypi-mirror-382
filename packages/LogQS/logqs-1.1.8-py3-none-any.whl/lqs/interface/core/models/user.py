from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.base.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)
from lqs.interface.core import models


class User(CommonModel):
    _repr_fields = ("id", "username")

    username: str = Field(..., description="Username of the user.")
    role_id: Optional[UUID] = Field(
        None, description="The ID of the role associated with the user."
    )
    admin: bool = Field(..., description="Whether the user has admin privileges.")
    disabled: bool = Field(..., description="Whether the user is disabled.")
    managed: bool = Field(..., description="Whether the user is managed by the system.")
    external_id: Optional[str] = Field(
        None, description="Arbitrary External ID for the user for reference."
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(["role_id", "external_id"])
    )

    def fetch_role(self) -> Optional["models.Role"]:
        if self.role_id is None:
            return None
        return self._app.fetch.role(self.role_id).data

    def list_api_keys(self) -> "models.APIKeyListResponse":
        return self._app.fetch.api_keys(user_id=self.id)


class UserDataResponse(BaseModel):
    data: User


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


class UserUpdateRequest(BaseModel):
    username: str = optional_field
    role_id: Optional[UUID] = optional_field
    admin: bool = optional_field
    disabled: bool = optional_field
    external_id: Optional[str] = optional_field
    password: Optional[str] = optional_field  # note: this is virtual
