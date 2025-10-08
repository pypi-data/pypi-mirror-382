#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Global Catalog API client."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_GLOBAL_CATALOG_API_VERSION = 1


class GlobalCatalogApiClient(BaseAPIClient):
    """The API client of the Global Catalog service."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://globalcatalog.cloud.ibm.com/api",
    ) -> None:
        """The __init__ of the GlobalCatalogApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL.
        """
        super().__init__(auth=auth, base_url=base_url)

    def get_global_catalog(self, q_string: str = None, complete: bool = False) -> requests:
        """Retrieves the Global Catalog.

        Args:
            q_string: The Q string to search.
            complete: Whether to return the complete JSON.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/v{DEFAULT_GLOBAL_CATALOG_API_VERSION}"
        params = {"complete": complete, "q": q_string}
        response = self.get(url=url, params=params)
        return response
