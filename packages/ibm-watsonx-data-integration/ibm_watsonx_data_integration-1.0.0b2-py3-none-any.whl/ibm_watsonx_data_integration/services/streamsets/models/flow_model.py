#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing StreamSets Flow Models."""

import inflection
import json
import logging
import re
import requests
import textwrap
from collections import defaultdict, namedtuple
from copy import deepcopy
from functools import cached_property
from ibm_watsonx_data_integration.common.constants import SUPPORTED_FLOWS
from ibm_watsonx_data_integration.common.exceptions import (
    StageNotFoundError,
    UniqueStageNameNotFoundError,
)
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.cpd_models.flow_model import Flow, PayloadExtender
from ibm_watsonx_data_integration.services.streamsets.data import create_pipeline_definition_for_new_flow
from ibm_watsonx_data_integration.services.streamsets.exceptions import StageDefinitionNotFound
from ibm_watsonx_data_integration.services.streamsets.models import Engine, Environment
from ibm_watsonx_data_integration.services.streamsets.models.configuration import Configuration
from ibm_watsonx_data_integration.services.streamsets.models.engine_model import LibraryDefinitions
from pydantic import ConfigDict, Field, PrivateAttr
from typing import TYPE_CHECKING, Any, ClassVar
from typing_extensions import override
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models import Project
    from ibm_watsonx_data_integration.platform import Platform

logger = logging.getLogger()

StageClassDefault = namedtuple("StageClassDefaults", ["class_name", "attributes"])
StageData = namedtuple("StageData", ["definition", "instance"])
StageConfigurationProperty = namedtuple("StageConfigurationProperty", ["config_name"])
StageServiceProperty = namedtuple("StageServiceProperty", ["service_name", "config_name"])


class Stage(BaseModel):
    """Class for a stage."""

    instance_name: str = Field(alias="instanceName", repr=False, frozen=True)
    library: str = Field(alias="library", repr=False, frozen=True)
    stage_name: str = Field(alias="stageName", repr=False, frozen=True)
    stage_version: str = Field(alias="stageVersion", repr=False, frozen=True)
    ui_info: dict = Field(alias="uiInfo", repr=False, frozen=True)
    input_lanes: list[str] = Field(alias="inputLanes", repr=False, default=list())
    output_lanes: list[str] = Field(alias="outputLanes", repr=False, default=list())
    event_lanes: list[str] = Field(alias="eventLanes", repr=False, default=list())
    services_data: list[dict] = Field(alias="services", repr=False)
    configuration_data: list[dict] = Field(alias="configuration", repr=False)

    def __init__(
        self,
        pipeline_definition: "PipelineDefinition",
        output_streams: int = 0,
        supported_connection_types: list[str] | None = None,
        attributes: dict | None = None,
        **stage_json: any,
    ) -> None:
        """The __init__ for the class.

        Args:
            pipeline_definition: Pipeline Definition of the flow this stage belongs to
            output_streams: The number of output streams for the stage, if 0 then it is inferred from output lanes
            supported_connection_types: The connection types supported by the stage.
            attributes: Any attributes specific to the stage.
            stage_json: All other properties used by BaseModel
        """
        super().__init__(**stage_json)
        self._attributes = attributes or {}
        self._pipeline_definition = pipeline_definition

        self._supported_connection_types = supported_connection_types
        self._output_streams = output_streams
        # for adding outputs to the stage
        self._output_lane_idx = 0
        # output lanes need to be set sometimes
        if self.output_lanes:
            self._output_streams = len(self.output_lanes)
        else:
            for i in range(self._output_streams):
                self.output_lanes.append(f"{self.instance_name}OutputLane{str(uuid4())}".replace("-", "_"))
        # create the configuration and service configurations
        configurations = [self.configuration_data]
        self._services = dict()
        for service in self.services_data:
            self._services[service["service"]] = Configuration(service["configuration"])
            configurations.append(service["configuration"])
        self._configurations = Configuration(configurations, id_to_remap=self._create_id_to_remap())

        # Add a docstring to show stage attributes when help() is run on a stage instance.
        # Attributes will be printed in two columns.
        attrs_ = list(sorted(self._attributes.keys()))
        split = int(len(attrs_) / 2)
        self.__class__.__doc__ = textwrap.dedent(
            """
            {class_name}: {label}
            Attributes:
            {attributes}
            """
        ).format(
            class_name=self.__class__.__name__,
            label=self.stage_name,
            attributes="\n".join(f"{first:<60}{second:<60}" for first, second in zip(attrs_[:split], attrs_[split:])),
        )

    def _create_id_to_remap(self) -> dict:
        """Constructs a mapping of stage_configuration_backend_name: stage_configuration_human_readable_name."""
        id_to_remap = {}
        for name, value in self._attributes.items():
            config_properties = [value] if not isinstance(value, list) else value
            for config_property in config_properties:
                id_to_remap[name] = config_property.config_name
        return id_to_remap

    @property
    def configuration(self) -> Configuration:
        """The stage's configurations."""
        return self._configurations

    def _add_output(self, *stages: "Stage", is_event: bool = False, predicate: dict = None) -> None:
        """Adds stages to the output of this stage."""
        if not stages:
            raise ValueError("Stages cannot be empty.")
        if predicate and not isinstance(self, StageWithPredicates):
            raise TypeError("Cannot pass predicate argument for a stage without predicates.")
        if is_event and predicate:
            raise ValueError("Choose one of is_event or predicate.")
        if (
            predicate
            and not predicate.get("outputLane")
            and not next(output_lane for output_lane in self.output_lanes if output_lane == predicate.get("outputLane"))
        ):
            raise TypeError("Pass a valid predicate with an existing output lane.")
        if not predicate and not is_event and self._output_lane_idx >= self._output_streams:
            raise ValueError("Stage does not produce any outputs.")

        if is_event:
            if not self.event_lanes:
                lane = f"{self.instance_name}_EventLane"
                self.event_lanes.append(lane)
            else:
                lane = self.event_lanes[0]
        elif predicate:
            lane = predicate.get("outputLane")
        else:
            lane = self.output_lanes[self._output_lane_idx]
            if self._output_lane_idx < self._output_streams - 1:
                self._output_lane_idx += 1
        for stage in stages:
            stage.input_lanes.append(lane)

    def connect_output_to(self, *stages: "Stage", predicate: dict = None) -> None:
        """Connect other stages to the output of this stage.

        Args:
            stages: Stages to connect to this stage
            predicate: Whether to use any specific predicate when connecting (only applicable to some stages)
        """
        self._add_output(*stages, is_event=False, predicate=predicate)

    def connect_input_to(self, *stages: "Stage", predicate: dict = None) -> None:
        """Connect other stages to the input of this stage.

        Args:
            stages: Stages to connect to this stage
            predicate: Whether to use any specific predicate when connecting
        """
        for stage in stages:
            stage.connect_output_to(self, predicate=predicate)

    def connect_event_to(self, *stages: "Stage") -> None:
        """Connect other stages to the event output of this stage.

        Args:
            stages: Stages to connect to this stage
        """
        self._add_output(*stages, is_event=True)

    def _remove_input(self, *stages: "Stage", is_event: bool = False) -> None:
        """Disconnect the inputs from this stage."""
        lane_identifier = "_EventLane" if is_event else "OutputLane"
        instance_names = [stage.instance_name for stage in stages]
        self.input_lanes = list(
            filter(lambda lane: lane.split(lane_identifier)[0] not in instance_names, self.input_lanes)
        )

    def disconnect_input_from(self, *stages: "Stage", is_event: bool = False) -> None:
        """Disconnect the input of this stage from the output of the provided stages.

        Args:
            stages: Stages to disconnect from this stage.
            is_event: Whether we are disconnecting events.
        """
        self._remove_input(*stages, is_event=is_event)

    def disconnect_output_from(self, *stages: "Stage") -> None:
        """Disconnect the output of this stage from the provided stages.

        Args:
            stages: Stages to disconnect from this stage.
        """
        for stage in stages:
            stage.disconnect_input_from(self)

    def disconnect_event_from(self, *stages: "Stage") -> None:
        """Disconnect the event output of this stage from the provided stages.

        Args:
            stages: Stages to disconnect from this stage.
        """
        for stage in stages:
            stage.disconnect_input_from(self, is_event=True)

    @property
    def outputs(self) -> list:
        """All the stages connected to this stages output."""
        return list(
            filter(
                lambda stage: any([lane in self.output_lanes for lane in stage.input_lanes]),
                self._pipeline_definition.stages,
            )
        )

    @property
    def inputs(self) -> list:
        """All the stages connected to this stages input."""
        return list(
            filter(
                lambda stage: any(
                    [(lane in stage.output_lanes) or (lane in stage.event_lanes) for lane in self.input_lanes]
                ),
                self._pipeline_definition.stages,
            )
        )

    @property
    def events(self) -> list:
        """All the stages connected to this stages event output."""
        return list(
            filter(
                lambda stage: any([lane in self.event_lanes for lane in stage.input_lanes]),
                self._pipeline_definition.stages,
            )
        )

    @property
    def type(self) -> str:
        """The type of this stage."""
        return self.ui_info.get("stageType")

    def __getattr__(self, name: str) -> any:
        """Get an attribute of this stage, includes any special attributes for this stage."""
        if name != "_attributes" and name in self._attributes:
            attr_value = self._attributes.get(name)
            config_properties = [attr_value] if not isinstance(attr_value, list) else attr_value

            for config_property in config_properties:
                if (
                    isinstance(config_property, StageConfigurationProperty)
                    and config_property.config_name in self.configuration
                ):
                    return self.configuration[config_property.config_name]
                elif (
                    isinstance(config_property, StageServiceProperty) and config_property.service_name in self._services
                ):
                    return self._services[config_property.service_name][config_property.config_name]

        return super().__getattr__(name)

    def __setattr__(self, name: str, value: any) -> None:
        """Set an attribute of this stage, includes any special attributes for this stage."""
        if name != "_attributes" and name in self._attributes:
            attr_value = self._attributes.get(name)
            config_properties = [attr_value] if not isinstance(attr_value, list) else attr_value

            found_config = False
            for config_property in config_properties:
                if (
                    isinstance(config_property, StageConfigurationProperty)
                    and config_property.config_name in self.configuration
                ):
                    found_config = True
                    self.configuration[config_property.config_name] = value
                elif (
                    isinstance(config_property, StageServiceProperty) and config_property.service_name in self._services
                ):
                    found_config = True
                    self._services[config_property.service_name][config_property.config_name] = value

            if not found_config:
                raise AttributeError(f"'{type(self).__name__!r}' has no attribute '{name!r}'.")
        else:
            super().__setattr__(name, value)

    def __dir__(self) -> list[str]:
        """The dir of a stage."""
        return sorted(list(super().__dir__()) + list(self._attributes.keys()))

    def __str__(self) -> str:
        """This stage's representation as a string."""
        from_pydantic = super().__str__()
        return self.instance_name + from_pydantic[len(self.__class__.__name__) :]

    def __repr__(self) -> str:
        """The stage's representation."""
        return str(self)


