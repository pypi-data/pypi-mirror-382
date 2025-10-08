# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""Module with HTTP adapters used for API."""

import requests
from ibm_watsonx_data_integration.__version__ import __version__
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator


class DefaultHTTPAdapter(requests.adapters.HTTPAdapter):
    """Default HTTP Adapter class.

    Every Adapter class used in BaseAPIClient should be a subclass of this one.
    """

    def __init__(
        self,
        pool_connections: int = 1,
        pool_maxsize: int = 10,
        max_retries: int = 0,
        pool_block: bool = False,
        timeout: tuple | float | None = None,
        auth: Optional["BaseAuthenticator"] = None,
    ) -> None:
        """Initialize Adapters.

        https://requests.readthedocs.io/en/latest/api/#requests.adapters.HTTPAdapter

        Args:
            pool_connections: See pool_connections parameter for requests.adapters.HTTPAdapter.
            pool_maxsize: See pool_maxsize parameter for requests.adapters.HTTPAdapter.
            max_retries: See max_retries parameter for requests.adapters.HTTPAdapter.
            pool_block: See pool_block parameter for requests.adapters.HTTPAdapter.
            timeout: See timeout parameter for requests.adapters.HTTPAdapter.send().
            auth: The Authentication object.
        """
        super().__init__(
            pool_connections=pool_connections, pool_maxsize=pool_maxsize, max_retries=max_retries, pool_block=pool_block
        )
        self._auth = auth
        self._timeout = timeout
        self._custom_headers = {}

    def send(self, request: requests.PreparedRequest, **kwargs: dict[str, Any]) -> requests.Response:
        """Overwritten HTTPAdapter.send method.

        https://requests.readthedocs.io/en/latest/api/#requests.adapters.HTTPAdapter.send
        """
        if self._timeout:
            kwargs["timeout"] = self._timeout
        return super().send(request, **kwargs)

    def add_headers(self, request: requests.PreparedRequest, **kwargs: dict[str, Any]) -> None:
        """Overwritten HTTPAdapter.add_headers.

        https://requests.readthedocs.io/en/latest/api/#requests.adapters.HTTPAdapter.add_headers
        """
        # authorization
        if self._auth is not None:
            request.headers["Authorization"] = self._auth.get_authorization_header()

        # required headers
        request.headers.setdefault("Accept", "application/json")
        request.headers.setdefault("Accept-Language", "en-US")
        request.headers.setdefault("Content-Type", "application/json")
        request.headers["watsonx-sdk-version"] = __version__

        request.headers.update(self._custom_headers)
