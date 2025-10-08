#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Environment Models."""

import json
import requests
from ibm_watsonx_data_integration.common.json_patch_format import prepare_json_patch_payload
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.services.streamsets.models import Engine
from pydantic import UUID4, Field, PrivateAttr, field_serializer, field_validator
from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models import Project
    from ibm_watsonx_data_integration.platform import Platform


class EnvironmentMetadata(BaseModel):
    """The model for CPD StreamSets Environment Metadata."""

    name: str
    description: str = Field(default="")
    owner_id: str = Field(repr=False, frozen=True)
    create_time: str = Field(repr=False, frozen=True)
    project_id: UUID4 | str = Field(repr=False, frozen=True)
    environment_id: UUID4 | str = Field(alias="asset_id", repr=True, frozen=True)
    asset_attributes: list | None = Field(repr=False, frozen=True)
    asset_state: str | None = Field(repr=False, frozen=True)
    asset_type: str | None = Field(repr=False, frozen=True)
    catalog_id: UUID4 | str | None = Field(repr=False, frozen=True)
    version: float | None = Field(repr=False, frozen=True)

    _expose: bool = PrivateAttr(default=False)

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


class EngineProperties(BaseModel):
    """The model for engine properties that are included in environments."""

    stagelibs_blocklist: list | None = Field(alias="system.stagelibs.blocklist", default=None)

    @field_validator("stagelibs_blocklist", mode="before")
    def split_string(cls, value: str | None) -> list | None:
        """Splits a stagelibs_blocklist by commas during instance creation."""
        if value is None:
            return None
        return value.split(",")

    @field_serializer("stagelibs_blocklist")
    def serialize_stagelibs(self, stagelibs: list | None) -> str | None:
        """Serializes a list of stage libraries into a comma-separated string (original format)."""
        if stagelibs is None:
            return None
        return ",".join(stagelibs)


class Environment(BaseModel):
    """The model for CPD StreamSets Environment."""

    EXPOSED_DATA_PATH = {"entity.streamsets_environment": {}}
    metadata: EnvironmentMetadata | None = Field(repr=True, default=None)
    engine_type: str = Field(repr=False)
    engine_version: str = Field(repr=False)
    engine_properties: EngineProperties | None = Field(repr=False, default_factory=EngineProperties)
    log4j2_properties: dict[str, str] = Field(repr=False, default_factory=dict)
    external_resource_asset: dict | None = Field(repr=False, default_factory=dict)
    stage_libs: list[str] | None = Field(repr=False, default_factory=list)
    jvm_options: list[str] | None = Field(repr=False, default_factory=list)
    max_cpu_load: float | None = Field(repr=False, default=None)
    max_memory_used: float | None = Field(repr=False, default=None)
    max_jobs_running: int | None = Field(repr=False, default=None)
    cpus_to_allocate: float | None = Field(repr=False, default=None)
    engine_heartbeat_interval: int | None = Field(repr=False, default=None)
    href: str | None = Field(repr=False, exclude=True, default=None)
    engine_statuses: dict[str, str] = Field(repr=False, default_factory=dict)

    def __init__(self, project: "Project", platform: Optional["Platform"] = None, **env_json: dict) -> None:
        """The __init__ of the Environment class.

        Args:
            env_json: The JSON for the Service.
            platform: The Platform object.
            project: The Project object.
        """
        super().__init__(**env_json)
        self._platform = platform
        self._project = project
        self._origin = self.model_dump()

    @staticmethod
    def _create(
        project: "Project",
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
    ) -> "Environment":
        if engine_version is None:
            engine_version = project._platform.available_engine_versions[0]

        params = locals()
        params.pop("project")

        env_json = {
            "name": params.pop("name"),
            "description": params.pop("description"),
            "streamsets_environment": {k: v for k, v in params.items() if v is not None},
        }
        query_params = {
            "project_id": project.metadata.guid,
        }
        api_response = project._platform._environment_api.create_environment(  # noqa
            data=json.dumps(env_json), params=query_params
        )
        payload = api_response.json()
        payload.pop("asset_id", None)
        return Environment(project=project, platform=project._platform, **payload)

    def _update(self) -> requests.Response:
        query_params = {
            "project_id": self._project.metadata.guid,
        }
        payload = prepare_json_patch_payload(self.origin, self.model_dump())
        return self._platform._environment_api.patch_environment(  # noqa
            environment_id=self.environment_id, data=payload, params=query_params
        )

    def _delete(self) -> requests.Response:
        query_params = {"project_id": self._project.metadata.guid}
        return self._platform._environment_api.delete_environment(  # noqa
            environment_id=self.environment_id, params=query_params
        )

    @property
    def origin(self) -> dict:
        """Returns origin model dump."""
        return self._origin

    @property
    def environment_id(self) -> str:
        """Returns id of environment."""
        return self.metadata.environment_id

    def get_installation_command(self, pretty: bool = True, foreground: bool = False) -> str | None:
        """Returns the installation command for the environment."""
        query_params = {"project_id": self.metadata.project_id, "pretty": pretty, "foreground": foreground}
        command = self._platform._environment_api.get_docker_run_command(
            environment_id=self.environment_id, params=query_params
        )
        if command.status_code == 200:
            return command.text

    @property
    def engines(self) -> list[Engine]:
        """Returns list of Engines."""
        query_params = {
            "project_id": self.metadata.project_id,
        }
        response = self._platform._environment_api.get_engines(self.environment_id, params=query_params)  # noqa
        return [Engine(platform=self._platform, **data) for data in response.json()["streamsets_engines"]]

    def add_stage_libraries(self, stage_libs: list) -> None:
        """Allows to add stage libraries to the environment.

        Args:
            stage_libs: List of stage libraries to add.
        """
        self.stage_libs.extend(stage_libs)
        self.stage_libs = sorted(set(self.stage_libs))

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


class Environments(CollectionModel):
    """Collection of Environments instances."""

    def __init__(self, platform: "Platform", project: "Project") -> None:
        """The __init__ of the Environment class.

        Args:
            platform: The Platform object.
            project: The Project object.
        """
        super().__init__(platform=platform)
        self.unique_id = "metadata.environment_id"
        self._project = project

    def __len__(self) -> int:
        """Total amount of environments."""
        params = {"project_id": self._project.metadata.guid, "limit": 0}
        return self._platform._environment_api.get_environments(params=params).json().get("total_count")

    def _request_parameters(self) -> list:
        return ["environment_id", "project_id", "limit", "start", "sort"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {"project_id": self._project.metadata.guid, "limit": 100, "start": None, "sort": None}

        request_params_unioned: dict[str, Any] = request_params_defaults
        request_params_unioned.update(request_params)
        if isinstance(value := request_params_unioned.get("start"), dict):
            request_params_unioned["start"] = parse_qs(urlparse(value.get("href")).query)["start"][0]
        if "environment_id" in request_params:
            response_json = self._platform._environment_api.get_environment(
                environment_id=request_params["environment_id"],
                params={k: v for k, v in request_params_unioned.items() if v is not None},
            ).json()
            response = {"streamsets_environments": [response_json]}
        else:
            response = self._platform._environment_api.get_environments(
                params={k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()
        return CollectionModelResults(
            results=response,
            class_type=Environment,
            response_bookmark="next",
            request_bookmark="start",
            response_location="streamsets_environments",
            constructor_params={"platform": self._platform, "project": self._project},
        )
