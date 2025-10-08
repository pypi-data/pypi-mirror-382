import json
from ibm_watsonx_data_integration.services.datastage.models.extractor import FlowExtractor
from ibm_watsonx_data_integration.services.datastage.models.flow import DataStageFlow

# from ibm_watsonx_data_integration.services.datastage._console import console
from ibm_watsonx_data_integration.services.datastage.models.flow_runner import FlowRunner
from ibm_watsonx_data_integration.services.datastage.models.layout import LayeredLayout
from ibm_watsonx_data_integration.services.datastage.models.log_transformer import transform_logs
from pathlib import Path
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from typing import Literal


class DataStageSDK:
    # def __init__(self, config: Config = None):
    #     self.config = config or AutoDetectConfig()

    # def _resolve_or_create_connections(
    #     self, dag: DAG, duplicate_assets: Literal["Skip", "Rename", "Overwrite"]
    # ):
    #     # should we update imported connections?
    #     cc = CreateConnection(config=self.config)
    #     for node in dag.nodes():
    #         if isinstance(node, SuperNode):
    #             continue
    #         if (
    #             not hasattr(node, "configuration")
    #             or "connection" not in vars(node.configuration)
    #             or not node.configuration.connection
    #             # or node.configuration.connection.asset_id
    #         ):
    #             continue
    #         _, exclude = node.configuration.connection.validate()
    #         conflict = exclude & node.configuration.connection.model_fields_set
    #         if conflict:
    #             conflict = list(conflict)
    #             if len(conflict) == 1:
    #                 warnings.warn(
    #                     f"\n\033[33mFound conflicting property: {conflict[0]}\033[0m"
    #                 )
    #             else:
    #                 warnings.warn(
    #                     f"\n\033[33mFound conflicting properties {', '.join(conflict[:-1])} and {conflict[-1]}\033[0m"
    #                 )
    #         exclude = exclude - node.configuration.connection.model_fields_set
    #         properties = json.loads(
    #             node.configuration.connection.model_dump_json(
    #                 exclude={"asset_id", "proj_id", "name"} | exclude,
    #                 exclude_none=True,
    #                 warnings=False,
    #                 by_alias=True,
    #             )
    #         )
    #         connection_name = node.configuration.connection.name
    #         datasource_type = node.configuration.connection.datasource_type
    #         response, connection_name = cc.handle_connection(
    #             connection_name=connection_name,
    #             properties=properties,
    #             datasource_type=datasource_type,
    #             duplicate_assets=duplicate_assets,
    #         )
    #         response = cc.list_connections(entity_name=connection_name)

    #         asset_id = None
    #         for conn in response.result["resources"]:
    #             if conn["entity"]["name"] == connection_name:
    #                 asset_id = conn["metadata"]["asset_id"]
    #         if not asset_id:
    #             raise ValueError(
    #                 f'No asset ID found for created connection "{connection_name}"'
    #             )

    #         node.configuration.connection.proj_id = self.config._get_project_id()
    #         node.configuration.connection.asset_id = asset_id

    # def _resolve_or_create_data_definitions(
    #     self,
    #     flow: DataStageFlow,
    #     duplicate_assets: Literal["Skip", "Rename", "Overwrite"],
    # ):
    #     dd = CreateDataDefinition(config=self.config)
    #     for data_definition in flow.data_definitions:
    #         if (
    #             "asset_id" in vars(data_definition)
    #             and vars(data_definition)["asset_id"]
    #             and "proj_id" in vars(data_definition)
    #             and vars(data_definition)["asset_id"]
    #         ):
    #             continue
    #         properties = data_definition.model_dump(include={"name"})
    #         properties["metadata"] = data_definition._get_metadata_props()
    #         properties["entity"] = data_definition._get_entity_props()
    #         response, data_definition_name = dd.handle_data_definition(
    #             properties, duplicate_assets
    #         )
    #         data_definition.name = data_definition_name
    #         asset_id = response.result["metadata"]["asset_id"]
    #         proj_id = self.config._get_project_id()
    #         data_definition.asset_id = asset_id
    #         data_definition.proj_id = proj_id

    # def _resolve_or_create_paramsets(
    #     self,
    #     parameter_sets: list[ParameterSet],
    #     duplicate_assets: Literal["Skip", "Rename", "Overwrite"],
    # ):
    #     ps = CreateParamSet(config=self.config)
    #     for paramset in parameter_sets:
    #         if (
    #             "asset_id" in vars(paramset)
    #             and vars(paramset)["asset_id"]
    #             and "proj_id" in vars(paramset)
    #             and vars(paramset)["proj_id"]
    #         ):
    #             continue
    #         properties = paramset.model_dump(
    #             exclude_none=True, exclude={"asset_id", "proj_id"}, warnings=False
    #         )
    #         response, paramset_name = ps.handle_param_set(
    #             properties=properties, duplicate_assets=duplicate_assets
    #         )
    #         paramset.name = paramset_name
    #         asset_id = response.result["metadata"]["asset_id"]
    #         proj_id = self.config._get_project_id()
    #         paramset.asset_id = asset_id
    #         paramset.proj_id = proj_id

    # def _resolve_or_create_function_libraries(
    #     self, dag: DAG, duplicate_assets: Literal["Skip", "Rename", "Overwrite"]
    # ):
    #     fl = CreateFunctionLibrary(config=self.config)
    #     for node in dag.nodes():
    #         if (
    #             not hasattr(node, "configuration")
    #             or "function_library" not in vars(node.configuration)
    #             or not node.configuration.function_library
    #             or node.configuration.function_library.asset_id
    #         ):
    #             continue
    #         function_library = node.configuration.function_library
    #         properties = function_library.model_dump(
    #             exclude_none=True, exclude={"asset_id", "proj_id"}, warnings=False
    #         )
    #         response, function_library_name = fl.handle_function_library(
    #             properties=properties, duplicate_assets=duplicate_assets
    #         )
    #         function_library.name = function_library_name
    #         asset_id = response.result["metadata"]["asset_id"]
    #         proj_id = self.config._get_project_id()
    #         function_library.asset_id = asset_id
    #         function_library.proj_id = proj_id

    # def _resolve_or_create_match_specifications(
    #     self, dag: DAG, duplicate_assets: Literal["Skip", "Rename", "Overwrite"]
    # ):
    #     cms = CreateMatchSpecification(config=self.config)
    #     for node in dag.nodes():
    #         if (
    #             not hasattr(node, "configuration")
    #             or "match_specification" not in vars(node.configuration)
    #             or not node.configuration.match_specification
    #             or node.configuration.match_specification.asset_id
    #         ):
    #             continue
    #         match_specification = node.configuration.match_specification
    #         properties = match_specification.model_dump(
    #             exclude_none=True, exclude={"asset_id", "proj_id"}, warnings=False
    #         )
    #         response, match_specification_name = cms.handle_match_specification(
    #             properties=properties, duplicate_assets=duplicate_assets
    #         )
    #         match_specification.name = match_specification_name
    #         asset_id = response.result["metadata"]["asset_id"]
    #         proj_id = self.config._get_project_id()
    #         match_specification.asset_id = asset_id
    #         match_specification.proj_id = proj_id

    # def _resolve_or_create_message_handlers(
    #     self,
    #     message_handlers: list[MessageHandler],
    #     duplicate_assets: Literal["Skip", "Rename", "Overwrite"],
    # ):
    #     mh = CreateMessageHandler(config=self.config)
    #     for message_handler in message_handlers:
    #         if (
    #             "asset_id" in vars(message_handler)
    #             and vars(message_handler)["asset_id"]
    #             and "proj_id" in vars(message_handler)
    #             and vars(message_handler)["proj_id"]
    #         ):
    #             continue
    #         properties = message_handler.model_dump(
    #             exclude_none=True, exclude={"asset_id", "proj_id"}, warnings=False
    #         )
    #         response, message_handler_name = mh.handle_message_handler(
    #             properties=properties,
    #             has_file=message_handler.msh_content != None,
    #             duplicate_assets=duplicate_assets,
    #         )
    #         message_handler.name = message_handler_name
    #         asset_id = response.result["metadata"]["asset_id"]
    #         proj_id = self.config._get_project_id()
    #         message_handler.asset_id = asset_id
    #         message_handler.proj_id = proj_id

    # def _resolve_or_create_subflows(
    #     self, dag: DAG, duplicate_assets: Literal["Skip", "Rename", "Overwrite"]
    # ):
    #     cs = CreateSubflow(config=self.config)
    #     subflows_data = []
    #     for node in dag.nodes():
    #         # Only do this for reusable subflows
    #         if isinstance(node, SuperNode) and not node.is_local:
    #             if node.url and node.pipeline_id:
    #                 # Skip if the subflow is already created / processed
    #                 continue

    #             # Fetch the subflow if it is imported by ID
    #             if node.asset_id and not node.subflow_dag:
    #                 subflow = self.get_subflow(id=node.asset_id)
    #                 node.subflow_dag = subflow.dag
    #                 node.name = subflow.name
    #                 node.entry_nodes = subflow.entry_nodes
    #                 node.exit_nodes = subflow.entry_nodes
    #                 node.is_local = subflow.is_local

    #             # Process nested subflows first, as we need their IDs
    #             subflow_data = self._resolve_or_create_subflows(
    #                 node.subflow_dag, duplicate_assets
    #             )
    #             subflows_data.extend(subflow_data)

    #             # Compute layout
    #             node.subflow_dag.compute_metadata()
    #             lay = LayeredLayout(node.subflow_dag)
    #             lay.compute()

    #             # Process subflow parameter sets
    #             self._resolve_or_create_paramsets(node.parameter_sets, duplicate_assets)

    #             ser = SubflowExtractor(
    #                 node.subflow_dag,
    #                 node.parameter_sets,
    #                 node.local_parameters,
    #                 subflow_data=subflow_data,
    #             )
    #             ser.extract()
    #             subflow_model = ser.serialize()

    #             subflow_json = subflow_model.model_dump_json(
    #                 indent=2, exclude_none=True, by_alias=True, warnings=False
    #             )

    #             subflow_obj = json.loads(subflow_json)

    #             used_subflow = False
    #             for subflow_item in subflows_data:
    #                 if (
    #                     "subflow_name" in subflow_item
    #                     and subflow_item["subflow_name"] == node.name
    #                 ):
    #                     node.pipeline_id = (
    #                         subflow_item["pipeline_id"]
    #                         if "pipeline_id" in subflow_item
    #                         else None
    #                     )
    #                     original_id = subflow_obj["primary_pipeline"]
    #                     subflow_obj["primary_pipeline"] = node.pipeline_id
    #                     for pipeline in subflow_obj["pipelines"]:
    #                         if "id" in pipeline and pipeline["id"] == original_id:
    #                             pipeline["id"] = node.pipeline_id
    #                     used_subflow = True

    #             response, subflow_name = cs.handle_subflow(
    #                 subflow_json=subflow_obj,
    #                 subflow_name=node.name,
    #                 duplicate_assets=duplicate_assets,
    #             )
    #             node.name = subflow_name
    #             asset_id = response.result["metadata"]["asset_id"]
    #             proj_id = self.config._get_project_id()

    #             if not used_subflow or not node.pipeline_id:
    #                 node.pipeline_id = ser.pipelines[ser.top_level_dag].id

    #             node.url = (
    #                 self.config._get_environment()._get_flow_service().service_url
    #                 + "/data_intg/v3/data_intg_flows/subflows/"
    #                 + asset_id
    #                 + "?project_id="
    #                 + proj_id
    #             )

    #             subflow_data = {
    #                 "id": asset_id,
    #                 "subflow_label": node.label,
    #                 "subflow_name": node.name,
    #                 "subflow_json": subflow_obj,
    #                 "subflow_url": node.url,
    #                 "pipeline_id": node.pipeline_id,
    #             }
    #             subflows_data.append(subflow_data)

    #     return subflows_data

    # def _resolve_or_create_java_libraries(
    #     self, dag: DAG, duplicate_assets: Literal["Skip", "Rename", "Overwrite"]
    # ):
    #     jl = CreateJavaLibrary(config=self.config)
    #     for node in dag.nodes():
    #         if (
    #             not hasattr(node, "configuration")
    #             or "java_library" not in vars(node.configuration)
    #             or not node.configuration.java_library
    #             or node.configuration.java_library.asset_id
    #         ):
    #             continue
    #         java_library = node.configuration.java_library
    #         properties = java_library.model_dump(
    #             exclude_none=True, exclude={"asset_id", "proj_id"}, warnings=False
    #         )
    #         response, java_library_name = jl.handle_java_library(
    #             properties=properties, duplicate_assets=duplicate_assets
    #         )
    #         java_library.name = java_library_name
    #         asset_id = response.result["metadata"]["asset_id"]
    #         proj_id = self.config._get_project_id()
    #         java_library.asset_id = asset_id
    #         java_library.proj_id = proj_id

    #         user_class = response.result["entity"]["primary"][
    #             os.path.basename(java_library.primary_file)
    #         ][node.configuration.user_class_name]
    #         if "capabilities" in user_class:
    #             capabilities = user_class["capabilities"]
    #             node.configuration.min_inputs = capabilities[
    #                 "minimum_input_link_count:"
    #             ]
    #             node.configuration.max_inputs = capabilities[
    #                 "maximum_input_link_count:"
    #             ]
    #             node.configuration.min_outputs = capabilities[
    #                 "minimum_output_stream_link_count:"
    #             ]
    #             node.configuration.max_outputs = capabilities[
    #                 "maximum_output_stream_link_count:"
    #             ]
    #             node.configuration.min_reject_outputs = capabilities[
    #                 "minimum_reject_link_count:"
    #             ]
    #             node.configuration.max_reject_outputs = capabilities[
    #                 "maximum_reject_link_count:"
    #             ]

    # def _resolve_or_create_build_stages(
    #     self,
    #     flow: DataStageFlow,
    #     duplicate_assets: Literal["Skip", "Rename", "Overwrite"],
    # ):
    #     cbs = CreateBuildStage(config=self.config)
    #     for node in flow._dag.nodes():
    #         if not isinstance(node, BuildStageStage):
    #             continue
    #         if (
    #             hasattr(node, "build_stage")
    #             and isinstance(node.build_stage, BuildStage)
    #             and node.build_stage.asset_id is not None
    #         ):
    #             continue
    #         ser = BuildStageExtractor(build_stage=node.build_stage, flow=flow)
    #         build_stage_model = ser.serialize()

    #         response, build_stage_name = cbs.handle_build_stage(
    #             properties=build_stage_model, duplicate_assets=duplicate_assets
    #         )
    #         node.build_stage.name = build_stage_name
    #         asset_id = response.result["metadata"]["asset_id"]
    #         proj_id = self.config._get_project_id()

    #         node.build_stage.asset_id = asset_id
    #         node.build_stage.proj_id = proj_id

    # def _resolve_or_create_wrapped_stages(
    #     self,
    #     flow: DataStageFlow,
    #     duplicate_assets: Literal["Skip", "Rename", "Overwrite"],
    # ):
    #     cws = CreateWrappedStage(config=self.config)
    #     for node in flow._dag.nodes():
    #         if not isinstance(node, WrappedStageStage):
    #             continue
    #         if (
    #             hasattr(node, "wrapped_stage")
    #             and isinstance(node.wrapped_stage, WrappedStage)
    #             and node.wrapped_stage.asset_id is not None
    #         ):
    #             continue
    #         ser = WrappedStageExtractor(wrapped_stage=node.wrapped_stage, flow=flow)
    #         wrapped_stage_model = ser.serialize()

    #         response, wrapped_stage_name = cws.handle_wrapped_stage(
    #             properties=wrapped_stage_model, duplicate_assets=duplicate_assets
    #         )
    #         node.wrapped_stage.name = wrapped_stage_name
    #         asset_id = response.result["metadata"]["asset_id"]
    #         proj_id = self.config._get_project_id()

    #         node.wrapped_stage.asset_id = asset_id
    #         node.wrapped_stage.proj_id = proj_id

    # def _resolve_or_create_custom_stages(
    #     self, dag: DAG, duplicate_assets: Literal["Skip", "Rename", "Overwrite"]
    # ):
    #     ccs = CreateCustomStage(config=self.config)
    #     for node in dag.nodes():
    #         if not isinstance(node, CustomStageStage):
    #             continue
    #         if (
    #             hasattr(node, "custom_stage")
    #             and isinstance(node.custom_stage, CustomStage)
    #             and node.custom_stage.asset_id is not None
    #         ):
    #             continue
    #         ser = CustomStageExtractor(custom_stage=node.custom_stage)
    #         custom_stage_model = ser.serialize()

    #         response, custom_stage_name = ccs.handle_custom_stage(
    #             properties=custom_stage_model, duplicate_assets=duplicate_assets
    #         )
    #         node.custom_stage.name = custom_stage_name
    #         asset_id = response.result["metadata"]["asset_id"]
    #         proj_id = self.config._get_project_id()

    #         node.custom_stage.asset_id = asset_id
    #         node.custom_stage.proj_id = proj_id

    # def _resolve_connections(self, dag: DAG):
    #     for node in dag.nodes():
    #         if (
    #             not hasattr(node, "configuration")
    #             or "connection" not in vars(node.configuration)
    #             or not node.configuration.connection
    #             or node.configuration.connection.asset_id
    #         ):
    #             continue
    #         node.configuration.connection.asset_id = uuid4().__str__()

    # def _resolve_paramsets(self, flow: DataStageFlow):
    #     for paramset in flow.parameter_sets:
    #         if (
    #             "asset_id" in vars(paramset)
    #             and vars(paramset)["asset_id"]
    #             and "proj_id" in vars(paramset)
    #             and vars(paramset)["proj_id"]
    #         ):
    #             continue
    #         paramset.asset_id = uuid4().__str__()

    # def _resolve_function_libraries(self, dag: DAG):
    #     for node in dag.nodes():
    #         if (
    #             not hasattr(node, "configuration")
    #             or "function_library" not in vars(node.configuration)
    #             or not node.configuration.function_library
    #             or node.configuration.function_library.asset_id
    #         ):
    #             continue
    #         node.configuration.function_library.asset_id = uuid4().__str__()

    # def _resolve_match_specifications(self, dag: DAG):
    #     for node in dag.nodes():
    #         if (
    #             not hasattr(node, "model")
    #             or "match_specification" not in vars(node.model)
    #             or not node.model.match_specification
    #             or node.model.match_specification.asset_id
    #         ):
    #             continue
    #         node.model.match_specification.asset_id = uuid4().__str__()

    # def _resolve_message_handlers(self, fc: DataStageFlow):
    #     for message_handler in fc.message_handlers:
    #         if (
    #             "asset_id" in vars(message_handler)
    #             and vars(message_handler)["asset_id"]
    #             and "proj_id" in vars(message_handler)
    #             and vars(message_handler)["proj_id"]
    #         ):
    #             continue
    #         message_handler.asset_id = uuid4().__str__()

    # def _resolve_subflows(self, flow: DataStageFlow):
    #     for node in flow._dag.nodes():
    #         if isinstance(node, SuperNode) and not node.is_local:
    #             if node.url and node.pipeline_id:
    #                 continue
    #             node.url = (
    #                 self.config._get_environment()._get_flow_service().service_url
    #                 + "/data_intg/v3/data_intg_flows/subflows/"
    #                 + uuid4().__str__()
    #                 + "?project_id="
    #                 + self.config._get_project_id()
    #             )
    #             node.pipeline_id = uuid4().__str__()

    # def _resolve_build_stages(self, flow: DataStageFlow):
    #     for node in flow._dag.nodes():
    #         if isinstance(node, BuildStageStage):
    #             if node.build_stage.asset_id:
    #                 continue
    #             node.build_stage.asset_id = uuid4().__str__()
    #             node.build_stage.operator = ""

    # def _resolve_wrapped_stages(self, flow: DataStageFlow):
    #     for node in flow._dag.nodes():
    #         if isinstance(node, WrappedStageStage):
    #             if node.wrapped_stage.asset_id:
    #                 continue
    #             node.wrapped_stage.asset_id = uuid4().__str__()
    #             node.wrapped_stage.wrapper_name = ""

    # def _resolve_custom_stages(self, flow: DataStageFlow):
    #     for node in flow._dag.nodes():
    #         if isinstance(node, CustomStageStage):
    #             if node.custom_stage.asset_id:
    #                 continue
    #             node.custom_stage.asset_id = uuid4().__str__()
    #             node.custom_stage.operator = ""

    # def _resolve_java_libraries(self, dag: DAG):
    #     for node in dag.nodes():
    #         if (
    #             not hasattr(node, "configuration")
    #             or "java_library" not in vars(node.configuration)
    #             or not node.configuration.java_library
    #             or node.configuration.java_library.asset_id
    #         ):
    #             continue
    #         node.configuration.java_library.asset_id = uuid4().__str__()

    # def __get_runtime_parameters(
    #     self, flow: DataStageFlow, runtime_parameters: RuntimeParameters = None
    # ):
    #     param_sets = []

    #     if not runtime_parameters:
    #         for param_set in flow.parameter_sets:
    #             param_sets.append({"name": param_set.name, "ref": param_set.asset_id})

    #     else:
    #         for ps, vs in runtime_parameters.value_sets.items():
    #             found_ps = False
    #             found_vs = False
    #             for param_set in flow.parameter_sets:
    #                 if ps == param_set.name:
    #                     found_ps = True
    #                     for value_set in param_set.value_sets:
    #                         if value_set.name == vs:
    #                             found_vs = True
    #                             param_sets.append(
    #                                 {
    #                                     "name": param_set.name,
    #                                     "ref": param_set.asset_id,
    #                                     "value_set": value_set.name,
    #                                 }
    #                             )
    #                             break
    #                     if not found_vs or vs.lower() == "default":
    #                         param_sets.append(
    #                             {"name": param_set.name, "ref": param_set.asset_id}
    #                         )

    #             if not found_ps:
    #                 warnings.warn(
    #                     f"\n\033[33mCannot find parameter set {ps} within flow. Excluding from runtime parameters...\033[0m"
    #                 )
    #             elif not found_vs and vs.lower() != "default":
    #                 warnings.warn(
    #                     f"\n\033[33mCannot find value set {vs} within parameter set {ps}. Using default parameters...\033[0m"
    #                 )

    #         for param_set in flow.parameter_sets:
    #             if param_set.name not in runtime_parameters.value_sets:
    #                 param_sets.append(
    #                     {
    #                         "name": param_set.name,
    #                         "ref": param_set.asset_id,
    #                     }
    #                 )

    #     return param_sets

    def create_flow(
        self,
        flow: DataStageFlow,
        flow_name: str,
        duplicate_assets: Literal["Skip", "Rename", "Overwrite"] = "Overwrite",
    ) -> None:
        """Creates a DataStage flow in the project with the flow constructed using the provided :class:`DataStageFlow`.
        If the flow with the same name already exists, it will be replaced.

        Args:
            flow: Flow composer object used to construct the flow.
            flow_name: Name of the flow to create in the project.

        """
        # self._resolve_or_create_connections(flow._dag, duplicate_assets)
        # self._resolve_or_create_data_definitions(flow, duplicate_assets)
        # self._resolve_or_create_paramsets(flow.parameter_sets, duplicate_assets)
        # self._resolve_or_create_function_libraries(flow._dag, duplicate_assets)
        # self._resolve_or_create_match_specifications(flow._dag, duplicate_assets)
        # self._resolve_or_create_message_handlers(
        #     flow.message_handlers, duplicate_assets
        # )
        # self._resolve_or_create_subflows(flow._dag, duplicate_assets)
        # self._resolve_or_create_java_libraries(flow._dag, duplicate_assets)
        # self._resolve_or_create_build_stages(flow, duplicate_assets)
        # self._resolve_or_create_wrapped_stages(flow, duplicate_assets)
        # self._resolve_or_create_custom_stages(flow._dag, duplicate_assets)
        flow_json = flow._dag_to_json()
        flow_obj = json.loads(flow_json)

        fr = FlowRunner(config=self.config)
        fr.create_or_replace_flow(flow_name, flow_obj, duplicate_assets)

    def delete_flow(self, flow_name: str) -> None:
        fr = FlowRunner(config=self.config)
        fr.delete_flow(flow_name=flow_name)

    def run_flow(
        self,
        flow: DataStageFlow,
        flow_name: str,
        # job_settings: JobSettings = None,
        print_logs: bool = False,
        time_limit: int = 0,
        duplicate_assets: Literal["Skip", "Rename", "Overwrite"] = "Overwrite",
    ) -> str:
        """Creates and runs the flow in the project with the flow constructed using the provided :class:`DataStageFlow`.
        If the flow with the same name already exists, it will be replaced.

        Args:
            flow: Flow composer object used to compose the flow.
            flow_name: Name of the flow to create and run.
            job_settings: The specified job settings for the run
            print_logs: Whether to print the logs of the flow run.
            time_limit: Time in seconds to wait before failing. If 0 or negative, then no time limit.

        Returns:
            The logs of the flow run.

        """
        with Progress(
            TimeElapsedColumn(),
            BarColumn(),
            TaskProgressColumn(),
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task1 = progress.add_task(total=150, description="Resolving connections")

            self._resolve_or_create_connections(flow._dag, duplicate_assets)
            progress.update(task1, completed=10, description="Resolving parameter sets")

            # self._resolve_or_create_data_definitions(flow, duplicate_assets)
            # self._resolve_or_create_paramsets(flow.parameter_sets, duplicate_assets)
            # self._resolve_or_create_function_libraries(flow._dag, duplicate_assets)
            # self._resolve_or_create_match_specifications(flow._dag, duplicate_assets)
            # self._resolve_or_create_message_handlers(
            #     flow.message_handlers, duplicate_assets
            # )
            # progress.update(task1, completed=20, description="Resolving assets")

            # self._resolve_or_create_subflows(flow._dag, duplicate_assets)
            # self._resolve_or_create_build_stages(flow, duplicate_assets)
            # self._resolve_or_create_wrapped_stages(flow, duplicate_assets)
            # self._resolve_or_create_custom_stages(flow._dag, duplicate_assets)
            # self._resolve_or_create_java_libraries(flow._dag, duplicate_assets)
            progress.update(task1, completed=30, description="Serializing flow to JSON assets")

            # if job_settings and job_settings.runtime_parameters:
            #     param_sets = self.__get_runtime_parameters(
            #         flow, job_settings.runtime_parameters
            #     )
            # elif flow.runtime and flow.runtime.runtime_parameters:
            #     param_sets = self.__get_runtime_parameters(
            #         flow, flow.runtime.runtime_parameters
            #     )
            # else:
            #     param_sets = []

            flow_json = json.loads(flow._dag_to_json())
            progress.update(task1, completed=40, description="Uploading flow")

            fr = FlowRunner(config=self.config)
            # schedule = job_settings.schedule if job_settings else None

            response = fr.create_or_replace_flow(flow_name, flow_json, duplicate_assets)
            progress.update(task1, completed=50, description="Compiling flow")
            flow_id = response.result["metadata"]["asset_id"]

            compile_response = fr.compile_flow(flow_id=flow_id)
            # progress.update(task1, completed=50, description='Getting compile info')
            result = compile_response.result["message"]["result"]
            if result != "success":
                raise Exception("Flow compile failed")

            compile_status = fr.get_compile_info(flow_id=flow_id)
            progress.update(task1, completed=60, description="Getting current jobs")
            compiled = compile_status.result["metadata"]["compiled"]
            if not compiled:
                raise Exception("Flow compile failed")

            job_exists = False
            job_json = None
            job_id = None
            job_exist_response = fr.get_jobs(asset_ref=flow_id)
            for job in job_exist_response.result["results"]:
                if job["entity"]["job"]["asset_ref"] == flow_id:
                    job_exists = True
                    job_json = job
                    job_id = job["metadata"]["asset_id"]
                    break

            if job_exists:
                progress.update(task1, completed=70, description="Updating existing flow run job")
                _ = fr.update_job(
                    # paramsets=param_sets,
                    runtime=flow.runtime,
                    # schedule=schedule,
                    job_json=job_json,
                    job_id=job_id,
                )
            else:
                progress.update(task1, completed=70, description="Creating new flow run job")
                create_job_response = fr.create_job(
                    job_name=f"{flow_name}.SDK",
                    flow_id=flow_id,
                    # paramsets=param_sets,
                    runtime=flow.runtime,
                    # schedule=schedule,
                )
                job_id = create_job_response.result["metadata"]["asset_id"]

            progress.update(task1, completed=80, description="Starting job run")
            job_run_response = fr.run_job(job_id=job_id)
            progress.update(task1, completed=90, description="Waiting for job to finish")

            run_id = job_run_response.result["metadata"]["asset_id"]

            # def poll_job_status() -> DetailedResponse | None:
            #     """Continually poll job status. Returns a boolean representing whether job was completed or is still
            #     running.
            #     """
            #     start_time = time.monotonic()
            #     # Poll at most every 3 seconds
            #     lock = CooldownLock(3)

            #     while time_limit <= 0 or (time.monotonic() - start_time < time_limit):
            #         lock.acquire()
            #         res = fr.get_job_run(job_id=job_id, run_id=run_id)
            #         lock.release()
            #         st = res.result["entity"]["job_run"]["state"]
            #         if (
            #             st == "Completed"
            #             or st == "Canceled"
            #             or st == "Failed"
            #             or st == "CompletedWithErrors"
            #             or st == "CompletedWithWarnings"
            #         ):
            #             return res

            #     return None

            # job_status_response = poll_job_status()
            progress.update(task1, completed=140, description="Getting job logs")

            job_log_response = fr.get_job_log(job_id=job_id, run_id=run_id)
            progress.update(task1, completed=150, description="Completed")

        # if not job_status_response:
        #     console.print(
        #         "Job exceeded time limit. Track job status in DataStage dashboard"
        #     )

        transformed_logs = transform_logs(job_log_response.result["results"])
        if print_logs:
            for row in transformed_logs:
                pass
                # console.print(row)
        return "\n".join(transformed_logs)

    # def run_test_case(
    #     self,
    #     tcc: TestCaseComposer,
    #     test_case_name: str = None,
    #     job_settings: JobSettings = None,
    #     create_diff_file: bool = False,
    #     time_limit: int = 0,
    # ) -> str:
    #     """Creates and runs the test case in the project with the test case constructed using the provided :class:`TestCaseComposer`.
    #     If the test case with the same name already exists, it will be replaced.

    #     Args:
    #         tcc: Test case composer object used to compose the flow.
    #         test_case_name: Name of the test case to create and run.
    #         job_settings: The specified job settings for the test case
    #         create_diff_file: Whether to create the diff file of the test case run.
    #         time_limit: Time in seconds to wait before failing. If 0 or negative, then no time limit.

    #     Returns:
    #         The result of the test case run.

    #     """
    #     with Progress(
    #         TimeElapsedColumn(),
    #         BarColumn(),
    #         TaskProgressColumn(),
    #         SpinnerColumn(),
    #         TextColumn("[progress.description]{task.description}"),
    #     ) as progress:
    #         task1 = progress.add_task(total=150, description="Creating test case")

    #         tcr = TestCaseRunner(config=self.config)
    #         schedule = job_settings.schedule if job_settings else None
    #         tcc.use_schedule(schedule=schedule)

    #         response = tcr.create_or_replace_test_case(
    #             tcc=tcc, test_case_name=test_case_name
    #         )

    #         flow_id = response.result["metadata"]["asset_id"]

    #         job_exist_response = tcr.get_jobs()
    #         for job in job_exist_response.result["results"]:
    #             if job["entity"]["job"]["asset_ref"] == flow_id:
    #                 job_exists = True
    #                 job_json = job
    #                 job_id = job["metadata"]["asset_id"]
    #                 break

    #         progress.update(task1, completed=80, description="Starting job run")
    #         job_run_response = tcr.run_test_case_job(job_id=job_id)

    #         progress.update(
    #             task1, completed=90, description="Waiting for job to finish"
    #         )

    #         run_id = job_run_response.result["metadata"]["asset_id"]

    #         def poll_job_status() -> DetailedResponse | None:
    #             """Continually poll job status. Returns a boolean representing whether job was completed or is still
    #             running.
    #             """
    #             start_time = time.monotonic()
    #             # Poll at most every 3 seconds
    #             lock = CooldownLock(3)

    #             while time_limit <= 0 or (time.monotonic() - start_time < time_limit):
    #                 lock.acquire()
    #                 res = tcr.get_job_run(job_id=job_id, run_id=run_id)
    #                 lock.release()
    #                 st = res.result["entity"]["job_run"]["state"]
    #                 if (
    #                     st == "Completed"
    #                     or st == "Canceled"
    #                     or st == "Failed"
    #                     or st == "CompletedWithErrors"
    #                     or st == "CompletedWithWarnings"
    #                 ):
    #                     return res

    #             return None

    #         job_status_response = poll_job_status()
    #         progress.update(task1, completed=140, description="Getting job result")

    #         job_result = job_status_response.result["entity"]["job_run"][
    #             "configuration"
    #         ]["test_result"]

    #         progress.update(task1, completed=150, description="Completed")

    #     if job_result != "PASS" and create_diff_file:
    #         tcr.get_job_result(job_id=job_id, run_id=run_id)

    #     return job_result

    def export_flow_json(
        self,
        flow: DataStageFlow,
        duplicate_assets: Literal["Skip", "Rename", "Overwrite"] = "Overwrite",
    ) -> str:
        """Exports the given flow composed using :class:`DataStageFlow` as a JSON string.

        Args:
            flow: Flow composer object used to compose the flow.

        Returns:
            The JSON string representing the flow.

        """
        # self._resolve_or_create_connections(flow._dag, duplicate_assets)
        # self._resolve_or_create_data_definitions(flow, duplicate_assets)
        # self._resolve_or_create_paramsets(flow.parameter_sets, duplicate_assets)
        # self._resolve_or_create_function_libraries(flow._dag, duplicate_assets)
        # self._resolve_or_create_build_stages(flow, duplicate_assets)
        # self._resolve_or_create_wrapped_stages(flow, duplicate_assets)
        # self._resolve_or_create_custom_stages(flow._dag, duplicate_assets)
        # self._resolve_or_create_match_specifications(flow._dag, duplicate_assets)
        # self._resolve_or_create_message_handlers(
        #     flow.message_handlers, duplicate_assets
        # )
        # self._resolve_or_create_subflows(flow._dag, duplicate_assets)
        # self._resolve_or_create_java_libraries(flow._dag, duplicate_assets)
        return flow._dag_to_json()

    # def export_flow_json_offline(self, flow: DataStageFlow) -> str:
    #     self._resolve_connections(flow._dag)
    #     self._resolve_paramsets(flow)
    #     self._resolve_function_libraries(flow._dag)
    #     self._resolve_match_specifications(flow._dag)
    #     self._resolve_message_handlers(flow)
    #     self._resolve_subflows(flow)
    #     self._resolve_build_stages(flow)
    #     self._resolve_wrapped_stages(flow)
    #     self._resolve_custom_stages(flow)
    #     self._resolve_java_libraries(flow._dag)
    #     return flow._dag_to_json()

    def export_flow(self, flow: DataStageFlow, file: str) -> None:
        """Exports the given flow composed using :class:`DataStageFlow` to a JSON file.

        Args:
            flow: Flow composer object used to compose the flow.
            file: Path to the JSON file to save the flow.

        """
        flow_json = self.export_flow_json(flow)
        with open(Path(file).expanduser().resolve(), "w") as f:
            f.write(flow_json)

    def export_flow_offline(self, flow: DataStageFlow, file: str) -> None:
        flow_json = self.export_flow_json_offline(flow)
        with open(Path(file).expanduser().resolve(), "w") as f:
            f.write(flow_json)

    @staticmethod
    def _dag_to_json(flow: DataStageFlow) -> str:
        flow._dag.compute_metadata()
        lay = LayeredLayout(flow._dag)
        lay.compute()

        # Compute layout for child DAGs for local subflows
        for node in flow._dag.nodes():
            if isinstance(node, SuperNode) and node.is_local:
                node.subflow_dag.compute_metadata()
                sub_lay = LayeredLayout(node.subflow_dag)
                sub_lay.compute()

        ser = FlowExtractor(flow)
        ser.extract()

        flow_model = ser.serialize()
        return flow_model.model_dump_json(indent=2, exclude_none=True, by_alias=True, warnings=False)

    # @staticmethod
    # def _subflow_to_json(subflow: SuperNode) -> str:
    #     subflow.subflow_dag.compute_metadata()
    #     lay = LayeredLayout(subflow.subflow_dag)
    #     lay.compute()

    #     ser = SubflowExtractor(subflow.subflow_dag)
    #     ser.extract()
    #     subflow_model = ser.serialize()
    #     return subflow_model.model_dump_json(
    #         indent=2, exclude_none=True, by_alias=True, warnings=False
    #     )

    def op_name_to_conn_class(self, op_name: str):
        """Converts an operator name (usually snake_case) into the PascalCase class name of that stage."""
        split = op_name.split("_")
        caps = [part[0].upper() + part[1:] for part in split]
        return "".join(caps) + "Conn"

    # def get_data_definition(
    #     self, id: str | None = None, name: str | None = None
    # ) -> DataDefinition:
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")

    #     dd = CreateDataDefinition(self.config)
    #     if name:
    #         response = dd.list_data_definitions(asset_name=name)
    #         data_definition = None
    #         for data_def in response.result["table_definitions"]:
    #             if name == data_def["metadata"]["name"]:
    #                 data_definition = data_def
    #                 break
    #         if not data_definition:
    #             raise ValueError(f"Could not find data definition {name}")
    #         id = data_definition["metadata"]["asset_id"]

    #     response = dd.get_data_definition(asset_id=id)
    #     properties = response.result
    #     return DataDefinition.from_dict(properties)

    # def get_paramset(
    #     self, id: str | None = None, name: str | None = None
    # ) -> ParameterSet:
    #     """Imports a parameter set from the project by its ID or name. Only one of the parameters should be provided.

    #     Args:
    #         id: The ID of the parameter set to import.
    #         name: The name of the parameter set to import.

    #     Returns:
    #         A :class:`ParameterSet` object representing the imported parameter set.
    #     """
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")

    #     if id:
    #         ps = CreateParamSet(self.config)
    #         response = ps.get_param_set(parameter_set_id=id)
    #         properties = response.result["entity"]["parameter_set"]
    #         properties["asset_id"] = response.result["metadata"]["asset_id"]
    #         properties["proj_id"] = response.result["metadata"]["project_id"]
    #         return ParameterSet(**properties)

    #     # Importing by name
    #     ps = CreateParamSet(self.config)
    #     response = ps.list_param_sets(entity_name=name)
    #     parameter_set = None
    #     for paramset in response.result["parameter_sets"]:
    #         if name == paramset["metadata"]["name"]:
    #             parameter_set = paramset
    #             break
    #     if not parameter_set:
    #         raise ValueError(f"Could not find parameter set {name}")

    #     asset_id = parameter_set["metadata"]["asset_id"]
    #     response = ps.get_param_set(parameter_set_id=asset_id)
    #     properties = response.result["entity"]["parameter_set"]
    #     properties["asset_id"] = asset_id
    #     properties["proj_id"] = response.result["metadata"]["project_id"]
    #     return ParameterSet.from_dict(properties)

    # def get_message_handler(self, id: str | None = None, name: str | None = None):
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")
    #     cmh = CreateMessageHandler(self.config)
    #     if id is not None:
    #         response = cmh.get_message_handler(message_handler_id=id)
    #         properties = response.result["entity"]
    #         properties["asset_id"] = response.result["metadata"]["asset_id"]
    #         properties["proj_id"] = response.result["metadata"]["project_id"]
    #         properties["name"] = response.result["metadata"]["name"]
    #         properties["description"] = response.result["metadata"]["description"]
    #         return MessageHandler(**properties)
    #     elif name is not None:
    #         response = cmh.list_message_handlers(entity_name=name)
    #         message_handler = None
    #         for handler in response.result["assets"]:
    #             if name == handler["metadata"]["name"]:
    #                 message_handler = handler
    #                 break
    #         if not message_handler:
    #             raise ValueError(f"Could not find message handler {name}")
    #         asset_id = message_handler["metadata"]["asset_id"]
    #         response = cmh.get_message_handler(message_handler_id=asset_id)
    #         properties = response.result["entity"]
    #         properties["asset_id"] = asset_id
    #         properties["proj_id"] = response.result["metadata"]["project_id"]
    #         properties["name"] = response.result["metadata"]["name"]
    #         properties["description"] = response.result["metadata"]["description"]
    #         return MessageHandler(**properties)

    # def get_java_library(self, id: str | None = None, name: str | None = None):
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")
    #     cjl = CreateJavaLibrary(self.config)
    #     if id is not None:
    #         response = cjl.get_java_library(java_library_id=id)
    #         dir_path = os.getcwd() + "/attachments"
    #         if not os.path.exists(dir_path):
    #             os.mkdir(dir_path)
    #         entity = response.result["entity"]
    #         primary_jar_content = entity["primary_jar_content"]
    #         primary_jar_name = list(entity["primary"])[0]
    #         with open(dir_path + "/" + primary_jar_name, "wb") as f:
    #             f.write(base64.b64decode(primary_jar_content))
    #         properties = {}
    #         properties["primary_file"] = "attachments/" + primary_jar_name
    #         secondary_files = []
    #         for secondary_file in entity["secondary"]:
    #             with open(dir_path + "/" + secondary_file["jar_file_name"], "wb") as f:
    #                 f.write(base64.b64decode(secondary_file["jar_file_content"]))
    #             secondary_files.append("attachments/" + secondary_file["jar_file_name"])
    #         properties["secondary_files"] = secondary_files
    #         properties["name"] = response.result["metadata"]["name"]
    #         properties["description"] = response.result["metadata"]["description"]
    #         return JavaLibrary(**properties)
    #     elif name is not None:
    #         java_library_response = cjl.list_java_libraries(entity_name=name)
    #         java_library_exists = False
    #         java_library_id = None
    #         for jl in java_library_response.result["assets"]:
    #             if jl["metadata"]["name"] == name:
    #                 java_library_exists = True
    #                 java_library_id = jl["metadata"]["asset_id"]
    #                 break
    #         if not java_library_exists:
    #             raise ValueError(f"Could not find message handler {name}")
    #         response = cjl.get_java_library(java_library_id=java_library_id)
    #         dir_path = os.getcwd() + "/attachments"
    #         if not os.path.exists(dir_path):
    #             os.mkdir(dir_path)
    #         entity = response.result["entity"]
    #         primary_jar_content = entity["primary_jar_content"]
    #         primary_jar_name = list(entity["primary"])[0]
    #         with open(dir_path + "/" + primary_jar_name, "wb") as f:
    #             f.write(base64.b64decode(primary_jar_content))
    #         properties = {}
    #         properties["primary_file"] = "attachments/" + primary_jar_name
    #         secondary_files = []
    #         for secondary_file in entity["secondary"]:
    #             with open(dir_path + "/" + secondary_file["jar_file_name"], "wb") as f:
    #                 f.write(base64.b64decode(secondary_file["jar_file_content"]))
    #             secondary_files.append("attachments/" + secondary_file["jar_file_name"])
    #         properties["secondary_files"] = secondary_files
    #         properties["name"] = response.result["metadata"]["name"]
    #         properties["description"] = response.result["metadata"]["description"]
    #         return JavaLibrary(**properties)

    # def get_build_stage(self, id: str | None = None, name: str | None = None):
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")
    #     cbs = CreateBuildStage(self.config)
    #     if id is not None:
    #         response = cbs.get_build_stage(build_stage_id=id)
    #         properties = response.result["entity"]
    #         properties["name"] = response.result["metadata"]["name"]
    #         properties["description"] = (
    #             response.result["metadata"]["description"]
    #             if "description" in response.result["metadata"]
    #             else ""
    #         )
    #         properties["asset_id"] = response.result["metadata"]["asset_id"]
    #         properties["proj_id"] = response.result["metadata"]["project_id"]
    #         return BuildStage.from_dict(properties)
    #     elif name is not None:
    #         response = cbs.list_build_stages(entity_name=name)
    #         build_stage = None
    #         for bs in response.result["assets"]:
    #             if name == bs["metadata"]["name"]:
    #                 build_stage = bs
    #                 break
    #         if not build_stage:
    #             raise ValueError(f"Could not find build stage {name}")
    #         asset_id = build_stage["metadata"]["asset_id"]
    #         response = cbs.get_build_stage(build_stage_id=asset_id)
    #         properties = response.result["entity"]
    #         properties["name"] = response.result["metadata"]["name"]
    #         properties["description"] = (
    #             response.result["metadata"]["description"]
    #             if "description" in response.result["metadata"]
    #             else ""
    #         )
    #         properties["asset_id"] = response.result["metadata"]["asset_id"]
    #         properties["proj_id"] = response.result["metadata"]["project_id"]
    #         return BuildStage.from_dict(properties)

    # def get_wrapped_stage(self, id: str | None = None, name: str | None = None):
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")
    #     cws = CreateWrappedStage(self.config)
    #     if id is not None:
    #         response = cws.get_wrapped_stage(wrapped_stage_id=id)
    #         properties = response.result["entity"]
    #         properties["name"] = response.result["metadata"]["name"]
    #         properties["description"] = (
    #             response.result["metadata"]["description"]
    #             if "description" in response.result["metadata"]
    #             else ""
    #         )
    #         properties["asset_id"] = response.result["metadata"]["asset_id"]
    #         properties["proj_id"] = response.result["metadata"]["project_id"]
    #         return WrappedStage.from_dict(properties)
    #     elif name is not None:
    #         response = cws.list_wrapped_stages(entity_name=name)
    #         wrapped_stage = None
    #         for ws in response.result["assets"]:
    #             if name == ws["metadata"]["name"]:
    #                 wrapped_stage = ws
    #                 break
    #         if not wrapped_stage:
    #             raise ValueError(f"Could not find wrapped stage {name}")
    #         asset_id = wrapped_stage["metadata"]["asset_id"]
    #         response = cws.get_wrapped_stage(wrapped_stage_id=asset_id)
    #         properties = response.result["entity"]
    #         properties["name"] = response.result["metadata"]["name"]
    #         properties["description"] = (
    #             response.result["metadata"]["description"]
    #             if "description" in response.result["metadata"]
    #             else ""
    #         )
    #         properties["asset_id"] = response.result["metadata"]["asset_id"]
    #         properties["proj_id"] = response.result["metadata"]["project_id"]
    #         return WrappedStage.from_dict(properties)

    # def get_custom_stage(self, id: str | None = None, name: str | None = None):
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")
    #     ccs = CreateCustomStage(self.config)
    #     if id is not None:
    #         response = ccs.get_custom_stage(custom_stage_id=id)
    #         properties = response.result["entity"]
    #         properties["name"] = response.result["metadata"]["name"]
    #         properties["description"] = (
    #             response.result["metadata"]["description"]
    #             if "description" in response.result["metadata"]
    #             else ""
    #         )
    #         properties["asset_id"] = response.result["metadata"]["asset_id"]
    #         properties["proj_id"] = response.result["metadata"]["project_id"]
    #         return CustomStage.from_dict(properties)
    #     elif name is not None:
    #         response = ccs.list_custom_stages(entity_name=name)
    #         custom_stage = None
    #         for cs in response.result["assets"]:
    #             if name == cs["metadata"]["name"]:
    #                 custom_stage = cs
    #                 break
    #         if not custom_stage:
    #             raise ValueError(f"Could not find custom stage {name}")
    #         asset_id = custom_stage["metadata"]["asset_id"]
    #         response = ccs.get_custom_stage(custom_stage_id=asset_id)
    #         properties = response.result["entity"]
    #         properties["name"] = response.result["metadata"]["name"]
    #         properties["description"] = (
    #             response.result["metadata"]["description"]
    #             if "description" in response.result["metadata"]
    #             else ""
    #         )
    #         properties["asset_id"] = response.result["metadata"]["asset_id"]
    #         properties["proj_id"] = response.result["metadata"]["project_id"]
    #         return CustomStage.from_dict(properties)

    # def get_connection(
    #     self, id: str | None = None, name: str | None = None
    # ) -> BaseConnection:
    #     """Imports a connection from the project by its ID or name. Only one of the parameters should be provided.

    #     Args:
    #         id: The ID of the connection to import.
    #         name: The name of the connection to import.

    #     Returns:
    #         A :class:`BaseConnection` object representing the imported connection.
    #     """
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")

    #     if id:
    #         cc = CreateConnection(self.config)
    #         response = cc.get_connection(connection_id=id)
    #         properties = response.result["entity"]["properties"]
    #         name = response.result["entity"]["name"]
    #         datasource_type = response.result["entity"]["datasource_type"]
    #         properties["name"] = name
    #         properties["config"] = self.config
    #         properties["proj_id"] = self.config._get_project_id()
    #         properties["asset_id"] = id
    #         if datasource_type in CONN_MAPPINGS:
    #             op_name = CONN_MAPPINGS[datasource_type]
    #             mod = importlib.import_module(
    #                 f"ibm.datastage._connections.{op_name}_connection"
    #             )
    #             class_ = getattr(mod, self.op_name_to_conn_class(op_name))
    #             return class_.model_construct(**properties)
    #         elif datasource_type in DATASOURCE_MAPPINGS:
    #             if DATASOURCE_MAPPINGS[datasource_type] in CONN_MAPPINGS:
    #                 op_name = CONN_MAPPINGS[DATASOURCE_MAPPINGS[datasource_type]]
    #                 mod = importlib.import_module(
    #                     f"ibm.datastage._connections.{op_name}_connection"
    #                 )
    #                 class_ = getattr(mod, self.op_name_to_conn_class(op_name))
    #                 return class_.model_construct(**properties)

    #         raise ValueError(
    #             "Connection type is not supported. Please check the connection type and try again."
    #         )

    #     # Importing by name
    #     cc = CreateConnection(self.config)
    #     connections = cc.list_connections(entity_name=name)
    #     connection = None
    #     for conn in connections.result["resources"]:
    #         if conn["entity"]["name"] == name:
    #             connection = conn
    #             break
    #     if not connection:
    #         connections = cc.list_connections(
    #             entity_name=name, entity_flags="parameterized"
    #         )
    #         connection = None
    #         for conn in connections.result["resources"]:
    #             if conn["entity"]["name"] == name:
    #                 connection = conn
    #                 break
    #         if not connection:
    #             raise ValueError(f"Could not find connection {name}")
    #     properties = connection["entity"]["properties"]
    #     datasource_type = conn["entity"]["datasource_type"]
    #     properties["asset_id"] = connection["metadata"]["asset_id"]
    #     properties["name"] = name
    #     properties["config"] = self.config
    #     properties["proj_id"] = self.config._get_project_id()

    #     if datasource_type in CONN_MAPPINGS:
    #         op_name = CONN_MAPPINGS[datasource_type]
    #         mod = importlib.import_module(
    #             f"ibm.datastage._connections.{op_name}_connection"
    #         )
    #         class_ = getattr(mod, self.op_name_to_conn_class(op_name))
    #         return class_.model_construct(**properties)
    #     elif datasource_type in DATASOURCE_MAPPINGS:
    #         if DATASOURCE_MAPPINGS[datasource_type] not in CONN_MAPPINGS:
    #             raise ValueError(f"Connection type {datasource_type} is not supported.")

    #         op_name = CONN_MAPPINGS[DATASOURCE_MAPPINGS[datasource_type]]
    #         mod = importlib.import_module(
    #             f"ibm.datastage._connections.{op_name}_connection"
    #         )
    #         class_ = getattr(mod, self.op_name_to_conn_class(op_name))
    #         return class_.model_construct(**properties)
    #     else:
    #         raise ValueError(
    #             "Connection type is not supported. Please check the connection type and try again."
    #         )

    # def get_function_library(
    #     self, id: str | None = None, name: str | None = None
    # ) -> FunctionLibrary:
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")
    #     cfl = CreateFunctionLibrary(self.config)
    #     if id is None:  # name is not None, search for id
    #         function_library_response = cfl.list_function_libraries(entity_name=name)
    #         function_library_exists = False
    #         for fl in function_library_response.result["assets"]:
    #             if fl["metadata"]["name"] == name:
    #                 function_library_exists = True
    #                 id = fl["metadata"]["asset_id"]
    #                 break
    #         if not function_library_exists:
    #             raise ValueError(f"Could not find function library {name}")

    #     response = cfl.get_function_library(function_library_id=id)
    #     dir_path = os.getcwd() + "/attachments"
    #     if not os.path.exists(dir_path):
    #         os.mkdir(dir_path)
    #     entity = response.result["entity"]
    #     so_file_content_bytes = entity["so_file_content_bytes"]
    #     function_library_name = response.result["attachments"][0]["name"]
    #     with open(dir_path + "/" + function_library_name, "wb") as f:
    #         f.write(so_file_content_bytes)
    #     properties = {}
    #     properties["library_path"] = "attachments/" + function_library_name
    #     properties["name"] = response.result["metadata"]["name"]
    #     properties["description"] = response.result["metadata"]["description"]
    #     return FunctionLibrary(**properties)

    # def get_match_specification(
    #     self, id: str | None = None, name: str | None = None
    # ) -> MatchSpecification:
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")
    #     cms = CreateMatchSpecification(self.config)
    #     if id is None:  # name is not None, search for id
    #         match_specification_response = cms.list_match_specifications(
    #             entity_name=name
    #         )
    #         match_specification_exists = False
    #         for ms in match_specification_response.result["assets"]:
    #             if ms["metadata"]["name"] == name:
    #                 match_specification_exists = True
    #                 id = ms["metadata"]["asset_id"]
    #                 break
    #         if not match_specification_exists:
    #             raise ValueError(f"Could not find match specification {name}")

    #     response = cms.get_match_specification(match_specification_id=id)
    #     mat_json = response.result["entity"]["content"]["mat"]["MATCHSPEC"]
    #     passes_json = response.result["entity"]["content"]["passes"]

    #     dir_path = os.getcwd() + "/attachments"
    #     if not os.path.exists(dir_path):
    #         os.mkdir(dir_path)

    #     match_properties = MatchSpecification.create_match_properties(
    #         response.result["metadata"]["name"], mat_json, passes_json
    #     )
    #     return MatchSpecification(**match_properties)

    # def get_subflow(self, id: str | None = None, name: str | None = None):
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")
    #     if id is not None:
    #         cs = CreateSubflow(self.config)
    #         response = cs.get_subflow(subflow_id=id)
    #         if "error" in response.result or "errors" in response.result:
    #             raise ValueError(f"Could not find subflow with id {id} in project")
    #         subflow_json = response.result["attachments"]
    #         subflow_name = response.result["metadata"]["name"]
    #         flow_model = models.Flow(**subflow_json)
    #         dag_gen = DAGGenerator(flow_model)
    #         dag = dag_gen.generate()._dag
    #         return Subflow(dag=dag, name=subflow_name, asset_id=id, is_local=False)
    #     elif name is not None:
    #         cs = CreateSubflow(self.config)
    #         response = cs.list_subflows(entity_name=name)
    #         if "error" in response.result or "errors" in response.result:
    #             raise ValueError(f"Could not find subflow with id {id} in project")
    #         subflow_id = None
    #         for subflow in response.result["data_flows"]:
    #             if subflow["metadata"]["name"] == name:
    #                 subflow_id = subflow["metadata"]["asset_id"]
    #         if not subflow_id:
    #             raise ValueError(f"Could not find subflow with name {name} in project")
    #         response = cs.get_subflow(subflow_id=subflow_id)
    #         if "error" in response.result or "errors" in response.result:
    #             raise ValueError(f"Could not find subflow with id {id}")
    #         subflow_json = response.result["attachments"]
    #         subflow_id = response.result["metadata"]["asset_id"]
    #         flow_model = models.Flow(**subflow_json)
    #         dag_gen = DAGGenerator(flow_model)
    #         dag = dag_gen.generate()._dag
    #         return Subflow(dag=dag, name=name, asset_id=subflow_id, is_local=False)
    #     return None

    # def get_test_case(self, id: str | None = None, name: str | None = None):
    #     if not id and not name:
    #         raise ValueError("Either id or name must be provided")
    #     if id is not None:
    #         tcr = TestCaseRunner(self.config)
    #         response = tcr.get_test_case(test_case_id=id)
    #         if "error" in response.result or "errors" in response.result:
    #             raise ValueError(f"Could not find test case with id {id} in project")
    #         specification = response.result["entity"]["specification"]
    #         given = specification["given"]
    #         then = specification["then"]
    #         when = specification["when"]

    #         tcc = TestCaseComposer(
    #             name=response.result["metadata"]["name"],
    #             flow_id=when["data_intg_flow_ref"],
    #         )

    #         for link in given:
    #             tcc.use_input_test_data((link["link"], link["path"]))
    #         for link in then:
    #             tcc.use_output_test_data((link["link"], link["path"]))

    #         tcc.use_parameters(when["parameters"])

    #         return tcc
    #     elif name is not None:
    #         tcr = TestCaseRunner(self.config)
    #         response = tcr.list_test_cases(test_case_name=name)
    #         if "error" in response.result or "errors" in response.result:
    #             raise ValueError("Could not find test cases in project")
    #         test_case_id = None
    #         for test_case in response.result["assets"]:
    #             if test_case["metadata"]["name"] == name:
    #                 test_case_id = test_case["metadata"]["asset_id"]
    #         if not test_case_id:
    #             raise ValueError(
    #                 f"Could not find test case with name {name} in project"
    #             )
    #         response = tcr.get_test_case(test_case_id=test_case_id)
    #         if "error" in response.result or "errors" in response.result:
    #             raise ValueError(f"Could not find test case with id {id}")
    #         specification = response.result["entity"]["specification"]
    #         given = specification["given"]
    #         then = specification["then"]
    #         when = specification["when"]

    #         tcc = TestCaseComposer(
    #             name=response.result["metadata"]["name"],
    #             flow_id=when["data_intg_flow_ref"],
    #         )

    #         for link in given:
    #             tcc.use_input_test_data((link["link"], link["path"]))
    #         for link in then:
    #             tcc.use_output_test_data((link["link"], link["path"]))

    #         tcc.use_parameters(when["parameters"])

    #         return tcc
    #     return None

    # def construct_asset(self, object):
    #     if isinstance(object, ParameterSet):
    #         return self.construct_paramset(object)

    #     if isinstance(object, BaseConnection):
    #         return self.construct_connection(object)

    #     if isinstance(object, Subflow):
    #         return self.construct_subflow(object)

    #     raise ValueError("Cannot construct unknown object")