class StageWithPredicates(Stage):
    """Class for a stage with predicates."""

    def __init__(self, variable_output_drive: str, *args: any, **kwargs: any) -> None:
        """The __init__ for stages with predicates.

        Args:
            variable_output_drive: The configuration key for where the predicates are located.
            args: Arguments for initializing a Stage.
            kwargs: Keyword arguments for initializing a Stage.
        """
        super().__init__(*args, **kwargs)
        self._variable_output_drive = variable_output_drive
        if not self.predicates:
            self.predicates = ["default"]

    def _prepare_predicates(self, predicates: list[dict | str]) -> list[dict]:
        """Create a set of predicates from a given set of conditions."""
        formatted_predicates = []
        for predicate in predicates:
            if isinstance(predicate, str):
                predicate = {"predicate": predicate}
            output_lane = predicate.get("outputLane", f"{self.instance_name}OutputLane{str(uuid4())}".replace("-", "_"))
            if not predicate.get("predicate", None):
                raise ValueError("Output Lane drives should have a predicate key.")
            if not predicate.get("outputLane", None):
                output_lane_config = {"outputLane": output_lane}
                # We make sure that the predicate is in the form {'outputLane': 'value', 'predicate': 'value'} to be
                # consistent with the UI
                predicate = {**output_lane_config, **predicate}
            formatted_predicates.append(predicate)
        return formatted_predicates

    def _disconnect_and_remove_predicate(self, i: int) -> None:
        """Disconnect and remove a predicate at location i."""
        deleted_predicate = self.predicates.pop(i)
        output_lane = deleted_predicate["outputLane"]

        output_stages_to_disconnect = [stage for stage in self.outputs if output_lane in stage.input_lanes]
        self.disconnect_output_from(*output_stages_to_disconnect)

        self.output_lanes.remove(output_lane)
        self._output_streams -= 1

    @property
    def predicates(self) -> list[dict]:
        """Get the predicate list for this stage."""
        return self.configuration[self._variable_output_drive]

    @predicates.setter
    def predicates(self, predicates: list[dict | str]) -> None:
        """Set the predicates for this stage."""
        predicates = self._prepare_predicates(predicates)
        # Create default condition if not present
        if not [predicate for predicate in predicates if predicate["predicate"] == "default"]:
            default_predicate = self._prepare_predicates(["predicate"])
            predicates.extend(default_predicate)
        if not predicates[-1]["predicate"] == "default":
            raise ValueError("The default predicate must be placed at the end of the list.")
        self.disconnect_output_from(*self.outputs)  # disconnect all output stages
        self._output_streams = 0
        self.output_lanes = []
        self._output_lane_idx = 0
        # Create output lanes in parent stage for each predicate
        for predicate in predicates:
            self.output_lanes.append(predicate["outputLane"])
            self._output_streams += 1
        self.configuration[self._variable_output_drive] = predicates

    def add_predicates(self, predicates: list[dict | str]) -> None:
        """Add a predicate.

        Example:
            stage.add_predicates(['>0'])
            stage.add_predicates([{'predicate':'>0', 'outputLane':'lane1'}])
            stage.add_predicates(['>0' ,'=0'])

        Args:
            predicates: The list of predicates to add.

        Raises:
            ValueError: If predicates is not a list.
        """
        if not isinstance(predicates, list):
            raise ValueError("Predicates should be a list.")
        formatted_predicates = self._prepare_predicates(predicates)
        for new_predicate in formatted_predicates:
            self.output_lanes.insert(0, new_predicate["outputLane"])
            self.predicates.insert(0, new_predicate)
            self._output_streams += 1

    def remove_predicate(self, predicate: dict) -> None:
        """Remove a predicate.

        Example:
            stage.remove_predicate(stage.predicates[0])
            stage.remove_predicate({'predicate':'>0', 'outputLane':'lane1'})

        Args:
            predicate: The predicate to delete as a dictionary including the outputLane.

        Raises:
            ValueError: If predicates is not specified or can't find its target.
        """
        clean_predicate = next(iter(self._prepare_predicates([predicate])), {})
        if not clean_predicate:
            raise ValueError("Need to specify a predicate")
        if clean_predicate.get("predicate") == "default":
            raise ValueError("Can't delete the default predicate.")
        for i, found_predicate in enumerate(self.predicates):
            if found_predicate == clean_predicate:
                self._disconnect_and_remove_predicate(i)
                return
        raise ValueError("Can't find target predicate in the predicates list.")


