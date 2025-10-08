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


class APIKey(CommonModel["APIKey"]):
    name: str = Field(..., description="Name of the API key for reference.")
    user_id: UUID = Field(
        ..., description="The ID of the user to which the API key belongs."
    )
    disabled: bool = Field(
        ..., description="Whether the API key is disabled and cannot be used."
    )
    secret: Optional[str] = Field(
        None,
        description="The secret key for the API key. This is only returned when the API key is created.",
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(["secret"])
    )

    def fetch_user(self) -> "models.User":
        return self._app.fetch.user(self.user_id).data


class APIKeyDataResponse(DataResponseModel[APIKey]):
    pass


class APIKeyListResponse(PaginationModel[APIKey]):
    pass


class APIKeyCreateRequest(BaseModel):
    name: str
    user_id: UUID
    disabled: bool = False


class APIKeyUpdateRequest(BaseModel):
    name: str = optional_field
    disabled: bool = optional_field
