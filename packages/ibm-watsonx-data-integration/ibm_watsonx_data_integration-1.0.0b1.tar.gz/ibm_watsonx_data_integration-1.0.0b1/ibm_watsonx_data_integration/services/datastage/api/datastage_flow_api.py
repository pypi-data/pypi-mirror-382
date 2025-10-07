# (C) Copyright IBM Corp. 2025.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# IBM OpenAPI SDK Code Generator Version: 3.100.0-2ad7a784-20250212-162551

"""The IBM  Data API Data Flow service provides APIs to generate runtime assets, manage,
edit, compile, and run data flows in supported runtimes such as PX-Engine.

API Version: 3.0.0
"""

import datetime as dt  # not to be confused with the other import, sadly; this is for the helper functions
import json
import requests
from datetime import datetime
from enum import Enum

# from ibm_cloud_sdk_core import get_query_param
# from ibm_cloud_sdk_core.utils import (
#     convert_list,
#     convert_model,
#     datetime_to_string,
#     string_to_datetime,
#     strip_extra_slashes,
# )
# new imports
from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

# from .common import get_sdk_headers
# from .custom_base_service import CustomBaseService
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import BinaryIO, Optional
from urllib.parse import parse_qs, urlparse

# new imports

# Helper functions

### Temporarily borrowed from ibm_cloud_sdk_core until that module is in use again (if ever)


def _get_query_param(url_str: str, param: str) -> str:
    """Return a query parameter value from url_str

    Args:
        url_str: the URL from which to extract the query
            parameter value
        param: the name of the query parameter whose value
            should be returned

    Returns:
        the value of the `param` query parameter as a string

    Raises:
        ValueError: if errors are encountered parsing `url_str`
    """
    if not url_str:
        return None
    url = urlparse(url_str)
    if not url.query:
        return None
    query = parse_qs(url.query, strict_parsing=True)
    values = query.get(param)
    return values[0] if values else None


def _convert_list(val: str | list[str]) -> str:
    """Convert a list of strings into comma-separated string.

    Arguments:
        val: A string or list of strings

    Returns:
        A comma-separated string of the items in the input list.
    """
    if isinstance(val, str):
        return val
    if isinstance(val, list) and all(isinstance(x, str) for x in val):
        return ",".join(val)
    # Consider raising a ValueError here in the next major release
    return val


def _convert_model(val: any) -> dict:
    """Convert a model object into an equivalent dict.

    Arguments:
        val: A dict or a model object

    Returns:
        A dict representation of the input object.
    """
    if isinstance(val, dict):
        return val
    if hasattr(val, "to_dict"):
        return val.to_dict()
    # Consider raising a ValueError here in the next major release
    return val


def _datetime_to_string(val: dt.datetime) -> str:
    """Convert a datetime object to string.

    If the supplied datetime does not specify a timezone,
    it is assumed to be UTC.

    Args:
        val: The datetime object.

    Returns:
        datetime serialized to iso8601 format.
    """
    if isinstance(val, dt.datetime):
        if val.tzinfo is None:
            return val.isoformat() + "Z"
        val = val.astimezone(dt.timezone.utc)
        return val.isoformat().replace("+00:00", "Z")
    return val


def _string_to_datetime(string: str) -> dt.datetime:
    """De-serializes string to datetime.

    Args:
        string: string containing datetime in iso8601 format.

    Returns:
        the de-serialized string as a datetime object.
    """
    val = datetime.fromisoformat(string)
    if val.tzinfo is not None:
        return val
    return val.replace(tzinfo=dt.timezone.utc)


def _strip_extra_slashes(value: str) -> str:
    """Combine multiple trailing slashes to a single slash"""
    if value.endswith("//"):
        return value.rstrip("/") + "/"
    return value


### Headers

# def {"agentname":"watsonx-di-sdk"}:
#     # pylint: disable=unused-argument
#     """Get the request headers to be sent in requests by the SDK.

#     If you plan to gather metrics for your SDK, the User-Agent header value must
#     be a string similar to the following:
#     watsonx-di-sdk/0.0.1 (lang=python; arch=x86_64; os=Linux; python.version=3.7.4)

#     In the example above, the analytics tool will parse the user-agent header and
#     use the following properties:
#     "watsonx-di-sdk" - the name of your sdk
#     "0.0.1"- the version of your sdk
#     "lang=python" - the language of the current sdk
#     "arch=x86_64; os=Linux; python.version=3.7.4" - system information

#     Note: It is very important that the sdk name ends with the string `-sdk`,
#     as the analytics data collector uses this to gather usage data.
#     """
#     headers = {}
#     headers["agentname"] = "watsonx-di-sdk"
#     return headers


##############################################################################
# Service
##############################################################################


