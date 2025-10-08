#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Engine API client."""

import requests
from ibm_watsonx_data_integration.common.constants import PROD_BASE_URL
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_ENGINE_API_VERSION = 1


class EngineApiClient(BaseAPIClient):
    """The API client of the Engine."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = PROD_BASE_URL,
    ) -> None:
        """The __init__ of the EngineApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"sset/engine_manager/v{DEFAULT_ENGINE_API_VERSION}/streamsets_engines"

    def get_engines(self, params: dict = None) -> requests.Response:
        """Get all Engines.

        Args:
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}"
        response = self.get(url=url, params=params)
        return response

    def get_engine(self, engine_id: str, params: dict = None) -> requests.Response:
        """Get an Engine.

        Args:
            engine_id: Engine asset_id.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(engine_id, safe='')}"
        response = self.get(url=url, params=params)
        return response

    def delete_engine(self, engine_id: str, params: dict = None) -> requests.Response:
        """Deletes an engine by its ID.

        Args:
            engine_id: Engine asset_id.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(engine_id, safe='')}"
        response = self.delete(url=url, params=params)
        return response
