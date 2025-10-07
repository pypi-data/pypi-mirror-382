import importlib
import re
from enum import Enum

import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as models
import ibm_watsonx_data_integration.services.datastage.models.schema.field as Field
from ibm_watsonx_data_integration.services.datastage.codegen.datasource_mappings import DATASOURCE_MAPPINGS
from ibm_watsonx_data_integration.services.datastage.codegen.label_mappings import LABEL_MAPPINGS
from ibm_watsonx_data_integration.services.datastage.codegen.op_mappings import OP_MAPPINGS
from ibm_watsonx_data_integration.services.datastage.models.flow.dag import (
    DAG,
    Link,
    Node,
    StageNode,
)
from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow
from ibm_watsonx_data_integration.services.datastage.models.schema.field.base_field import BaseField
from ibm_watsonx_data_integration.services.datastage.models.schema.schema import Schema
from ibm_watsonx_data_integration.services.datastage.models.stage_models.complex_stages import lookup
from ibm_watsonx_data_integration.services.datastage.models.stage_models.complex_stages.complex_flat_file import (
    Column,
    OutputColumns,
    Record,
    RecordID,
    Constraint as CFFConstraint,
)

from ibm_watsonx_data_integration.services.datastage.models.stage_models.complex_stages.rest import (
    Authentication,
    Body,
    Control,
    Cookie,
    FormData,
    FormURLEncodedData,
    Header,
    Parameter,
    Request,
    RequestInfo,
    Response,
    Settings,
    Variable,
)
from ibm_watsonx_data_integration.services.datastage.models.stage_models.complex_stages.transformer import (
    Constraint,
    LoopVariable,
    StageVariable,
    Trigger,
)

CONNECTIONS = {}
JAVA_LIBRARIES = {}
FUNCTION_LIBRARIES = {}
MATCH_SPECIFICATIONS = {}


def label_to_stage_name(label: str) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", label)
    result = []
    for word in words:
        if word.isupper():
            result.append(word)
        else:
            result.append(word.capitalize())
    return "".join(result)


def op_name_to_conn_class(op_name: str):
    """Converts an operator name (usually snake_case) into the PascalCase class name of that stage."""
    split = op_name.split("_")
    caps = [part[0].upper() + part[1:] for part in split]
    return "".join(caps) + "Conn"


def instantiate_stage_model(model_class: str, model_stage_props: dict):
    """Instantiates a model object of a specific model class using the given dictionary of properties."""
    mod = importlib.import_module(f"ibm_watsonx_data_integration.services.datastage.models.stage_models.{model_class}")
    class_ = getattr(mod, model_class)
    obj = class_.model_construct(**model_stage_props)
    # Convert enums from strings to objects
    for prop, value in obj.model_fields.items():
        if "enum" in str(value.annotation) or isinstance(value.default, Enum):
            try:
                enum = type(value.default)(getattr(obj, prop))
                setattr(obj, prop, enum)
            except (ValueError, KeyError, TypeError):
                pass
    return obj


def instantiate_stage_node(op_name: str, dag: DAG, model: models.BaseModel) -> StageNode:
    """Instantiates a stage object of a specific stage class."""
    mod = importlib.import_module(f"ibm_watsonx_data_integration.services.datastage.models.stages.{op_name}")
    label = LABEL_MAPPINGS[op_name]
    class_ = getattr(mod, label_to_stage_name(label) + "Stage")
    obj = class_(dag, model)
    return obj


# edit this to keep track of same connection instance
def instantiate_connection_model(op_name: str, conn_props: dict):
    if conn_props["name"] in CONNECTIONS:
        return CONNECTIONS[conn_props["name"]]
    mod = importlib.import_module(f"ibm_watsonx_data_integration.services.datastage.models.connections.{op_name}_connection")
    class_ = getattr(mod, op_name_to_conn_class(op_name))
    obj = class_.model_construct(**conn_props)
    CONNECTIONS[obj.name] = obj
    return obj


# def instantiate_java_library_model(jl_props: dict):
#     if jl_props["name"] in JAVA_LIBRARIES:
#         return JAVA_LIBRARIES[jl_props["name"]]
#     jl = JavaLibrary(**jl_props)
#     JAVA_LIBRARIES[jl.name] = jl
#     return jl


# def instantiate_function_library_model(fl_props: dict):
#     if fl_props["name"] in FUNCTION_LIBRARIES:
#         return FUNCTION_LIBRARIES[fl_props["name"]]
#     fl = FunctionLibrary(**fl_props)
#     FUNCTION_LIBRARIES[fl.name] = fl
#     return fl


# def instantiate_match_specification_model(ms_props: dict):
#     if ms_props["name"] in MATCH_SPECIFICATIONS:
#         return MATCH_SPECIFICATIONS[ms_props["name"]]
#     ms = MatchSpecification(**ms_props)
#     MATCH_SPECIFICATIONS[ms.name] = ms
#     return ms


