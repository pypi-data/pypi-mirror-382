from lqs.interface.admin import CreateInterface
from lqs.client.common import RESTInterface
import lqs.interface.admin.models as models


class Create(CreateInterface, RESTInterface):
    service: str = "admin"

    def __init__(self, app):
        super().__init__(app=app)

    def _command(self, **params):
        return self._create_resource("commands", params, models.CommandDataResponse)