class DatastageFlowApiClient(BaseAPIClient):
    """The IBM API For Data Flow Service V3 service."""

    DEFAULT_SERVICE_URL = "https://dataplatform.dev.cloud.ibm.com/"
    DEFAULT_SERVICE_NAME = "datastage"
    disable_ssl = False

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://api.dataplatform.cloud.ibm.com",
        disable_ssl_verification=False,
    ) -> None:
        """Construct a new client for the IBM API For Data Flow Service service.

        Args:
            auth: The Authentication object.
            base_url: The DataStage Flow URL.
        """
        super().__init__(auth=auth, base_url=base_url)

        self.disable_ssl = disable_ssl_verification

    def send_request(
        self,
        method: str,
        path: str,
        headers: dict | None = None,
        params: dict | None = None,
        data: dict | str | None = None,
        verify: bool | str = disable_ssl,
    ) -> requests.Response:
        """Sends a request with the given method, URL, headers, and other info and returns the resulting response.

        The purpose of this indirect method is to simplify the conversion to responses in the current base API client
        from responses in the old client.

        Args:
            method: The HTTP method of the request ex. GET, POST, etc.
            path: The origin + pathname according to WHATWG spec. In other words, the API call pathname.
            params: HTTP request parameters.
            data: HTTP request payload.
            headers: HTTP request headers to add to the request. Can overwrite default set headers.
            verify: Whether to verify a request. Can also be a path to a certificate file.

        Returns:
            An HTTP response from making the call.
        """
        full_url = _strip_extra_slashes(str(self.base_url) + path)
        return self._request(method=method, url=full_url, params=params, data=data, headers=headers, verify=verify)

    # Helper function
    @staticmethod
    def _encode_path_vars(*args: str) -> list[str]:
        """Encode path variables to be substituted into a URL path.

        Arguments:
            args: A list of strings to be URL path encoded

        Returns:
            A list of encoded strings that are safe to substitute into a URL path.
        """
        return (requests.utils.quote(x, safe="") for x in args)

    #########################
    # General
    #########################

    def datastage_flows_version(
        self,
        **kwargs,
    ) -> requests.Response:
        """Get version information about the service.

        Get version information about the service. This can also be used as part of a
        heartbeat mechanism to confirm the service is up and running. This API is expected
        to always return with a status of 200, even if some components are not running
        correctly.

        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `VersionInfo` object
        """
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/version"

        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
        )

    def datastage_codegen_version(
        self,
        **kwargs,
    ) -> requests.Response:
        """Get version information about the service.

        Get version information about the service. This can also be used as part of a
        heartbeat mechanism to confirm the service is up and running. This API is expected
        to always return with a status of 200, even if some components are not running
        correctly.

        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `VersionInfo` object
        """
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        url = "/data_intg/v3/ds_codegen/version"
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
        )

    #########################
    # DataStage flows
    #########################

    def list_datastage_flows(
        self,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        sort: str | None = None,
        start: str | None = None,
        limit: int | None = None,
        entity_name: str | None = None,
        entity_description: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get metadata for DataStage flows.

        Lists the metadata and entity for DataStage flows that are contained in the
        specified project.
        Use the following parameters to filter the results:
        | Field                    | Match type   | Example
         |
        | ------------------------ | ------------ |
        --------------------------------------- |
        | `entity.name`              | Equals           | `entity.name=MyDataStageFlow`  |
        | `entity.name`              | Starts with      | `entity.name=starts:MyData`  |
        | `entity.description`       | Equals           | `entity.description=movement`  |
        | `entity.description`       | Starts with      | `entity.description=starts:data`
         |
        To sort the results, use one or more of the parameters  described in the following
        section. If no sort key is specified, the results are sorted in descending order
        on `metadata.create_time` (i.e. returning the most  recently created data flows
        first).
        | Field                          | Example |
        | ------------------------- | ----------------------------------- |
        | sort     | `sort=+entity.name` (sort by ascending name)  |
        | sort     | `sort=-metadata.create_time` (sort by descending creation time) |
        Multiple sort keys can be specified by delimiting them with a comma. For example,
        to sort in descending order on `create_time` and then in ascending order on name
        use: `sort=-metadata.create_time`,`+entity.name`.

        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str sort: (optional) The field to sort the results on, including
               whether to sort ascending (+) or descending (-), for example,
               sort=-metadata.create_time.
        :param str start: (optional) The page token indicating where to start
               paging from.
        :param int limit: (optional) The limit of the number of items to return for
               each page, for example limit=50. If not specified a default of 100 will be
               used. The maximum value of limit is 200.
        :param str entity_name: (optional) Filter results based on the specified
               name.
        :param str entity_description: (optional) Filter results based on the
               specified description.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataFlowPagedCollection` object
        """
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "sort": sort,
            "start": start,
            "limit": limit,
            "entity.name": entity_name,
            "entity.description": entity_description,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows"
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def create_datastage_flows(
        self,
        data_intg_flow_name: str,
        *,
        pipeline_flows: Optional["PipelineJson"] = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        directory_asset_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Create DataStage flow.

        Creates a DataStage flow in the specified project or catalog (either `project_id`
        or `catalog_id` must be set). All subsequent calls to use the data flow must
        specify the project or catalog ID the data flow was created in.

        :param str data_intg_flow_name: The data flow name.
        :param PipelineJson pipeline_flows: (optional) Pipeline flow to be stored.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str directory_asset_id: (optional) The directory asset ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if not data_intg_flow_name:
            raise ValueError("data_intg_flow_name must be provided")
        if pipeline_flows is not None:
            pipeline_flows = _convert_model(pipeline_flows)
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "data_intg_flow_name": data_intg_flow_name,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "directory_asset_id": directory_asset_id,
        }

        data = {
            "pipeline_flows": pipeline_flows,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows"
        return self.send_request(method="POST", path=url, headers=headers, params=params, data=data, verify=True)

    def delete_datastage_flows(
        self,
        id: list[str],
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        force: bool | None = None,
        **kwargs,
    ) -> requests.Response:
        """Delete DataStage flows.

        Deletes the specified data flows in a project or catalog (either `project_id` or
        `catalog_id` must be set).
        If the deletion of the data flows and their runs will take some time to finish,
        then a 202 response will be returned and the deletion will continue
        asynchronously.
                 All the data flow runs associated with the data flows will also be
        deleted. If a data flow is still running, it will not be deleted unless the force
        parameter is set to true. If a data flow is still running and the force parameter
        is set to true, the call returns immediately with a 202 response. The related data
        flows are deleted after the data flow runs are stopped.

        :param List[str] id: The list of DataStage flow IDs to delete.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param bool force: (optional) Whether to stop all running data flows.
               Running DataStage flows must be stopped before the DataStage flows can be
               deleted.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response
        """
        if id is None:
            raise ValueError("id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "id": _convert_list(id),
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "force": force,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]

        url = "/data_intg/v3/data_intg_flows"
        return self.send_request(
            method="DELETE",
            path=url,
            headers=headers,
            params=params,
        )

    def import_datastage_flows(
        self,
        *,
        metadata: list["DataIntgFlow"] | None = None,
        asset_ref_map: dict | None = None,
        owner_id: str | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Import DataStage flow.

        Import DataStage flow that is called by project import feature.

        :param List[DataIntgFlow] metadata: (optional) Metadata information for
               DataStage flow import.
        :param dict asset_ref_map: (optional) Asset reference map for DataStage
               flow.
        :param str owner_id: (optional) owner ID for DataStage flow import.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if metadata is not None:
            metadata = [_convert_model(x) for x in metadata]
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = {
            "metadata": metadata,
            "asset_ref_map": asset_ref_map,
            "owner_id": owner_id,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/import"
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def export_datastage_flows(
        self,
        data_intg_flow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Export DataStage flow.

        Export DataStage flow that is called by project export feature.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlowExport` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}/export".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def get_datastage_flows(
        self,
        data_intg_flow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get DataStage flow.

        Lists the DataStage flow that is contained in the specified project. Attachments,
        metadata and a limited number of attributes from the entity of each DataStage flow
        is returned.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlowJson` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def update_datastage_flows(
        self,
        data_intg_flow_id: str,
        data_intg_flow_name: str,
        *,
        pipeline_flows: Optional["PipelineJson"] = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        directory_asset_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Update DataStage flow.

        Modifies a data flow in the specified project or catalog (either `project_id` or
        `catalog_id` must be set). All subsequent calls to use the data flow must specify
        the project or catalog ID the data flow was created in.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str data_intg_flow_name: The data flow name.
        :param PipelineJson pipeline_flows: (optional) Pipeline flow to be stored.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str directory_asset_id: (optional) The directory asset ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        if not data_intg_flow_name:
            raise ValueError("data_intg_flow_name must be provided")
        if pipeline_flows is not None:
            pipeline_flows = _convert_model(pipeline_flows)
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "data_intg_flow_name": data_intg_flow_name,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "directory_asset_id": directory_asset_id,
        }

        data = {
            "pipeline_flows": pipeline_flows,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}".format(**path_param_dict)
        return self.send_request(method="PUT", path=url, headers=headers, params=params, data=data, verify=True)

    def clone_datastage_flows(
        self,
        data_intg_flow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        directory_asset_id: str | None = None,
        data_intg_flow_name: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Clone DataStage flow.

        Create a DataStage flow in the specified project or catalog or space based on an
        existing DataStage flow in the same project or catalog or space.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str directory_asset_id: (optional) The directory asset ID.
        :param str data_intg_flow_name: (optional) The data flow name.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "directory_asset_id": directory_asset_id,
            "data_intg_flow_name": data_intg_flow_name,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}/clone".format(**path_param_dict)
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
        )

    def set_datastage_flow_relationships(
        self,
        data_intg_flow_id: str,
        *,
        pipeline_flows: Optional["PipelineJson"] = None,
        usage: str | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Create relationships between DataStage flow and its referenced assets.

        Create relationships between given DataStage flow in the specified project or
        catalog or space and its referenced assets.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param PipelineJson pipeline_flows: (optional) Pipeline flow to be stored.
        :param str usage: (optional) Caller.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlowRelationships` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        if pipeline_flows is not None:
            pipeline_flows = _convert_model(pipeline_flows)
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "usage": usage,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = {
            "pipeline_flows": pipeline_flows,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}/relationships".format(**path_param_dict)
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def datastage_flows_compile_info(
        self,
        data_intg_flow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        include_osh: bool | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get compile information for a DataStage flow.

        Returns compile information for a DataStage flow in the specified project. The
        response contains a metadata section which indicates if the current flow was
        compiled or not and an entity section which contains the DataStage flow ID.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param bool include_osh: (optional) Caller.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlowCompile` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "includeOSH": include_osh,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}/flowbinary".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def patch_attributes_datastage_flow(
        self,
        data_intg_flow_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        directory_asset_id: str | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Modifies attributes of a DataStage flow.

        Modifies attributes of a DataStage flow in the specified project or catalog
        (either `project_id` or `catalog_id` must be set).

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str name: (optional) name of the asset.
        :param str description: (optional) description of the asset.
        :param str directory_asset_id: (optional) The directory asset ID of the
               asset.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = {
            "name": name,
            "description": description,
            "directory_asset_id": directory_asset_id,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}/attributes".format(**path_param_dict)
        return self.send_request(
            method="PUT",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def get_zip_attachments(
        self,
        data_intg_flow_id: str,
        attachment_type: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get runtime asset for a DataStage flow.

        Gets runtime asset for a given DataStage flow in a project. This is retrieved from
        the cloud object storage(COS) as a stream of bytes.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str attachment_type: Type of attachment to be inserted/retrieved.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `BinaryIO` result
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        if not attachment_type:
            raise ValueError("attachment_type must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "attachment_type": attachment_type,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/octet-stream"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}/zip".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def update_zip_attachments(
        self,
        data_intg_flow_id: str,
        attachment_type: str,
        *,
        body: BinaryIO | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Replace runtime asset for a DataStage flow.

        Replace runtime asset for a DataStage flow in the specified project. This is
        inserted into cloud object storage(COS) as a stream of bytes.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str attachment_type: Type of attachment to be inserted/retrieved.
        :param BinaryIO body: (optional)
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        if not attachment_type:
            raise ValueError("attachment_type must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "attachment_type": attachment_type,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = body
        headers["content-type"] = "application/octet-stream"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}/zip".format(**path_param_dict)
        return self.send_request(
            method="PUT",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def delete_zip_attachment(
        self,
        data_intg_flow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Delete runtime asset for a DataStage flow.

        Deletes runtime asset for a given DataStage flow in a project. This is to delete
        the px_executables attachment from the cloud object storage(COS).

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}/zip".format(**path_param_dict)
        return self.send_request(
            method="DELETE",
            path=url,
            headers=headers,
            params=params,
        )

    def datastage_flows_get_dependencies(
        self,
        data_intg_flow_id: str,
        *,
        usage: str | None = None,
        use_cached_parameters: bool | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        asset_type: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get DataStage flow with dependencies.

        Gets the DataStage flow that is contained in the specified project. Attachments,
        metadata and a limited number of attributes from the entity of each DataStage flow
        is returned.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str usage: (optional) Caller.
        :param bool use_cached_parameters: (optional) Specify whether using
               parameter information from cache.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str asset_type: (optional)
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "usage": usage,
            "use_cached_parameters": use_cached_parameters,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "asset_type": asset_type,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}/dependencies".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def get_datastage_flow_parms(
        self,
        data_intg_flow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        asset_type: str | None = None,
        use_cached_parameters: bool | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get referenced parameters and parameter sets information of a DataStage flow.

        Returns referenced parameters and parameter sets information of a DataStage flow.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str asset_type: (optional) Caller.
        :param bool use_cached_parameters: (optional) Specify whether using
               parameter information from cache.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlowReferencedParm` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "asset_type": asset_type,
            "use_cached_parameters": use_cached_parameters,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/{data_intg_flow_id}/referencedparms".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def get_datastage_flow_asset_parms(
        self,
        asset_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        use_cached_parameters: bool | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get referenced parameters and parameter sets information of a DataStage flow.

        Returns referenced parameters and parameter sets information of a DataStage flow.

        :param str asset_id: The data flow asset id.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param bool use_cached_parameters: (optional) Specify whether using
               parameter information from cache.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlowAssetParm` object
        """
        if not asset_id:
            raise ValueError("asset_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "asset_id": asset_id,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "use_cached_parameters": use_cached_parameters,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/asset_parameters"
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def get_datastage_flow_unknown_parms(
        self,
        asset_id: str,
        *,
        parameters: list[dict] | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get types of unknown parameters.

        Returns referenced parameters and parameter sets information of a DataStage flow.

        :param str asset_id: The data flow asset id.
        :param List[dict] parameters: (optional) list of parameters, properties of
               each can have name and type.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlowUnknownParameters` object
        """
        if not asset_id:
            raise ValueError("asset_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "asset_id": asset_id,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = {
            "parameters": parameters,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/unknown_parameters"
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def flow_dependencies_update(
        self,
        *,
        pipeline_flows: Optional["PipelineJson"] = None,
        flow_id: str | None = None,
        flow_name: str | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Create/update DataStage flow including referenced asset Ids.

        Creates a DataStage flow in the specified project or catalog (either `project_id`
        or `catalog_id` must be set). All subsequent calls to use the data flow must
        specify the project or catalog ID the data flow was created in.

        :param PipelineJson pipeline_flows: (optional) Pipeline flow to be stored.
        :param str flow_id: (optional)
        :param str flow_name: (optional)
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if pipeline_flows is not None:
            pipeline_flows = _convert_model(pipeline_flows)
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "flow_id": flow_id,
            "flow_name": flow_name,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = {
            "pipeline_flows": pipeline_flows,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/dependencies_update"
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def subflow_dependencies_update(
        self,
        *,
        pipeline_flows: Optional["PipelineJson"] = None,
        subflow_id: str | None = None,
        subflow_name: str | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Create/update DataStage subflow including referenced asset Ids.

        Creates/Updates a DataStage subflow in the specified project or catalog (either
        `project_id` or `catalog_id` must be set). All subsequent calls to use the data
        flow must specify the project or catalog ID the data flow was created in.

        :param PipelineJson pipeline_flows: (optional) Pipeline flow to be stored.
        :param str subflow_id: (optional)
        :param str subflow_name: (optional)
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if pipeline_flows is not None:
            pipeline_flows = _convert_model(pipeline_flows)
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "subflow_id": subflow_id,
            "subflow_name": subflow_name,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = {
            "pipeline_flows": pipeline_flows,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/subflows/dependencies_update"
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def compile_datastage_flows(
        self,
        data_intg_flow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        runtime_type: str | None = None,
        enable_sql_pushdown: bool | None = None,
        enable_async_compile: bool | None = None,
        enable_pushdown_source: bool | None = None,
        enable_push_processing_to_source: bool | None = None,
        enable_push_join_to_source: bool | None = None,
        enable_pushdown_target: bool | None = None,
        delete_lastest_osh_on_failure: bool | None = None,
        **kwargs,
    ) -> requests.Response:
        """Compile DataStage flow to generate runtime assets.

        Generate the runtime assets for a DataStage flow in the specified project or
        catalog for a specified runtime type. Either project_id or catalog_id must be
        specified.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str runtime_type: (optional) The type of the runtime to use. e.g.
               dspxosh or Spark etc. If not provided queried from within pipeline flow if
               available otherwise default of dspxosh is used.
        :param bool enable_sql_pushdown: (optional) Whether to enable the SQL
               pushdown code generation or not. When this flag is set to true and
               enable_pushdown_source is not specified, enable_pushdown_source will be set
               to true. When this flag is set to true and enable_pushdown_target is not
               specified, enable_pushdown_target will be set to true.
        :param bool enable_async_compile: (optional) Whether to compile the flow
               asynchronously or not. When set to true, the compile request will be queued
               and then compiled. Response will be returned immediately as "Compiling".
               For compile status, call get compile status api.
        :param bool enable_pushdown_source: (optional) Whether to enable the push
               sql to source connectors. Setting this flag to true will automatically set
               enable_sql_pushdown to true if the latter is not specified or is explicitly
               set to false. When this flag is set to true and
               enable_push_processing_to_source is not specified,
               enable_push_processing_to_source will be automatically set to true as well.
               When this flag is set to true and enable_push_join_to_source is not
               speicified, enable_push_join_to_source will be automatically set to true as
               well.
        :param bool enable_push_processing_to_source: (optional) Whether to enable
               pushing processing stages to source connectors or not. Setting this flag to
               true will automatically set enable_pushdown_source to true if the latter is
               not specified or is explicitly set to false.
        :param bool enable_push_join_to_source: (optional) Whether to enable
               pushing join/lookup stages to source connectors or not. Setting this flag
               to true will automatically set enable_pushdown_source to true if the latter
               is not specified or is explicitly set to false.
        :param bool enable_pushdown_target: (optional) Whether to enable the push
               sql to target connectors. Setting this flag to true will automatically set
               enable_sql_pushdown to true if the latter is not specified or is explicitly
               set to false.
        :param bool delete_lastest_osh_on_failure: (optional) Whether to delete the
               latest generated OSH if the compile is failed. If not specified, the
               default is false.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `FlowCompileResponse` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "runtime_type": runtime_type,
            "enable_sql_pushdown": enable_sql_pushdown,
            "enable_async_compile": enable_async_compile,
            "enable_pushdown_source": enable_pushdown_source,
            "enable_push_processing_to_source": enable_push_processing_to_source,
            "enable_push_join_to_source": enable_push_join_to_source,
            "enable_pushdown_target": enable_pushdown_target,
            "delete_lastest_osh_on_failure": delete_lastest_osh_on_failure,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/ds_codegen/compile/{data_intg_flow_id}".format(**path_param_dict)
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
        )

    def get_flow_compile_status(
        self,
        data_intg_flow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        enable_sql_pushdown: bool | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get DataStage flow compile status.

        Request compile status of the flow that was previously submitted for compile.
        Either project_id or catalog_id must be specified.

        :param str data_intg_flow_id: The DataStage flow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param bool enable_sql_pushdown: (optional) Whether to enable the SQL
               pushdown code generation or not. When this flag is set to true and
               enable_pushdown_source is not specified, enable_pushdown_source will be set
               to true. When this flag is set to true and enable_pushdown_target is not
               specified, enable_pushdown_target will be set to true.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `FlowCompileStatusResponse` object
        """
        if not data_intg_flow_id:
            raise ValueError("data_intg_flow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "enable_sql_pushdown": enable_sql_pushdown,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        path_param_keys = ["data_intg_flow_id"]
        path_param_values = self._encode_path_vars(data_intg_flow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/ds_codegen/compile/status/{data_intg_flow_id}".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def tuning_datastage_flow(
        self,
        *,
        doc_type: str | None = None,
        version: str | None = None,
        json_schema: str | None = None,
        id: str | None = None,
        primary_pipeline: str | None = None,
        pipelines: list["Pipelines"] | None = None,
        schemas: list[dict] | None = None,
        runtimes: list[dict] | None = None,
        app_data: dict | None = None,
        parameters: dict | None = None,
        external_paramsets: list[dict] | None = None,
        **kwargs,
    ) -> requests.Response:
        """Tuning DataStage flow json for RCP 2.0.

        Internal API to tune a flow json into a new flow json that supports RCP 2.0.

        :param str doc_type: (optional) The document type.
        :param str version: (optional) Pipeline flow version.
        :param str json_schema: (optional) Refers to the JSON schema used to
               validate documents of this type.
        :param str id: (optional) Document identifier, GUID recommended.
        :param str primary_pipeline: (optional) Reference to the primary (main)
               pipeline flow within the document.
        :param List[Pipelines] pipelines: (optional) Array of pipeline.
        :param List[dict] schemas: (optional) Array of data record schemas used in
               the pipeline.
        :param List[dict] runtimes: (optional) Runtime information for pipeline
               flow.
        :param dict app_data: (optional) Object containing app-specific data.
        :param dict parameters: (optional) Parameters for the flow document.
        :param List[dict] external_paramsets: (optional) Array of parameter set
               references.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `PipelineJson` object
        """
        if pipelines is not None:
            pipelines = [_convert_model(x) for x in pipelines]
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        data = {
            "doc_type": doc_type,
            "version": version,
            "json_schema": json_schema,
            "id": id,
            "primary_pipeline": primary_pipeline,
            "pipelines": pipelines,
            "schemas": schemas,
            "runtimes": runtimes,
            "app_data": app_data,
            "parameters": parameters,
            "external_paramsets": external_paramsets,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        url = "/data_intg/v3/ds_codegen/tuning"
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            data=data,
        )

    def compile_express_datastage_flow(
        self,
        request_body: dict,
        **kwargs,
    ) -> requests.Response:
        """Getting the osh for attached json flow.

        Internal API to get osh for a flow json.

        :param dict request_body: Json format for input string to be tested.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `FlowCompileResponse` object
        """
        if request_body is None:
            raise ValueError("request_body must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        data = json.dumps(request_body)
        headers["content-type"] = "application/json;charset=utf-8"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        url = "/data_intg/v3/ds_codegen/compileExpress"
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            data=data,
        )

    #########################
    # DataStage subflows
    #########################

    def list_datastage_subflows(
        self,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        sort: str | None = None,
        start: str | None = None,
        limit: int | None = None,
        entity_name: str | None = None,
        entity_description: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get metadata for DataStage subflows.

        Lists the metadata and entity for DataStage subflows that are contained in the
        specified project.
        Use the following parameters to filter the results:
        | Field                    | Match type   | Example
         |
        | ------------------------ | ------------ |
        --------------------------------------- |
        | `entity.name`              | Equals           | `entity.name=MyDataStageSubFlow`
         |
        | `entity.name`              | Starts with      | `entity.name=starts:MyData`  |
        | `entity.description`       | Equals           | `entity.description=movement`  |
        | `entity.description`       | Starts with      | `entity.description=starts:data`
         |
        To sort the results, use one or more of the parameters  described in the following
        section. If no sort key is specified, the results are sorted in descending order
        on `metadata.create_time` (i.e. returning the most  recently created data flows
        first).
        | Field                          | Example |
        | ------------------------- | ----------------------------------- |
        | sort     | `sort=+entity.name` (sort by ascending name)  |
        | sort     | `sort=-metadata.create_time` (sort by descending creation time) |
        Multiple sort keys can be specified by delimiting them with a comma. For example,
        to sort in descending order on `create_time` and then in ascending order on name
        use: `sort=-metadata.create_time`,`+entity.name`.

        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str sort: (optional) The field to sort the results on, including
               whether to sort ascending (+) or descending (-), for example,
               sort=-metadata.create_time.
        :param str start: (optional) The page token indicating where to start
               paging from.
        :param int limit: (optional) The limit of the number of items to return for
               each page, for example limit=50. If not specified a default of 100 will be
               used. The maximum value of limit is 200.
        :param str entity_name: (optional) Filter results based on the specified
               name.
        :param str entity_description: (optional) Filter results based on the
               specified description.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataFlowPagedCollection` object
        """
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "sort": sort,
            "start": start,
            "limit": limit,
            "entity.name": entity_name,
            "entity.description": entity_description,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/subflows"
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def create_datastage_subflows(
        self,
        data_intg_subflow_name: str,
        *,
        pipeline_flows: Optional["PipelineJson"] = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        directory_asset_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Create DataStage subflow.

        Creates a DataStage subflow in the specified project or catalog (either
        `project_id` or `catalog_id` must be set). All subsequent calls to use the data
        flow must specify the project or catalog ID the data flow was created in.

        :param str data_intg_subflow_name: The DataStage subflow name.
        :param PipelineJson pipeline_flows: (optional) Pipeline flow to be stored.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str directory_asset_id: (optional) The directory asset ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if not data_intg_subflow_name:
            raise ValueError("data_intg_subflow_name must be provided")
        if pipeline_flows is not None:
            pipeline_flows = _convert_model(pipeline_flows)
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "data_intg_subflow_name": data_intg_subflow_name,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "directory_asset_id": directory_asset_id,
        }

        data = {
            "pipeline_flows": pipeline_flows,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/subflows"
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def delete_datastage_subflows(
        self,
        id: list[str],
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Delete DataStage subflows.

        Deletes the specified data subflows in a project or catalog (either `project_id`
        or `catalog_id` must be set).
        If the deletion of the data subflows will take some time to finish, then a 202
        response will be returned and the deletion will continue asynchronously.

        :param List[str] id: The list of DataStage subflow IDs to delete.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response
        """
        if id is None:
            raise ValueError("id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "id": _convert_list(id),
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]

        url = "/data_intg/v3/data_intg_flows/subflows"
        return self.send_request(
            method="DELETE",
            path=url,
            headers=headers,
            params=params,
        )

    def get_datastage_subflows(
        self,
        data_intg_subflow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get DataStage subflow.

        Lists the DataStage subflow that is contained in the specified project.
        Attachments, metadata and a limited number of attributes from the entity of each
        DataStage flow is returned.

        :param str data_intg_subflow_id: The DataStage subflow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlowJson` object
        """
        if not data_intg_subflow_id:
            raise ValueError("data_intg_subflow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_subflow_id"]
        path_param_values = self._encode_path_vars(data_intg_subflow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/subflows/{data_intg_subflow_id}".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def update_datastage_subflows(
        self,
        data_intg_subflow_id: str,
        data_intg_subflow_name: str,
        *,
        pipeline_flows: Optional["PipelineJson"] = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        directory_asset_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Update DataStage subflow.

        Modifies a data subflow in the specified project or catalog (either `project_id`
        or `catalog_id` must be set). All subsequent calls to use the data flow must
        specify the project or catalog ID the data flow was created in.

        :param str data_intg_subflow_id: The DataStage subflow ID to use.
        :param str data_intg_subflow_name: The DataStage subflow name.
        :param PipelineJson pipeline_flows: (optional) Pipeline flow to be stored.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str directory_asset_id: (optional) The directory asset ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if not data_intg_subflow_id:
            raise ValueError("data_intg_subflow_id must be provided")
        if not data_intg_subflow_name:
            raise ValueError("data_intg_subflow_name must be provided")
        if pipeline_flows is not None:
            pipeline_flows = _convert_model(pipeline_flows)
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "data_intg_subflow_name": data_intg_subflow_name,
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "directory_asset_id": directory_asset_id,
        }

        data = {
            "pipeline_flows": pipeline_flows,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_subflow_id"]
        path_param_values = self._encode_path_vars(data_intg_subflow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/subflows/{data_intg_subflow_id}".format(**path_param_dict)
        return self.send_request(
            method="PUT",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def patch_attributes_datastage_subflow(
        self,
        data_intg_subflow_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        directory_asset_id: str | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Modifies attributes of DataStage subflow.

        Modifies attributes of a data subflow in the specified project or catalog (either
        `project_id` or `catalog_id` must be set).

        :param str data_intg_subflow_id: The DataStage subflow ID to use.
        :param str name: (optional) name of the asset.
        :param str description: (optional) description of the asset.
        :param str directory_asset_id: (optional) The directory asset ID of the
               asset.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if not data_intg_subflow_id:
            raise ValueError("data_intg_subflow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = {
            "name": name,
            "description": description,
            "directory_asset_id": directory_asset_id,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_subflow_id"]
        path_param_values = self._encode_path_vars(data_intg_subflow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/subflows/{data_intg_subflow_id}/attributes".format(**path_param_dict)
        return self.send_request(
            method="PUT",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def clone_datastage_subflows(
        self,
        data_intg_subflow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        directory_asset_id: str | None = None,
        data_intg_subflow_name: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Clone DataStage subflow.

        Create a DataStage subflow in the specified project or catalog based on an
        existing DataStage subflow in the same project or catalog.

        :param str data_intg_subflow_id: The DataStage subflow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str directory_asset_id: (optional) The directory asset ID.
        :param str data_intg_subflow_name: (optional) The data subflow name.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if not data_intg_subflow_id:
            raise ValueError("data_intg_subflow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "directory_asset_id": directory_asset_id,
            "data_intg_subflow_name": data_intg_subflow_name,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_subflow_id"]
        path_param_values = self._encode_path_vars(data_intg_subflow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/subflows/{data_intg_subflow_id}/clone".format(**path_param_dict)
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
        )

    def get_datastage_subflow_parms(
        self,
        data_intg_subflow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        use_cached_parameters: bool | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get referenced parameters and parameter sets information of a DataStage subflow.

        Returns referenced parameters and parameter sets information of a DataStage
        subflow.

        :param str data_intg_subflow_id: The DataStage subflow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param bool use_cached_parameters: (optional) Specify whether using
               parameter information from cache.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlowReferencedParm` object
        """
        if not data_intg_subflow_id:
            raise ValueError("data_intg_subflow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "use_cached_parameters": use_cached_parameters,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_subflow_id"]
        path_param_values = self._encode_path_vars(data_intg_subflow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/subflows/{data_intg_subflow_id}/referencedparms".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def export_datastage_subflows(
        self,
        data_intg_subflow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Export DataStage subflow.

        Export DataStage subflow that is called by project export feature.

        :param str data_intg_subflow_id: The DataStage subflow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlowExport` object
        """
        if not data_intg_subflow_id:
            raise ValueError("data_intg_subflow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["data_intg_subflow_id"]
        path_param_values = self._encode_path_vars(data_intg_subflow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/subflows/{data_intg_subflow_id}/export".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def import_datastage_subflows(
        self,
        *,
        metadata: list["DataIntgFlow"] | None = None,
        asset_ref_map: dict | None = None,
        owner_id: str | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Import DataStage subflow.

        Import DataStage subflow that is called by project import feature.

        :param List[DataIntgFlow] metadata: (optional) Metadata information for
               DataStage flow import.
        :param dict asset_ref_map: (optional) Asset reference map for DataStage
               flow.
        :param str owner_id: (optional) owner ID for DataStage flow import.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `DataIntgFlow` object
        """
        if metadata is not None:
            metadata = [_convert_model(x) for x in metadata]
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = {
            "metadata": metadata,
            "asset_ref_map": asset_ref_map,
            "owner_id": owner_id,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/subflows/import"
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def post_update_subflow(
        self,
        data_intg_subflow_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Modifies compilation information of parent flows who are referencing this subflow.

        Modifies compilation information of parent flows who are referencing this subflow.

        :param str data_intg_subflow_id: The DataStage subflow ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response
        """
        if not data_intg_subflow_id:
            raise ValueError("data_intg_subflow_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]

        path_param_keys = ["data_intg_subflow_id"]
        path_param_values = self._encode_path_vars(data_intg_subflow_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/subflows/{data_intg_subflow_id}/postupdate".format(**path_param_dict)
        return self.send_request(
            method="PATCH",
            path=url,
            headers=headers,
            params=params,
        )

    #########################
    # copyTheRules
    #########################

    def copy_files(
        self,
        from_location: str,
        to_location: str,
        *,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Copy the file under the specify from_location to to_location.

        Copy the specify files from from_location to to_location. This is uploaded to the
        cloud object storage(COS).

        :param str from_location:
        :param str to_location:
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `BucketFolder` object
        """
        if not from_location:
            raise ValueError("from_location must be provided")
        if not to_location:
            raise ValueError("to_location must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "from_location": from_location,
            "to_location": to_location,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/files"
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
        )

    #########################
    # dataStageBuildOp
    #########################

    def generate_datastage_buildop(
        self,
        data_intg_bldop_id: str,
        *,
        type: str | None = None,
        general: Optional["BuildopGeneral"] = None,
        creator: Optional["BuildopCreator"] = None,
        properties: list["BuildopPropertiesItem"] | None = None,
        build: Optional["BuildopBuild"] = None,
        wrapped: Optional["BuildopWrapped"] = None,
        schemas: list[dict] | None = None,
        ui_data: dict | None = None,
        directory_asset: dict | None = None,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        runtime_type: str | None = None,
        enable_async_compile: bool | None = None,
        **kwargs,
    ) -> requests.Response:
        """Generate OPD-code for DataStage buildop.

        Generate the runtime assets for a DataStage buildop in the specified project or
        catalog for a specified runtime type. Either project_id or catalog_id must be
        specified.

        :param str data_intg_bldop_id: The DataStage BuildOp-Asset-ID to use.
        :param str type: (optional) The operator type.
        :param BuildopGeneral general: (optional) General information.
        :param BuildopCreator creator: (optional) Creator information.
        :param List[BuildopPropertiesItem] properties: (optional) List of stage
               properties.
        :param BuildopBuild build: (optional) Build info.
        :param BuildopWrapped wrapped: (optional) Wrapped info.
        :param List[dict] schemas: (optional) Array of data record schemas used in
               the buildop.
        :param dict ui_data: (optional) UI data.
        :param dict directory_asset: (optional) directory information.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str runtime_type: (optional) The type of the runtime to use. e.g.
               dspxosh or Spark etc. If not provided queried from within pipeline flow if
               available otherwise default of dspxosh is used.
        :param bool enable_async_compile: (optional) Whether to compile the flow
               asynchronously or not. When set to true, the compile request will be queued
               and then compiled. Response will be returned immediately as "Compiling".
               For compile status, call get compile status api.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `GenerateBuildOpResponse` object
        """
        if not data_intg_bldop_id:
            raise ValueError("data_intg_bldop_id must be provided")
        if general is not None:
            general = _convert_model(general)
        if creator is not None:
            creator = _convert_model(creator)
        if properties is not None:
            properties = [_convert_model(x) for x in properties]
        if build is not None:
            build = _convert_model(build)
        if wrapped is not None:
            wrapped = _convert_model(wrapped)
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "runtime_type": runtime_type,
            "enable_async_compile": enable_async_compile,
        }

        data = {
            "type": type,
            "general": general,
            "creator": creator,
            "properties": properties,
            "build": build,
            "wrapped": wrapped,
            "schemas": schemas,
            "ui_data": ui_data,
            "directory_asset": directory_asset,
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers["content-type"] = "application/json"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        path_param_keys = ["data_intg_bldop_id"]
        path_param_values = self._encode_path_vars(data_intg_bldop_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/ds_codegen/generateBuildOp/{data_intg_bldop_id}".format(**path_param_dict)
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    #########################
    # deleteFiles
    #########################

    def delete_files(
        self,
        location: str,
        *,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Removes all the files under the specify location on the cloud object storage(COS).

        Removes all the files under the specify location on the cloud object storage(COS).

        :param str location: The location.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `BucketFolder` object
        """
        if not location:
            raise ValueError("location must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "location": location,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/files"
        return self.send_request(
            method="DELETE",
            path=url,
            headers=headers,
            params=params,
        )

    #########################
    # downloadAFile
    #########################

    def download_file(
        self,
        location: str,
        file_name: str,
        *,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Download the file from the given location.

        Download the file from the given location.. This is retrieved from the cloud
        object storage(COS).

        :param str location: The location.
        :param str file_name: The file name.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `BinaryIO` result
        """
        if not location:
            raise ValueError("location must be provided")
        if not file_name:
            raise ValueError("file_name must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "location": location,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/octet-stream"

        path_param_keys = ["file_name"]
        path_param_values = self._encode_path_vars(file_name)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/files/{file_name}".format(**path_param_dict)
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    #########################
    # listFiles
    #########################

    def list_files(
        self,
        location: str,
        *,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """List the files in the specify location in a project.

        List the files in the specify location in a project. This is retrieved from the
        cloud object storage(COS).

        :param str location: The location.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `BucketFolder` object
        """
        if not location:
            raise ValueError("location must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "location": location,
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/files"
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    #########################
    # uploadAFile
    #########################

    def upload_file(
        self,
        location: str,
        file_name: str,
        *,
        body: BinaryIO | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Upload/update the file to cloud object storage(COS).

        Upload/update the file to cloud object storage(COS) in the specified project. This
        is inserted into cloud object storage(COS).

        :param str location: The location.
        :param str file_name: The file name.
        :param BinaryIO body: (optional)
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result
        """
        if not location:
            raise ValueError("location must be provided")
        if not file_name:
            raise ValueError("file_name must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "location": location,
            "project_id": project_id,
            "space_id": space_id,
        }

        data = body
        headers["content-type"] = "application/octet-stream"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        path_param_keys = ["file_name"]
        path_param_values = self._encode_path_vars(file_name)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/data_intg_flows/files/{file_name}".format(**path_param_dict)
        return self.send_request(
            method="PUT",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    #########################
    # userLibrary
    #########################

    def get_userlib(
        self,
        project_id: str,
        space_id: str,
        *,
        lib_path: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Get the user library metadata JSON file.

        Download the user library metadata JSON file.

        :param str project_id: The ID of the project to use. `project_id` or
               `space_id` is required.
        :param str space_id: The ID of the space to use. `project_id` or `space_id`
               is required.
        :param str lib_path: (optional) The path to user library.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result
        """
        if not project_id:
            raise ValueError("project_id must be provided")
        if not space_id:
            raise ValueError("space_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "project_id": project_id,
            "space_id": space_id,
            "lib_path": lib_path,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/userlibrary"
        return self.send_request(
            method="GET",
            path=url,
            headers=headers,
            params=params,
        )

    def upload_userlib(
        self,
        project_id: str,
        space_id: str,
        file_name: str,
        *,
        body: BinaryIO | None = None,
        **kwargs,
    ) -> requests.Response:
        """Upload/update a user library file by a given file name.

        Upload/update a user library file by a given file name.

        :param str project_id: The ID of the project to use. `project_id` or
               `space_id` is required.
        :param str space_id: The ID of the space to use. `project_id` or `space_id`
               is required.
        :param str file_name: The file name.
        :param BinaryIO body: (optional)
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result
        """
        if not project_id:
            raise ValueError("project_id must be provided")
        if not space_id:
            raise ValueError("space_id must be provided")
        if not file_name:
            raise ValueError("file_name must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "project_id": project_id,
            "space_id": space_id,
            "file_name": file_name,
        }

        data = body
        headers["content-type"] = "application/octet-stream"

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/userlibrary"
        return self.send_request(
            method="PUT",
            path=url,
            headers=headers,
            params=params,
            data=data,
        )

    def delete_userlib(
        self,
        file_names: list[str],
        *,
        project_id: str | None = None,
        space_id: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Remove the user library by file names.

        Remove the user library by file names.

        :param List[str] file_names: The list of file names to delete.
        :param str project_id: (optional) The ID of the project to use. `space_id`
               or `project_id` is required.
        :param str space_id: (optional) The ID of the space to use. `space_id` or
               `project_id` is required.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `BucketFolder` object
        """
        if file_names is None:
            raise ValueError("file_names must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "file_names": _convert_list(file_names),
            "project_id": project_id,
            "space_id": space_id,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json"

        url = "/data_intg/v3/data_intg_flows/userlibrary"
        return self.send_request(
            method="DELETE",
            path=url,
            headers=headers,
            params=params,
        )

    #########################
    # watsonPipelines
    #########################

    def compile_watson_pipeline(
        self,
        pipeline_id: str,
        *,
        catalog_id: str | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        enable_inline_pipeline: bool | None = None,
        runtime_type: str | None = None,
        job_name_suffix: str | None = None,
        **kwargs,
    ) -> requests.Response:
        """Compile Watson pipeline to generate runtime code.

        Generate Runtime code for a Watson pipeline in the specified project or catalog
        for a specified runtime type. Either project_id or catalog_id must be specified.

        :param str pipeline_id: The Watson Pipeline ID to use.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param bool enable_inline_pipeline: (optional) Whether to enable inline
               pipeline execution or not. When this flag is set to true, no individual job
               runs will be created for nested pipelines. The flag is set to false by
               default.
        :param str runtime_type: (optional) The type of the runtime to use. e.g.
               dspxosh or Spark etc. If not provided queried from within pipeline flow if
               available otherwise default of dspxosh is used.
        :param str job_name_suffix: (optional) The name suffix for the created job,
               will use the pipeline name suffix configured in datastage project settings.
        :param dict headers: A `dict` containing the request headers
        :return: A `Response` containing the result, headers and HTTP status code.
        :rtype: Response with `dict` result representing a `FlowCompileResponse` object
        """
        if not pipeline_id:
            raise ValueError("pipeline_id must be provided")
        headers = {}
        sdk_headers = {"agentname": "watsonx-di-sdk"}
        headers.update(sdk_headers)

        params = {
            "catalog_id": catalog_id,
            "project_id": project_id,
            "space_id": space_id,
            "enable_inline_pipeline": enable_inline_pipeline,
            "runtime_type": runtime_type,
            "job_name_suffix": job_name_suffix,
        }

        if "headers" in kwargs:
            headers.update(kwargs.get("headers"))
            del kwargs["headers"]
        headers["Accept"] = "application/json;charset=utf-8"

        path_param_keys = ["pipeline_id"]
        path_param_values = self._encode_path_vars(pipeline_id)
        path_param_dict = dict(zip(path_param_keys, path_param_values))
        url = "/data_intg/v3/ds_codegen/pipeline/compile/{pipeline_id}".format(**path_param_dict)
        return self.send_request(
            method="POST",
            path=url,
            headers=headers,
            params=params,
        )

    def enable_retries(self):
        pass

    def disable_retries(self):
        pass


##############################################################################
# Models
##############################################################################


class AssetEntityROV:
    """The rules of visibility for an asset.

    :param int mode: (optional) The values for mode are 0 (public, searchable and
          viewable by all), 8 (private, searchable by all, but not viewable unless view
          permission given) or 16 (hidden, only searchable by users with view
          permissions).
    :param List[str] members: (optional) An array of members belonging to
          AssetEntityROV.
    """

    def __init__(
        self,
        *,
        mode: int | None = None,
        members: list[str] | None = None,
    ) -> None:
        """Initialize a AssetEntityROV object.

        :param int mode: (optional) The values for mode are 0 (public, searchable
               and viewable by all), 8 (private, searchable by all, but not viewable
               unless view permission given) or 16 (hidden, only searchable by users with
               view permissions).
        :param List[str] members: (optional) An array of members belonging to
               AssetEntityROV.
        """
        self.mode = mode
        self.members = members

    @classmethod
    def from_dict(cls, _dict: dict) -> "AssetEntityROV":
        """Initialize a AssetEntityROV object from a json dictionary."""
        args = {}
        if (mode := _dict.get("mode")) is not None:
            args["mode"] = mode
        if (members := _dict.get("members")) is not None:
            args["members"] = members
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AssetEntityROV object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "mode") and self.mode is not None:
            _dict["mode"] = self.mode
        if hasattr(self, "members") and self.members is not None:
            _dict["members"] = self.members
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AssetEntityROV object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "AssetEntityROV") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "AssetEntityROV") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class AssetSystemMetadata:
    """System metadata about an asset.

    :param str asset_id: (optional) The ID of the asset.
    :param str asset_type: (optional) The type of the asset.
    :param str catalog_id: (optional) The ID of the catalog which contains the
          asset. `catalog_id` or `project_id` or 'space_id` is required.
    :param datetime create_time: (optional) The timestamp when the asset was created
          (in format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ, matching the
          date-time format as specified by RFC 3339).
    :param str creator_id: (optional) The IAM ID of the user that created the asset.
    :param str href: (optional) URL that can be used to get the asset.
    :param str name: (optional) name of the asset.
    :param str origin_country: (optional) origin of the asset.
    :param int size: (optional) size of the asset.
    :param str project_id: (optional) The ID of the project which contains the
          asset. `catalog_id` or `project_id` or 'space_id` is required.
    :param str space_id: (optional) The ID of the space which contains the asset.
          `catalog_id` or `project_id` or 'space_id` is required.
    :param str resource_key: (optional) This is a unique string that uniquely
          identifies an asset.
    :param str description: (optional) The description of the asset.
    :param List[str] tags: (optional) A list of tags that can be used to identify
          different types of data flow.
    :param dict source_system: (optional) Custom data to be associated with a given
          object.
    :param dict usage: (optional) Metadata usage information about an asset.
    """

    def __init__(
        self,
        *,
        asset_id: str | None = None,
        asset_type: str | None = None,
        catalog_id: str | None = None,
        create_time: datetime | None = None,
        creator_id: str | None = None,
        href: str | None = None,
        name: str | None = None,
        origin_country: str | None = None,
        size: int | None = None,
        project_id: str | None = None,
        space_id: str | None = None,
        resource_key: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        source_system: dict | None = None,
        usage: dict | None = None,
    ) -> None:
        """Initialize a AssetSystemMetadata object.

        :param str asset_id: (optional) The ID of the asset.
        :param str asset_type: (optional) The type of the asset.
        :param str catalog_id: (optional) The ID of the catalog which contains the
               asset. `catalog_id` or `project_id` or 'space_id` is required.
        :param datetime create_time: (optional) The timestamp when the asset was
               created (in format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ,
               matching the date-time format as specified by RFC 3339).
        :param str creator_id: (optional) The IAM ID of the user that created the
               asset.
        :param str href: (optional) URL that can be used to get the asset.
        :param str name: (optional) name of the asset.
        :param str origin_country: (optional) origin of the asset.
        :param int size: (optional) size of the asset.
        :param str project_id: (optional) The ID of the project which contains the
               asset. `catalog_id` or `project_id` or 'space_id` is required.
        :param str space_id: (optional) The ID of the space which contains the
               asset. `catalog_id` or `project_id` or 'space_id` is required.
        :param str resource_key: (optional) This is a unique string that uniquely
               identifies an asset.
        :param str description: (optional) The description of the asset.
        :param List[str] tags: (optional) A list of tags that can be used to
               identify different types of data flow.
        :param dict source_system: (optional) Custom data to be associated with a
               given object.
        :param dict usage: (optional) Metadata usage information about an asset.
        """
        self.asset_id = asset_id
        self.asset_type = asset_type
        self.catalog_id = catalog_id
        self.create_time = create_time
        self.creator_id = creator_id
        self.href = href
        self.name = name
        self.origin_country = origin_country
        self.size = size
        self.project_id = project_id
        self.space_id = space_id
        self.resource_key = resource_key
        self.description = description
        self.tags = tags
        self.source_system = source_system
        self.usage = usage

    @classmethod
    def from_dict(cls, _dict: dict) -> "AssetSystemMetadata":
        """Initialize a AssetSystemMetadata object from a json dictionary."""
        args = {}
        if (asset_id := _dict.get("asset_id")) is not None:
            args["asset_id"] = asset_id
        if (asset_type := _dict.get("asset_type")) is not None:
            args["asset_type"] = asset_type
        if (catalog_id := _dict.get("catalog_id")) is not None:
            args["catalog_id"] = catalog_id
        if (create_time := _dict.get("create_time")) is not None:
            args["create_time"] = _string_to_datetime(create_time)
        if (creator_id := _dict.get("creator_id")) is not None:
            args["creator_id"] = creator_id
        if (href := _dict.get("href")) is not None:
            args["href"] = href
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        if (origin_country := _dict.get("origin_country")) is not None:
            args["origin_country"] = origin_country
        if (size := _dict.get("size")) is not None:
            args["size"] = size
        if (project_id := _dict.get("project_id")) is not None:
            args["project_id"] = project_id
        if (space_id := _dict.get("space_id")) is not None:
            args["space_id"] = space_id
        if (resource_key := _dict.get("resource_key")) is not None:
            args["resource_key"] = resource_key
        if (description := _dict.get("description")) is not None:
            args["description"] = description
        if (tags := _dict.get("tags")) is not None:
            args["tags"] = tags
        if (source_system := _dict.get("source_system")) is not None:
            args["source_system"] = source_system
        if (usage := _dict.get("usage")) is not None:
            args["usage"] = usage
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AssetSystemMetadata object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "asset_id") and self.asset_id is not None:
            _dict["asset_id"] = self.asset_id
        if hasattr(self, "asset_type") and self.asset_type is not None:
            _dict["asset_type"] = self.asset_type
        if hasattr(self, "catalog_id") and self.catalog_id is not None:
            _dict["catalog_id"] = self.catalog_id
        if hasattr(self, "create_time") and self.create_time is not None:
            _dict["create_time"] = _datetime_to_string(self.create_time)
        if hasattr(self, "creator_id") and self.creator_id is not None:
            _dict["creator_id"] = self.creator_id
        if hasattr(self, "href") and self.href is not None:
            _dict["href"] = self.href
        if hasattr(self, "name") and self.name is not None:
            _dict["name"] = self.name
        if hasattr(self, "origin_country") and self.origin_country is not None:
            _dict["origin_country"] = self.origin_country
        if hasattr(self, "size") and self.size is not None:
            _dict["size"] = self.size
        if hasattr(self, "project_id") and self.project_id is not None:
            _dict["project_id"] = self.project_id
        if hasattr(self, "space_id") and self.space_id is not None:
            _dict["space_id"] = self.space_id
        if hasattr(self, "resource_key") and self.resource_key is not None:
            _dict["resource_key"] = self.resource_key
        if hasattr(self, "description") and self.description is not None:
            _dict["description"] = self.description
        if hasattr(self, "tags") and self.tags is not None:
            _dict["tags"] = self.tags
        if hasattr(self, "source_system") and self.source_system is not None:
            _dict["source_system"] = self.source_system
        if hasattr(self, "usage") and self.usage is not None:
            _dict["usage"] = self.usage
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AssetSystemMetadata object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "AssetSystemMetadata") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "AssetSystemMetadata") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BucketFolder:
    """a folder.

    :param str value: (optional)
    :param str type: (optional)
    :param str label: (optional)
    :param bool editable: (optional)
    :param List[BucketFolder] children: (optional)
    :param List[str] files: (optional)
    """

    def __init__(
        self,
        *,
        value: str | None = None,
        type: str | None = None,
        label: str | None = None,
        editable: bool | None = None,
        children: list["BucketFolder"] | None = None,
        files: list[str] | None = None,
    ) -> None:
        """Initialize a BucketFolder object.

        :param str value: (optional)
        :param str type: (optional)
        :param str label: (optional)
        :param bool editable: (optional)
        :param List[BucketFolder] children: (optional)
        :param List[str] files: (optional)
        """
        self.value = value
        self.type = type
        self.label = label
        self.editable = editable
        self.children = children
        self.files = files

    @classmethod
    def from_dict(cls, _dict: dict) -> "BucketFolder":
        """Initialize a BucketFolder object from a json dictionary."""
        args = {}
        if (value := _dict.get("value")) is not None:
            args["value"] = value
        if (type := _dict.get("type")) is not None:
            args["type"] = type
        if (label := _dict.get("label")) is not None:
            args["label"] = label
        if (editable := _dict.get("editable")) is not None:
            args["editable"] = editable
        if (children := _dict.get("children")) is not None:
            args["children"] = [BucketFolder.from_dict(v) for v in children]
        if (files := _dict.get("files")) is not None:
            args["files"] = files
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BucketFolder object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "value") and self.value is not None:
            _dict["value"] = self.value
        if hasattr(self, "type") and self.type is not None:
            _dict["type"] = self.type
        if hasattr(self, "label") and self.label is not None:
            _dict["label"] = self.label
        if hasattr(self, "editable") and self.editable is not None:
            _dict["editable"] = self.editable
        if hasattr(self, "children") and self.children is not None:
            children_list = []
            for v in self.children:
                if isinstance(v, dict):
                    children_list.append(v)
                else:
                    children_list.append(v.to_dict())
            _dict["children"] = children_list
        if hasattr(self, "files") and self.files is not None:
            _dict["files"] = self.files
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BucketFolder object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BucketFolder") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BucketFolder") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopBuild:
    """Build info.

    :param BuildopBuildInterfaces interfaces: (optional)
    :param BuildopBuildLogic logic: (optional) Operator business logic.
    """

    def __init__(
        self,
        *,
        interfaces: Optional["BuildopBuildInterfaces"] = None,
        logic: Optional["BuildopBuildLogic"] = None,
    ) -> None:
        """Initialize a BuildopBuild object.

        :param BuildopBuildInterfaces interfaces: (optional)
        :param BuildopBuildLogic logic: (optional) Operator business logic.
        """
        self.interfaces = interfaces
        self.logic = logic

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopBuild":
        """Initialize a BuildopBuild object from a json dictionary."""
        args = {}
        if (interfaces := _dict.get("interfaces")) is not None:
            args["interfaces"] = BuildopBuildInterfaces.from_dict(interfaces)
        if (logic := _dict.get("logic")) is not None:
            args["logic"] = BuildopBuildLogic.from_dict(logic)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopBuild object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "interfaces") and self.interfaces is not None:
            if isinstance(self.interfaces, dict):
                _dict["interfaces"] = self.interfaces
            else:
                _dict["interfaces"] = self.interfaces.to_dict()
        if hasattr(self, "logic") and self.logic is not None:
            if isinstance(self.logic, dict):
                _dict["logic"] = self.logic
            else:
                _dict["logic"] = self.logic.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopBuild object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopBuild") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopBuild") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopBuildInterfaces:
    """BuildopBuildInterfaces.

    :param List[BuildopBuildInterfacesInputItem] input: (optional) Input port.
    :param List[BuildopBuildInterfacesOutputItem] output: (optional) Output port.
    :param List[BuildopBuildInterfacesTransferItem] transfer: (optional)
          input-output column mapping.
    :param str inputs_order: (optional) Inputs-Order.
    :param str outputs_order: (optional) Outputs-Order.
    """

    def __init__(
        self,
        *,
        input: list["BuildopBuildInterfacesInputItem"] | None = None,
        output: list["BuildopBuildInterfacesOutputItem"] | None = None,
        transfer: list["BuildopBuildInterfacesTransferItem"] | None = None,
        inputs_order: str | None = None,
        outputs_order: str | None = None,
    ) -> None:
        """Initialize a BuildopBuildInterfaces object.

        :param List[BuildopBuildInterfacesInputItem] input: (optional) Input port.
        :param List[BuildopBuildInterfacesOutputItem] output: (optional) Output
               port.
        :param List[BuildopBuildInterfacesTransferItem] transfer: (optional)
               input-output column mapping.
        :param str inputs_order: (optional) Inputs-Order.
        :param str outputs_order: (optional) Outputs-Order.
        """
        self.input = input
        self.output = output
        self.transfer = transfer
        self.inputs_order = inputs_order
        self.outputs_order = outputs_order

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopBuildInterfaces":
        """Initialize a BuildopBuildInterfaces object from a json dictionary."""
        args = {}
        if (input := _dict.get("input")) is not None:
            args["input"] = [BuildopBuildInterfacesInputItem.from_dict(v) for v in input]
        if (output := _dict.get("output")) is not None:
            args["output"] = [BuildopBuildInterfacesOutputItem.from_dict(v) for v in output]
        if (transfer := _dict.get("transfer")) is not None:
            args["transfer"] = [BuildopBuildInterfacesTransferItem.from_dict(v) for v in transfer]
        if (inputs_order := _dict.get("inputs_order")) is not None:
            args["inputs_order"] = inputs_order
        if (outputs_order := _dict.get("outputs_order")) is not None:
            args["outputs_order"] = outputs_order
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopBuildInterfaces object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "input") and self.input is not None:
            input_list = []
            for v in self.input:
                if isinstance(v, dict):
                    input_list.append(v)
                else:
                    input_list.append(v.to_dict())
            _dict["input"] = input_list
        if hasattr(self, "output") and self.output is not None:
            output_list = []
            for v in self.output:
                if isinstance(v, dict):
                    output_list.append(v)
                else:
                    output_list.append(v.to_dict())
            _dict["output"] = output_list
        if hasattr(self, "transfer") and self.transfer is not None:
            transfer_list = []
            for v in self.transfer:
                if isinstance(v, dict):
                    transfer_list.append(v)
                else:
                    transfer_list.append(v.to_dict())
            _dict["transfer"] = transfer_list
        if hasattr(self, "inputs_order") and self.inputs_order is not None:
            _dict["inputs_order"] = self.inputs_order
        if hasattr(self, "outputs_order") and self.outputs_order is not None:
            _dict["outputs_order"] = self.outputs_order
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopBuildInterfaces object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopBuildInterfaces") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopBuildInterfaces") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopBuildInterfacesInputItem:
    """BuildopBuildInterfacesInputItem.

    :param str port_name: (optional) Name of input port.
    :param str alias: (optional) Alias.
    :param bool auto_read: (optional) Auto read.
    :param str table_name: (optional) Table name.
    :param str id: (optional) inputID.
    :param bool runtime_column_propagation: (optional) Runtime column propagation.
    """

    def __init__(
        self,
        *,
        port_name: str | None = None,
        alias: str | None = None,
        auto_read: bool | None = None,
        table_name: str | None = None,
        id: str | None = None,
        runtime_column_propagation: bool | None = None,
    ) -> None:
        """Initialize a BuildopBuildInterfacesInputItem object.

        :param str port_name: (optional) Name of input port.
        :param str alias: (optional) Alias.
        :param bool auto_read: (optional) Auto read.
        :param str table_name: (optional) Table name.
        :param str id: (optional) inputID.
        :param bool runtime_column_propagation: (optional) Runtime column
               propagation.
        """
        self.port_name = port_name
        self.alias = alias
        self.auto_read = auto_read
        self.table_name = table_name
        self.id = id
        self.runtime_column_propagation = runtime_column_propagation

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopBuildInterfacesInputItem":
        """Initialize a BuildopBuildInterfacesInputItem object from a json dictionary."""
        args = {}
        if (port_name := _dict.get("port_name")) is not None:
            args["port_name"] = port_name
        if (alias := _dict.get("alias")) is not None:
            args["alias"] = alias
        if (auto_read := _dict.get("auto_read")) is not None:
            args["auto_read"] = auto_read
        if (table_name := _dict.get("table_name")) is not None:
            args["table_name"] = table_name
        if (id := _dict.get("id")) is not None:
            args["id"] = id
        if (runtime_column_propagation := _dict.get("runtime_column_propagation")) is not None:
            args["runtime_column_propagation"] = runtime_column_propagation
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopBuildInterfacesInputItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "port_name") and self.port_name is not None:
            _dict["port_name"] = self.port_name
        if hasattr(self, "alias") and self.alias is not None:
            _dict["alias"] = self.alias
        if hasattr(self, "auto_read") and self.auto_read is not None:
            _dict["auto_read"] = self.auto_read
        if hasattr(self, "table_name") and self.table_name is not None:
            _dict["table_name"] = self.table_name
        if hasattr(self, "id") and self.id is not None:
            _dict["id"] = self.id
        if hasattr(self, "runtime_column_propagation") and self.runtime_column_propagation is not None:
            _dict["runtime_column_propagation"] = self.runtime_column_propagation
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopBuildInterfacesInputItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopBuildInterfacesInputItem") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopBuildInterfacesInputItem") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopBuildInterfacesOutputItem:
    """BuildopBuildInterfacesOutputItem.

    :param str port_name: (optional) Name of output port.
    :param str alias: (optional) Alias.
    :param bool auto_write: (optional) Auto write.
    :param str table_name: (optional) Table name.
    :param str id: (optional) outputID.
    :param bool runtime_column_propagation: (optional) Runtime column propagation.
    """

    def __init__(
        self,
        *,
        port_name: str | None = None,
        alias: str | None = None,
        auto_write: bool | None = None,
        table_name: str | None = None,
        id: str | None = None,
        runtime_column_propagation: bool | None = None,
    ) -> None:
        """Initialize a BuildopBuildInterfacesOutputItem object.

        :param str port_name: (optional) Name of output port.
        :param str alias: (optional) Alias.
        :param bool auto_write: (optional) Auto write.
        :param str table_name: (optional) Table name.
        :param str id: (optional) outputID.
        :param bool runtime_column_propagation: (optional) Runtime column
               propagation.
        """
        self.port_name = port_name
        self.alias = alias
        self.auto_write = auto_write
        self.table_name = table_name
        self.id = id
        self.runtime_column_propagation = runtime_column_propagation

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopBuildInterfacesOutputItem":
        """Initialize a BuildopBuildInterfacesOutputItem object from a json dictionary."""
        args = {}
        if (port_name := _dict.get("port_name")) is not None:
            args["port_name"] = port_name
        if (alias := _dict.get("alias")) is not None:
            args["alias"] = alias
        if (auto_write := _dict.get("auto_write")) is not None:
            args["auto_write"] = auto_write
        if (table_name := _dict.get("table_name")) is not None:
            args["table_name"] = table_name
        if (id := _dict.get("id")) is not None:
            args["id"] = id
        if (runtime_column_propagation := _dict.get("runtime_column_propagation")) is not None:
            args["runtime_column_propagation"] = runtime_column_propagation
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopBuildInterfacesOutputItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "port_name") and self.port_name is not None:
            _dict["port_name"] = self.port_name
        if hasattr(self, "alias") and self.alias is not None:
            _dict["alias"] = self.alias
        if hasattr(self, "auto_write") and self.auto_write is not None:
            _dict["auto_write"] = self.auto_write
        if hasattr(self, "table_name") and self.table_name is not None:
            _dict["table_name"] = self.table_name
        if hasattr(self, "id") and self.id is not None:
            _dict["id"] = self.id
        if hasattr(self, "runtime_column_propagation") and self.runtime_column_propagation is not None:
            _dict["runtime_column_propagation"] = self.runtime_column_propagation
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopBuildInterfacesOutputItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopBuildInterfacesOutputItem") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopBuildInterfacesOutputItem") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopBuildInterfacesTransferItem:
    """BuildopBuildInterfacesTransferItem.

    :param str input: (optional) Input.
    :param str output: (optional) Output.
    :param bool auto_transfer: (optional) Auto transfer.
    :param bool separate: (optional) Separate.
    """

    def __init__(
        self,
        *,
        input: str | None = None,
        output: str | None = None,
        auto_transfer: bool | None = None,
        separate: bool | None = None,
    ) -> None:
        """Initialize a BuildopBuildInterfacesTransferItem object.

        :param str input: (optional) Input.
        :param str output: (optional) Output.
        :param bool auto_transfer: (optional) Auto transfer.
        :param bool separate: (optional) Separate.
        """
        self.input = input
        self.output = output
        self.auto_transfer = auto_transfer
        self.separate = separate

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopBuildInterfacesTransferItem":
        """Initialize a BuildopBuildInterfacesTransferItem object from a json dictionary."""
        args = {}
        if (input := _dict.get("input")) is not None:
            args["input"] = input
        if (output := _dict.get("output")) is not None:
            args["output"] = output
        if (auto_transfer := _dict.get("auto_transfer")) is not None:
            args["auto_transfer"] = auto_transfer
        if (separate := _dict.get("separate")) is not None:
            args["separate"] = separate
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopBuildInterfacesTransferItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "input") and self.input is not None:
            _dict["input"] = self.input
        if hasattr(self, "output") and self.output is not None:
            _dict["output"] = self.output
        if hasattr(self, "auto_transfer") and self.auto_transfer is not None:
            _dict["auto_transfer"] = self.auto_transfer
        if hasattr(self, "separate") and self.separate is not None:
            _dict["separate"] = self.separate
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopBuildInterfacesTransferItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopBuildInterfacesTransferItem") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopBuildInterfacesTransferItem") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopBuildLogic:
    """Operator business logic.

    :param str definitions: (optional) Definitions.
    :param str pre_loop: (optional) Pre-loop logic.
    :param str per_record: (optional) Logic for each record.
    :param str post_loop: (optional) Post-loop logic.
    """

    def __init__(
        self,
        *,
        definitions: str | None = None,
        pre_loop: str | None = None,
        per_record: str | None = None,
        post_loop: str | None = None,
    ) -> None:
        """Initialize a BuildopBuildLogic object.

        :param str definitions: (optional) Definitions.
        :param str pre_loop: (optional) Pre-loop logic.
        :param str per_record: (optional) Logic for each record.
        :param str post_loop: (optional) Post-loop logic.
        """
        self.definitions = definitions
        self.pre_loop = pre_loop
        self.per_record = per_record
        self.post_loop = post_loop

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopBuildLogic":
        """Initialize a BuildopBuildLogic object from a json dictionary."""
        args = {}
        if (definitions := _dict.get("definitions")) is not None:
            args["definitions"] = definitions
        if (pre_loop := _dict.get("pre_loop")) is not None:
            args["pre_loop"] = pre_loop
        if (per_record := _dict.get("per_record")) is not None:
            args["per_record"] = per_record
        if (post_loop := _dict.get("post_loop")) is not None:
            args["post_loop"] = post_loop
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopBuildLogic object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "definitions") and self.definitions is not None:
            _dict["definitions"] = self.definitions
        if hasattr(self, "pre_loop") and self.pre_loop is not None:
            _dict["pre_loop"] = self.pre_loop
        if hasattr(self, "per_record") and self.per_record is not None:
            _dict["per_record"] = self.per_record
        if hasattr(self, "post_loop") and self.post_loop is not None:
            _dict["post_loop"] = self.post_loop
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopBuildLogic object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopBuildLogic") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopBuildLogic") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopCreator:
    """Creator information.

    :param str vendor: (optional) Vendor name.
    :param str author: (optional) Author name.
    :param str version: (optional) Version.
    """

    def __init__(
        self,
        *,
        vendor: str | None = None,
        author: str | None = None,
        version: str | None = None,
    ) -> None:
        """Initialize a BuildopCreator object.

        :param str vendor: (optional) Vendor name.
        :param str author: (optional) Author name.
        :param str version: (optional) Version.
        """
        self.vendor = vendor
        self.author = author
        self.version = version

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopCreator":
        """Initialize a BuildopCreator object from a json dictionary."""
        args = {}
        if (vendor := _dict.get("vendor")) is not None:
            args["vendor"] = vendor
        if (author := _dict.get("author")) is not None:
            args["author"] = author
        if (version := _dict.get("version")) is not None:
            args["version"] = version
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopCreator object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "vendor") and self.vendor is not None:
            _dict["vendor"] = self.vendor
        if hasattr(self, "author") and self.author is not None:
            _dict["author"] = self.author
        if hasattr(self, "version") and self.version is not None:
            _dict["version"] = self.version
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopCreator object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopCreator") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopCreator") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopGeneral:
    """General information.

    :param str class_name: (optional) Class name.
    :param str operator_name: (optional) Operator name.
    :param str node_type_name: (optional) Node type name.
    :param str wrapped_name: (optional) Wrapped name.
    :param str command: (optional) Command name.
    :param str execmode: (optional) Exec Mode.
    """

    def __init__(
        self,
        *,
        class_name: str | None = None,
        operator_name: str | None = None,
        node_type_name: str | None = None,
        wrapped_name: str | None = None,
        command: str | None = None,
        execmode: str | None = None,
    ) -> None:
        """Initialize a BuildopGeneral object.

        :param str class_name: (optional) Class name.
        :param str operator_name: (optional) Operator name.
        :param str node_type_name: (optional) Node type name.
        :param str wrapped_name: (optional) Wrapped name.
        :param str command: (optional) Command name.
        :param str execmode: (optional) Exec Mode.
        """
        self.class_name = class_name
        self.operator_name = operator_name
        self.node_type_name = node_type_name
        self.wrapped_name = wrapped_name
        self.command = command
        self.execmode = execmode

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopGeneral":
        """Initialize a BuildopGeneral object from a json dictionary."""
        args = {}
        if (class_name := _dict.get("class_name")) is not None:
            args["class_name"] = class_name
        if (operator_name := _dict.get("operator_name")) is not None:
            args["operator_name"] = operator_name
        if (node_type_name := _dict.get("node_type_name")) is not None:
            args["node_type_name"] = node_type_name
        if (wrapped_name := _dict.get("wrapped_name")) is not None:
            args["wrapped_name"] = wrapped_name
        if (command := _dict.get("command")) is not None:
            args["command"] = command
        if (execmode := _dict.get("execmode")) is not None:
            args["execmode"] = execmode
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopGeneral object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "class_name") and self.class_name is not None:
            _dict["class_name"] = self.class_name
        if hasattr(self, "operator_name") and self.operator_name is not None:
            _dict["operator_name"] = self.operator_name
        if hasattr(self, "node_type_name") and self.node_type_name is not None:
            _dict["node_type_name"] = self.node_type_name
        if hasattr(self, "wrapped_name") and self.wrapped_name is not None:
            _dict["wrapped_name"] = self.wrapped_name
        if hasattr(self, "command") and self.command is not None:
            _dict["command"] = self.command
        if hasattr(self, "execmode") and self.execmode is not None:
            _dict["execmode"] = self.execmode
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopGeneral object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopGeneral") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopGeneral") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopPropertiesItem:
    """BuildopPropertiesItem.

    :param str property_name: (optional) Name of property.
    :param str data_type: (optional) Data type.
    :param str prompt: (optional) Prompt.
    :param str default_value: (optional) Default value.
    :param str required: (optional) Required.
    :param str repeats: (optional) Repeats.
    :param str conversion: (optional) Conversion.
    :param str use_quoting: (optional) use Quoting.
    :param str hidden: (optional) hidden.
    :param str category: (optional) Category.
    :param str conditions: (optional) Conditions.
    :param str template: (optional) Template.
    :param str parents: (optional) Parents.
    :param str list_values: (optional) list values.
    :param str description: (optional) Description.
    """

    def __init__(
        self,
        *,
        property_name: str | None = None,
        data_type: str | None = None,
        prompt: str | None = None,
        default_value: str | None = None,
        required: str | None = None,
        repeats: str | None = None,
        conversion: str | None = None,
        use_quoting: str | None = None,
        hidden: str | None = None,
        category: str | None = None,
        conditions: str | None = None,
        template: str | None = None,
        parents: str | None = None,
        list_values: str | None = None,
        description: str | None = None,
    ) -> None:
        """Initialize a BuildopPropertiesItem object.

        :param str property_name: (optional) Name of property.
        :param str data_type: (optional) Data type.
        :param str prompt: (optional) Prompt.
        :param str default_value: (optional) Default value.
        :param str required: (optional) Required.
        :param str repeats: (optional) Repeats.
        :param str conversion: (optional) Conversion.
        :param str use_quoting: (optional) use Quoting.
        :param str hidden: (optional) hidden.
        :param str category: (optional) Category.
        :param str conditions: (optional) Conditions.
        :param str template: (optional) Template.
        :param str parents: (optional) Parents.
        :param str list_values: (optional) list values.
        :param str description: (optional) Description.
        """
        self.property_name = property_name
        self.data_type = data_type
        self.prompt = prompt
        self.default_value = default_value
        self.required = required
        self.repeats = repeats
        self.conversion = conversion
        self.use_quoting = use_quoting
        self.hidden = hidden
        self.category = category
        self.conditions = conditions
        self.template = template
        self.parents = parents
        self.list_values = list_values
        self.description = description

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopPropertiesItem":
        """Initialize a BuildopPropertiesItem object from a json dictionary."""
        args = {}
        if (property_name := _dict.get("property_name")) is not None:
            args["property_name"] = property_name
        if (data_type := _dict.get("data_type")) is not None:
            args["data_type"] = data_type
        if (prompt := _dict.get("prompt")) is not None:
            args["prompt"] = prompt
        if (default_value := _dict.get("default_value")) is not None:
            args["default_value"] = default_value
        if (required := _dict.get("required")) is not None:
            args["required"] = required
        if (repeats := _dict.get("repeats")) is not None:
            args["repeats"] = repeats
        if (conversion := _dict.get("conversion")) is not None:
            args["conversion"] = conversion
        if (use_quoting := _dict.get("use_quoting")) is not None:
            args["use_quoting"] = use_quoting
        if (hidden := _dict.get("hidden")) is not None:
            args["hidden"] = hidden
        if (category := _dict.get("category")) is not None:
            args["category"] = category
        if (conditions := _dict.get("conditions")) is not None:
            args["conditions"] = conditions
        if (template := _dict.get("template")) is not None:
            args["template"] = template
        if (parents := _dict.get("parents")) is not None:
            args["parents"] = parents
        if (list_values := _dict.get("list_values")) is not None:
            args["list_values"] = list_values
        if (description := _dict.get("description")) is not None:
            args["description"] = description
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopPropertiesItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "property_name") and self.property_name is not None:
            _dict["property_name"] = self.property_name
        if hasattr(self, "data_type") and self.data_type is not None:
            _dict["data_type"] = self.data_type
        if hasattr(self, "prompt") and self.prompt is not None:
            _dict["prompt"] = self.prompt
        if hasattr(self, "default_value") and self.default_value is not None:
            _dict["default_value"] = self.default_value
        if hasattr(self, "required") and self.required is not None:
            _dict["required"] = self.required
        if hasattr(self, "repeats") and self.repeats is not None:
            _dict["repeats"] = self.repeats
        if hasattr(self, "conversion") and self.conversion is not None:
            _dict["conversion"] = self.conversion
        if hasattr(self, "use_quoting") and self.use_quoting is not None:
            _dict["use_quoting"] = self.use_quoting
        if hasattr(self, "hidden") and self.hidden is not None:
            _dict["hidden"] = self.hidden
        if hasattr(self, "category") and self.category is not None:
            _dict["category"] = self.category
        if hasattr(self, "conditions") and self.conditions is not None:
            _dict["conditions"] = self.conditions
        if hasattr(self, "template") and self.template is not None:
            _dict["template"] = self.template
        if hasattr(self, "parents") and self.parents is not None:
            _dict["parents"] = self.parents
        if hasattr(self, "list_values") and self.list_values is not None:
            _dict["list_values"] = self.list_values
        if hasattr(self, "description") and self.description is not None:
            _dict["description"] = self.description
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopPropertiesItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopPropertiesItem") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopPropertiesItem") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopWrapped:
    """Wrapped info.

    :param BuildopWrappedInterfaces interfaces: (optional) Interfaces.
    :param BuildopWrappedEnvironment environment: (optional) Environment
          information.
    """

    def __init__(
        self,
        *,
        interfaces: Optional["BuildopWrappedInterfaces"] = None,
        environment: Optional["BuildopWrappedEnvironment"] = None,
    ) -> None:
        """Initialize a BuildopWrapped object.

        :param BuildopWrappedInterfaces interfaces: (optional) Interfaces.
        :param BuildopWrappedEnvironment environment: (optional) Environment
               information.
        """
        self.interfaces = interfaces
        self.environment = environment

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopWrapped":
        """Initialize a BuildopWrapped object from a json dictionary."""
        args = {}
        if (interfaces := _dict.get("interfaces")) is not None:
            args["interfaces"] = BuildopWrappedInterfaces.from_dict(interfaces)
        if (environment := _dict.get("environment")) is not None:
            args["environment"] = BuildopWrappedEnvironment.from_dict(environment)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopWrapped object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "interfaces") and self.interfaces is not None:
            if isinstance(self.interfaces, dict):
                _dict["interfaces"] = self.interfaces
            else:
                _dict["interfaces"] = self.interfaces.to_dict()
        if hasattr(self, "environment") and self.environment is not None:
            if isinstance(self.environment, dict):
                _dict["environment"] = self.environment
            else:
                _dict["environment"] = self.environment.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopWrapped object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopWrapped") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopWrapped") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopWrappedEnvironment:
    """Environment information.

    :param List[BuildopWrappedEnvironmentNameValueItem] name_value: (optional) Each
          element is JSONObject containing name and value.
    :param BuildopWrappedEnvironmentExitCodes exit_codes: (optional) Exit codes.
    """

    def __init__(
        self,
        *,
        name_value: list["BuildopWrappedEnvironmentNameValueItem"] | None = None,
        exit_codes: Optional["BuildopWrappedEnvironmentExitCodes"] = None,
    ) -> None:
        """Initialize a BuildopWrappedEnvironment object.

        :param List[BuildopWrappedEnvironmentNameValueItem] name_value: (optional)
               Each element is JSONObject containing name and value.
        :param BuildopWrappedEnvironmentExitCodes exit_codes: (optional) Exit
               codes.
        """
        self.name_value = name_value
        self.exit_codes = exit_codes

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopWrappedEnvironment":
        """Initialize a BuildopWrappedEnvironment object from a json dictionary."""
        args = {}
        if (name_value := _dict.get("name_value")) is not None:
            args["name_value"] = [BuildopWrappedEnvironmentNameValueItem.from_dict(v) for v in name_value]
        if (exit_codes := _dict.get("exit_codes")) is not None:
            args["exit_codes"] = BuildopWrappedEnvironmentExitCodes.from_dict(exit_codes)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopWrappedEnvironment object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "name_value") and self.name_value is not None:
            name_value_list = []
            for v in self.name_value:
                if isinstance(v, dict):
                    name_value_list.append(v)
                else:
                    name_value_list.append(v.to_dict())
            _dict["name_value"] = name_value_list
        if hasattr(self, "exit_codes") and self.exit_codes is not None:
            if isinstance(self.exit_codes, dict):
                _dict["exit_codes"] = self.exit_codes
            else:
                _dict["exit_codes"] = self.exit_codes.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopWrappedEnvironment object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopWrappedEnvironment") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopWrappedEnvironment") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopWrappedEnvironmentExitCodes:
    """Exit codes.

    :param bool all_exit_codes_successful: (optional) All exit codes successful.
    :param List[str] success_codes: (optional)
    :param List[str] failure_codes: (optional)
    """

    def __init__(
        self,
        *,
        all_exit_codes_successful: bool | None = None,
        success_codes: list[str] | None = None,
        failure_codes: list[str] | None = None,
    ) -> None:
        """Initialize a BuildopWrappedEnvironmentExitCodes object.

        :param bool all_exit_codes_successful: (optional) All exit codes
               successful.
        :param List[str] success_codes: (optional)
        :param List[str] failure_codes: (optional)
        """
        self.all_exit_codes_successful = all_exit_codes_successful
        self.success_codes = success_codes
        self.failure_codes = failure_codes

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopWrappedEnvironmentExitCodes":
        """Initialize a BuildopWrappedEnvironmentExitCodes object from a json dictionary."""
        args = {}
        if (all_exit_codes_successful := _dict.get("all_exit_codes_successful")) is not None:
            args["all_exit_codes_successful"] = all_exit_codes_successful
        if (success_codes := _dict.get("success_codes")) is not None:
            args["success_codes"] = success_codes
        if (failure_codes := _dict.get("failure_codes")) is not None:
            args["failure_codes"] = failure_codes
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopWrappedEnvironmentExitCodes object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "all_exit_codes_successful") and self.all_exit_codes_successful is not None:
            _dict["all_exit_codes_successful"] = self.all_exit_codes_successful
        if hasattr(self, "success_codes") and self.success_codes is not None:
            _dict["success_codes"] = self.success_codes
        if hasattr(self, "failure_codes") and self.failure_codes is not None:
            _dict["failure_codes"] = self.failure_codes
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopWrappedEnvironmentExitCodes object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopWrappedEnvironmentExitCodes") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopWrappedEnvironmentExitCodes") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopWrappedEnvironmentNameValueItem:
    """BuildopWrappedEnvironmentNameValueItem.

    :param str name: (optional) Environment Name.
    :param str value: (optional) Environment Value.
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        value: str | None = None,
    ) -> None:
        """Initialize a BuildopWrappedEnvironmentNameValueItem object.

        :param str name: (optional) Environment Name.
        :param str value: (optional) Environment Value.
        """
        self.name = name
        self.value = value

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopWrappedEnvironmentNameValueItem":
        """Initialize a BuildopWrappedEnvironmentNameValueItem object from a json dictionary."""
        args = {}
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        if (value := _dict.get("value")) is not None:
            args["value"] = value
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopWrappedEnvironmentNameValueItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "name") and self.name is not None:
            _dict["name"] = self.name
        if hasattr(self, "value") and self.value is not None:
            _dict["value"] = self.value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopWrappedEnvironmentNameValueItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopWrappedEnvironmentNameValueItem") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopWrappedEnvironmentNameValueItem") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopWrappedInterfaces:
    """Interfaces.

    :param List[BuildopWrappedInterfacesInputItem] input: (optional) Input link.
    :param List[BuildopWrappedInterfacesOutputItem] output: (optional) Output link.
    :param str inputs_order: (optional) Inputs-Order.
    :param str outputs_order: (optional) Outputs-Order.
    """

    def __init__(
        self,
        *,
        input: list["BuildopWrappedInterfacesInputItem"] | None = None,
        output: list["BuildopWrappedInterfacesOutputItem"] | None = None,
        inputs_order: str | None = None,
        outputs_order: str | None = None,
    ) -> None:
        """Initialize a BuildopWrappedInterfaces object.

        :param List[BuildopWrappedInterfacesInputItem] input: (optional) Input
               link.
        :param List[BuildopWrappedInterfacesOutputItem] output: (optional) Output
               link.
        :param str inputs_order: (optional) Inputs-Order.
        :param str outputs_order: (optional) Outputs-Order.
        """
        self.input = input
        self.output = output
        self.inputs_order = inputs_order
        self.outputs_order = outputs_order

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopWrappedInterfaces":
        """Initialize a BuildopWrappedInterfaces object from a json dictionary."""
        args = {}
        if (input := _dict.get("input")) is not None:
            args["input"] = [BuildopWrappedInterfacesInputItem.from_dict(v) for v in input]
        if (output := _dict.get("output")) is not None:
            args["output"] = [BuildopWrappedInterfacesOutputItem.from_dict(v) for v in output]
        if (inputs_order := _dict.get("inputs_order")) is not None:
            args["inputs_order"] = inputs_order
        if (outputs_order := _dict.get("outputs_order")) is not None:
            args["outputs_order"] = outputs_order
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopWrappedInterfaces object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "input") and self.input is not None:
            input_list = []
            for v in self.input:
                if isinstance(v, dict):
                    input_list.append(v)
                else:
                    input_list.append(v.to_dict())
            _dict["input"] = input_list
        if hasattr(self, "output") and self.output is not None:
            output_list = []
            for v in self.output:
                if isinstance(v, dict):
                    output_list.append(v)
                else:
                    output_list.append(v.to_dict())
            _dict["output"] = output_list
        if hasattr(self, "inputs_order") and self.inputs_order is not None:
            _dict["inputs_order"] = self.inputs_order
        if hasattr(self, "outputs_order") and self.outputs_order is not None:
            _dict["outputs_order"] = self.outputs_order
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopWrappedInterfaces object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopWrappedInterfaces") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopWrappedInterfaces") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopWrappedInterfacesInputItem:
    """BuildopWrappedInterfacesInputItem.

    :param str link_name: (optional) Name of input link.
    :param str table_name: (optional) Table name.
    :param bool use_stream: (optional) Use stream or not.
    :param str file_descriptor: (optional) File descriptor.
    :param bool is_command_line: (optional) Is command line argument or environment
          variable.
    :param str argument_variable_name: (optional) Command line argument or
          Environment variable name.
    :param str named_pipe: (optional) Named pipe.
    :param str id: (optional) inputID.
    """

    def __init__(
        self,
        *,
        link_name: str | None = None,
        table_name: str | None = None,
        use_stream: bool | None = None,
        file_descriptor: str | None = None,
        is_command_line: bool | None = None,
        argument_variable_name: str | None = None,
        named_pipe: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize a BuildopWrappedInterfacesInputItem object.

        :param str link_name: (optional) Name of input link.
        :param str table_name: (optional) Table name.
        :param bool use_stream: (optional) Use stream or not.
        :param str file_descriptor: (optional) File descriptor.
        :param bool is_command_line: (optional) Is command line argument or
               environment variable.
        :param str argument_variable_name: (optional) Command line argument or
               Environment variable name.
        :param str named_pipe: (optional) Named pipe.
        :param str id: (optional) inputID.
        """
        self.link_name = link_name
        self.table_name = table_name
        self.use_stream = use_stream
        self.file_descriptor = file_descriptor
        self.is_command_line = is_command_line
        self.argument_variable_name = argument_variable_name
        self.named_pipe = named_pipe
        self.id = id

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopWrappedInterfacesInputItem":
        """Initialize a BuildopWrappedInterfacesInputItem object from a json dictionary."""
        args = {}
        if (link_name := _dict.get("link_name")) is not None:
            args["link_name"] = link_name
        if (table_name := _dict.get("table_name")) is not None:
            args["table_name"] = table_name
        if (use_stream := _dict.get("use_stream")) is not None:
            args["use_stream"] = use_stream
        if (file_descriptor := _dict.get("file_descriptor")) is not None:
            args["file_descriptor"] = file_descriptor
        if (is_command_line := _dict.get("is_command_line")) is not None:
            args["is_command_line"] = is_command_line
        if (argument_variable_name := _dict.get("argument_variable_name")) is not None:
            args["argument_variable_name"] = argument_variable_name
        if (named_pipe := _dict.get("named_pipe")) is not None:
            args["named_pipe"] = named_pipe
        if (id := _dict.get("id")) is not None:
            args["id"] = id
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopWrappedInterfacesInputItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "link_name") and self.link_name is not None:
            _dict["link_name"] = self.link_name
        if hasattr(self, "table_name") and self.table_name is not None:
            _dict["table_name"] = self.table_name
        if hasattr(self, "use_stream") and self.use_stream is not None:
            _dict["use_stream"] = self.use_stream
        if hasattr(self, "file_descriptor") and self.file_descriptor is not None:
            _dict["file_descriptor"] = self.file_descriptor
        if hasattr(self, "is_command_line") and self.is_command_line is not None:
            _dict["is_command_line"] = self.is_command_line
        if hasattr(self, "argument_variable_name") and self.argument_variable_name is not None:
            _dict["argument_variable_name"] = self.argument_variable_name
        if hasattr(self, "named_pipe") and self.named_pipe is not None:
            _dict["named_pipe"] = self.named_pipe
        if hasattr(self, "id") and self.id is not None:
            _dict["id"] = self.id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopWrappedInterfacesInputItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopWrappedInterfacesInputItem") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopWrappedInterfacesInputItem") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class BuildopWrappedInterfacesOutputItem:
    """BuildopWrappedInterfacesOutputItem.

    :param str link_name: (optional) Name of output link.
    :param str table_name: (optional) Table name.
    :param bool use_stream: (optional) Use stream or not.
    :param str file_descriptor: (optional) File descriptor.
    :param bool is_command_line: (optional) Is command line argument or environment
          variable.
    :param str argument_variable_name: (optional) Command line argument or
          Environment variable name.
    :param str named_pipe: (optional) Named pipe.
    :param str id: (optional) outputID.
    """

    def __init__(
        self,
        *,
        link_name: str | None = None,
        table_name: str | None = None,
        use_stream: bool | None = None,
        file_descriptor: str | None = None,
        is_command_line: bool | None = None,
        argument_variable_name: str | None = None,
        named_pipe: str | None = None,
        id: str | None = None,
    ) -> None:
        """Initialize a BuildopWrappedInterfacesOutputItem object.

        :param str link_name: (optional) Name of output link.
        :param str table_name: (optional) Table name.
        :param bool use_stream: (optional) Use stream or not.
        :param str file_descriptor: (optional) File descriptor.
        :param bool is_command_line: (optional) Is command line argument or
               environment variable.
        :param str argument_variable_name: (optional) Command line argument or
               Environment variable name.
        :param str named_pipe: (optional) Named pipe.
        :param str id: (optional) outputID.
        """
        self.link_name = link_name
        self.table_name = table_name
        self.use_stream = use_stream
        self.file_descriptor = file_descriptor
        self.is_command_line = is_command_line
        self.argument_variable_name = argument_variable_name
        self.named_pipe = named_pipe
        self.id = id

    @classmethod
    def from_dict(cls, _dict: dict) -> "BuildopWrappedInterfacesOutputItem":
        """Initialize a BuildopWrappedInterfacesOutputItem object from a json dictionary."""
        args = {}
        if (link_name := _dict.get("link_name")) is not None:
            args["link_name"] = link_name
        if (table_name := _dict.get("table_name")) is not None:
            args["table_name"] = table_name
        if (use_stream := _dict.get("use_stream")) is not None:
            args["use_stream"] = use_stream
        if (file_descriptor := _dict.get("file_descriptor")) is not None:
            args["file_descriptor"] = file_descriptor
        if (is_command_line := _dict.get("is_command_line")) is not None:
            args["is_command_line"] = is_command_line
        if (argument_variable_name := _dict.get("argument_variable_name")) is not None:
            args["argument_variable_name"] = argument_variable_name
        if (named_pipe := _dict.get("named_pipe")) is not None:
            args["named_pipe"] = named_pipe
        if (id := _dict.get("id")) is not None:
            args["id"] = id
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a BuildopWrappedInterfacesOutputItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "link_name") and self.link_name is not None:
            _dict["link_name"] = self.link_name
        if hasattr(self, "table_name") and self.table_name is not None:
            _dict["table_name"] = self.table_name
        if hasattr(self, "use_stream") and self.use_stream is not None:
            _dict["use_stream"] = self.use_stream
        if hasattr(self, "file_descriptor") and self.file_descriptor is not None:
            _dict["file_descriptor"] = self.file_descriptor
        if hasattr(self, "is_command_line") and self.is_command_line is not None:
            _dict["is_command_line"] = self.is_command_line
        if hasattr(self, "argument_variable_name") and self.argument_variable_name is not None:
            _dict["argument_variable_name"] = self.argument_variable_name
        if hasattr(self, "named_pipe") and self.named_pipe is not None:
            _dict["named_pipe"] = self.named_pipe
        if hasattr(self, "id") and self.id is not None:
            _dict["id"] = self.id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this BuildopWrappedInterfacesOutputItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "BuildopWrappedInterfacesOutputItem") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "BuildopWrappedInterfacesOutputItem") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataFlowPagedCollection:
    """A page from a collection of DataStage flows.

    :param List[DataIntgFlow] data_flows: (optional) A page from a collection of
          DataStage flows.
    :param HrefModel first: (optional) URI of a resource.
    :param HrefModel prev: (optional) URI of a resource.
    :param HrefModel next: (optional) URI of a resource.
    :param HrefModel last: (optional) URI of a resource.
    :param int limit: (optional) The number of data flows requested to be returned.
    :param int total_count: (optional) The total number of DataStage flows
          available.
    """

    def __init__(
        self,
        *,
        data_flows: list["DataIntgFlow"] | None = None,
        first: Optional["HrefModel"] = None,
        prev: Optional["HrefModel"] = None,
        next: Optional["HrefModel"] = None,
        last: Optional["HrefModel"] = None,
        limit: int | None = None,
        total_count: int | None = None,
    ) -> None:
        """Initialize a DataFlowPagedCollection object.

        :param List[DataIntgFlow] data_flows: (optional) A page from a collection
               of DataStage flows.
        :param HrefModel first: (optional) URI of a resource.
        :param HrefModel prev: (optional) URI of a resource.
        :param HrefModel next: (optional) URI of a resource.
        :param HrefModel last: (optional) URI of a resource.
        :param int limit: (optional) The number of data flows requested to be
               returned.
        :param int total_count: (optional) The total number of DataStage flows
               available.
        """
        self.data_flows = data_flows
        self.first = first
        self.prev = prev
        self.next = next
        self.last = last
        self.limit = limit
        self.total_count = total_count

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataFlowPagedCollection":
        """Initialize a DataFlowPagedCollection object from a json dictionary."""
        args = {}
        if (data_flows := _dict.get("data_flows")) is not None:
            args["data_flows"] = [DataIntgFlow.from_dict(v) for v in data_flows]
        if (first := _dict.get("first")) is not None:
            args["first"] = HrefModel.from_dict(first)
        if (prev := _dict.get("prev")) is not None:
            args["prev"] = HrefModel.from_dict(prev)
        if (next := _dict.get("next")) is not None:
            args["next"] = HrefModel.from_dict(next)
        if (last := _dict.get("last")) is not None:
            args["last"] = HrefModel.from_dict(last)
        if (limit := _dict.get("limit")) is not None:
            args["limit"] = limit
        if (total_count := _dict.get("total_count")) is not None:
            args["total_count"] = total_count
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataFlowPagedCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "data_flows") and self.data_flows is not None:
            data_flows_list = []
            for v in self.data_flows:
                if isinstance(v, dict):
                    data_flows_list.append(v)
                else:
                    data_flows_list.append(v.to_dict())
            _dict["data_flows"] = data_flows_list
        if hasattr(self, "first") and self.first is not None:
            if isinstance(self.first, dict):
                _dict["first"] = self.first
            else:
                _dict["first"] = self.first.to_dict()
        if hasattr(self, "prev") and self.prev is not None:
            if isinstance(self.prev, dict):
                _dict["prev"] = self.prev
            else:
                _dict["prev"] = self.prev.to_dict()
        if hasattr(self, "next") and self.next is not None:
            if isinstance(self.next, dict):
                _dict["next"] = self.next
            else:
                _dict["next"] = self.next.to_dict()
        if hasattr(self, "last") and self.last is not None:
            if isinstance(self.last, dict):
                _dict["last"] = self.last
            else:
                _dict["last"] = self.last.to_dict()
        if hasattr(self, "limit") and self.limit is not None:
            _dict["limit"] = self.limit
        if hasattr(self, "total_count") and self.total_count is not None:
            _dict["total_count"] = self.total_count
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataFlowPagedCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataFlowPagedCollection") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataFlowPagedCollection") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlow:
    """A DataStage flow model that defines physical source(s), physical target(s) and an
    optional pipeline containing operations to apply to source(s).

    :param AssetSystemMetadata metadata: (optional) System metadata about an asset.
    :param DataIntgFlowEntity entity: (optional) The underlying DataStage flow
          definition.
    :param List[dict] attachments: (optional) Metadata information for datastage
          flow.
    """

    def __init__(
        self,
        *,
        metadata: Optional["AssetSystemMetadata"] = None,
        entity: Optional["DataIntgFlowEntity"] = None,
        attachments: list[dict] | None = None,
    ) -> None:
        """Initialize a DataIntgFlow object.

        :param AssetSystemMetadata metadata: (optional) System metadata about an
               asset.
        :param DataIntgFlowEntity entity: (optional) The underlying DataStage flow
               definition.
        :param List[dict] attachments: (optional) Metadata information for
               datastage flow.
        """
        self.metadata = metadata
        self.entity = entity
        self.attachments = attachments

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlow":
        """Initialize a DataIntgFlow object from a json dictionary."""
        args = {}
        if (metadata := _dict.get("metadata")) is not None:
            args["metadata"] = AssetSystemMetadata.from_dict(metadata)
        if (entity := _dict.get("entity")) is not None:
            args["entity"] = DataIntgFlowEntity.from_dict(entity)
        if (attachments := _dict.get("attachments")) is not None:
            args["attachments"] = attachments
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlow object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "metadata") and self.metadata is not None:
            if isinstance(self.metadata, dict):
                _dict["metadata"] = self.metadata
            else:
                _dict["metadata"] = self.metadata.to_dict()
        if hasattr(self, "entity") and self.entity is not None:
            if isinstance(self.entity, dict):
                _dict["entity"] = self.entity
            else:
                _dict["entity"] = self.entity.to_dict()
        if hasattr(self, "attachments") and self.attachments is not None:
            _dict["attachments"] = self.attachments
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlow object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlow") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlow") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowAssetParameter:
    """The parameter definition.

    :param str name: (optional) The name of the parameter.
    :param str description: (optional) The description of the parameter.
    :param str prompt: (optional) The prompt of the parameter.
    :param str type: (optional) The parameter type.
    :param str subtype: (optional) The parameter subtype.
    :param dict value: (optional) The literal default value to replace at runtime.
    :param List[dict] valid_values: (optional) The valid values of the parameter.
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        prompt: str | None = None,
        type: str | None = None,
        subtype: str | None = None,
        value: dict | None = None,
        valid_values: list[dict] | None = None,
    ) -> None:
        """Initialize a DataIntgFlowAssetParameter object.

        :param str name: (optional) The name of the parameter.
        :param str description: (optional) The description of the parameter.
        :param str prompt: (optional) The prompt of the parameter.
        :param str type: (optional) The parameter type.
        :param str subtype: (optional) The parameter subtype.
        :param dict value: (optional) The literal default value to replace at
               runtime.
        :param List[dict] valid_values: (optional) The valid values of the
               parameter.
        """
        self.name = name
        self.description = description
        self.prompt = prompt
        self.type = type
        self.subtype = subtype
        self.value = value
        self.valid_values = valid_values

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowAssetParameter":
        """Initialize a DataIntgFlowAssetParameter object from a json dictionary."""
        args = {}
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        if (description := _dict.get("description")) is not None:
            args["description"] = description
        if (prompt := _dict.get("prompt")) is not None:
            args["prompt"] = prompt
        if (type := _dict.get("type")) is not None:
            args["type"] = type
        if (subtype := _dict.get("subtype")) is not None:
            args["subtype"] = subtype
        if (value := _dict.get("value")) is not None:
            args["value"] = value
        if (valid_values := _dict.get("valid_values")) is not None:
            args["valid_values"] = valid_values
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowAssetParameter object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "name") and self.name is not None:
            _dict["name"] = self.name
        if hasattr(self, "description") and self.description is not None:
            _dict["description"] = self.description
        if hasattr(self, "prompt") and self.prompt is not None:
            _dict["prompt"] = self.prompt
        if hasattr(self, "type") and self.type is not None:
            _dict["type"] = self.type
        if hasattr(self, "subtype") and self.subtype is not None:
            _dict["subtype"] = self.subtype
        if hasattr(self, "value") and self.value is not None:
            _dict["value"] = self.value
        if hasattr(self, "valid_values") and self.valid_values is not None:
            _dict["valid_values"] = self.valid_values
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowAssetParameter object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowAssetParameter") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowAssetParameter") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowAssetParameterSet:
    """the parameter set definition from repository.

    :param str ref: (optional) referenced paramemter set asset.
    :param str name: (optional) referenced parameter set name.
    :param str description: (optional) The description of the parameter set.
    :param List[DataIntgFlowAssetParameter] parameters: (optional) the list of
          parameters in the parameter set.
    :param List[ValueSet] value_sets: (optional) the list of values.
    """

    def __init__(
        self,
        *,
        ref: str | None = None,
        name: str | None = None,
        description: str | None = None,
        parameters: list["DataIntgFlowAssetParameter"] | None = None,
        value_sets: list["ValueSet"] | None = None,
    ) -> None:
        """Initialize a DataIntgFlowAssetParameterSet object.

        :param str ref: (optional) referenced paramemter set asset.
        :param str name: (optional) referenced parameter set name.
        :param str description: (optional) The description of the parameter set.
        :param List[DataIntgFlowAssetParameter] parameters: (optional) the list of
               parameters in the parameter set.
        :param List[ValueSet] value_sets: (optional) the list of values.
        """
        self.ref = ref
        self.name = name
        self.description = description
        self.parameters = parameters
        self.value_sets = value_sets

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowAssetParameterSet":
        """Initialize a DataIntgFlowAssetParameterSet object from a json dictionary."""
        args = {}
        if (ref := _dict.get("ref")) is not None:
            args["ref"] = ref
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        if (description := _dict.get("description")) is not None:
            args["description"] = description
        if (parameters := _dict.get("parameters")) is not None:
            args["parameters"] = [DataIntgFlowAssetParameter.from_dict(v) for v in parameters]
        if (value_sets := _dict.get("value_sets")) is not None:
            args["value_sets"] = [ValueSet.from_dict(v) for v in value_sets]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowAssetParameterSet object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "ref") and self.ref is not None:
            _dict["ref"] = self.ref
        if hasattr(self, "name") and self.name is not None:
            _dict["name"] = self.name
        if hasattr(self, "description") and self.description is not None:
            _dict["description"] = self.description
        if hasattr(self, "parameters") and self.parameters is not None:
            parameters_list = []
            for v in self.parameters:
                if isinstance(v, dict):
                    parameters_list.append(v)
                else:
                    parameters_list.append(v.to_dict())
            _dict["parameters"] = parameters_list
        if hasattr(self, "value_sets") and self.value_sets is not None:
            value_sets_list = []
            for v in self.value_sets:
                if isinstance(v, dict):
                    value_sets_list.append(v)
                else:
                    value_sets_list.append(v.to_dict())
            _dict["value_sets"] = value_sets_list
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowAssetParameterSet object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowAssetParameterSet") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowAssetParameterSet") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowAssetParm:
    """Respond of getting referenced parameters API.

    :param List[DataIntgFlowAssetParameter] local_parameters: (optional) list of
          local paramemter objects referenced in DataStage flow.
    :param List[DataIntgFlowAssetParameterSet] parameter_sets: (optional) List of
          parameter set object referenced in DataStage flow.
    """

    def __init__(
        self,
        *,
        local_parameters: list["DataIntgFlowAssetParameter"] | None = None,
        parameter_sets: list["DataIntgFlowAssetParameterSet"] | None = None,
    ) -> None:
        """Initialize a DataIntgFlowAssetParm object.

        :param List[DataIntgFlowAssetParameter] local_parameters: (optional) list
               of local paramemter objects referenced in DataStage flow.
        :param List[DataIntgFlowAssetParameterSet] parameter_sets: (optional) List
               of parameter set object referenced in DataStage flow.
        """
        self.local_parameters = local_parameters
        self.parameter_sets = parameter_sets

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowAssetParm":
        """Initialize a DataIntgFlowAssetParm object from a json dictionary."""
        args = {}
        if (local_parameters := _dict.get("local_parameters")) is not None:
            args["local_parameters"] = [DataIntgFlowAssetParameter.from_dict(v) for v in local_parameters]
        if (parameter_sets := _dict.get("parameter_sets")) is not None:
            args["parameter_sets"] = [DataIntgFlowAssetParameterSet.from_dict(v) for v in parameter_sets]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowAssetParm object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "local_parameters") and self.local_parameters is not None:
            local_parameters_list = []
            for v in self.local_parameters:
                if isinstance(v, dict):
                    local_parameters_list.append(v)
                else:
                    local_parameters_list.append(v.to_dict())
            _dict["local_parameters"] = local_parameters_list
        if hasattr(self, "parameter_sets") and self.parameter_sets is not None:
            parameter_sets_list = []
            for v in self.parameter_sets:
                if isinstance(v, dict):
                    parameter_sets_list.append(v)
                else:
                    parameter_sets_list.append(v.to_dict())
            _dict["parameter_sets"] = parameter_sets_list
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowAssetParm object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowAssetParm") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowAssetParm") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowCompile:
    """Compile information for a DataStage flow asset.

    :param DataIntgFlowCompileMetadata metadata: (optional) Metadata information for
          a DataStage compile object.
    :param DataIntgFlowCompileEntity entity: (optional) Entity information for a
          DataStage Compile object.
    """

    def __init__(
        self,
        *,
        metadata: Optional["DataIntgFlowCompileMetadata"] = None,
        entity: Optional["DataIntgFlowCompileEntity"] = None,
    ) -> None:
        """Initialize a DataIntgFlowCompile object.

        :param DataIntgFlowCompileMetadata metadata: (optional) Metadata
               information for a DataStage compile object.
        :param DataIntgFlowCompileEntity entity: (optional) Entity information for
               a DataStage Compile object.
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowCompile":
        """Initialize a DataIntgFlowCompile object from a json dictionary."""
        args = {}
        if (metadata := _dict.get("metadata")) is not None:
            args["metadata"] = DataIntgFlowCompileMetadata.from_dict(metadata)
        if (entity := _dict.get("entity")) is not None:
            args["entity"] = DataIntgFlowCompileEntity.from_dict(entity)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowCompile object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "metadata") and self.metadata is not None:
            if isinstance(self.metadata, dict):
                _dict["metadata"] = self.metadata
            else:
                _dict["metadata"] = self.metadata.to_dict()
        if hasattr(self, "entity") and self.entity is not None:
            if isinstance(self.entity, dict):
                _dict["entity"] = self.entity
            else:
                _dict["entity"] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowCompile object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowCompile") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowCompile") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowCompileEntity:
    """Entity information for a DataStage Compile object.

    :param str data_intg_flow_id: (optional) DataStage flow ID.
    """

    def __init__(
        self,
        *,
        data_intg_flow_id: str | None = None,
    ) -> None:
        """Initialize a DataIntgFlowCompileEntity object.

        :param str data_intg_flow_id: (optional) DataStage flow ID.
        """
        self.data_intg_flow_id = data_intg_flow_id

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowCompileEntity":
        """Initialize a DataIntgFlowCompileEntity object from a json dictionary."""
        args = {}
        if (data_intg_flow_id := _dict.get("data_intg_flow_id")) is not None:
            args["data_intg_flow_id"] = data_intg_flow_id
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowCompileEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "data_intg_flow_id") and self.data_intg_flow_id is not None:
            _dict["data_intg_flow_id"] = self.data_intg_flow_id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowCompileEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowCompileEntity") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowCompileEntity") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowCompileMetadata:
    """Metadata information for a DataStage compile object.

    :param bool compiled: (optional) Compile status.
    :param str runtime_code: (optional) OSH script.
    :param str dataservice_endpoint: (optional) Data Service endpoint.
    """

    def __init__(
        self,
        *,
        compiled: bool | None = None,
        runtime_code: str | None = None,
        dataservice_endpoint: str | None = None,
    ) -> None:
        """Initialize a DataIntgFlowCompileMetadata object.

        :param bool compiled: (optional) Compile status.
        :param str runtime_code: (optional) OSH script.
        :param str dataservice_endpoint: (optional) Data Service endpoint.
        """
        self.compiled = compiled
        self.runtime_code = runtime_code
        self.dataservice_endpoint = dataservice_endpoint

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowCompileMetadata":
        """Initialize a DataIntgFlowCompileMetadata object from a json dictionary."""
        args = {}
        if (compiled := _dict.get("compiled")) is not None:
            args["compiled"] = compiled
        if (runtime_code := _dict.get("runtime_code")) is not None:
            args["runtime_code"] = runtime_code
        if (dataservice_endpoint := _dict.get("dataservice_endpoint")) is not None:
            args["dataservice_endpoint"] = dataservice_endpoint
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowCompileMetadata object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "compiled") and self.compiled is not None:
            _dict["compiled"] = self.compiled
        if hasattr(self, "runtime_code") and self.runtime_code is not None:
            _dict["runtime_code"] = self.runtime_code
        if hasattr(self, "dataservice_endpoint") and self.dataservice_endpoint is not None:
            _dict["dataservice_endpoint"] = self.dataservice_endpoint
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowCompileMetadata object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowCompileMetadata") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowCompileMetadata") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowEntity:
    """The underlying DataStage flow definition.

    :param dict data_intg_flow: (optional) Asset type object.
    :param dict data_intg_subflow: (optional) Asset type object.
    :param dict directory_asset: (optional) Asset type object for folder container.
    :param str description: (optional) The description of the DataStage flow.
    :param str name: (optional) The name of the DataStage flow.
    :param AssetEntityROV rov: (optional) The rules of visibility for an asset.
    :param str sub_type: (optional) A read-only field that can be used to
          distinguish between different types of data flow based on the service that
          created it.
    :param dict orchestration_flow: (optional) Asset type object.
    """

    def __init__(
        self,
        *,
        data_intg_flow: dict | None = None,
        data_intg_subflow: dict | None = None,
        directory_asset: dict | None = None,
        description: str | None = None,
        name: str | None = None,
        rov: Optional["AssetEntityROV"] = None,
        sub_type: str | None = None,
        orchestration_flow: dict | None = None,
    ) -> None:
        """Initialize a DataIntgFlowEntity object.

        :param dict data_intg_flow: (optional) Asset type object.
        :param dict data_intg_subflow: (optional) Asset type object.
        :param dict directory_asset: (optional) Asset type object for folder
               container.
        :param str description: (optional) The description of the DataStage flow.
        :param str name: (optional) The name of the DataStage flow.
        :param AssetEntityROV rov: (optional) The rules of visibility for an asset.
        :param str sub_type: (optional) A read-only field that can be used to
               distinguish between different types of data flow based on the service that
               created it.
        :param dict orchestration_flow: (optional) Asset type object.
        """
        self.data_intg_flow = data_intg_flow
        self.data_intg_subflow = data_intg_subflow
        self.directory_asset = directory_asset
        self.description = description
        self.name = name
        self.rov = rov
        self.sub_type = sub_type
        self.orchestration_flow = orchestration_flow

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowEntity":
        """Initialize a DataIntgFlowEntity object from a json dictionary."""
        args = {}
        if (data_intg_flow := _dict.get("data_intg_flow")) is not None:
            args["data_intg_flow"] = data_intg_flow
        if (data_intg_subflow := _dict.get("data_intg_subflow")) is not None:
            args["data_intg_subflow"] = data_intg_subflow
        if (directory_asset := _dict.get("directory_asset")) is not None:
            args["directory_asset"] = directory_asset
        if (description := _dict.get("description")) is not None:
            args["description"] = description
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        if (rov := _dict.get("rov")) is not None:
            args["rov"] = AssetEntityROV.from_dict(rov)
        if (sub_type := _dict.get("sub_type")) is not None:
            args["sub_type"] = sub_type
        if (orchestration_flow := _dict.get("orchestration_flow")) is not None:
            args["orchestration_flow"] = orchestration_flow
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "data_intg_flow") and self.data_intg_flow is not None:
            _dict["data_intg_flow"] = self.data_intg_flow
        if hasattr(self, "data_intg_subflow") and self.data_intg_subflow is not None:
            _dict["data_intg_subflow"] = self.data_intg_subflow
        if hasattr(self, "directory_asset") and self.directory_asset is not None:
            _dict["directory_asset"] = self.directory_asset
        if hasattr(self, "description") and self.description is not None:
            _dict["description"] = self.description
        if hasattr(self, "name") and self.name is not None:
            _dict["name"] = self.name
        if hasattr(self, "rov") and self.rov is not None:
            if isinstance(self.rov, dict):
                _dict["rov"] = self.rov
            else:
                _dict["rov"] = self.rov.to_dict()
        if hasattr(self, "sub_type") and self.sub_type is not None:
            _dict["sub_type"] = self.sub_type
        if hasattr(self, "orchestration_flow") and self.orchestration_flow is not None:
            _dict["orchestration_flow"] = self.orchestration_flow
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowEntity") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowEntity") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowExport:
    """Respond of Export API, including metadata array and attachment array of a DataStage
    flow asset.

    :param List[DataIntgFlow] metadata: (optional) Information about the export
          object for DataStage flow.
    :param List[str] attachments: (optional) List of attachments for export.
    """

    def __init__(
        self,
        *,
        metadata: list["DataIntgFlow"] | None = None,
        attachments: list[str] | None = None,
    ) -> None:
        """Initialize a DataIntgFlowExport object.

        :param List[DataIntgFlow] metadata: (optional) Information about the export
               object for DataStage flow.
        :param List[str] attachments: (optional) List of attachments for export.
        """
        self.metadata = metadata
        self.attachments = attachments

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowExport":
        """Initialize a DataIntgFlowExport object from a json dictionary."""
        args = {}
        if (metadata := _dict.get("metadata")) is not None:
            args["metadata"] = [DataIntgFlow.from_dict(v) for v in metadata]
        if (attachments := _dict.get("attachments")) is not None:
            args["attachments"] = attachments
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowExport object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "metadata") and self.metadata is not None:
            metadata_list = []
            for v in self.metadata:
                if isinstance(v, dict):
                    metadata_list.append(v)
                else:
                    metadata_list.append(v.to_dict())
            _dict["metadata"] = metadata_list
        if hasattr(self, "attachments") and self.attachments is not None:
            _dict["attachments"] = self.attachments
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowExport object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowExport") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowExport") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowJson:
    """A pipeline JSON containing operations to apply to source(s).

    :param AssetSystemMetadata metadata: (optional) System metadata about an asset.
    :param DataIntgFlowEntity entity: (optional) The underlying DataStage flow
          definition.
    :param PipelineJson attachments: (optional) Pipeline flow to be stored.
    """

    def __init__(
        self,
        *,
        metadata: Optional["AssetSystemMetadata"] = None,
        entity: Optional["DataIntgFlowEntity"] = None,
        attachments: Optional["PipelineJson"] = None,
    ) -> None:
        """Initialize a DataIntgFlowJson object.

        :param AssetSystemMetadata metadata: (optional) System metadata about an
               asset.
        :param DataIntgFlowEntity entity: (optional) The underlying DataStage flow
               definition.
        :param PipelineJson attachments: (optional) Pipeline flow to be stored.
        """
        self.metadata = metadata
        self.entity = entity
        self.attachments = attachments

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowJson":
        """Initialize a DataIntgFlowJson object from a json dictionary."""
        args = {}
        if (metadata := _dict.get("metadata")) is not None:
            args["metadata"] = AssetSystemMetadata.from_dict(metadata)
        if (entity := _dict.get("entity")) is not None:
            args["entity"] = DataIntgFlowEntity.from_dict(entity)
        if (attachments := _dict.get("attachments")) is not None:
            args["attachments"] = PipelineJson.from_dict(attachments)
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowJson object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "metadata") and self.metadata is not None:
            if isinstance(self.metadata, dict):
                _dict["metadata"] = self.metadata
            else:
                _dict["metadata"] = self.metadata.to_dict()
        if hasattr(self, "entity") and self.entity is not None:
            if isinstance(self.entity, dict):
                _dict["entity"] = self.entity
            else:
                _dict["entity"] = self.entity.to_dict()
        if hasattr(self, "attachments") and self.attachments is not None:
            if isinstance(self.attachments, dict):
                _dict["attachments"] = self.attachments
            else:
                _dict["attachments"] = self.attachments.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowJson object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowJson") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowJson") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowParameter:
    """The parameter definition.

    :param str name: (optional) The name of the parameter.
    :param str description: (optional) The description of the parameter.
    :param str prompt: (optional) The prompt of the parameter.
    :param str type: (optional) The parameter type.
    :param str subtype: (optional) The parameter subtype.
    :param dict value: (optional) The literal default value to replace at runtime.
    :param List[dict] valid_values: (optional) The valid values of the parameter.
    :param List[str] referenced_by: (optional) The list of pipeline flows reference
          the parameter.
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        prompt: str | None = None,
        type: str | None = None,
        subtype: str | None = None,
        value: dict | None = None,
        valid_values: list[dict] | None = None,
        referenced_by: list[str] | None = None,
    ) -> None:
        """Initialize a DataIntgFlowParameter object.

        :param str name: (optional) The name of the parameter.
        :param str description: (optional) The description of the parameter.
        :param str prompt: (optional) The prompt of the parameter.
        :param str type: (optional) The parameter type.
        :param str subtype: (optional) The parameter subtype.
        :param dict value: (optional) The literal default value to replace at
               runtime.
        :param List[dict] valid_values: (optional) The valid values of the
               parameter.
        :param List[str] referenced_by: (optional) The list of pipeline flows
               reference the parameter.
        """
        self.name = name
        self.description = description
        self.prompt = prompt
        self.type = type
        self.subtype = subtype
        self.value = value
        self.valid_values = valid_values
        self.referenced_by = referenced_by

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowParameter":
        """Initialize a DataIntgFlowParameter object from a json dictionary."""
        args = {}
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        if (description := _dict.get("description")) is not None:
            args["description"] = description
        if (prompt := _dict.get("prompt")) is not None:
            args["prompt"] = prompt
        if (type := _dict.get("type")) is not None:
            args["type"] = type
        if (subtype := _dict.get("subtype")) is not None:
            args["subtype"] = subtype
        if (value := _dict.get("value")) is not None:
            args["value"] = value
        if (valid_values := _dict.get("valid_values")) is not None:
            args["valid_values"] = valid_values
        if (referenced_by := _dict.get("referenced_by")) is not None:
            args["referenced_by"] = referenced_by
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowParameter object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "name") and self.name is not None:
            _dict["name"] = self.name
        if hasattr(self, "description") and self.description is not None:
            _dict["description"] = self.description
        if hasattr(self, "prompt") and self.prompt is not None:
            _dict["prompt"] = self.prompt
        if hasattr(self, "type") and self.type is not None:
            _dict["type"] = self.type
        if hasattr(self, "subtype") and self.subtype is not None:
            _dict["subtype"] = self.subtype
        if hasattr(self, "value") and self.value is not None:
            _dict["value"] = self.value
        if hasattr(self, "valid_values") and self.valid_values is not None:
            _dict["valid_values"] = self.valid_values
        if hasattr(self, "referenced_by") and self.referenced_by is not None:
            _dict["referenced_by"] = self.referenced_by
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowParameter object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowParameter") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowParameter") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowReferencedParameterSet:
    """Respond of getting referenced parameter set API.

    :param str ref: (optional) referenced paramemter set asset.
    :param str name: (optional) referenced parameter set name.
    :param str project_ref: (optional) project Id of the referenced parameter set.
    :param str space_ref: (optional) space Id of the referenced parameter set.
    :param List[str] referenced_by: (optional) The list of pipeline flows reference
          the parameter set.
    :param DataIntgFlowReferencedParameterSetParameterSet parameter_set: (optional)
          the parameter set definition from repository.
    :param str warning: (optional) warning while getting parameter set definition
          from repository.
    """

    def __init__(
        self,
        *,
        ref: str | None = None,
        name: str | None = None,
        project_ref: str | None = None,
        space_ref: str | None = None,
        referenced_by: list[str] | None = None,
        parameter_set: Optional["DataIntgFlowReferencedParameterSetParameterSet"] = None,
        warning: str | None = None,
    ) -> None:
        """Initialize a DataIntgFlowReferencedParameterSet object.

        :param str ref: (optional) referenced paramemter set asset.
        :param str name: (optional) referenced parameter set name.
        :param str project_ref: (optional) project Id of the referenced parameter
               set.
        :param str space_ref: (optional) space Id of the referenced parameter set.
        :param List[str] referenced_by: (optional) The list of pipeline flows
               reference the parameter set.
        :param DataIntgFlowReferencedParameterSetParameterSet parameter_set:
               (optional) the parameter set definition from repository.
        :param str warning: (optional) warning while getting parameter set
               definition from repository.
        """
        self.ref = ref
        self.name = name
        self.project_ref = project_ref
        self.space_ref = space_ref
        self.referenced_by = referenced_by
        self.parameter_set = parameter_set
        self.warning = warning

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowReferencedParameterSet":
        """Initialize a DataIntgFlowReferencedParameterSet object from a json dictionary."""
        args = {}
        if (ref := _dict.get("ref")) is not None:
            args["ref"] = ref
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        if (project_ref := _dict.get("project_ref")) is not None:
            args["project_ref"] = project_ref
        if (space_ref := _dict.get("space_ref")) is not None:
            args["space_ref"] = space_ref
        if (referenced_by := _dict.get("referenced_by")) is not None:
            args["referenced_by"] = referenced_by
        if (parameter_set := _dict.get("parameter_set")) is not None:
            args["parameter_set"] = DataIntgFlowReferencedParameterSetParameterSet.from_dict(parameter_set)
        if (warning := _dict.get("warning")) is not None:
            args["warning"] = warning
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowReferencedParameterSet object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "ref") and self.ref is not None:
            _dict["ref"] = self.ref
        if hasattr(self, "name") and self.name is not None:
            _dict["name"] = self.name
        if hasattr(self, "project_ref") and self.project_ref is not None:
            _dict["project_ref"] = self.project_ref
        if hasattr(self, "space_ref") and self.space_ref is not None:
            _dict["space_ref"] = self.space_ref
        if hasattr(self, "referenced_by") and self.referenced_by is not None:
            _dict["referenced_by"] = self.referenced_by
        if hasattr(self, "parameter_set") and self.parameter_set is not None:
            if isinstance(self.parameter_set, dict):
                _dict["parameter_set"] = self.parameter_set
            else:
                _dict["parameter_set"] = self.parameter_set.to_dict()
        if hasattr(self, "warning") and self.warning is not None:
            _dict["warning"] = self.warning
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowReferencedParameterSet object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowReferencedParameterSet") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowReferencedParameterSet") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowReferencedParameterSetParameterSet:
    """the parameter set definition from repository.

    :param str name: (optional) the parameter set name from repository.
    :param str description: (optional) the parameter set description from
          repository.
    :param List[DataIntgFlowParameter] parameters: (optional) the list of parameters
          in the parameter set.
    :param List[ValueSet] value_sets: (optional) the list of values.
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        parameters: list["DataIntgFlowParameter"] | None = None,
        value_sets: list["ValueSet"] | None = None,
    ) -> None:
        """Initialize a DataIntgFlowReferencedParameterSetParameterSet object.

        :param str name: (optional) the parameter set name from repository.
        :param str description: (optional) the parameter set description from
               repository.
        :param List[DataIntgFlowParameter] parameters: (optional) the list of
               parameters in the parameter set.
        :param List[ValueSet] value_sets: (optional) the list of values.
        """
        self.name = name
        self.description = description
        self.parameters = parameters
        self.value_sets = value_sets

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowReferencedParameterSetParameterSet":
        """Initialize a DataIntgFlowReferencedParameterSetParameterSet object from a json dictionary."""
        args = {}
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        if (description := _dict.get("description")) is not None:
            args["description"] = description
        if (parameters := _dict.get("parameters")) is not None:
            args["parameters"] = [DataIntgFlowParameter.from_dict(v) for v in parameters]
        if (value_sets := _dict.get("value_sets")) is not None:
            args["value_sets"] = [ValueSet.from_dict(v) for v in value_sets]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowReferencedParameterSetParameterSet object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "name") and self.name is not None:
            _dict["name"] = self.name
        if hasattr(self, "description") and self.description is not None:
            _dict["description"] = self.description
        if hasattr(self, "parameters") and self.parameters is not None:
            parameters_list = []
            for v in self.parameters:
                if isinstance(v, dict):
                    parameters_list.append(v)
                else:
                    parameters_list.append(v.to_dict())
            _dict["parameters"] = parameters_list
        if hasattr(self, "value_sets") and self.value_sets is not None:
            value_sets_list = []
            for v in self.value_sets:
                if isinstance(v, dict):
                    value_sets_list.append(v)
                else:
                    value_sets_list.append(v.to_dict())
            _dict["value_sets"] = value_sets_list
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowReferencedParameterSetParameterSet object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowReferencedParameterSetParameterSet") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowReferencedParameterSetParameterSet") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowReferencedParm:
    """Respond of getting referenced parameters API.

    :param List[DataIntgFlowParameter] local_parameters: (optional) list of local
          paramemter objects referenced in DataStage flow.
    :param List[dict] pipeline_parameters: (optional) list of pipeline paramemter
          objects referenced in Orchestration flow.
    :param List[DataIntgFlowReferencedParameterSet] parameter_sets: (optional) List
          of parameter set object referenced in DataStage flow.
    """

    def __init__(
        self,
        *,
        local_parameters: list["DataIntgFlowParameter"] | None = None,
        pipeline_parameters: list[dict] | None = None,
        parameter_sets: list["DataIntgFlowReferencedParameterSet"] | None = None,
    ) -> None:
        """Initialize a DataIntgFlowReferencedParm object.

        :param List[DataIntgFlowParameter] local_parameters: (optional) list of
               local paramemter objects referenced in DataStage flow.
        :param List[dict] pipeline_parameters: (optional) list of pipeline
               paramemter objects referenced in Orchestration flow.
        :param List[DataIntgFlowReferencedParameterSet] parameter_sets: (optional)
               List of parameter set object referenced in DataStage flow.
        """
        self.local_parameters = local_parameters
        self.pipeline_parameters = pipeline_parameters
        self.parameter_sets = parameter_sets

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowReferencedParm":
        """Initialize a DataIntgFlowReferencedParm object from a json dictionary."""
        args = {}
        if (local_parameters := _dict.get("local_parameters")) is not None:
            args["local_parameters"] = [DataIntgFlowParameter.from_dict(v) for v in local_parameters]
        if (pipeline_parameters := _dict.get("pipeline_parameters")) is not None:
            args["pipeline_parameters"] = pipeline_parameters
        if (parameter_sets := _dict.get("parameter_sets")) is not None:
            args["parameter_sets"] = [DataIntgFlowReferencedParameterSet.from_dict(v) for v in parameter_sets]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowReferencedParm object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "local_parameters") and self.local_parameters is not None:
            local_parameters_list = []
            for v in self.local_parameters:
                if isinstance(v, dict):
                    local_parameters_list.append(v)
                else:
                    local_parameters_list.append(v.to_dict())
            _dict["local_parameters"] = local_parameters_list
        if hasattr(self, "pipeline_parameters") and self.pipeline_parameters is not None:
            _dict["pipeline_parameters"] = self.pipeline_parameters
        if hasattr(self, "parameter_sets") and self.parameter_sets is not None:
            parameter_sets_list = []
            for v in self.parameter_sets:
                if isinstance(v, dict):
                    parameter_sets_list.append(v)
                else:
                    parameter_sets_list.append(v.to_dict())
            _dict["parameter_sets"] = parameter_sets_list
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowReferencedParm object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowReferencedParm") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowReferencedParm") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowRelationships:
    """The result of creating relationships between the flow and its referenced assets.

    :param str asset_id: (optional) The asset ID of the source.
    :param str asset_type: (optional) The asset type of the source.
    :param int total_count: (optional) The total number of relationships.
    :param List[object] relationships: (optional) An array of all relationships to
          referenced assets.
    """

    def __init__(
        self,
        *,
        asset_id: str | None = None,
        asset_type: str | None = None,
        total_count: int | None = None,
        relationships: list[object] | None = None,
    ) -> None:
        """Initialize a DataIntgFlowRelationships object.

        :param str asset_id: (optional) The asset ID of the source.
        :param str asset_type: (optional) The asset type of the source.
        :param int total_count: (optional) The total number of relationships.
        :param List[object] relationships: (optional) An array of all relationships
               to referenced assets.
        """
        self.asset_id = asset_id
        self.asset_type = asset_type
        self.total_count = total_count
        self.relationships = relationships

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowRelationships":
        """Initialize a DataIntgFlowRelationships object from a json dictionary."""
        args = {}
        if (asset_id := _dict.get("asset_id")) is not None:
            args["asset_id"] = asset_id
        if (asset_type := _dict.get("asset_type")) is not None:
            args["asset_type"] = asset_type
        if (total_count := _dict.get("total_count")) is not None:
            args["total_count"] = total_count
        if (relationships := _dict.get("relationships")) is not None:
            args["relationships"] = relationships
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowRelationships object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "asset_id") and self.asset_id is not None:
            _dict["asset_id"] = self.asset_id
        if hasattr(self, "asset_type") and self.asset_type is not None:
            _dict["asset_type"] = self.asset_type
        if hasattr(self, "total_count") and self.total_count is not None:
            _dict["total_count"] = self.total_count
        if hasattr(self, "relationships") and self.relationships is not None:
            _dict["relationships"] = self.relationships
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowRelationships object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowRelationships") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowRelationships") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class DataIntgFlowUnknownParameters:
    """DataIntgFlowUnknownParameters.

    :param List[dict] parameters: (optional) list of parameters, properties of each
          can have name and type.
    """

    def __init__(
        self,
        *,
        parameters: list[dict] | None = None,
    ) -> None:
        """Initialize a DataIntgFlowUnknownParameters object.

        :param List[dict] parameters: (optional) list of parameters, properties of
               each can have name and type.
        """
        self.parameters = parameters

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataIntgFlowUnknownParameters":
        """Initialize a DataIntgFlowUnknownParameters object from a json dictionary."""
        args = {}
        if (parameters := _dict.get("parameters")) is not None:
            args["parameters"] = parameters
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataIntgFlowUnknownParameters object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "parameters") and self.parameters is not None:
            _dict["parameters"] = self.parameters
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataIntgFlowUnknownParameters object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "DataIntgFlowUnknownParameters") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "DataIntgFlowUnknownParameters") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class FlowCompileResponse:
    """Describes the compile response model.

    :param str type: (optional) Compile response type. For example ok or error.
    :param dict message: (optional) Compile result for DataStage flow.
    """

    def __init__(
        self,
        *,
        type: str | None = None,
        message: dict | None = None,
    ) -> None:
        """Initialize a FlowCompileResponse object.

        :param str type: (optional) Compile response type. For example ok or error.
        :param dict message: (optional) Compile result for DataStage flow.
        """
        self.type = type
        self.message = message

    @classmethod
    def from_dict(cls, _dict: dict) -> "FlowCompileResponse":
        """Initialize a FlowCompileResponse object from a json dictionary."""
        args = {}
        if (type := _dict.get("type")) is not None:
            args["type"] = type
        if (message := _dict.get("message")) is not None:
            args["message"] = message
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a FlowCompileResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "type") and self.type is not None:
            _dict["type"] = self.type
        if hasattr(self, "message") and self.message is not None:
            _dict["message"] = self.message
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this FlowCompileResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "FlowCompileResponse") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "FlowCompileResponse") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class FlowCompileStatusResponse:
    """Describes the compile status response model.

    :param str type: (optional) Compile status response type. For example ok or
          error.
    :param dict message: (optional) Compile status response for DataStage flow.
    """

    def __init__(
        self,
        *,
        type: str | None = None,
        message: dict | None = None,
    ) -> None:
        """Initialize a FlowCompileStatusResponse object.

        :param str type: (optional) Compile status response type. For example ok or
               error.
        :param dict message: (optional) Compile status response for DataStage flow.
        """
        self.type = type
        self.message = message

    @classmethod
    def from_dict(cls, _dict: dict) -> "FlowCompileStatusResponse":
        """Initialize a FlowCompileStatusResponse object from a json dictionary."""
        args = {}
        if (type := _dict.get("type")) is not None:
            args["type"] = type
        if (message := _dict.get("message")) is not None:
            args["message"] = message
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a FlowCompileStatusResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "type") and self.type is not None:
            _dict["type"] = self.type
        if hasattr(self, "message") and self.message is not None:
            _dict["message"] = self.message
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this FlowCompileStatusResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "FlowCompileStatusResponse") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "FlowCompileStatusResponse") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class GenerateBuildOpResponse:
    """Describes the generateBuildOp response model.

    :param str type: (optional) generateBuildop response type. For example ok or
          error.
    :param dict message: (optional) generateBuildOp result for DataStage BuildOp.
    """

    def __init__(
        self,
        *,
        type: str | None = None,
        message: dict | None = None,
    ) -> None:
        """Initialize a GenerateBuildOpResponse object.

        :param str type: (optional) generateBuildop response type. For example ok
               or error.
        :param dict message: (optional) generateBuildOp result for DataStage
               BuildOp.
        """
        self.type = type
        self.message = message

    @classmethod
    def from_dict(cls, _dict: dict) -> "GenerateBuildOpResponse":
        """Initialize a GenerateBuildOpResponse object from a json dictionary."""
        args = {}
        if (type := _dict.get("type")) is not None:
            args["type"] = type
        if (message := _dict.get("message")) is not None:
            args["message"] = message
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a GenerateBuildOpResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "type") and self.type is not None:
            _dict["type"] = self.type
        if hasattr(self, "message") and self.message is not None:
            _dict["message"] = self.message
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this GenerateBuildOpResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "GenerateBuildOpResponse") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "GenerateBuildOpResponse") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class HrefModel:
    """URI of a resource.

    :param str href: URI of a resource.
    """

    def __init__(
        self,
        href: str,
    ) -> None:
        """Initialize a HrefModel object.

        :param str href: URI of a resource.
        """
        self.href = href

    @classmethod
    def from_dict(cls, _dict: dict) -> "HrefModel":
        """Initialize a HrefModel object from a json dictionary."""
        args = {}
        if (href := _dict.get("href")) is not None:
            args["href"] = href
        else:
            raise ValueError("Required property 'href' not present in HrefModel JSON")
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a HrefModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "href") and self.href is not None:
            _dict["href"] = self.href
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this HrefModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "HrefModel") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "HrefModel") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class PipelineJson:
    """Pipeline flow to be stored.

    :param str doc_type: (optional) The document type.
    :param str version: (optional) Pipeline flow version.
    :param str json_schema: (optional) Refers to the JSON schema used to validate
          documents of this type.
    :param str id: (optional) Document identifier, GUID recommended.
    :param str primary_pipeline: (optional) Reference to the primary (main) pipeline
          flow within the document.
    :param List[Pipelines] pipelines: (optional) Array of pipeline.
    :param List[dict] schemas: (optional) Array of data record schemas used in the
          pipeline.
    :param List[dict] runtimes: (optional) Runtime information for pipeline flow.
    :param dict app_data: (optional) Object containing app-specific data.
    :param dict parameters: (optional) Parameters for the flow document.
    :param List[dict] external_paramsets: (optional) Array of parameter set
          references.
    """

    def __init__(
        self,
        *,
        doc_type: str | None = None,
        version: str | None = None,
        json_schema: str | None = None,
        id: str | None = None,
        primary_pipeline: str | None = None,
        pipelines: list["Pipelines"] | None = None,
        schemas: list[dict] | None = None,
        runtimes: list[dict] | None = None,
        app_data: dict | None = None,
        parameters: dict | None = None,
        external_paramsets: list[dict] | None = None,
    ) -> None:
        """Initialize a PipelineJson object.

        :param str doc_type: (optional) The document type.
        :param str version: (optional) Pipeline flow version.
        :param str json_schema: (optional) Refers to the JSON schema used to
               validate documents of this type.
        :param str id: (optional) Document identifier, GUID recommended.
        :param str primary_pipeline: (optional) Reference to the primary (main)
               pipeline flow within the document.
        :param List[Pipelines] pipelines: (optional) Array of pipeline.
        :param List[dict] schemas: (optional) Array of data record schemas used in
               the pipeline.
        :param List[dict] runtimes: (optional) Runtime information for pipeline
               flow.
        :param dict app_data: (optional) Object containing app-specific data.
        :param dict parameters: (optional) Parameters for the flow document.
        :param List[dict] external_paramsets: (optional) Array of parameter set
               references.
        """
        self.doc_type = doc_type
        self.version = version
        self.json_schema = json_schema
        self.id = id
        self.primary_pipeline = primary_pipeline
        self.pipelines = pipelines
        self.schemas = schemas
        self.runtimes = runtimes
        self.app_data = app_data
        self.parameters = parameters
        self.external_paramsets = external_paramsets

    @classmethod
    def from_dict(cls, _dict: dict) -> "PipelineJson":
        """Initialize a PipelineJson object from a json dictionary."""
        args = {}
        if (doc_type := _dict.get("doc_type")) is not None:
            args["doc_type"] = doc_type
        if (version := _dict.get("version")) is not None:
            args["version"] = version
        if (json_schema := _dict.get("json_schema")) is not None:
            args["json_schema"] = json_schema
        if (id := _dict.get("id")) is not None:
            args["id"] = id
        if (primary_pipeline := _dict.get("primary_pipeline")) is not None:
            args["primary_pipeline"] = primary_pipeline
        if (pipelines := _dict.get("pipelines")) is not None:
            args["pipelines"] = [Pipelines.from_dict(v) for v in pipelines]
        if (schemas := _dict.get("schemas")) is not None:
            args["schemas"] = schemas
        if (runtimes := _dict.get("runtimes")) is not None:
            args["runtimes"] = runtimes
        if (app_data := _dict.get("app_data")) is not None:
            args["app_data"] = app_data
        if (parameters := _dict.get("parameters")) is not None:
            args["parameters"] = parameters
        if (external_paramsets := _dict.get("external_paramsets")) is not None:
            args["external_paramsets"] = external_paramsets
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a PipelineJson object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "doc_type") and self.doc_type is not None:
            _dict["doc_type"] = self.doc_type
        if hasattr(self, "version") and self.version is not None:
            _dict["version"] = self.version
        if hasattr(self, "json_schema") and self.json_schema is not None:
            _dict["json_schema"] = self.json_schema
        if hasattr(self, "id") and self.id is not None:
            _dict["id"] = self.id
        if hasattr(self, "primary_pipeline") and self.primary_pipeline is not None:
            _dict["primary_pipeline"] = self.primary_pipeline
        if hasattr(self, "pipelines") and self.pipelines is not None:
            pipelines_list = []
            for v in self.pipelines:
                if isinstance(v, dict):
                    pipelines_list.append(v)
                else:
                    pipelines_list.append(v.to_dict())
            _dict["pipelines"] = pipelines_list
        if hasattr(self, "schemas") and self.schemas is not None:
            _dict["schemas"] = self.schemas
        if hasattr(self, "runtimes") and self.runtimes is not None:
            _dict["runtimes"] = self.runtimes
        if hasattr(self, "app_data") and self.app_data is not None:
            _dict["app_data"] = self.app_data
        if hasattr(self, "parameters") and self.parameters is not None:
            _dict["parameters"] = self.parameters
        if hasattr(self, "external_paramsets") and self.external_paramsets is not None:
            _dict["external_paramsets"] = self.external_paramsets
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this PipelineJson object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "PipelineJson") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "PipelineJson") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class Pipelines:
    """Pipelines.

    :param str id: (optional) Unique identifier.
    :param str name: (optional) Name of the pipeline.
    :param str description: (optional) A brief description of the DataStage flow.
    :param str runtime_ref: (optional) Reference to the runtime type.
    :param List[dict] nodes: (optional) Array of pipeline nodes.
    :param dict app_data: (optional) Object containing app-specific data.
    """

    def __init__(
        self,
        *,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        runtime_ref: str | None = None,
        nodes: list[dict] | None = None,
        app_data: dict | None = None,
    ) -> None:
        """Initialize a Pipelines object.

        :param str id: (optional) Unique identifier.
        :param str name: (optional) Name of the pipeline.
        :param str description: (optional) A brief description of the DataStage
               flow.
        :param str runtime_ref: (optional) Reference to the runtime type.
        :param List[dict] nodes: (optional) Array of pipeline nodes.
        :param dict app_data: (optional) Object containing app-specific data.
        """
        self.id = id
        self.name = name
        self.description = description
        self.runtime_ref = runtime_ref
        self.nodes = nodes
        self.app_data = app_data

    @classmethod
    def from_dict(cls, _dict: dict) -> "Pipelines":
        """Initialize a Pipelines object from a json dictionary."""
        args = {}
        if (id := _dict.get("id")) is not None:
            args["id"] = id
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        if (description := _dict.get("description")) is not None:
            args["description"] = description
        if (runtime_ref := _dict.get("runtime_ref")) is not None:
            args["runtime_ref"] = runtime_ref
        if (nodes := _dict.get("nodes")) is not None:
            args["nodes"] = nodes
        if (app_data := _dict.get("app_data")) is not None:
            args["app_data"] = app_data
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Pipelines object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "id") and self.id is not None:
            _dict["id"] = self.id
        if hasattr(self, "name") and self.name is not None:
            _dict["name"] = self.name
        if hasattr(self, "description") and self.description is not None:
            _dict["description"] = self.description
        if hasattr(self, "runtime_ref") and self.runtime_ref is not None:
            _dict["runtime_ref"] = self.runtime_ref
        if hasattr(self, "nodes") and self.nodes is not None:
            _dict["nodes"] = self.nodes
        if hasattr(self, "app_data") and self.app_data is not None:
            _dict["app_data"] = self.app_data
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Pipelines object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "Pipelines") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "Pipelines") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class ValueSet:
    """ValueSet.

    :param str name: (optional) The name of the value_set.
    :param List[object] values: (optional) The list of values.
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        values: list[object] | None = None,
    ) -> None:
        """Initialize a ValueSet object.

        :param str name: (optional) The name of the value_set.
        :param List[object] values: (optional) The list of values.
        """
        self.name = name
        self.values = values

    @classmethod
    def from_dict(cls, _dict: dict) -> "ValueSet":
        """Initialize a ValueSet object from a json dictionary."""
        args = {}
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        if (values := _dict.get("values")) is not None:
            args["values"] = values
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ValueSet object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "name") and self.name is not None:
            _dict["name"] = self.name
        if hasattr(self, "values") and self.values is not None:
            _dict["values"] = self.values
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ValueSet object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "ValueSet") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "ValueSet") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other


class VersionInfo:
    """Version information about a service.

    :param str failure_message: (optional) A message indicating the cause if the
          service is not running. correctly.
    :param str service_name: (optional) The name of the service.
    :param str status: (optional) An overall status indicating whether the service
          is running. correctly.
    :param datetime timestamp: (optional) The timestamp when the information was
          retrieved (in format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ, matching
          the date-time format as specified by RFC 3339).
    :param str version: (optional) The service version string.
    """

    def __init__(
        self,
        *,
        failure_message: str | None = None,
        service_name: str | None = None,
        status: str | None = None,
        timestamp: datetime | None = None,
        version: str | None = None,
    ) -> None:
        """Initialize a VersionInfo object.

        :param str failure_message: (optional) A message indicating the cause if
               the service is not running. correctly.
        :param str service_name: (optional) The name of the service.
        :param str status: (optional) An overall status indicating whether the
               service is running. correctly.
        :param datetime timestamp: (optional) The timestamp when the information
               was retrieved (in format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ,
               matching the date-time format as specified by RFC 3339).
        :param str version: (optional) The service version string.
        """
        self.failure_message = failure_message
        self.service_name = service_name
        self.status = status
        self.timestamp = timestamp
        self.version = version

    @classmethod
    def from_dict(cls, _dict: dict) -> "VersionInfo":
        """Initialize a VersionInfo object from a json dictionary."""
        args = {}
        if (failure_message := _dict.get("failure_message")) is not None:
            args["failure_message"] = failure_message
        if (service_name := _dict.get("service_name")) is not None:
            args["service_name"] = service_name
        if (status := _dict.get("status")) is not None:
            args["status"] = status
        if (timestamp := _dict.get("timestamp")) is not None:
            args["timestamp"] = _string_to_datetime(timestamp)
        if (version := _dict.get("version")) is not None:
            args["version"] = version
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a VersionInfo object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, "failure_message") and self.failure_message is not None:
            _dict["failure_message"] = self.failure_message
        if hasattr(self, "service_name") and self.service_name is not None:
            _dict["service_name"] = self.service_name
        if hasattr(self, "status") and self.status is not None:
            _dict["status"] = self.status
        if hasattr(self, "timestamp") and self.timestamp is not None:
            _dict["timestamp"] = _datetime_to_string(self.timestamp)
        if hasattr(self, "version") and self.version is not None:
            _dict["version"] = self.version
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this VersionInfo object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: "VersionInfo") -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: "VersionInfo") -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class StatusEnum(str, Enum):
        """An overall status indicating whether the service is running. correctly."""

        FATAL = "fatal"
        WARNING = "warning"
        OK = "ok"


