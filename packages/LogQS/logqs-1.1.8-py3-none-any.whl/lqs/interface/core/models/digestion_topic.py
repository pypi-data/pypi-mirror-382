from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    DataResponseModel,
    CommonModel,
    PaginationModel,
    optional_field,
    Int64,
)
from lqs.interface.core import models


class DigestionTopic(CommonModel):
    digestion_id: UUID = Field(
        ...,
        description="The ID of the associated digestion.",
    )
    topic_id: UUID = Field(
        ...,
        description="The ID of the associated topic.",
    )
    start_time: Optional[Int64] = Field(
        None,
        description="The timestamp of the first record to be digested.",
    )
    end_time: Optional[Int64] = Field(
        None,
        description="The timestamp of the last record to be digested.",
    )
    frequency: Optional[float] = Field(
        None,
        description="The frequency of the records to be digested.",
    )
    query_data_filter: Optional[dict] = Field(
        None,
        description="A JSON filter applied to the record's query data for the digestion.",
    )
    context_filter: Optional[dict] = Field(
        None,
        description="A JSON filter applied to the record's context for the digestion.",
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            [
                "start_time",
                "end_time",
                "frequency",
                "query_data_filter",
                "context_filter",
            ]
        )
    )

    def fetch_digestion(self) -> "models.Digestion":
        return self._app.fetch.digestion(self.digestion_id).data

    def fetch_topic(self) -> "models.Topic":
        return self._app.fetch.topic(self.topic_id).data


class DigestionTopicDataResponse(DataResponseModel[DigestionTopic]):
    pass


class DigestionTopicListResponse(PaginationModel[DigestionTopic]):
    pass


class DigestionTopicForDigestionCreateRequest(BaseModel):
    topic_id: UUID
    start_time: Optional[Int64]
    end_time: Optional[Int64]
    frequency: Optional[float] = None
    query_data_filter: Optional[dict] = None
    context_filter: Optional[dict] = None


class DigestionTopicCreateRequest(DigestionTopicForDigestionCreateRequest):
    digestion_id: UUID


class DigestionTopicUpdateRequest(BaseModel):
    start_time: Optional[Int64] = optional_field
    end_time: Optional[Int64] = optional_field
    frequency: Optional[float] = optional_field
    query_data_filter: Optional[dict] = optional_field
    context_filter: Optional[dict] = optional_field