class PipelineDefinition(BaseModel):
    """Pipeline Definition of a flow in an engine."""

    _NODE_TYPES: ClassVar[dict] = {
        "origin": "SOURCE",
        "destination": "TARGET",
        "executor": "EXECUTOR",
        "processor": "PROCESSOR",
    }

    @staticmethod
    def get_attribute(config_definition: dict) -> tuple[str, str]:
        """Gets the attribute name for a configuration using its definition in a human-readable format."""
        config_name = config_definition.get("name")
        config_label = config_definition.get("label")
        if config_label:
            replacements = [(r"[\s-]+", "_"), (r"&", "and"), (r"/sec", "_per_sec"), (r"_\((.+)\)", r"_in_\1")]
            attribute_name = config_label.lower()
            for pattern, replacement in replacements:
                attribute_name = re.sub(pattern, replacement, attribute_name)
        else:
            attribute_name = inflection.underscore(config_definition["fieldName"])
        return attribute_name, config_name

    @staticmethod
    def get_color_icon_from_stage_definition(stage_definition: dict, stage_types: dict) -> str:
        """Create `colorIcon` value from stage definition.

        Args:
            stage_definition: stage definition from pipeline definitions
            stage_types: The PipelineDefinition._NODE_TYPES
        """
        reversed_stage_types = {v: k for k, v in stage_types.items()}
        if stage_definition.get("type") not in reversed_stage_types or not stage_definition.get("label"):
            return ""  # an empty string shows a greyed out image on the UI
        stage_processor_type = reversed_stage_types[stage_definition["type"]].capitalize()
        # space or slash should be delimiters
        escaped_stage_labels = re.split(r"[ /]", stage_definition["label"])
        color_icon_name = "_".join([stage_processor_type] + escaped_stage_labels) + ".png"
        return color_icon_name

    @staticmethod
    def stage_configuration_name(stage_json: dict) -> str:
        """Gets a stages configuration name, the name it has in a flow's configuration."""
        return f"{stage_json['library']}::{stage_json['stageName']}::{stage_json['stageVersion']}"

    schema_version: int = Field(alias="schemaVersion", repr=False)
    version: int = Field(alias="version", repr=False)
    pipeline_id: str = Field(alias="pipelineId", repr=False)
    title: str = Field(alias="title", repr=False)
    description: str = Field(alias="description", repr=False)
    uuid: str = Field(alias="uuid", repr=False)
    ui_info: dict = Field(alias="uiInfo", repr=False)
    fragments: list = Field(alias="fragments", repr=False)
    info: dict = Field(alias="info", repr=False)
    metadata: dict | None = Field(alias="metadata", repr=False, default=None)
    valid: bool = Field(alias="valid", repr=False)
    issues: dict = Field(alias="issues", repr=False)
    previewable: bool = Field(alias="previewable", repr=False)

    configuration_data: list[dict] = Field(alias="configuration", repr=False)

    stages_data: list[dict] = Field(alias="stages", repr=False)
    error_stage_data: dict | None = Field(alias="errorStage", repr=False)
    stats_aggregator_stage_data: dict | None = Field(alias="statsAggregatorStage", repr=False)
    start_event_stages_data: list[dict] | None = Field(default=None, alias="startEventStages", repr=False)
    stop_event_stages_data: list[dict] | None = Field(default=None, alias="stopEventStages", repr=False)
    test_origin_stages_data: dict | None = Field(default=None, alias="testOriginStage", repr=False)

    def __init__(self, flow: "StreamsetsFlow", **pipeline_definition_json: any) -> None:
        """The __init__ for the pipeline definition.

        Args:
            flow: The parent flow object
            pipeline_definition_json: Pipeline definition from the engine.
        """
        super().__init__(**pipeline_definition_json)
        self._flow = flow

        # lazy load library definitions
        self.__library_definitions: LibraryDefinitions | None = None

        self.__all_stages = None

        # for all the stage objects in the flow currently.
        self.__current_stages = None

        # all the special stages
        self.__error_stage = None
        self.__stats_aggregator_stage = None
        self.__start_event_stage = None
        self.__stop_event_stage = None
        self.__test_origin_stage = None

    @property
    def _library_definitions(self) -> LibraryDefinitions:
        if self.__library_definitions is None:
            if self._flow.engine is not None:
                # if possible try to get the library definitions from the engine
                try:
                    self.__library_definitions = self._flow.engine.library_definitions
                except requests.exceptions.HTTPError:
                    pass
            if self.__library_definitions is None:
                # if the library definitions is still None, we either don't have a running engine
                # or we faced an error trying to get the definitions from the engine
                # in this case, we should use a flow's engine_version
                self.__library_definitions = LibraryDefinitions.for_engine_version(
                    engine_version=self._flow.engine_version, platform=self._flow._project._platform
                )

        return self.__library_definitions

    @property
    def _all_stages(self) -> dict:
        if self.__all_stages is None:
            self.__all_stages = {}

            for stage_definition in self._library_definitions.stages:
                stage_name = stage_definition["name"]

                # Get configuration definition attributes
                attributes = defaultdict(list)
                for config_definition in stage_definition["configDefinitions"]:
                    attribute_name, config_name = self.get_attribute(config_definition)
                    attributes[attribute_name].append(StageConfigurationProperty(config_name=config_name))

                for service in stage_definition.get("services"):
                    service_name = service["service"]
                    service_definition = next(
                        (
                            service_def
                            for service_def in self._library_definitions.services
                            if service_def["provides"] == service_name
                        ),
                        None,
                    )

                    if service_definition is None:
                        raise StageDefinitionNotFound(f"Could not find definition of service {service_name}")

                    for config_definition in service_definition["configDefinitions"]:
                        attribute_name, config_name = self.get_attribute(config_definition)
                        attributes[attribute_name].append(
                            StageServiceProperty(service_name=service_name, config_name=config_name)
                        )
                # Invoke the StageWithPredicates class IFF the stage's output streams are governed by lane predicates
                variable_output_drive = stage_definition.get("outputStreamsDrivenByConfig", None)
                if variable_output_drive and variable_output_drive == "lanePredicates":
                    self.__all_stages[stage_name] = StageClassDefault(
                        class_name=StageWithPredicates, attributes=attributes
                    )
                else:
                    self.__all_stages[stage_name] = StageClassDefault(class_name=Stage, attributes=attributes)

        return self.__all_stages

    @property
    def configuration(self) -> Configuration:
        """The configuration for the pipeline."""
        config_definitions = self._library_definitions.pipeline[0]["configDefinitions"]

        mapping = {}
        for config_definition in config_definitions:
            attribute_name, config_name = self.get_attribute(config_definition)
            mapping[attribute_name] = config_name

        return Configuration(
            configuration=self.configuration_data,
            id_to_remap=mapping,
        )

    def _get_stage_data(
        self, label: str | None = None, name: str | None = None, type: str | None = None, library: str | None = None
    ) -> list["StageData"]:
        """Get a stages definition and new instance based on parameters provided.

        Raises:
            ValueError: If both label and name are provided, or if neither is provided.
            StageNotFoundError: If a stage wasn't found.
        """
        if label and name:
            raise ValueError("Use `label` or `name`, not both.")
        elif not label and not name:
            raise ValueError("Either `label` or `name` must be specified.")
        stages = [
            stage
            for stage in self._library_definitions.stages
            if (
                (label and stage["label"] == label or name and stage["name"] == name)
                and (not library or stage["library"] == library)
                and (not type or stage["type"] == self._NODE_TYPES.get(type, type))
            )
        ]
        if not stages:
            raise StageNotFoundError(f"Could not find a stage ({label or name}).")
        return [StageData(definition=stage, instance=self._get_new_stage_instance(stage)) for stage in stages]

    def _get_new_stage_instance(self, stage: dict) -> dict:
        """Create a new instance of a stage's json based on definition."""
        ui_info = dict(
            colorIcon=self.get_color_icon_from_stage_definition(stage, self._NODE_TYPES),
            description="",
            label=self._get_stage_label(stage),
            xPos=0,
            yPos=0,
            stageType=stage.get("type"),
        )
        stage_instance = dict(
            instanceName=self._get_stage_instance_name(stage),
            library=stage.get("library"),
            stageName=stage.get("name"),
            stageVersion=stage.get("version"),
            configuration=list(),
            uiInfo=ui_info,
            inputLanes=list(),
            outputLanes=list(),
            eventLanes=list(),
        )
        stage_instance["configuration"] = [
            self._set_default_value_for_config(config_definition, stage_instance)
            for config_definition in stage["configDefinitions"]
        ]
        stage_instance["services"] = [
            {
                "service": service_definition["provides"],
                "serviceVersion": service_definition["version"],
                "configuration": [
                    self._set_default_value_for_config(config_definition, None)
                    for config_definition in service_definition["configDefinitions"]
                ],
            }
            for service in stage["services"]
            for service_definition in self._library_definitions.services
            if service_definition["provides"] == service["service"]
        ]
        # Propagate RUNTIME configuration injected by the stage.
        for stage_instance_service in stage_instance["services"]:
            for service in stage["services"]:
                if stage_instance_service["service"] == service["service"]:
                    Configuration(stage_instance_service["configuration"]).update(service["configuration"])
        return stage_instance

    def _get_stage_instance_name(self, stage: dict) -> str:
        """Get the instance name for a new stage. Since new instance names increment by value of 1."""
        stage_name = re.sub("[^0-9A-Za-z_]", "", stage["label"])
        if stage["errorStage"]:
            return f"{stage_name}_ErrorStage"
        elif stage["statsAggregatorStage"]:
            return f"{stage_name}_StatsAggregatorStage"
        else:
            similar_instances = set(stage.instance_name for stage in self.stages)
            for i in range(1, 1001):  # upto 1000 stages in a sdc
                new_instance_name = f"{stage_name}_{i:0>2}"
                if new_instance_name not in similar_instances:
                    return new_instance_name
        raise UniqueStageNameNotFoundError("Couldn't find unique instance name for stage.")

    def _get_stage_label(self, stage: dict) -> str:
        """Gets the label of a stage."""
        if stage["errorStage"]:
            return "Error Records - {}".format(stage["label"])
        elif stage["statsAggregatorStage"]:
            return "Stats Aggregator - {}".format(stage["label"])
        else:
            similar_instances = sum(
                stage.get("label") in existing_stage.ui_info.get("label") for existing_stage in self.stages
            )
            return "{} {}".format(stage["label"], similar_instances + 1)

    def _set_default_value_for_config(self, config_definition: dict, stage_instance: dict | None) -> dict:
        # A port of pipelineService.js's setDefaultValueForConfig method (https://git.io/vSh3W).
        config = {"name": config_definition["name"], "value": config_definition["defaultValue"]}
        if config_definition["type"] == "MODEL":
            if config_definition["model"]["modelType"] == "FIELD_SELECTOR_MULTI_VALUE" and not config["value"]:
                config["value"] = []
            # We don't follow the logic for PREDICATE as that assumes that the stage already have output lanes.
            # However, this is called at the time of stage initialization on our side and the stage output lanes
            # does not exist until user explicitly connects stages together.
            elif config_definition["model"]["modelType"] == "LIST_BEAN" and config["value"] is None:
                config["value"] = [
                    {
                        self._set_default_value_for_config(model_config_definition, stage_instance)[
                            "name"
                        ]: self._set_default_value_for_config(model_config_definition, stage_instance).get("value")
                        for model_config_definition in config_definition["model"]["configDefinitions"]
                        if (
                            self._set_default_value_for_config(model_config_definition, stage_instance).get("value")
                            is not None
                        )
                    }
                ]
        elif config_definition["type"] == "BOOLEAN" and config["value"] is None:
            config["value"] = False
        elif config_definition["type"] == "LIST" and not config["value"]:
            config["value"] = []
        elif config_definition["type"] == "MAP" and not config["value"]:
            config["value"] = []
        return config

    def add_stage(
        self, label: str | None = None, name: str | None = None, type: str | None = None, library: str | None = None
    ) -> Stage | StageWithPredicates:
        """Add a new stage to the pipeline.

        Args:
            label: Label of the stage
            name: Name of the stage
            type: Type of stage
            library: Library the stage belongs to
        """
        # get the data for the stage
        stage_instance, stage_definition = next(
            (stage_data.instance, stage_data.definition)
            for stage_data in self._get_stage_data(label=label, name=name, type=type, library=library)
            if stage_data.definition.get("errorStage") is False
        )
        # get output streams, predicates and supported connection types
        output_streams = stage_definition.get("outputStreams", 0)
        variable_output_drive = stage_definition.get("outputStreamsDrivenByConfig", None)
        extra_args = {"variable_output_drive": variable_output_drive} if variable_output_drive else {}
        supported_connection_types = [
            config["connectionType"]
            for config in stage_definition["configDefinitions"]
            # we want all the fields that have connectionType
            if config.get("connectionType")
        ]
        # get the appropriate class with attributes and initialize it.
        stage_class, stage_attributes = self._all_stages.get(
            stage_instance["stageName"], StageClassDefault(class_name=Stage, attributes={})
        )

        stage_object = stage_class(
            pipeline_definition=self,
            output_streams=output_streams,
            supported_connection_types=supported_connection_types,
            attributes=stage_attributes,
            **stage_instance,  # stage_json
            **extra_args,
        )
        self.stages.append(stage_object)
        return stage_object

    def remove_stage(self, stage: Stage) -> None:
        """Removed a stage from the flow.

        Args:
            stage: Stage to remove.
        """
        # remove it from the underlying json
        self.stages = [
            current_stage for current_stage in self.stages if current_stage.instance_name != stage.instance_name
        ]
        # disconnect everything
        stage.disconnect_input_from(*self.stages)
        stage.disconnect_output_from(*self.stages)
        stage.disconnect_event_from(*self.stages)

    def _convert_stage_from_json_to_obj(self, stage_json: dict) -> Stage:
        """Take a stage dict from pipeline definition and convert to a stage class."""
        stage_definition = next(
            (
                stage_def
                for stage_def in self._library_definitions.stages
                if stage_def["name"] == stage_json["stageName"]
            ),
            {},
        )

        if not stage_definition:
            logger.debug("Definitions not found for stage", extra=dict(stage_name=stage_json["stageName"]))

        supported_connection_types = [
            config["connectionType"]
            for config in stage_definition.get("configDefinitions", [])
            if config.get("connectionType")
        ]
        extra_args = {}
        variable_output_drive = stage_definition.get("outputStreamsDrivenByConfig")
        if variable_output_drive == "lanePredicates":
            extra_args.update({"variable_output_drive": variable_output_drive})

        stage_class, stage_attributes = self._all_stages.get(
            stage_json["stageName"], StageClassDefault(class_name=Stage, attributes={})
        )

        stage_object = stage_class(
            pipeline_definition=self,
            supported_connection_types=supported_connection_types,
            attributes=stage_attributes,
            **stage_json,
            **extra_args,
        )

        return stage_object

    @property
    def stages(self) -> list[Stage | StageWithPredicates]:
        """The stages belonging to the flow."""
        if self.__current_stages is None:
            self.__current_stages = [
                self._convert_stage_from_json_to_obj(stage_json=stage_json) for stage_json in self.stages_data
            ]
        return self.__current_stages

    @stages.setter
    def stages(self, val: list[Stage]) -> None:
        self.__current_stages = val

    @property
    def error_stage(self) -> Stage | None:
        """The error stage of the flow."""
        if self.__error_stage is None:
            if not self.error_stage_data:
                return None
            else:
                self.__error_stage = self._convert_stage_from_json_to_obj(self.error_stage_data)
        return self.__error_stage

    @property
    def stats_aggregator_stage(self) -> Stage | None:
        """The stats aggregator stage of the flow."""
        if self.__stats_aggregator_stage is None:
            if not self.stats_aggregator_stage_data:
                return None
            else:
                self.__stats_aggregator_stage = self._convert_stage_from_json_to_obj(self.stats_aggregator_stage_data)
        return self.__stats_aggregator_stage

    @property
    def start_event(self) -> Stage | None:
        """The start event stage of the flow."""
        if self.__start_event_stage is None:
            if not self.start_event_stages_data or not self.start_event_stages_data[0]:
                return None
            else:
                self.__start_event_stage = self._convert_stage_from_json_to_obj(self.start_event_stages_data[0])
        return self.__start_event_stage

    @property
    def stop_event(self) -> Stage | None:
        """The stop event stage of the flow."""
        if self.__stop_event_stage is None:
            if not self.stop_event_stages_data or not self.stop_event_stages_data[0]:
                return None
            else:
                self.__stop_event_stage = self._convert_stage_from_json_to_obj(self.stop_event_stages_data[0])
        return self.__stop_event_stage

    @property
    def test_origin(self) -> Stage | None:
        """The test origin stage of the flow."""
        if self.__test_origin_stage is None:
            if not self.test_origin_stages_data:
                return None
            else:
                self.__test_origin_stage = self._convert_stage_from_json_to_obj(self.test_origin_stages_data)
        return self.__test_origin_stage

    def set_error_stage(self, label: str | None = None, name: str | None = None, library: str | None = None) -> Stage:
        """Set the error stage of the flow.

        Args:
            label: Label of the stage.
            name: Name of the stage.
            library: Library the stage belongs to.
        """
        stage_instance, stage_definition = next(
            (stage_data.instance, stage_data.definition)
            for stage_data in self._get_stage_data(label=label, name=name, library=library)
            if stage_data.definition.get("errorStage") is True
        )

        self.error_stage_data = stage_instance
        self.configuration["badRecordsHandling"] = self.stage_configuration_name(stage_instance)
        stage_class, stage_attributes = self._all_stages.get(
            stage_instance["stageName"], StageClassDefault(class_name=Stage, attributes={})
        )

        self.__error_stage = stage_class(
            pipeline_definition=self,
            output_streams=stage_definition.get("outputStreams", 0),
            **stage_instance,
        )
        return self.__error_stage

    def set_stats_aggregator_stage(
        self, label: str | None = None, name: str | None = None, library: str | None = None
    ) -> Stage:
        """Set the stats aggregator stage of the flow.

        Args:
            label: Label of the stage.
            name: Name of the stage.
            library: Library the stage belongs to.
        """
        stage_instance, stage_definition = next(
            (stage_data.instance, stage_data.definition)
            for stage_data in self._get_stage_data(label=label, name=name, library=library)
            if stage_data.definition.get("statsAggregatorStage") is True
        )

        self.stats_aggregator_stage_data = stage_instance
        self.configuration["statsAggregatorStage"] = self.stage_configuration_name(stage_instance)
        stage_class, stage_attributes = self._all_stages.get(
            stage_instance["stageName"], StageClassDefault(class_name=Stage, attributes={})
        )

        self.__stats_aggregator_stage = stage_class(
            pipeline_definition=self, output_streams=stage_definition.get("outputStreams", 0), **stage_instance
        )
        return self.__stats_aggregator_stage

    def set_start_event_stage(
        self, label: str | None = None, name: str | None = None, library: str | None = None
    ) -> Stage:
        """Set the start event stage of the flow.

        Args:
            label: Label of the stage.
            name: Name of the stage.
            library: Library the stage belongs to.
        """
        stage_instance, stage_definition = next(
            (stage_data.instance, stage_data.definition)
            for stage_data in self._get_stage_data(label=label, name=name, library=library)
            if stage_data.definition.get("pipelineLifecycleStage") is True
        )

        # We need instanceName in the form <instance_name>_StartEventStage and not <instance_name>_01
        instance_name_split_list = stage_instance["instanceName"].split("_")
        instance_name_split_list[-1] = "StartEventStage"
        stage_instance["instanceName"] = "_".join(instance_name_split_list)
        self.start_event_stages_data = [stage_instance]
        self.configuration["startEventStage"] = self.stage_configuration_name(stage_instance)

        stage_class, stage_attributes = self._all_stages.get(
            stage_instance["stageName"], StageClassDefault(class_name=Stage, attributes={})
        )

        self.__start_event_stage = stage_class(
            pipeline_definition=self, output_streams=stage_definition.get("outputStreams", 0), **stage_instance
        )
        return self.__start_event_stage

    def set_stop_event_stage(
        self, label: str | None = None, name: str | None = None, library: str | None = None
    ) -> Stage:
        """Set the stop event stage of the flow.

        Args:
            label: Label of the stage.
            name: Name of the stage.
            library: Library the stage belongs to.
        """
        stage_instance, stage_definition = next(
            (stage_data.instance, stage_data.definition)
            for stage_data in self._get_stage_data(label=label, name=name, library=library)
            if stage_data.definition.get("pipelineLifecycleStage") is True
        )

        # We need instanceName in the form <instance_name>_StopEventStage and not <instance_name>_01
        instance_name_split_list = stage_instance["instanceName"].split("_")
        instance_name_split_list[-1] = "StopEventStage"
        stage_instance["instanceName"] = "_".join(instance_name_split_list)
        self.stop_event_stages_data = [stage_instance]
        self.configuration["stopEventStage"] = self.stage_configuration_name(stage_instance)
        stage_class, stage_attributes = self._all_stages.get(
            stage_instance["stageName"], StageClassDefault(class_name=Stage, attributes={})
        )

        self.__stop_event_stage = stage_class(
            pipeline_definition=self, output_streams=stage_definition.get("outputStreams", 0), **stage_instance
        )
        return self.__stop_event_stage

    def set_test_origin_stage(
        self, label: str | None = None, name: str | None = None, library: str | None = None
    ) -> Stage:
        """Set the test origin stage of the flow.

        Args:
            label: Label of the stage.
            name: Name of the stage.
            library: Library the stage belongs to.
        """
        stage_instance, stage_definition = next(
            (stage_data.instance, stage_data.definition)
            for stage_data in self._get_stage_data(label=label, name=name, library=library)
            if stage_data.definition.get("errorStage") is True
        )

        # We need instanceName in the form <instance_name>_TestOriginStage and not <instance_name>_01
        instance_name_split_list = stage_instance["instanceName"].split("_")
        instance_name_split_list[-1] = "TestOriginStage"
        stage_instance["instanceName"] = "_".join(instance_name_split_list)
        self.test_origin_stages_data = stage_instance
        self.configuration["testOriginStage"] = self.stage_configuration_name(stage_instance)
        stage_class, stage_attributes = self._all_stages.get(
            stage_instance["stageName"], StageClassDefault(class_name=Stage, attributes={})
        )

        self.__test_origin_stage = stage_class(
            pipeline_definition=self, output_streams=stage_definition.get("outputStreams", 0), **stage_instance
        )
        return self.__test_origin_stage

    def _sort_stage_instances(self) -> list[Stage]:
        """A port of pipelineService.js's sortStageInstances (https://git.io/JmAoO)."""
        sorted_stages = list()
        removed_map = dict()
        produced_outputs = list()
        check = True
        iteration = 0

        while check:
            prior = len(sorted_stages)
            for stage in self.stages:
                if stage.instance_name not in removed_map:
                    already_produced = [item for item in produced_outputs if item in stage.input_lanes]
                    if len(already_produced) == len(stage.input_lanes):
                        produced_outputs += stage.output_lanes
                        produced_outputs += stage.event_lanes
                        removed_map[stage.instance_name] = True
                        sorted_stages.append(stage)
            iteration += 1
            if prior == len(sorted_stages) and iteration >= len(sorted_stages):
                check = False
                for stage in self.stages:
                    if stage.instance_name not in removed_map:
                        sorted_stages.append(stage)

        return sorted_stages

    def _auto_arrange_stages(self) -> None:
        """https://sor.bz/N3QcJ. Sets the x-pos and y-pos values of a stage so that they look organized on the UI."""
        sorted_stages = self._sort_stage_instances()

        x_pos = 60
        y_pos = 50
        lane_y_pos = {}
        lane_x_pos = {}

        for stage in sorted_stages:
            y = lane_y_pos.get(stage.input_lanes[0], 0) if len(stage.input_lanes) else y_pos
            x = lane_x_pos.get(stage.input_lanes[0], 0) + 220 if len(stage.input_lanes) else x_pos

            if len(stage.input_lanes) > 1:
                m_x = 0
                for input_lane in stage.input_lanes:
                    m_x = max(lane_x_pos.get(input_lane, 0), m_x)
                x = m_x + 220

            if stage.input_lanes and lane_y_pos.get(stage.input_lanes[0], 0):
                lane_y_pos[stage.input_lanes[0]] += 150

            if not y:
                y = y_pos

            if len(stage.output_lanes) > 1:
                for i, output_lane in enumerate(stage.output_lanes):
                    lane_y_pos[output_lane] = y - 10 + (130 * i)
                    lane_x_pos[output_lane] = x

                if y == y_pos:
                    y += 30 * len(stage.output_lanes)
            else:
                if len(stage.output_lanes):
                    lane_y_pos[stage.output_lanes[0]] = y
                    lane_x_pos[stage.output_lanes[0]] = x

                if len(stage.input_lanes) > 1 and y == y_pos:
                    y += 130

            if len(stage.event_lanes):
                lane_y_pos[stage.event_lanes[0]] = y + 150
                lane_x_pos[stage.event_lanes[0]] = x

            stage.ui_info["xPos"] = x
            stage.ui_info["yPos"] = y

            x_pos = x + 220

    def model_dump(self, by_alias: bool = True, **kwargs: any) -> dict:
        """Ensure stages are properly arranged when pipeline definition is stringified."""
        self._auto_arrange_stages()

        # after arranging we can model dump our stages which are not dumped implicitly
        self.stages_data = [stage.model_dump(by_alias=by_alias) for stage in self.stages]
        self.error_stage_data = self.error_stage.model_dump(by_alias=by_alias) if self.error_stage else None
        self.stats_aggregator_stage_data = (
            self.stats_aggregator_stage.model_dump(by_alias=by_alias) if self.stats_aggregator_stage else None
        )
        self.start_event_stages_data = [self.start_event.model_dump(by_alias=by_alias)] if self.start_event else list()
        self.stop_event_stages_data = [self.stop_event.model_dump(by_alias=by_alias)] if self.stop_event else list()
        self.test_origin_stages_data = self.test_origin.model_dump(by_alias=by_alias) if self.test_origin else None

        # metadata labels need to be an empty list for the UI
        if self.metadata is None:
            self.metadata = dict()
        self.metadata.update(dict(labels=list()))

        return super().model_dump(by_alias=by_alias, **kwargs)


