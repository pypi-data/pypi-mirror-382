# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module containing the TrustedProfileAPIClient class."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_TRUSTED_PROFILE_API_VERSION = 1


class TrustedProfileAPIClient(BaseAPIClient):
    """The API Client of Trusted Profiles."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://iam.cloud.ibm.com",
    ) -> None:
        """Initializes the TrustedProfileAPIClient.

        Args:
            auth: The Authentication object.
            base_url: Default is "https://iam.cloud.ibm.com".
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"v{DEFAULT_TRUSTED_PROFILE_API_VERSION}/profiles"

    def list_all_trusted_profiles(self, params: dict) -> requests.Response:
        """Lists all trusted profiles under an account.

        Args:
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}"
        response = self.get(url, params)
        return response

    def get_trusted_profile(self, iam_id: str) -> requests.Response:
        """Returns a trusted profile.

        Args:
            iam_id: The IAM ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(iam_id, safe='')}"
        response = self.get(url)
        return response
