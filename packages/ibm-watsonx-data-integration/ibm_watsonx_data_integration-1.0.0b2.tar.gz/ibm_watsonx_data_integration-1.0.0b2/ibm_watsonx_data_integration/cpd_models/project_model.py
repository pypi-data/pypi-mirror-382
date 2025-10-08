#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Project Models."""

import json
import requests
import warnings
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.common.utils import get_params_from_swagger
from ibm_watsonx_data_integration.cpd_models import (
    Connection,
    Connections,
    DatasourceType,
    Job,
    Jobs,
)
from ibm_watsonx_data_integration.cpd_models.flow_model import Flow
from ibm_watsonx_data_integration.cpd_models.flows_model import Flows
from ibm_watsonx_data_integration.services.streamsets.models import (
    Engine,
    Environment,
    Environments,
    StreamsetsConnection,
    StreamsetsFlow,
)
from ibm_watsonx_data_integration.services.streamsets.models.flow_model import FlowValidationError
from pydantic import ConfigDict, Field, PrivateAttr
from typing import TYPE_CHECKING, Any, ClassVar, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class ProjectMetadata(BaseModel):
    """Model for metadata in a project."""

    guid: str = Field(repr=True)
    url: str = Field(repr=False)
    created_at: str | None = Field(repr=False)
    updated_at: str | None = Field(repr=False)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class Storage(BaseModel):
    """Model for Storage details in a project."""

    type: str
    guid: str = Field(frozen=True)
    properties: dict[str, Any]
    _expose: bool = PrivateAttr(default=False)


