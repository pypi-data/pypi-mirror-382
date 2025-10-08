import re
from typing import (
    Iterator,
    List,
    Optional,
    Union,
    TypeVar,
    Generic,
    Type,
    Annotated,
    Any,
)
from datetime import datetime
from uuid import UUID
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    WithJsonSchema,
    SerializerFunctionWrapHandler,
    WrapSerializer,
    SerializationInfo,
)

from fastapi import Path
import cattrs.preconf.json

converter = cattrs.preconf.json.make_converter()
converter.register_unstructure_hook(
    cls=int, func=lambda x: str(x) if x > 2**53 else x
)

optional_field = Field(default=None, json_schema_extra=lambda x: x.pop("default"))
optional_deprecated_field = Field(
    default=None, deprecated=True, json_schema_extra=lambda x: x.pop("default")
)


def special_dict_wrap(
    v: Any, nxt: SerializerFunctionWrapHandler, info: SerializationInfo
):
    if info.context and info.context.get("stringify_bigints", False):
        return converter.unstructure(v)
    return nxt(v)


def big_int_wrap(
    v: Any, nxt: SerializerFunctionWrapHandler, info: SerializationInfo
) -> Union[str, int]:
    if info.context and info.context.get("stringify_bigints", False):
        return str(v)
    return nxt(v)


SpecialDict = Annotated[
    dict,
    dict,
    WrapSerializer(special_dict_wrap, when_used="json"),
]


Int64 = Annotated[
    int,
    int,
    WithJsonSchema({"type": "integer", "format": "int64"}),
    WrapSerializer(big_int_wrap, when_used="json"),
    Path(json_schema_extra={"type": "integer", "format": "int64"}),
]


def optional_field_alt(description: str):
    return Field(
        default=None,
        json_schema_extra=lambda x: x.pop("default"),
        description=description,
    )


def convert_camel_to_snake_case(camel_string: str) -> str:
    return re.sub("(.)([A-Z])", r"\1_\2", camel_string).lower()


class EmptyModel(BaseModel):
    pass


T = TypeVar("T", bound="ResourceModel")


