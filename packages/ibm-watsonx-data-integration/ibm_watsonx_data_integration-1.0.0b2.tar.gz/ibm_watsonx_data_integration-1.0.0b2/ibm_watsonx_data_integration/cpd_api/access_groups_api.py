# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module containing the AccessGroupsAPIClient class."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_ACCESS_GROUP_API_VERSION = 2


class AccessGroupsAPIClient(BaseAPIClient):
    """The API Client of Access Groups."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://iam.cloud.ibm.com",
    ) -> None:
        """Initializes the AccessGroupsAPIClient.

        Args:
            auth: The Authentication object.
            base_url: Default is "https://iam.cloud.ibm.com".
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"v{DEFAULT_ACCESS_GROUP_API_VERSION}/groups"

    def get_access_group(self, access_group_id: str) -> requests.Response:
        """Gets an access group.

        Args:
            access_group_id: The access group ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(access_group_id, safe='')}"
        response = self.get(url=url)
        return response

    def get_all_access_groups(self, params: dict) -> requests.Response:
        """Lists all access groups under an account. Will only list those the listed user can access.

        Args:
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}"
        response = self.get(url=url, params=params)
        return response

    def create_access_group(self, params: dict, data: dict = None) -> requests.Response:
        """Creates a new access group.

        Args:
            params: Query parameters.
            data: The name and description of the access group to be created/updated, in json form.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}"
        response = self.post(url=url, params=params, data=data)
        return response

    def update_access_group(self, access_group_id: str, etag: str, data: dict) -> requests.Response:
        """Updates existing access group.

        Args:
            access_group_id: The access group ID.
            etag: The etag for the latest revision to the AccessGroup.
            data: The name and description of the access group to be created/updated, in json form.

        Returns:
            A HTTP response.
        """
        headers = {"If-Match": etag}

        url = f"{self.base_url}/{self.url_path}/{quote(access_group_id, safe='')}"
        response = self.patch(url=url, data=data, headers=headers)
        return response

    def delete_access_group(self, access_group_id: str) -> requests.Response:
        """Deletes an access group from an account.

        Args:
            access_group_id: The access group ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(access_group_id, safe='')}"
        response = self.delete(url=url)
        return response

    def add_members(self, access_group_id: str, data: dict) -> requests.Response:
        """Adds member(s) to an access group.

        Args:
            access_group_id: The access group ID.
            data: The member(s) to be added to an access group, in json form.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(access_group_id, safe='')}/members"
        response = self.put(url, data=data)
        return response

    def get_members(self, access_group_id: str) -> requests.Response:
        """Lists all members in an access group.

        Args:
            access_group_id: The access group ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(access_group_id, safe='')}/members"
        response = self.get(url)
        return response

    def check_membership(self, access_group_id: str, iam_id: str) -> requests.Response:
        """Checks if a member is present in an access group.

        Args:
            access_group_id: The access group ID.
            iam_id: The IAM ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(access_group_id, safe='')}/members/{iam_id}"
        response = self.head(url)
        return response

    def remove_members_from_access_group(self, access_group_id: str, data: dict) -> requests.Response:
        """Removes multiple members from an access group.

        Args:
            access_group_id: The access group ID.
            data: List of IAM IDs to remove, in json form
        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{quote(access_group_id, safe='')}/members/delete"
        response = self.post(url, data=data)
        return response

    def remove_member_from_all_access_groups(self, iam_id: str, params: dict) -> requests.Response:
        """Removes member from all access groups under an account.

        Args:
            params: Query parameters.
            iam_id: The IAM ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/_allgroups/members/{quote(iam_id, safe='')}"
        response = self.delete(url, params)
        return response

    def add_member_to_multiple_access_groups(self, params: dict, iam_id: str, data: dict) -> requests.Response:
        """Adds member to multiple access groups.

        Args:
            params: Query parameters.
            iam_id: The IAM ID.
            data: The type of member and the groups to add a member to, in json form.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/_allgroups/members/{quote(iam_id, safe='')}"
        response = self.put(url, params, data)
        return response
