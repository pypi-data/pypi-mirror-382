from abc import ABC, abstractmethod
from uuid import UUID

import lqs.interface.base.models as models


class UpdateInterface(ABC):
    def _process_data(self, data):
        if not isinstance(data, dict):
            return data.model_dump(exclude_unset=True)
        return data

    @abstractmethod
    def _api_key(self, **kwargs) -> models.APIKeyDataResponse:
        pass

    def api_key(
        self, api_key_id: UUID, data: models.APIKeyUpdateRequest
    ) -> models.APIKeyDataResponse:
        return self._api_key(
            api_key_id=api_key_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _role(self, **kwargs) -> models.RoleDataResponse:
        pass

    def role(
        self, role_id: UUID, data: models.RoleUpdateRequest
    ) -> models.RoleDataResponse:
        return self._role(
            role_id=role_id,
            data=self._process_data(data),
        )

    @abstractmethod
    def _user(self, **kwargs) -> models.UserDataResponse:
        pass

    def user(
        self, user_id: UUID, data: models.UserUpdateRequest
    ) -> models.UserDataResponse:
        return self._user(user_id=user_id, data=self._process_data(data))