class StreamsetsFlowUsage(BaseModel):
    """The Model for StreamsetsFlowUsage."""

    last_update_time: str | None = Field(repr=True)
    access_count: int | None = Field(repr=True)
    last_access_time: str | None = Field(repr=False)
    last_updated_at: str | None = Field(repr=False)
    last_updater_id: str | None = Field(repr=False)
    last_accessed_at: str | None = Field(repr=False)
    last_accessor_id: str | None = Field(repr=False)


class StreamsetsFlowROV(BaseModel):
    """The Model for StreamsetsFlowROV."""

    mode: int | None = Field(repr=True)
    member_roles: dict | None = Field(repr=False)
    collaborator_ids: dict | None = Field(repr=False)


class StreamsetsFlowMetadata(BaseModel):
    """The Model for StreamsetsFlowMetadata."""

    name: str = Field(repr=True)
    description: str = Field(repr=True)
    flow_id: str = Field(
        alias="asset_id",
        repr=True,
    )
    owner_id: str | None = Field(repr=False, default=None)
    created: int | None = Field(repr=False, default=None)
    created_at: str | None = Field(repr=False, default=None)
    tags: list | None = Field(repr=False, default=None)
    asset_attributes: list | None = Field(repr=False, default=None)
    asset_state: str | None = Field(repr=False, default=None)
    asset_type: str | None = Field(repr=False, default=None)
    catalog_id: str | None = Field(repr=False, default=None)
    rating: int | None = Field(repr=False, default=None)
    total_ratings: int | None = Field(repr=False, default=None)
    size: int | None = Field(repr=False, default=None)
    project_id: str | None = Field(repr=False, default=None)
    rov: StreamsetsFlowROV | None = Field(repr=False, default=None)
    usage: StreamsetsFlowUsage | None = Field(repr=False, default=None)
    version: float | None = Field(repr=False, default=None)
    create_time: str | None = Field(repr=False, default=None)
    is_linked_with_sub_container: bool | None = Field(repr=False, default=None)
    asset_category: str | None = Field(repr=False, default=None)
    sandbox_id: str | None = Field(repr=False, default=None)
    creator_id: str | None = Field(repr=False, default=None)

    _expose: bool = PrivateAttr(default=False)


