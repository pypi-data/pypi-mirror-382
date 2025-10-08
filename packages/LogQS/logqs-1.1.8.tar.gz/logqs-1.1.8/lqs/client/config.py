from uuid import UUID
from typing import Optional

from lqs.common.config import CommonConfig


class RESTClientConfig(CommonConfig):
    """
    Configuration for the RESTClient class.

    Attributes:
        api_key_id (Optional[UUID]): The ID of the API key with which requests will be made.
        api_key_secret (Optional[str]): The secret of the API key with which requests will be made.
        datastore_id (Optional[UUID]): The ID of the DataStore which the client will interact with.

        api_url (Optional[str]): The base URL of the LogQS API (default: "https://api.logqs.com")
        api_endpoint_prefix (str): The prefix for the API endpoints (default: "/apps")
        dsm_api_key_id (Optional[UUID]): The ID of the API key used to interact with the DataStore Manager.
        dsm_api_key_secret (Optional[str]): The secret of the API key used to interact with the DataStore Manager.

        pretty (bool): Whether to pretty-print responses (default: False)
        verbose (bool): Whether to print verbose output (default: False)
        log_level (str): The logging level (default: "INFO")
        log_as_json (bool): Whether to log as JSON (default: False)
        dry_run (bool): Whether to run in dry-run mode (default: False)
        retry_count (int): The number of times to retry requests (default: 2)
        retry_delay (int): The delay between retries (default: 5)
        retry_aggressive (bool): Whether to use an aggressive retry strategy (default: False)
        api_request_timeout (int): The timeout for API requests (default: 60)
        additional_headers (dict[str, str]): Additional headers to include in requests (default: {})
    """

    api_key_id: Optional[UUID] = None
    api_key_secret: Optional[str] = None
    datastore_id: Optional[UUID] = None

    api_url: Optional[str] = "https://api.logqs.com"
    api_endpoint_prefix: str = "/apps"
    dsm_api_key_id: Optional[UUID] = None
    dsm_api_key_secret: Optional[str] = None

    pretty: bool = False
    verbose: bool = False
    log_level: str = "INFO"
    log_as_json: bool = False
    dry_run: bool = False
    retry_count: int = 2
    retry_delay: int = 5
    retry_aggressive: bool = False
    api_request_timeout: int = 60
    version_match_level: Optional[str] = "minor"
    raise_for_version_mismatch: bool = False
    warn_for_version_mismatch: bool = True
    additional_headers: dict[str, str] = {}
    session_id: Optional[str] = None
