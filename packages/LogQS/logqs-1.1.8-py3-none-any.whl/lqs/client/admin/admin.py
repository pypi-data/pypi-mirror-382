from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lqs.client import RESTClient
from lqs.client.admin.create import Create


class Admin:
    def __init__(self, app: "RESTClient"):
        self.app = app

        self.create = Create(app=app)
