from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.dsm.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)


class Comment(CommonModel):
    user_id: Optional[UUID]
    datastore_id: Optional[UUID]
    resource_type: Optional[str]
    resource_id: Optional[UUID]

    subject: Optional[str]
    content: Optional[str]
    context: Optional[dict]
    status: Optional[str]


class CommentDataResponse(DataResponseModel[Comment]):
    pass


class CommentListResponse(PaginationModel[Comment]):
    pass


class CommentCreateRequest(BaseModel):
    user_id: Optional[UUID] = None
    datastore_id: Optional[UUID] = None
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None

    subject: Optional[str] = None
    content: Optional[str] = None
    context: Optional[dict] = None


class CommentUpdateRequest(BaseModel):
    user_id: Optional[UUID] = optional_field
    datastore_id: Optional[UUID] = optional_field
    resource_type: Optional[str] = optional_field
    resource_id: Optional[UUID] = optional_field

    subject: Optional[str] = optional_field
    content: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    status: Optional[str] = optional_field
