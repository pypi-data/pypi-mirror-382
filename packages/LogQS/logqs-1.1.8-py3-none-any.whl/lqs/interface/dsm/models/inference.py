from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.dsm.models.__common__ import (
    DataResponseModel,
    PaginationModel,
)


class Inference(BaseModel):
    output: dict | list
    meta: dict


class InferenceDataResponse(DataResponseModel[Inference]):
    pass


class InferenceListResponse(PaginationModel[Inference]):
    pass


class InferenceCreateRequest(BaseModel):
    datastore_id: UUID
    topic_id: UUID
    timestamp: int
    pipeline_task: str
    pipeline_model: Optional[str] = None
    pipeline_revision: Optional[str] = None


class InferenceUpdateRequest(BaseModel):
    pass
