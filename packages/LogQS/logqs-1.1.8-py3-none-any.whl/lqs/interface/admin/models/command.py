from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class Command(BaseModel):
    action: str
    resource: Optional[str]
    app: Optional[str]
    datastore_id: Optional[UUID]
    kwargs: Optional[dict]
    process_states: Optional[List[str]]
    process_types: Optional[List[str]]


class CommandCreateRequest(BaseModel):
    action: str
    resource: Optional[str] = None
    app: Optional[str] = None
    datastore_id: Optional[UUID] = None
    kwargs: Optional[dict] = None
    process_states: Optional[List[str]] = None
    process_types: Optional[List[str]] = None


class CommandDataResponse(BaseModel):
    data: Optional[dict] = None
