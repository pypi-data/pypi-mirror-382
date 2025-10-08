from typing import Optional
from uuid import UUID

from pydantic import Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    DataResponseModel,
    TimeSeriesModel,
    PaginationModel,
    LockModel,
    LockCreateRequest,
    LockUpdateRequest,
    optional_field,
    Int64,
)
from lqs.interface.core import models


class Record(TimeSeriesModel["Record"], LockModel):
    _repr_fields = ("timestamp", "topic_id", "log_id")

    log_id: UUID = Field(
        ..., description="The ID of the log to which this record's topic belongs."
    )
    topic_id: UUID = Field(
        ..., description="The ID of the topic to which this record belongs."
    )
    timestamp: Int64 = Field(
        ..., description="The timestamp, in nanoseconds, of the record."
    )

    ingestion_id: Optional[UUID] = Field(
        None, description="The ID of the ingestion which created this record, if any."
    )
    data_offset: Optional[int] = Field(
        None,
        description="The offset, in bytes, of the record's message data in the log object.",
    )
    data_length: Optional[int] = Field(
        None,
        description="The length, in bytes, of the record's message data in the log object.",
    )
    chunk_compression: Optional[str] = Field(
        None,
        description="The compression algorithm used to compress the record's message data in the log object, if any.",
    )
    chunk_offset: Optional[int] = Field(
        None,
        description="The offset, in bytes, of the record's message data in the log object's uncompressed data relative to the start of the uncompressed chunk, if compressed.",
    )
    chunk_length: Optional[int] = Field(
        None,
        description="The length, in bytes, of the record's message data in the log object's uncompressed data, if compressed.",
    )
    source: Optional[str] = Field(
        None,
        description="A relative path to the record's log object relative to the record's ingestion object, if any.",
    )
    error: Optional[dict] = Field(
        None,
        description="The JSON payload of an error that occurred during record processing.",
    )

    query_data: Optional[dict | list] = Field(
        None,
        description="A JSON data representation of the record's message data which is queryable.",
    )
    auxiliary_data: Optional[dict | list] = Field(
        None,
        description="A JSON data representation of the record's auxiliary data which can be used for functional purposes.",
    )
    raw_data: Optional[str] = Field(
        None,
        description="A string representation of the record's message data, presented as-is. This data will be base 64 encoded if needed.",
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the record."
    )
    note: Optional[str] = Field(
        None, description="A general note about the record for reference."
    )

    def get_auxiliary_data(self):
        if self.auxiliary_data is None:
            record = self.fetch(
                self.timestamp, self.topic_id, include_auxiliary_data=True
            )
            self.auxiliary_data = record.auxiliary_data
        return self.auxiliary_data

    def load_auxiliary_data_image(self):
        return self._app.utils.load_auxiliary_data_image(self)

    def get_raw_data(self):
        if self.raw_data is None:
            record = self.fetch(self.timestamp, self.topic_id, include_raw_data=True)
            self.raw_data = record.raw_data
        return self.raw_data

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            [
                "ingestion_id",
                "data_offset",
                "data_length",
                "chunk_compression",
                "chunk_offset",
                "chunk_length",
                "source",
                "error",
                "query_data",
                "auxiliary_data",
                "raw_data",
                "context",
                "note",
            ]
        )
    )

    def fetch_log(self) -> "models.Log":
        return self._app.fetch.log(self.log_id).data

    def fetch_topic(self) -> "models.Topic":
        return self._app.fetch.topic(self.topic_id).data

    def fetch_ingestion(self) -> Optional["models.Ingestion"]:
        if self.ingestion_id is None:
            return None
        return self._app.fetch.ingestion(self.ingestion_id).data


class RecordDataResponse(DataResponseModel[Record]):
    pass


class RecordListResponse(PaginationModel[Record]):
    pass


class RecordCreateRequest(LockCreateRequest):
    timestamp: Int64
    note: Optional[str] = None
    context: Optional[dict] = None
    query_data: Optional[dict] = None
    auxiliary_data: Optional[dict] = None

    data_offset: Optional[int] = None
    data_length: Optional[int] = None
    chunk_compression: Optional[str] = None
    chunk_offset: Optional[int] = None
    chunk_length: Optional[int] = None
    source: Optional[str] = None


class RecordUpdateRequest(LockUpdateRequest):
    error: Optional[dict] = optional_field
    query_data: Optional[dict] = optional_field
    auxiliary_data: Optional[dict] = optional_field
    context: Optional[dict] = optional_field
    note: Optional[str] = optional_field
