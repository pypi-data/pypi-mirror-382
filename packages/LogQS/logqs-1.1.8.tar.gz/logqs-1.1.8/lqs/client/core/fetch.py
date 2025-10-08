from lqs.interface.core import FetchInterface
from lqs.client.common import RESTInterface
import lqs.interface.core.models as models


class Fetch(FetchInterface, RESTInterface):
    service: str = "lqs"

    def __init__(self, app):
        super().__init__(app=app)

    def _api_key(self, **params):
        api_key_id = params.pop("api_key_id")
        result = self._get_resource(
            f"apiKeys/{api_key_id}", response_model=models.APIKeyDataResponse
        )
        return result

    def _callback(self, **params):
        callback_id = params.pop("callback_id")
        result = self._get_resource(
            f"callbacks/{callback_id}", response_model=models.CallbackDataResponse
        )
        return result

    def _digestion(self, **params):
        digestion_id = params.pop("digestion_id")
        result = self._get_resource(
            f"digestions/{digestion_id}", response_model=models.DigestionDataResponse
        )
        return result

    def _digestion_part(self, **kwargs):
        digestion_id = kwargs.pop("digestion_id", None)
        digestion_part_id = kwargs.pop("digestion_part_id")
        if digestion_id is None:
            resource_path = f"digestionParts/{digestion_part_id}"
        else:
            resource_path = f"digestions/{digestion_id}/parts/{digestion_part_id}"
        result = self._get_resource(
            resource_path,
            response_model=models.DigestionPartDataResponse,
        )
        return result

    def _digestion_topic(self, **params):
        digestion_id = params.pop("digestion_id", None)
        digestion_topic_id = params.pop("digestion_topic_id")
        if digestion_id is None:
            resource_path = f"digestionTopics/{digestion_topic_id}"
        else:
            resource_path = f"digestions/{digestion_id}/topics/{digestion_topic_id}"
        result = self._get_resource(
            resource_path,
            response_model=models.DigestionTopicDataResponse,
        )
        return result

    def _group(self, **params):
        group_id = params.pop("group_id")
        result = self._get_resource(
            f"groups/{group_id}", response_model=models.GroupDataResponse
        )
        return result

    def _hook(self, **params):
        workflow_id = params.pop("workflow_id", None)
        hook_id = params.pop("hook_id")
        if workflow_id is None:
            resource_path = f"hooks/{hook_id}"
        else:
            resource_path = f"workflows/{workflow_id}/hooks/{hook_id}"
        result = self._get_resource(
            resource_path,
            response_model=models.HookDataResponse,
        )
        return result

    def _ingestion(self, **params):
        ingestion_id = params.pop("ingestion_id")
        result = self._get_resource(
            f"ingestions/{ingestion_id}", response_model=models.IngestionDataResponse
        )
        return result

    def _ingestion_part(self, **params):
        ingestion_id = params.pop("ingestion_id", None)
        ingestion_part_id = params.pop("ingestion_part_id")
        if ingestion_id is None:
            resource_path = f"ingestionParts/{ingestion_part_id}"
        else:
            resource_path = f"ingestions/{ingestion_id}/parts/{ingestion_part_id}"
        result = self._get_resource(
            resource_path,
            response_model=models.IngestionPartDataResponse,
        )
        return result

    def _label(self, **params):
        label_id = params.pop("label_id")
        result = self._get_resource(
            f"labels/{label_id}", response_model=models.LabelDataResponse
        )
        return result

    def _log(self, **params):
        log_id = params.pop("log_id")
        result = self._get_resource(
            f"logs/{log_id}", response_model=models.LogDataResponse
        )
        return result

    def _log_object(self, **params):
        log_id = params.pop("log_id")
        object_key = params.pop("object_key")

        resource_path = (
            f"logs/{log_id}/objects/{object_key}"
            + self._get_url_param_string(params, [])
        )

        if params.get("redirect", False):
            offset = params.pop("offset", None)
            length = params.pop("length", None)
            headers = {}
            if offset is not None:
                if length is not None:
                    headers["Range"] = f"bytes={offset}-{offset + length - 1}"
                else:
                    if offset < 0:
                        headers["Range"] = f"bytes={offset}"
                    else:
                        headers["Range"] = f"bytes={offset}-"
            elif length is not None:
                headers["Range"] = f"bytes=0-{length - 1}"
            result = self._get_resource(
                resource_path, expected_content_type=None, additional_headers=headers
            )
        else:
            result = self._get_resource(
                resource_path, response_model=models.ObjectDataResponse
            )
        return result

    def _log_object_part(self, **params):
        log_id = params.pop("log_id")
        object_key = params.pop("object_key")
        part_number = params.pop("part_number")
        result = self._get_resource(
            f"logs/{log_id}/objects/{object_key}/parts/{part_number}",
            response_model=models.ObjectPartDataResponse,
        )
        return result

    def _me(self, **params):
        result = self._get_resource("users/me", response_model=models.MeDataResponse)
        return result

    def _object(self, **params):
        object_store_id = params.pop("object_store_id")
        object_key = params.pop("object_key")

        resource_path = (
            f"objectStores/{object_store_id}/objects/{object_key}"
            + self._get_url_param_string(params, [])
        )

        if params.get("redirect", False):
            offset = params.pop("offset", None)
            length = params.pop("length", None)
            headers = {}
            if offset is not None:
                if length is not None:
                    headers["Range"] = f"bytes={offset}-{offset + length - 1}"
                else:
                    if offset < 0:
                        headers["Range"] = f"bytes={offset}"
                    else:
                        headers["Range"] = f"bytes={offset}-"
            elif length is not None:
                headers["Range"] = f"bytes=0-{length - 1}"
            result = self._get_resource(
                resource_path, expected_content_type=None, additional_headers=headers
            )
        else:
            result = self._get_resource(
                resource_path, response_model=models.ObjectDataResponse
            )
        return result

    def _object_part(self, **params):
        raise NotImplementedError

    def _object_store(self, **params):
        object_store_id = params.pop("object_store_id")
        result = self._get_resource(
            f"objectStores/{object_store_id}",
            response_model=models.ObjectStoreDataResponse,
        )
        return result

    def _object_store_session_credentials(self, **params):
        object_store_id = params.pop("object_store_id")
        result = self._get_resource(
            f"objectStores/{object_store_id}/sessionCredentials",
            response_model=models.ObjectStoreSessionCredentialsDataResponse,
        )
        return result

    def _query(self, **params):
        log_id = params.pop("log_id", None)
        query_id = params.pop("query_id")
        if log_id is None:
            resource_path = f"queries/{query_id}"
        else:
            resource_path = f"logs/{log_id}/queries/{query_id}"
        result = self._get_resource(
            resource_path, response_model=models.QueryDataResponse
        )
        return result

    def _record(self, **params):
        topic_id = params.pop("topic_id")
        timestamp = params.pop("timestamp")
        url_params = self._get_url_param_string(params, [])
        result = self._get_resource(
            f"topics/{topic_id}/records/{timestamp}" + url_params,
            response_model=models.RecordDataResponse,
        )
        return result

    def _role(self, **params):
        role_id = params.pop("role_id")
        result = self._get_resource(
            f"roles/{role_id}", response_model=models.RoleDataResponse
        )
        return result

    def _tag(self, **params):
        log_id = params.pop("log_id", None)
        tag_id = params.pop("tag_id")
        if log_id is None:
            resource_path = f"tags/{tag_id}"
        else:
            resource_path = f"logs/{log_id}/tags/{tag_id}"
        result = self._get_resource(
            resource_path, response_model=models.TagDataResponse
        )
        return result

    def _topic(self, **params):
        topic_id = params.pop("topic_id")
        result = self._get_resource(
            f"topics/{topic_id}", response_model=models.TopicDataResponse
        )
        return result

    def _user(self, **params):
        user_id = params.pop("user_id")
        result = self._get_resource(
            f"users/{user_id}", response_model=models.UserDataResponse
        )
        return result

    def _workflow(self, **params):
        workflow_id = params.pop("workflow_id")
        result = self._get_resource(
            f"workflows/{workflow_id}", response_model=models.WorkflowDataResponse
        )
        return result
