# © Copyright Databand.ai, an IBM Company 2022-2024

import copy
import gzip
import json
import logging
import uuid

from datetime import datetime, timedelta
from http import HTTPStatus
from time import sleep
from typing import Dict, Optional, Tuple, Union

import requests

from six.moves.urllib_parse import urljoin

from dbnd import __version__
from dbnd._core.errors.base import (
    DatabandApiError,
    DatabandAuthenticationError,
    DatabandConnectionException,
)
from dbnd._core.errors.friendly_error.api import api_connection_refused
from dbnd._core.utils.http.retry_policy import LinearRetryPolicy
from dbnd._core.utils.trace import get_tracing_id


# we'd like to have all requests with default timeout, just in case it's stuck
DEFAULT_REQUEST_TIMEOUT = 300
DEFAULT_SESSION_KEY_ERROR_MAX_RETRY = 3
logger = logging.getLogger(__name__)


# uncomment for requests trace
# import http.client
# http.client.HTTPConnection.debuglevel = 1


class ApiClient(object):
    """Json API client implementation."""

    api_prefix = "/api/v1/"
    default_headers = None

    def __init__(
        self,
        api_base_url: str,
        credentials: Optional[Dict[str, str]] = None,
        session_timeout: int = 5,
        default_max_retry: int = 1,
        default_retry_sleep: Union[int, float] = 0,
        default_request_timeout: Union[
            float, Tuple[float, float]
        ] = DEFAULT_REQUEST_TIMEOUT,
        extra_default_headers: Optional[Dict[str, str]] = None,
        ignore_ssl_errors: bool = False,
        default_session_key_error_max_retry=DEFAULT_SESSION_KEY_ERROR_MAX_RETRY,
    ):
        """
        @param api_base_url: databand webserver url to build the request with
        @param credentials: dict of credential to authenticate with the webserver
         can include "token" key or "username"  and "password" keys
        @param session_timeout: minutes to recreate the requests session
        @param default_max_retry: default value for retries for failed connection
        @param default_retry_sleep: default value for sleep between retries
        @param default_request_timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple
        @param default_session_key_error_max_retry: (Optional): session retry for key_error
        """

        self._api_base_url = api_base_url

        self.credentials = credentials
        self.default_headers = {
            "Accept": "application/json",
            "content-encoding": "gzip",
            "Content-Type": "application/json",
            "X-Databand-Version": __version__,
            **(extra_default_headers or {}),
        }

        self.session: Optional[requests.Session] = None
        self.session_creation_time = None
        self.session_timeout = session_timeout

        self.default_max_retry = default_max_retry
        self.default_retry_sleep = default_retry_sleep
        self.default_request_timeout = default_request_timeout

        self.ignore_ssl_errors = ignore_ssl_errors

        self.default_session_key_error_max_retry = default_session_key_error_max_retry

    def is_session_expired(self):
        return datetime.now() - self.session_creation_time >= timedelta(
            minutes=self.session_timeout
        )

    def _log_request(self, request_params: dict):
        """
        1. No logging for python INFO and above log levels.
        2. Simplified logging of short REST request for python DEBUG.
        3. Extensive logging of full REST request for server debug mode with python DEBUG log level.
        """
        if not logger.isEnabledFor(logging.DEBUG):
            return  # skip, nothing to log

        request_copy = copy.deepcopy(request_params)

        # only size is relevant
        request_copy["data"] = "<{} bytes>".format(len(request_params["data"]))

        # remove and shortify security-sensitive data
        request_header_auth = request_copy["headers"].get("Authorization")
        if request_header_auth:
            request_copy["headers"]["auth"] = "<{} bytes>".format(
                len(request_header_auth)
            )
            request_copy["headers"].pop("Authorization")

        # shortify frequent headers
        if request_copy["headers"].get("X-Request-ID"):
            request_copy["headers"]["rID"] = request_copy["headers"].pop("X-Request-ID")
        if request_copy["headers"].get("X-Databand-Trace-ID"):
            request_copy["headers"]["tID"] = request_copy["headers"].pop(
                "X-Databand-Trace-ID"
            )

        # minimize default headers
        for header, value in request_params["headers"].items():
            if (
                self.default_headers.get(header) == value and header != "Authorization"
            ):  # Authorization is already removed from a request_copy
                request_copy["headers"].pop(header)
                # "X-Databand-Version" --> "XDdVn"
                abbreviation = "".join(
                    [
                        part[0] + part[-1] if len(part) > 1 else part[0]
                        for part in header.split("-")
                    ]
                )
                request_copy["headers"]["def"] = (
                    request_copy["headers"].get("def", "") + " " + abbreviation
                )

        # SDK debug, log short REST request
        logger.debug("Sending the following request: %s", request_copy)

    def _request(
        self,
        endpoint,
        session,
        method="GET",
        data=None,
        headers=None,
        query=None,
        request_timeout=None,
    ):
        headers = dict(self.default_headers, **(headers or {}))
        url = urljoin(self._api_base_url, endpoint)

        headers["X-Request-ID"] = uuid.uuid4().hex
        headers["X-Databand-Trace-ID"] = get_tracing_id().hex
        request_params = dict(
            method=method,
            url=url,
            data=gzip.compress(json.dumps(data).encode("utf-8")),
            headers=headers,
            params=query,
            timeout=request_timeout or self.default_request_timeout,
            verify=not self.ignore_ssl_errors,
        )

        self._log_request(request_params)
        resp = self._send_request(session, **request_params)

        if not resp.ok:
            logger.debug("Response is not ok, Raising DatabandApiError")
            if resp.status_code in [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN]:
                raise DatabandAuthenticationError(
                    "Authentication Error: Failed authenticating to Databand server, please check supplied credentials"
                )

            raise DatabandApiError(
                method, url, resp.status_code, resp.content.decode("utf-8")
            )

        if resp.content:
            try:
                data = resp.json()
            except Exception as e:
                logger.info("Failed to get resp.json(). Exception: {}".format(e))
            else:
                return data

        return

    def _send_request(self, session, method, url, **kwargs):
        retry_count = self.default_session_key_error_max_retry
        if retry_count <= 0:
            return session.request(method, url, **kwargs)
        while retry_count > 0:
            try:
                return session.request(method, url, **kwargs)
            except KeyError as ex:
                # workaround to https://app.asana.com/0/1201045293211331/1204415755607921
                retry_count -= 1
                logger.warning(
                    "retrying request retry count %s", retry_count, exc_info=True
                )
                if retry_count == 0:
                    raise ex

    def _authenticate(self):
        if not self.has_credentials():
            return

        try:
            credentials = self.credentials
            token = credentials.get("token")
            if token:
                self.default_headers["Authorization"] = "Bearer {}".format(token)
                return

            # get the csrf token cookie (if enabled on the server)
            self.api_request("auth/csrf", None, method="GET")
            csrf_token = self.session.cookies.get("X-CSRF-TOKEN")
            if csrf_token:
                logger.debug("Got csrf token from session")
                self.default_headers["X-CSRFToken"] = csrf_token

            if "username" in credentials and "password" in credentials:
                logger.debug("Attempting to login to webserver")
                self.api_request("auth/login", method="POST", data=credentials)
            else:
                logger.warning(
                    "ApiClient._authenticate: username or password is not provided"
                )
        except DatabandConnectionException as e:
            self.remove_session()
            raise e
        except Exception:
            self.remove_session()
            logger.debug("Fail authenticating Databand Webserver ", exc_info=True)
            raise DatabandAuthenticationError(
                "Authentication Error: Failed authenticating to Databand server, please check supplied credentials"
            )

    def create_session(self):
        logger.debug("Initialising session for webserver")
        self.session = requests.session()
        self.session_creation_time = datetime.now()

    def remove_session(self):
        self.session = None
        self.session_creation_time = None

    def api_request(
        self,
        endpoint,
        data,
        method="POST",
        headers=None,
        query=None,
        no_prefix=False,
        retry_policy=None,
        failure_handler=None,
        request_timeout=None,
        requires_auth=True,
    ):
        retry_policy = retry_policy or LinearRetryPolicy(
            seconds_to_sleep=self.default_retry_sleep,
            max_retries=self.default_max_retry,
        )

        url = endpoint if no_prefix else urljoin(self.api_prefix, endpoint)

        retry_number = 0
        while True:
            retry_number += 1
            try:
                if requires_auth:
                    session = self.authenticated_session()
                else:
                    session = self.anonymous_session()

                resp = self._request(
                    url,
                    session=session,
                    method=method,
                    data=data,
                    headers=headers,
                    query=query,
                    request_timeout=request_timeout,
                )
            except (requests.ConnectionError, requests.Timeout) as ex:
                if failure_handler:
                    failure_handler(ex, retry_policy, retry_number)

                if retry_policy.should_retry(500, None, retry_number):
                    logger.info("Retrying request - %s", url)
                    sleep(retry_policy.seconds_to_sleep(retry_number))
                    continue

                self.remove_session()
                raise api_connection_refused(self._api_base_url + url, ex)
            return resp

    def is_ready(self):
        try:
            self.api_request(
                "auth/ping",
                None,
                method="GET",
                requires_auth=False,
                retry_policy=LinearRetryPolicy(0, 1),
            )
            return True
        except (DatabandConnectionException, DatabandApiError):
            return False

    def has_credentials(self) -> bool:
        return bool(self.credentials)

    def is_configured(self) -> bool:
        return bool(self._api_base_url)

    def authenticated_session(self):
        if not self.session or self.is_session_expired():
            logger.debug(
                "Webserver session does not exist or timed out, creating new one"
            )
            self.create_session()
            self._authenticate()
        return self.session

    def anonymous_session(self) -> requests.Session:
        return requests.session()

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self._api_base_url)
