from typing import List, Optional
from enum import Enum

from pydantic import Field, BaseModel, ConfigDict

from lqs.interface.base.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)
from lqs.interface.core import models


class StatementEffect(str, Enum):
    allow = "allow"
    deny = "deny"


class StatementAction(str, Enum):
    read = "read"
    write = "write"
    wildcard = "*"

    create = "create"
    list = "list"
    fetch = "fetch"
    update = "update"
    delete = "delete"


class Statement(BaseModel):
    effect: StatementEffect
    action: List[StatementAction] = []
    resource: List[str] = []
    filter: Optional[dict] = {}

    model_config = ConfigDict(
        json_schema_extra={"required": ["effect", "action", "resource", "filter"]}
    )


class Policy(BaseModel):
    statement: List[Statement]


class Role(CommonModel):
    name: str = Field(..., description="The unique name of the role for reference.")
    policy: Policy = Field(..., description="The policy of the role.")
    note: Optional[str] = Field(
        None, description="A general note about the role for reference."
    )

    disabled: bool = Field(
        ..., description="Whether the role is disabled and cannot be used."
    )
    default: bool = Field(
        ..., description="Whether the role is applied to users by default."
    )
    managed: bool = Field(..., description="Whether the role is managed by the system.")

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(["name", "note"])
    )

    def list_users(self, threaded=False, **kwargs) -> list["models.User"]:
        return self._list_all_subresources(
            list_method=self._app.list.user,
            threaded=threaded,
            role_id=self.id,
            **kwargs,
        )


class RoleDataResponse(DataResponseModel[Role]):
    pass


class RoleListResponse(PaginationModel[Role]):
    pass


class RoleCreateRequest(BaseModel):
    name: str
    policy: Policy

    note: Optional[str] = None
    disabled: bool = False
    managed: bool = False
    default: bool = False


class RoleUpdateRequest(BaseModel):
    name: str = optional_field
    policy: Policy = optional_field
    note: Optional[str] = optional_field
    disabled: bool = optional_field
    default: bool = optional_field
