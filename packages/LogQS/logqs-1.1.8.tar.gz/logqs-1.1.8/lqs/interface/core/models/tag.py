from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
    Int64,
)
from lqs.interface.core import models


class Tag(CommonModel):
    label_id: UUID = Field(
        ..., description="The ID of the label associated with the tag"
    )
    log_id: UUID = Field(..., description="The ID of the log associated with the tag")
    topic_id: Optional[UUID] = Field(
        None, description="The ID of the topic associated with the tag"
    )

    note: Optional[str] = Field(
        None, description="A general note about the tag for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the tag."
    )
    start_time: Optional[Int64] = Field(
        None, description="The timestamp of the beggining of the tagged time range."
    )
    end_time: Optional[Int64] = Field(
        None, description="The timestamp of the end of the tagged time range."
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            ["topic_id", "note", "context", "start_time", "end_time"]
        )
    )

    def fetch_label(self) -> "models.Label":
        return self._app.fetch.label(self.label_id).data

    def fetch_log(self) -> "models.Log":
        return self._app.fetch.log(self.log_id).data

    def fetch_topic(self) -> Optional["models.Topic"]:
        if self.topic_id is None:
            return None
        return self._app.fetch.topic(self.topic_id).data


class TagDataResponse(DataResponseModel[Tag]):
    pass


class TagListResponse(PaginationModel[Tag]):
    pass


class TagForLogCreateRequest(BaseModel):
    label_id: UUID
    topic_id: Optional[UUID] = None

    note: Optional[str] = None
    context: Optional[dict] = None
    start_time: Optional[Int64] = None
    end_time: Optional[Int64] = None


class TagCreateRequest(TagForLogCreateRequest):
    log_id: UUID


class TagUpdateRequest(BaseModel):
    label_id: UUID = optional_field
    topic_id: Optional[UUID] = optional_field

    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    start_time: Optional[Int64] = optional_field
    end_time: Optional[Int64] = optional_field