class DAGGenerator:
    def __init__(self, flow_model: models.Flow):
        self.flow_model = flow_model
        self.id_to_dag_node: dict[str, Node] = {}
        self.id_to_node_model: dict[str, models.Node] = {}
        self.schemas: dict[str, Schema] = {}
        self.fc = DataStageFlow()
        self.dag = self.fc._dag
        self.rcp = {}

    def generate(self) -> DataStageFlow:
        for record_schema in self.flow_model.schemas:
            self.process_schema(record_schema)

        for pipeline_model in self.flow_model.pipelines:
            if self.flow_model.primary_pipeline == pipeline_model.id:
                self.process_pipeline(pipeline_model)

        # if self.flow_model.external_paramsets:
        #     for paramset in self.flow_model.external_paramsets:
        #         self.fc.use_paramset(self.process_paramsets(paramset))

        # if self.flow_model.parameters and "local_parameters" in self.flow_model.parameters:
        #     self.fc.use_localparams(self.process_localparams(self.flow_model.parameters["local_parameters"]))
        # if hasattr(self.flow_model.app_data, "datastage") and self.flow_model.app_data.datastage:
        #     if "message_handlers" in self.flow_model.app_data.datastage:
        #         self.fc.use_local_message_handler(
        #             self.process_local_message_handler(self.flow_model.app_data.datastage["message_handlers"])
        #         )
        #     if "external_message_handlers" in self.flow_model.app_data.datastage:
        #         for asset_id in self.flow_model.app_data.datastage["external_message_handlers"]:
        #             self.fc.use_message_handler(self.process_message_handler(asset_id))

        # self.fc.use_runtime(self.process_runtime(self.flow_model.app_data))
        self.fc._dag = self.dag

        return self.fc

    def process_schema(self, schema_model: models.RecordSchema) -> None:
        fields = [self.generate_field(field_model) for field_model in schema_model.fields]
        # if not len(fields):
        #     print(f"WARNING: Found schema with no fields, skipping: {schema_model.id}")
        #     return

        schema = Schema(fields)

        assert schema_model.id not in self.schemas
        self.schemas[schema_model.id] = schema

    def generate_field(self, field_model: models.FieldModel) -> BaseField:
        ODBC_TO_CLASS = {
            "BIGINT": Field.BigInt,
            "BINARY": Field.Binary,
            "BIT": Field.Bit,
            "CHAR": Field.Char,
            "DATE": Field.Date,
            "DECIMAL": Field.Decimal,
            "DOUBLE": Field.Double,
            "FLOAT": Field.Float,
            "INTEGER": Field.Integer,
            "LONGVARBINARY": Field.LongVarBinary,
            "LONGVARCHAR": Field.LongVarChar,
            "LONGNVARCHAR": Field.LongVarChar,
            "NUMERIC": Field.Numeric,
            "REAL": Field.Real,
            "SMALLINT": Field.SmallInt,
            "TIME": Field.Time,
            "TIMESTAMP": Field.Timestamp,
            "TINYINT": Field.TinyInt,
            "UNKNOWN": Field.Unknown,
            "VARBINARY": Field.VarBinary,
            "VARCHAR": Field.VarChar,
            "NCHAR": Field.NChar,
            "NVARCHAR": Field.VarChar,
            "WCHAR": Field.NChar,
            "WLONGVARCHAR": Field.LongNVarChar,
            "WVARCHAR": Field.NVarChar,
        }

        try:
            odbc = field_model.app_data["odbc_type"]
        except Exception:
            raise KeyError(f"Field {field_model.name} is missing an ODBC type")

        try:
            class_ = ODBC_TO_CLASS[odbc.upper()]
        except KeyError:
            raise KeyError(f"Unknown ODBC type for field {field_model.name}: {odbc}")

        field_obj: BaseField = class_(field_model.name)
        field_obj.configuration = models.FieldModelComplex.from_field_model(field_model)

        return field_obj

    def process_pipeline(self, pipeline_model: models.Pipeline) -> None:
        for node_model in pipeline_model.nodes:
            model_stage_node = self.generate_node(node_model)
            assert node_model.id
            self.id_to_dag_node[node_model.id] = model_stage_node
            self.id_to_node_model[node_model.id] = node_model

        for node_id in self.id_to_dag_node:
            self.link_up_node(self.id_to_dag_node[node_id], self.id_to_node_model[node_id])

        for link in self.dag.links():
            if link.name in self.rcp:
                try:
                    if hasattr(link.src, "configuration"):
                        link.src.configuration.runtime_column_propagation = self.rcp[link.name]
                    elif hasattr(link.src, "rcp"):
                        link.src.rcp = self.rcp[link.name]
                    else:
                        link.src.with_runtime_column_propagation(self.rcp[link.name])
                except Exception:
                    pass

        self.populate_funnel_schema(pipeline_model=pipeline_model)
        self.populate_difference_schema(pipeline_model=pipeline_model)
        self.populate_sort_schema(pipeline_model=pipeline_model)
        self.populate_pivot_schema(pipeline_model=pipeline_model)
        self.populate_change_capture_schema(pipeline_model=pipeline_model)
        self.populate_transformer_schema(pipeline_model=pipeline_model)
        self.populate_rest_schema()

        # if pipeline_model.app_data.ui_data and pipeline_model.app_data.ui_data.comments:
        #     self.process_comments(pipeline_model=pipeline_model)

    def populate_funnel_schema(self, pipeline_model: models.Pipeline) -> None:
        for link in self.dag.links():
            if hasattr(link.src, "configuration"):
                if link.src.configuration.op_name == "PxFunnel":
                    for node_model in pipeline_model.nodes:
                        if hasattr(node_model, "op") and node_model.op == "PxFunnel":
                            if node_model.app_data.ui_data.label == link.src.label:
                                for output in node_model.outputs:
                                    if hasattr(output, "parameters") and output.parameters and "valueDerivation" in output.parameters:
                                        for vd in output.parameters["valueDerivation"]:
                                            if vd["columnName"] != vd["parsedExpression"]:
                                                for field in link.schema.fields:
                                                    if field.configuration.name == vd["columnName"]:
                                                        field.configuration.metadata.source_field_id = vd["parsedExpression"]

    def populate_difference_schema(self, pipeline_model: models.Pipeline) -> None:
        for link in self.dag.links():
            if hasattr(link.src, "configuration"):
                if link.src.configuration.op_name == "PxDifference":
                    for node_model in pipeline_model.nodes:
                        if hasattr(node_model, "op") and node_model.op == "PxDifference":
                            if node_model.app_data.ui_data.label == link.src.label:
                                for output in node_model.outputs:
                                    if hasattr(output, "parameters") and output.parameters and "valueDerivation" in output.parameters:
                                        for vd in output.parameters["valueDerivation"]:
                                            if vd["parsedExpression"] == "DiffCode()":
                                                if vd["columnName"] != "diff":
                                                    for field in link.schema.fields:
                                                        if field.configuration.name == vd["columnName"]:
                                                            field.configuration.app_data["difference"] = True

    def populate_sort_schema(self, pipeline_model: models.Pipeline) -> None:
        for link in self.dag.links():
            if hasattr(link.src, "configuration"):
                if link.src.configuration.op_name == "PxSort":
                    for node_model in pipeline_model.nodes:
                        if hasattr(node_model, "op") and node_model.op == "PxSort":
                            if node_model.app_data.ui_data.label == link.src.label:
                                for output in node_model.outputs:
                                    if hasattr(output, "parameters") and output.parameters and "valueDerivation" in output.parameters:
                                        for vd in output.parameters["valueDerivation"]:
                                            if vd["parsedExpression"] == "ClusterKeyChange()":
                                                if vd["columnName"] != "clusterKeyChange":
                                                    for field in link.schema.fields:
                                                        if field.configuration.name == vd["columnName"]:
                                                            field.configuration.app_data["cluster_key_change"] = True
                                            elif vd["parsedExpression"] == "KeyChange()":
                                                if vd["columnName"] != "keyChange":
                                                    for field in link.schema.fields:
                                                        if field.configuration.name == vd["columnName"]:
                                                            field.configuration.app_data["key_change"] = True

    def populate_pivot_schema(self, pipeline_model: models.Pipeline) -> None:
        for link in self.dag.links():
            if hasattr(link.src, "configuration"):
                if link.src.configuration.op_name == "PxPivot":
                    for node_model in pipeline_model.nodes:
                        if hasattr(node_model, "op") and node_model.op == "PxPivot":
                            if node_model.app_data.ui_data.label == link.src.label:
                                for output in node_model.outputs:
                                    if hasattr(output, "parameters") and output.parameters and "valueDerivation" in output.parameters:
                                        for vd in output.parameters["valueDerivation"]:
                                            if "parsedExpression" in vd and vd["parsedExpression"].startswith("Pivot"):
                                                for field in link.schema.fields:
                                                    if field.configuration.name == vd["columnName"]:
                                                        pivot_prop = vd["parsedExpression"].split("(")[-1].strip(")")
                                                        if pivot_prop != vd["columnName"]:
                                                            field.configuration.app_data["pivot_property"] = pivot_prop

    def populate_change_capture_schema(self, pipeline_model: models.Pipeline) -> None:
        for link in self.dag.links():
            if hasattr(link.src, "configuration"):
                if link.src.configuration.op_name == "PxChangeCapture":
                    for node_model in pipeline_model.nodes:
                        if hasattr(node_model, "op") and node_model.op == "PxChangeCapture":
                            if node_model.app_data.ui_data.label == link.src.label:
                                for output in node_model.outputs:
                                    if hasattr(output, "parameters") and output.parameters and "valueDerivation" in output.parameters:
                                        for vd in output.parameters["valueDerivation"]:
                                            if vd["parsedExpression"] == "ChangeCode()":
                                                for field in link.schema.fields:
                                                    if field.configuration.name == vd["columnName"]:
                                                        field.configuration.app_data["change_code"] = True

    def populate_transformer_schema(self, pipeline_model: models.Pipeline) -> None:
        for link in self.dag.links():
            if hasattr(link.src, "configuration"):
                if link.src.configuration.op_name == "CTransformerStage":
                    for node_model in pipeline_model.nodes:
                        if hasattr(node_model, "op") and node_model.op == "CTransformerStage":
                            if node_model.app_data.ui_data.label == link.src.label:
                                for output in node_model.outputs:
                                    schema = None
                                    for schema_id, schema_model in self.schemas.items():
                                        if output.schema_ref == schema_id:
                                            schema = schema_model
                                    if hasattr(output, "parameters") and output.parameters and "valueDerivation" in output.parameters:
                                        for vd in output.parameters["valueDerivation"]:
                                            for field in schema.fields:
                                                if field.configuration.name == vd["columnName"]:
                                                    if "parsedExpression" in vd:
                                                        field.configuration.app_data["derivation"] = vd["parsedExpression"]
                                                    if "sourceColumn" in vd:
                                                        field.configuration.metadata.source_field_id = vd["sourceColumn"]
                                        del output.parameters["valueDerivation"]

    def populate_rest_schema(self) -> None:
        for link in self.dag.links():
            if hasattr(link.src, "configuration"):
                if link.src.configuration.op_name == "PxRest":
                    if link.schema:
                        for field in link.schema.fields:
                            if field.configuration.metadata.description:
                                field.configuration.app_data["derivation"] = field.configuration.metadata.description

    # def process_comments(self, pipeline_model: models.Pipeline) -> None:
    #     for comment in pipeline_model.app_data.ui_data.comments:
    #         if comment.content_type == "WYSIWYG":
    #             if comment.associated_id_refs:
    #                 for comment_ref in comment.associated_id_refs:
    #                     if comment_ref.node_ref in self.id_to_dag_node:
    #                         dag_node = self.id_to_dag_node[comment_ref.node_ref]
    #                         new_comment = StyledComment(dag=self.dag, configuration=comment)
    #                         new_comment.connect_output_to(dag_node)
    #             else:
    #                 new_comment = StyledComment(dag=self.dag, configuration=comment)
    #                 self.dag.add_node(new_comment)
    #         else:
    #             if comment.associated_id_refs:
    #                 for comment_ref in comment.associated_id_refs:
    #                     if comment_ref.node_ref in self.id_to_dag_node:
    #                         dag_node = self.id_to_dag_node[comment_ref.node_ref]
    #                         new_comment = MarkdownComment(dag=self.dag, content=comment.content)
    #                         new_comment.connect_output_to(dag_node)
    #             else:
    #                 new_comment = MarkdownComment(dag=self.dag, content=comment.content)
    #                 self.dag.add_node(new_comment)

    def link_up_node(
        self,
        dag_node: Node,
        node_model: models.Node,
        dag: DAG = None,
        id_to_dag_node: dict = None,
    ) -> None:
        """Links up the given node with other nodes in the DAG based on the links represented in its JSON model"""

        def create_link(link_model: models.NodeLink, src: Node, dest: Node, schema_ref: str | None) -> Link:
            """Creates a Link object from the given link model and source and destination nodes"""

            link = Link(dag=self.dag, name=link_model.link_name)
            link.src = src
            link.dest = dest

            if schema_ref:
                if schema_ref not in self.schemas:
                    raise KeyError(f"Could not find schema {schema_ref} referenced by node output")
                link.schema = self.schemas[schema_ref]

            type_attr = link_model.type_attr
            if type_attr is None:
                try:
                    type_attr = link_model.app_data.datastage["link_type"]
                except (AttributeError, KeyError):
                    type_attr = type_attr

            match type_attr:
                case "PRIMARY":
                    link.primary()
                case "REFERENCE":
                    link.reference()
                case "REJECT":
                    link.reject()
                case other:
                    raise ValueError(f"Unsupported link type: {other}")

            try:
                partner_link_out = link_model.app_data.datastage["partner_link_out"]
                link.maps_from_link = partner_link_out
            except (AttributeError, KeyError):
                pass
            try:
                partner_link_in = link_model.app_data.datastage["partner_link_in"]
                link.maps_to_link = partner_link_in
            except (AttributeError, KeyError):
                pass

            return link

        if hasattr(node_model, "inputs"):
            for input_port_model in node_model.inputs or []:
                if isinstance(input_port_model, tuple) and [] in input_port_model:
                    continue

                if not hasattr(input_port_model, "links"):
                    input_port_model = input_port_model[1][0]

                for link_model in input_port_model.links or []:
                    src_node_id = link_model.node_id_ref
                    if id_to_dag_node:
                        src_node = id_to_dag_node[src_node_id]
                    else:
                        src_node = self.id_to_dag_node[src_node_id]

                    if dag and src_node not in dag.adj:
                        raise KeyError(f"Could not find node {src_node}")
                    elif src_node not in self.dag.adj:
                        raise KeyError(f"Could not find node {src_node}")

                    if dag:
                        dag.adj[src_node].setdefault(dag_node, [])
                    else:
                        self.dag.adj[src_node].setdefault(dag_node, [])

                    link = create_link(link_model, src_node, dag_node, input_port_model.schema_ref)
                    if dag:
                        dag.adj[src_node][dag_node].append(link)
                    else:
                        self.dag.adj[src_node][dag_node].append(link)

        if dag and id_to_dag_node:
            return dag, id_to_dag_node

        # Commented out because there are never any output links
        # if hasattr(node_model, "outputs"):
        #     for output_port_model in node_model.outputs or []:
        #         for link_model in output_port_model.links or []:
        #             dest_node_id = link_model.node_id_ref
        #             dest_node = self.id_to_dag_node[dest_node_id]

        #             assert dag_node in self.dag.adj
        #             self.dag.adj[dag_node].setdefault(dest_node, [])

        #             link = create_link(link_model, dag_node, dest_node)
        #             self.dag.adj[dag_node][dest_node].append(link)

    def generate_node(self, node_model: models.Node) -> Node:
        """Given a node JSON model, pulls various information and returns a StageNode"""
        if isinstance(node_model, models.ExecutionNode):
            model_stage_node = self.generate_execution_node(node_model)
        elif isinstance(node_model, models.BindingEntryNode):
            model_stage_node = self.generate_binding_entry_node(node_model)
        elif isinstance(node_model, models.BindingExitNode):
            model_stage_node = self.generate_binding_exit_node(node_model)
        elif isinstance(node_model, models.ModelNode):
            model_stage_node = self.generate_model_node(node_model)
        elif isinstance(node_model, models.Supernode):
            raise TypeError("SuperNodes are not supported.")
            # model_stage_node = self.generate_super_node(node_model)
        else:
            raise TypeError(f"Unknown node model: {type(node_model).__class__.__name__}")

        # Pull label from JSON and assign it to the DAG node
        try:
            label = node_model.app_data.ui_data.label
        except AttributeError:
            label = None
        model_stage_node.label = label

        return model_stage_node

    def get_schema_ref_from_node(self, node: models.Node) -> models.RecordSchema | None:
        schema_ref = None
        out_ports = node.outputs if hasattr(node, "outputs") else []

        for out_port in out_ports:
            if hasattr(out_port, "schema_ref") and out_port.schema_ref:
                if schema_ref:
                    raise ValueError(f"Found multiple output ports with schema ref in node {node.id}")
                schema_ref = out_port.schema_ref
        return schema_ref

    def generate_execution_node(self, node_model: models.ExecutionNode) -> Node:
        if hasattr(node_model, "parameters") and node_model.parameters:
            model_stage_props = node_model.parameters.copy()
        else:
            model_stage_props = {}

        lookup_properties = []
        transformer_properties = []
        cff_properties = []
        for out_ in node_model.outputs or []:
            if out_.parameters:
                if node_model.op == "CTransformerStage":
                    if "outputName" in out_.parameters:
                        transformer_properties.append((out_.parameters, out_.parameters["outputName"]))
                    else:
                        output_id = out_.id
                        link_name = None
                        for pipeline in self.flow_model.pipelines:
                            for node in pipeline.nodes:
                                if hasattr(node, "inputs") and node.inputs:
                                    for input in node.inputs:
                                        if input.links:
                                            for link in input.links:
                                                if link.port_id_ref == output_id:
                                                    link_name = link.link_name
                        transformer_properties.append((out_.parameters, link_name))
                elif node_model.op == "PxCFF":
                    if "outputName" in out_.parameters:
                        cff_properties.append((out_.parameters, out_.parameters["outputName"]))
                    else:
                        output_id = out_.id
                        link_name = None
                        for pipeline in self.flow_model.pipelines:
                            for node in pipeline.nodes:
                                if hasattr(node, "inputs") and node.inputs:
                                    for input in node.inputs:
                                        if input.links:
                                            for link in input.links:
                                                if link.port_id_ref == output_id:
                                                    link_name = link.link_name
                        cff_properties.append((out_.parameters, link_name))
                if node_model.op != "JavaStagePX":
                    model_stage_props.update(out_.parameters)

        if node_model.inputs:
            for in_ in node_model.inputs:
                if in_.parameters:
                    if node_model.op == "PxLookup":
                        for link in in_.links:
                            if link.type_attr != "PRIMARY":
                                lookup_properties.append((in_.parameters, link.link_name))
                            else:
                                if "runtime_column_propagation" in in_.parameters:
                                    model_stage_props["runtime_column_propagation"] = in_.parameters["runtime_column_propagation"]
                    elif node_model.op != "JavaStagePX":
                        if "runtime_column_propagation" in in_.parameters:
                            for link in in_.links:
                                self.rcp[link.link_name] = bool(in_.parameters["runtime_column_propagation"])
                        model_stage_props.update(in_.parameters)

        if node_model.op == "CTransformerStage":
            # deal with string to int/bool
            if "LoopVariables" in model_stage_props:
                loop_variables = model_stage_props["LoopVariables"]
                for loop_var in loop_variables:
                    if "Precision" in loop_var:
                        loop_var["Precision"] = int(loop_var["Precision"])
                    if "Extended" in loop_var:
                        loop_var["Extended"] = True if str(loop_var["Extended"]).lower() == "true" or loop_var["Extended"] else False
                    if "Scale" in loop_var:
                        loop_var["Scale"] = int(loop_var["Scale"])
                model_stage_props["LoopVariables"] = [LoopVariable.model_construct(**loop_var) for loop_var in loop_variables]
            if "StageVariables" in model_stage_props:
                stage_variables = model_stage_props["StageVariables"]
                for stage_var in stage_variables:
                    if "Precision" in stage_var:
                        stage_var["Precision"] = int(stage_var["Precision"])
                    if "Extended" in stage_var:
                        stage_var["Extended"] = True if stage_var["Extended"] or str(stage_var["Extended"]).lower() == "true" else False
                    if "Scale" in stage_var:
                        stage_var["Scale"] = int(stage_var["Scale"])
                model_stage_props["StageVariables"] = [StageVariable.model_construct(**stage_var) for stage_var in stage_variables]
            if "Triggers" in model_stage_props:
                # deal with arguments here
                triggers = model_stage_props["Triggers"]
                for trigger in triggers:
                    arguments = []
                    for i in range(1, len(trigger)):
                        if f"Argument{i}" in trigger:
                            arguments.append(trigger[f"Argument{i}"])
                    trigger["arguments"] = arguments
                model_stage_props["Triggers"] = [Trigger.model_construct(**trigger) for trigger in triggers]
            # deal with constraints
            if len(transformer_properties) > 0:
                constraints = []
                for constraint_properties, link_name in transformer_properties:
                    constraint_props = {}
                    if "TransformerConstraint" in constraint_properties:
                        constraint_props["constraint"] = constraint_properties["TransformerConstraint"]
                    if "Reject" in constraint_properties:
                        constraint_props["otherwise_log"] = constraint_properties["Reject"]
                    if "RowLimit" in constraint_properties:
                        constraint_props["abort_after_rows"] = constraint_properties["RowLimit"]
                    if not len(constraint_props):
                        continue
                    constraint_props["output_name"] = link_name
                    constraints.append(Constraint.model_construct(**constraint_props))
                if len(constraints) > 0:
                    if "Reject" in model_stage_props:
                        del model_stage_props["Reject"]
                    if "RowLimit" in model_stage_props:
                        del model_stage_props["RowLimit"]
                model_stage_props["TransformerConstraint"] = constraints

        if node_model.op == "PxCFF":
            schemas = self.flow_model.schemas
            if (
                hasattr(node_model, "app_data")
                and node_model.app_data
                and hasattr(node_model.app_data, "datastage")
                and node_model.app_data.datastage
                and "stage_records" in node_model.app_data.datastage
            ):
                stage_records = node_model.app_data.datastage["stage_records"]
                records = []
                record_ids = []
                for stage_record in stage_records:
                    if "schema_ref" in stage_record:
                        for schema in schemas:
                            if schema.id == stage_record["schema_ref"]:
                                columns = []
                                for field in schema.fields:
                                    field_data = field.model_dump(exclude_none=True)
                                    properties = {
                                        "name": (field_data["name"] if "name" in field_data else None),
                                        "type": (field_data["type"] if "type" in field_data else None),
                                        "nullable": (field_data["nullable"] if "nullable" in field_data else None),
                                        **field_data["metadata"],
                                        **field_data["app_data"],
                                    }
                                    column = Column.from_dict(properties)
                                    columns.append(column)
                                record_name = stage_record["record_name"]
                                record = Record(name=record_name, columns=columns)
                                records.append(record)
                    record_id = RecordID(**stage_record)
                    record_ids.append(record_id)
                    model_stage_props["records"] = records
                    model_stage_props["records_id"] = record_ids
            if node_model.outputs:
                output_columns = []
                for output in node_model.outputs:
                    output_column = []
                    link_name = None
                    if output.schema_ref:
                        for schema in schemas:
                            if schema.id == output.schema_ref:
                                for field in schema.fields:
                                    output_column.append(field.name)
                    for pipeline in self.flow_model.pipelines:
                        for node in pipeline.nodes:
                            if hasattr(node, "inputs") and node.inputs:
                                for input in node.inputs:
                                    if input.links:
                                        for link in input.links:
                                            if link.port_id_ref == output.id:
                                                link_name = link.link_name
                    if link_name:
                        output_col_obj = OutputColumns(output_name=link_name, output_columns=output_column)
                        output_columns.append(output_col_obj)
                model_stage_props["output_columns"] = output_columns
            if len(cff_properties) > 0:
                constraints = []
                for constraint_properties, link_name in cff_properties:
                    constraint_props = {}
                    if "predicate" in constraint_properties:
                        constraint_props["constraint"] = constraint_properties["predicate"]
                    if not (len(constraint_props)):
                        continue
                    constraint_props["output_name"] = link_name
                    constraints.append(CFFConstraint.model_construct(**constraint_props))
                model_stage_props["predicate"] = constraints

        if node_model.op == "PxRest":
            if "requests" in model_stage_props:
                requests = []
                for request in model_stage_props["requests"]:
                    method = request["endpoint"]["method"] if "endpoint" in request and "method" in request["endpoint"] else None
                    use_expression_url = (
                        request["endpoint"]["expression_endpoint_on"]
                        if "endpoint" in request and "expression_endpoint_on" in request["endpoint"]
                        else False
                    )
                    url = None
                    auth = None
                    request_info = None
                    response = None
                    settings = None
                    control = None
                    if "endpoint" in request and "url" in request["endpoint"]:
                        if isinstance(request["endpoint"]["url"], dict) and "expression" in request["endpoint"]["url"]:
                            url = request["endpoint"]["url"]["expression"]
                        else:
                            url = request["endpoint"]["url"]
                    if "authentication" in request:
                        authentication = request["authentication"]
                        if "inherit" in authentication and authentication["inherit"]:
                            auth = Authentication(same_config=True)
                        else:
                            if "body" in authentication:
                                auth_props = {}
                                for key, value in authentication["body"].items():
                                    if isinstance(value, dict) and "expression" in value:
                                        auth_props[key] = value["expression"]
                                    else:
                                        auth_props[key] = value
                                auth = Authentication(**auth_props)
                    if "request" in request:
                        request_dict = request["request"]
                        if "inherit" in request_dict and request_dict["inherit"]:
                            request_info = RequestInfo(same_config=True)
                        else:
                            headers = []
                            cookies = []
                            parameters = []
                            body = None
                            additional_headers_on = False
                            addition_headers = None
                            if "headers" in request_dict:
                                for header in request_dict["headers"]:
                                    header_props = {}
                                    for key, value in header.items():
                                        if isinstance(value, dict) and "expression" in value:
                                            header_props[key] = value["expression"]
                                        else:
                                            header_props[key] = value
                                    new_header = Header(**header_props)
                                    headers.append(new_header)
                            if "cookies" in request_dict:
                                for cookie in request_dict["cookies"]:
                                    cookie_props = {}
                                    for key, value in cookie.items():
                                        if isinstance(value, dict) and "expression" in value:
                                            cookie_props[key] = value["expression"]
                                        else:
                                            cookie_props[key] = value
                                    new_cookie = Cookie(**cookie_props)
                                    cookies.append(new_cookie)
                            if "params" in request_dict:
                                for param in request_dict["params"]:
                                    param_props = {}
                                    for key, value in param.items():
                                        if isinstance(value, dict) and "expression" in value:
                                            param_props[key] = value["expression"]
                                        else:
                                            param_props[key] = value
                                    new_param = Parameter(**param_props)
                                    parameters.append(new_param)
                            if "body" in request_dict:
                                body_props = {}
                                if "content" in request_dict["body"]:
                                    type = request_dict["body"]["content"]["type"] if "type" in request_dict["body"]["content"] else None
                                    body_props["type"] = type
                                    if type == "BINARY":
                                        if "data" in request_dict["body"]["content"]:
                                            if (
                                                isinstance(
                                                    request_dict["body"]["content"]["data"],
                                                    dict,
                                                )
                                                and "expression" in request_dict["body"]["content"]["data"]
                                            ):
                                                if "source" in request_dict["body"]["content"]:
                                                    if request_dict["body"]["content"]["source"] == "DATA":
                                                        body_props["binary_data"] = request_dict["body"]["content"]["data"]["expression"]
                                                    elif request_dict["body"]["content"]["source"] == "FILE":
                                                        body_props["file_path"] = request_dict["body"]["content"]["data"]["expression"]
                                    if type == "RAW":
                                        if "data" in request_dict["body"]["content"]:
                                            if (
                                                isinstance(
                                                    request_dict["body"]["content"]["data"],
                                                    dict,
                                                )
                                                and "expression" in request_dict["body"]["content"]["data"]
                                            ):
                                                if "source" in request_dict["body"]["content"]:
                                                    if request_dict["body"]["content"]["source"] == "TEXT":
                                                        body_props["raw_text"] = request_dict["body"]["content"]["data"]["expression"]
                                                    elif request_dict["body"]["content"]["source"] == "FILE":
                                                        body_props["file_path"] = request_dict["body"]["content"]["data"]["expression"]
                                    if type == "FORM_DATA":
                                        if "data" in request_dict["body"]["content"]:
                                            if isinstance(
                                                request_dict["body"]["content"]["data"],
                                                list,
                                            ):
                                                form_datas = []
                                                for form_data in request_dict["body"]["content"]["data"]:
                                                    data_props = {}
                                                    for key, value in form_data.items():
                                                        if isinstance(value, dict) and "expression" in value:
                                                            data_props[key] = value["expression"]
                                                        else:
                                                            data_props[key] = value
                                                    new_form_data = FormData(**data_props)
                                                    form_datas.append(new_form_data)
                                                body_props["form_data"] = form_datas
                                    if type == "X_WWW_FORM_URLENCODED":
                                        if "data" in request_dict["body"]["content"]:
                                            if isinstance(
                                                request_dict["body"]["content"]["data"],
                                                list,
                                            ):
                                                form_datas = []
                                                for form_data in request_dict["body"]["content"]["data"]:
                                                    data_props = {}
                                                    for key, value in form_data.items():
                                                        if isinstance(value, dict) and "expression" in value:
                                                            data_props[key] = value["expression"]
                                                        else:
                                                            data_props[key] = value
                                                    new_form_data = FormURLEncodedData(**data_props)
                                                    form_datas.append(new_form_data)
                                                body_props["form_urlencoded_data"] = form_datas
                                    if "content_type" in request_dict["body"]["content"]:
                                        body_props["content_type"] = request_dict["body"]["content"]["content_type"]
                                    if "charset" in request_dict["body"]["content"]:
                                        body_props["charset"] = request_dict["body"]["content"]["charset"]
                                    if "expression_filePath_on" in request_dict:
                                        body_props["expression_filePath_on"] = request_dict["body"]["content"]["expression_filePath_on"]
                                    if "expression_text_on" in request_dict:
                                        if "source" in request_dict["body"]["content"]:
                                            if request_dict["body"]["content"]["source"] == "DATA":
                                                body_props["use_expression_data"] = request_dict["body"]["content"]["expression_text_on"]
                                            if request_dict["body"]["content"]["source"] == "TEXT":
                                                body_props["use_expression_text"] = request_dict["body"]["content"]["expression_text_on"]
                                body = Body(**body_props)
                                if "additional_headers_on" in request_dict["body"]:
                                    additional_headers_on = request_dict["body"]["additional_headers_on"]
                            if "additional_headers" in request_dict:
                                if (
                                    isinstance(request_dict["additional_headers"], dict)
                                    and "expression" in request_dict["additional_headers"]
                                ):
                                    addition_headers = request_dict["additional_headers"]["expression"]
                                else:
                                    addition_headers = request_dict["additional_headers"]
                            request_info = RequestInfo(
                                query_parameters=parameters,
                                custom_headers=headers,
                                custom_cookies=cookies,
                                body=body,
                                additional_headers_on=additional_headers_on,
                                additional_headers=addition_headers,
                            )
                    if "response" in request:
                        response_dict = request["response"]
                        if "inherit" in response_dict and response_dict["inherit"]:
                            response = Response(same_config=True)
                        else:
                            response_props = {}
                            if "body" in response_dict:
                                if "content_type" in response_dict["body"]:
                                    response_props["content_type"] = response_dict["body"]["content_type"]
                                if "charset" in response_dict["body"]:
                                    response_props["charset"] = response_dict["body"]["charset"]
                                if "content" in response_dict["body"]:
                                    if "target" in response_dict["body"]["content"]:
                                        response_props["target"] = response_dict["body"]["content"]["target"]
                                    if "file_path" in response_dict["body"]["content"]:
                                        if (
                                            isinstance(
                                                response_dict["body"]["content"]["file_path"],
                                                dict,
                                            )
                                            and "expression" in response_dict["body"]["content"]["file_path"]
                                        ):
                                            response_props["file_path"] = response_dict["body"]["content"]["file_path"]["expression"]
                                        else:
                                            response_props["file_path"] = response_dict["body"]["content"]["file_path"]
                                if "expression_filePath_on" in response_dict["body"]:
                                    response_props["expression_filePath_on"] = response_dict["body"]["expression_filePath_on"]
                            response = Response(**response_props)
                    if "settings" in request:
                        if "inherit" in request["settings"] and request["settings"]["inherit"]:
                            settings = Settings(same_config=True)
                        else:
                            settings_props = {}
                            for key, val in request["settings"].items():
                                if key == "server_cert":
                                    server_cert_props = {}
                                    for serv_key, serv_prop in request["settings"][key].items():
                                        if isinstance(serv_prop, dict) and "expression" in serv_prop:
                                            server_cert_props[serv_key] = serv_prop["expression"]
                                        else:
                                            server_cert_props[serv_key] = serv_prop
                                    settings_props["server_cert"] = server_cert_props
                                elif key == "client_cert":
                                    client_cert_props = {}
                                    for client_key, client_prop in request["settings"][key].items():
                                        if isinstance(client_prop, dict) and "expression" in client_prop:
                                            client_cert_props[client_key] = client_prop["expression"]
                                        else:
                                            client_cert_props[client_key] = client_prop
                                    settings_props["client_cert"] = client_cert_props
                                elif key in [
                                    "client_certificate",
                                    "server_certificate",
                                ]:
                                    continue
                                else:
                                    settings_props[key] = val
                            settings = Settings(**settings_props)
                    if "control" in request:
                        if "inherit" in request["control"] and request["control"]["inherit"]:
                            control = Control(same_config=True)
                        else:
                            control_props = {}
                            if "write_output_per_iteration" in request["control"] and request["control"]["write_output_per_iteration"]:
                                request["control"]["output_type"] = "PER_ITERATION"
                            for key, value in request["control"].items():
                                if isinstance(value, dict) and "expression" in value:
                                    control_props[key] = value["expression"]
                                else:
                                    control_props[key] = value
                            control = Control(**control_props)

                    new_request = Request(
                        method=method,
                        url=url,
                        use_expression_url=use_expression_url,
                        authentication=auth,
                        request=request_info,
                        response=response,
                        settings=settings,
                        control=control,
                    )
                    requests.append(new_request)
                model_stage_props["requests"] = requests
            if "variables" in model_stage_props:
                variables = []
                for var in model_stage_props["variables"]:
                    variable = {}
                    for key, val in var.items():
                        if isinstance(val, dict) and "expression" in val:
                            variable[key] = val["expression"]
                        else:
                            variable[key] = val
                    new_var = Variable(**variable)
                    variables.append(new_var)
                model_stage_props["variables"] = variables

        if node_model.op == "PxJoin" and "InputlinkOrderingList" not in model_stage_props:
            if (
                hasattr(node_model, "app_data")
                and node_model.app_data is not None
                and hasattr(node_model.app_data, "datastage")
                and node_model.app_data.datastage is not None
                and "inputs_order" in node_model.app_data.datastage
                and node_model.app_data.datastage["inputs_order"] is not None
            ):
                inputs_order = node_model.app_data.datastage["inputs_order"].split("|")
                ordering_list = []
                for i in range(len(inputs_order)):
                    link_name = None
                    for input in node_model.inputs:
                        if input.id == inputs_order[i]:
                            link_name = input.links[0].link_name
                    if link_name:
                        if i == 0:
                            ordering_list.append({"link_label": "Left", "link_name": link_name})
                        elif i == len(inputs_order) - 1:
                            ordering_list.append({"link_label": "Right", "link_name": link_name})
                        else:
                            key = f"Intermediate {i}"
                            ordering_list.append({"link_label": key, "link_name": link_name})
                model_stage_props["InputlinkOrderingList"] = ordering_list

        if node_model.op == "PxLookup":
            if "InputlinkOrderingList" not in model_stage_props:
                if (
                    hasattr(node_model, "app_data")
                    and node_model.app_data is not None
                    and hasattr(node_model.app_data, "datastage")
                    and node_model.app_data.datastage is not None
                    and "inputs_order" in node_model.app_data.datastage
                    and node_model.app_data.datastage["inputs_order"] is not None
                ):
                    inputs_order = node_model.app_data.datastage["inputs_order"].split("|")
                    ordering_list = []
                    primary_first = False
                    for input in node_model.inputs:
                        if len(inputs_order) and input.id == inputs_order[0]:
                            if input.links[0].type_attr == "PRIMARY":
                                primary_first = True
                    for i in range(len(inputs_order)):
                        link_name = None
                        for input in node_model.inputs:
                            if input.id == inputs_order[i]:
                                link_name = input.links[0].link_name
                        if link_name:
                            if primary_first:
                                if i == 0:
                                    ordering_list.append(
                                        {
                                            "link_label": "Primary",
                                            "link_name": link_name,
                                        }
                                    )
                                else:
                                    ordering_list.append(
                                        {
                                            "link_label": f"Lookup {i}",
                                            "link_name": link_name,
                                        }
                                    )
                            else:
                                if i == len(inputs_order) - 1:
                                    ordering_list.append(
                                        {
                                            "link_label": "Primary",
                                            "link_name": link_name,
                                        }
                                    )
                                else:
                                    ordering_list.append(
                                        {
                                            "link_label": f"Lookup {i + 1}",
                                            "link_name": link_name,
                                        }
                                    )

                    model_stage_props["InputlinkOrderingList"] = ordering_list
            if len(lookup_properties) > 0:
                lookup_derivations = []
                for lookup_derivation, link_name in lookup_properties:
                    ld_props = {}
                    if "conditionNotMet" in lookup_derivation:
                        ld_props["condition_not_met"] = lookup_derivation["conditionNotMet"]
                    if "lookupFail" in lookup_derivation:
                        ld_props["lookup_failure"] = lookup_derivation["lookupFail"]
                    if "condition" in lookup_derivation:
                        ld_props["condition"] = lookup_derivation["condition"]
                    if "Condition" in lookup_derivation:
                        ld_props["condition"] = lookup_derivation["Condition"]
                    ld_props["reference_link"] = link_name
                    if "lookupDerivation" in lookup_derivation and lookup_derivation["lookupDerivation"]:
                        derivations = []
                        for ld in lookup_derivation["lookupDerivation"]:
                            derivation = {}
                            if "columnName" in ld:
                                derivation["key_column"] = ld["columnName"]
                            if "keyType" in ld:
                                derivation["key_type"] = ld["keyType"]
                            if "parsedExpression" in ld:
                                if "Range" in ld["parsedExpression"]:
                                    derivation["key_expression"] = ld["parsedExpression"]
                                else:
                                    derivation["key_expression"] = ld["parsedExpression"].split(".")[-1]
                            derivations.append(derivation)
                        ld_props["derivations"] = derivations
                    ld_class = lookup.LookupDerivation.model_construct(**ld_props) if len(ld_props) else None
                    if ld_class:
                        # IDEALLY GET RID OF THIS
                        if not isinstance(ld_class.lookup_failure, str) and ld_class.lookup_failure:
                            ld_class.lookup_failure = ld_class.lookup_failure.value
                        if not isinstance(ld_class.condition_not_met, str) and ld_class.condition_not_met:
                            ld_class.condition_not_met = ld_class.condition_not_met.value
                        lookup_derivations.append(ld_class)
                model_stage_props["lookup_derivation"] = lookup_derivations

        if node_model.op == "PxChangeCapture" and "InputlinkOrderingList" not in model_stage_props:
            if (
                hasattr(node_model, "app_data")
                and node_model.app_data is not None
                and hasattr(node_model.app_data, "datastage")
                and node_model.app_data.datastage is not None
                and "inputs_order" in node_model.app_data.datastage
                and node_model.app_data.datastage["inputs_order"] is not None
            ):
                inputs_order = node_model.app_data.datastage["inputs_order"].split("|")
                ordering_list = []
                for i in range(len(inputs_order)):
                    link_name = None
                    for input in node_model.inputs:
                        if input.id == inputs_order[i]:
                            link_name = input.links[0].link_name
                    if link_name:
                        if i == 0:
                            ordering_list.append({"link_label": "Before", "link_name": link_name})
                        else:
                            ordering_list.append({"link_label": "After", "link_name": link_name})
                model_stage_props["InputlinkOrderingList"] = ordering_list

        if node_model.op == "PxGeneric":
            if "InputlinkOrderingList" not in model_stage_props:
                if (
                    hasattr(node_model, "app_data")
                    and node_model.app_data is not None
                    and hasattr(node_model.app_data, "datastage")
                    and node_model.app_data.datastage is not None
                    and "inputs_order" in node_model.app_data.datastage
                    and node_model.app_data.datastage["inputs_order"] is not None
                ):
                    inputs_order = node_model.app_data.datastage["inputs_order"].split("|")
                    ordering_list = []
                    for i in range(len(inputs_order)):
                        link_name = None
                        for input in node_model.inputs:
                            if input.id == inputs_order[i]:
                                link_name = input.links[0].link_name
                        if link_name:
                            ordering_list.append({"link_label": f"{i}", "link_name": link_name})
                    model_stage_props["InputlinkOrderingList"] = ordering_list

            if "OutputlinkOrderingList" not in model_stage_props:
                if (
                    hasattr(node_model, "app_data")
                    and node_model.app_data is not None
                    and hasattr(node_model.app_data, "datastage")
                    and node_model.app_data.datastage is not None
                    and "outputs_order" in node_model.app_data.datastage
                    and node_model.app_data.datastage["outputs_order"] is not None
                ):
                    outputs_order = node_model.app_data.datastage["outputs_order"].split("|")
                    ordering_list = []
                    for i in range(len(outputs_order)):
                        link_name = None
                        for output in node_model.outputs:
                            if output.id == outputs_order[i] and output.links:
                                # TODO: outputs don't have link_name, can grab from corresponding input
                                # link, but it would require passing extra data to the method
                                link_name = output.links[0].link_name
                        if link_name:
                            ordering_list.append({"link_label": f"{i}", "link_name": link_name})
                    model_stage_props["OutputlinkOrderingList"] = ordering_list

        if node_model.op == "PxChecksum" and "valueDerivation" in model_stage_props:
            for value_deriv in model_stage_props["valueDerivation"]:
                if "parsedExpression" in value_deriv and value_deriv["parsedExpression"] == "Checksum()":
                    if "columnName" in value_deriv:
                        model_stage_props["checksum_name"] = value_deriv["columnName"]

        if node_model.op in ["PxJoin", "PxSort", "PxFunnel", "PxAggregator", "PxRemDup", "PxFilter"] and "keyColsPart" in model_stage_props:
            del model_stage_props["keyColsPart"]

        if node_model.op in ["PxJoin", "PxSort", "PxFunnel", "PxAggregator", "PxRemDup", "PxFilter"] and "keyColsColl" in model_stage_props:
            del model_stage_props["keyColsColl"]

        if node_model.op in ["PxJoin", "PxSort", "PxFunnel", "PxAggregator", "PxRemDup", "PxFilter"] and "keyColsNone" in model_stage_props:
            del model_stage_props["keyColsNone"]

        if "runtime_column_propagation" in model_stage_props:
            if model_stage_props["runtime_column_propagation"] in [0, 1]:
                model_stage_props["runtime_column_propagation"] = bool(model_stage_props["runtime_column_propagation"])

        if hasattr(node_model.app_data, "datastage") and (
            "custom_op_asset_id" in node_model.app_data.datastage and "custom_optype" in node_model.app_data.datastage
        ):
            if node_model.app_data.datastage["custom_optype"] == 0:
                return self.create_custom_stage_node(node_model, model_stage_props)
            elif node_model.app_data.datastage["custom_optype"] == 1:
                return self.create_build_stage_node(node_model, model_stage_props)
            elif node_model.app_data.datastage["custom_optype"] == 2:
                return self.create_wrapped_stage_node(node_model, model_stage_props)

        model_stage_node = self.create_stage_node(node_model, model_stage_props)
        return model_stage_node

    def generate_binding_entry_node(self, node_model: models.BindingEntryNode) -> Node:
        if hasattr(node_model, "parameters") and node_model.parameters:
            model_stage_props = node_model.parameters.copy()
        else:
            model_stage_props = {}

        for out_ in node_model.outputs or []:
            if out_.parameters:
                model_stage_props.update(out_.parameters)

        if not node_model.op:
            return self.create_entry_node(node_model)

        if node_model.connection:
            model_stage_props.update(node_model.connection.properties)

        return self.create_stage_node(node_model, model_stage_props)

    def generate_binding_exit_node(self, node_model: models.BindingExitNode) -> Node:
        if hasattr(node_model, "parameters") and node_model.parameters:
            model_stage_props = node_model.parameters.copy()
        else:
            model_stage_props = {}

        for out_ in node_model.outputs or []:
            if out_.parameters:
                model_stage_props.update(out_.parameters)

        if not node_model.op:
            return self.create_exit_node(node_model)

        if node_model.inputs or []:
            for in_ in node_model.inputs:
                if in_.parameters:
                    model_stage_props.update(in_.parameters)

        if node_model.connection:
            model_stage_props.update(node_model.connection.properties)

        return self.create_stage_node(node_model, model_stage_props)

    def generate_model_node(self, model_node: models.ModelNode):
        raise NotImplementedError("Model node generation is not supported yet")

    # def generate_super_node(self, super_node: models.Supernode):
    #     if hasattr(super_node.subflow_ref, "url") and super_node.subflow_ref.url:
    #         # If the url is present, then the subflow must be external
    #         # Use a placeholder SuperNodeRef here so that we can import the subflow asset later
    #         name = super_node.subflow_ref.name
    #         node = SuperNodeRef(self.fc._dag, name)
    #         self.dag.add_node(node)
    #         return node

    #     # URL is not present, so the subflow must be local
    #     # First, find the pipeline model referenced by the ID
    #     pipeline_id_ref = super_node.subflow_ref.pipeline_id_ref
    #     pipeline: models.Pipeline | None = None
    #     for pipe in self.flow_model.pipelines:
    #         if pipe.id == pipeline_id_ref:
    #             pipeline = pipe
    #             break

    #     if not pipeline:
    #         raise ValueError(f"Could not find local subflow referenced by ID {pipeline_id_ref}")

    #     flow_model = models.Flow(
    #         pipelines=[pipeline],
    #         schemas=self.flow_model.schemas,
    #         primary_pipeline=pipeline_id_ref,
    #     )
    #     pipeline_dag_gen = DAGGenerator(flow_model)
    #     dag = pipeline_dag_gen.generate()._dag

    #     entry_nodes = filter(
    #         lambda node: isinstance(node, EntryNode),
    #         self.dag.nodes(),
    #     )
    #     exit_nodes = filter(
    #         lambda node: isinstance(node, ExitNode),
    #         self.dag.nodes(),
    #     )
    #     name = pipeline.name or super_node.app_data.ui_data.label
    #     node = SuperNode(
    #         parent_dag=self.dag,
    #         subflow_dag=dag,
    #         is_local=True,
    #         entry_nodes=entry_nodes,
    #         exit_nodes=exit_nodes,
    #         name=name,
    #     )

    #     self.dag.add_node(node)
    #     return node

    # def create_build_stage_node(self, node_model: models.ExecutionNode, model_stage_props: dict):
    #     model_stage_props["op_name"] = node_model.op
    #     build_stage_model = build_stage.model_construct(**model_stage_props)
    #     property_names = [value.alias for value in build_stage_model.model_fields.values()] + [
    #         key for key in build_stage_model.model_fields.keys()
    #     ]
    #     properties = {}
    #     for prop in model_stage_props:
    #         if prop not in property_names and prop not in [
    #             "showPartType",
    #             "showCollType",
    #             "showSortOptions",
    #             "conversion",
    #             "operator",
    #             "keyColsPart",
    #             "outputName",
    #             "outputcolProperties",
    #         ]:
    #             properties[prop] = model_stage_props[prop]
    #     build_stage_stage = BuildStageStage(
    #         dag=self.fc._dag,
    #         build_stage_asset=None,
    #         label=node_model.app_data.ui_data.label,
    #         configuration=build_stage_model,
    #     )
    #     build_stage_stage.properties = properties
    #     self.dag.add_node(build_stage_stage)
    #     return build_stage_stage

    # def create_wrapped_stage_node(self, node_model: models.ExecutionNode, model_stage_props: dict):
    #     model_stage_props["op_name"] = node_model.op
    #     wrapped_stage_model = wrapped_stage.model_construct(**model_stage_props)
    #     property_names = [value.alias for value in wrapped_stage_model.model_fields.values()] + [
    #         key for key in wrapped_stage_model.model_fields.keys()
    #     ]
    #     properties = {}
    #     for prop in model_stage_props:
    #         if prop not in property_names and prop not in [
    #             "showPartType",
    #             "showCollType",
    #             "showSortOptions",
    #             "conversion",
    #             "operator",
    #             "properties_order",
    #             "keyColsPart",
    #             "outputName",
    #             "outputcolProperties",
    #         ]:
    #             properties[prop] = model_stage_props[prop]
    #     wrapped_stage_stage = WrappedStageStage(
    #         dag=self.fc._dag,
    #         wrapped_stage_asset=None,
    #         label=node_model.app_data.ui_data.label,
    #         configuration=wrapped_stage_model,
    #     )
    #     wrapped_stage_stage.properties = properties
    #     self.dag.add_node(wrapped_stage_stage)
    #     return wrapped_stage_stage

    # def create_custom_stage_node(self, node_model: models.ExecutionNode, model_stage_props: dict):
    #     model_stage_props["op_name"] = node_model.op
    #     custom_stage_model = custom_stage.model_construct(**model_stage_props)
    #     property_names = [value.alias for value in custom_stage_model.model_fields.values()] + [
    #         key for key in custom_stage_model.model_fields.keys()
    #     ]
    #     properties = {}
    #     for prop in model_stage_props:
    #         if prop not in property_names and prop not in [
    #             "showPartType",
    #             "showCollType",
    #             "showSortOptions",
    #             "conversion",
    #             "operator",
    #             "preserve",
    #             "outputName",
    #             "outputcolProperties",
    #         ]:
    #             properties[prop] = model_stage_props[prop]
    #     custom_stage_stage = CustomStageStage(
    #         dag=self.fc._dag,
    #         custom_stage_asset=None,
    #         label=node_model.app_data.ui_data.label,
    #         configuration=custom_stage_model,
    #     )
    #     custom_stage_stage.properties = properties
    #     self.dag.add_node(custom_stage_stage)
    #     return custom_stage_stage

    # def create_entry_node(self, node_model: models.BindingEntryNode):
    #     """Creates an entry node generally used in subflows"""
    #     node = EntryNode(self.fc._dag)
    #     self.dag.add_node(node)
    #     return node

    # def create_exit_node(self, node_model: models.BindingExitNode):
    #     """Creates an exit node generally used in subflows"""
    #     node = ExitNode(self.fc._dag)
    #     self.dag.add_node(node)
    #     return node

    def create_stage_node(
        self,
        node_model: models.ExecutionNode | models.BindingEntryNode | models.BindingExitNode,
        model_stage_props: dict,
    ) -> StageNode:
        """Creates a model stage node from the given internal operator name and a dictionary of the model properties"""

        if node_model.op in OP_MAPPINGS:
            op_name = OP_MAPPINGS[node_model.op]
        else:
            op_name = "peek"
        connection_model_node = None
        java_library_model_node = None
        if (
            hasattr(node_model, "connection")
            and node_model.connection
            and (node_model.connection.ref and node_model.connection.ref != "local")
        ):
            if node_model.connection.name:
                conn_name = node_model.connection.name
            elif node_model.connection.connData and node_model.connection.connData["connectionName"]:
                conn_name = node_model.connection.connData["connectionName"]
            else:
                conn_name = node_model.app_data.ui_data.label + "_connection"

            connection_model_node = self.create_connection_model(op_name=op_name, asset_id=node_model.connection.ref, name=conn_name)
        if node_model.op == "JavaStagePX":
            files = node_model.parameters["classpath"].split(";")
            if len(files) > 1:
                secondary_files = files[1:]
            else:
                secondary_files = []

            if "asset_name" in node_model.parameters and "asset_id" in node_model.parameters:
                java_library_model_node = self.create_java_library_model(
                    name=node_model.parameters["asset_name"],
                    asset_id=node_model.parameters["asset_id"],
                    primary_file=files[0],
                    secondary_files=secondary_files,
                )

        stage_model = instantiate_stage_model(model_class=op_name, model_stage_props=model_stage_props)

        if connection_model_node:
            stage_model.connection = connection_model_node
        if java_library_model_node:
            stage_model.java_library = java_library_model_node

        stage_node = instantiate_stage_node(op_name, self.fc._dag, stage_model)

        self.dag.add_node(stage_node)
        return stage_node

    # TODO refactor to support creating connections
    def create_connection_model(self, op_name: str, asset_id: str, name: str):
        conn_props = {"asset_id": asset_id, "name": name}
        conn_model = instantiate_connection_model(op_name=op_name, conn_props=conn_props)

        return conn_model

    # def create_java_library_model(self, name: str, asset_id: str, primary_file: str, secondary_files: list[str]):
    #     jl_props = {
    #         "name": name,
    #         "asset_id": asset_id,
    #         "primary_file": primary_file,
    #         "secondary_files": secondary_files,
    #     }
    #     jl_model = instantiate_java_library_model(jl_props)
    #     return jl_model

    # def process_paramsets(self, paramset_model: models.ParamSet):
    #     return ParameterSet(name=paramset_model.name, asset_id=paramset_model.ref)

    # def process_localparams(self, local_params: list[dict]):
    #     if not local_params:
    #         return None
    #     return LocalParameters.from_dict({"parameters": local_params})

    # def process_message_handler(self, message_handler_id: str):
    #     return MessageHandler(name="referenced_message_handler", asset_id=message_handler_id)

    # def process_local_message_handler(self, local_messages: list[dict]):
    #     if not local_messages:
    #         return None
    #     return LocalMessageHandler(**{"messages": local_messages})

    # def process_runtime(self, app_data: models.AppData):
    #     if (app_data and hasattr(app_data, "datastage") and app_data.datastage) and (
    #         app_data.datastage.get("date_format")
    #         or app_data.datastage.get("timestamp_format")
    #         or app_data.datastage.get("decimal_separator")
    #         or app_data.datastage.get("time_format")
    #     ):
    #         format = Format(
    #             date_format=app_data.datastage.get("date_format"),
    #             timestamp_format=app_data.datastage.get("timestamp_format"),
    #             decimal_separator=app_data.datastage.get("decimal_separator"),
    #             time_format=app_data.datastage.get("time_format"),
    #         )
    #     else:
    #         format = None

    #     settings = None
    #     retention = (
    #         app_data.datastage.get("runArtifactRetentionJob")
    #         if app_data and hasattr(app_data, "datastage") and app_data.datastage
    #         else None
    #     )
    #     if retention:
    #         retention.get("retentionData")
    #     if retention and "days" in retention:
    #         settings = RuntimeSettings(retention_days=retention["days"])
    #     elif retention and "amount" in retention:
    #         settings = RuntimeSettings(retention_amount=retention["amount"])

    #     # TODO add ps/vs support
    #     return Runtime(runtime_settings=settings, format=format)


