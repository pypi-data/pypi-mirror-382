#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Resource Controller API client."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_RESOURCE_CONTROLLER_API_VERSION = 2


class ResourceControllerApiClient(BaseAPIClient):
    """The API client of the Resource Controller service."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://resource-controller.cloud.ibm.com",
    ) -> None:
        """The __init__ of the ResourceControllerApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path_resource_instances = f"v{DEFAULT_RESOURCE_CONTROLLER_API_VERSION}/resource_instances"
        self.url_path_resource_groups = f"v{DEFAULT_RESOURCE_CONTROLLER_API_VERSION}/resource_groups"
        self.url_path_resource_keys = f"v{DEFAULT_RESOURCE_CONTROLLER_API_VERSION}/resource_keys"

    def get_resource_instances(self, params: dict) -> requests.Response:
        """Retrieves Resource Instances.

        Args:
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_resource_instances}"
        response = self.get(url=url, params=params)
        return response

    def create_resource_instance(self, data: dict) -> requests.Response:
        """Creates a Resource Instance.

        Args:
            data: The resource instance JSON.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_resource_instances}"
        response = self.post(url=url, data=data)
        return response

    def delete_resource_instance(self, resource_instance_id: str, recursive: bool) -> requests.Response:
        """Deletes a Resource Instance.

        Args:
            resource_instance_id: The resource instance ID.
            recursive: Whether to recursively delete keys of the resource instance.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_resource_instances}/{quote(resource_instance_id, safe='')}"
        params = {"recursive": recursive}
        response = self.delete(url=url, params=params)
        return response

    def get_resource_groups(self) -> requests.Response:
        """Gets the Resource Groups.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_resource_groups}"
        response = self.get(url=url)
        return response

    def delete_resource_keys(self, resource_instance_id: str) -> requests.Response:
        """Deletes the Resource Keys.

        Args:
            resource_instance_id: The resource instance ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_resource_keys}/{quote(resource_instance_id, safe='')}"
        response = self.delete(url=url)
        return response

    def get_resource_keys(self, resource_id: str) -> requests.Response:
        """Gets the Resource Keys.

        Args:
            resource_id: The resource ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_resource_keys}"
        params = {"resource_id": resource_id}
        response = self.get(url=url, params=params)
        return response
