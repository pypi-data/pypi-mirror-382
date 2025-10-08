from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.base.models.__common__ import (
    ResourceModel,
    UploadState,
)


class Object(ResourceModel["Object"]):
    _repr_fields = ("key",)

    key: str = Field(
        ...,
        description="The key of the object (i.e., the path within the object store).",
    )
    etag: Optional[str] = Field(
        None, description="The ETag of the object, used for integrity checks."
    )
    size: Optional[int] = Field(None, description="The size of the object in bytes.")
    last_modified: Optional[datetime] = Field(
        None, description="The last modified timestamp of the object."
    )
    presigned_url: Optional[str] = Field(
        None, description="The presigned URL for fetching the object data."
    )
    upload_state: UploadState = Field(
        ..., description="The upload state of the object."
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            [
                "etag",
                "size",
                "last_modified",
                "presigned_url",
            ]
        )
    )


class ObjectDataResponse(BaseModel):
    data: Object


class ObjectListResponse(BaseModel):
    data: List[Object]
    is_truncated: Optional[bool]
    key_count: Optional[int]
    max_keys: int

    continuation_token: Optional[str]
    next_continuation_token: Optional[str]
    prefix: Optional[str]
    start_after: Optional[str]
    delimiter: Optional[str]
    common_prefixes: Optional[List[str]]


class ObjectCreateRequest(BaseModel):
    key: str
    content_type: Optional[str] = None


class ObjectUpdateRequest(BaseModel):
    upload_state: UploadState


# Object Parts


class ObjectPart(BaseModel):
    part_number: int
    etag: str
    size: int
    last_modified: Optional[datetime]
    presigned_url: Optional[str]


class ObjectPartDataResponse(BaseModel):
    data: ObjectPart


class ObjectPartListResponse(BaseModel):
    data: List[ObjectPart]
    part_number_marker: Optional[int]
    next_part_number_marker: Optional[int]
    max_parts: Optional[int]
    is_truncated: Optional[bool]


class ObjectPartCreateRequest(BaseModel):
    part_number: Optional[int] = None
    size: int
