import io
import json
from typing import List, Optional, Union

from pydantic import BaseModel
from lqs.interface.base.models import Int64


class JSONLHeader(BaseModel):
    is_header: bool

    log_name: str
    log_note: Optional[str] = None
    log_context: Optional[dict] = None

    group_name: str
    group_note: Optional[str] = None
    group_context: Optional[dict] = None

    extra: Optional[dict] = None


class JSONLTopicRow(BaseModel):
    is_topic_row: bool
    is_default_topic: bool

    topic_name: str
    topic_type_name: Optional[str] = None
    topic_type_schema: Optional[dict] = None
    topic_note: Optional[str] = None
    topic_context: Optional[dict] = None
    associated_topic_name: Optional[str] = None
    extra: Optional[dict] = None


class JSONLRecordRow(BaseModel):
    timestamp: Int64
    data: Union[dict, list]
    topic_name: Optional[str] = None
    extra: Optional[dict] = None


class JSONLLog(BaseModel):
    name: Optional[str] = None
    header: Optional[JSONLHeader] = None
    rows: List[Union[JSONLTopicRow, JSONLRecordRow]] = []

    def write_jsonl_file_like(self, f=None):
        if f is None:
            f = io.StringIO()
        if self.header:
            f.write(self.header.model_dump_json(exclude_unset=True))
            f.write("\n")
        for line in self.rows:
            if isinstance(line, dict):
                # write this as compressed as possible
                f.write(json.dumps(line, separators=(",", ":")))
            else:
                f.write(line.model_dump_json(exclude_unset=True))
            f.write("\n")
        f.seek(0)
        return f

    def write_jsonl_file(self, file_path=None):
        if file_path is None:
            if self.name is None:
                raise Exception("No file path provided and no name set.")
            file_path = f"{self.name}.jsonl"

        with open(file_path, "w") as f:
            if self.header:
                f.write(self.header.model_dump_json(exclude_unset=True))
                f.write("\n")
            for line in self.rows:
                if isinstance(line, dict):
                    f.write(json.dumps(line, separators=(",", ":")))
                else:
                    f.write(line.model_dump_json(exclude_unset=True))
                f.write("\n")

    def get_jsonl_data(self):
        lines = []
        if self.header:
            lines.append(self.header.model_dump_json(exclude_unset=True))
        for line in self.rows:
            lines.append(line.model_dump_json(exclude_unset=True))
        return "\n".join(lines).encode("utf-8")

    def load_jsonl_file(self, file_path: str, name: Optional[str] = None):
        self.name = name
        self.header = None
        self.rows = []
        if name is None:
            name = file_path.split("/")[-1].split(".")[0]
        with open(file_path, "r") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                data = json.loads(line)
                if idx == 0 and data.get("is_header"):
                    self.header = JSONLHeader(**data)
                elif data.get("is_topic_row"):
                    self.rows.append(JSONLTopicRow(**data))
                else:
                    self.rows.append(JSONLRecordRow(**data))
        return self
