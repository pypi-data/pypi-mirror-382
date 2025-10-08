from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

from lqs.interface.dsm.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)


class Announcement(CommonModel):
    datastore_id: Optional[UUID]
    subject: Optional[str]
    content: Optional[str]
    context: Optional[dict]
    status: Optional[str]
    starts_at: Optional[datetime]
    ends_at: Optional[datetime]


class AnnouncementDataResponse(DataResponseModel[Announcement]):
    pass


class AnnouncementListResponse(PaginationModel[Announcement]):
    pass


class AnnouncementCreateRequest(BaseModel):
    datastore_id: Optional[UUID] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    context: Optional[dict] = None
    status: Optional[str] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None


class AnnouncementUpdateRequest(BaseModel):
    datastore_id: Optional[UUID] = optional_field
    subject: Optional[str] = optional_field
    content: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    status: Optional[str] = optional_field
    starts_at: Optional[datetime] = optional_field
    ends_at: Optional[datetime] = optional_field
