#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025


"""This module contains the UserAPIClient class."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_USER_API_VERSION = 2


class UserAPIClient(BaseAPIClient):
    """The API client of the User service."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://user-management.cloud.ibm.com",
    ) -> None:
        """Initializes the UserAPIClient.

        Args:
            auth: The Authentication object.
            base_url: The User Service URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"v{DEFAULT_USER_API_VERSION}/accounts"

    def get_users(self, account_id: str, params: dict = None) -> requests.Response:
        """Retrieve a list of users in the account by the account ID.

        Args:
            account_id: Unique identifier of the account.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(account_id, safe='')}/users"
        response = self.get(url=url, params=params)
        return response

    def get_user_profile(self, account_id: str, iam_id: str) -> requests.Response:
        """Retrieve a user's profile by the user's IAM ID in the account.

        Args:
            account_id: Unique identifier of the account.
            iam_id: Unique identifier of the user.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(account_id, safe='')}/users/{quote(iam_id, safe='')}"
        response = self.get(url=url)
        return response

    def delete_user_from_account(self, account_id: str, iam_id: str) -> requests.Response:
        """Remove a user from an account by user's IAM ID.

        Args:
            account_id: Unique identifier of the account.
            iam_id: Unique identifier of the user.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(account_id, safe='')}/users/{quote(iam_id, safe='')}"
        response = self.delete(url=url)
        return response

    def delete_user_from_account_by_id_or_email(self, account_id: str, params: dict) -> requests.Response:
        """Remove a user from an account by user's user ID or email.

        Args:
            account_id: Unique identifier of the account.
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(account_id, safe='')}/users"
        response = self.delete(url=url, params=params)
        return response

    def get_user_settings(self, account_id: str, iam_id: str) -> requests.Response:
        """Retrieve a user's settings by the user's IAM ID in the account.

        Args:
            account_id: Unique identifier of the account.
            iam_id: Unique identifier of the user.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(account_id, safe='')}/users/{quote(iam_id, safe='')}/settings"
        response = self.get(url=url)
        return response

    def update_user_settings(self, account_id: str, iam_id: str, data: dict) -> requests.Response:
        """Update the settings for a specific user in an account.

        Args:
            account_id: Unique identifier of the account.
            iam_id: Unique identifier (IAM ID) of the user.
            data: Dictionary containing any or all settings to update. For example:
                {
                    "language": "en-us",
                    "notification_language": "en-us",
                    "allowed_ip_addresses": "32.96.110.50,172.16.254.1",
                    "self_manage": True,
                    "2FA": False,
                    "security_questions_required": False,
                    "security_questions_setup": False
                }

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(account_id, safe='')}/users/{quote(iam_id, safe='')}/settings"
        response = self.patch(url=url, data=data)
        return response
