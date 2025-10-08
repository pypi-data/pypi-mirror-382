from typing import List, Optional, Tuple, Union
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


class IngestionPartIndexEntry(BaseModel):
    topic_id: str
    data_offset: int
    data_length: int
    chunk_compression: Optional[str]
    chunk_offset: Optional[int]
    chunk_length: Optional[int]
    timestamp: Int64
    # context: Optional[dict] = None


# TODO: in Python 3.11, we can use Tuple[*get_type_hints(IngestionPartIndex).values()]
IngestionPartIndexTuple = Tuple[
    str, int, int, Optional[str], Optional[int], Optional[int], Int64
]

IngestionPartIndexTupleV2 = Tuple[
    str, int, int, Optional[str], Optional[int], Optional[int], Int64, Optional[dict]
]


class IngestionPartIndex(BaseModel):
    ingestion_part_id: UUID
    index: Optional[
        Union[List[IngestionPartIndexTuple], List[IngestionPartIndexTupleV2]]
    ]


class IngestionPartIndexCreateRequest(BaseModel):
    ingestion_part_id: UUID
    index: Optional[
        Union[List[IngestionPartIndexTuple], List[IngestionPartIndexTupleV2]]
    ] = None


class IngestionPartIndexUpdateRequest(BaseModel):
    index: Optional[
        Union[List[IngestionPartIndexTuple], List[IngestionPartIndexTupleV2]]
    ] = optional_field


class IngestionPartIndexDataResponse(DataResponseModel[IngestionPartIndex]):
    pass


class IngestionPartIndexListResponse(PaginationModel[IngestionPartIndex]):
    pass


# Ingestion Part


class IngestionPart(ProcessModel["IngestionPart"]):
    sequence: int = Field(
        ...,
        description="The index of the ingestion part within the ingestion for a given source.",
    )
    ingestion_id: UUID = Field(
        ..., description="The ID of the ingestion to which the ingestion part belongs."
    )
    source: Optional[str] = Field(
        None,
        description="The path of the source object relative to the ingestion's object key.",
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the ingestion part."
    )
    index: Optional[
        Union[List[IngestionPartIndexTuple], List[IngestionPartIndexTupleV2]]
    ] = Field(None, description="The record metadata index of the ingestion part.")

    log_id: Optional[UUID] = Field(
        None, description="The ID of the log to which the ingestion part belongs."
    )
    group_id: Optional[UUID] = Field(
        None, description="The ID of the group to which the ingestion part belongs."
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            ["source", "context", "index", "log_id", "group_id"]
            + process_required_fields
        )
    )

    def fetch_ingestion(self) -> "models.Ingestion":
        return self._app.fetch.ingestion(self.ingestion_id).data

    def fetch_log(self) -> "models.Log":
        return self._app.fetch.log(self.log_id).data

    def fetch_group(self) -> "models.Group":
        return self._app.fetch.group(self.group_id).data


class IngestionPartListResponse(PaginationModel[IngestionPart]):
    pass


class IngestionPartDataResponse(DataResponseModel[IngestionPart]):
    pass


class IngestionPartForIngestionCreateRequest(ProcessCreateRequest):
    sequence: int
    source: Optional[str] = None
    context: Optional[dict] = None
    index: Optional[
        Union[List[IngestionPartIndexTuple], List[IngestionPartIndexTupleV2]]
    ] = None


class IngestionPartCreateRequest(IngestionPartForIngestionCreateRequest):
    ingestion_id: UUID


class IngestionPartUpdateRequest(ProcessUpdateRequest):
    sequence: int = optional_field
    source: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    index: Optional[
        Union[List[IngestionPartIndexTuple], List[IngestionPartIndexTupleV2]]
    ] = optional_field
