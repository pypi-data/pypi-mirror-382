#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

# ruff: noqa: D100   # auto-generated file (Missing docstring in public module)
# ruff: noqa: D101   # auto-generated file (Missing docstring in public class)
# ruff: noqa: E501   # auto-generated file (Line too long)


from __future__ import annotations

import json
import requests
import urllib
import urllib3
from ibm_watsonx_data_integration.common.json_patch_format import prepare_json_patch_payload
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.common.utils import get_params_from_swagger
from pathlib import Path
from pydantic import ConfigDict, Field
from typing import TYPE_CHECKING, Any, ClassVar
from typing_extensions import override

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models import Project
    from ibm_watsonx_data_integration.platform import Platform


class ConnectionsServiceInfo(BaseModel):
    configuration: dict[str, Any] | None = Field(None, repr=False)
    failure_message: str | None = Field(
        None, description="A message indicating the cause if the service is not running correctly", repr=False
    )
    service_name: str | None = Field(None, description="The name of the service", repr=True)
    status: str | None = Field(
        None, description="An overall status indicating whether the service is running correctly", repr=False
    )
    timestamp: str | None = Field(
        None,
        description="The timestamp when the information was retrieved (in format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ, matching the date-time format as specified by RFC 3339)",
        repr=False,
    )
    version: str | None = Field(None, description="The service version string", repr=True)

    model_config = ConfigDict(frozen=True)


class FunctionalID(BaseModel):
    description: str | None = Field(None, description="Description of this functional.", repr=False)
    entitlements: list[str] | None = Field(None, description="The list of names of relevant entitlements.", repr=False)
    functional_id: str | None = Field(None, description="the ID of function.", repr=True)
    label: str | None = Field(None, description="the label of this functional.", repr=False)
    tools: list[str] | None = Field(None, description="Allowed tools that consume this functional ID.", repr=False)

    model_config = ConfigDict(frozen=True)


class DirectoryAsset(BaseModel):
    path: str | None = Field(None, description="Folder ID that the connection asset lives in.", repr=False)

    model_config = ConfigDict(frozen=True)


class DatasourceTypeProperty(BaseModel):
    default_value: str | None = Field(
        None, description="The default value for the property if the value is not otherwise specified.", repr=False
    )
    description: str | None = Field(None, description="The description for the property.", repr=False)
    group: str | None = Field(None, description="A classification group for the property.", repr=False)
    hidden: bool | None = Field(
        None, description="Whether the property should be displayed in a user interface.", repr=False
    )
    label: str | None = Field(None, description="The label for the property.", repr=False)
    masked: bool | None = Field(
        None,
        description="Whether the property should be masked. For example, when the property is a password.",
        repr=False,
    )
    name: str | None = Field(None, description="The property name.", repr=True)
    required: bool | None = Field(None, description="Whether the property is required.", repr=False)
    type: str | None = Field(None, description="The type of the property.", repr=False)
    values: list[dict] | None = Field(
        None,
        description="If the property type is enum, the list of enumerated values that the property can take.",
        repr=False,
    )

    model_config = ConfigDict(frozen=True)


class ConnectionInteractionProperties(BaseModel):
    source: list[DatasourceTypeProperty] | None = Field(
        None, description="The properties that can be set for a source interaction.", repr=False
    )
    target: list[DatasourceTypeProperty] | None = Field(
        None, description="The properties that can be set for a target interaction.", repr=False
    )

    model_config = ConfigDict(frozen=True)