##############################################################################
# Pagers
##############################################################################


class DatastageFlowsPager:
    """DatastageFlowsPager can be used to simplify the use of the "list_datastage_flows" method."""

    def __init__(
        self,
        *,
        client: DatastageFlowApiClient,
        catalog_id: str = None,
        project_id: str = None,
        space_id: str = None,
        sort: str = None,
        limit: int = None,
        entity_name: str = None,
        entity_description: str = None,
    ) -> None:
        """Initialize a DatastageFlowsPager object.
        :param str catalog_id: (optional) The ID of the catalog to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str project_id: (optional) The ID of the project to use.
               `catalog_id` or `project_id` or `space_id` is required.
        :param str space_id: (optional) The ID of the space to use. `catalog_id` or
               `project_id` or `space_id` is required.
        :param str sort: (optional) The field to sort the results on, including
               whether to sort ascending (+) or descending (-), for example,
               sort=-metadata.create_time.
        :param int limit: (optional) The limit of the number of items to return for
               each page, for example limit=50. If not specified a default of 100 will be
               used. The maximum value of limit is 200.
        :param str entity_name: (optional) Filter results based on the specified
               name.
        :param str entity_description: (optional) Filter results based on the
               specified description.
        """
        self._has_next = True
        self._client = client
        self._page_context = {"next": None}
        self._catalog_id = catalog_id
        self._project_id = project_id
        self._space_id = space_id
        self._sort = sort
        self._limit = limit
        self._entity_name = entity_name
        self._entity_description = entity_description

    def has_next(self) -> bool:
        """Returns true if there are potentially more results to be retrieved."""
        return self._has_next

    def get_next(self) -> list[dict]:
        """Returns the next page of results.
        :return: A List[dict], where each element is a dict that represents an instance of DataIntgFlow.
        :rtype: List[dict]
        """
        if not self.has_next():
            raise StopIteration(message="No more results available")

        result = self._client.list_datastage_flows(
            catalog_id=self._catalog_id,
            project_id=self._project_id,
            space_id=self._space_id,
            sort=self._sort,
            limit=self._limit,
            entity_name=self._entity_name,
            entity_description=self._entity_description,
            start=self._page_context.get("next"),
        ).json()

        next = None
        next_page_link = result.get("next")
        if next_page_link is not None:
            next = _get_query_param(next_page_link.get("href"), "start")
        self._page_context["next"] = next
        if next is None:
            self._has_next = False

        return result.get("data_flows")

    def get_all(self) -> list[dict]:
        """Returns all results by invoking get_next() repeatedly
        until all pages of results have been retrieved.
        :return: A List[dict], where each element is a dict that represents an instance of DataIntgFlow.
        :rtype: List[dict]
        """
        results = []
        while self.has_next():
            next_page = self.get_next()
            results.extend(next_page)
        return results


