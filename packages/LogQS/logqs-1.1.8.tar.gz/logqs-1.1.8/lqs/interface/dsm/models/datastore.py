from uuid import UUID
from typing import Optional

from pydantic import BaseModel

from lqs.interface.dsm.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)


class DataStore(CommonModel):
    name: str
    note: Optional[str]
    context: Optional[dict]
    owner_id: Optional[UUID]
    config: Optional[dict]
    version: Optional[str]
    region: Optional[str]
    endpoint: Optional[str]
    disabled: bool
    plan: Optional[str]
    record_count: int


class DataStoreInternal(DataStore):
    stripe_subscription_id: Optional[str]


class DataStoreDataResponse(DataResponseModel[DataStore]):
    pass


class DataStoreListResponse(PaginationModel[DataStore]):
    pass


class DataStoreCreateRequest(BaseModel):
    name: str
    note: Optional[str] = None
    context: Optional[dict] = None
    owner_id: Optional[UUID] = None
    config: Optional[dict] = None
    version: Optional[str] = None
    region: Optional[str] = None
    endpoint: Optional[str] = None
    disabled: bool = False


class DataStoreUpdateRequest(BaseModel):
    name: str = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    owner_id: Optional[UUID] = optional_field
    config: Optional[dict] = optional_field
    version: Optional[str] = optional_field
    region: Optional[str] = optional_field
    endpoint: Optional[str] = optional_field
    disabled: bool = optional_field
