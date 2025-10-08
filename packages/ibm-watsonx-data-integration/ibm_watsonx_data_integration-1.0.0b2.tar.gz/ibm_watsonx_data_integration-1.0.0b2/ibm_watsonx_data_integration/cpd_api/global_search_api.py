#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Global Search API client."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_GLOBAL_SEARCH_API_VERSION = 3


class GlobalSearchApiClient(BaseAPIClient):
    """The API client of the Global Search service."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://api.global-search-tagging.cloud.ibm.com/api",
    ) -> None:
        """The __init__ of the GlobalSearchApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL.
        """
        super().__init__(auth=auth, base_url=base_url)

    def get_resources(self, data: dict | None) -> requests:
        """Retrieves the Global Search.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/v{DEFAULT_GLOBAL_SEARCH_API_VERSION}/resources/search"
        response = self.post(url=url, data=data)
        return response
