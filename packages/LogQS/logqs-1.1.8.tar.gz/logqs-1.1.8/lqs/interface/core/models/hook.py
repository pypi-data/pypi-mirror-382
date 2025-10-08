from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    ProcessState,
    ProcessType,
    optional_field,
)
from lqs.interface.core import models


class Hook(CommonModel):
    workflow_id: UUID = Field(
        ..., description="The ID of the workflow to which the hook belongs."
    )
    trigger_process: ProcessType = Field(
        ..., description="The process type that triggers the hook."
    )
    trigger_state: ProcessState = Field(
        ..., description="The process state that triggers the hook."
    )
    name: Optional[str] = Field(
        None, description="The name of the hook for reference (not unique)."
    )
    note: Optional[str] = Field(
        None, description="A general note about the hook for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the hook."
    )
    managed: bool = Field(..., description="Whether the hook is managed by the system.")
    disabled: bool = Field(
        ..., description="Whether the hook is disabled and cannot be triggered."
    )
    uri: Optional[str] = Field(
        None, description="The URI to which the hook should send requests."
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            ["name", "note", "context", "uri"]
        )
    )

    def fetch_workflow(self) -> "models.Workflow":
        return self._app.fetch.workflow(self.workflow_id).data


class HookDataResponse(DataResponseModel[Hook]):
    pass


class HookListResponse(PaginationModel[Hook]):
    pass


class HookForWorkflowCreateRequest(BaseModel):
    trigger_process: ProcessType
    trigger_state: ProcessState
    name: Optional[str] = None
    note: Optional[str] = None
    context: Optional[dict] = None
    disabled: bool = False
    managed: bool = False
    uri: Optional[str] = None
    secret: Optional[str] = None


class HookCreateRequest(HookForWorkflowCreateRequest):
    workflow_id: UUID


class HookUpdateRequest(BaseModel):
    trigger_process: ProcessType = optional_field
    trigger_state: ProcessState = optional_field
    name: Optional[str] = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    disabled: bool = optional_field
    uri: Optional[str] = optional_field
    secret: Optional[str] = optional_field
