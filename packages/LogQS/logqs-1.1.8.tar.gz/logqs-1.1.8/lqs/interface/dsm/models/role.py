from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict

from lqs.interface.base.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)


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
    name: str
    policy: Policy
    note: Optional[str]

    disabled: bool
    default: bool
    managed: bool


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
