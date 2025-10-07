#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Job API client."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_JOBS_COMMON_CORE_API_VERSION = 2


class JobApiClient(BaseAPIClient):
    """The API client for resources related with Jobs and Job Runs."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://api.dataplatform.cloud.ibm.com",
    ) -> None:
        """The __init__ of the JobApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL.
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path_common_core = f"v{DEFAULT_JOBS_COMMON_CORE_API_VERSION}/jobs"

    def get_jobs(self, params: dict[str, Any]) -> requests.Response:
        """Retrieves list of Jobs for specified project.

        Args:
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}"
        response = self.get(url=url, params=params)
        return response

    def get_job(self, job_id: str, params: dict[str, Any]) -> requests.Response:
        """Retrieves information about selected Job.

        Args:
            job_id: The ID of the job to use.
            params: Query Parameters.
        f
        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}/{quote(job_id, safe='')}"
        response = self.get(url, params=params)
        return response

    def create_job(self, data: dict, params: dict[str, Any]) -> requests.Response:
        """Creates a Job instance.

        Args:
            data: Payload required to create a new Job.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}"
        response = self.post(url, data=data, params=params)
        return response

    def delete_job(self, job_id: str, params: dict[str, Any]) -> requests.Response:
        """Remove a Job.

        Args:
            job_id: The ID of the job to use.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}/{quote(job_id, safe='')}"
        response = self.delete(url, params=params)
        return response

    def update_job(self, job_id: str, data: list[dict], params: dict[str, Any]) -> requests.Response:
        """Patch Job attributes.

        Args:
            job_id: The ID of the job to use.
            data: List of patch operation to do on a Job.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}/{quote(job_id, safe='')}"
        response = self.patch(url, data=data, params=params)
        return response

    def get_job_runs(self, job_id: str, params: dict[str, Any]) -> requests.Response:
        """Retrieves list of Job Runs for a Job.

        Args:
            job_id: The ID of the job to use.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}/{quote(job_id, safe='')}/runs"
        response = self.get(url, params=params)
        return response

    def get_job_run(self, run_id: str, job_id: str, params: dict[str, Any]) -> requests.Response:
        """Retrieves information about selected Job Run.

        Args:
            run_id: The ID of the job run.
            job_id: The ID of the job to use.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}/{quote(job_id, safe='')}/runs/{quote(run_id, safe='')}"
        response = self.get(url, params=params)
        return response

    def delete_job_run(self, run_id: str, job_id: str, params: dict[str, Any]) -> requests.Response:
        """Delete single run for a Job.

        Args:
            run_id: The ID of the job run.
            job_id: The ID of the job to use.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}/{quote(job_id, safe='')}/runs/{quote(run_id, safe='')}"
        response = self.delete(url, params=params)
        return response

    def create_job_run(self, job_id: str, data: dict, params: dict[str, Any]) -> requests.Response:
        """Create Job Run instance for given asset.

        Args:
            job_id: The ID of the job to use.
            data: Payload with job run configuration.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}/{quote(job_id, safe='')}/runs"
        response = self.post(url, data=data, params=params)
        return response

    def cancel_job_run(self, run_id: str, job_id: str, data: dict, params: dict[str, Any]) -> requests.Response:
        """Cancel already running job run.

        Args:
            run_id: The ID of the job run.
            job_id: The ID of the job to use.
            data: Required by POST endpoint, actually sends empty dictionary.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = (
            f"{self.base_url}/{self.url_path_common_core}/{quote(job_id, safe='')}/runs/{quote(run_id, safe='')}/cancel"
        )
        response = self.post(url, data=data, params=params)
        return response

    def get_job_run_logs(self, run_id: str, job_id: str, params: dict[str, Any]) -> requests.Response:
        """Retrieves list of logs for job run.

        Args:
            run_id: The ID of the job run.
            job_id: The ID of the job to use.
            params: Query Parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}/{quote(job_id, safe='')}/runs/{quote(run_id, safe='')}/logs"
        response = self.get(url, params=params)
        return response

    def get_swagger(self) -> requests.Response:
        """Retrieve the swagger definitions to retrieve projects.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_common_core}/docs/schemas/v2-swagger.yaml"
        response = self.get(url=url)
        return response