class Scope(BaseModel):
    """Model for Scope details in a project."""

    bss_account_id: str = Field(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class Project(BaseModel):
    """The Model for Projects."""

    metadata: ProjectMetadata = Field(repr=True)

    name: str = Field(repr=True)
    description: str = Field(repr=False)
    type: str | None = Field(repr=False)
    generator: str | None = Field(repr=False)
    public: bool | None = Field(repr=False)
    creator: str | None = Field(repr=False)
    tags: list | None = Field(default_factory=list, repr=False)

    storage: Storage | None = Field(repr=False)
    scope: Scope | None = Field(repr=False)

    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity": {}}

    def __init__(self, platform: Optional["Platform"] = None, **project_json: dict) -> None:
        """The __init__ of the Project class.

        Args:
            platform: The Platform object.
            project_json: The JSON for the Service.
        """
        super().__init__(**project_json)
        self._platform = platform
        self._inital_tags = [] if not hasattr(self, "tags") else list(self.tags)

    def _update_tags(self) -> None:
        """Updates tags of the Project."""
        initial_tags = set(self._inital_tags)
        current_tags = set(self.tags)

        body = []

        tags_to_delete = initial_tags - current_tags
        if tags_to_delete:
            body.append({"op": "remove", "tags": list(tags_to_delete)})

        tags_to_add = current_tags - initial_tags
        if tags_to_add:
            body.append({"op": "add", "tags": list(tags_to_add)})

        if body:
            self._inital_tags = self.tags
            self._platform._project_api.update_tags(self.metadata.guid, json.dumps(body))

    @staticmethod
    def _create(
        platform: "Platform",
        name: str,
        description: str = "",
        tags: list = None,
        public: bool = False,
        project_type: str = "wx",
    ) -> "Project":
        cloud_storage = platform._get_cloud_storage()
        cloud_storage_guid = cloud_storage["guid"]
        cloud_storage_id = cloud_storage["id"]

        data = {
            "name": name,
            "description": description,
            "generator": "watsonx-di-sdk",
            "public": public,
            "tags": ["sdk-tags"] if not tags else tags,
            "storage": {
                "type": "bmcos_object_storage",
                "guid": cloud_storage_guid,
                "resource_crn": cloud_storage_id,
            },
            "type": project_type,
        }

        response = platform._project_api.create_project(json.dumps(data))
        location = response.json()["location"]
        project_id = location.split("/")[-1]

        project_json = platform._project_api.get_project(project_id).json()
        return Project(platform=platform, **project_json)

    def _update(self) -> requests.Response:
        # Update tags
        self._update_tags()

        # Update rest of project
        data = {"name": self.name, "description": self.description, "public": self.public}

        project_json = self.model_dump()
        if "catalog" in project_json:
            data["catalog"] = {"guid": project_json["catalog"]["guid"], "public": project_json["catalog"]["public"]}

        data = json.dumps(data)
        return self._platform._project_api.update_project(id=self.metadata.guid, data=data)

    def _delete(self) -> requests.Response:
        return self._platform._project_api.delete_project(self.metadata.guid)

    @property
    def jobs(self) -> Jobs:
        """Retrieves jobs associated with the project.

        Returns:
            A list of Jobs within the project.
        """
        return Jobs(platform=self._platform, project=self)

    def create_job(
        self,
        name: str,
        flow: Flow,
        configuration: dict[str, Any] | None = None,
        description: str | None = None,
        job_parameters: dict[str, Any] | None = None,
        retention_policy: dict[str, int] | None = None,
        parameter_sets: list[dict[str, str]] | None = None,
        schedule: str | None = None,
        schedule_info: dict[str, Any] | None = None,
    ) -> Job:
        """Create Job for given asset.

        Args:
            name: Name for a Job.
            flow: A reference to the flow for which the job will be created.
            configuration: Environment variables for a Job.
            description: Job description.
            job_parameters: Parameters use internally by a Job.
            retention_policy: Retention policy for a Job.
            parameter_sets: Parameter sets for a Job.
            schedule: Crone string.
            schedule_info: Schedule info for a Job.

        Returns:
            A Job instance.

        Raises:
            TypeError: If both asset_ref and asset_ref_type are provided, or if neither is provided
        """
        return Job._create(
            self,
            name,
            flow,
            configuration,
            description,
            job_parameters,
            retention_policy,
            parameter_sets,
            schedule,
            schedule_info,
        )

    def delete_job(self, job: Job) -> requests.Response:
        """Allows to delete specified Job within project.

        Args:
            job: Instance of a Job to delete.

        Returns:
            A HTTP response. If it is 204, then the operation completed successfully.
        """
        return job._delete()

    def update_job(self, job: Job) -> requests.Response:
        """Allows to update specified Job within a project.

        Args:
            job: Instance of a Job to update.

        Returns:
            A HTTP response. If it is 200, then the operation completed successfully.
        """
        return job._update()

    @property
    def environments(self) -> Environments:
        """Retrieves environments associated with the project.

        Returns:
            A list of Environments within the project.
        """
        return Environments(platform=self._platform, project=self)

    def create_environment(
        self,
        *,
        name: str,
        engine_version: str | None = None,
        description: str = None,
        engine_type: str = "data_collector",
        engine_properties: dict = None,
        log4j2_properties: dict = None,
        external_resource_asset: dict = None,
        stage_libs: list = None,
        jvm_options: list = None,
        max_cpu_load: float = None,
        max_memory_used: float = None,
        max_jobs_running: int = None,
        engine_heartbeat_interval: int = None,
        cpus_to_allocate: float = None,
    ) -> Environment:
        """Allows to create a new Environment within project.

        All of not set parameters will be skipped and set with default values provided by backed.

        Args:
            name: Name of the environment.
            description: Description of the environment.
            engine_type: Type of the engine.
            engine_version: Version of the engine. Default is the latest engine version.
            engine_properties: Properties of the engine.
            external_resource_asset: External resources.
            log4j2_properties: Log4j2 properties.
            stage_libs: Stage libraries.
            jvm_options: JVM options.
            max_cpu_load: Maximum CPU load.
            max_memory_used: Maximum memory used.
            max_jobs_running: Maximum jobs running.
            engine_heartbeat_interval: Engine heartbeat interval.
            cpus_to_allocate: Number of CPU used.

        Returns:
            The created environment.
        """
        return Environment._create(
            self,
            name,
            engine_version,
            description,
            engine_type,
            engine_properties,
            log4j2_properties,
            external_resource_asset,
            stage_libs,
            jvm_options,
            max_cpu_load,
            max_memory_used,
            max_jobs_running,
            engine_heartbeat_interval,
            cpus_to_allocate,
        )

    def delete_environment(self, environment: Environment) -> requests.Response:
        """Allows to delete specified Environment within a Project.

        Args:
            environment: Instance of an Environment to delete.

        Returns:
            A HTTP response.
        """
        return environment._delete()

    def update_environment(self, environment: Environment) -> requests.Response:
        """Allows to update specified Environment within a Project.

        Args:
            environment: Instance of an Environment to update.

        Returns:
            A HTTP response.
        """
        return environment._update()

    @property
    def flows(self) -> Flows:
        """Returns Flows from the Project."""
        return Flows(project=self)

    def delete_flow(self, flow: Flow) -> requests.Response:
        """Delete a Flow.

        Args:
            flow: The Flow object.

        Returns:
            A HTTP response.
        """
        return flow._delete()

    def create_flow(
        self, name: str, environment: Environment | None = None, description: str = "", flow_type: str = "streamsets"
    ) -> Flow:
        """Creates a Flow.

        Args:
            name: The name of the flow.
            environment: The environment which will be used to run this flow.
            description: The description of the flow.
            flow_type: The type of flow (must be registered in Flow.flow_registry).

        Returns:
            The created Flow subclass instance (StreamsetsFlow by default).

        """
        try:
            flow = Flow._flow_registry[flow_type]
        except ValueError:
            raise TypeError(f"Flow type '{flow_type}' is not supported. Available: {list(Flow._flow_registry)}")

        flow = flow._create(
            project=self, name=name, environment=environment, description=description, flow_type=flow_type
        )
        return flow

    def update_flow(self, flow: Flow) -> requests.Response:
        """Update a Flow.

        Args:
            flow: The Flow object.

        Returns:
            A HTTP response.
        """
        return flow._update()

    def duplicate_flow(self, flow: Flow, name: str, description: str = "") -> Flow:
        """Duplicate a Flow.

        Args:
            flow: The Flow.
            name: The name of the flow.
            description: The description of the flow.

        Returns:
            A copy of passed flow.
        """
        return flow._duplicate(name, description)

    def validate_flow(self, flow: StreamsetsFlow) -> list[FlowValidationError]:
        """Validates a flow.

        Args:
            flow: The Flow to validate.

        Returns:
            A `list` of `FlowValidationError` containing issues.
        """
        warnings.warn(
            "Project.validate_flow() is now deprecated. Use StreamsetsFlow.validate() instead.", DeprecationWarning
        )
        return flow.validate()

    @property
    def engines(self) -> list[Engine]:
        """Returns a list of Engines within project."""
        # TODO: replace with CollectionModel when implemented
        query_params = {
            "project_id": self.metadata.guid,
        }
        api_response = self._platform._engine_api.get_engines(params=query_params).json()

        return [
            Engine(platform=self._platform, project=self, **engine_json)
            for engine_json in api_response.get("streamsets_engines", [])
        ]

    def get_engine(self, engine_id: str) -> Engine:
        """Retrieve an engine by its engine_id.

        Args:
            engine_id (str): The asset_id of the engine to retrieve.

        Returns:
            Engine: The retrieved engine.

        Raises:
            HTTPError: If the request fails.
        """
        query_params = {
            "project_id": self.metadata.guid,
        }
        api_response = self._platform._engine_api.get_engine(engine_id=engine_id, params=query_params)
        return Engine(platform=self._platform, project=self, **api_response.json())

    def delete_engine(self, engine: Engine) -> requests.Response:
        """Allows to delete specified Engine within project.

        Args:
            engine: Instance of an Engine to delete.

        Returns:
            A HTTP response.
        """
        query_params = {"project_id": self.metadata.guid}
        return self._platform._engine_api.delete_engine(engine_id=engine.engine_id, params=query_params)

    @property
    def connections(self) -> Connections:
        """Retrieves connections associated with the project.

        Returns:
            A Connections object.
        """
        return Connections(platform=self._platform, project=self)

    def create_connection(
        self,
        name: str,
        datasource_type: DatasourceType,
        description: str | None = None,
        properties: dict | None = None,
        test: bool = True,
    ) -> Connection:
        """Create a Connection.

        Args:
            name: name for the new connection.
            description: description for the new connection.
            datasource_type: type of the datasource.
            properties: properties of the new connection.
            test: whether to test the connection before saving it.
                  If true and validation cannot be estabilished, connection will not be saved.

        Returns:
            Created Connection object.
        """
        return Connection._create(self, name, datasource_type, description, properties, test)

    def delete_connection(self, connection: Connection) -> requests.Response:
        """Remove the Connection.

        Args:
            connection: connection to delete

        Returns:
            A HTTP response.
        """
        return connection._delete()

    def update_connection(self, connection: Connection, test: bool = True) -> requests.Response:
        """Update the Connection.

        Args:
            connection: connection to update
            test: whether to test the connection before saving it.
                  If true and validation cannot be estabilished, connection will not be saved.

        Returns:
            A HTTP response.
        """
        return connection._update(test=test)

    def copy_connection(self, connection: Connection) -> Connection:
        """Update the Connection.

        Args:
            connection: connection to copy

        Returns:
            Copied Connection object.
        """
        return connection._copy()

    @property
    def _streamsets_connections(self) -> list[StreamsetsConnection]:
        """Retrieves StreamSets connections associated with the project.

        Returns:
            A list of StreamsetsConnection within the project.
        """
        connections_json = self._platform._streamsets_flow_api.get_streamsets_connections(
            params={
                "project_id": self.metadata.guid,
            },
        ).json()

        return [
            StreamsetsConnection(
                platform=self._platform,
                project=self,
                **{
                    "entity": {
                        "datasource_type": connection["datasource_type"],
                        "name": connection["name"],
                    },
                    "metadata": {
                        "asset_id": connection["asset_id"],
                    },
                },
            )
            for connection in connections_json.get("connections", list())
        ]

    def _get_streamsets_connection(
        self, connection_id: str, version: str | None = None, type: str | None = None
    ) -> StreamsetsConnection:
        """Retrieves StreamSets connection by id associated with the project.

        Args:
            connection_id: Id of the connection asset to retrieve.
            version: Connection version.
            type: Connection type.

        Returns:
            Retrieved StreamsetsConnection object.
        """
        params = {
            "project_id": self.metadata.guid,
        }
        if version:
            params["connection_version"] = version
        if type:
            params["connection_type"] = type

        connection_json = self._platform._streamsets_flow_api.get_streamsets_connection(
            connection_id=connection_id,
            params=params,
        ).json()

        # NOTE: connection_json has also 'alternative_mapping' reserved for future use
        #       this object is stripped for now as it is filled with nulls
        return StreamsetsConnection(platform=self._platform, project=self, **connection_json["connection"])


class Projects(CollectionModel):
    """Collection of Project instances."""

    def __init__(self, platform: "Platform") -> None:
        """The __init__ of the Projects class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "metadata.guid"

    def __len__(self) -> int:
        """Total amount of projects."""
        return self._platform._project_api.get_projects_total().json()["total"]

    def _request_parameters(self) -> list:
        request_params = ["project_id"]
        content_string = self._platform._project_api.get_swagger().content.decode("utf-8")
        request_path = f"/{self._platform._project_api.url_path}"
        request_params.extend(get_params_from_swagger(content_string=content_string, request_path=request_path))
        return request_params

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "project_id": None,
            "bss_acount_id": None,
            "type": None,
            "member": None,
            "roles": None,
            "tag_names": None,
            "name": None,
            "match": None,
            "project_ids": None,
            "include": "name,fields,members,tags,settings",
            "limit": 100,
            "bookmark": None,
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)
        project_id = request_params_unioned.get("project_id")

        if project_id:
            response = self._platform._project_api.get_project(project_id).json()
            response = {"resources": [response]}
        else:
            response = self._platform._project_api.get_projects(
                params={k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()
        return CollectionModelResults(
            response,
            Project,
            "bookmark",
            "bookmark",
            "resources",
            {"platform": self._platform},
        )
