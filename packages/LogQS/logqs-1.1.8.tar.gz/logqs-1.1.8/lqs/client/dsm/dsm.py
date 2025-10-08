from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lqs.client import RESTClient
from lqs.client.dsm.list import List
from lqs.client.dsm.fetch import Fetch
from lqs.client.dsm.create import Create
from lqs.client.dsm.update import Update
from lqs.client.dsm.delete import Delete


class DataStoreManager:
    def __init__(self, app: "RESTClient"):
        self.app = app

        self.list = List(app=app)
        self.fetch = Fetch(app=app)
        self.create = Create(app=app)
        self.update = Update(app=app)
        self.delete = Delete(app=app)
