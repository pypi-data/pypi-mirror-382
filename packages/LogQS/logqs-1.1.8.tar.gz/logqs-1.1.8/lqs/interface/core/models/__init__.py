from lqs.interface.core.models.api_key import *
from lqs.interface.core.models.callback import *
from lqs.interface.core.models.digestion import *
from lqs.interface.core.models.digestion_part import *
from lqs.interface.core.models.digestion_topic import *

from lqs.interface.core.models.hook import *
from lqs.interface.core.models.ingestion import *
from lqs.interface.core.models.ingestion_part import *
from lqs.interface.core.models.label import *

from lqs.interface.core.models.record import (
    Record,
    RecordDataResponse,
    RecordListResponse,
    RecordCreateRequest,
    RecordUpdateRequest,
)
from lqs.interface.core.models.topic import (
    Topic,
    TopicDataResponse,
    TopicListResponse,
    TopicCreateRequest,
    TopicUpdateRequest,
)
from lqs.interface.core.models.log import (
    Log,
    LogDataResponse,
    LogListResponse,
    LogCreateRequest,
    LogUpdateRequest,
)
from lqs.interface.core.models.group import (
    Group,
    GroupDataResponse,
    GroupListResponse,
    GroupCreateRequest,
    GroupUpdateRequest,
)

from lqs.interface.core.models.object import *
from lqs.interface.core.models.object_store import *
from lqs.interface.core.models.query import *

from lqs.interface.core.models.role import *
from lqs.interface.core.models.tag import *

from lqs.interface.core.models.user import *
from lqs.interface.core.models.workflow import *

from lqs.interface.core.models.jsonl import *
from lqs.interface.core.models.__common__ import *


class Resources:
    APIKey = APIKey
    Callback = Callback
    Digestion = Digestion
    DigestionPart = DigestionPart
    DigestionTopic = DigestionTopic
    Group = Group
    Hook = Hook
    Ingestion = Ingestion
    IngestionPart = IngestionPart
    Label = Label
    Log = Log
    Object = Object
    ObjectStore = ObjectStore
    Query = Query
    Record = Record
    Role = Role
    Tag = Tag
    Topic = Topic
    User = User
    Workflow = Workflow
