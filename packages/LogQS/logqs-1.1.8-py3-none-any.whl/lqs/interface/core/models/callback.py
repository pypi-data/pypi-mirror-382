from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)


class Callback(CommonModel):
    name: str = Field(..., description="The name of the callback for reference.")
    note: Optional[str] = Field(
        None, description="A general note about the callback for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the callback."
    )
    managed: bool = Field(
        ..., description="Whether the callback is managed by the system."
    )
    default: bool = Field(
        ..., description="Whether the callback is the default callback."
    )
    disabled: bool = Field(
        ..., description="Whether the callback is disabled and cannot be used."
    )
    uri: Optional[str] = Field(
        None, description="The URI to which the callback should send requests."
    )
    parameter_schema: Optional[dict] = Field(
        None, description="The parameter JSON schema for the callback."
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            ["note", "context", "uri", "parameter_schema"]
        )
    )


class CallbackDataResponse(DataResponseModel[Callback]):
    pass


class CallbackListResponse(PaginationModel[Callback]):
    pass


class CallbackCreateRequest(BaseModel):
    name: str
    note: Optional[str] = None
    context: Optional[dict] = None
    managed: bool = False
    default: bool = False
    disabled: bool = False
    uri: Optional[str] = None
    secret: Optional[str] = None
    parameter_schema: Optional[dict] = None


class CallbackUpdateRequest(BaseModel):
    name: str = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    managed: bool = optional_field
    default: bool = optional_field
    disabled: bool = optional_field
    uri: Optional[str] = optional_field
    secret: Optional[str] = optional_field
    parameter_schema: Optional[dict] = optional_field
