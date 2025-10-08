from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)


class Query(CommonModel):
    log_id: UUID = Field(
        ..., description="The ID of the log to which the query is scoped."
    )
    name: Optional[str] = Field(
        None, description="The name of the query for reference (not unique)."
    )
    note: Optional[str] = Field(
        None, description="A general note about the query for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the query."
    )

    statement: Optional[str] = Field(
        None, description="The SQL statement of the query."
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="The parameters of the query."
    )
    columns: Optional[List[str]] = Field(
        None, description="The columns of the query result."
    )
    rows: Optional[List[List[Any]]] = Field(
        None, description="The rows of the query result."
    )
    error: Optional[dict] = Field(None, description="The error of the query if any.")

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            [
                "name",
                "note",
                "context",
                "statement",
                "parameters",
                "columns",
                "rows",
                "error",
            ]
        )
    )


class QueryDataResponse(DataResponseModel[Query]):
    pass


class QueryListResponse(PaginationModel[Query]):
    pass


class QueryForLogCreateRequest(BaseModel):
    name: Optional[str] = None
    note: Optional[str] = None
    context: Optional[dict] = None
    statement: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class QueryCreateRequest(QueryForLogCreateRequest):
    log_id: UUID


class QueryUpdateRequest(BaseModel):
    name: Optional[str] = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    statement: Optional[str] = optional_field
    parameters: Optional[Dict[str, Any]] = optional_field