class ConnectionGenerator:
    def __init__(self, conn_json: dict):
        self.conn_json = conn_json
        self.conn_type = OP_MAPPINGS[DATASOURCE_MAPPINGS[conn_json["datasource_type"]]]

    def create_connection_model(self):
        conn_props = self.conn_json["properties"]
        conn_props["name"] = self.conn_json["name"]
        return instantiate_connection_model(op_name=self.conn_type, conn_props=conn_props)


# class JavaLibraryGenerator:
#     def __init__(self, jl_data: dict):
#         self.jl_data = jl_data

#     def create_java_library_model(self, output_path: str, write_to_output: bool):
#         entity = self.jl_data["entity"]
#         primary_jar_content = entity["primary_jar_content"]
#         primary_jar_name = list(entity["primary"])[0]
#         if write_to_output:
#             if not os.path.exists(output_path):
#                 _check_create_dir(os.getcwd() + "/attachments")
#                 output_path = os.getcwd()
#             else:
#                 _check_create_dir(output_path + "/attachments")
#             with open(Path(output_path) / "attachments" / (Path(primary_jar_name)), "wb") as f:
#                 f.write(base64.b64decode(primary_jar_content))
#         jl_props = {}
#         jl_props["primary_file"] = primary_jar_name
#         print(primary_jar_name)
#         secondary_files = []
#         for secondary_file in entity["secondary"]:
#             if write_to_output:
#                 with open(
#                     Path(output_path) / "attachments" / (Path(secondary_file["jar_file_name"])),
#                     "wb",
#                 ) as f:
#                     f.write(base64.b64decode(secondary_file["jar_file_content"]))
#             secondary_files.append(secondary_file["jar_file_name"])
#         jl_props["secondary_files"] = secondary_files
#         jl_props["name"] = self.jl_data["name"]
#         jl_props["description"] = self.jl_data["description"]
#         return instantiate_java_library_model(jl_props)