@Flow.register("streamsets")
class StreamsetsFlow(Flow):
    """The Model for StreamsetsFlow."""

    metadata: StreamsetsFlowMetadata = Field(repr=True)

    connection_ids: list[str] = Field(default=[], alias="connection_ids", repr=False)
    engine_version: str = Field(alias="engine_version", repr=True)
    environment_id: str = Field(alias="environment_id", repr=False)
    fragments_ids: list[str] = Field(default=[], alias="fragment_ids", repr=False)

    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity.streamsets_flow": {}}

    def __init__(self, project: "Project", pipeline_definition: dict | None = None, **flow_json: dict) -> None:
        """The __init__ of the StreamsetsFlow class.

        Args:
            project: The Project object.
            pipeline_definition: Pipeline definition for the flow
            flow_json: The JSON for the flow.
        """
        super().__init__(**flow_json)
        self._project = project

        # attributes to be used for lazy-loading properties
        self.__pipeline_definition_object = (
            PipelineDefinition(flow=self, **pipeline_definition) if pipeline_definition else None
        )
        self._environment = None
        self._engine = None

    @staticmethod
    def _create(
        project: "Project",
        name: str,
        environment: Environment | None = None,
        description: str = "",
        flow_type: str = "streamsets",
    ) -> "StreamsetsFlow":
        if flow_type not in SUPPORTED_FLOWS:
            raise TypeError("Flow type not supported.")

        # create a flow in the project
        # default to the latest engine version if an environment is not passed.
        payload = json.dumps(
            {
                "name": name,
                "description": description,
                "environment_id": environment.environment_id if environment else "",
                "engine_version": environment.engine_version
                if environment
                else project._platform.available_engine_versions[0],
            }
        )
        params = {"project_id": project.metadata.guid}
        create_flow_response = project._platform._streamsets_flow_api.create_streamsets_flow(
            params=params, data=payload
        )
        flow = StreamsetsFlow(project=project, **create_flow_response.json()["flow"])

        # create a pipeline definition from the template and add it in.
        flow.pipeline_definition = create_pipeline_definition_for_new_flow(
            flow_executor_id=flow.executor_id,
            iam_id=flow.metadata.usage.last_updater_id,
        )

        # update the flow to ensure it has a pipeline definition
        project.update_flow(flow)

        return flow

    def _update(self) -> requests.Response:
        """Update the Flow class with provided data.

        Args:
            project: The Project object.
            pipeline_definition: Pipeline definition for the flow
            data: The JSON for the flow.
        """
        params = {"project_id": self._project.metadata.guid}
        payload = {
            "name": self.name,
            "connection_ids": self.connection_ids if self.connection_ids else [],
            "description": self.description,
            "environment_id": self.environment_id,
            "engine_version": self.engine_version,
            "fragment_ids": self.fragments_ids if self.fragments_ids else [],
            "pipeline_definition": self.pipeline_definition,
        }

        update_flow_response = self._project._platform._streamsets_flow_api.update_streamsets_flow(
            params=params, flow_id=self.flow_id, data=json.dumps(payload)
        )
        update_flow_json = update_flow_response.json()

        self.__init__(
            project=self._project,
            pipeline_definition=update_flow_json["pipeline_definition"],
            **update_flow_json["flow"],
        )

        return update_flow_response

    def _delete(self) -> requests.Response:
        params = {"project_id": self._project.metadata.guid}
        return self._project._platform._streamsets_flow_api.delete_streamsets_flow(params=params, flow_id=self.flow_id)

    def _duplicate(self, name: str, description: str = "") -> "StreamsetsFlow":
        """Duplicate this StreamsetsFlow with a new name and description.

        Args:
            name: The name for the duplicated flow.
            description: The description for the duplicated flow.

        Returns:
            The newly created duplicate flow.
        """
        payload = json.dumps({"name": name, "description": description})
        params = {"project_id": self._project.metadata.guid}

        response = self._project._platform._streamsets_flow_api.duplicate_streamsets_flow(
            params=params, data=payload, flow_id=self.flow_id
        )
        response_json = response.json()

        flow = StreamsetsFlow(
            project=self._project,
            pipeline_definition=response_json["pipeline_definition"],
            **response_json["flow"],
            flow_type="streamsets",
        )

        return flow

    @property
    def name(self) -> str:
        """Returns name of the flow."""
        return self.metadata.name

    @name.setter
    def name(self, value: str) -> None:
        """Sets name of the flow."""
        self.metadata.name = value

    @property
    def description(self) -> str:
        """Returns description of the flow."""
        return self.metadata.description

    @description.setter
    def description(self, value: str) -> None:
        """Sets description of the flow."""
        self.metadata.description = value

    @property
    def flow_id(self) -> str:
        """Returns id of the flow."""
        return self.metadata.flow_id

    @cached_property
    def executor_id(self) -> str:
        """Get a flow's id in an executor."""
        return f"testRun__{self.metadata.flow_id}"

    @property
    def _pipeline_definition(self) -> PipelineDefinition:
        if self.__pipeline_definition_object is None:
            # lazy load the pipeline definition
            full_flow_data = self._project._platform._streamsets_flow_api.get_streamsets_flow_by_id(
                params=dict(project_id=self.metadata.project_id), flow_id=self.flow_id
            ).json()
            self.__pipeline_definition_object = PipelineDefinition(flow=self, **full_flow_data["pipeline_definition"])
        return self.__pipeline_definition_object

    @property
    def pipeline_definition(self) -> dict:
        """A flow's definition in an engine."""
        return self._pipeline_definition.model_dump(by_alias=True)

    @pipeline_definition.setter
    def pipeline_definition(self, val: dict) -> None:
        self.__pipeline_definition_object = PipelineDefinition(flow=self, **val)

    @property
    def environment(self) -> Environment:
        """The environment this flow belongs to."""
        if self._environment is None and self.environment_id:
            self._environment = self._project.environments.get(**dict(environment_id=self.environment_id))
        return self._environment

    @environment.setter
    def environment(self, val: Environment) -> None:
        """Set the environment of the flow."""
        # unset the _engine attribute for consistency
        self._engine = None

        self._environment = val
        self.environment_id = self._environment.environment_id
        # having an environment, we will always have an associated engine version
        self.engine_version = self._environment.engine_version

    @property
    def engine(self) -> Engine | None:
        """The engine in which this flow will be run."""
        if self._engine is None and self.environment is not None and len(self.environment.engines) > 0:
            self._engine = self.environment.engines[0]
        return self._engine

    @property
    def configuration(self) -> Configuration:
        """The configuration of a flow."""
        return self._pipeline_definition.configuration

    @property
    def stages(self) -> list[Stage | StageWithPredicates]:
        """The stages in the flow."""
        return self._pipeline_definition.stages

    @property
    def error_stage(self) -> Stage | None:
        """The error stage of the flow."""
        return self._pipeline_definition.error_stage

    @property
    def stats_aggregator_stage(self) -> Stage | None:
        """The stats aggregator stage of the flow."""
        return self._pipeline_definition.stats_aggregator_stage

    @property
    def start_event(self) -> Stage | None:
        """The start event stage of the flow."""
        return self._pipeline_definition.start_event

    @property
    def stop_event(self) -> Stage | None:
        """The stop event stage of the flow."""
        return self._pipeline_definition.stop_event

    @property
    def test_origin(self) -> Stage | None:
        """The test origin stage of the flow."""
        return self._pipeline_definition.test_origin

    def add_stage(
        self, label: str | None = None, name: str | None = None, type: str | None = None, library: str | None = None
    ) -> Stage | StageWithPredicates:
        """Add a stage to the flow.

        Args:
            label: Label of the stage to add.
            name: Name of the stage to add.
            type: Type of the stage to add.
            library: Library that stage to add belongs to.
        """
        return self._pipeline_definition.add_stage(label=label, name=name, type=type, library=library)

    def remove_stage(self, stage: Stage) -> None:
        """Removes a stage from the flow.

        Args:
            stage: The stage to remove.
        """
        self._pipeline_definition.remove_stage(stage=stage)

    def set_error_stage(self, label: str | None = None, name: str | None = None, library: str | None = None) -> Stage:
        """Set the error stage of a flow."""
        return self._pipeline_definition.set_error_stage(label=label, name=name, library=library)

    def set_stats_aggregator_stage(
        self, label: str | None = None, name: str | None = None, library: str | None = None
    ) -> Stage:
        """Set the stats aggregator stage of a flow."""
        return self._pipeline_definition.set_stats_aggregator_stage(label=label, name=name, library=library)

    def set_start_event_stage(
        self, label: str | None = None, name: str | None = None, library: str | None = None
    ) -> Stage:
        """Set the start event stage of a flow."""
        return self._pipeline_definition.set_start_event_stage(label=label, name=name, library=library)

    def set_stop_event_stage(
        self, label: str | None = None, name: str | None = None, library: str | None = None
    ) -> Stage:
        """Set the stop event stage of a flow."""
        return self._pipeline_definition.set_stop_event_stage(label=label, name=name, library=library)

    def set_test_origin_stage(
        self, label: str | None = None, name: str | None = None, library: str | None = None
    ) -> Stage:
        """Set the test origin stage of a flow."""
        return self._pipeline_definition.set_test_origin_stage(label=label, name=name, library=library)

    def validate(self) -> list["FlowValidationError"]:
        """Validates a flow.

        Returns:
            A `list` of `FlowValidationError` containing issues.
        """
        if not self.environment:
            raise ValueError("Cannot validate a flow that is not associated with an environment")
        if not self.engine:
            raise ValueError("Cannot validate a flow in an environment without an engine.")

        # create pipeline in sdc if it doesn't exist
        try:
            response = self.engine.api_client.get_pipeline_by_id(pipeline_id=self.executor_id)
        except requests.exceptions.HTTPError:
            response = self.engine.api_client.create_pipeline(
                pipeline_title=self.executor_id,
                params=dict(description="description", draft=False, autoGeneratePipelineId=False),
            )

        # use that engine pipeline's uuid and pipeline id, help's us run on different engines if required.
        pipeline_definition = deepcopy(self.pipeline_definition)
        pipeline_definition["uuid"] = response.json()["uuid"]
        pipeline_definition["pipelineId"] = response.json()["pipelineId"]

        # do the validation
        validation_result = self.engine.api_client.validate_pipeline(self.executor_id)
        previewer_id = validation_result.json()["previewerId"]
        self.engine.api_client.get_pipeline_preview_status(self.executor_id, previewer_id)
        self.engine.api_client.get_pipeline_preview(self.executor_id, previewer_id)

        flow_data_issues = self.engine.api_client.get_pipeline_validation_status(
            self.executor_id, data=pipeline_definition
        ).json()["issues"]

        issues = []
        for k, v in flow_data_issues["stageIssues"].items():
            for i in v:
                validation = FlowValidationError(type="stageIssues", **i)
                issues.append(validation)
        for i in flow_data_issues["pipelineIssues"]:
            validation = FlowValidationError(type="pipelineIssues", **i)
            issues.append(validation)

        return issues

    @override
    def model_dump(self, by_alias: bool = True, **kwargs: any) -> dict:
        data = super().model_dump(by_alias=by_alias, **kwargs)
        data["pipeline_definition"] = self.pipeline_definition
        return data


