# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""Module contains base class for all API Clients."""

import requests
import urllib3
from abc import ABC
from dataclasses import dataclass
from ibm_watsonx_data_integration.common.auth import BaseAuthenticator
from ibm_watsonx_data_integration.common.exceptions import IbmCloudApiException
from ibm_watsonx_data_integration.cpd_api.adapters import DefaultHTTPAdapter
from requests.exceptions import HTTPError
from typing import Any


@dataclass
class BaseAPIClient(ABC):
    """Base Abstract API Client class.

    Every APIClient class should Inherit from this one.
    """

    base_url: urllib3.util.Url
    _auth: BaseAuthenticator
    _session: requests.Session

    def __init__(self, base_url: str, auth: BaseAuthenticator) -> None:
        """Initialize API Client classes.

        To customize behaviour per host in all API Clients, add adapter for this host below.

        Args:
            base_url: The Cloud Pak for Data URL.
            auth: The Authentication object.
        """
        # strip trailing "/" so that we do not end up with "//" when appending paths to urls.
        base_url = base_url.rstrip("/")
        self.base_url = urllib3.util.parse_url(base_url)
        self._auth = auth
        self._session = requests.Session()

        retries = urllib3.Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429],
            raise_on_status=True,
            allowed_methods={"GET", "POST", "PUT", "PATCH", "DELETE"},
        )

        self._default_adapter = DefaultHTTPAdapter(auth=self._auth, max_retries=retries)
        self._session.mount("http://", self._default_adapter)
        self._session.mount("https://", self._default_adapter)

    def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict | str | None = None,
        adapter: DefaultHTTPAdapter | None = None,
        headers: dict | None = None,
        verify: bool | str = True,
    ) -> requests.Response:
        """Proxy method for all HTTP methods.

        Main entrypoint that call all requests.

        Args:
            method: HTTP method name (GET, POST, ...).
            url: URL to requests for
            params: HTTP request parameters.
            data: HTTP request payload.
            adapter: HTTP request adapter. Has priority over header's parameter.
            headers: HTTP request headers to add to the request. Can overwrite default set headers.
            verify: Whether to verify a request. Can also be a path to a certificate file.

        Returns:
            A HTTP response.
        """
        if adapter is not None:
            adapter._auth = self._auth
            self._session.mount(url, adapter)
        elif headers:
            self._default_adapter._custom_headers = headers

        _url = urllib3.util.parse_url(url)
        try:
            response = self._session.request(
                method=method,
                url=urllib3.util.Url(
                    scheme=self.base_url.scheme,
                    host=self.base_url.host,
                    port=self.base_url.port,
                    path=_url.path,
                ),
                params=params,
                data=data,
                verify=verify,
            )
            try:
                # raise HTTPError on HTTP error codes in range [400; 600)
                response.raise_for_status()
            except HTTPError as exc:
                raise IbmCloudApiException(response=exc.response) from exc

        finally:
            if adapter is not None:
                adapter._auth = None
                self._session.adapters.pop(url)
            elif headers:
                self._default_adapter._custom_headers = {}
        return response

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        adapter: DefaultHTTPAdapter | None = None,
        headers: dict | None = None,
        verify: bool | str = True,
    ) -> requests.Response:
        """Proxy method for all HTTP GET method calls.

        Args:
            url: URL to requests for
            params: HTTP request parameters.
            adapter: HTTP request adapter. Has priority over headers parameter.
            headers: HTTP request headers to add to the request. Can overwrite default set headers.
            verify: Whether to verify a request. Can also be a path to a certificate file.

        Returns:
            A HTTP response.
        """
        return self._request(method="GET", url=url, params=params, adapter=adapter, headers=headers, verify=verify)

    def post(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict | str | None = None,
        adapter: DefaultHTTPAdapter | None = None,
        headers: dict | None = None,
        verify: bool | str = True,
    ) -> requests.Response:
        """Proxy method for all HTTP POST method calls.

        Args:
            url: URL to requests for
            params: HTTP request parameters.
            data: HTTP request payload.
            adapter: HTTP request adapter. Has priority over headers parameter.
            headers: HTTP request headers to add to the request. Can overwrite default set headers.
            verify: Whether to verify a request. Can also be a path to a certificate file.

        Returns:
            A HTTP response.
        """
        return self._request(
            method="POST", url=url, params=params, data=data, adapter=adapter, headers=headers, verify=verify
        )

    def put(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict | str | None = None,
        adapter: DefaultHTTPAdapter | None = None,
        headers: dict | None = None,
        verify: bool | str = True,
    ) -> requests.Response:
        """Proxy method for all HTTP PUT method calls.

        Args:
            url: URL to requests for
            params: HTTP request parameters.
            data: HTTP request payload.
            adapter: HTTP request adapter. Has priority over headers parameter.
            headers: HTTP request headers to add to the request. Can overwrite default set headers.
            verify: Whether to verify a request. Can also be a path to a certificate file.

        Returns:
            A HTTP response.
        """
        return self._request(
            method="PUT", url=url, params=params, data=data, adapter=adapter, headers=headers, verify=verify
        )

    def patch(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict | str | None = None,
        adapter: DefaultHTTPAdapter | None = None,
        headers: dict | None = None,
        verify: bool | str = True,
    ) -> requests.Response:
        """Proxy method for all HTTP PATCH method calls.

        Args:
            url: URL to requests for
            params: HTTP request parameters.
            data: HTTP request payload.
            adapter: HTTP request adapter. Has priority over headers parameter.
            headers: HTTP request headers to add to the request. Can overwrite default set headers.
            verify: Whether to verify a request. Can also be a path to a certificate file.

        Returns:
            A HTTP response.
        """
        return self._request(
            method="PATCH", url=url, params=params, data=data, adapter=adapter, headers=headers, verify=verify
        )

    def delete(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict | str | None = None,
        adapter: DefaultHTTPAdapter | None = None,
        headers: dict | None = None,
        verify: bool | str = True,
    ) -> requests.Response:
        """Proxy method for all HTTP DELETE method calls.

        Args:
            url: URL to requests for
            params: HTTP request parameters.
            data: HTTP request payload.
            adapter: HTTP request adapter. Has priority over headers parameter.
            headers: HTTP request headers to add to the request. Can overwrite default set headers.
            verify: Whether to verify a request. Can also be a path to a certificate file.

        Returns:
            A HTTP response.
        """
        return self._request(
            method="DELETE", url=url, params=params, data=data, adapter=adapter, headers=headers, verify=verify
        )

    def head(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict | str | None = None,
        adapter: DefaultHTTPAdapter | None = None,
        headers: dict | None = None,
        verify: bool | str = True,
    ) -> requests.Response:
        """Proxy method for all HTTP HEAD method calls.

        Args:
            url: URL to requests for
            params: HTTP request parameters.
            data: HTTP request payload.
            adapter: HTTP request adapter. Has priority over headers parameter.
            headers: HTTP request headers to add to the request. Can overwrite default set headers.
            verify: Whether to verify a request. Can also be a path to a certificate file.

        Returns:
            A HTTP response.
        """
        return self._request(
            method="HEAD", url=url, params=params, data=data, adapter=adapter, headers=headers, verify=verify
        )
