from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    CommonModel,
    ProcessType,
    DataResponseModel,
    PaginationModel,
    optional_field,
)
from lqs.interface.core import models


class Workflow(CommonModel):
    name: str = Field(..., description="The unique name of the workflow for reference.")
    process_type: Optional[ProcessType] = Field(
        None,
        description="The process type of the workflow (`ingestion` or `digestion`).",
    )
    note: Optional[str] = Field(
        None, description="A general note about the workflow for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the workflow."
    )
    managed: bool = Field(
        ..., description="Whether the workflow is managed by the system."
    )
    default: bool = Field(
        ..., description="Whether the workflow is the default workflow."
    )
    disabled: bool = Field(
        ..., description="Whether the workflow is disabled and cannot be used."
    )
    context_schema: Optional[dict] = Field(
        None,
        description="The context JSON schema for the workflow which process workflow contexts are validated against.",
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            [
                "process_type",
                "note",
                "context",
                "context_schema",
            ]
        )
    )

    def list_digestions(self, threaded=False, **kwargs) -> list["models.Digestion"]:
        return self._list_all_subresources(
            list_method=self._app.list.digestion,
            threaded=threaded,
            workflow_id=self.id,
            **kwargs,
        )

    def list_ingestions(self, threaded=False, **kwargs) -> list["models.Ingestion"]:
        return self._list_all_subresources(
            list_method=self._app.list.ingestion,
            threaded=threaded,
            workflow_id=self.id,
            **kwargs,
        )

    def list_hooks(self, threaded=False, **kwargs) -> list["models.Hook"]:
        return self._list_all_subresources(
            list_method=self._app.list.hook,
            threaded=threaded,
            workflow_id=self.id,
            **kwargs,
        )


class WorkflowDataResponse(DataResponseModel[Workflow]):
    pass


class WorkflowListResponse(PaginationModel[Workflow]):
    pass


class WorkflowCreateRequest(BaseModel):
    name: str
    process_type: ProcessType = ProcessType.digestion
    note: Optional[str] = None
    context: Optional[dict] = None
    default: bool = False
    disabled: bool = False
    managed: bool = False
    context_schema: Optional[dict] = None


class WorkflowUpdateRequest(BaseModel):
    name: str = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    default: bool = optional_field
    disabled: bool = optional_field
    context_schema: Optional[dict] = optional_field
