#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Metering API client."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_METERING_API_VERSION = 1


class MeteringApiClient(BaseAPIClient):
    """The API client for resources related with Jobs and Job Runs."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://api.dai.dataplatform.cloud.ibm.com",
    ) -> None:
        """The __init__ of the JobApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"sset/metering/v{DEFAULT_METERING_API_VERSION}"

    def get_billing_data(self, params: dict[str, Any]) -> requests.Response:
        """Retrieves metering billing data.

        Args:
            params: Query Parameters.
        f
        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/metering_data/billing"
        response = self.get(url, params=params)
        return response

    def get_engine_metrics(self, params: dict[str, Any]) -> requests.Response:
        """Retrieves meterrics based on engine id.

        Args:
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/metering_event/utilization_by_engine_id"
        response = self.get(url, params=params)
        return response

    def save_engine_metrics(
        self,
        data: dict,
    ) -> requests.Response:
        """Send a payload of metrics mostly from Engine Manager and metering will save it.

        Args:
            data: Requires by POST endpoint.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/metering_event/save"
        response = self.post(url, data=data)
        return response
