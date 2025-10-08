from abc import abstractmethod
from uuid import UUID

import lqs.interface.dsm.models as models
from lqs.interface.base.update import UpdateInterface as BaseUpdateInterface


class UpdateInterface(BaseUpdateInterface):
    @abstractmethod
    def _announcement(self, **kwargs) -> models.AnnouncementDataResponse:
        pass

    def announcement(
        self,
        announcement_id: UUID,
        data: models.AnnouncementUpdateRequest,
    ):
        return self._announcement(
            announcement_id=announcement_id,
            data=self._process_data(data),
        )

    def _announcement_by_model(
        self, announcement_id: UUID, data: models.AnnouncementUpdateRequest
    ):
        return self.announcement(announcement_id=announcement_id, data=data)

    @abstractmethod
    def _comment(self, **kwargs) -> models.CommentDataResponse:
        pass

    def comment(
        self,
        comment_id: UUID,
        data: models.CommentUpdateRequest,
    ):
        return self._comment(
            comment_id=comment_id,
            data=self._process_data(data),
        )

    def _comment_by_model(self, comment_id: UUID, data: models.CommentUpdateRequest):
        return self.comment(comment_id=comment_id, data=data)

    @abstractmethod
    def _configuration(self, **kwargs) -> models.ConfigurationDataResponse:
        pass

    def configuration(
        self,
        configuration_id: UUID,
        data: models.ConfigurationUpdateRequest,
    ):
        return self._configuration(
            configuration_id=configuration_id,
            data=self._process_data(data),
        )

    def _configuration_by_model(
        self, configuration_id: UUID, data: models.ConfigurationUpdateRequest
    ):
        return self.configuration(configuration_id=configuration_id, data=data)

    @abstractmethod
    def _datastore(self, **kwargs) -> models.DataStoreDataResponse:
        pass

    def datastore(self, datastore_id: UUID, data: models.DataStoreUpdateRequest):
        return self._datastore(
            datastore_id=datastore_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _datastore_association(
        self, **kwargs
    ) -> models.DataStoreAssociationDataResponse:
        pass

    def datastore_association(
        self,
        datastore_association_id: UUID,
        data: models.DataStoreAssociationUpdateRequest,
    ):
        return self._datastore_association(
            datastore_association_id=datastore_association_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _event(self, **kwargs) -> models.EventDataResponse:
        pass

    def event(self, event_id: UUID, data: models.EventUpdateRequest):
        return self._event(
            event_id=event_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _job(self, **kwargs) -> models.JobDataResponse:
        pass

    def job(self, job_id: UUID, data: models.JobUpdateRequest):
        return self._job(
            job_id=job_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _user(self, **kwargs) -> models.UserDataResponse:
        pass

    def user(
        self, user_id: UUID, data: models.UserUpdateRequest
    ) -> models.UserDataResponse:
        return self._user(user_id=user_id, data=self._process_data(data))
