from lqs.interface.core import UpdateInterface
from lqs.client.common import RESTInterface
import lqs.interface.core.models as models


class Update(UpdateInterface, RESTInterface):
    service: str = "lqs"

    def __init__(self, app):
        super().__init__(app=app)

    def _api_key(self, **params):
        api_key_id = params.pop("api_key_id")
        data = params.pop("data")
        return self._update_resource(
            f"apiKeys/{api_key_id}", data, models.APIKeyDataResponse
        )

    def _callback(self, **params):
        callback_id = params.pop("callback_id")
        data = params.pop("data")
        return self._update_resource(
            f"callbacks/{callback_id}", data, models.CallbackDataResponse
        )

    def _digestion(self, **params):
        digestion_id = params.pop("digestion_id")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        return self._update_resource(
            f"digestions/{digestion_id}",
            data,
            models.DigestionDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _digestion_part(self, **params):
        digestion_id = params.pop("digestion_id", None)
        digestion_part_id = params.pop("digestion_part_id")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        if digestion_id is None:
            url = f"digestionParts/{digestion_part_id}"
        else:
            url = f"digestions/{digestion_id}/parts/{digestion_part_id}"
        return self._update_resource(
            url,
            data,
            models.DigestionPartDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _digestion_topic(self, **params):
        digestion_id = params.pop("digestion_id", None)
        digestion_topic_id = params.pop("digestion_topic_id")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        if digestion_id is None:
            url = f"digestionTopics/{digestion_topic_id}"
        else:
            url = f"digestions/{digestion_id}/topics/{digestion_topic_id}"
        return self._update_resource(
            url,
            data,
            models.DigestionTopicDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _group(self, **params):
        group_id = params.pop("group_id")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        return self._update_resource(
            f"groups/{group_id}",
            data,
            models.GroupDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _hook(self, **params):
        workflow_id = params.pop("workflow_id", None)
        hook_id = params.pop("hook_id")
        data = params.pop("data")
        if workflow_id is None:
            url = f"hooks/{hook_id}"
        else:
            url = f"workflows/{workflow_id}/hooks/{hook_id}"
        return self._update_resource(url, data, models.HookDataResponse)

    def _ingestion(self, **params):
        ingestion_id = params.pop("ingestion_id")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        return self._update_resource(
            f"ingestions/{ingestion_id}",
            data,
            models.IngestionDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _ingestion_part(self, **params):
        ingestion_id = params.pop("ingestion_id", None)
        ingestion_part_id = params.pop("ingestion_part_id")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        if ingestion_id is None:
            url = f"ingestionParts/{ingestion_part_id}"
        else:
            url = f"ingestions/{ingestion_id}/parts/{ingestion_part_id}"
        return self._update_resource(
            url,
            data,
            models.IngestionPartDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _label(self, **params):
        label_id = params.pop("label_id")
        data = params.pop("data")
        return self._update_resource(
            f"labels/{label_id}", data, models.LabelDataResponse
        )

    def _log(self, **params):
        log_id = params.pop("log_id")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        return self._update_resource(
            f"logs/{log_id}",
            data,
            models.LogDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _log_object(self, **params):
        log_id = params.pop("log_id")
        object_key = params.pop("object_key")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        return self._update_resource(
            f"logs/{log_id}/objects/{object_key}",
            data,
            models.ObjectDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _object(self, **params):
        raise NotImplementedError

    def _object_store(self, **params):
        object_store_id = params.pop("object_store_id")
        data = params.pop("data")
        return self._update_resource(
            f"objectStores/{object_store_id}", data, models.ObjectStoreDataResponse
        )

    def _query(self, **params):
        log_id = params.pop("log_id", None)
        query_id = params.pop("query_id")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        if log_id is None:
            url = f"queries/{query_id}"
        else:
            url = f"logs/{log_id}/queries/{query_id}"
        return self._update_resource(
            url,
            data,
            models.QueryDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _record(self, **params):
        topic_id = params.pop("topic_id")
        timestamp = params.pop("timestamp")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        return self._update_resource(
            f"topics/{topic_id}/records/{timestamp}",
            data,
            models.RecordDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _role(self, **params):
        role_id = params.pop("role_id")
        data = params.pop("data")
        return self._update_resource(f"roles/{role_id}", data, models.RoleDataResponse)

    def _tag(self, **params):
        log_id = params.pop("log_id", None)
        tag_id = params.pop("tag_id")
        lock_token = params.pop("lock_token", None)
        data = params.pop("data")
        if log_id is None:
            url = f"tags/{tag_id}"
        else:
            url = f"logs/{log_id}/tags/{tag_id}"
        return self._update_resource(
            url,
            data,
            models.TagDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _topic(self, **params):
        topic_id = params.pop("topic_id")
        data = params.pop("data")
        lock_token = params.pop("lock_token", None)
        return self._update_resource(
            f"topics/{topic_id}",
            data,
            models.TopicDataResponse,
            additiona_params={"lock_token": lock_token},
        )

    def _user(self, **params):
        user_id = params.pop("user_id")
        data = params.pop("data")
        return self._update_resource(f"users/{user_id}", data, models.UserDataResponse)

    def _workflow(self, **params):
        workflow_id = params.pop("workflow_id")
        data = params.pop("data")
        return self._update_resource(
            f"workflows/{workflow_id}", data, models.WorkflowDataResponse
        )
