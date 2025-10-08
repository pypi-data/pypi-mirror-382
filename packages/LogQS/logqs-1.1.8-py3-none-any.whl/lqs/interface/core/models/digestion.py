from typing import Optional, List
from uuid import UUID

from pydantic import Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    DataResponseModel,
    PaginationModel,
    ProcessModel,
    ProcessCreateRequest,
    ProcessUpdateRequest,
    optional_field_alt as optional_field,
    process_required_fields,
)
from lqs.interface.core import models


class Digestion(ProcessModel["Digestion"]):
    log_id: UUID = Field(
        ..., description="The ID of the log to which the digestion belongs."
    )
    group_id: UUID = Field(
        ..., description="The ID of the group to which the digestion belongs."
    )
    name: Optional[str] = Field(
        None, description="The name of the digestion for reference (not unique)."
    )
    note: Optional[str] = Field(
        None, description="A general note about the digestion for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the digestion."
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            ["name", "note", "context"] + process_required_fields
        )
    )

    def list_digestion_topics(
        self, threaded=False, **kwargs
    ) -> List["models.DigestionTopic"]:
        return self._list_all_subresources(
            list_method=self._app.list.digestion_topic,
            threaded=threaded,
            digestion_id=self.id,
            **kwargs,
        )

    def list_digestion_parts(
        self, threaded=False, **kwargs
    ) -> List["models.DigestionPart"]:
        return self._list_all_subresources(
            list_method=self._app.list.digestion_part,
            threaded=threaded,
            digestion_id=self.id,
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


class DigestionDataResponse(DataResponseModel[Digestion]):
    pass


class DigestionListResponse(PaginationModel[Digestion]):
    pass


class DigestionCreateRequest(ProcessCreateRequest):
    log_id: UUID = Field(
        ..., description="The ID of the log to which the digestion should be added."
    )
    name: Optional[str] = Field(
        None, description="The name of the digestion (not unique)."
    )
    note: Optional[str] = Field(
        None, description="A general note about the digestion for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the digestion."
    )


class DigestionUpdateRequest(ProcessUpdateRequest):
    name: Optional[str] = optional_field("The name of the digestion (not unique).")
    note: Optional[str] = optional_field(
        "A general note about the digestion for reference."
    )
    context: Optional[dict] = optional_field(
        "Arbitrary JSON context for the digestion."
    )
