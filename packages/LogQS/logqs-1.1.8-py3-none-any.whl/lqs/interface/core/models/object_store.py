from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.base.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)
from lqs.interface.core import models


class ObjectStore(CommonModel):
    name: Optional[str] = Field(
        None, description="The unique name of the object store for reference."
    )
    bucket_name: str = Field(
        ..., description="The name of the bucket for the object store."
    )
    access_key_id: Optional[str] = Field(
        None, description="The access key ID used to access the object store's bucket."
    )
    region_name: Optional[str] = Field(
        None,
        description="The name of the region where the object store's bucket is located.",
    )
    endpoint_url: Optional[str] = Field(
        None,
        description="The endpoint URL of the object store's bucket. If not provided, the AWS default endpoint will be used.",
    )
    note: Optional[str] = Field(
        None, description="A general note about the object store for reference."
    )
    context: Optional[dict] = Field(
        None, description="Arbitrary JSON context for the object store."
    )
    disabled: bool = Field(
        False, description="Whether the object store is disabled and cannot be used."
    )
    default: bool = Field(
        False,
        description="Whether the object store is the default object store. Used for reference.",
    )
    read_only: bool = Field(
        False,
        description="Whether the object store can only be used for read operations.",
    )
    managed: bool = Field(
        False, description="Whether the object store is managed by the system."
    )
    key_prefix: Optional[str] = Field(
        None,
        description="The prefix for enforcing/limiting the object store's objects' keys.",
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(
            [
                "name",
                "access_key_id",
                "region_name",
                "endpoint_url",
                "note",
                "context",
                "disabled",
                "default",
                "read_only",
                "managed",
                "key_prefix",
            ]
        )
    )

    def list_objects(self, threaded=False, **kwargs) -> list["models.Object"]:
        return self._list_all_subresources(
            list_method=self._app.list.object,
            threaded=threaded,
            object_store_id=self.id,
            **kwargs,
        )


class ObjectStoreDataResponse(DataResponseModel[ObjectStore]):
    pass


class ObjectStoreListResponse(PaginationModel[ObjectStore]):
    pass


class ObjectStoreCreateRequest(BaseModel):
    name: str
    bucket_name: str
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    region_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    note: Optional[str] = None
    context: Optional[dict] = None
    disabled: bool = False
    default: bool = False
    read_only: bool = False
    managed: bool = False
    key_prefix: Optional[str] = None


class ObjectStoreUpdateRequest(BaseModel):
    name: str = optional_field
    bucket_name: str = optional_field
    access_key_id: Optional[str] = optional_field
    secret_access_key: Optional[str] = optional_field
    region_name: Optional[str] = optional_field
    endpoint_url: Optional[str] = optional_field
    note: Optional[str] = optional_field
    context: Optional[dict] = optional_field
    disabled: bool = optional_field
    default: bool = optional_field
    read_only: bool = optional_field
    managed: bool = optional_field
    key_prefix: Optional[str] = optional_field


# Session Credentials


class ObjectStoreSessionCredentials(BaseModel):
    access_key_id: str = Field(
        ..., description="The access key ID used to access the object store's bucket."
    )
    secret_access_key: str = Field(
        ...,
        description="The secret access key used to access the object store's bucket.",
    )
    session_token: str = Field(
        ...,
        description="The session token used to access the object store's bucket.",
    )
    expiration: datetime = Field(
        ...,
        description="The expiration time of the session token.",
    )


class ObjectStoreSessionCredentialsDataResponse(
    DataResponseModel[ObjectStoreSessionCredentials]
):
    pass
