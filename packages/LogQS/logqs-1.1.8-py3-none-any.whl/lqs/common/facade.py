import json
from typing import Type, Any, Union
from logging import Logger

from lqs.common.utils import get_logger, ContextLoggerAdapter
from lqs.common.config import CommonConfig
from lqs.interface import core


class Facade:
    logger: Union[Logger, ContextLoggerAdapter]

    def setup(
        self,
        config: Union[CommonConfig, dict[str, Any], str],
        config_class: Type[CommonConfig],
    ):
        if isinstance(config, dict):
            self.config: config_class = config_class(**config)
        elif isinstance(config, str):
            self.config: config_class = config_class(**json.loads(config))
        else:
            self.config: config_class = config
        log_level = self.config.log_level or "INFO"

        self.correlation_id = getattr(self.config, "session_id", None)
        self.logger = get_logger(
            self.__class__.__name__,
            level=log_level,
            log_to_file=self.config.log_to_file,
            json_logging=self.config.log_as_json,
            correlation_id=self.correlation_id,
        )

    def json(self, req):
        """
        Convert a JSON request to a dictionary.
        """
        return self.dict(json.loads(req))

    def dict(self, req):
        """
        Parse a dictionary request to a dictionary.
        """
        action = req.get("action")
        resource = req.get("resource")
        kwargs = req.get("kwargs")

        if action is None:
            raise Exception('[BadRequest] Required field "action" is missing.')

        if resource is None:
            resource_handler = getattr(self, action)
        else:
            action_handler = getattr(self, action)
            resource_handler = getattr(action_handler, resource)

        if kwargs is None:
            return resource_handler()
        else:
            return resource_handler(**kwargs)


class CoreFacade(Facade):
    fetch: core.FetchInterface
    list: core.ListInterface
    update: core.UpdateInterface
    create: core.CreateInterface
    delete: core.DeleteInterface
