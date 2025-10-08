from lqs.interface.core import ListInterface
from lqs.client.common import RESTInterface
import lqs.interface.core.models as models


class List(ListInterface, RESTInterface):
    service: str = "lqs"

    def __init__(self, app):
        super().__init__(app=app)

    def _api_key(self, **params):
        resource_path = "apiKeys" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.APIKeyListResponse
        )
        return result

    def _callback(self, **params):
        resource_path = "callbacks" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.CallbackListResponse
        )
        return result

    def _digestion(self, **params):
        resource_path = "digestions" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.DigestionListResponse
        )
        return result

    def _digestion_part(self, **params):
        digestion_id = params.pop("digestion_id", None)
        if digestion_id is None:
            url = "digestionParts"
        else:
            url = f"digestions/{digestion_id}/parts"
        resource_path = url + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.DigestionPartListResponse
        )
        return result

    def _digestion_topic(self, **params):
        digestion_id = params.pop("digestion_id", None)
        if digestion_id is None:
            url = "digestionTopics"
        else:
            url = f"digestions/{digestion_id}/topics"
        resource_path = url + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.DigestionTopicListResponse
        )
        return result

    def _group(self, **params):
        resource_path = "groups" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.GroupListResponse
        )
        return result

    def _hook(self, **params):
        workflow_id = params.pop("workflow_id", None)
        if workflow_id is None:
            url = "hooks"
        else:
            url = f"workflows/{workflow_id}/hooks"
        resource_path = url + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.HookListResponse
        )
        return result

    def _ingestion(self, **params):
        resource_path = "ingestions" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.IngestionListResponse
        )
        return result

    def _ingestion_part(self, **params):
        ingestion_id = params.pop("ingestion_id", None)
        if ingestion_id is None:
            url = "ingestionParts"
        else:
            url = f"ingestions/{ingestion_id}/parts"
        resource_path = url + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.IngestionPartListResponse
        )
        return result

    def _label(self, **params):
        resource_path = "labels" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.LabelListResponse
        )
        return result

    def _log(self, **params):
        resource_path = "logs" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.LogListResponse
        )
        return result

    def _log_object(self, **params):
        log_id = params.pop("log_id")
        resource_path = f"logs/{log_id}/objects" + self._get_url_param_string(
            params, []
        )
        result = self._get_resource(
            resource_path, response_model=models.ObjectListResponse
        )
        return result

    def _log_object_part(self, **params):
        log_id = params.pop("log_id")
        object_key = params.pop("object_key")
        resource_path = (
            f"logs/{log_id}/objects/{object_key}/parts"
            + self._get_url_param_string(params, [])
        )
        result = self._get_resource(
            resource_path, response_model=models.ObjectPartListResponse
        )
        return result

    def _object(self, **params):
        object_store_id = params.pop("object_store_id")
        resource_path = (
            f"objectStores/{object_store_id}/objects"
            + self._get_url_param_string(params, [])
        )
        result = self._get_resource(
            resource_path, response_model=models.ObjectListResponse
        )
        return result

    def _object_part(self, **params):
        raise NotImplementedError

    def _object_store(self, **params):
        resource_path = "objectStores" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.ObjectStoreListResponse
        )
        return result

    def _query(self, **params):
        log_id = params.pop("log_id", None)
        if log_id is None:
            url = "queries"
        else:
            url = f"logs/{log_id}/queries"
        resource_path = url + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.QueryListResponse
        )
        return result

    def _record(self, **params):
        topic_id = params.pop("topic_id")
        resource_path = f"topics/{topic_id}/records" + self._get_url_param_string(
            params, []
        )
        result = self._get_resource(
            resource_path, response_model=models.RecordListResponse
        )
        return result

    def _role(self, **params):
        resource_path = "roles" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.RoleListResponse
        )
        return result

    def _tag(self, **params):
        log_id = params.pop("log_id", None)
        if log_id is None:
            url = "tags"
        else:
            url = f"logs/{log_id}/tags"
        resource_path = url + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.TagListResponse
        )
        return result

    def _topic(self, **params):
        resource_path = "topics" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.TopicListResponse
        )
        return result

    def _user(self, **params):
        resource_path = "users" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.UserListResponse
        )
        return result

    def _workflow(self, **params):
        resource_path = "workflows" + self._get_url_param_string(params, [])
        result = self._get_resource(
            resource_path, response_model=models.WorkflowListResponse
        )
        return result
