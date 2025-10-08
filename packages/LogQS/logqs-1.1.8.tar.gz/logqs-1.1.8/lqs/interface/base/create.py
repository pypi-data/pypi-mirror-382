from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

import lqs.interface.base.models as models


class CreateInterface(ABC):
    @abstractmethod
    def _api_key(self, **kwargs) -> models.APIKeyDataResponse:
        pass

    def api_key(
        self, user_id: UUID, name: str, disabled: bool = False
    ) -> models.APIKeyDataResponse:
        return self._api_key(
            user_id=user_id,
            name=name,
            disabled=disabled,
        )

    def _api_key_by_model(
        self, data: models.APIKeyCreateRequest
    ) -> models.APIKeyDataResponse:
        return self.api_key(**data.model_dump())

    @abstractmethod
    def _role(self, **kwargs) -> models.RoleDataResponse:
        pass

    def role(
        self,
        name: str,
        policy: dict,
        note: Optional[str] = None,
        disabled: Optional[bool] = False,
        managed: Optional[bool] = False,
        default: Optional[bool] = False,
    ) -> models.RoleDataResponse:
        return self._role(
            name=name,
            policy=policy,
            note=note,
            disabled=disabled,
            managed=managed,
            default=default,
        )

    def _role_by_model(self, data: models.RoleCreateRequest) -> models.RoleDataResponse:
        return self.role(**data.model_dump())

    @abstractmethod
    def _user(self, **kwargs) -> models.UserDataResponse:
        pass

    def user(
        self,
        username: str,
        role_id: Optional[UUID] = None,
        admin: Optional[bool] = False,
        disabled: Optional[bool] = False,
        managed: Optional[bool] = False,
        external_id: Optional[str] = None,
        password: Optional[str] = None,
    ) -> models.UserDataResponse:
        return self._user(
            username=username,
            role_id=role_id,
            admin=admin,
            disabled=disabled,
            managed=managed,
            external_id=external_id,
            password=password,
        )

    def _user_by_model(self, data: models.UserCreateRequest) -> models.UserDataResponse:
        return self.user(**data.model_dump())
