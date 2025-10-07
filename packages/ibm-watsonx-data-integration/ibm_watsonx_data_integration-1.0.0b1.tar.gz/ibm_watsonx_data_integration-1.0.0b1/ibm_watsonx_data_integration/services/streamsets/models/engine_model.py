#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Engine Models."""

from copy import deepcopy
from functools import cached_property
from ibm_watsonx_data_integration.common.models import BaseModel
from ibm_watsonx_data_integration.services.streamsets.api.sdc_api import DataCollectorAPIClient
from pydantic import ConfigDict, Field, PrivateAttr
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models import Project
    from ibm_watsonx_data_integration.platform import Platform


class EngineMetrics(BaseModel):
    """StreamSets Engine Metrics."""

    cpu_load: float = Field(repr=True)
    memory_load: float = Field(repr=True)
    job_count: int = Field(repr=True)

    model_config = ConfigDict(frozen=True)


class EngineHealthMetadata(BaseModel):
    """StreamSets Engine Health Metadata."""

    status: str = Field(frozen=True, repr=True)
    last_heartbeat_time: int | None = Field(frozen=True, repr=False, default=None)
    last_status_updated_time: int | None = Field(repr=False, default=None)
    last_startup_time: int | None = Field(repr=False, default=None)
    last_registration_time: int | None = Field(repr=False, default=None)
    metrics: EngineMetrics | None = Field(repr=True, default=None)

    model_config = ConfigDict(frozen=True)


class EngineMetadata(BaseModel):
    """The model for CPD StreamSets Engine Metadata."""

    name: str = Field(repr=False)
    description: str = Field(repr=False)
    owner: str = Field(repr=False, default=None)
    owner_id: str = Field(repr=False)
    created: int = Field(repr=False)
    created_at: str = Field(repr=False)

    tags: list | None = Field(repr=False, default_factory=list)

    project_id: str = Field(repr=False)
    asset_id: str = Field(repr=True)
    asset_attributes: list | None = Field(repr=False)
    asset_state: str | None = Field(repr=False)
    asset_type: str | None = Field(repr=False)
    origin_country: str | None = Field(repr=False, default=None)
    catalog_id: str = Field(repr=False)
    rating: int | None = Field(repr=False)
    size: int | None = Field(repr=False)
    space_id: str = Field(repr=False, default=None)
    rov: dict | None = Field(repr=False)
    usage: dict | None = Field(repr=False)
    version: int | None = Field(repr=False)

    create_time: str | None = Field(repr=False, default=None)
    sandbox_id: str = Field(repr=False)
    creator_id: str = Field(repr=False)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class LibraryDefinitions(BaseModel):
    """An engine's library definition."""

    _expose: bool = PrivateAttr(default=False)

    schema_version: str = Field(alias="schemaVersion", repr=False)
    pipeline: list[dict] = Field(alias="pipeline", repr=False)
    pipeline_fragment: list[dict] = Field(alias="pipelineFragment", repr=False)
    pipeline_rules: list[dict] = Field(alias="pipelineRules", repr=False)
    stages: list[dict] = Field(alias="stages", repr=False)
    services: list[dict] = Field(alias="services", repr=False)
    rules_el_metadata: dict = Field(alias="rulesElMetadata", repr=False)
    el_catalog: Any = Field(alias="elCatalog", repr=False)
    runtime_configs: list[Any] = Field(alias="runtimeConfigs", repr=False)
    stage_icons: Any = Field(alias="stageIcons", repr=False)
    legacy_stage_libs: list[dict] = Field(alias="legacyStageLibs", repr=False)
    event_definitions: dict = Field(alias="eventDefinitions", repr=False)
    version: int | None = Field(alias="version", repr=False)
    executor_version: str | None = Field(alias="executorVersion", repr=False)
    category: Any | None = Field(alias="category", repr=False)
    category_label: str | None = Field(alias="categoryLabel", repr=False)
    stage_definition_map: dict | None = Field(alias="stageDefinitionMap", repr=False)
    stage_definition_minimal_list: list[dict] | None = Field(alias="stageDefinitionMinimalList", repr=False)

    def __init__(self, **library_definitions: any) -> None:
        """The __init__ for this class."""
        processed_definitions = self.process_library_definitions(library_definitions=library_definitions)
        super().__init__(**processed_definitions)

    @staticmethod
    def process_library_definitions(library_definitions: dict) -> dict:
        """Copied from https://shorturl.at/sfrgJ.

        This entire function essentially expands on stageDefinitionMap and stageDefinitionMinimalList
        to make the entire library definitions.

        This is only required for library definitions gotten from CPD and not from an engine as it is compressed \
        to contain all possible stage libraries.
        """
        processed_definitions = deepcopy(library_definitions)
        processed_definitions["stageDefinitionMap"] = dict()

        for key, stage_definition in library_definitions.get("stageDefinitionMap").items():
            processed_definitions["stageDefinitionMap"][key] = deepcopy(stage_definition)
            processed_definitions["stageDefinitionMap"][key]["services"] = list()

        processed_definitions["stages"] = list()
        for stage_definition_minimal in library_definitions.get("stageDefinitionMinimalList"):
            key = f"{stage_definition_minimal['name']}::{stage_definition_minimal['version']}"
            if key in library_definitions.get("stageDefinitionMap", {}):
                stage_definition = deepcopy(library_definitions.get("stageDefinitionMap")[key])
                stage_definition["library"] = stage_definition_minimal["library"]
                stage_definition["libraryLabel"] = stage_definition_minimal["libraryLabel"]
                processed_definitions["stages"].append(stage_definition)

        if not processed_definitions.get("injectedServices"):
            services = processed_definitions["services"]
            processed_definitions["injectedServices"] = True

            services_name_map = {}
            for service in services:
                services_name_map[service["provides"]] = service

            for key, stage_definition in library_definitions.get("stageDefinitionMap").items():
                if stage_definition.get("services"):
                    processed_definitions["stageDefinitionMap"][key]["services"] = []
                    for service in stage_definition.get("services"):
                        service_definition = deepcopy(services_name_map[service["service"]])
                        service_definition["configuration"] = service["configuration"]
                        processed_definitions["stageDefinitionMap"][key]["services"].append(service_definition)

        return processed_definitions

    @classmethod
    def for_engine_version(cls, platform: "Platform", engine_version: str) -> "LibraryDefinitions":
        """Returns the library definitions for a particular engine version, includes all possible stage libraries.

        Args:
            platform: Instance of platform to get the definitions from.
            engine_version: The engine version for which library definitions need to be fetched.

        Returns:
            An instance of the LibraryDefinitions class.
        """
        return cls(
            **platform._environment_api.get_library_definitions_for_engine_version(engine_version=engine_version).json()
        )


