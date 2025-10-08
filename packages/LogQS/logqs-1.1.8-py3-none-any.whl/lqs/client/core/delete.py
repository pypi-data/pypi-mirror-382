from uuid import UUID
from typing import Optional

from lqs.interface.core import DeleteInterface
from lqs.client.common import RESTInterface

# TODO: make this consistent with other interfaces


class Delete(DeleteInterface, RESTInterface):
    service: str = "lqs"

    def __init__(self, app):
        super().__init__(app=app)

    def _api_key(self, api_key_id: UUID):
        self._delete_resource(f"apiKeys/{api_key_id}")
        return

    def _callback(self, callback_id: UUID):
        self._delete_resource(f"callbacks/{callback_id}")
        return

    def _digestion(self, digestion_id: UUID, lock_token: Optional[str] = None):
        self._delete_resource(
            f"digestions/{digestion_id}",
            additiona_params={"lock_token": lock_token},
        )
        return

    def _digestion_part(
        self,
        digestion_part_id: UUID,
        digestion_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        if digestion_id is None:
            resource_path = f"digestionParts/{digestion_part_id}"
        else:
            resource_path = f"digestions/{digestion_id}/parts/{digestion_part_id}"
        self._delete_resource(
            resource_path,
            additiona_params={"lock_token": lock_token},
        )
        return

    def _digestion_topic(
        self,
        digestion_topic_id: UUID,
        digestion_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        if digestion_id is None:
            resource_path = f"digestionTopics/{digestion_topic_id}"
        else:
            resource_path = f"digestions/{digestion_id}/topics/{digestion_topic_id}"
        self._delete_resource(
            resource_path,
            additiona_params={"lock_token": lock_token},
        )
        return

    def _group(self, group_id: UUID, lock_token: Optional[str] = None):
        self._delete_resource(
            f"groups/{group_id}",
            additiona_params={"lock_token": lock_token},
        )
        return

    def _hook(self, hook_id: UUID, workflow_id: Optional[UUID] = None):
        if workflow_id is None:
            resource_path = f"hooks/{hook_id}"
        else:
            resource_path = f"workflows/{workflow_id}/hooks/{hook_id}"
        self._delete_resource(resource_path)
        return

    def _ingestion(self, ingestion_id: UUID, lock_token: Optional[str] = None):
        self._delete_resource(
            f"ingestions/{ingestion_id}",
            additiona_params={"lock_token": lock_token},
        )
        return

    def _ingestion_part(
        self,
        ingestion_part_id: UUID,
        ingestion_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        if ingestion_id is None:
            resource_path = f"ingestionParts/{ingestion_part_id}"
        else:
            resource_path = f"ingestions/{ingestion_id}/parts/{ingestion_part_id}"
        self._delete_resource(
            resource_path,
            additiona_params={"lock_token": lock_token},
        )
        return

    def _label(self, label_id: UUID):
        self._delete_resource(f"labels/{label_id}")
        return

    def _log(self, log_id: UUID, lock_token: Optional[str] = None):
        self._delete_resource(
            f"logs/{log_id}", additiona_params={"lock_token": lock_token}
        )
        return

    def _log_object(
        self, log_id: UUID, object_key: str, lock_token: Optional[str] = None
    ):
        self._delete_resource(
            f"logs/{log_id}/objects/{object_key}",
            additiona_params={"lock_token": lock_token},
        )
        return

    def _object(self, object_store_id: UUID, object_key: str):
        raise NotImplementedError

    def _object_store(self, object_store_id: UUID):
        self._delete_resource(f"objectStores/{object_store_id}")
        return

    def _query(
        self,
        query_id: UUID,
        log_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        if log_id is None:
            resource_path = f"queries/{query_id}"
        else:
            resource_path = f"logs/{log_id}/queries/{query_id}"
        self._delete_resource(
            resource_path,
            additiona_params={"lock_token": lock_token},
        )
        return

    def _record(
        self, timestamp: float, topic_id: UUID, lock_token: Optional[str] = None
    ):
        self._delete_resource(
            f"topics/{topic_id}/records/{timestamp}",
            additiona_params={"lock_token": lock_token},
        )
        return

    def _role(self, role_id: UUID):
        self._delete_resource(f"roles/{role_id}")
        return

    def _tag(
        self,
        tag_id: UUID,
        log_id: Optional[UUID] = None,
        lock_token: Optional[str] = None,
    ):
        if log_id is None:
            resource_path = f"tags/{tag_id}"
        else:
            resource_path = f"logs/{log_id}/tags/{tag_id}"
        self._delete_resource(
            resource_path,
            additiona_params={"lock_token": lock_token},
        )
        return

    def _topic(self, topic_id: UUID, lock_token: Optional[str] = None):
        self._delete_resource(
            f"topics/{topic_id}",
            additiona_params={"lock_token": lock_token},
        )
        return

    def _user(self, user_id: UUID):
        self._delete_resource(f"users/{user_id}")
        return

    def _workflow(self, workflow_id: UUID):
        self._delete_resource(f"workflows/{workflow_id}")
        return
