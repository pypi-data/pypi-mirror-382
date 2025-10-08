from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from lqs.interface.dsm.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    ProcessState,
    ProcessType,
    optional_field,
)


class Event(CommonModel):
    previous_state: Optional[ProcessState]
    current_state: ProcessState
    process_type: ProcessType
    resource_id: UUID
    workflow_id: Optional[UUID]
    hook_id: Optional[UUID]
    datastore_id: Optional[UUID]
    datastore_endpoint: Optional[str]


class EventDataResponse(DataResponseModel[Event]):
    pass


class EventListResponse(PaginationModel[Event]):
    pass


class EventCreateRequest(BaseModel):
    previous_state: Optional[ProcessState] = None
    current_state: ProcessState
    process_type: ProcessType
    resource_id: UUID
    workflow_id: Optional[UUID] = None
    hook_id: Optional[UUID] = None
    datastore_id: Optional[UUID] = None
    datastore_endpoint: Optional[str] = None


class EventUpdateRequest(BaseModel):
    previous_state: Optional[ProcessState] = optional_field
    current_state: Optional[ProcessState] = optional_field
    process_type: ProcessType = optional_field
    resource_id: UUID = optional_field
    workflow_id: Optional[UUID] = optional_field
    hook_id: Optional[UUID] = optional_field
    datastore_id: Optional[UUID] = optional_field
    datastore_endpoint: Optional[str] = optional_field
