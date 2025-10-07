#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025


"""This module contains the AccountAPIClient class."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_ACCOUNT_API_VERSION = 2


class AccountAPIClient(BaseAPIClient):
    """The API client of the Accounts service."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://accounts.cloud.ibm.com",
    ) -> None:
        """Initializes the AccountAPIClient.

        Args:
            auth: The Authentication object.
            base_url: The Accounts Service URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"v{DEFAULT_ACCOUNT_API_VERSION}/accounts"

    def get_accounts(self, params: dict = None) -> requests.Response:
        """Retrieve a list of accounts associated with the current IAM bearer token.

        Args:
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/coe/{self.url_path}"
        response = self.get(url=url, params=params)
        return response

    def get_account(self, account_id: str) -> requests.Response:
        """Retrieve details of a specific account by its ID.

        Args:
            account_id: Unique identifier of the account.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/coe/{self.url_path}/{quote(account_id, safe='')}"
        response = self.get(url=url)
        return response