# class DatastageSubflowsPager:
#     """DatastageSubflowsPager can be used to simplify the use of the "list_datastage_subflows" method."""

#     def __init__(
#         self,
#         *,
#         client: DatastageFlowApiClient,
#         catalog_id: str = None,
#         project_id: str = None,
#         space_id: str = None,
#         sort: str = None,
#         limit: int = None,
#         entity_name: str = None,
#         entity_description: str = None,
#     ) -> None:
#         """Initialize a DatastageSubflowsPager object.
#         :param str catalog_id: (optional) The ID of the catalog to use.
#                `catalog_id` or `project_id` or `space_id` is required.
#         :param str project_id: (optional) The ID of the project to use.
#                `catalog_id` or `project_id` or `space_id` is required.
#         :param str space_id: (optional) The ID of the space to use. `catalog_id` or
#                `project_id` or `space_id` is required.
#         :param str sort: (optional) The field to sort the results on, including
#                whether to sort ascending (+) or descending (-), for example,
#                sort=-metadata.create_time.
#         :param int limit: (optional) The limit of the number of items to return for
#                each page, for example limit=50. If not specified a default of 100 will be
#                used. The maximum value of limit is 200.
#         :param str entity_name: (optional) Filter results based on the specified
#                name.
#         :param str entity_description: (optional) Filter results based on the
#                specified description.
#         """
#         self._has_next = True
#         self._client = client
#         self._page_context = {"next": None}
#         self._catalog_id = catalog_id
#         self._project_id = project_id
#         self._space_id = space_id
#         self._sort = sort
#         self._limit = limit
#         self._entity_name = entity_name
#         self._entity_description = entity_description

