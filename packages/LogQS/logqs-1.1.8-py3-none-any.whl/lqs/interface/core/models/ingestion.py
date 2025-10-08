from typing import Optional
from uuid import UUID

from pydantic import Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    DataResponseModel,
    PaginationModel,
    ProcessModel,
    ProcessCreateRequest,
    ProcessUpdateRequest,
    optional_field,
    process_required_fields,
)
from lqs.interface.core import models


class Ingestion(ProcessModel["Ingestion"]):
    log_id: UUID = Field(
        ..., description="The ID of the log to which this ingestion belongs."
    )

    object_store_id: Optional[UUID] = Field(
        None,
        description="The ID of the object store where the ingestion object is stored.",
    )
    object_key: Optional[str] = Field(
        None, description="The key of the ingestion object."
    )

    name: Optional[str] = Field(
        None, description="The name of the ingestion for reference (not unique)."
    )
    note: Optional[str] = Field(
        None, description="A general note about the ingestion for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the ingestion."
    )

    group_id: UUID = Field(
        ...,
        description="The ID of the group to which this ingestion belongs.",
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            ["object_store_id", "object_key", "name", "note", "context"]
            + process_required_fields
        )
    )

    def list_ingestion_parts(
        self, threaded=False, **kwargs
    ) -> list["models.IngestionPart"]:
        return self._list_all_subresources(
            list_method=self._app.list.ingestion_part,
            threaded=threaded,
            ingestion_id=self.id,
            **kwargs,
        )

    def fetch_log(self) -> "models.Log":
        return self._app.fetch.log(self.log_id).data

    def fetch_group(self) -> "models.Group":
        return self._app.fetch.group(self.group_id).data

    def fetch_workflow(self) -> Optional["models.Workflow"]:
        if self.workflow_id is None:
            return None
        return self._app.fetch.workflow(self.workflow_id).data


class IngestionDataResponse(DataResponseModel[Ingestion]):
    pass


class IngestionListResponse(PaginationModel[Ingestion]):
    pass


class IngestionCreateRequest(ProcessCreateRequest):
    log_id: UUID
    name: Optional[str] = None
    object_store_id: Optional[UUID] = None
    object_key: Optional[str] = None
    note: Optional[str] = None
    context: Optional[dict] = None


class IngestionUpdateRequest(ProcessUpdateRequest):
    name: Optional[str] = optional_field
    object_store_id: Optional[UUID] = optional_field
    object_key: Optional[str] = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
