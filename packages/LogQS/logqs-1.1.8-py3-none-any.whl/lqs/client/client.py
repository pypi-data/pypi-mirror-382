from typing import Union, Optional

from lqs.common.facade import Facade

from lqs.client.config import RESTClientConfig
from lqs.client.core import LogQS
from lqs.client.dsm import DataStoreManager
from lqs.client.admin import Admin
from lqs.client.utils import Utils


class RESTClient(Facade):
    config: RESTClientConfig
    version = "1.1"

    def __init__(
        self,
        config: Union[RESTClientConfig, dict] = RESTClientConfig(),
        http_client=None,
        datastore_id: Optional[str] = None,
    ):
        self.setup(config, RESTClientConfig)
        self.http_client = http_client
        self.datastore_id = datastore_id

        self.lqs = LogQS(app=self)
        self.dsm = DataStoreManager(app=self)
        self.admin = Admin(app=self)

        self.list = self.lqs.list
        self.fetch = self.lqs.fetch
        self.create = self.lqs.create
        self.update = self.lqs.update
        self.delete = self.lqs.delete
        self.resource = self.lqs.resource

        self.utils = Utils(app=self)

    def set_datastore_id(self, datastore_id: Optional[str]):
        self.datastore_id = datastore_id
        return self

    def get_datastore_id(self):
        return self.datastore_id or self.config.datastore_id

    def set_http_client(self, http_client):
        self.http_client = http_client
        return self

    def get_http_client(self):
        return self.http_client
