"""This module converts a flow DAG (Directed Acyclic Graph) into structured Pydantic models for
a JSON representation of the flow ("flow JSON").

Algorithm overview:
- The `FlowExtractor` initializes the conversion process, managing multiple `PipelineExtractor` instances.
- Each `PipelineExtractor` processes a `DAG`, creating node, link, and port representations.
- Nodes in the DAG are mapped to `AbstractNodeExtractor` subclasses (`ExecutionNodeExtractor`,
  `BindingNodeExtractor`, etc.) based on their type.
- Edges in the DAG are converted into `LinkExtractor` objects, while their connections are handled by
  `InputPortExtractor` and `OutputPortExtractor`.
- Supernodes, representing subflows, are processed via `SuperNodeExtractor`.

Classes:
- `FlowExtractor`: Manages pipeline extraction from the DAG.
- `PipelineExtractor`: Represents a pipeline, mapping nodes and links.
- `AbstractNodeExtractor` (and subclasses): Converts DAG nodes into model representations.
- `LinkExtractor`: Handles links between nodes.
- `InputPortExtractor` / `OutputPortExtractor`: Defines node ports that links may connect to.

The final output is a `model.Flow` object, encapsulating the DataStage flow in a format that can be directly dumped as
a flow JSON importable into the canvas UI or run as a job.
"""

import json
import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as model
from abc import ABC, abstractmethod
import pydantic
from ibm_watsonx_data_integration.services.datastage.models.acp import ACP
from ibm_watsonx_data_integration.services.datastage.models.flow.dag import (
    DAG,
    Link,
    StageNode,
    Node,
    StageNode,
)
from ibm_watsonx_data_integration.services.datastage.models.schema.schema import Schema

from typing import Any
from uuid import uuid4

from ibm_watsonx_data_integration.services.datastage.models.stage_models.address_verification import address_verification
from ibm_watsonx_data_integration.services.datastage.models.stage_models.aggregator import aggregator
from ibm_watsonx_data_integration.services.datastage.models.stage_models.bloom_filter import bloom_filter
from ibm_watsonx_data_integration.services.datastage.models.stage_models.change_apply import change_apply
from ibm_watsonx_data_integration.services.datastage.models.stage_models.change_capture import change_capture
from ibm_watsonx_data_integration.services.datastage.models.stage_models.checksum import checksum
from ibm_watsonx_data_integration.services.datastage.models.stage_models.column_export import column_export
from ibm_watsonx_data_integration.services.datastage.models.stage_models.column_generator import column_generator
from ibm_watsonx_data_integration.services.datastage.models.stage_models.column_import import column_import
from ibm_watsonx_data_integration.services.datastage.models.stage_models.compare import compare
from ibm_watsonx_data_integration.services.datastage.models.stage_models.complex_flat_file import complex_flat_file
from ibm_watsonx_data_integration.services.datastage.models.stage_models.complex_stages.complex_flat_file import Record, RecordID
from ibm_watsonx_data_integration.services.datastage.models.stage_models.difference import difference
from ibm_watsonx_data_integration.services.datastage.models.stage_models.funnel import funnel
from ibm_watsonx_data_integration.services.datastage.models.stage_models.generic import generic
from ibm_watsonx_data_integration.services.datastage.models.stage_models.join import join
from ibm_watsonx_data_integration.services.datastage.models.stage_models.lookup import lookup
from ibm_watsonx_data_integration.services.datastage.models.stage_models.match_frequency import match_frequency
from ibm_watsonx_data_integration.services.datastage.models.stage_models.peek import peek
from ibm_watsonx_data_integration.services.datastage.models.stage_models.pivot import pivot
from ibm_watsonx_data_integration.services.datastage.models.stage_models.sort import sort
from ibm_watsonx_data_integration.services.datastage.models.stage_models.standardize import standardize
from ibm_watsonx_data_integration.services.datastage.models.stage_models.transformer import transformer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ibm_watsonx_data_integration.services.datastage.models.flow import DataStageFlow

import logging
logger = logging.getLogger(__name__)


def generate_uuid():
    """Generate a unique identifier as a string."""
    return uuid4().__str__()


def satisfies_min_cardinality(cardinality: int, min_cardinality: int):
    """Returns True if the cardinality is greater than or equal to the minimum cardinality. If the minimum cardinality
    is -1, it is ignored.
    """
    return min_cardinality == -1 or cardinality >= min_cardinality


def satisfies_max_cardinality(cardinality: int, max_cardinality: int):
    """Returns True if the cardinality is less than or equal to the maximum cardinality. If the maximum cardinality
    is -1, it is ignored.
    """
    return max_cardinality == -1 or cardinality <= max_cardinality


class AbstractIdent(ABC):
    """Abstract class providing a unique identifier for each instance."""

    def __init__(self):
        self.__id = generate_uuid()

    @property
    def id(self):
        return self.__id


def verify_node_cardinality(node: Node, dag: DAG):
    assert dag.is_metadata_computed

    primary_in = node.metadata.get("primary_inputs", 0)
    primary_out = node.metadata.get("primary_outputs", 0)
    reject_out = node.metadata.get("reject_outputs", 0)
    reference_in = node.metadata.get("reference_inputs", 0)

    # Get expected cardinality
    min_primary_in = node._get_min_primary_inputs()
    max_primary_in = node._get_max_primary_inputs()
    min_primary_out = node._get_min_primary_outputs()
    max_primary_out = node._get_max_primary_outputs()
    min_reject_out = node._get_min_reject_outputs()
    max_reject_out = node._get_max_reject_outputs()
    min_reference_in = node._get_min_reference_inputs()
    max_reference_in = node._get_max_reference_inputs()

    # Check primary input cardinality
    if not satisfies_min_cardinality(primary_in, min_cardinality=min_primary_in):
        logger.warning(
            f"\n{node.__class__.__name__} {node} has insufficient primary inputs: {primary_in}, min: {min_primary_in}",
        )
    if not satisfies_max_cardinality(primary_in, max_cardinality=max_primary_in):
        raise ValueError(
            f"\n{node.__class__.__name__} {node} has too many primary inputs: {primary_in}, max: {max_primary_in}"
        )

    # Check primary output cardinality
    if not satisfies_min_cardinality(primary_out, min_cardinality=min_primary_out):
        logger.warning(
            f"\n{node.__class__.__name__} {node} has insufficient primary outputs: {primary_out}, min: {min_primary_out}",
        )
    if not satisfies_max_cardinality(primary_out, max_cardinality=max_primary_out):
        raise ValueError(
            f"\n{node.__class__.__name__} {node} has too many primary outputs: {primary_out}, max: {max_primary_out}"
        )

    # Check reject output cardinality
    if not satisfies_min_cardinality(reject_out, min_cardinality=min_reject_out):
        logger.warning(
            f"\n{node.__class__.__name__} {node} has insufficient reject outputs: {reject_out}, min: {min_reject_out}",
        )
    if not satisfies_max_cardinality(reject_out, max_cardinality=max_reject_out):
        raise ValueError(
            f"\n{node.__class__.__name__} {node} has too many reject outputs: {reject_out}, max: {max_reject_out}"
        )

    # Check reference input cardinality
    if not satisfies_min_cardinality(reference_in, min_cardinality=min_reference_in):
        logger.warning(
            f"\n{node.__class__.__name__} {node} has insufficient reference inputs: {reference_in}, min: {min_reference_in}",
        )
    if not satisfies_max_cardinality(reference_in, max_cardinality=max_reference_in):
        raise ValueError(
            f"\n{node.__class__.__name__} {node} has too many reference inputs: {reference_in}, max: {max_reference_in}"
        )

    if isinstance(node, StageNode):
        node.configuration.input_count = primary_in + reference_in
        node.configuration.output_count = primary_out + reject_out