#     def has_next(self) -> bool:
#         """Returns true if there are potentially more results to be retrieved."""
#         return self._has_next

#     def get_next(self) -> list[dict]:
#         """Returns the next page of results.
#         :return: A List[dict], where each element is a dict that represents an instance of DataIntgFlow.
#         :rtype: List[dict]
#         """
#         if not self.has_next():
#             raise StopIteration(message="No more results available")

#         result = self._client.list_datastage_subflows(
#             catalog_id=self._catalog_id,
#             project_id=self._project_id,
#             space_id=self._space_id,
#             sort=self._sort,
#             limit=self._limit,
#             entity_name=self._entity_name,
#             entity_description=self._entity_description,
#             start=self._page_context.get("next"),
#         ).get_result()

#         next = None
#         next_page_link = result.get("next")
#         if next_page_link is not None:
#             next = _get_query_param(next_page_link.get("href"), "start")
#         self._page_context["next"] = next
#         if next is None:
#             self._has_next = False

#         return result.get("data_flows")

#     def get_all(self) -> list[dict]:
#         """Returns all results by invoking get_next() repeatedly
#         until all pages of results have been retrieved.
#         :return: A List[dict], where each element is a dict that represents an instance of DataIntgFlow.
#         :rtype: List[dict]
#         """
#         results = []
#         while self.has_next():
#             next_page = self.get_next()
#             results.extend(next_page)
#         return results