# class FunctionLibraryGenerator:
#     def __init__(self, fl_data: dict):
#         self.fl_data = fl_data

#     def create_function_library_model(self, output_path: str, write_to_output: bool):
#         entity = self.fl_data["entity"]
#         so_file_content = entity["so_file_content"]
#         function_library_name = list(entity["custom_function_name"])[0]
#         if write_to_output:
#             if not os.path.exists(output_path):
#                 _check_create_dir(os.getcwd() + "/attachments")
#                 output_path = os.getcwd()
#             else:
#                 _check_create_dir(output_path + "/attachments")
#             with open(Path(output_path) / "attachments" / (Path(function_library_name)), "wb") as f:
#                 f.write(base64.b64decode(so_file_content))
#         fl_props = {}
#         fl_props["library_path"] = function_library_name
#         fl_props["name"] = self.fl_data["name"]
#         fl_props["description"] = self.fl_data["description"]
#         return instantiate_function_library_model(fl_props)


# class MatchSpecificationGenerator:
#     def __init__(self, ms_data: dict):
#         self.ms_data = ms_data

#     def create_match_specification_model(self, output_path: str, write_to_output: bool):
#         entity = self.ms_data["entity"]
#         mat_json = entity["content"]["mat"]["MATCHSPEC"]
#         passes_json = entity["content"]["passes"]

