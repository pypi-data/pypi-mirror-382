from typing import List, Optional, Tuple
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    DataResponseModel,
    PaginationModel,
    ProcessModel,
    ProcessCreateRequest,
    ProcessUpdateRequest,
    optional_field,
    Int64,
    process_required_fields,
)
from lqs.interface.core import models


class DigestionPartIndexEntry(BaseModel):
    topic_id: str
    ingestion_id: Optional[str]
    source: Optional[str]

    data_offset: int
    data_length: int

    chunk_compression: Optional[str]
    chunk_offset: Optional[int]
    chunk_length: Optional[int]
    timestamp: Int64


# TODO: in Python 3.11, we can use Tuple[*get_type_hints(DigestionPartIndex).values()]
DigestionPartIndexTuple = Tuple[
    str,
    Optional[str],
    Optional[str],
    int,
    int,
    Optional[str],
    Optional[int],
    Optional[int],
    Int64,
]


class DigestionPartIndex(BaseModel):
    digestion_part_id: UUID
    index: Optional[List[DigestionPartIndexTuple]]


class DigestionPartIndexCreateRequest(BaseModel):
    digestion_part_id: UUID
    index: Optional[List[DigestionPartIndexTuple]] = None


class DigestionPartIndexUpdateRequest(BaseModel):
    index: Optional[List[DigestionPartIndexTuple]] = optional_field


class DigestionPartIndexDataResponse(DataResponseModel[DigestionPartIndex]):
    pass


class DigestionPartIndexListResponse(PaginationModel[DigestionPartIndex]):
    pass


# Digestion Part


class DigestionPart(ProcessModel["DigestionPart"]):
    sequence: int = Field(
        ..., description="The index of the digestion part within the digestion."
    )
    digestion_id: UUID = Field(
        ..., description="The ID of the digestion to which the digestion part belongs."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the digestion part."
    )
    index: Optional[List[DigestionPartIndexTuple]] = Field(
        None, description="The record metadata index of the digestion part."
    )

    log_id: Optional[UUID] = Field(
        None, description="The ID of the log to which the digestion part belongs."
    )
    group_id: Optional[UUID] = Field(
        None, description="The ID of the group to which the digestion part belongs."
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            ["context", "index", "log_id", "group_id"] + process_required_fields
        )
    )

    def fetch_digestion(self) -> "models.Digestion":
        return self._app.fetch.digestion(self.digestion_id).data

    def fetch_log(self) -> "models.Log":
        return self._app.fetch.log(self.log_id).data

    def fetch_group(self) -> "models.Group":
        return self._app.fetch.group(self.group_id).data


class DigestionPartForDigestionCreateRequest(ProcessCreateRequest):
    sequence: int
    context: Optional[dict] = None
    index: Optional[List[DigestionPartIndexTuple]] = None


class DigestionPartCreateRequest(DigestionPartForDigestionCreateRequest):
    digestion_id: UUID


class DigestionPartUpdateRequest(ProcessUpdateRequest):
    sequence: int = optional_field
    context: Optional[dict] = optional_field
    index: Optional[List[DigestionPartIndexTuple]] = optional_field


class DigestionPartDataResponse(DataResponseModel[DigestionPart]):
    pass


class DigestionPartListResponse(PaginationModel[DigestionPart]):
    pass
