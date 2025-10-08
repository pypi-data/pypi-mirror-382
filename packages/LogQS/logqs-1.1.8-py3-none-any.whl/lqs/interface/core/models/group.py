from typing import List, Optional
from uuid import UUID

from pydantic import Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    CommonModel,
    DataResponseModel,
    LockModel,
    LockCreateRequest,
    LockUpdateRequest,
    PaginationModel,
    optional_field,
    optional_deprecated_field,
)
from lqs.interface.core import models


class Group(CommonModel, LockModel):
    name: str = Field(..., description="The unique name of the group.")
    note: Optional[str] = Field(
        None, description="A general note about the group for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the group."
    )
    default_workflow_id: Optional[UUID] = Field(
        None,
        description="The ID of the workflow to be executed during state transitions of associated processes.",
        deprecated="This field is no longer populated with a non-null value.",
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            ["note", "context", "default_workflow_id"]
        )
    )

    def list_logs(self, threaded=False, **kwargs) -> List["models.Log"]:
        return self._list_all_subresources(
            list_method=self._app.list.log,
            threaded=threaded,
            group_id=self.id,
            **kwargs,
        )


class GroupDataResponse(DataResponseModel[Group]):
    pass


class GroupListResponse(PaginationModel[Group]):
    pass


class GroupCreateRequest(LockCreateRequest):
    name: str
    note: Optional[str] = None
    context: Optional[dict] = None
    default_workflow_id: Optional[UUID] = Field(
        None,
        deprecated=True,
    )


class GroupUpdateRequest(LockUpdateRequest):
    name: str = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    default_workflow_id: Optional[UUID] = optional_deprecated_field
