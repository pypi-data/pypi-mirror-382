from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.base.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)


class APIKey(CommonModel["APIKey"]):
    name: str
    user_id: UUID
    disabled: bool
    secret: Optional[str]


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
