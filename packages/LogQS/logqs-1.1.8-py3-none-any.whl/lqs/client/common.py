from typing import Optional, TYPE_CHECKING
import requests

import time
import json
import base64
import pprint
import decimal
from datetime import datetime, date
from uuid import UUID
import urllib.parse

if TYPE_CHECKING:
    from lqs.client import RESTClient

from lqs.common import exceptions


class LogQSEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()

        if isinstance(obj, bytes):
            return obj.decode("utf-8")

        if isinstance(obj, decimal.Decimal):
            return float(obj)

        return json.JSONEncoder.default(self, obj)


def output_decorator(func):
    def wrapper(*args, **kwargs):
        if args[0]._pretty:
            return pprint.pprint(func(*args, **kwargs))
        return func(*args, **kwargs)

    return wrapper


class RESTInterface:
    service: str

    def __init__(self, app: "RESTClient"):
        self.app = app
        if self.app.http_client is None:
            self._client = requests
            self._use_content = False
        else:
            self._client = self.app.http_client
            self._use_content = True
        self.version_mismatch_warned = False

    def _get_request_kwargs(self, **kwargs):
        # If we're using http_client (TestClient), exclude timeout to avoid deprecation warning
        if self.app.http_client is not None:
            # Remove timeout from kwargs since TestClient doesn't support it
            return {k: v for k, v in kwargs.items() if k != "timeout"}
        else:
            # Using requests library, include all kwargs including timeout
            return kwargs

    def _get_headers(self, url=None):
        headers = {
            "Content-Type": "application/json",
        }

        api_key_id = self.app.config.api_key_id
        api_key_secret = self.app.config.api_key_secret
        if url is not None and "/apps/dsm/api" in url:
            if (
                self.app.config.dsm_api_key_id is not None
                and self.app.config.dsm_api_key_secret is not None
            ):
                self.app.logger.debug("Using DSM API Key")
                api_key_id = self.app.config.dsm_api_key_id
                api_key_secret = self.app.config.dsm_api_key_secret

        if api_key_id is not None and api_key_secret is not None:
            headers["Authorization"] = "Bearer " + base64.b64encode(
                bytes(
                    f"{api_key_id}:{api_key_secret}",
                    "utf-8",
                )
            ).decode("utf-8")

        headers.update(self.app.config.additional_headers)
        return headers

    def _get_url_param_string(self, args, exclude=[]):
        url_params = ""
        for key, value in args.items():
            if value is not None and key not in ["self"] + exclude:
                if type(value) is dict:
                    value = json.dumps(value, cls=LogQSEncoder)
                elif type(value) is list:
                    if all(isinstance(i, (str, int, float, UUID)) for i in value):
                        for i in value:
                            url_params += f"&{key}={i}"
                        continue
                quoted_value = urllib.parse.quote(str(value))
                url_params += f"&{key}={quoted_value}"
        if len(url_params) > 0:
            url_params = "?" + url_params[1:]
        return url_params

    def _get_payload_data(self, args, exclude=[]):
        payload = {}
        for key, value in args.items():
            if value is not None and key not in ["self"] + exclude:
                payload[key] = value
        return payload

    def _check_version_match(
        self, api_version: Optional[str], client_version: Optional[str]
    ) -> bool:
        if self.app.config.version_match_level is None:
            return True
        if api_version is None:
            return True
        if client_version is None:
            return True

        api_version_parts = api_version.split(".")
        client_version_parts = client_version.split(".")

        if self.app.config.version_match_level.lower() == "major":
            return api_version_parts[0] == client_version_parts[0]
        elif self.app.config.version_match_level.lower() == "minor":
            return (
                api_version_parts[0] == client_version_parts[0]
                and api_version_parts[1] <= client_version_parts[1]
            )

    def _handle_response_data(self, response: requests.Response):
        api_version = response.headers.get("x-logqs-version")
        if api_version is not None:
            versions_match = self._check_version_match(
                api_version=api_version,
                client_version=self.app.version,
            )
            if not versions_match:
                version_mismatch_message = f"Version mismatch: client version: {self.app.version}, server version: {api_version}."
                if self.app.config.raise_for_version_mismatch:
                    raise Exception(version_mismatch_message)
                if self.app.config.warn_for_version_mismatch:
                    if not self.version_mismatch_warned:
                        self.version_mismatch_warned = True
                        self.app.logger.warning(version_mismatch_message)

        if response.status_code == 204:
            return

        content_type = response.headers.get("content-type")
        if content_type == "application/json":
            try:
                response_data = response.json()
            except json.decoder.JSONDecodeError:
                raise Exception(f"Error: {response.text}")
        elif content_type == "text/plain":
            response_data = response.text
        else:
            response_data = response.content

        try:
            response_ok = response.ok
        except AttributeError:
            # the TestClient from starlette does not have an ok attribute
            response_ok = response.is_success

        if response_ok:
            return response_data
        else:
            response_message = response_data
            if isinstance(response_data, bytes):
                raise Exception(f"Error: {response_data}")

            if "message" in response_data:
                response_message = response_data["message"]
            if response.status_code == 400:
                raise exceptions.BadRequestException(msg=response_message)
            if response.status_code == 401:
                raise exceptions.UnauthorizedException(msg=response_message)
            elif response.status_code == 403:
                raise exceptions.ForbiddenException(msg=response_message)
            elif response.status_code == 404:
                raise exceptions.NotFoundException(msg=response_message)
            elif response.status_code == 408:
                raise exceptions.TimeoutException(msg=response_message)
            elif response.status_code == 409:
                raise exceptions.ConflictException(msg=response_message)
            elif response.status_code == 413:
                raise exceptions.ContentTooLargeException(msg=response_message)
            elif response.status_code == 423:
                raise exceptions.LockedException(msg=response_message)
            elif response.status_code == 500:
                raise exceptions.InternalServerErrorException(msg=response_message)
            elif response.status_code == 501:
                raise exceptions.NotImplementedException(msg=response_message)
            raise Exception(response_message)

    def _handle_retries(self, func, retry_count=None):
        if retry_count is None:
            retry_count = self.app.config.retry_count
        for i in range(retry_count + 1):
            try:
                return func()
            except Exception as e:
                if not self.app.config.retry_aggressive:
                    # check if the error is one of our expected exceptions,
                    # i.e., an error that probably won't be resolved by retrying
                    lqs_expected_exceptions = [
                        exceptions.UnauthorizedException,
                        exceptions.ForbiddenException,
                        exceptions.NotFoundException,
                        exceptions.ConflictException,
                        exceptions.ContentTooLargeException,
                        exceptions.LockedException,
                        exceptions.BadRequestException,
                    ]
                    for exception in lqs_expected_exceptions:
                        if isinstance(e, exception):
                            raise e
                if retry_count > 0 and i < retry_count:
                    # exponential backoff
                    backoff = self.app.config.retry_delay * (2**i)
                    self.app.logger.error(f"Error: {e}")
                    self.app.logger.debug(f"Retrying in {backoff} seconds")
                    time.sleep(backoff)
                else:
                    raise e
        raise Exception("Error: Max retries exceeded")

    def _get_url(self, resource_path):
        path_prefix = f"/{self.service}/api"
        datastore_id = self.app.get_datastore_id()
        if self.service == "lqs" and datastore_id is not None:
            path_prefix = f"/{self.service}/{datastore_id}/api"

        url = self.app.config.api_url or ""
        url += self.app.config.api_endpoint_prefix or ""
        url += path_prefix + "/"
        url += resource_path
        return url

    def _head_resource(self, resource_path):
        url = self._get_url(resource_path)
        if self.app.config.dry_run:
            self.app.logger.info(
                {
                    "log_type": "dry_run",
                    "method": "HEAD",
                    "url": url,
                }
            )
            return {}

        def make_request():
            request_kwargs = self._get_request_kwargs(
                url=url,
                headers=self._get_headers(url=url),
                timeout=self.app.config.api_request_timeout,
            )
            r = self._client.head(**request_kwargs)
            response_data = self._handle_response_data(r)
            if isinstance(response_data, (dict, list)):
                return response_data
            else:
                raise Exception("Error: HEAD request returned non-JSON data")

        return self._handle_retries(make_request)

    def _get_resource(
        self,
        resource_path,
        expected_content_type: Optional[str] = "application/json",
        additional_headers=None,
        response_model=None,
    ):
        url = self._get_url(resource_path)
        if self.app.config.dry_run:
            self.app.logger.info(
                {
                    "log_type": "dry_run",
                    "method": "GET",
                    "url": url,
                    "expected_content_type": expected_content_type,
                    "additional_headers": additional_headers,
                }
            )
            return {}

        def make_request():
            headers = self._get_headers(url=url)
            if additional_headers:
                headers = {**headers, **additional_headers}
            request_kwargs = self._get_request_kwargs(
                url=url,
                headers=headers,
                timeout=self.app.config.api_request_timeout,
            )
            r = self._client.get(**request_kwargs)
            response_data = self._handle_response_data(r)
            if expected_content_type == "application/json":
                if isinstance(response_data, (dict, list)):
                    if response_model:
                        return response_model(**response_data)
                    return response_data
                else:
                    raise Exception("Error: GET request returned non-JSON data")
            elif expected_content_type == "text/plain":
                if isinstance(response_data, str):
                    return response_data
                else:
                    raise Exception("Error: GET request returned non-string data")
            else:
                if isinstance(response_data, bytes):
                    return response_data
                else:
                    raise Exception(
                        f"Error: GET request returned non-bytes data: {response_data}"
                    )

        return self._handle_retries(make_request)

    def _create_resource(
        self, resource_path, data, response_model, additiona_params={}
    ):
        url = self._get_url(resource_path)
        if self.app.config.dry_run:
            self.app.logger.info(
                {
                    "log_type": "dry_run",
                    "method": "POST",
                    "url": url,
                    "data": data,
                    "response_model": response_model,
                    "additiona_params": additiona_params,
                }
            )
            return {}

        def make_request():
            if self._use_content:
                params = dict(
                    url=url,
                    params=additiona_params,
                    content=json.dumps(data, cls=LogQSEncoder),
                    headers=self._get_headers(url=url),
                    timeout=self.app.config.api_request_timeout,
                )
            else:
                params = dict(
                    url=url,
                    params=additiona_params,
                    data=json.dumps(data, cls=LogQSEncoder),
                    headers=self._get_headers(url=url),
                    timeout=self.app.config.api_request_timeout,
                )

            # Apply conditional timeout handling
            params = self._get_request_kwargs(**params)
            r = self._client.post(**params)  # type: ignore
            response_data = self._handle_response_data(r)
            if isinstance(response_data, (dict, list)):
                if response_model is None:
                    return response_data
                return response_model(**response_data)
            else:
                raise Exception("Error: POST request returned non-JSON data")

        return self._handle_retries(make_request)

    def _update_resource(
        self, resource_path, data, response_model, additiona_params={}
    ):
        url = self._get_url(resource_path)
        if self.app.config.dry_run:
            self.app.logger.info(
                {
                    "log_type": "dry_run",
                    "method": "PATCH",
                    "url": url,
                    "data": data,
                    "response_model": response_model,
                    "additiona_params": additiona_params,
                }
            )
            return {}

        def make_request():
            if self._use_content:
                params = dict(
                    url=url,
                    params=additiona_params,
                    content=json.dumps(data, cls=LogQSEncoder),
                    headers=self._get_headers(url=url),
                    timeout=self.app.config.api_request_timeout,
                )
            else:
                params = dict(
                    url=url,
                    params=additiona_params,
                    data=json.dumps(data, cls=LogQSEncoder),
                    headers=self._get_headers(url=url),
                    timeout=self.app.config.api_request_timeout,
                )
            # Apply conditional timeout handling
            params = self._get_request_kwargs(**params)
            r = self._client.patch(**params)  # type: ignore
            response_data = self._handle_response_data(r)
            if isinstance(response_data, (dict, list)):
                return response_model(**response_data)
            else:
                raise Exception("Error: PATCH request returned non-JSON data")

        return self._handle_retries(make_request)

    def _delete_resource(self, resource_path, additiona_params={}):
        url = self._get_url(resource_path)
        if self.app.config.dry_run:
            self.app.logger.info(
                {
                    "log_type": "dry_run",
                    "method": "DELETE",
                    "url": url,
                    "additiona_params": additiona_params,
                }
            )
            return

        def make_request():
            request_kwargs = self._get_request_kwargs(
                url=url,
                params=additiona_params,
                headers=self._get_headers(url=url),
                timeout=self.app.config.api_request_timeout,
            )
            r = self._client.delete(**request_kwargs)
            response_data = self._handle_response_data(r)
            if response_data is not None:
                raise Exception(f"Error: DELETE request returned data: {response_data}")

        return self._handle_retries(make_request)
