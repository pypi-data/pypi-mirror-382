from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.dsm.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    ProcessState,
    ProcessType,
    JobType,
    optional_field,
)


class Job(CommonModel):
    event_id: Optional[UUID]
    type: JobType
    process_type: ProcessType
    resource_id: UUID
    datastore_id: Optional[UUID]
    datastore_endpoint: Optional[str]
    state: ProcessState
    error: Optional[dict]


class JobDataResponse(DataResponseModel[Job]):
    pass


class JobListResponse(PaginationModel[Job]):
    pass


class JobCreateRequest(BaseModel):
    type: JobType
    process_type: ProcessType
    resource_id: UUID
    event_id: Optional[UUID] = None
    datastore_id: Optional[UUID] = None
    datastore_endpoint: Optional[str] = None
    state: ProcessState = ProcessState.ready


class JobUpdateRequest(BaseModel):
    type: JobType = optional_field
    process_type: ProcessType = optional_field
    resource_id: UUID = optional_field
    datastore_id: Optional[UUID] = optional_field
    datastore_endpoint: Optional[str] = optional_field
    state: ProcessState = optional_field
    error: Optional[dict] = optional_field