class StreamsetsFlowPayloadExtender(PayloadExtender):
    """Streamsets flow extender setup also `streamsets_env_id`.

    :meta: private
    """

    @override
    def extend(self, payload: dict[str, Any], flow: Flow) -> dict[str, Any]:
        payload["asset_ref"] = flow.flow_id
        payload.setdefault("configuration", {})["streamsets_env_id"] = flow.environment_id
        return payload


class StreamsetsFlows(CollectionModel):
    """Collection of StreamsetsFlows."""

    def __init__(self, project: "Project") -> None:
        """The __init__ of the StreamsetsFlow class.

        Args:
            project: The Project object.
        """
        super().__init__(project)
        self._project = project
        self.unique_id = "metadata.flow_id"

    def _request_parameters(self) -> list:
        return ["flow_id", "project_id"]

    def __len__(self) -> int:
        """The len of the StreamsetsFlows class."""
        query_params = {
            "project_id": self._project.metadata.guid,
        }
        res = self._project._platform._streamsets_flow_api.get_streamsets_flows(params=query_params)
        res_json = res.json()
        return res_json["total_count"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        if "start" in request_params:
            parsed_url = urlparse(request_params["start"]["href"])
            params = parse_qs(parsed_url.query)
            request_params["start"] = params.get("start", [None])[0]

        request_params_defaults = {
            "project_id": self._project.metadata.guid,
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)

        if "flow_id" in request_params:
            response_json = self._project._platform._streamsets_flow_api.get_streamsets_flow_by_id(
                params={k: v for k, v in request_params_unioned.items() if v is not None},
                flow_id=request_params["flow_id"],
            ).json()
            response = {"streamsets_flows": [response_json["flow"]]}

        else:
            response = self._project._platform._streamsets_flow_api.get_streamsets_flows(
                params={k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()

        return CollectionModelResults(
            response,
            StreamsetsFlow,
            "next",
            "start",
            "streamsets_flows",
            {"project": self._project, "flow_type": "streamsets"},
        )


class StreamsetsConnectionMetadata(BaseModel):
    """Streamsets Connection Metadata object."""

    asset_category: str | None = Field(default=None, description="Category of the asset", repr=False)
    asset_id: str = Field(description="Asset identifier", repr=True)
    asset_type: str | None = Field(default=None, description="Type of the asset", repr=False)
    create_time: str | None = Field(default=None, description="Creation time", repr=False)
    creator_id: str | None = Field(default=None, description="Asset creator identifier", repr=False)
    project_id: str | None = Field(default=None, description="Project identifier", repr=False)
    model_config = ConfigDict(frozen=True)


class StreamsetsConnection(BaseModel):
    """Streamsets Connection object."""

    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity": {}}
    metadata: StreamsetsConnectionMetadata = Field(repr=False)
    datasource_type: str | None = Field(default=None, description="Datasource type", repr=False)
    name: str | None = Field(default=None, description="Connection name", repr=True)
    properties: dict | None = Field(default=None, repr=False)

    def __init__(self, platform: "Platform" = None, project: "Project" = None, **connection_json: dict) -> None:
        """The __init__ of the StreamsetsConnection class.

        Args:
            connection_json: The JSON for the StreamsetsConnection.
            platform: The Platform object.
            project: The Project object.
        """
        super().__init__(**connection_json)
        self._platform = platform
        self._project = project


class FlowValidationError(BaseModel):
    """Streamsets validation error object."""

    type: str = Field(repr=True)
    instanceName: str | None = Field(default=None, repr=True)
    level: str = Field(repr=False)
    message: str = Field(repr=False)
    errorCode: str = Field(repr=False)
    humanReadableMessage: str = Field(repr=True)
    technicalMessage: str = Field(repr=False)
