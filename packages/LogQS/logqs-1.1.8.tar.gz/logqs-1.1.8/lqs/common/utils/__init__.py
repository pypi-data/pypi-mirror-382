from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lqs.common.facade import CoreFacade
from lqs.common.utils.record_utils import RecordUtils
from lqs.common.utils.crud_utils import CRUDUtils
from lqs.common.utils.object_utils import ObjectUtils
from lqs.common.utils.digestion_utils import DigestionUtils
from lqs.common.utils.ingestion_utils import IngestionUtils

from lqs.common.utils.utils import *


class Utils(RecordUtils, CRUDUtils, ObjectUtils, DigestionUtils, IngestionUtils):
    def __init__(self, app: "CoreFacade"):
        super().__init__(app)
        self.app: CoreFacade

    def get_info(self, print_config=False, log_config=False):
        self.app.logger.info("Logging info message.")
        self.app.logger.debug("Logging debug message.")
        self.app.logger.warning("Logging warn message.")
        self.app.logger.error("Logging error message.")

        if print_config:
            print(self.app.config)

        if log_config:
            self.app.logger.info(self.app.config)
