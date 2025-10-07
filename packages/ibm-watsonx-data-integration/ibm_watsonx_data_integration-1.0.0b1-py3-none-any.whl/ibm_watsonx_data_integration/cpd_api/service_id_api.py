# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module containing the ServiceIDAPIClient class."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_SERVICE_ID_API_VERSION = 1


class ServiceIDAPIClient(BaseAPIClient):
    """The API Client of Service IDs."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://iam.cloud.ibm.com",
    ) -> None:
        """Initializes the ServiceIDAPIClient.

        Args:
            auth: The Authentication object.
            base_url: Default is "https://iam.cloud.ibm.com".
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"v{DEFAULT_SERVICE_ID_API_VERSION}/serviceids"

    def list_all_service_ids(self, params: dict) -> requests.Response:
        """Lists all Service IDs under an account.

        Args:
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}"
        response = self.get(url, params)
        return response

    def get_service_id(self, iam_id: str) -> requests.Response:
        """Returns a trusted profile.

        Args:
            iam_id: The IAM ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(iam_id, safe='')}"
        response = self.get(url)
        return response
