from abc import ABC, abstractmethod
from uuid import UUID


class DeleteInterface(ABC):
    @abstractmethod
    def _api_key(self, **kwargs):
        pass

    def api_key(self, api_key_id: UUID):
        return self._api_key(
            api_key_id=api_key_id,
        )

    @abstractmethod
    def _role(self, **kwargs):
        pass

    def role(self, role_id: UUID):
        return self._role(
            role_id=role_id,
        )

    @abstractmethod
    def _user(self, **kwargs):
        pass

    def user(self, user_id: UUID):
        return self._user(
            user_id=user_id,
        )