#         if write_to_output:
#             if not os.path.exists(output_path):
#                 _check_create_dir(os.getcwd() + "/attachments")
#                 output_path = os.getcwd()
#             else:
#                 _check_create_dir(output_path + "/attachments")

#         match_properties = MatchSpecification.create_match_properties(self.ms_data["name"], mat_json, passes_json)

#         return instantiate_match_specification_model(match_properties)


# class JobGenerator:
#     def __init__(self, job_json: dict):
#         self.job_json = job_json

#     def create_job_model(self):
#         schedule_info = self.job_json.get("schedule_info")
#         start, end, repeat = None, None, None
#         if schedule_info:
#             start = schedule_info.get("startOn")
#             start = str(datetime.datetime.fromtimestamp(start / 1000)).replace(":", "-") if start else start
#             end = schedule_info.get("endOn")
#             end = str(datetime.datetime.fromtimestamp(end / 1000)).replace(":", "-") if end else end
#             repeat = schedule_info.get("repeat")
#         schedule = self.job_json.get("schedule")
#         schedule_obj = None
#         if schedule_info or schedule:
#             schedule_obj = Schedule(start=start, end=end, repeat=repeat, schedule=schedule)

#         parameter_sets = self.job_json.get("parameter_sets")
#         value_sets = {}
#         if parameter_sets:
#             for param_set in parameter_sets:
#                 value_sets[param_set.get("name")] = param_set.get("value_set")
#         runtime_parameters = RuntimeParameters(value_sets=value_sets)

#         job_settings = JobSettings(runtime_parameters=runtime_parameters, schedule=schedule_obj)

#         return job_settings
