from lqs.interface.dsm import UpdateInterface
from lqs.client.common import RESTInterface
import lqs.interface.dsm.models as models


class Update(UpdateInterface, RESTInterface):
    service: str = "dsm"

    def __init__(self, app):
        super().__init__(app=app)

    def _announcement(self, **params):
        announcement_id = params.pop("announcement_id")
        data = params.pop("data")
        return self._update_resource(
            f"announcements/{announcement_id}",
            data,
            models.AnnouncementDataResponse,
        )

    def _api_key(self, **params):
        api_key_id = params.pop("api_key_id")
        data = params.pop("data")
        return self._update_resource(
            f"apiKeys/{api_key_id}", data, models.APIKeyDataResponse
        )

    def _comment(self, **params):
        comment_id = params.pop("comment_id")
        data = params.pop("data")
        return self._update_resource(
            f"comments/{comment_id}", data, models.CommentDataResponse
        )

    def _configuration(self, **params):
        configuration_id = params.pop("configuration_id")
        data = params.pop("data")
        return self._update_resource(
            f"configurations/{configuration_id}",
            data,
            models.ConfigurationDataResponse,
        )

    def _datastore(self, **params):
        datastore_id = params.pop("datastore_id")
        data = params.pop("data")
        return self._update_resource(
            f"dataStores/{datastore_id}", data, models.DataStoreDataResponse
        )

    def _datastore_association(self, **params):
        datastore_association_id = params.pop("datastore_association_id")
        data = params.pop("data")
        return self._update_resource(
            f"dataStoreAssociations/{datastore_association_id}",
            data,
            models.DataStoreAssociationDataResponse,
        )

    def _event(self, **params):
        event_id = params.pop("event_id")
        data = params.pop("data")
        return self._update_resource(
            f"events/{event_id}", data, models.EventDataResponse
        )

    def _job(self, **params):
        job_id = params.pop("job_id")
        data = params.pop("data")
        return self._update_resource(f"jobs/{job_id}", data, models.JobDataResponse)

    def _role(self, **params):
        role_id = params.pop("role_id")
        data = params.pop("data")
        return self._update_resource(f"roles/{role_id}", data, models.RoleDataResponse)

    def _user(self, **params):
        user_id = params.pop("user_id")
        data = params.pop("data")
        return self._update_resource(f"users/{user_id}", data, models.UserDataResponse)
