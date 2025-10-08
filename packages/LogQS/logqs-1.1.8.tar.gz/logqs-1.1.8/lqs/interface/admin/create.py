from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

import lqs.interface.admin.models as models


class CreateInterface(ABC):
    @abstractmethod
    def _command(self, **kwargs) -> models.CommandDataResponse:
        pass

    def command(
        self,
        action: str,
        resource: Optional[str] = None,
        app: Optional[str] = None,
        datastore_id: Optional[UUID] = None,
        kwargs: Optional[dict] = None,
        process_states: Optional[list[str]] = None,
        process_types: Optional[list[str]] = None,
    ):
        return self._command(
            action=action,
            resource=resource,
            app=app,
            datastore_id=datastore_id,
            kwargs=kwargs,
            process_states=process_states,
            process_types=process_types,
        )

    def _command_by_model(self, data: models.CommandCreateRequest):
        return self.command(**data.model_dump())