class ResourceModel(BaseModel, Generic[T]):
    _app: Any = None
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def _describe(cls, return_description: bool = False):
        description = f"{cls.__name__}:\n"
        model_field_items = cls.model_fields.items()

        # reorganize the fields so that the common fields are at the top
        top_fields = ("id", "timestamp")
        bottom_fields = (
            "created_at",
            "updated_at",
            "deleted_at",
            "created_by",
            "updated_by",
            "deleted_by",
        )
        model_field_items = sorted(
            model_field_items,
            key=lambda x: (
                0 if x[0] in top_fields else 1,
                1 if x[0] in bottom_fields else 0,
                x[0],
            ),
        )

        for field_name, field_info in model_field_items:
            if field_name in ResourceModel.model_fields:
                continue

            field_type = field_info.annotation
            if hasattr(field_type, "__args__"):
                raw_sub_type_name = str(field_type.__args__[0])
                if "typing.Annotated[int" in raw_sub_type_name:
                    sub_type_name = "int"
                else:
                    sub_type_name = raw_sub_type_name
                if str(field_type).startswith("typing."):
                    type_name = str(field_type)[7:]
                else:
                    type_name = field_type.__name__
                type_name = type_name.replace(raw_sub_type_name, sub_type_name)
            elif str(field_type).startswith("typing."):
                type_name = str(field_type)[7:]
            else:
                type_name = field_type.__name__
            type_name = re.sub(r"(\w+\.)+", "", type_name)

            field_title = f"{field_name} [{type_name}]"
            buffer_length = 38 - len(field_title)
            description += (
                f"{field_title}: {' ' * buffer_length}{field_info.description or ''}\n"
            )
        description = description[:-1]
        if return_description:
            return description
        else:
            print(description)

    _repr_fields = ("id", "name")

    def __repr__(self):
        model_name = self.__class__.__name__
        value = f"<{model_name} "
        for field_name in self._repr_fields:
            if field_name in self.model_fields:
                value += f"{field_name}={getattr(self, field_name)}, "
        value = value[:-2] + ">"
        return value

    @classmethod
    def set_app(cls, app):
        cls._app = app

    @classmethod
    def fetch(cls: Type[T], *args, **kwargs) -> T:
        id = None
        friendly_id = None
        parent_id = None
        if len(args) > 0:
            try:
                if type(args[0]) is UUID:
                    id = args[0]
                elif type(args[0]) is int:
                    id = int(args[0])
                else:
                    id = UUID(args[0])
            except ValueError:
                friendly_id = args[0]
            if len(args) > 1:
                try:
                    if type(args[1]) is UUID:
                        parent_id = args[1]
                    else:
                        parent_id = UUID(args[1])
                except ValueError:
                    raise ValueError(
                        "Second argument must be the UUID of the parent resource."
                    )

        if "id" in kwargs:
            id = kwargs["id"]

        if id is not None:
            fetch_method = getattr(
                cls._app.fetch, convert_camel_to_snake_case(cls.__name__)
            )
            if parent_id is not None:
                return fetch_method(id, parent_id, **kwargs).data
            else:
                return fetch_method(id, **kwargs).data
        else:
            list_method = getattr(
                cls._app.list, convert_camel_to_snake_case(cls.__name__)
            )

            list_args = {
                "order": "created_at",
                "sort": "desc",
                "limit": 1,
            }
            list_args.update(kwargs)
            if friendly_id is not None:
                fields = cls._repr_fields.default
                if len(fields) < 2:
                    raise Exception(f"Cannot fetch {cls.__name__} without it's ID.")
                list_args[fields[1]] = friendly_id

            if parent_id is not None:
                list_res = list_method(parent_id, **list_args)
            else:
                list_res = list_method(**list_args)
            if list_res.count == 0:
                raise ValueError(f"No {cls.__name__} found.")
            elif list_res.count > 1:
                try:
                    cls._app.logger.warning(
                        f"Multiple {cls.__name__}s ({list_res.count}) found."
                    )
                except AttributeError:
                    pass
            return list_res.data[0]

    @classmethod
    def first(cls: Type[T], **kwargs) -> T:
        kwargs["order"] = kwargs.get("order", "created_at")
        kwargs["sort"] = kwargs.get("sort", "asc")
        kwargs["limit"] = 1
        return cls.list(**kwargs)[0]

    @classmethod
    def list(cls: Type[T], **kwargs) -> List[T]:
        list_method = getattr(cls._app.list, convert_camel_to_snake_case(cls.__name__))
        return list_method(**kwargs).data

    @classmethod
    def list_all(cls: Type[T], **kwargs) -> List[T]:
        list_method = getattr(cls._app.list, convert_camel_to_snake_case(cls.__name__))
        offset = kwargs.pop("offset", 0)
        limit = kwargs.pop("limit", 100)
        total_count = float("inf")
        resources = []

        while len(resources) < total_count:
            res = list_method(**kwargs, offset=offset, limit=limit)
            total_count = res.count
            resources.extend(res.data)
            offset += limit

        return resources

    @classmethod
    def iterate_efficiently(cls: Type[T], **kwargs) -> Iterator[T]:
        MAX_LIMIT = 100
        order = kwargs.get("order", "created_at")
        assert order == "created_at"
        sort = kwargs.pop("sort", "desc")
        if kwargs.pop("offset", None):
            raise Exception("Can't use offsets with this method")
        limit = kwargs.pop("limit", float("inf"))
        yields_left = limit
        created_at_target = None
        kwargs["include_count"] = False
        while yields_left > 0:
            _limit = min(MAX_LIMIT, yields_left)
            if created_at_target is not None:
                if sort == "desc":
                    created_at_target -= datetime.resolution
                    kwargs["created_at_lte"] = created_at_target
                else:
                    created_at_target += datetime.resolution
                    kwargs["created_at_gte"] = created_at_target
            res = cls.list(**kwargs, limit=_limit, sort=sort)
            if len(res) == 0:
                return
            # this may break when too many records have the same created_at, although it's pretty unlikely
            created_at_target: datetime = res[-1].created_at
            yields_left -= len(res)
            for i in res:
                yield i

    @classmethod
    def iterate(cls: Type[T], **kwargs) -> Iterator[T]:
        MAX_LIMIT = 100
        limit = kwargs.pop("limit", float("inf"))
        if not limit or limit > MAX_LIMIT:
            _limit = MAX_LIMIT
            _offset = kwargs.pop("offset", 0)
            yielded_count = 0
            while yielded_count < limit:
                res = cls.list(**kwargs, limit=_limit, offset=_offset)
                for i in res:
                    yield i
                if len(res) < _limit:
                    return
                _offset += _limit
                yielded_count += limit
        else:
            return iter(cls.list(**kwargs))

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        create_method = getattr(
            cls._app.create, convert_camel_to_snake_case(cls.__name__)
        )
        return create_method(**kwargs).data

    def update(self, **kwargs) -> T:
        # get the class name and convert it to snake case
        class_name = convert_camel_to_snake_case(self.__class__.__name__)
        update_method = getattr(self._app.update, class_name)
        updated_resource = update_method(self.id, data=kwargs).data
        for field, value in updated_resource.dict().items():
            # check that the field is a pydantic field
            if field in self.model_fields:
                # set the value of the field
                setattr(self, field, value)
        return self

    @classmethod
    def delete(cls, **kwargs) -> None:
        delete_method = getattr(
            cls._app.delete, convert_camel_to_snake_case(cls.__name__)
        )
        return delete_method(**kwargs)

    @classmethod
    def fetch_or_create(cls, **kwargs):
        try:
            return cls.fetch(**kwargs)
        except Exception:
            return cls.create(**kwargs)

    def refresh(self):
        refreshed_resource = self.fetch(self.id)
        for field, value in refreshed_resource.model_dump().items():
            if field in self.model_fields:
                setattr(self, field, value)
        return self

    def _list_all_subresources(self, list_method, threaded=True, **kwargs):
        if threaded:
            return self._list_all_subresources_threaded(list_method, **kwargs)
        else:
            return self._list_all_subresources_single(list_method, **kwargs)

    def _list_all_subresources_single(self, list_method, **kwargs):
        subresources = []
        total_limit = kwargs.pop("limit", None)
        limit = 100 if total_limit is None else min(100, total_limit)
        offset = 0
        kwargs["limit"] = limit
        kwargs["offset"] = offset
        while True:
            res = list_method(**kwargs)
            subresources.extend(res.data)
            if len(res.data) < limit:
                break
            if total_limit is not None:
                total_limit -= limit
                if total_limit <= 0:
                    break
            offset += limit
            kwargs["offset"] = offset
        return subresources

    def _list_all_subresources_threaded(self, list_method, **kwargs):
        count_kwargs = kwargs.copy()
        count_kwargs["include_count"] = True
        count_kwargs["limit"] = 0
        count_kwargs["offset"] = 0
        count = list_method(**count_kwargs).count
        if count == 0:
            return []

        subresources = []
        total_limit = kwargs.pop("limit", None)
        limit = 100 if total_limit is None else min(100, total_limit)
        offset = 0
        kwargs["limit"] = limit
        kwargs["offset"] = offset
        with ThreadPoolExecutor() as executor:
            futures = []
            while offset < count:
                futures.append(executor.submit(list_method, **kwargs))
                offset += limit
                kwargs["offset"] = offset
                if total_limit is not None:
                    total_limit -= limit
                    if total_limit <= 0:
                        break
            for future in futures:
                res = future.result()
                subresources.extend(res.data)
        return subresources