class FlowExtractor(AbstractIdent):
    """Extracts a flow model from a flow DAG. This is the master class that accepts a flow DAG and represents its
    entirety as a flow model.

    To use: instantiate FlowExtractor with your DAG, then call extract(), and then call serialize().
    """

    def __init__(self, fc: "DataStageFlow"):
        super().__init__()
        self.fc = fc
        self.top_level_dag = fc._dag
        self.all_nodes: dict[Node, AbstractNodeExtractor] = {}
        self.schemas: list[SchemaExtractor] = []
        self.pipelines: dict[DAG, PipelineExtractor] = {}

    def get_or_create_node_extractor(self, pipeline: "PipelineExtractor", node: Node):
        """Creates a node extractor based on its type."""
        if ext := self.all_nodes.get(node):
            return ext

        if isinstance(node, StageNode):
            if hasattr(node.configuration, "connection"):
                ext = ConnectorNodeExtractor(pipeline, node)
            else:
                match node._get_node_type():
                    case "binding":
                        ext = BindingNodeExtractor(pipeline, node)
                    case "execution_node":
                        ext = ExecutionNodeExtractor(pipeline, node)

        if ext:
            self.all_nodes[node] = ext
            return ext
        else:
            raise NotImplementedError(f"Unsupported node type: {type(node)}")

    def extract(self):
        """Extracts complete pipelines from the DAG."""
        # Add the top level DAG as the primary pipeline
        self.pipelines[self.top_level_dag] = PipelineExtractor(self, self.top_level_dag)

        self.pipelines[self.top_level_dag].extract()

        # Verify the cardinality of every node in the flow
        for node in self.all_nodes.keys():
            verify_node_cardinality(node, self.top_level_dag)

        # Apply global RCP value to all nodes
        if self.fc.rcp:
            for node in self.all_nodes.keys():
                if isinstance(node, StageNode):
                    node.configuration.runtime_column_propagation = True

    def serialize(self):
        """Serializes the flow into a model.Flow object."""
        if not self.pipelines:
            raise ValueError("No pipelines found. Did you call extract()?")

        pipelines: list[model.Pipeline] = []
        for pipe in self.pipelines.values():
            pipelines.append(pipe.serialize())

        primary_pipeline = self.pipelines[self.top_level_dag]

        app_data = model.AppData()
        app_data.additionalProperties = {"globalAcp": self.fc.acp}

        return model.Flow(
            id=self.id,
            doc_type="pipeline",
            primary_pipeline=primary_pipeline.id,
            pipelines=pipelines,
            schemas=[sch.serialize() for sch in self.schemas],
            app_data=app_data,
        )

class PipelineExtractor(AbstractIdent):
    """Extracts a complete pipeline model, including all of its nodes, links, and ports, from a DAG."""

    def __init__(
        self,
        parent_flow: FlowExtractor,
        dag: DAG,
    ):
        super().__init__()
        self.parent_flow = parent_flow
        self.dag = dag
        self.used_link_names = set()
        self.links: dict[Link, LinkExtractor] = {}
        self.input_ports: dict[Link, InputPortExtractor] = {}
        self.output_ports: dict[Link, OutputPortExtractor] = {}
        self.schemas: dict[str, model.RecordSchema] = {}


    def extract(self):
        """Extracts nodes, links, and ports from the pipeline."""
        # Reset link counter to 1
        LinkExtractor.reset_counter()

        if not self.dag.is_metadata_computed:
            self.dag.compute_metadata()

        for link in self.dag.links_stable():
            # Get or create a link extractor while enforcing link name uniqueness
            if link not in self.links:
                link_ext = self.links.setdefault(link, LinkExtractor(self, link))
                self.used_link_names.add(link_ext.get_link_name())
            else:
                link_ext = self.links[link]

            src_node = self.parent_flow.get_or_create_node_extractor(self, link.src)
            dest_node = self.parent_flow.get_or_create_node_extractor(self, link.dest)

            schema: model.RecordSchema | None = None

            # Check if link has a schema attached. If so, use it. Otherwise, fallback to schema attached to src node.
            if link.schema:
                schema = link.schema.configuration
            elif len(src_node.inputs) > 0 or (
                hasattr(src_node.node, "configuration") and src_node.node.configuration.op_name == "PxCFF"
            ):
                input_nodes = src_node.inputs[:]
                for input_node in input_nodes:
                    if not input_node.schema:
                        input_node.schema = SchemaExtractor(parent_flow=self.parent_flow, schema=Schema())

                acp = ACP(
                    link=link,
                    src_input_nodes=input_nodes,
                    src_ext=src_node,
                    dest_ext=dest_node,
                )

                schema = acp.compute_schema()
                #link.schema = schema

            # Create a schema extractor if applicable
            schema_ext: SchemaExtractor | None = None
            if schema:
                schema_ext = SchemaExtractor(self.parent_flow, schema)
                self.parent_flow.schemas.append(schema_ext)

            if isinstance(link.src, StageNode):
                src_output_port = self.output_ports.setdefault(
                    link,
                    OutputPortExtractor(self, link_ext, src_node, schema_ext),
                )

            dest_out_port = None
            if isinstance(link.dest, StageNode):
                dest_input_port = self.input_ports.setdefault(
                    link,
                    InputPortExtractor(self, link_ext, dest_node, schema_ext),
                )

            if link.dest.metadata["out_degree"] == 0:
                dest_out_port = PlainOutputPortExtractor(dest_node)

            dest_node.inputs.append(dest_input_port)
            if dest_out_port:
                if link.dest.metadata["out_degree"] == 0: #not self.is_subflow and :
                    if not len(dest_node.outputs):
                        dest_node.outputs.append(dest_out_port)
                else:
                    dest_node.outputs.append(dest_out_port)
            src_node.outputs.append(src_output_port)

        for node in self.dag.adj:
            if not self.dag.adj[node]:
                self.parent_flow.get_or_create_node_extractor(self, node)

    def serialize(self):
        """Serializes the pipeline into a model.Pipeline object."""
        #comment_models = [comm.serialize() for comm in self.comments.values()]
        node_models = []
        for node in self.dag.nodes():
            #if not isinstance(node, CommentNode):
            mod = self.parent_flow.all_nodes[node].serialize() if node in self.parent_flow.all_nodes else None
            if mod:
                node_models.append(mod)

        return model.Pipeline(
            id=self.id,
            name=None,
            description="",
            runtime_ref="pxOsh",
            app_data=model.PipelineAppData(ui_data=model.PipelineUI()),
            nodes=node_models,
        )

class SchemaExtractor(AbstractIdent):
    def __init__(self, parent_flow: FlowExtractor, schema: model.RecordSchema):
        super().__init__()
        self.parent_flow = parent_flow
        self.schema = schema

    def serialize(self) -> model.RecordSchema:
        self.schema.id = self.id
        return model.RecordSchema(
            id=self.id,
            name=self.schema.name,
            json_schema=self.schema.json_schema,
            type=self.schema.type,
            fields=self.schema.fields,
            struct_types=self.schema.struct_types,
        )


class LinkExtractor(AbstractIdent):
    """Extracts a link between nodes in a pipeline."""

    # Counter keeps track of the global number of instantiated links. It is used to label links with unique numbers.
    counter = 1

    def __init__(self, parent_pipe: PipelineExtractor, link: Link):
        super().__init__()
        self.parent_pipe = parent_pipe
        self.link = link
        self.num = LinkExtractor.counter
        LinkExtractor.counter += 1

    @classmethod
    def reset_counter(cls):
        cls.counter = 1

    def get_link_name(self):
        if self.link.name:
            return self.link.name
        else:
            return f"Link_{self.num}"

    def serialize(self):
        """Serializes the link into a model.NodeLink object."""
        app_data = model.LinkAppData(
            ui_data=model.NodeLinkUI(class_name="", decorations=[]),
        )

        ds_app_data = {}
        if self.link.maps_to_link:
            ds_app_data["partner_link_in"] = self.link.maps_to_link
        if self.link.maps_from_link:
            ds_app_data["partner_link_out"] = self.link.maps_from_link
        app_data.datastage = ds_app_data

        return model.NodeLink(
            id=self.id,
            link_name=self.get_link_name(),
            type_attr=self.link.type,
            node_id_ref=self.parent_pipe.parent_flow.all_nodes[self.link.src].id,
            port_id_ref=self.parent_pipe.output_ports[self.link].id,
            app_data=app_data,
        )


