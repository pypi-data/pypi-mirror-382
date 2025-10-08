from typing import List, Optional
from uuid import UUID

from pydantic import Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    CommonModel,
    DataResponseModel,
    LockModel,
    LockCreateRequest,
    LockUpdateRequest,
    PaginationModel,
    TypeEncoding,
    optional_field,
    Int64,
)
from lqs.interface.core import models


class Topic(CommonModel, LockModel):
    log_id: UUID = Field(
        ..., description="The ID of the log to which this topic belongs."
    )
    group_id: Optional[UUID] = Field(
        ..., description="The ID of the group to which this topic belongs."
    )

    name: str = Field(..., description="The name of the topic (unique per log).")
    note: Optional[str] = Field(
        None, description="A general note about the topic for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the topic."
    )

    associated_topic_id: Optional[UUID] = Field(
        None, description="The ID of an associated topic (if any) for reference."
    )
    start_time: Optional[Int64] = Field(
        None, description="The timestamp of the first record of the topic."
    )
    end_time: Optional[Int64] = Field(
        None, description="The timestamp of the last record of the topic."
    )
    duration: Optional[Int64] = Field(
        None, description="The duration of the topic in nanoseconds."
    )
    base_timestamp: Optional[Int64] = Field(
        None,
        description="The time, in nanoseconds, to be added to all timestamps in the log.",
    )
    record_size: int = Field(
        ..., description="The total size of all records in the topic in bytes."
    )
    record_count: int = Field(
        ..., description="The total number of records in the topic."
    )
    object_size: int = Field(
        0,
        description="The total size of all objects in the topic in bytes.",
        deprecated="This field is no longer populated with a non-zero value.",
    )
    object_count: int = Field(
        0,
        description="The total number of objects in the topic.",
        deprecated="This field is no longer populated with a non-zero value.",
    )

    strict: bool = Field(
        ..., description="Whether the topic's schema should be strictly enforced."
    )
    type_name: Optional[str] = Field(
        None,
        description="The name of the message type which the topic's records should conform to.",
    )
    type_encoding: Optional[TypeEncoding] = Field(
        None, description="The encoding of the message data of the topic's records."
    )
    type_data: Optional[str] = Field(
        None,
        description="The definition of the message type used to (de)serialize the topic's records.",
    )
    type_schema: Optional[dict] = Field(
        None,
        description="A JSON schema describing the record data of the topic's records.",
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            [
                "note",
                "context",
                "associated_topic_id",
                "start_time",
                "end_time",
                "duration",
                "base_timestamp",
                "object_size",
                "object_count",
                "type_name",
                "type_encoding",
                "type_data",
                "type_schema",
            ]
        )
    )

    def fetch_log(self) -> "models.Log":
        return self._app.fetch.log(self.log_id).data

    def fetch_group(self) -> Optional["models.Group"]:
        if self.group_id is None:
            return None
        return self._app.fetch.group(self.group_id).data

    def fetch_associated_topic(self) -> Optional["models.Topic"]:
        if self.associated_topic_id is None:
            return None
        return self._app.fetch.topic(self.associated_topic_id).data

    def list_records(self, threaded=False, **kwargs) -> List["models.Record"]:
        return self._list_all_subresources(
            list_method=self._app.list.record,
            threaded=threaded,
            topic_id=self.id,
            **kwargs,
        )


Topic.model_rebuild()


class TopicDataResponse(DataResponseModel[Topic]):
    pass


class TopicListResponse(PaginationModel[Topic]):
    pass


class TopicCreateRequest(LockCreateRequest):
    log_id: UUID
    name: str
    note: Optional[str] = None
    base_timestamp: Optional[Int64] = None
    context: Optional[dict] = None
    associated_topic_id: Optional[UUID] = None

    strict: bool = False
    type_name: Optional[str] = None
    type_encoding: Optional[TypeEncoding] = None
    type_data: Optional[str] = None
    type_schema: Optional[dict] = None


class TopicUpdateRequest(LockUpdateRequest):
    name: str = optional_field
    note: Optional[str] = optional_field
    base_timestamp: Optional[Int64] = optional_field
    context: Optional[dict] = optional_field
    associated_topic_id: Optional[UUID] = optional_field

    strict: bool = optional_field
    type_name: Optional[str] = optional_field
    type_encoding: Optional[TypeEncoding] = optional_field
    type_data: Optional[str] = optional_field
    type_schema: Optional[dict] = optional_field
