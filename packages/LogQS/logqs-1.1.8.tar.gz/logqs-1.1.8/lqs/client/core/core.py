from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lqs.client import RESTClient
from lqs.client.core.list import List
from lqs.client.core.fetch import Fetch
from lqs.client.core.create import Create
from lqs.client.core.update import Update
from lqs.client.core.delete import Delete
from lqs.interface.core.models import Resources


class LogQS:
    def __init__(self, app: "RESTClient"):
        self.app = app

        self.resource = Resources
        for resource_name in dir(self.resource):
            if resource_name.startswith("_"):
                continue
            resource = getattr(self.resource, resource_name)
            try:
                resource.set_app(self.app)
            except AttributeError:
                self.app.logger.debug(f"Failed to set app for {resource_name}.")

        self.list = List(app=app)
        self.fetch = Fetch(app=app)
        self.create = Create(app=app)
        self.update = Update(app=app)
        self.delete = Delete(app=app)