class AbstractNodeExtractor(AbstractIdent):
    """Abstract class representing a node extractor in a pipeline."""

    def __init__(self, parent_pipe: PipelineExtractor, stage_node: StageNode):
        super().__init__()
        self.parent_pipe = parent_pipe
        self.inputs: list[InputPortExtractor] = []
        self.outputs: list[OutputPortExtractor] = []
        self.stage_node: StageNode = stage_node
        self.node: Node = stage_node

    @abstractmethod
    def get_input_port_params(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_output_port_params(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def serialize(self) -> pydantic.BaseModel:
        """Abstract method to serialize the node extractor."""
        pass

    def _serialize_ui_data(self, node: Node) -> model.NodeUI:
        if not isinstance(node, StageNode):
            raise TypeError()
        ui_data = model.NodeUI(
            x_pos=node.metadata.get("x"),
            y_pos=node.metadata.get("y"),
            image=node._get_image(),
            label=node._get_node_label()
            # or self.parent_pipe.ui_gen.lg._get_node_label(node._get_op_name()),
        )

        if width := node.metadata.get("width"):
            ui_data.resize_width = width
            ui_data.is_resized = True
        if height := node.metadata.get("height"):
            ui_data.resize_height = height
            ui_data.is_resized = True

        return ui_data

class ExecutionNodeExtractor(AbstractNodeExtractor):
    """Extracts an execution node within a pipeline."""

    def __init__(self, parent_pipe: PipelineExtractor, stage_node: StageNode):
        super().__init__(parent_pipe, stage_node)
        if not isinstance(stage_node, StageNode):
            raise TypeError()
        self.node: StageNode = stage_node

    def get_input_port_params(self, link=None) -> dict[str, Any]:
        return self.node._get_input_port_params(link)

    def get_output_port_params(self, link=None) -> dict[str, Any]:
        return self.node._get_output_port_params(link)

    def get_output_schema(self) -> model.RecordSchema | None:
        return self.node._get_output_schema()

    def set_output_schema(self, schema: model.RecordSchema):
        self.node._set_output_schema(schema)

    def get_cff_stage_records(self):
        assert isinstance(self.node.configuration, complex_flat_file)
        schemas = []
        stage_records = []
        column_names = []
        for record in self.node.configuration.records:
            for column in record.columns:
                column.mf_update_value = record.name
                if column.name in column_names:
                    logger.warning(
                        f"\nFound duplicate column {column.name} in Complex Flat File stage {self.node.label}",
                    )
                else:
                    column_names.append(column.name)
        for record in self.node.configuration.records:
            assert isinstance(record, Record)
            found_record_id = False
            for record_id in self.node.configuration.records_id:
                assert isinstance(record_id, RecordID)
                if record.name == record_id.record_name:
                    found_record_id = True
                    fields = [column._to_field() for column in record.columns]
                    schema = model.RecordSchema(id="", fields=fields)
                    schema_ext = SchemaExtractor(
                        self.parent_pipe.parent_flow, schema=schema
                    )
                    schemas.append(schema_ext)
                    stage_record = record_id.model_dump(
                        by_alias=True, exclude_none=True
                    )
                    stage_record["schema_ref"] = schema_ext.id
                    stage_records.append(stage_record)
                    break
            if not found_record_id:
                fields = [column._to_field() for column in record.columns]
                schema = model.RecordSchema(id="", fields=fields)
                schema_ext = SchemaExtractor(
                    self.parent_pipe.parent_flow, schema=schema
                )
                schemas.append(schema_ext)
                stage_records.append(
                    {
                        "name": record.name,
                        "record_name": record.name,
                        "schema_ref": schema_ext.id,
                    }
                )
        self.parent_pipe.parent_flow.schemas.extend(schemas)
        if (
            not len(self.node.configuration.records)
            and self.node.configuration.records_id
        ):
            for records_id in self.node.configuration.records_id:
                stage_record = records_id.model_dump(
                    by_alias=True, exclude_none=True, exclude_unset=True
                )
                stage_records.append(stage_record)
        return stage_records

    def get_join_inputs_order(self):
        assert isinstance(self.node.configuration, join)
        if (
            hasattr(self.node.configuration, "inputlink_ordering_list")
            and self.node.configuration.inputlink_ordering_list is not None
        ):
            ordering_list = self.node.configuration.inputlink_ordering_list
            inputs_order = []
            for link in ordering_list:
                if "link_label" in link and link["link_label"] == "Left":
                    link_name = link["link_name"] if "link_name" in link else None
                    if link_name:
                        for input in self.inputs:
                            if input.link.get_link_name() == link_name:
                                inputs_order.append(input.id)
            if len(ordering_list) > 2:
                for i in range(1, len(ordering_list) - 1):
                    for link in ordering_list:
                        if (
                            "link_label" in link
                            and link["link_label"] == f"Intermediate {i}"
                        ):
                            link_name = (
                                link["link_name"] if "link_name" in link else None
                            )
                            if link_name:
                                for input in self.inputs:
                                    if input.link.get_link_name() == link_name:
                                        inputs_order.append(input.id)
            for link in ordering_list:
                if "link_label" in link and link["link_label"] == "Right":
                    link_name = link["link_name"] if "link_name" in link else None
                    if link_name:
                        for input in self.inputs:
                            if input.link.get_link_name() == link_name:
                                inputs_order.append(input.id)
            return "|".join(inputs_order)
        else:
            return None

    def get_lookup_inputs_order(self):
        assert isinstance(self.node.configuration, lookup)
        if (
            hasattr(self.node.configuration, "inputlink_ordering_list")
            and self.node.configuration.inputlink_ordering_list is not None
        ):
            ordering_list = self.node.configuration.inputlink_ordering_list
            inputs_order = []
            for i in range(1, len(ordering_list)):
                for link in ordering_list:
                    if "link_label" in link and link["link_label"] == f"Lookup {i}":
                        link_name = link["link_name"] if "link_name" in link else None
                        if link_name:
                            for input in self.inputs:
                                if input.link.get_link_name() == link_name:
                                    inputs_order.append(input.id)
            for link in ordering_list:
                if "link_label" in link and link["link_label"] == "Primary":
                    link_name = link["link_name"] if "link_name" in link else None
                    if link_name:
                        for input in self.inputs:
                            if input.link.get_link_name() == link_name:
                                inputs_order.append(input.id)
            return "|".join(inputs_order)
        else:
            return None

    def get_lookup_outputs_order(self):
        assert isinstance(self.node.configuration, lookup)
        outputs_order = []
        for output in self.outputs:
            if output.link.link.type == "PRIMARY":
                outputs_order.append(output.id)
        for output in self.outputs:
            if output.link.link.type == "REFERENCE":
                outputs_order.append(output.id)
        for output in self.outputs:
            if output.link.link.type == "REJECT":
                outputs_order.append(output.id)
        return "|".join(outputs_order)

    def get_transformer_outputs_order(self):
        assert isinstance(self.node.configuration, transformer)
        outputs_order = []
        for output in self.outputs:
            if output.link.link.type == "PRIMARY":
                outputs_order.append(output.id)
        for output in self.outputs:
            if output.link.link.type == "REFERENCE":
                outputs_order.append(output.id)
        for output in self.outputs:
            if output.link.link.type == "REJECT":
                outputs_order.append(output.id)
        return "|".join(outputs_order)

    def get_change_capture_inputs_order(self):
        assert isinstance(self.node.configuration, change_capture)
        if (
            hasattr(self.node.configuration, "inputlink_ordering_list")
            and self.node.configuration.inputlink_ordering_list is not None
        ):
            ordering_list = self.node.configuration.inputlink_ordering_list
            inputs_order = []
            for link in ordering_list:
                if "link_label" in link and link["link_label"] == "Before":
                    link_name = link["link_name"] if "link_name" in link else None
                    if link_name:
                        for input in self.inputs:
                            if input.link.get_link_name() == link_name:
                                inputs_order.append(input.id)
            for link in ordering_list:
                if "link_label" in link and link["link_label"] == "After":
                    link_name = link["link_name"] if "link_name" in link else None
                    if link_name:
                        for input in self.inputs:
                            if input.link.get_link_name() == link_name:
                                inputs_order.append(input.id)
            return "|".join(inputs_order)
        else:
            return None

    def get_generic_inputs_order(self):
        assert isinstance(self.node.configuration, generic)
        if (
            hasattr(self.node.configuration, "inputlink_ordering_list")
            and self.node.configuration.inputlink_ordering_list is not None
        ):
            ordering_list = self.node.configuration.inputlink_ordering_list
            inputs_order = []
            for i in range(len(ordering_list)):
                for link in ordering_list:
                    if "link_label" in link and link["link_label"] == str(i):
                        link_name = link["link_name"] if "link_name" in link else None
                        if link_name:
                            for input in self.inputs:
                                if input.link.get_link_name() == link_name:
                                    inputs_order.append(input.id)
            return "|".join(inputs_order)
        else:
            return None

    def get_generic_outputs_order(self):
        assert isinstance(self.node.configuration, generic)
        if (
            hasattr(self.node.configuration, "outputlink_ordering_list")
            and self.node.configuration.outputlink_ordering_list is not None
        ):
            ordering_list = self.node.configuration.outputlink_ordering_list
            outputs_order = []
            for i in range(len(ordering_list)):
                for link in ordering_list:
                    if "link_label" in link and link["link_label"] == str(i):
                        link_name = link["link_name"] if "link_name" in link else None
                        if link_name:
                            for output in self.outputs:
                                if output.link.get_link_name() == link_name:
                                    outputs_order.append(output.id)
            return "|".join(outputs_order)
        else:
            return None

    def get_general_inputs_order(self):
        inputs_order = []
        for input in self.inputs:
            inputs_order.append(input.id)
        return "|".join(inputs_order)

    def get_general_outputs_order(self):
        outputs_order = []
        for output in self.outputs:
            outputs_order.append(output.id)
        return "|".join(outputs_order)

    def validate_cff_level_numbers(self):
        assert isinstance(self.node.configuration, complex_flat_file)
        for record in self.node.configuration.records:
            assert isinstance(record, Record)
            current_level_number = 2
            group = (
                record.columns[0].native_type.value == "GROUP"
                if len(record.columns)
                else False
            )
            for column in record.columns:
                if column.level == current_level_number:
                    continue
                if column.level > current_level_number:
                    if not group:
                        logger.warning(
                            f"\nColumn {column.name} has an invalid level number\n",
                        )
                    current_level_number = column.level
                group = column.native_type.value == "GROUP"
                current_level_number = column.level

    def process_rest_requests(self, requests):
        if not len(requests):
            return requests
        for i, request in enumerate(requests):
            request["id"] = i
            request["label"] = f"Request {i}"
        return requests

    def process_rest_schema(self):
        for output in self.outputs:
            if output.schema:
                for field in output.schema.schema.fields:
                    if "derivation" in field.app_data:
                        field.metadata.description = field.app_data["derivation"]

    def serialize(self):
        """Serializes the execution node into a model.ExecutionNode object."""
        ui_data = self._serialize_ui_data(self.node)
        inputs_order = None
        if self.node.configuration.op_name == "PxJoin":
            inputs_order = self.get_join_inputs_order()
        elif self.node.configuration.op_name == "PxLookup":
            inputs_order = self.get_lookup_inputs_order()
        elif self.node.configuration.op_name == "PxChangeCapture":
            inputs_order = self.get_change_capture_inputs_order()
        elif self.node.configuration.op_name == "PxGeneric":
            inputs_order = self.get_generic_inputs_order()
        elif (
            self.node.configuration.op_name in ["PxFunnel", "XMLStagePX"]
        ):
            inputs_order = self.get_general_inputs_order()

        outputs_order = None
        if self.node.configuration.op_name == "PxLookup":
            outputs_order = self.get_lookup_outputs_order()
        elif self.node.configuration.op_name == "CTransformerStage":
            outputs_order = self.get_transformer_outputs_order()
        elif self.node.configuration.op_name == "PxGeneric":
            outputs_order = self.get_generic_outputs_order()
        elif (
            self.node.configuration.op_name in ["PxJoin", "XMLStagePX"]
        ):
            outputs_order = self.get_general_outputs_order()

        stage_records = None
        if self.node.configuration.op_name == "PxCFF":
            self.validate_cff_level_numbers()
            stage_records = self.get_cff_stage_records()

        stage_records = None
        if self.node.configuration.op_name == "PxCFF":
            self.validate_cff_level_numbers()
            stage_records = self.get_cff_stage_records()

        datastage = {}
        if inputs_order is not None:
            datastage["inputs_order"] = inputs_order
        if outputs_order is not None:
            datastage["outputs_order"] = outputs_order
        if stage_records is not None:
            datastage["stage_records"] = stage_records

        if not len(datastage):
            datastage = None

        parameters = {
            **self.node._get_node_params(),
            **self.node._get_advanced_params(),
        }

        if self.node.configuration.op_name == "CTransformerStage":
            if "Triggers" in parameters:
                for trigger in parameters["Triggers"]:
                    if "arguments" in trigger:
                        args = trigger.pop("arguments")
                        trigger.update(args)

        if self.node.configuration.op_name == "PxColumnImport":
            if "schema" in parameters:
                parameters["schema"] = [
                    col_schema["ColumnName"] for col_schema in parameters["schema"]
                ]

        if self.node.configuration.op_name == "PxRest":
            if "requests" in parameters:
                parameters["requests"] = self.process_rest_requests(
                    parameters["requests"]
                )
            self.process_rest_schema()

        inputs = [ip.serialize() for ip in self.inputs]
        if not len(inputs):
            return model.ExecutionNode(
                id=self.id,
                op=self.node._get_op_name(),
                parameters=parameters,
                outputs=[op.serialize() for op in self.outputs],
                inputs=[
                    {
                        "id": "",
                        "app_data": {
                            "ui_data": {
                                "cardinality": {"min": 0, "max": 1},
                                "label": "inPort",
                            }
                        },
                    }
                ],
                app_data=model.NodeAppData(ui_data=ui_data, datastage=datastage),
            )
        else:
            return model.ExecutionNode(
                id=self.id,
                op=self.node._get_op_name(),
                parameters=parameters,
                inputs=[ip.serialize() for ip in self.inputs],
                outputs=[op.serialize() for op in self.outputs],
                app_data=model.NodeAppData(ui_data=ui_data, datastage=datastage),
            )


class BindingNodeExtractor(AbstractNodeExtractor):
    """Extracts a binding node within a pipeline."""

    def __init__(self, parent_pipe: PipelineExtractor, stage_node: StageNode):
        super().__init__(parent_pipe, stage_node)
        assert isinstance(stage_node, StageNode)
        self.node: StageNode = stage_node

    def get_input_port_params(self) -> dict[str, Any]:
        return self.node._get_input_port_params()

    def get_output_port_params(self) -> dict[str, Any]:
        return self.node._get_output_port_params()

    def get_source_connection_params(self):
        return self.node._get_source_connection_params()

    def get_target_connection_params(self):
        return self.node._get_target_connection_params()

    def serialize(self):
        """Serializes the binding node into a model.BindingEntryNode or model.BindingExitNode object."""
        ui_data = self._serialize_ui_data(self.node)

        # Binding nodes with inputs must be exit nodes (sinks), while those without inputs are entry nodes (sources).
        if self.inputs:
            return model.BindingExitNode(
                id=self.id,
                op=self.node._get_op_name(),
                parameters={
                    **self.node._get_node_params(),
                    **self.node._get_advanced_params(),
                },
                inputs=[ip.serialize() for ip in self.inputs],
                outputs=[op.serialize() for op in self.outputs],
                app_data=model.NodeAppData(ui_data=ui_data),
            )
        else:
            return model.BindingEntryNode(
                id=self.id,
                op=self.node._get_op_name(),
                parameters={
                    **self.node._get_node_params(),
                    **self.node._get_advanced_params(),
                },
                outputs=[op.serialize() for op in self.outputs],
                app_data=model.NodeAppData(ui_data=ui_data),
            )


class ConnectorNodeExtractor(BindingNodeExtractor):
    def __init__(self, parent_pipe: PipelineExtractor, stage_node: StageNode):
        super().__init__(parent_pipe, stage_node)
        self.node: StageNode = stage_node

        if self.node.metadata["out_degree"] > 0 and self.node.metadata["in_degree"] > 0:
            self.location = "both"
        elif self.node.metadata["out_degree"] > 0:
            self.location = "source"
        else:
            self.location = "target"

    def serialize(self):
        mod = super().serialize()
        mod.connection = self.serialize_connection()
        return mod

    def serialize_connection(self):
        """Serializes the connection into a model.CommonPipelineConnection object"""
        # if not hasattr(self.node.configuration, "connection") or (
        #     hasattr(self.node.configuration, "connection") and not self.node.configuration.connection
        # ):
        #     return None
        # return model.CommonPipelineConnection(
        #     name=self.node._get_connection_name(),
        #     ref=self.node._get_connection_id(),
        #     # catalog_ref="",
        #     project_ref=self.node._get_project_id(),
        #     # space_ref="",
        #     properties=self.node._get_connection_params(self.location),
        #     app_data=model.AppDataDef(),
        # )

        if not hasattr(self.node.configuration, "connection") or (
            hasattr(self.node.configuration, "connection")
            and not self.node.configuration.connection
        ):
            return None
        conn = self.node.configuration.connection
        properties = self.node._get_connection_params(self.location)
        ref = self.node._get_connection_id()

        if not ref:
            ref = "local"
            included = [field for field in conn.model_fields_set]
            properties |= json.loads(conn.model_dump_json(include=included, exclude_none=True, by_alias=True, warnings=False))

        return model.CommonPipelineConnection(
            name=self.node._get_connection_name(),
            ref=ref,
            # catalog_ref="",
            project_ref=self.node._get_project_id(),
            # space_ref="",
            properties=properties,
            app_data=model.AppDataDef(),
        )

class ValueDerivationExtractor(AbstractIdent):
    def __init__(
        self, node: AbstractNodeExtractor, schema: SchemaExtractor, link: LinkExtractor
    ):
        super().__init__()
        self.node = node
        self.schema = schema
        self.link = link
        self.configuration = self.node.stage_node.configuration
        self.inputs = self.node.inputs
        self.outputs = self.node.outputs
        self.value_derivation = []

    def get_node_value_derivation(self):
        valueDerivation = []
        op = self.configuration.op_name
        if len(self.inputs) > 1:
            num_primary = 0
            for input in self.inputs:
                if input.link.link.type == "PRIMARY":
                    num_primary += 1
            if num_primary > 1:
                if len(self.outputs) == 1:
                    for output in self.outputs:
                        if output.schema:
                            for field in output.schema.schema.fields:
                                expression = {
                                    "columnName": field.name,
                                    "parsedExpression": field.name,
                                    "sourceColumn": "",
                                }
                                for input in self.inputs:
                                    if input.schema:
                                        for input_field in input.schema.schema.fields:
                                            if input_field.name == field.name:
                                                expression[
                                                    "sourceColumn"
                                                ] += f"{input.link.get_link_name()}.{input_field.name};"
                                if (
                                    expression["sourceColumn"]
                                    and expression["sourceColumn"][-1] == ";"
                                ):
                                    expression["sourceColumn"] = expression[
                                        "sourceColumn"
                                    ][:-1]
                                valueDerivation.append(expression)
        if op == "PxMerge":
            valueDerivation = []
        if op == "PxSort":
            assert isinstance(self.configuration, sort)
            for input in self.inputs:
                link_name = input.link.get_link_name()
                if self.configuration.flag_key.value == "flagKey":
                    column_name = None
                    for output in self.outputs:
                        for field in output.schema.schema.fields:
                            if (
                                "key_change" in field.app_data
                                and field.app_data["key_change"]
                            ):
                                column_name = field.name
                    if not column_name:
                        column_name = "keyChange"

                    valueDerivation.append(
                        {
                            "columnName": column_name,
                            "parsedExpression": "KeyChange()",
                            "sourceColumn": f"{link_name}.keyChange",
                        }
                    )
                if self.configuration.flag_cluster.value == "flagCluster":
                    column_name = None
                    for output in self.outputs:
                        for field in output.schema.schema.fields:
                            if (
                                "cluster_key_change" in field.app_data
                                and field.app_data["cluster_key_change"]
                            ):
                                column_name = field.name
                    if not column_name:
                        column_name = "clusterKeyChange"

                    valueDerivation.append(
                        {
                            "columnName": column_name,
                            "parsedExpression": "ClusterKeyChange()",
                            "sourceColumn": f"{link_name}.{column_name}",
                        }
                    )
        elif op == "PxPeek":
            assert isinstance(self.configuration, peek)
            link_name = self.link.get_link_name()
            if self.configuration.dataset.value == "dataset":
                valueDerivation.append(
                    {
                        "columnName": "rec",
                        "parsedExpression": "Peek()",
                        "sourceColumn": f"{link_name}.rec",
                    }
                )
        elif op == "PxDifference":
            assert isinstance(self.configuration, difference)
            valueDerivation = []
            for input in self.inputs:
                column_name = None
                for output in self.outputs:
                    for field in output.schema.schema.fields:
                        if (
                            "difference" in field.app_data
                            and field.app_data["difference"]
                        ):
                            column_name = field.name
                if not column_name:
                    column_name = "diff"
                valueDerivation.append(
                    {
                        "columnName": column_name,
                        "parsedExpression": "DiffCode()",
                        "sourceColumn": f"{input.link.get_link_name()}.{column_name}",
                    }
                )
        elif op == "PxChecksum":
            assert isinstance(self.configuration, checksum)
            for input in self.inputs:
                link_name = input.link.get_link_name()
                if self.configuration.checksum_name:
                    valueDerivation.append(
                        {
                            "columnName": self.configuration.checksum_name,
                            "parsedExpression": "Checksum()",
                            "sourceColumn": f"{link_name}.{self.configuration.checksum_name}",
                        }
                    )
                else:
                    valueDerivation.append(
                        {
                            "columnName": "checksum",
                            "parsedExpression": "Checksum()",
                            "sourceColumn": f"{link_name}.checksum",
                        }
                    )
                if self.configuration.export_name:
                    valueDerivation.append(
                        {
                            "columnName": self.configuration.export_name,
                            "parsedExpression": "CRCBuffer()",
                            "sourceColumn": f"{link_name}.{self.configuration.export_name}",
                        }
                    )
        elif op == "PxBLM":
            assert isinstance(self.configuration, bloom_filter)
            link_name = self.link.get_link_name()
            valueDerivation.append(
                {
                    "columnName": "dflag",
                    "parsedExpression": "IsADuplicate()",
                    "sourceColumn": f"{link_name}.dflag",
                }
            )
        elif op == "PxChangeCapture":
            assert isinstance(self.configuration, change_capture)
            valueDerivation = []
            link_name = None
            for input_link in self.configuration.inputlink_ordering_list:
                # TODO change when objects (instead of dict)
                if "link_label" in input_link and (
                    input_link["link_label"] == "1"
                    or input_link["link_label"] == "After"
                ):
                    link_name = input_link["link_name"]
            for input in self.inputs:
                new_link_name = link_name or input.link.get_link_name()
                column_name = self.configuration.code_field or "change_code"
                for output in self.outputs:
                    for field in output.schema.schema.fields:
                        if (
                            "change_code" in field.app_data
                            and field.app_data["change_code"]
                        ):
                            column_name = field.name
                valueDerivation.append(
                    {
                        "columnName": column_name,
                        "parsedExpression": "ChangeCode()",
                        "sourceColumn": f"{new_link_name}.change_code",
                    }
                )
                if not link_name:
                    logger.warning(
                        "\nProper input ordering has not been set for Change Capture stage. Input ordering will be randomly assigned.",
                    )
                break
        elif op == "PxChangeApply":
            assert isinstance(self.configuration, change_apply)
            link_name = None
            input_link1 = None
            input_link2 = None
            if len(self.configuration.inputlink_ordering_list) > 1:
                if "link_name" in self.configuration.inputlink_ordering_list[0]:
                    input_link1 = self.configuration.inputlink_ordering_list[0][
                        "link_name"
                    ]
                if "link_name" in self.configuration.inputlink_ordering_list[1]:
                    input_link2 = self.configuration.inputlink_ordering_list[1][
                        "link_name"
                    ]
                for input_link in self.configuration.inputlink_ordering_list:
                    if (
                        "link_label" in input_link
                        and input_link["link_label"] == "Change"
                    ):
                        if "link_name" in input_link:
                            link_name = input_link["link_name"]
            change_schema = None
            for input_node in self.inputs:
                if input_node.link.get_link_name() == link_name:
                    change_schema = input_node.schema.schema
            change_code_column_name = self.configuration.code_field or "change_code"
            if change_schema and len(change_schema.fields) != 0:
                for field in change_schema.fields:
                    column_name = field.name
                    if column_name and column_name != change_code_column_name:
                        valueDerivation.append(
                            {
                                "columnName": column_name,
                                "parsedExpression": f"{link_name}.{column_name}",
                                "sourceColumn": f"{input_link1}.{column_name};{input_link2}.{column_name}",
                            }
                        )
        elif op == "PxCompare":
            assert isinstance(self.configuration, compare)
            valueDerivation = []
            # valueDerivation.append(
            #     {"columnName": "first", "parsedExpression": "-", "sourceColumn": "-"}
            # )
            # valueDerivation.append(
            #     {"columnName": "second", "parsedExpression": "-", "sourceColumn": "-"}
            # )
            # valueDerivation.append(
            #     {"columnName": "result", "parsedExpression": "-", "sourceColumn": "-"}
            # )
        elif op == "MatchFrequency":
            assert isinstance(self.configuration, match_frequency)
            mf_columns = [
                "qsFreqValue",
                "qsFreqCounts",
                "qsFreqColumnID",
                "qsFreqHeaderFlag",
            ]
            for input in self.inputs:
                link_name = input.link.get_link_name()
                for derivation in mf_columns:
                    valueDerivation.append(
                        {
                            "columnName": derivation,
                            "parsedExpression": f"MatchFrequency({derivation})",
                            "sourceColumn": f"{link_name}.{derivation}",
                        }
                    )
        elif op == "UnduplicateMatch":
            mf_columns = [
                "qsMatchType",
                "qsMatchWeight",
                "qsMatchPattern",
                "qsMatchLRFlag",
                "qsMatchExactFlag",
                "qsMatchPassNumber",
                "qsMatchSetID",
                "qsMatchDataID",
                "qsMatchStatType",
                "qsMatchStatValue",
            ]
            for input in self.inputs:
                link_name = input.link.get_link_name()
                for derivation in mf_columns:
                    valueDerivation.append(
                        {
                            "columnName": derivation,
                            "parsedExpression": f"UnduplicateMatch({derivation})",
                            "sourceColumn": f"{link_name}.{derivation}",
                        }
                    )
        elif op == "ReferenceMatch":
            mf_columns = [
                "qsMatchRefID",
                "qsMatchType",
                "qsMatchWeight",
                "qsMatchPattern",
                "qsMatchLRFlag",
                "qsMatchExactFlag",
                "qsMatchPassNumber",
                "qsMatchSetID",
                "qsMatchDataID",
                "qsMatchStatType",
                "qsMatchStatValue",
            ]
            for input in self.inputs:
                link_name = input.link.get_link_name()
                for derivation in mf_columns:
                    valueDerivation.append(
                        {
                            "columnName": derivation,
                            "parsedExpression": f"ReferenceMatch({derivation})",
                            "sourceColumn": f"{link_name}.{derivation}",
                        }
                    )
        elif op in [
            "QSmwi",
        ]:
            pass
        elif op == "AddressVerification2":
            assert isinstance(self.configuration, address_verification)
            column_data = {
                "AccuracyCode_QSAV": "AccuracyCode",
                "AddressQualityIndex_QSAV": "AddressQualityIndex",
                "Organization_QSAV": "Organization",
                "Department_QSAV": "Department",
                "Function_QSAV": "Function",
                "Contact_QSAV": "Contact",
                "Building_QSAV": "Building",
                "Subbuilding_QSAV": "Subbuilding",
                "HouseNumber_QSAV": "HouseNumber",
                "Street_QSAV": "Street",
                "DependentStreet_QSAV": "DependentStreet",
                "POBOX_QSAV": "POBOX",
                "Locality_QSAV": "Locality",
                "DependentLocality_QSAV": "DependentLocality",
                "DoubleDependentLocality_QSAV": "DoubleDependentLocality",
                "PostCode_QSAV": "PostCode",
                "PostalCodePrimary_QSAV": "PostalCodePrimary",
                "PostalCodeSecondary_QSAV": "PostalCodeSecondary",
                "SuperAdministrativeArea_QSAV": "SuperAdministrativeArea",
                "AdministrativeArea_QSAV": "AdministrativeArea",
                "SubAdministrativeArea_QSAV": "SubAdministrativeArea",
                "Country_QSAV": "Country",
                "ISO3166_2_QSAV": "ISO3166",
                "ISO3166_3_QSAV": "ISO3166",
                "ISO3166_N_QSAV": "ISO3166",
                "Address_QSAV": "Address",
                "Residue_QSAV": "Residue",
                "DeliveryAddress1_QSAV": "DeliveryAddress1",
                "DeliveryAddress2_QSAV": "DeliveryAddress2",
                "DeliveryAddress3_QSAV": "DeliveryAddress3",
                "DeliveryAddress4_QSAV": "DeliveryAddress4",
                "DeliveryAddress5_QSAV": "DeliveryAddress5",
                "DeliveryAddress6_QSAV": "DeliveryAddress6",
                "DeliveryAddress7_QSAV": "DeliveryAddress7",
                "DeliveryAddress8_QSAV": "DeliveryAddress8",
                "FormattedAddress1_QSAV": "FormattedAddress1",
                "FormattedAddress2_QSAV": "FormattedAddress2",
                "FormattedAddress3_QSAV": "FormattedAddress3",
                "FormattedAddress4_QSAV": "FormattedAddress4",
                "FormattedAddress5_QSAV": "FormattedAddress5",
                "FormattedAddress6_QSAV": "FormattedAddress6",
                "FormattedAddress7_QSAV": "FormattedAddress7",
                "FormattedAddress8_QSAV": "FormattedAddress8",
                "FormattedAddress9_QSAV": "FormattedAddress9",
                "FormattedAddress10_QSAV": "FormattedAddress10",
                "AddressFormat_QSAV": "AddressFormat",
                "DeliveryAddress_QSAV": "DeliveryAddress",
                "DeliveryAddressFormat_QSAV": "DeliveryAddressFormat",
                "LocalityExtra_QSAV": "LocalityExtra",
                "LocalitySpecial_QSAV": "LocalitySpecial",
                "PremiseExtra_QSAV": "PremiseExtra",
                "ErrorCode_QSAV": "ErrorCode",
                "ErrorMessage_QSAV": "ErrorMessage",
            }
            for field in self.schema.schema.fields:
                if field.name in column_data:
                    valueDerivation.append(
                        {
                            "columnName": field.name,
                            "parsedExpression": column_data[field.name],
                            "sourceColumn": f".{field.name}",
                        }
                    )

        elif op == "PxFunnel":
            valueDerivation = []
            assert isinstance(self.configuration, funnel)
            output_col = []
            result = []
            for output_node in self.outputs:
                if output_node.schema:
                    output_col.append(output_node.schema.schema.fields)
            if len(output_col) > 0:
                result = output_col.pop(0)
                result = [
                    v
                    for v in result
                    if all(any(x.name == v.name for x in a) for a in output_col)
                ]
            # if result:
            #     for col in result:
            #         source_column = ""
            #         for input_node in self.inputs:
            #             if input_node.link.get_link_name():
            #                 append_str = ";"
            #                 if source_column != "":
            #                     source_column += (
            #                         append_str
            #                         + f"{input_node.link.get_link_name()}.{col.name}"
            #                     )
            #                 else:
            #                     source_column = (
            #                         f"{input_node.link.get_link_name()}.{col.name}"
            #                     )
            #         valueDerivation.append(
            #             {
            #                 "columnName": col.name,
            #                 "parsedExpression": col.name,
            #                 "sourceColumn": source_column,
            #             }
            #         )
            for output_node in self.outputs:
                if not output_node.schema:
                    continue
                for field in output_node.schema.schema.fields:
                    # result_names = [res.name for res in result]
                    # if field.name not in result_names:
                    source_column = ""
                    parsed_expression = field.metadata.source_field_id or field.name
                    field.metadata.source_field_id = None
                    for input_node in self.inputs:
                        if input_node.link.get_link_name():
                            append_str = ";"
                            if source_column != "":
                                source_column += (
                                    append_str
                                    + f"{input_node.link.get_link_name()}.{parsed_expression}"
                                )
                            else:
                                source_column = f"{input_node.link.get_link_name()}.{parsed_expression}"

                    valueDerivation.append(
                        {
                            "columnName": field.name,
                            "parsedExpression": parsed_expression,
                            "sourceColumn": source_column,
                        }
                    )
        elif op == "PxAggregator":
            assert isinstance(self.configuration, aggregator)
            selection = self.configuration.selection.value
            operations = {
                "sum": "Sum",
                "min": "Min",
                "max": "Max",
                "css": "CorrectedSumSquares",
                "mean": "Mean",
                "missing": "MissingValCount",
                "count": "Count",
                "cv": "PctCoeffVar",
                "range": "Range",
                "std": "StandardDeviation",
                "ste": "StandardError",
                "sumw": "SumWeights",
                "uss": "UncorrectedSumSquares",
                "var": "Variance",
            }
            if len(self.configuration.reduce_properties) > 0:
                for input in self.inputs:
                    for reduce_props in self.configuration.reduce_properties:
                        selected_column = None
                        for reduce_prop in reduce_props:
                            if selection in reduce_prop:
                                selected_column = reduce_prop[selection]
                        for reduce_prop in reduce_props:
                            summary_operations = {
                                "n": "SummaryNumRecs",
                                "nMissing": "SummaryNumMissingVals",
                                "sumOfWeights": "SummarySumWeights",
                                "minimum": "SummaryMinimum",
                                "maximum": "SummaryMaximum",
                                "mean": "SummaryMean",
                                "css": "SummarySumSquares",
                            }
                            for agg_op in operations:
                                if agg_op in reduce_prop:
                                    column_name = None
                                    for output in self.outputs:
                                        for field in output.schema.schema.fields:
                                            if field.name == reduce_prop[agg_op]:
                                                column_name = reduce_prop[agg_op]
                                    if not column_name:
                                        column_name = selected_column
                                    valueDerivation.append(
                                        {
                                            "columnName": column_name,
                                            "parsedExpression": f"{operations[agg_op]}({input.link.get_link_name()}.{selected_column})",
                                            "sourceColumn": f"{input.link.get_link_name()}.{selected_column}",
                                        }
                                    )
                            if "summary" in reduce_prop:
                                column_name = None
                                for output in self.outputs:
                                    for field in output.schema.schema.fields:
                                        if field.name == reduce_prop["summary"]:
                                            column_name = reduce_prop["summary"]
                                if not column_name:
                                    column_name = selected_column
                                valueDerivation.append(
                                    {
                                        "columnName": column_name,
                                        "parsedExpression": f"Summary({input.link.get_link_name()}.{selected_column})",
                                        "sourceColumn": f"{input.link.get_link_name()}.{selected_column}",
                                    }
                                )
                                for suffix, operation in summary_operations.items():
                                    valueDerivation.append(
                                        {
                                            "columnName": f"{column_name}.{suffix}",
                                            "parsedExpression": f"{operation}({input.link.get_link_name()}.{selected_column})",
                                            "sourceColumn": f"{input.link.get_link_name()}.{selected_column}",
                                        }
                                    )

            if len(self.configuration.rereduce_properties) > 0:
                for input in self.inputs:
                    for rereduce_props in self.configuration.rereduce_properties:
                        selected_column = None
                        for rereduce_prop in rereduce_props:
                            if selection in rereduce_prop:
                                selected_column = rereduce_prop[selection]
                        for rereduce_prop in rereduce_props:
                            for agg_op in operations:
                                if agg_op in rereduce_prop:
                                    column_name = None
                                    for output in self.outputs:
                                        for field in output.schema.schema.fields:
                                            if field.name == rereduce_prop[agg_op]:
                                                column_name = rereduce_prop[agg_op]
                                    if not column_name:
                                        column_name = selected_column
                                    valueDerivation.append(
                                        {
                                            "columnName": column_name,
                                            "parsedExpression": f"{operations[agg_op]}({input.link.get_link_name()}.{selected_column})",
                                            "sourceColumn": f"{input.link.get_link_name()}.{selected_column}",
                                        }
                                    )

            if len(self.configuration.count_field_properties) > 0:
                for input in self.inputs:
                    for count_fields in self.configuration.count_field_properties:
                        for count_field in count_fields:
                            if "countField" in count_field:
                                valueDerivation.append(
                                    {
                                        "columnName": count_field["countField"],
                                        "parsedExpression": "RecCount()",
                                        "sourceColumn": f"{input.link.get_link_name()}.{count_field['countField']}",
                                    }
                                )
        elif op == "PxColumnImport":
            assert isinstance(self.configuration, column_import)
            input_link = None
            if self.configuration.field:
                for input_node in self.inputs:
                    for field in input_node.schema.schema.fields:
                        if field.name == self.configuration.field:
                            input_link = input_node.link.link.name
                            break

                if self.link.link.type == "PRIMARY":
                    for field in self.schema.schema.fields:
                        for col_schema in self.configuration.schema_:
                            if (
                                "ColumnName" in col_schema
                                and col_schema["ColumnName"] == field.name
                            ):
                                valueDerivation.append(
                                    {
                                        "columnName": field.name,
                                        "parsedExpression": f"ColumnImport({input_link}.{self.configuration.field},{field.name})",
                                        "sourceColumn": f"{input_link}.{self.configuration.field}",
                                    }
                                )
        elif op == "PxColumnExport":
            assert isinstance(self.configuration, column_export)
            input_columns = []
            export_columns = self.configuration.schema_
            if self.configuration.field and export_columns:
                for input_node in self.inputs:
                    for field in input_node.schema.schema.fields:
                        if field.name in export_columns:
                            input_columns.append(
                                f"{input_node.link.get_link_name()}.{field.name}"
                            )
            valueDerivation.append(
                {
                    "columnName": self.configuration.field,
                    "parsedExpression": f"ColumnExport({','.join(input_columns)},{self.configuration.field})",
                    "sourceColumn": ";".join(input_columns),
                }
            )
        elif op == "PxColumnGenerator":
            assert isinstance(self.configuration, column_generator)
            input_link = None
            if len(self.configuration.schema_) > 0:
                for schema in self.configuration.schema_:
                    for input in self.inputs:
                        valueDerivation.append(
                            {
                                "columnName": schema,
                                "parsedExpression": f"Generate({schema})",
                                "sourceColumn": f"{input.link.get_link_name()}.{schema}",
                            }
                        )
        elif op == "PxPivot":
            assert isinstance(self.configuration, pivot)
            if (
                hasattr(self.configuration.pivot_type, "value")
                and self.configuration.pivot_type.value == "verticalpivot"
            ) or self.configuration.pivot_type == "verticalpivot":
                for input in self.inputs:
                    for output in self.outputs:
                        for field in output.schema.schema.fields:
                            valueDerivation.append(
                                {
                                    "columnName": field.name,
                                    "parsedExpression": f"VerticalPivot({field.name})",
                                    "sourceColumn": f"{input.link.get_link_name()}.{field.name}",
                                }
                            )
            elif self.configuration.pivot_properties:
                for input in self.inputs:
                    for output in self.outputs:
                        for field in output.schema.schema.fields:
                            for pivot_prop in self.configuration.pivot_properties:
                                if "name" in pivot_prop:
                                    if pivot_prop["name"] == field.name or (
                                        "pivot_property" in field.app_data
                                        and field.app_data["pivot_property"]
                                        == pivot_prop["name"]
                                    ):
                                        valueDerivation.append(
                                            {
                                                "columnName": field.name,
                                                "parsedExpression": f"Pivot({pivot_prop['name']})",
                                                "sourceColumn": f"{input.link.get_link_name()}.{field.name}",
                                            }
                                        )
        elif op == "Standardize":
            assert isinstance(self.configuration, standardize)
            ruleset = self.configuration.ruleset_properties
            for output in self.outputs:
                for field in output.schema.schema.fields:
                    for rule in ruleset:
                        if "ruleset" in rule and field.name.endswith(rule["ruleset"]):
                            for input in self.inputs:
                                valueDerivation.append(
                                    {
                                        "columnName": field.name,
                                        "parsedExpression": f"Standardize({field.name})",
                                        "sourceColumn": f"{input.link.get_link_name()}.{field.name}",
                                    }
                                )
        elif op == "Investigate":
            investigate_names = [
                "qsInvColumnName",
                "qsInvPattern",
                "qsInvSample",
                "qsInvCount",
                "qsInvPercent",
                "qsInvWord",
                "qsInvClassCode",
            ]
            for output in self.outputs:
                for field in output.schema.schema.fields:
                    if field.name in investigate_names:
                        for input in self.inputs:
                            valueDerivation.append(
                                {
                                    "columnName": field.name,
                                    "parsedExpression": f"Investigate({field.name})",
                                    "sourceColumn": f"{input.link.get_link_name()}.{field.name}",
                                }
                            )
        elif op == "XMLStagePX" or op == "PxJoin":
            valueDerivation = []
        elif op == "CTransformerStage":
            assert isinstance(self.configuration, transformer)
            if self.link.link.schema.configuration:
                for field in self.link.link.schema.configuration.fields:
                    if "derivation" in field.app_data:
                        source_column = field.metadata.source_field_id
                        if not source_column:
                            found_field = None
                            num_found = 0
                            for input in self.inputs:
                                if input.schema:
                                    for input_field in input.schema.schema.fields:
                                        if input_field.name == field.name:
                                            found_field = f"{input.link.get_link_name()}.{input_field.name}"
                                            num_found += 1
                            if num_found == 1:
                                source_column = found_field
                        elif "." not in source_column:
                            found_field = None
                            num_found = 0
                            for input in self.inputs:
                                if input.schema:
                                    for input_field in input.schema.schema.fields:
                                        if input_field.name == source_column:
                                            found_field = f"{input.link.get_link_name()}.{input_field.name}"
                                            num_found += 1
                            if num_found == 1:
                                source_column = found_field

                        if source_column:
                            valueDerivation.append(
                                {
                                    "columnName": field.name,
                                    "parsedExpression": field.app_data["derivation"],
                                    "sourceColumn": source_column,
                                }
                            )
                        else:
                            valueDerivation.append(
                                {
                                    "columnName": field.name,
                                    "parsedExpression": field.app_data["derivation"],
                                }
                            )

        self.value_derivation.extend(valueDerivation)

        if self.schema:
            for field in self.schema.schema.fields:
                found = False
                for vd in self.value_derivation:
                    if "columnName" in vd and vd["columnName"] == field.name:
                        found = True
                if not found:
                    if not field.metadata.source_field_id:
                        num_found = 0
                        link_name = None
                        for input_node in self.inputs:
                            if input_node.schema:
                                for input_field in input_node.schema.schema.fields:
                                    if field.name == input_field.name:
                                        num_found += 1
                                        link_name = input_node.link.get_link_name()
                        if num_found == 1:
                            field.metadata.source_field_id = f"{link_name}.{field.name}"
                    elif "." not in field.metadata.source_field_id:
                        num_found = 0
                        link_name = None
                        for input_node in self.inputs:
                            if input_node.schema:
                                for input_field in input_node.schema.schema.fields:
                                    if (
                                        field.metadata.source_field_id
                                        == input_field.name
                                    ):
                                        num_found += 1
                                        link_name = input_node.link.get_link_name()
                        if num_found == 1:
                            field.metadata.source_field_id = (
                                f"{link_name}.{field.metadata.source_field_id}"
                            )

    def get_link_value_derivation(self):
        pass

    def serialize(self):
        self.get_node_value_derivation()
        return self.value_derivation


class OutputPortExtractor(AbstractIdent):
    """Extracts an output port for a node."""

    def __init__(
        self,
        parent_pipe: PipelineExtractor,
        link: LinkExtractor,
        node: AbstractNodeExtractor,
        schema: SchemaExtractor | None,
    ):
        super().__init__()
        self.parent_pipe = parent_pipe
        self.link = link
        self.node_ext = node
        self.schema = schema

    def serialize(self):
        """Serializes the output port into a model.Port object."""
        cardinality = (
            self.node_ext.stage_node.configuration.get_output_cardinality()
        )

        app_data = model.PortAppData(
            ui_data=model.PortUI(
                label="outPort",
                cardinality=cardinality,
            ),
        )
        app_data.datastage = {"is_source_of_link": self.link.id}

        value_derivation = None
        if isinstance(self.node_ext.stage_node, StageNode):
            app_data.ui_data = model.PortUI(
                label="outPort",
                cardinality=self.node_ext.stage_node.configuration.get_output_cardinality(),
            )
            vd_extractor = ValueDerivationExtractor(
                self.node_ext, self.schema, self.link
            )
            value_derivation = vd_extractor.serialize()

        if (
            self.node_ext.stage_node._get_node_label() != None
            and "Java_Integration" in self.node_ext.stage_node._get_node_label()
        ):
            parameters = self.node_ext.get_output_port_params(self.link.get_link_name())
        else:
            parameters = self.node_ext.get_output_port_params()

        if value_derivation:
            parameters["valueDerivation"] = value_derivation

        if (
            hasattr(self.node_ext.stage_node, "configuration")
            and self.node_ext.stage_node.configuration.op_name == "PxSequentialFile"
            and self.link.link.type == "REJECT"
        ):
            parameters["is_reject_output"] = True

        if (
            hasattr(self.node_ext.stage_node, "configuration")
            and self.node_ext.stage_node.configuration.op_name == "CTransformerStage"
        ):
            if "TransformerConstraint" in parameters:
                update = {}
                for constraint in parameters["TransformerConstraint"]:
                    if (
                        "output_name" in constraint
                        and constraint["output_name"] == self.link.get_link_name()
                    ):
                        update["TransformerConstraint"] = (
                            constraint["TransformerConstraint"]
                            if "TransformerConstraint" in constraint
                            else None
                        )
                        update["Reject"] = (
                            constraint["Reject"] if "Reject" in constraint else None
                        )
                        update["RowLimit"] = (
                            constraint["RowLimit"] if "RowLimit" in constraint else None
                        )
                del parameters["TransformerConstraint"]
                parameters.update(update)
        if (
            hasattr(self.node_ext.stage_node, "configuration")
            and self.node_ext.stage_node.configuration.op_name == "PxCFF"
        ):
            if "predicate" in parameters:
                predicate = None
                for constraint in parameters["predicate"]:
                    if (
                        "output_name" in constraint
                        and constraint["output_name"] == self.link.get_link_name()
                    ):
                        predicate = (
                            constraint["constraint"]
                            if "constraint" in constraint
                            else None
                        )
                if predicate:
                    parameters["predicate"] = predicate
                else:
                    del parameters["predicate"]

        if (
            self.node_ext.stage_node.metadata["in_degree"] > 0
            and self.node_ext.stage_node.metadata["out_degree"] > 0
        ):
            app_data.additionalProperties = {
                "enableAcp": self.node_ext.stage_node._get_acp()
            }

            return model.Port(
                id=self.id,
                parameters=parameters,
                schema_ref=self.schema.id if self.schema else None,
                app_data=app_data,
            )
        else:
            return model.Port(
                id=self.id,
                parameters=parameters,
                schema_ref=self.schema.id if self.schema else None,
                app_data=app_data,
            )


class PlainOutputPortExtractor:
    def __init__(self, node: AbstractNodeExtractor):
        self.node = node

    def serialize(self):
        return model.Port(
            id="",
            app_data=model.PortAppData(
                ui_data=model.PortUI(
                    label="outPort",
                    cardinality=model.Cardinality(
                        min=self.node.stage_node._get_min_primary_outputs(),
                        max=self.node.stage_node._get_max_primary_outputs(),
                    ),
                )
            ),
        )

class InputPortExtractor(AbstractIdent):
    """Extracts an input port for a node."""

    def __init__(
        self,
        parent_pipe: PipelineExtractor,
        link: LinkExtractor,
        node: AbstractNodeExtractor,
        schema: SchemaExtractor = None,
    ):
        super().__init__()
        self.parent_pipe = parent_pipe
        self.link = link
        self.node = node
        self.schema = schema

    def serialize(self):
        """Serializes the input port into a model.Port object."""
        if (
            self.node.stage_node._get_node_label() != None
            and "Java_Integration" in self.node.stage_node._get_node_label()
        ):
            parameters = self.node.get_input_port_params(self.link.get_link_name())
        else:
            parameters = self.node.get_input_port_params()
        if (
            hasattr(self.node.node, "configuration")
            and self.node.node.configuration.op_name == "PxLookup"
        ):
            if "lookupDerivation" in parameters:
                lookup_derivation = []
                primary_link = None
                for link in self.node.inputs:
                    if link.link.link.type == "PRIMARY":
                        primary_link = link.link.get_link_name()
                for ld_props in parameters["lookupDerivation"]:
                    if self.link.get_link_name() == ld_props["reference_link"]:
                        for derivation in ld_props["derivations"]:
                            key_expression = (
                                derivation["key_expression"]
                                if "key_expression" in derivation
                                else ""
                            )
                            parsed_expression = None
                            if "key_expression" in derivation:
                                if "Range" in derivation["key_expression"]:
                                    parsed_expression = derivation["key_expression"]
                                else:
                                    parsed_expression = (
                                        f"{primary_link}.{key_expression}"
                                    )
                            lookup_derivation.append(
                                {
                                    "parsedExpression": parsed_expression,
                                    "sourceColumn": f"{primary_link}.{key_expression}",
                                    "keyType": derivation["key_type"],
                                    "columnName": derivation["key_column"],
                                }
                            )
                        if "conditionNotMet" in ld_props:
                            parameters["conditionNotMet"] = ld_props["conditionNotMet"]
                        if "Condition" in ld_props:
                            parameters["Condition"] = ld_props["Condition"]
                        if "lookupFail" in ld_props:
                            parameters["lookupFail"] = ld_props["lookupFail"]

                if lookup_derivation:
                    parameters["lookupDerivation"] = lookup_derivation
                else:
                    del parameters["lookupDerivation"]

        if hasattr(self.link.link.src, "configuration") and hasattr(
            self.link.link.src.configuration, "runtime_column_propagation"
        ):
            if (
                hasattr(self.node.node, "configuration")
                and self.node.node.configuration.op_name == "WSTransformerPX"
            ):
                parameters["runtime_column_propagation"] = int(
                    self.link.link.src.configuration.runtime_column_propagation
                )
            else:
                parameters["runtime_column_propagation"] = bool(
                    self.link.link.src.configuration.runtime_column_propagation
                )
        elif hasattr(self.link.link.src, "rcp"):
            parameters["runtime_column_propagation"] = self.link.link.src.rcp

        return model.Port(
            id=self.id,
            schema_ref=self.schema.id if self.schema else None,
            parameters=parameters,
            links=[self.link.serialize()],
            app_data=model.PortAppData(ui_data=model.PortUI(label="")),
        )
