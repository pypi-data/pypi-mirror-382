#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the StreamsetsFlow API client."""

import requests
from ibm_watsonx_data_integration.common.utils import wait_and_retry_on_http_error
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

FLOWSTORE_API_VERSION = 1


class StreamsetsFlowApiClient(BaseAPIClient):
    """The API client of the Project."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://api.dataplatform.cloud.ibm.com",
    ) -> None:
        """The __init__ of the ProjectApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Streamsets Flow URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"sset/streamsets_flows/v{FLOWSTORE_API_VERSION}"
        self.url_path_connections = f"sset/streamsets_flows/v{FLOWSTORE_API_VERSION}/connections"

    @wait_and_retry_on_http_error(timeout_sec=10)
    def get_streamsets_flows(self, params: dict) -> requests.Response:
        """Get all Projects.

        Args:
           params: The Query params.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows"
        response = self.get(url=url, params=params)
        return response

    def get_streamsets_flow_by_id(self, params: dict, flow_id: str) -> requests.Response:
        """Get all Projects.

        Args:
            params: The Query params.
            flow_id: The Flow ID.

        Returns:
           A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows/{quote(flow_id, safe='')}"
        response = self.get(url=url, params=params)
        return response

    def delete_streamsets_flow(self, params: dict, flow_id: str) -> requests.Response:
        """Delete a Streamsets Flow.

        Args:
            params: The Query params.
            flow_id: The Flow ID.

        Returns:
           A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows/{quote(flow_id, safe='')}"
        response = self.delete(url=url, params=params)
        return response

    def update_streamsets_flow(self, params: dict, flow_id: str, data: str) -> requests.Response:
        """Update a Streamsets Flow.

        Args:
            params: The Query params.
            flow_id: The Flow ID.
            data: The payload data.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows/{quote(flow_id, safe='')}"
        response = self.put(url=url, data=data, params=params)
        return response

    @wait_and_retry_on_http_error(timeout_sec=4)
    def create_streamsets_flow(self, params: dict, data: str) -> requests.Response:
        """Create a Streamsets Flow.

        Args:
            params: The Query params.
            data: The payload data.

        Returns:
           A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows"
        response = self.post(url=url, data=data, params=params)
        return response

    def duplicate_streamsets_flow(self, params: dict, flow_id: str, data: str) -> requests.Response:
        """Duplicate a Streamsets Flow.

        Args:
            params: The Query params.
            flow_id: The Flow ID.
            data: The payload data.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/streamsets_flows/{quote(flow_id, safe='')}/duplicate"
        response = self.post(url=url, data=data, params=params)
        return response

    def get_streamsets_connection(self, connection_id: str, params: dict[str, Any]) -> requests.Response:
        """Get StreamSets connection.

        Args:
            connection_id: Connection id.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/{quote(connection_id, safe='')}"
        return self.get(url=url, params=params)

    def get_streamsets_connections(self, params: dict[str, Any]) -> requests.Response:
        """List defined StreamSets connections.

        Args:
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}"
        return self.get(url=url, params=params)
