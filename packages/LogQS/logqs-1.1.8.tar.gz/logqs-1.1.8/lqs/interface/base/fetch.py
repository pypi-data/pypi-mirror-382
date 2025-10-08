from abc import ABC, abstractmethod
from uuid import UUID

import lqs.interface.base.models as models


class FetchInterface(ABC):
    @abstractmethod
    def _api_key(self, **kwargs) -> models.APIKeyDataResponse:
        pass

    def api_key(self, api_key_id: UUID) -> models.APIKeyDataResponse:
        return self._api_key(
            api_key_id=api_key_id,
        )

    @abstractmethod
    def _me(self, **kwargs) -> models.MeDataResponse:
        pass

    def me(self) -> models.MeDataResponse:
        return self._me()

    @abstractmethod
    def _role(self, **kwargs) -> models.RoleDataResponse:
        pass

    def role(self, role_id: UUID) -> models.RoleDataResponse:
        return self._role(
            role_id=role_id,
        )

    @abstractmethod
    def _user(self, **kwargs) -> models.UserDataResponse:
        pass

    def user(self, user_id: UUID) -> models.UserDataResponse:
        return self._user(
            user_id=user_id,
        )