class ConnectionMetadata(BaseModel):
    asset_category: str | None = Field(None, description='The asset category ("USER" or "SYSTEM")', repr=False)
    asset_id: str | None = Field(None, description="The ID of the asset", repr=False)
    asset_type: str | None = Field(None, description="The type of the asset", repr=False)
    catalog_id: str | None = Field(
        None,
        description="The ID of the catalog which contains the asset. catalog_id, project_id or spaceid is required.",
        repr=False,
    )
    create_time: str | None = Field(
        None,
        description="The timestamp when the asset was created (in format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ, matching the date-time format as specified by RFC 3339)",
        repr=False,
    )
    creator_id: str | None = Field(None, description="The IAM ID of the user that created the asset", repr=False)
    href: str | None = Field(None, description="URL that can be used to get the asset.", repr=False)
    owner_id: str | None = Field(None, description="The IAM ID of the user that owns the asset", repr=False)
    project_id: str | None = Field(
        None,
        description="The ID of the project which contains the asset. catalog_id, project_id or spaceid is required.",
        repr=False,
    )
    resource_key: str | None = Field(
        None, description="Optional external unique key for assets that supports it", repr=False
    )
    space_id: str | None = Field(
        None,
        description="The ID of the space which contains the asset. catalog_id, project_id or spaceid is required.",
        repr=False,
    )
    tags: list[str] | None = Field(None, repr=False)


class Connection(BaseModel):
    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity": {}}
    asset_category: str | None = Field(None, description="The asset category", repr=False, frozen=True)
    data_source_definition_asset_id: str | None = Field(
        None,
        description='The id of the data source definition asset related to connection. For example "cfdcb449-1204-44ba-baa6-9a8a878e6aa7".',
        repr=False,
        frozen=True,
    )
    data_source_definition_asset_name: str | None = Field(
        None,
        description='The name of the data source definition asset related to connection. For example "Data privacy profile for DB2".',
        repr=False,
    )
    datasource_type: str = Field(
        description='The id or the name of the data source type to connect to. For example "cfdcb449-1204-44ba-baa6-9a8a878e6aa7" or "db2".',
        repr=False,
    )
    description: str | None = Field(None, description="The description of the connection.", repr=False)
    gateway_id: str | None = Field(
        None,
        description='The id of the secure gateway to use with the connection. A Secure Gateway is needed when connecting to an on-premises data source. This is the id of the Secure Gateway created with the SecureGateway Service. Your Secure Gateway Client running on-premises must be connected to the gateway with this Id. For example, "E9oXGRIhv1e_prod_ng".',
        repr=False,
    )
    interaction_properties: ConnectionInteractionProperties | None = Field(None, repr=False)
    metadata: ConnectionMetadata | None = Field(None, repr=False)
    name: str = Field(description="The name of the connection.", repr=True)
    owner_id: str | None = Field(
        None,
        description="Owner or creator of connection.  Provided when a service ID token is used to create connection.",
        repr=False,
        frozen=True,
    )
    properties: dict | None = Field(None, repr=False)
    ref_asset_id: str | None = Field(
        None,
        description="The ID of the connection in reference catalog that this connection refers to for properties values.",
        repr=False,
    )
    ref_catalog_id: str | None = Field(
        None, description="The ID of the catalog that this connection refers to for properties values.", repr=False
    )
    resource_key: str | None = Field(
        None,
        description="Resource key that should be set in connection asset metadata record instead of using a calculated one by the service.",
        repr=False,
    )
    source_system: dict[str, dict[str, Any]] | None = Field(None, repr=False)
    source_system_history: list[dict[str, dict[str, Any]]] | None = Field(None, repr=False)
    tags: list[str] | None = Field(None, repr=False)

    def __init__(self, platform: Platform = None, project: Project = None, **connection_json: dict) -> None:
        """The __init__ of the Connection class.

        Args:
            connection_json: The JSON for the Connection.
            platform: The Platform object.
            project: The Project object.
        """
        super().__init__(**connection_json)
        self._platform = platform
        self._project = project
        self._origin = self.model_dump()

    @staticmethod
    def _create(
        project: Project,
        name: str,
        datasource_type: DatasourceType,
        description: str | None = None,
        properties: dict | None = None,
        test: bool = True,
    ) -> Connection:
        data = {
            "name": name,
            "datasource_type": datasource_type.metadata.asset_id,
        }
        if description:
            data["description"] = description
        if properties:
            data["properties"] = properties
        params = {
            "project_id": project.metadata.guid,
            "test": test,
        }
        response = project._platform._connections_api.add_connection(data=json.dumps(data), params=params)
        return Connection(platform=project._platform, project=project, **response.json())

    def model_dump(self, *, by_alias: bool = True, exclude_unset: bool = True, **kwargs: dict) -> dict:
        """Changing default parameters of model_dump to make sure that serialized json math API response.

        Args:
            by_alias: Whether to use alias names in serialization.
            exclude_unset: Whether to exclude unset fields from serialization.
            **kwargs: Additional keyword arguments to pass to the model_dump method.

        Returns:
           A dictionary representation of the model.
        """
        return super().model_dump(exclude_unset=exclude_unset, by_alias=by_alias, **kwargs)

    @property
    def connection_id(self) -> str:
        """Returns id of connection."""
        return self.metadata.asset_id

    @property
    def origin(self) -> dict:
        """Returns origin model dump."""
        return self._origin

    @property
    def actions(self) -> list[DatasourceTypeAction]:
        """Get all supported actions for the connection.

        Returns:
            Retrieved list of Actions.
        """
        params = {
            "project_id": self._project.metadata.guid,
        }
        actions = self._platform._connections_api.get_connection_actions(
            connection_id=self.metadata.asset_id,
            params=params,
        )
        return [
            DatasourceTypeAction(platform=self._platform, project=self, connection=self, **action)
            for action in actions.json().get("actions", list())
        ]

    def _delete(self) -> requests.Response:
        """Remove the Connection.

        Returns:
            A HTTP response.
        """
        params = {
            "project_id": self._project.metadata.guid,
        }
        return self._platform._connections_api.delete_connection(connection_id=self.metadata.asset_id, params=params)

    def _update(self, test: bool = True) -> requests.Response:
        """Update the Connection.

        Args:
            test: whether to test the connection before saving it.
                  If true and validation cannot be estabilished, connection will not be saved.

        Returns:
            A HTTP response.
        """
        params = {
            "project_id": self._project.metadata.guid,
            "test": test,
        }
        data = prepare_json_patch_payload(self.origin["entity"], self.model_dump()["entity"])
        return self._platform._connections_api.update_connection(
            connection_id=self.metadata.asset_id,
            params=params,
            data=data,
        )

    def _copy(self) -> Connection:
        """Update the Connection.

        Returns:
            Copied Connection object.
        """
        params = {
            "project_id": self._project.metadata.guid,
            "target_project_id": self._project.metadata.guid,
        }
        new_connection = self._platform._connections_api.copy_connection(
            connection_id=self.metadata.asset_id,
            params=params,
        )
        return Connection(platform=self._platform, project=self._project, **new_connection.json())