class CommonModel(ResourceModel[T]):
    id: UUID = Field(..., description="The ID of the resource.")

    created_at: datetime = Field(
        ..., description="The creation timestamp of the resource."
    )
    updated_at: Optional[datetime] = Field(
        ..., description="The last update timestamp of the resource."
    )
    deleted_at: Optional[datetime] = Field(
        ..., description="The deletion timestamp of the resource."
    )
    created_by: Optional[UUID] = Field(
        ..., description="The ID of the user who created the resource."
    )
    updated_by: Optional[UUID] = Field(
        ..., description="The ID of the user who last updated the resource."
    )
    deleted_by: Optional[UUID] = Field(
        ..., description="The ID of the user who deleted the resource."
    )


class TimeSeriesModel(ResourceModel[T]):
    _repr_fields = ("timestamp",)

    timestamp: Int64 = Field(..., description="The timestamp of the resource.")

    created_at: datetime = Field(
        ..., description="The creation timestamp of the resource."
    )
    updated_at: Optional[datetime] = Field(
        ..., description="The last update timestamp of the resource."
    )
    deleted_at: Optional[datetime] = Field(
        ..., description="The deletion timestamp of the resource."
    )
    created_by: Optional[UUID] = Field(
        ..., description="The ID of the user who created the resource."
    )
    updated_by: Optional[UUID] = Field(
        ..., description="The ID of the user who last updated the resource."
    )
    deleted_by: Optional[UUID] = Field(
        ..., description="The ID of the user who deleted the resource."
    )


BaseElement = TypeVar("BaseElement", bound=BaseModel)


class DataResponseModel(BaseModel, Generic[BaseElement]):
    data: BaseElement


class PaginationModel(BaseModel, Generic[BaseElement]):
    offset: int
    limit: int
    order: str
    sort: str
    count: Optional[int]
    data: List[BaseElement]


class PatchOperation(BaseModel):
    op: str
    path: str
    value: Optional[Union[str, int, float, bool, dict, list, None]]


class JSONFilter(BaseModel):
    var: str
    op: str
    val: Union[str, int, float, bool, list, None]


class UploadState(str, Enum):
    complete = "complete"
    processing = "processing"
    aborted = "aborted"
