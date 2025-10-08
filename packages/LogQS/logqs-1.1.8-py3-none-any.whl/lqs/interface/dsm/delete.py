from abc import abstractmethod
from uuid import UUID

from lqs.interface.base.delete import DeleteInterface as BaseDeleteInterface


class DeleteInterface(BaseDeleteInterface):
    @abstractmethod
    def _announcement(self, **kwargs):
        pass

    def announcement(self, announcement_id: UUID):
        return self._announcement(
            announcement_id=announcement_id,
        )

    @abstractmethod
    def _comment(self, **kwargs):
        pass

    def comment(self, comment_id: UUID):
        return self._comment(
            comment_id=comment_id,
        )

    @abstractmethod
    def _configuration(self, **kwargs):
        pass

    def configuration(self, configuration_id: UUID):
        return self._configuration(
            configuration_id=configuration_id,
        )

    @abstractmethod
    def _datastore(self, **kwargs):
        pass

    def datastore(self, datastore_id: UUID):
        return self._datastore(
            datastore_id=datastore_id,
        )

    @abstractmethod
    def _datastore_association(self, **kwargs):
        pass

    def datastore_association(self, datastore_association_id: UUID):
        return self._datastore_association(
            datastore_association_id=datastore_association_id,
        )

    @abstractmethod
    def _event(self, **kwargs):
        pass

    def event(self, event_id: UUID):
        return self._event(
            event_id=event_id,
        )

    @abstractmethod
    def _job(self, **kwargs):
        pass

    def job(self, job_id: UUID):
        return self._job(
            job_id=job_id,
        )

    @abstractmethod
    def _user(self, **kwargs):
        pass

    def user(self, user_id: UUID):
        return self._user(
            user_id=user_id,
        )
