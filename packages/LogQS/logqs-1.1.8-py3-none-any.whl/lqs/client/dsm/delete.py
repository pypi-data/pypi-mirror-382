from uuid import UUID

from lqs.interface.dsm import DeleteInterface
from lqs.client.common import RESTInterface

# TODO: make this consistent with other interfaces


class Delete(DeleteInterface, RESTInterface):
    service: str = "dsm"

    def __init__(self, app):
        super().__init__(app=app)

    def _announcement(self, announcement_id: UUID):
        self._delete_resource(f"announcements/{announcement_id}")
        return

    def _api_key(self, api_key_id: UUID):
        self._delete_resource(f"apiKeys/{api_key_id}")
        return

    def _comment(self, comment_id: UUID):
        self._delete_resource(f"comments/{comment_id}")
        return

    def _configuration(self, configuration_id: UUID):
        self._delete_resource(f"configurations/{configuration_id}")
        return

    def _datastore(self, datastore_id: UUID):
        self._delete_resource(f"dataStores/{datastore_id}")
        return

    def _datastore_association(self, datastore_association_id: UUID):
        self._delete_resource(f"dataStoreAssociations/{datastore_association_id}")
        return

    def _event(self, event_id: UUID):
        self._delete_resource(f"events/{event_id}")
        return

    def _job(self, job_id: UUID):
        self._delete_resource(f"jobs/{job_id}")
        return

    def _role(self, role_id: UUID):
        self._delete_resource(f"roles/{role_id}")
        return

    def _user(self, user_id: UUID):
        self._delete_resource(f"users/{user_id}")
        return
