# from ..components.local_message_handler import LocalMessageHandler
# from ..components.message_handler import MessageHandler
import requests
from ibm_watsonx_data_integration.common.models import CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.services.datastage.models.flow_stages import FlowComposer
from ibm_watsonx_data_integration.cpd_models.flow_model import Flow, PayloadExtender
from typing_extensions import override
from ibm_watsonx_data_integration.services.datastage.models.flow.dag import (
    DAG,
    Link,
    Node,
)
from ibm_watsonx_data_integration.services.streamsets.models.environment_model import Environment
from urllib.parse import parse_qs, urlparse

# from ibm_watsonx_data_integration.services.datastage._console import console
# from ibm_watsonx_data_integration.services.datastage.models.flow.dag import SuperNode
# from ibm_watsonx_data_integration.services.datastage.models.flow_runner import FlowRunner
from ibm_watsonx_data_integration.services.datastage.models.layout import LayeredLayout

# from ibm.datastage._framework.paramsets import LocalParameters, ParameterSet
# from ibm.datastage._framework.runtime import Runtime
# from ibm.datastage._framework.schema.data_definition import DataDefinition

import json

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models.project_model import Project
from ibm_watsonx_data_integration.services.datastage.models.extractor import FlowExtractor

@Flow.register("datastage")
class DataStageFlow(Flow, FlowComposer):
    rcp: bool = False
    acp: bool = True
    _project : "Project" = None
    name : str = "unnamed_flow"
    description : str = ""
    # env : Environment = None
    flow_id : str = ""

    def __init__(self,
                 project = None,
                 **kwargs):
        """Initialize a DataStage flow.

        Args:
           project: The project for the flow to be created in. If None, then the flow is not created remotely.
           name: The flow name.
           description: The flow description.
           flow_type: The type of flow. This should always be datastage.
        """

        Flow.__init__(self, **kwargs)
        FlowComposer.__init__(self, DAG())
        self._project = project

    # def use_data_definition(self, data_definition: DataDefinition):
    #     self.data_definitions.append(data_definition)
    #     return self

    # def use_message_handler(self, message_handler: MessageHandler):
    #     self.message_handlers.append(message_handler)
    #     return self

    # def use_local_message_handler(self, local_message_handler: LocalMessageHandler):
    #     self.local_message_handler = local_message_handler
    #     return self

    # def use_paramset(self, paramset: ParameterSet):
    #     self.parameter_sets.append(paramset)
    #     return self

    # def use_localparams(self, localparams: LocalParameters):
    #     self.local_parameters = localparams
    #     return self

    # def use_runtime(self, runtime: Runtime):
    #     self.runtime = runtime
    #     return self

    def use_runtime_column_propagation(self, rcp: bool = True):
        self.rcp = rcp
        return self

    def use_auto_column_propagation(self, acp: bool = True):
        self.acp = acp
        return self

    # def _add_ghost_node(self) -> Node:
    #     node = GhostNode(self._dag)
    #     self._dag.add_node(node)
    #     return node

    def remove_stage(self, node: Node) -> None:
        """Removes a node from the flow.

        Args:
            node: The node to be removed.
        """
        self._dag.remove_node(node)

    # def add_markdown_comment(self, text: str) -> MarkdownComment:
    #     comment = MarkdownComment(self._dag, content=text)
    #     self._dag.add_node(comment)
    #     return comment

    # def add_styled_comment(self, text: str) -> StyledComment:
    #     comment = StyledComment(self._dag, content=text)
    #     self._dag.add_node(comment)
    #     return comment

    def get_link(self, source: Node, destination: Node) -> Link:
        """Gets the link between two nodes in the flow. If there are no links or multiple links, it raises an error.

        Args:
            source: Node from which the link originates.
            destination: Node to which the link points.

        Returns:
            The single link between the source and destination nodes.
        """
        links = self._dag.get_links_between(source, destination)
        if len(links) == 0:
            raise ValueError("No link between nodes")
        if len(links) > 1:
            raise ValueError("Multiple links between nodes")
        return links[0]

    def get_links(self, source: Node, destination: Node) -> list[Link]:
        """Gets all links between two nodes in the flow.

        Args:
            source: Node from which the links originate.
            destination: Node to which the links point.

        Returns:
            A list of Links between the source and destination nodes.
        """
        return self._dag.get_links_between(source, destination)

    def _dag_to_json(self) -> str:
        self._dag.compute_metadata()
        lay = LayeredLayout(self._dag)
        lay.compute()

        # # Compute layout for child DAGs for local subflows
        # for node in self._dag.nodes():
        #     if isinstance(node, SuperNode) and node.is_local:
        #         node.subflow_dag.compute_metadata()
        #         sub_lay = LayeredLayout(node.subflow_dag)
        #         sub_lay.compute()

        ser = FlowExtractor(self)
        ser.extract()

        flow_model = ser.serialize()
        return flow_model.model_dump_json(indent=2, exclude_none=True, by_alias=True, warnings=False)

    @staticmethod
    def _create(project: "Project" = None,
                name: str = "unnamed_flow",
                environment: Environment = None,
                description: str = "",
                flow_type: str = "datastage",
                ) -> "DataStageFlow":
        # self.parameter_sets: list[ParameterSet] = []
        # self.local_parameters: LocalParameters | None = None
        # self.runtime: Runtime | None = None
        # self.message_handlers: list[MessageHandler] = []
        # self.local_message_handler: LocalMessageHandler | None = None
        # self.data_definitions: list[DataDefinition] = []

        flow_name = name

        test_json : dict = {
            "primary_pipeline" : "",
            "pipelines" : [ {
                "nodes" : [ ],
                "description" : "",
                "id" : "",
                "app_data" : {
                "datastage" : { },
                "ui_data" : {
                    "comments" : [ ]
                }
                },
                "runtime_ref" : ""
            } ],
            "json_schema" : "http://api.dataplatform.ibm.com/schemas/common-pipeline/pipeline-flow/pipeline-flow-v3-schema.json",
            "schemas" : [ ],
            "doc_type" : "pipeline",
            "id" : "",
            "app_data" : {
                "datastage" : { }
            },
            "version" : "3.0"
        }
        project_id = project.metadata.guid

        response = project._platform._datastage_flow_api.create_datastage_flows(
            data_intg_flow_name=flow_name,
            pipeline_flows=test_json,
            project_id=project_id,
        )

        flow = DataStageFlow(project=project, name=name, description=description, flow_type=flow_type, flow_id = response.json()["metadata"]["asset_id"])
        return flow

    @staticmethod
    def create_or_get(project: "Project" = None,
                name: str = "unnamed_flow",
                environment: Environment = None,
                description: str = "",
                flow_type: str = "datastage",
                ) -> "DataStageFlow":
        """Either creates the flow with the given name or returns the preexisting flow of that name."""
        try:
            return project.datastage_flows.get(name = name)
        except ValueError:
            return DataStageFlow._create(project, name, environment, description, flow_type)

    def _update(self) -> requests.Response:
        flow_name = self.name
        flow_json = json.loads(self._dag_to_json())
        project_id = self._project.metadata.guid
        response = self._project._platform._datastage_flow_api.update_datastage_flows(
            data_intg_flow_id=self.flow_id,
            data_intg_flow_name=flow_name,
            pipeline_flows=flow_json,
            project_id=project_id,
        )
        return response

    def _delete(self) -> requests.Response:
        return self._project._platform._datastage_flow_api.delete_datastage_flows(
            id=[self.flow_id],
            project_id=self._project.metadata.guid,
        )

    def compile(self) -> requests.Response:
        flow_json = self._dag_to_json()
        project_id = self._project.metadata.guid

        response = self._project._platform._datastage_flow_api.compile_datastage_flows(
            data_intg_flow_id=self.flow_id,
            pipeline_flows=flow_json,
            project_id=project_id,
        )
        return response

    def _duplicate(self, name : str, description: str) -> "DataStageFlow":
        project_id = self._project.metadata.guid

        response = self._project._platform._datastage_flow_api.clone_datastage_flows(
            data_intg_flow_id=self.flow_id,
            project_id=project_id,
            data_intg_flow_name=name,
            description=description
        )
        flow = DataStageFlow(project=self._project, name=name, description=description, flow_type="datastage", flow_id = response.json()["metadata"]["asset_id"])
        return flow

    def get_compile_status(self) -> requests.Response:
        project_id = self._project.metadata.guid
        response = self._project._platform._datastage_flow_api.get_flow_compile_status(data_intg_flow_id=self.flow_id, project_id=project_id)
        return response

    def get_compile_info(self) -> requests.Response:
        project_id = self._project.metadata.guid
        response = self._project._platform._datastage_flow_api.datastage_flows_compile_info(data_intg_flow_id=self.flow_id, project_id=project_id)
        return response