class Engine(BaseModel):
    """The Model for Engine."""

    EXPOSED_DATA_PATH = {
        "entity.streamsets_engine": {},
    }

    metadata: EngineMetadata = Field(repr=True)

    registration_status: str | None = Field(repr=False)
    registration_time: int = Field(repr=False)
    reported_engine_version: str = Field(repr=False, default=None)
    reported_build_time: int = Field(repr=False, default=None)
    reported_build_sha: str = Field(repr=False, default=None)
    reported_java_vendor: str | None = Field(repr=False, default=None)
    reported_java_version: str = Field(repr=False, default=None)
    reported_os_name: str = Field(repr=False, default=None)
    reported_os_arch: str = Field(repr=False, default=None)
    reported_os_version: str = Field(repr=False, default=None)
    last_startup_time: int = Field(repr=True, default=None)
    engine_type: str = Field(repr=True)
    url: str = Field(repr=True, default=None)
    streamsets_environment_asset_id: str = Field(repr=False)
    health: EngineHealthMetadata | None = Field(repr=False, default=None)

    model_config = ConfigDict(frozen=True)

    def __init__(self, platform: "Platform" = None, project: "Project" = None, **engine_json: dict) -> None:
        """The __init__ of the Engine class.

        Args:
            platform: The Platform object.
            project: The Project object.
            engine_json: The JSON for the Engine.
        """
        super().__init__(**engine_json)
        self._platform = platform
        self._project = project

    def __str__(self) -> str:
        """Custom __str__ to include the product property.

        Returns:
            A string representation of class.
        """
        return f"Engine(name={self.metadata.name}, engine_id={self.metadata.asset_id}, \
            project_id={self.metadata.project_id})"

    @property
    def engine_id(self) -> str:
        """Returns engine asset_id."""
        return self.metadata.asset_id

    @cached_property
    def api_client(self) -> DataCollectorAPIClient:
        """The API Client connected directly to the engine."""
        return DataCollectorAPIClient(auth=self._platform._engine_api._auth, engine_url=self.url)

    @cached_property
    def library_definitions(self) -> LibraryDefinitions:
        """Library Definitions of the Engine."""
        return LibraryDefinitions(**self.api_client.get_library_definitions().json())
