from typing import List
from pydantic import BaseModel


class ManifestEntry(BaseModel):
    source: str


class Manifest(BaseModel):
    entries: List[ManifestEntry]
