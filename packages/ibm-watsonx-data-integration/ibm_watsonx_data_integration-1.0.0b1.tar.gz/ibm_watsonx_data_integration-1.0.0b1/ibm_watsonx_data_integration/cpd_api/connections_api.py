#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Connections API client."""

import requests
from .base import BaseAPIClient
from ibm_watsonx_data_integration.common.auth import BaseAuthenticator
from ibm_watsonx_data_integration.cpd_api.adapters import DefaultHTTPAdapter
from pathlib import Path
from typing import Any
from urllib.parse import quote

DEFAULT_CONNECTIONS_API_VERSION = 2
DEFAULT_DATASOURCE_TYPES_API_VERSION = 2


class ConnectionsApiClient(BaseAPIClient):
    """The API client for resources related with Connections."""

    def __init__(self, auth: BaseAuthenticator, base_url: str = "https://api.dataplatform.cloud.ibm.com") -> None:
        """The __init__ of the ConnectionsApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL. Default: ``https://api.dataplatform.cloud.ibm.com``.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path_connections = f"v{DEFAULT_CONNECTIONS_API_VERSION}/connections"
        self.url_path_datasource_types = f"v{DEFAULT_DATASOURCE_TYPES_API_VERSION}/datasource_types"

    def get_connections(self, params: dict[str, Any]) -> requests.Response:
        """List defined connections.

        Args:
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}"
        return self.get(url=url, params=params)

    def add_connection(self, data: dict[str, Any], params: dict[str, Any]) -> requests.Response:
        """Define connection.

        Args:
            params: REST Query Parameters.
            data: REST Query payload. This should be an entity (without `metadata`) of the connection.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}"
        return self.post(url=url, params=params, data=data)

    def get_connection(self, connection_id: str, params: dict[str, Any]) -> requests.Response:
        """Get connection.

        Args:
            connection_id: Connection id.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/{quote(connection_id, safe='')}"
        return self.get(url=url, params=params)

    def delete_connection(self, connection_id: str, params: dict[str, Any]) -> requests.Response:
        """Delete connection.

        Args:
            connection_id: Connection id.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/{quote(connection_id, safe='')}"
        return self.delete(url=url, params=params)

    def update_connection(self, connection_id: str, data: dict[str, Any], params: dict[str, Any]) -> requests.Response:
        """Update connection.

        Args:
            connection_id: Connection id.
            data: REST Query payload.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/{quote(connection_id, safe='')}"
        adapter = DefaultHTTPAdapter(auth=self._auth)
        adapter._custom_headers["Content-Type"] = "application/json-patch+json;charset=utf-8"

        return self.patch(url=url, params=params, data=data, adapter=adapter)

    def copy_connection(self, connection_id: str, params: dict[str, Any]) -> requests.Response:
        """Copy connection.

        Args:
            connection_id: Connection id.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/{quote(connection_id, safe='')}/copy"
        return self.post(url=url, params=params)

    def get_connections_assets(self, data: dict[str, Any], params: dict[str, Any]) -> requests.Response:
        """Discover connections assets.

        Args:
            data: REST Query payload. This should be an entity (without `metadata`) of the connection.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/assets"
        return self.post(url=url, params=params, data=data)

    def get_connection_assets(self, connection_id: str, params: dict[str, Any]) -> requests.Response:
        """Get connection assets.

        Args:
            connection_id: Connection id.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/{quote(connection_id, safe='')}/assets"
        return self.get(url=url, params=params)

    def get_connections_asset_data(self, connection_asset_id: str, params: dict[str, Any]) -> requests.Response:
        """Get connections asset data.

        Args:
            connection_asset_id: Connection asset id.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/assets/{quote(connection_asset_id, safe='')}"
        return self.get(url=url, params=params)

    def get_connection_actions(self, connection_id: str, params: dict[str, Any]) -> requests.Response:
        """Get connection actions.

        Args:
            connection_id: Connection id.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/{quote(connection_id, safe='')}/actions"
        return self.get(url=url, params=params)

    def perform_connection_action(
        self, connection_id: str, action_name: str, params: dict[str, Any], data: dict[str, Any]
    ) -> requests.Response:
        """Perform connection action.

        Args:
            connection_id: Connection id.
            action_name: Action name.
            params: REST Query Parameters.
            data: Action request configuration.

        Returns:
            A HTTP response.
        """
        url = (
            f"{self.base_url}/{self.url_path_connections}/{quote(connection_id, safe='')}/actions/"
            f"{quote(action_name, safe='')}"
        )
        return self.put(url=url, params=params, data=data)

    def get_version(self, params: dict[str, Any] | None = None) -> requests.Response:
        """Gets version and other information about the connections service.

        Args:
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/version"
        return self.get(url=url, params=params or dict())

    def get_functional_ids(self, params: dict[str, Any] | None = None) -> requests.Response:
        """Get the list of functional IDs.

        Args:
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/functional_ids"
        return self.get(url=url, params=params or dict())

    def get_file(self, name: str, hash: str, output: Path) -> None:
        """Download a file.

        Args:
            name: The name of file to download.
            hash: The hash of file to download.
            output: Output path for the downloading file.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/files/{quote(name, safe='')}"

        adapter = DefaultHTTPAdapter(auth=self._auth)
        adapter._custom_headers["Content-Type"] = "application/octet-stream"

        params = {"hash": hash}
        response = self.get(url=url, params=params, adapter=adapter)
        with output.open("wb") as byte_file:
            byte_file.write(response.content)

    def upload_file(self, file_name: str, file: Path) -> requests.Response:
        """Upload a file and get back a signed handle in 'Location' header with a hash.

        Args:
            file_name: The name of file to upload.
            file: Path to the uploaded file.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/files/{quote(file_name, safe='')}"

        adapter = DefaultHTTPAdapter(auth=self._auth)
        adapter._custom_headers["Content-Type"] = "application/octet-stream"

        with file.open("rb") as byte_file:
            return self.post(url=url, data=byte_file.read(), adapter=adapter)

    def delete_file(self, name: str, hash: str) -> requests.Response:
        """Delete a file.

        Args:
            name: The name of file to delete.
            hash: The hash of file to download.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/files/{quote(name, safe='')}"
        params = {"hash": hash}
        return self.delete(url=url, params=params)

    def get_file_list(self, params: dict[str, Any] | None = None) -> requests.Response:
        """List files available in mounted directory.

        Args:
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/files"
        return self.get(url=url, params=params or dict())

    def move_files(self, params: dict[str, Any]) -> requests.Response:
        """Migrates files from old locations to new one.

        Args:
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/files"
        return self.put(url=url, params=params)

    def get_datasources(self, params: dict[str, Any] | None = None) -> requests.Response:
        """Gets all defined types of data sources.

        Args:
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        params = params or dict()
        params["connection_properties"] = True
        url = f"{self.base_url}/{self.url_path_datasource_types}"
        return self.get(url=url, params=params)

    def add_datasource(self, data: dict[str, Any]) -> requests.Response:
        """Defines a data source type.

        Args:
            data: REST Query Payload. The definition of the data source type.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_datasource_types}"
        return self.post(url=url, data=data)

    def get_datasource(self, datasource_type: str, params: dict[str, Any]) -> requests.Response:
        """Get details for type of data source.

        Args:
            datasource_type: The data source type.
            params: REST Query Parameters.

        Returns:
            A HTTP response.
        """
        params = params or dict()
        params["connection_properties"] = True
        url = f"{self.base_url}/{self.url_path_datasource_types}/{quote(datasource_type, safe='')}"
        return self.get(url=url, params=params)

    def delete_datasource(self, datasource_type: str) -> requests.Response:
        """Deletes a data source type definition.

        Args:
            datasource_type: The data source type.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_datasource_types}/{quote(datasource_type, safe='')}"
        return self.delete(url=url)

    def update_datasource(self, datasource_type: str) -> requests.Response:
        """Updates the definition of a datasource type.

        Args:
            datasource_type: The data source type.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_datasource_types}/{quote(datasource_type, safe='')}"
        return self.patch(url=url)

    def get_swagger(self) -> requests.Response:
        """Retrieve the swagger definitions to retrieve connections.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_connections}/api/docs"
        return self.get(url=url)
