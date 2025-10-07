#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Python Generator processors for streaming flow."""

import copy
import re
import textwrap
from collections import defaultdict
from ibm_watsonx_data_integration.codegen.code import Code, Coder
from ibm_watsonx_data_integration.codegen.preamble import StreamingPreamble
from ibm_watsonx_data_integration.common.constants import (
    PROD_BASE_API_URL,
    PROD_BASE_URL,
)
from ibm_watsonx_data_integration.services.streamsets.api import EnvironmentApiClient
from ibm_watsonx_data_integration.services.streamsets.models.flow_model import PipelineDefinition
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import IAMAuthenticator


class StageVertex:
    """Wrapper class for streaming flow stage."""

    def __init__(
        self, source_data: dict, config_definitions: list[dict[str, Any]], number_suffix: int | None = None
    ) -> None:
        """The __init__ of the StageVertex class.

        Args:
            source_data: Raw stage data taken from pipeline definition.
            config_definitions: Default stage configuration definitions.
            number_suffix: Number of stage in whole pipeline definition.
        """
        self._source_data = source_data
        self._config_definitions = config_definitions
        self._number_suffix = number_suffix

        # TODO: add event lanes
        self.output_lanes = source_data["outputLanes"]
        self.input_lanes = source_data["inputLanes"]
        # Remove additional stage numbers.
        self.label = re.sub(r"\s\d+$", "", source_data["uiInfo"]["label"])
        self.stage_type = source_data["uiInfo"]["stageType"]
        self.stage_name = source_data["stageName"]
        self.configuration: list[dict[str, Any]] = source_data["configuration"]

        self.stage_variable_name = self.label.lower().replace(" ", "_")
        if self._number_suffix:
            self.stage_variable_name = f"{self.stage_variable_name}_{self._number_suffix}"

    def __str__(self) -> str:
        """String representation of code to create stage."""
        stage_definition = f'{self.stage_variable_name} = flow.add_stage("{self.label}")'
        return f"{stage_definition}\n{self.stage_configuration()}".strip()

    def stage_configuration(self) -> str:
        """Return stage configuration properties changed by user."""
        changed_config_values = []
        for stage_config in self.configuration:
            if not stage_config.get("value"):
                continue

            value = stage_config.get("value")
            name = stage_config.get("name")
            config_definition = self._get_stage_config_definition(config_name=name)

            if value == config_definition["defaultValue"]:
                continue

            human_readable_config_name, _ = PipelineDefinition.get_attribute(config_definition)
            processed_value = value
            # TODO: WSDK-487
            if (
                config_definition.get("type", "").lower() in ("text", "string")
                or config_definition.get("fieldName", "").lower() == "connectionselection"
            ):
                processed_value = f'"{processed_value}"'

            if config_definition.get("type", "").lower() == "credential":
                processed_value = '"***"'

            changed_config_values.append(f"{self.stage_variable_name}.{human_readable_config_name} = {processed_value}")

        return "\n".join(changed_config_values)

    def _get_stage_config_definition(self, config_name: str) -> dict[str, Any]:
        for config in self._config_definitions:
            if config["name"] == config_name:
                return config


class StreamingProcessor(Coder):
    """Main processor for recreating script to create streaming flow.

    Responsible for creating ``StageVertex`` class foe each stage within pipeline definition.
    Handle building relation graph between stages using adjacency list.
    """

    def __init__(
        self,
        source_data: dict,
        auth: "IAMAuthenticator",  # pragma: allowlist secret
        base_url: str = PROD_BASE_URL,
        base_api_url: str = PROD_BASE_API_URL,
    ) -> None:
        """The __init__ of the StreamingProcessor class.

        Args:
            source_data: Streaming flow definition as python dictionary.
            auth: Authenticator instance.
            base_url: URL to IBM Cloud.
            base_api_url: URL to API endpoints.
        """
        self._source_data = source_data
        self._environment_api_client = EnvironmentApiClient(auth=auth, base_url=base_api_url)
        self._stage_counter = defaultdict(int)
        self._stages = list()
        self._preamble = StreamingPreamble(source_data=source_data, base_url=base_url, base_api_url=base_api_url)
        self._lanes_to_vertex_lookup = dict()
        self._graph = defaultdict(list)
        self._definitions = None

    @property
    def definitions(self) -> dict[str, list]:
        """Parsed stage definitions with configuration definition."""
        if not self._definitions:
            res_json = self._environment_api_client.get_library_definitions_for_engine_version(
                engine_version=self._source_data["entity"]["streamsets_flow"]["engine_version"]
            ).json()
            self._definitions = self._parse_definition_response(res_json)

        return self._definitions

    @staticmethod
    def _parse_definition_response(definition_json: dict) -> dict:
        result = dict()
        for _, stage_definition in definition_json["stageDefinitionMap"].items():
            stage_name = stage_definition["name"]
            result[stage_name] = copy.deepcopy(stage_definition["configDefinitions"])

        return result

    def _extract_stages(self) -> None:
        """Actual StaveVertex creation and building relation graph between stages."""
        for stage_dict in self._source_data["pipeline_definition"]["stages"]:
            self._stage_counter[stage_dict["stageName"]] += 1

            default_stage_definition = self.definitions[stage_dict["stageName"]]

            vertex = StageVertex(
                stage_dict,
                number_suffix=self._stage_counter[stage_dict["stageName"]],
                config_definitions=default_stage_definition,
            )
            self._stages.append(vertex)

            # build stages connection graph
            if vertex.stage_type.lower() == "source":
                self._lanes_to_vertex_lookup[vertex.output_lanes[0]] = vertex
                _ = self._graph[vertex.output_lanes[0]]
                continue

            # stages type other than `source`
            for output_lane in vertex.output_lanes:
                self._lanes_to_vertex_lookup[output_lane] = vertex

            for input_lane in vertex.input_lanes:
                self._graph[input_lane].append(vertex)

    def stages_as_str(self) -> str:
        """Collect string representation of all stages.

        Returns:
            A string representation of create stage code for all stages.
        """
        if len(self._stages) == 0:
            self._extract_stages()

        result = []
        for stage in self._stages:
            result.append(str(stage))

        return "\n".join(result)

    def stages_connection_as_str(self) -> str:
        """Collect string representation of connection between stages.

        Returns:
            A string representation of connection between stages.
        """
        if len(self._stages) == 0:
            self._extract_stages()

        result = []
        for output_lane, neighbours in self._graph.items():
            vertex = self._lanes_to_vertex_lookup[output_lane]

            for neighbour in neighbours:
                result.append(f"{vertex.stage_variable_name}.connect_output_to({neighbour.stage_variable_name})")

        return "\n".join(result)

    @property
    def script_footer(self) -> str:
        """Return generated script footer."""
        return "project.update_flow(flow)"

    def to_code(self) -> Code:
        """Returns object holding generated python script."""
        content = textwrap.dedent(f"""\
{self._preamble}

{self.stages_as_str()}

{self.stages_connection_as_str()}

{self.script_footer}
""")
        return Code(content=content)
