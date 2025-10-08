from typing import TYPE_CHECKING

from lqs.common.core_utils import CoreUtils

if TYPE_CHECKING:
    from lqs.client import RESTClient


class Utils(CoreUtils):
    def __init__(self, app: "RESTClient"):
        super().__init__(app)