class Connections(CollectionModel):
    """Collection of Connection instances."""

    def __init__(self, platform: Platform, project: Project) -> None:
        """The __init__ of the Connection class.

        Args:
            platform: The Platform object.
            project: Instance of Project in which connection was created.
        """
        super().__init__(platform)
        self.unique_id = "metadata.asset_id"
        self._project = project

    @override
    def __len__(self) -> int:
        connections_json = self._platform._connections_api.get_connections(
            params={
                "project_id": self._project.metadata.guid,
                "limit": 1,
            },
        ).json()
        return connections_json["total_count"]

    def _request_parameters(self) -> list:
        request_params = ["project_id", "connection_id"]
        content_string = self._platform._connections_api.get_swagger().text
        request_path = f"/{self._platform._connections_api.url_path_connections}"
        request_params.extend(get_params_from_swagger(content_string=content_string, request_path=request_path))
        return request_params

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "project_id": self._project.metadata.guid,
            "limit": 100,
        }
        request_params_unioned: dict[str, Any] = request_params_defaults

        request_params_unioned.update(request_params)

        if "creator" in request_params_unioned:
            request_params_unioned["metadata.creator"] = request_params_unioned["creator"]
            del request_params_unioned["creator"]
        if "name" in request_params_unioned:
            request_params_unioned["entity.name"] = request_params_unioned["name"]
            del request_params_unioned["name"]
        if "datasource_type" in request_params_unioned:
            request_params_unioned["entity.datasource_type"] = request_params_unioned["datasource_type"]
            del request_params_unioned["datasource_type"]
        if "data_source_definition_asset_id" in request_params_unioned:
            request_params_unioned["entity.data_source_definition_asset_id"] = request_params_unioned[
                "data_source_definition_asset_id"
            ]
            del request_params_unioned["data_source_definition_asset_id"]
        if "context" in request_params_unioned:
            request_params_unioned["entity.context"] = request_params_unioned["context"]
            del request_params_unioned["context"]
        if "properties" in request_params_unioned:
            request_params_unioned["entity.properties"] = json.dumps(request_params_unioned["properties"])
        if "flags" in request_params_unioned:
            request_params_unioned["entity.flags"] = request_params_unioned["flags"]
            del request_params_unioned["flags"]

        response = dict()
        if "connection_id" in request_params:
            connection_json = self._platform._connections_api.get_connection(
                connection_id=request_params["connection_id"],
                params={
                    "project_id": self._project.metadata.guid,
                },
            ).json()
            response["resources"] = [connection_json]
        else:
            response = self._platform._connections_api.get_connections(
                params={k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()

            if "next" in response:
                response["next"] = urllib.parse.parse_qs(urllib3.util.parse_url(response["next"]["href"]).query).get(
                    "start"
                )

        return CollectionModelResults(
            results=response,
            class_type=Connection,
            response_bookmark="next",
            request_bookmark="start",
            response_location="resources",
            constructor_params={"platform": self._platform, "project": self._project},
        )


class DiscoveredAsset(BaseModel):
    description: str | None = Field(None, description="A description of the asset.", repr=False)
    details: dict[str, dict[str, Any]] | None = Field(None, repr=False)
    has_children: bool | None = Field(
        None,
        description="True if it is known that the asset has children. False if it is known that the asset does not have children. If it is not known, or it is too expensive to determine this, then this property will not be returned.",
        repr=False,
    )
    id: str | None = Field(None, description="An ID for the asset.", repr=False)
    name: str | None = Field(None, description="A name for the asset.", repr=True)
    path: str | None = Field(
        None, description="The path for the object which can be used to discover child assets.", repr=False
    )
    tags: list[str] | None = Field(None, description="Tags associated with the asset.", repr=False)
    type: str | None = Field(
        None, description="The type of the asset, such as SCHEMA, TABLE, FILE, or FOLDER.", repr=True
    )

    model_config = ConfigDict(frozen=True)


class DatasourceTypeActionProperties(BaseModel):
    input: list[DatasourceTypeProperty] | None = Field(None, description="The input properties.", repr=False)
    output: list[DatasourceTypeProperty] | None = Field(
        None, description="The properties of the action result.", repr=False
    )

    model_config = ConfigDict(frozen=True)


class DatasourceTypeAction(BaseModel):
    description: str | None = Field(None, description="A description of the action.", repr=False)
    name: str | None = Field(None, description="The action name.", repr=True)
    properties: DatasourceTypeActionProperties | None = Field(None, repr=False)

    model_config = ConfigDict(frozen=True)

    def __init__(
        self,
        platform: Platform = None,
        project: Project = None,
        connection: Connection = None,
        **action_json: dict,
    ) -> None:
        """The __init__ of the DatasourceTypeAction class.

        Args:
            action_json: The JSON for the DatasourceTypeAction.
            platform: The Platform object.
            project: The Project object.
            connection: The Connection object.
        """
        super().__init__(**action_json)
        self._platform = platform
        self._project = project
        self._connection = connection

    def model_dump(self, *, by_alias: bool = True, exclude_unset: bool = True, **kwargs: dict) -> dict:
        """Changing default parameters of model_dump to make sure that serialized json math API response.

        Args:
            by_alias: Whether to use alias names in serialization.
            exclude_unset: Whether to exclude unset fields from serialization.
            **kwargs: Additional keyword arguments to pass to the model_dump method.

        Returns:
           A dictionary representation of the model.
        """
        return super().model_dump(exclude_unset=exclude_unset, by_alias=by_alias, **kwargs)

    def execute(
        self, configuration: dict[str, Any] | None = None, connection: Connection | None = None
    ) -> requests.Response:
        """Execute DatasourceTypeAction.

        Args:
            configuration: action config parameters.
            connection: connection to be used.

        Returns:
            A HTTP response.

        Raises:
            ValueError: If no connection is provided.
        """
        if self._connection is None and connection is None:
            raise ValueError("No connection provided.")

        params = {
            "project_id": self._project.metadata.guid,
        }
        data = configuration or dict()
        response = self._platform._connections_api.perform_connection_action(
            connection_id=connection.metadata.asset_id if connection else self._connection.metadata.asset_id,
            action_name=self.name,
            params=params,
            data=data,
        )
        return response


class DatasourceTypeProperties(BaseModel):
    connection: list[DatasourceTypeProperty] = Field(
        default_factory=list, description="The connection properties.", repr=False
    )
    filter: list[DatasourceTypeProperty] | None = Field(
        None, description="The filter properties that can be set for a discovery interaction.", repr=False
    )
    source: list[DatasourceTypeProperty] | None = Field(
        None, description="The properties that can be set for a source interaction.", repr=False
    )
    target: list[DatasourceTypeProperty] | None = Field(
        None, description="The properties that can be set for a target interaction.", repr=False
    )

    model_config = ConfigDict(frozen=True)


class DatasourceType(BaseModel):
    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity": {}}
    actions: list[DatasourceTypeAction] | None = Field(
        None, description="The actions supported for the data source.", repr=False
    )
    allowed_as_source: bool | None = Field(
        None,
        description="Whether the data source can be accessed as a source of data. That is, data can be read from the data source.",
        repr=False,
    )
    allowed_as_target: bool | None = Field(
        None,
        description="Whether the data source can be accessed as a target. That is, data can be written to the data source.",
        repr=False,
    )
    child_source_systems: list[dict[str, dict[str, Any]]] | None = Field(None, repr=False)
    description: str | None = Field(
        None, description="A localized, displayable description of the data source.", repr=False
    )
    label: str | None = Field(None, description='A localized, displayable label such as, "IBM dashDB".', repr=False)
    metadata: ConnectionMetadata | None = Field(None, repr=False)
    name: str | None = Field(None, description='A unique name, such as "dashdb".', repr=True)
    origin_country: str | None = Field(
        None, description="Country which data originated from. - ISO 3166 Country Codes.", repr=False
    )
    owner_id: str | None = Field(
        None,
        description="Owner or creator of connection.  Provided when a service ID token is used to create connection.",
        repr=False,
    )
    properties: DatasourceTypeProperties = Field(default_factory=DatasourceTypeProperties, repr=False)
    status: str | None = Field(None, description="The status of the data source.", repr=False)
    tags: list[str] | None = Field(None, description="Tags associated with a data source type.", repr=False)

    model_config = ConfigDict(frozen=True)

    def __init__(self, platform: Platform = None, **datasource_json: dict) -> None:
        """The __init__ of the Datasource class.

        Args:
            datasource_json: The JSON for the Datasource.
            platform: The Platform object.
        """
        super().__init__(**datasource_json)
        self._platform = platform

    def model_dump(self, *, by_alias: bool = True, exclude_unset: bool = True, **kwargs: dict) -> dict:
        """Changing default parameters of model_dump to make sure that serialized json math API response.

        Args:
            by_alias: Whether to use alias names in serialization.
            exclude_unset: Whether to exclude unset fields from serialization.
            **kwargs: Additional keyword arguments to pass to the model_dump method.

        Returns:
           A dictionary representation of the model.
        """
        return super().model_dump(exclude_unset=exclude_unset, by_alias=by_alias, **kwargs)

    @property
    def datasource_id(self) -> str:
        """Returns id of datasource."""
        return self.metadata.asset_id

    @property
    def required_connection_properties(self) -> list[DatasourceTypeProperty]:
        """Get all required connection properties."""
        return [prty for prty in self.properties.connection if prty.required]


class DatasourceTypes(CollectionModel):
    """Collection of DatasourceType instances."""

    def __init__(self, platform: Platform) -> None:
        """The __init__ of the DatasourceType class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "metadata.asset_id"

    @override
    def __len__(self) -> int:
        datasources_json = self._platform._connections_api.get_datasources(
            params={
                "limit": 1,
            }
        ).json()
        return datasources_json["total_count"]

    def _request_parameters(self) -> list:
        request_params = []
        content_string = self._platform._connections_api.get_swagger().text
        request_path = f"/{self._platform._connections_api.url_path_datasource_types}"
        request_params.extend(get_params_from_swagger(content_string=content_string, request_path=request_path))
        return request_params

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "limit": 100,
            "offset": 0,
        }
        request_params_unioned: dict[str, Any] = request_params_defaults

        request_params_unioned.update(request_params)

        if "environment" in request_params_unioned:
            request_params_unioned["entity.environment"] = request_params_unioned["environment"]
            del request_params_unioned["environment"]
        if "perspective" in request_params_unioned:
            request_params_unioned["entity.perspective"] = request_params_unioned["perspective"]
            del request_params_unioned["perspective"]
        if "product" in request_params_unioned:
            request_params_unioned["entity.product"] = request_params_unioned["product"]
            del request_params_unioned["product"]

        response = self._platform._connections_api.get_datasources(
            params={k: v for k, v in request_params_unioned.items() if v is not None}
        ).json()

        if "next" in response:
            response["next"] = urllib.parse.parse_qs(urllib3.util.parse_url(response["next"]["href"]).query).get(
                "offset"
            )

        return CollectionModelResults(
            results=response,
            class_type=DatasourceType,
            response_bookmark="next",
            request_bookmark="offset",
            response_location="resources",
            constructor_params={"platform": self._platform},
        )

    @override
    def _paginate(self, **kwargs: dict) -> BaseModel:
        datasource_id = kwargs.pop("datasource_id", None)

        # to allow filter by datasource_id on DatasourceTypes
        # | endpoint dont support this param and it is a property (no way to set repr field)
        for ds in super()._paginate(**kwargs):
            if datasource_id is None or datasource_id == ds.datasource_id:
                yield ds


class ConnectionFile(BaseModel):
    created_at: str | None = Field(None, alias="createdAt", description="Date of creation of the file.", repr=False)
    url: str | None = Field(None, description="Signed URL of the file.", repr=False)
    hash: str | None = Field(None, description="Hash of the file.", repr=False)
    digest: str | None = Field(None, description="Digest of the file.", repr=False)
    file_name: str | None = Field(
        None, alias="fileName", description="Name of the file to be used by connections.", repr=True
    )

    model_config = ConfigDict(frozen=True)

    def __init__(self, platform: Platform = None, **file_json: dict) -> None:
        """The __init__ of the Datasource class.

        Args:
            file_json: The JSON for the ConnectionFile.
            platform: The Platform object.
        """
        super().__init__(**file_json)
        self._platform = platform

    def download(self, output: Path) -> requests.Response:
        """Download a file.

        Args:
            output: destination file path.

        Returns:
            A HTTP response.
        """
        return self._platform._connections_api.get_file(file_name=self.file_name, hash=self.hash, output=output)

    def _delete(self) -> requests.Response:
        """Delete a file.

        Returns:
            A HTTP response.
        """
        return self._platform._connections_api.delete_file(file_name=self.file_name, hash=self.hash)


class ConnectionFiles(CollectionModel):
    """Collection of ConnectionFile instances."""

    def __init__(self, platform: Platform) -> None:
        """The __init__ of the ConnectionFile class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "hash"

    @override
    def __len__(self) -> int:
        datasources_json = self._platform._connections_api.get_file_list(
            params={
                "limit": 0,
            }
        ).json()
        return datasources_json["connection_action_response"]["value"]["total_count"]

    def _request_parameters(self) -> list:
        request_params = []
        content_string = self._platform._connections_api.get_swagger().text
        request_path = f"/{self._platform._connections_api.url_path_connections}/files"
        request_params.extend(get_params_from_swagger(content_string=content_string, request_path=request_path))
        return request_params

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "limit": 100,
        }
        request_params_unioned: dict[str, Any] = request_params_defaults
        request_params_unioned.update(request_params)

        response = self._platform._connections_api.get_file_list(
            params={k: v for k, v in request_params_unioned.items() if v is not None}
        ).json()
        return CollectionModelResults(
            results=response["connection_action_response"]["value"],
            class_type=ConnectionFile,
            response_bookmark="",
            request_bookmark="",
            response_location="resources",
            constructor_params={"platform": self._platform},
        )
