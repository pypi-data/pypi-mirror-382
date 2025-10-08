from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from lqs.interface.core.models.__common__ import (
    CommonModel,
    DataResponseModel,
    PaginationModel,
    optional_field,
)
from lqs.interface.core import models


class Label(CommonModel):
    value: str = Field(..., description="The value of the label")
    note: Optional[str] = Field(
        None, description="A general note about the label for reference."
    )
    category: Optional[str] = Field(
        None,
        description="The category of the label used to group labels of similar purpose.",
    )

    model_config = ConfigDict(
        json_schema_extra=lambda x: x["required"].extend(["note", "category"])
    )

    def list_tags(self, threaded=False, **kwargs) -> list["models.Tag"]:
        return self._list_all_subresources(
            list_method=self._app.list.tag,
            threaded=threaded,
            label_id=self.id,
            **kwargs,
        )


class LabelDataResponse(DataResponseModel[Label]):
    pass


class LabelListResponse(PaginationModel[Label]):
    pass


class LabelCreateRequest(BaseModel):
    value: str
    note: Optional[str] = None
    category: Optional[str] = None


class LabelUpdateRequest(BaseModel):
    value: str = optional_field
    note: Optional[str] = optional_field
    category: Optional[str] = optional_field