class DataStageFlows(CollectionModel):
    """Collection of DataStageFlow objects."""

    def __init__(self, project: "Project") -> None:
        """The __init__ of the DataStageFlows class.

        Args:
            project: The Project object.
        """
        super().__init__(project)
        self._project = project
        self.unique_id = "flow_id"

    def _request_parameters(self) -> list:
        return ["data_intg_flow_id",
                "project_id",
                "catalog_id",
                "space_id",
                "sort",
                "start",
                "limit",
                "entity.name",
                "entity.description"]

    def __len__(self) -> int:
        """The len of the DataStageFlows class."""
        query_params = {
            "project_id": self._project.metadata.guid,
        }
        res = self._project._platform._datastage_flow_api.list_datastage_flows(**query_params)
        res_json = res.json()
        return res_json["total_count"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        if "start" in request_params:
            parsed_url = urlparse(request_params["start"]["href"])
            params = parse_qs(parsed_url.query)
            request_params["start"] = params.get("start", [None])[0]

        request_params_defaults = {
            "data_intg_flow_id": None,
            "project_id": self._project.metadata.guid,
            "catalog_id": None,
            "space_id": None,
            "sort": None,
            "start": None,
            "limit": 100,
            "entity.name": None,
            "entity.description": None,
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)

        if "entity.name" in request_params_unioned:
            request_params_unioned["entity_name"] = request_params_unioned.get("entity.name")
        if "entity.description" in request_params_unioned:
            request_params_unioned["entity_description"] = request_params_unioned.get("entity.description")

        if "data_intg_flow_id" in request_params:
            response_json = self._project._platform._datastage_flow_api.get_datastage_flows(
                **{k: v for k, v in request_params_unioned.items() if v is not None},
                data_intg_flow_id=request_params["data_intg_flow_id"],
            ).json()
            response = {"data_flows": [response_json]}

        else:
            response = self._project._platform._datastage_flow_api.list_datastage_flows(
                **{k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()

        # Create parameters for construction
        for flow_json in response["data_flows"]:
            flow_json["flow_id"] = flow_json["metadata"]["asset_id"]
            flow_json["name"] = flow_json["metadata"]["name"]
            flow_json["description"] = flow_json["metadata"]["description"]

        return CollectionModelResults(
            results=response,
            class_type=DataStageFlow,
            response_bookmark="next",
            request_bookmark="start",
            response_location="data_flows",
            constructor_params={"project": self._project},
        )

class DataStageFlowPayloadExtender(PayloadExtender):
    """DataStage flow extender setup also compiles the flow.

    :meta: private
    """

    @override
    def extend(self, payload: dict[str, Any], flow: Flow) -> dict[str, Any]:
        flow.compile()
        payload["asset_ref"] = flow.flow_id
        return payload
