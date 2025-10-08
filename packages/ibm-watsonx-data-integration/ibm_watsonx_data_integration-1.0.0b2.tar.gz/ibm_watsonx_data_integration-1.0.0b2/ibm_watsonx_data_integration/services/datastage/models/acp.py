import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as model
from ibm_watsonx_data_integration.services.datastage.models.flow.dag import Link, StageNode
from ibm_watsonx_data_integration.services.datastage.models.stage_models.address_verification import (
    address_verification,
)
from ibm_watsonx_data_integration.services.datastage.models.stage_models.aggregator import aggregator
from ibm_watsonx_data_integration.services.datastage.models.stage_models.bloom_filter import bloom_filter
from ibm_watsonx_data_integration.services.datastage.models.stage_models.change_apply import change_apply
from ibm_watsonx_data_integration.services.datastage.models.stage_models.change_capture import change_capture
from ibm_watsonx_data_integration.services.datastage.models.stage_models.checksum import checksum
from ibm_watsonx_data_integration.services.datastage.models.stage_models.column_export import column_export
from ibm_watsonx_data_integration.services.datastage.models.stage_models.column_generator import column_generator
from ibm_watsonx_data_integration.services.datastage.models.stage_models.column_import import column_import
from ibm_watsonx_data_integration.services.datastage.models.stage_models.combine_records import combine_records
from ibm_watsonx_data_integration.services.datastage.models.stage_models.compare import compare
from ibm_watsonx_data_integration.services.datastage.models.stage_models.complex_flat_file import complex_flat_file
from ibm_watsonx_data_integration.services.datastage.models.stage_models.compress import compress
from ibm_watsonx_data_integration.services.datastage.models.stage_models.copy import copy
from ibm_watsonx_data_integration.services.datastage.models.stage_models.data_rules import data_rules
from ibm_watsonx_data_integration.services.datastage.models.stage_models.decode import decode
from ibm_watsonx_data_integration.services.datastage.models.stage_models.difference import difference
from ibm_watsonx_data_integration.services.datastage.models.stage_models.encode import encode
from ibm_watsonx_data_integration.services.datastage.models.stage_models.expand import expand
from ibm_watsonx_data_integration.services.datastage.models.stage_models.external_filter import external_filter
from ibm_watsonx_data_integration.services.datastage.models.stage_models.external_target import external_target
from ibm_watsonx_data_integration.services.datastage.models.stage_models.filter import filter
from ibm_watsonx_data_integration.services.datastage.models.stage_models.funnel import funnel
from ibm_watsonx_data_integration.services.datastage.models.stage_models.generic import generic
from ibm_watsonx_data_integration.services.datastage.models.stage_models.head import head
from ibm_watsonx_data_integration.services.datastage.models.stage_models.investigate import investigate
from ibm_watsonx_data_integration.services.datastage.models.stage_models.java_integration import java_integration
from ibm_watsonx_data_integration.services.datastage.models.stage_models.join import join
from ibm_watsonx_data_integration.services.datastage.models.stage_models.lookup import lookup
from ibm_watsonx_data_integration.services.datastage.models.stage_models.make_subrecord import make_subrecord
from ibm_watsonx_data_integration.services.datastage.models.stage_models.make_vector import make_vector
from ibm_watsonx_data_integration.services.datastage.models.stage_models.match_frequency import match_frequency
from ibm_watsonx_data_integration.services.datastage.models.stage_models.merge import merge
from ibm_watsonx_data_integration.services.datastage.models.stage_models.modify import modify
from ibm_watsonx_data_integration.services.datastage.models.stage_models.pivot import pivot
from ibm_watsonx_data_integration.services.datastage.models.stage_models.promote_subrecord import promote_subrecord
from ibm_watsonx_data_integration.services.datastage.models.stage_models.remove_duplicates import remove_duplicates
from ibm_watsonx_data_integration.services.datastage.models.stage_models.rest import rest
from ibm_watsonx_data_integration.services.datastage.models.stage_models.sample import sample
from ibm_watsonx_data_integration.services.datastage.models.stage_models.sort import sort
from ibm_watsonx_data_integration.services.datastage.models.stage_models.split_subrecord import split_subrecord
from ibm_watsonx_data_integration.services.datastage.models.stage_models.split_vector import split_vector
from ibm_watsonx_data_integration.services.datastage.models.stage_models.standardize import standardize
from ibm_watsonx_data_integration.services.datastage.models.stage_models.surrogate_key_generator import (
    surrogate_key_generator,
)
from ibm_watsonx_data_integration.services.datastage.models.stage_models.survive import survive
from ibm_watsonx_data_integration.services.datastage.models.stage_models.switch import switch
from ibm_watsonx_data_integration.services.datastage.models.stage_models.tail import tail
from ibm_watsonx_data_integration.services.datastage.models.stage_models.transformer import transformer
from ibm_watsonx_data_integration.services.datastage.models.stage_models.wave_generator import wave_generator
from ibm_watsonx_data_integration.services.datastage.models.stages.sequentialfile import sequentialfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.services.datastage.models.extractor import (
        AbstractNodeExtractor,
        InputPortExtractor,
    )

import logging
logger = logging.getLogger(__name__)

class ACP:
    def __init__(
        self,
        link: Link,
        src_input_nodes: list["InputPortExtractor"],
        src_ext: "AbstractNodeExtractor",
        dest_ext: "AbstractNodeExtractor",
    ):
        self.link = link
        self.src_input_nodes = src_input_nodes
        self.src_ext = src_ext
        self.dest_ext = dest_ext
        self.type_data = {
            "BIGINT": {"type_code": "INT64", "type": "integer"},
            "BINARY": {"type_code": "BINARY", "type": "binary"},
            "BIT": {"type_code": "BOOLEAN", "type": "boolean"},
            "CHAR": {"type_code": "STRING", "type": "string"},
            "DATE": {"type_code": "DATE", "type": "date"},
            "DECIMAL": {"type_code": "DECIMAL", "type": "double"},
            "DOUBLE": {"type_code": "DFLOAT", "type": "double"},
            "FLOAT": {"type_code": "SFLOAT", "type": "double"},
            "INTEGER": {"type_code": "INT32", "type": "integer"},
            "LONGVARBINARY": {"type_code": "BINARY", "type": "binary"},
            "LONGVARCHAR": {"type_code": "STRING", "type": "string"},
            "NUMERIC": {"type_code": "DECIMAL", "type": "double"},
            "REAL": {"type_code": "SFLOAT", "type": "double"},
            "SMALLINT": {"type_code": "INT16", "type": "integer"},
            "TIME": {"type_code": "TIME", "type": "time"},
            "TIMESTAMP": {"type_code": "DATETIME", "type": "timestamp"},
            "TINYINT": {"type_code": "INT8", "type": "integer"},
            "UNKNOWN": {"type_code": "UNKNOWN", "type": "string"},
            "VARBINARY": {"type_code": "BINARY", "type": "binary"},
            "VARCHAR": {"type_code": "STRING", "type": "string"},
            "WCHAR": {"type_code": "STRING", "type": "string"},
            "WLONGVARCHAR": {"type_code": "STRING", "type": "string"},
        }

    def compute_schema(self):
        if hasattr(self.src_ext, "node"):
            if isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, compare):
                return self.compute_compare()
            if isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, funnel):
                return self.compute_funnel()
            if isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, join):
                return self.compute_join()
            if isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, lookup):
                return self.compute_lookup()
            if isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, merge):
                return self.compute_merge()
            if isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, pivot):
                return self.compute_pivot()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, aggregator
            ):
                return self.compute_aggregator()
            if isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, checksum):
                return self.compute_checksum()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, column_export
            ):
                return self.compute_column_export()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, column_generator
            ):
                return self.compute_column_generator()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, column_import
            ):
                return self.compute_column_import()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, combine_records
            ):
                return self.compute_combine_records()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, difference
            ):
                return self.compute_difference()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, make_subrecord
            ):
                return self.compute_make_subrecord()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, make_vector
            ):
                return self.compute_make_vector()
            if isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, sort):
                return self.compute_sort()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, surrogate_key_generator
            ):
                return self.compute_surrogate_key_generator()
            if isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, generic):
                return self.compute_generic()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, change_capture
            ):
                return self.compute_change_capture()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, change_apply
            ):
                return self.compute_change_apply()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, address_verification
            ):
                return self.compute_address_verification()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, complex_flat_file
            ):
                return self.compute_complex_flat_file()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, investigate
            ):
                return self.compute_investigate()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, match_frequency
            ):
                return self.compute_match_frequency()
            if isinstance(self.src_ext.node, StageNode) and isinstance(
                self.src_ext.node.configuration, standardize
            ):
                return self.compute_standardize()
            # if isinstance(self.src_ext.node, StageNode) and isinstance(
            #     self.src_ext.node.configuration, build_stage
            # ):
            #     return self.compute_build_stage()
            # if isinstance(self.src_ext.node, StageNode) and isinstance(
            #     self.src_ext.node.configuration, wrapped_stage
            # ):
            #     return self.compute_wrapped_stage()
            # if isinstance(self.src_ext.node, StageNode) and isinstance(
            #     self.src_ext.node.configuration, custom_stage
            # ):
            #     return self.compute_custom_stage()
            # if isinstance(self.src_ext.node, SuperNode):
            #     return self.compute_subflow()

            if isinstance(self.src_ext.node, StageNode) and (
                isinstance(self.src_ext.node.configuration, bloom_filter)
                or isinstance(self.src_ext.node.configuration, compress)
                or isinstance(self.src_ext.node.configuration, copy)
                or isinstance(self.src_ext.node.configuration, decode)
                or isinstance(self.src_ext.node.configuration, encode)
                or isinstance(self.src_ext.node.configuration, expand)
                or isinstance(self.src_ext.node.configuration, external_filter)
                or isinstance(self.src_ext.node.configuration, external_target)
                or isinstance(self.src_ext.node.configuration, filter)
                or isinstance(self.src_ext.node.configuration, head)
                or isinstance(self.src_ext.node.configuration, java_integration)
                or isinstance(self.src_ext.node.configuration, modify)
                or isinstance(self.src_ext.node.configuration, promote_subrecord)
                or isinstance(self.src_ext.node.configuration, remove_duplicates)
                or isinstance(self.src_ext.node.configuration, sample)
                or isinstance(self.src_ext.node.configuration, split_subrecord)
                or isinstance(self.src_ext.node.configuration, split_vector)
                or isinstance(self.src_ext.node.configuration, switch)
                or isinstance(self.src_ext.node.configuration, tail)
                or isinstance(self.src_ext.node.configuration, transformer)
                or isinstance(self.src_ext.node.configuration, wave_generator)
                or isinstance(self.src_ext.node.configuration, sequentialfile)
                or isinstance(self.src_ext.node.configuration, data_rules)
                or isinstance(self.src_ext.node.configuration, survive)
                or hasattr(self.src_ext.node.configuration, "connection")
            ):
                return self.compute_general()
            if isinstance(self.src_ext.node, StageNode) and (isinstance(self.src_ext.node.configuration, rest)):
                return model.RecordSchema(id="", fields=[])

    def compute_aggregator(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, aggregator)
        key_properties = self.src_ext.node.configuration.key_properties
        if (
            hasattr(self.src_ext.node.configuration.selection, "value")
            and self.src_ext.node.configuration.selection.value == "reduce"
        ) or self.src_ext.node.configuration.selection == "reduce":
            reduce_properties = self.src_ext.node.configuration.reduce_properties
            operations = [
                "css",
                "max",
                "mean",
                "min",
                "missing",
                "count",
                "cv",
                "range",
                "std",
                "ste",
                "sumw",
                "sum",
                "uss",
                "var",
            ]
            summary_values = [
                "n",
                "nMissing",
                "sumOfWeights",
                "minimum",
                "maximum",
                "mean",
                "css",
            ]
            fields = []
            for input_node in self.src_input_nodes:
                for input_field in input_node.schema.schema.fields:
                    for key_prop in key_properties:
                        if "key" in key_prop and key_prop["key"] == input_field.name:
                            new_field = model.FieldModel(
                                name=input_field.name,
                                type=input_field.type,
                                metadata=input_field.metadata.copy(),
                                nullable=input_field.nullable,
                                app_data=input_field.app_data,
                            )
                            new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                            fields.append(new_field)
                    for reduce_prop in reduce_properties:
                        correct_props = False
                        for prop in reduce_prop:
                            if "reduce" in prop and prop["reduce"] == input_field.name:
                                correct_props = True
                        if correct_props:
                            for prop in reduce_prop:
                                for value in prop:
                                    if value in operations:
                                        new_field = model.FieldModel(
                                            name=prop[value],
                                            type="double",
                                            metadata=model.Metadata(
                                                is_key=False,
                                                min_length=0,
                                                decimal_scale=0,
                                                decimal_precision=0,
                                                max_length=100,
                                                is_signed=False,
                                            ),
                                            nullable=False,
                                            app_data={
                                                "odbc_type": "DOUBLE",
                                                "is_unicode_string": False,
                                                "type_code": "DFLOAT",
                                            },
                                        )
                                        fields.append(new_field)
                                    if value == "summary":
                                        summary_field = model.FieldModel(
                                            name=prop[value],
                                            type="double",
                                            metadata=model.Metadata(
                                                is_key=False,
                                                min_length=0,
                                                decimal_scale=0,
                                                decimal_precision=0,
                                                max_length=6,
                                                is_signed=False,
                                            ),
                                            nullable=False,
                                            app_data={
                                                "odbc_type": "UNKNOWN",
                                                "type_code": "UNKNOWN",
                                                "is_unicode_string": False,
                                            },
                                        )
                                        fields.append(summary_field)
                                        for sum_value in summary_values:
                                            new_field = model.FieldModel(
                                                name=f"{prop[value]}.{sum_value}",
                                                type="double",
                                                metadata=model.Metadata(
                                                    is_key=False,
                                                    min_length=0,
                                                    decimal_scale=0,
                                                    decimal_precision=0,
                                                    max_length=6,
                                                    is_signed=False,
                                                    item_index=2,
                                                ),
                                                nullable=True,
                                                app_data={
                                                    "odbc_type": "DOUBLE",
                                                    "is_unicode_string": False,
                                                    "type_code": "DFLOAT",
                                                },
                                            )
                                            fields.append(new_field)
            new_schema = model.RecordSchema(id="", fields=fields)
            return new_schema

        elif (
            hasattr(self.src_ext.node.configuration.selection, "value")
            and self.src_ext.node.configuration.selection.value == "rereduce"
        ) or self.src_ext.node.configuration.selection == "rereduce":
            rereduce_properties = self.src_ext.node.configuration.rereduce_properties
            operations = [
                "css",
                "max",
                "mean",
                "min",
                "missing",
                "count",
                "cv",
                "range",
                "std",
                "ste",
                "sumw",
                "sum",
                "uss",
                "var",
            ]
            fields = []
            for input_node in self.src_input_nodes:
                for input_field in input_node.schema.schema.fields:
                    for key_prop in key_properties:
                        if "key" in key_prop and key_prop["key"] == input_field.name:
                            new_field2 = model.FieldModel(
                                name=input_field.name,
                                type=input_field.type,
                                metadata=input_field.metadata.copy(),
                                nullable=input_field.nullable,
                                app_data=input_field.app_data,
                            )
                            new_field2.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                            fields.append(new_field2)
                    for rereduce_prop in rereduce_properties:
                        correct_props = False
                        for prop in rereduce_prop:
                            if "rereduce" in prop and prop["rereduce"] == input_field.name:
                                correct_props = True
                        if correct_props:
                            for prop in rereduce_prop:
                                for value in prop:
                                    if value in operations:
                                        new_field = model.FieldModel(
                                            name=prop[value],
                                            type="double",
                                            metadata=model.Metadata(
                                                is_key=False,
                                                min_length=0,
                                                decimal_scale=0,
                                                decimal_precision=0,
                                                max_length=100,
                                                is_signed=False,
                                            ),
                                            nullable=False,
                                            app_data={
                                                "odbc_type": "DOUBLE",
                                                "is_unicode_string": False,
                                                "type_code": "DFLOAT",
                                            },
                                        )
                                        fields.append(new_field)

            new_schema = model.RecordSchema(id="", fields=fields)
            return new_schema

        elif (
            hasattr(self.src_ext.node.configuration.selection, "value")
            and self.src_ext.node.configuration.selection.value == "countField"
        ) or self.src_ext.node.configuration.selection == "countField":
            count_field_properties = self.src_ext.node.configuration.count_field_properties
            fields = []
            for input_node in self.src_input_nodes:
                for input_field in input_node.schema.schema.fields:
                    for key_prop in key_properties:
                        if "key" in key_prop and key_prop["key"] == input_field.name:
                            new_field = model.FieldModel(
                                name=input_field.name,
                                type=input_field.type,
                                metadata=input_field.metadata.copy(),
                                nullable=input_field.nullable,
                                app_data=input_field.app_data,
                            )
                            new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                            fields.append(new_field)
            for count_field in count_field_properties:
                for item in count_field:
                    if "countField" in item:
                        new_field = model.FieldModel(
                            name=item["countField"],
                            type="double",
                            metadata=model.Metadata(
                                is_key=False,
                                min_length=0,
                                decimal_scale=0,
                                decimal_precision=0,
                                max_length=6,
                                is_signed=False,
                            ),
                            nullable=True,
                            app_data={
                                "odbc_type": "DOUBLE",
                                "is_unicode_string": False,
                                "type_code": "DFLOAT",
                            },
                        )
                        fields.append(new_field)

            new_schema = model.RecordSchema(id="", fields=fields)
            return new_schema

    def compute_compare(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, compare)
        if len(self.src_input_nodes) != 2:
            logger.warning(
                f"\nCompare stage {self.src_ext.node.label} does not have 2 inputs. Auto column metadata propagation can not be computed.\n",
            )
            return None

        first_link_name: str | None = None
        second_link_name: str | None = None
        if self.src_ext.node.configuration.inputlink_ordering_list is not None:
            for link in self.src_ext.node.configuration.inputlink_ordering_list:
                if "link_label" in link and link["link_label"].lower() == "first":
                    first_link_name = link["link_name"] if "link_name" in link else None
                elif "link_label" in link and link["link_label"].lower() == "second":
                    second_link_name = link["link_name"] if "link_name" in link else None
        if not first_link_name and not second_link_name:
            logger.warning(
                f"\nInput link ordering has not been set for compare stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
            )
            first_link_name = self.src_input_nodes[0].link.link.name
            second_link_name = self.src_input_nodes[1].link.link.name
        elif not first_link_name:
            for input_node in self.src_input_nodes:
                if input_node.link.link.name != second_link_name:
                    first_link_name = input_node.link.link.name
        elif not second_link_name:
            for input_node in self.src_input_nodes:
                if input_node.link.link.name != first_link_name:
                    second_link_name = input_node.link.link.name

        first_link_node: Link | None = None
        second_link_node: Link | None = None
        for input_node in self.src_input_nodes:
            if input_node.link.link.name == first_link_name:
                first_link_node = input_node.link.link
            if input_node.link.link.name == second_link_name:
                second_link_node = input_node.link.link

        if not first_link_node or not second_link_node:
            logger.warning(
                f"Link ordering assignment for compare stage {self.src_ext.label} does not match link names",
            )
            return None

        fields = []
        for input_field in first_link_node.schema.configuration.fields:
            new_field = model.FieldModel(
                name=f"first.{input_field.name}",
                type=input_field.type,
                metadata=input_field.metadata.copy(),
                nullable=input_field.nullable,
                app_data=input_field.app_data,
            )
            new_field.metadata.source_field_id = f"{first_link_name}.{input_field.name}"
            fields.append(new_field)

        fields.append(
            model.FieldModel(
                name="first",
                type="string",
                nullable=False,
                metadata=model.Metadata(
                    description="Compare output",
                    max_length=0,
                    min_length=0,
                    decimal_precision=0,
                    decimal_scale=0,
                    is_key=False,
                    is_signed=False,
                ),
                app_data={
                    "is_unicode_string": False,
                    "odbc_type": "UNKNOWN",
                    "type_code": "UNKNOWN",
                },
            )
        )

        for input_field in second_link_node.schema.configuration.fields:
            new_field = model.FieldModel(
                name=f"second.{input_field.name}",
                type=input_field.type,
                metadata=input_field.metadata.copy(),
                nullable=input_field.nullable,
                app_data=input_field.app_data,
            )
            new_field.metadata.source_field_id = f"{second_link_name}.{input_field.name}"
            fields.append(new_field)

        fields.append(
            model.FieldModel(
                name="second",
                type="string",
                nullable=False,
                metadata=model.Metadata(
                    description="Compare output",
                    max_length=0,
                    min_length=0,
                    decimal_precision=0,
                    decimal_scale=0,
                    is_key=False,
                    is_signed=False,
                ),
                app_data={
                    "is_unicode_string": False,
                    "odbc_type": "UNKNOWN",
                    "type_code": "UNKNOWN",
                },
            )
        )

        fields.append(
            model.FieldModel(
                name="result",
                type="integer",
                nullable=False,
                metadata=model.Metadata(
                    description="Compare output",
                    max_length=0,
                    min_length=0,
                    decimal_precision=0,
                    decimal_scale=0,
                    is_key=False,
                    is_signed=True,
                ),
                app_data={
                    "is_unicode_string": False,
                    "odbc_type": "INTEGER",
                    "type_code": "INT32",
                },
            )
        )

        new_schema = model.RecordSchema(id="", fields=fields)

        return new_schema

    def compute_funnel(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, funnel)
        most_fields_input = self.src_input_nodes[0]
        for input_node in self.src_input_nodes:
            if len(input_node.schema.schema.fields) > len(most_fields_input.schema.schema.fields):
                most_fields_input = input_node
        fields = []
        for input_field in most_fields_input.schema.schema.fields:
            in_all = True
            for input_node in self.src_input_nodes:
                found = False
                for field in input_node.schema.schema.fields:
                    assert isinstance(field, model.FieldModel)
                    assert isinstance(input_field, model.FieldModel)
                    if (
                        field.name == input_field.name
                        and field.type == input_field.type
                        and (
                            "odbc_type" in field.app_data
                            and "odbc_type" in input_field.app_data
                            and field.app_data["odbc_type"] == input_field.app_data["odbc_type"]
                        )
                    ):
                        found = True
                if not found:
                    in_all = False
            if in_all:
                fields.append(
                    model.FieldModel(
                        name=input_field.name,
                        type=input_field.type,
                        metadata=input_field.metadata,
                        nullable=input_field.nullable,
                        app_data=input_field.app_data,
                    )
                )

        return model.RecordSchema(id="", fields=fields)

    def compute_join(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, join)
        if (
            hasattr(self.src_ext.node.configuration.operator, "value")
            and self.src_ext.node.configuration.operator.value in ["innerjoin", "leftouterjoin"]
        ) or self.src_ext.node.configuration.operator in ["innerjoin", "leftouterjoin"]:
            ordering_list = self.src_ext.node.configuration.inputlink_ordering_list or []
            if not len(ordering_list):
                logger.warning(
                    f"\nInput link ordering has not been set for join stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
                )
                for i, input_node in enumerate(self.src_input_nodes):
                    if i == 0:
                        ordering_list.append(
                            {
                                "link_label": "Left",
                                "link_name": input_node.link.link.name,
                            }
                        )
                    elif i == len(self.src_input_nodes) - 1:
                        ordering_list.append(
                            {
                                "link_label": "Right",
                                "link_name": input_node.link.link.name,
                            }
                        )
                    else:
                        ordering_list.append(
                            {
                                "link_label": f"Intermediate {i}",
                                "link_name": input_node.link.link.name,
                            }
                        )
                self.src_ext.node.configuration.inputlink_ordering_list = ordering_list
            fields = {}
            for link_order in ordering_list:
                if "link_label" in link_order and link_order["link_label"] == "Left":
                    for input_node in self.src_input_nodes:
                        if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                            for input_field in input_node.schema.schema.fields:
                                new_field = model.FieldModel(
                                    name=input_field.name,
                                    type=input_field.type,
                                    metadata=input_field.metadata.copy(),
                                    nullable=input_field.nullable,
                                    app_data=input_field.app_data,
                                )
                                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                                fields[input_field.name] = new_field
            for i in range(1, len(self.src_input_nodes)):
                for link_order in ordering_list:
                    if "link_label" in link_order and link_order["link_label"] == f"Intermediate {i}":
                        for input_node in self.src_input_nodes:
                            if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                                for input_field in input_node.schema.schema.fields:
                                    if input_field.name not in fields:
                                        new_field = model.FieldModel(
                                            name=input_field.name,
                                            type=input_field.type,
                                            metadata=input_field.metadata.copy(),
                                            nullable=input_field.nullable,
                                            app_data=input_field.app_data,
                                        )
                                        new_field.metadata.source_field_id = (
                                            f"{input_node.link.link.name}.{input_field.name}"
                                        )
                                        fields[input_field.name] = new_field
            for link_order in ordering_list:
                if "link_label" in link_order and link_order["link_label"] == "Right":
                    for input_node in self.src_input_nodes:
                        if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                            for input_field in input_node.schema.schema.fields:
                                if input_field.name not in fields:
                                    new_field = model.FieldModel(
                                        name=input_field.name,
                                        type=input_field.type,
                                        metadata=input_field.metadata.copy(),
                                        nullable=input_field.nullable,
                                        app_data=input_field.app_data,
                                    )
                                    new_field.metadata.source_field_id = (
                                        f"{input_node.link.link.name}.{input_field.name}"
                                    )
                                    fields[input_field.name] = new_field

            new_schema = model.RecordSchema(id="", fields=list(fields.values()))
            return new_schema

        elif (
            hasattr(self.src_ext.node.configuration.operator, "value")
            and self.src_ext.node.configuration.operator.value == "rightouterjoin"
        ) or self.src_ext.node.configuration.operator == "rightouterjoin":
            ordering_list = self.src_ext.node.configuration.inputlink_ordering_list or []
            if not len(ordering_list):
                logger.warning(
                    f"\nInput link ordering has not been set for join stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
                )
                for i, input_node in enumerate(self.src_input_nodes):
                    if i == 0:
                        ordering_list.append(
                            {
                                "link_label": "Left",
                                "link_name": input_node.link.link.name,
                            }
                        )
                    elif i == len(self.src_input_nodes) - 1:
                        ordering_list.append(
                            {
                                "link_label": "Right",
                                "link_name": input_node.link.link.name,
                            }
                        )
                    else:
                        ordering_list.append(
                            {
                                "link_label": f"Intermediate {i}",
                                "link_name": input_node.link.link.name,
                            }
                        )
            fields = {}
            if not len(self.src_ext.node.configuration.key_properties):
                logger.warning(
                    f"\nNo key properties have been set for join stage {self.src_ext.node.label}. Cannot compute schema.\n",
                )
                return None
            key_properties = self.src_ext.node.configuration.key_properties
            for link_order in ordering_list:
                if "link_label" in link_order and link_order["link_label"] == "Right":
                    for input_node in self.src_input_nodes:
                        if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                            for input_field in input_node.schema.schema.fields:
                                for key_prop in key_properties:
                                    if "key" in key_prop and input_field.name == key_prop["key"]:
                                        new_field = model.FieldModel(
                                            name=input_field.name,
                                            type=input_field.type,
                                            metadata=input_field.metadata.copy(),
                                            nullable=input_field.nullable,
                                            app_data=input_field.app_data,
                                        )
                                        new_field.metadata.source_field_id = (
                                            f"{input_node.link.link.name}.{input_field.name}"
                                        )
                                        fields[input_field.name] = new_field

            for link_order in ordering_list:
                if "link_label" in link_order and link_order["link_label"] == "Left":
                    for input_node in self.src_input_nodes:
                        if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                            for input_field in input_node.schema.schema.fields:
                                if input_field.name not in fields:
                                    new_field = model.FieldModel(
                                        name=input_field.name,
                                        type=input_field.type,
                                        metadata=input_field.metadata.copy(),
                                        nullable=input_field.nullable,
                                        app_data=input_field.app_data,
                                    )
                                    new_field.metadata.source_field_id = (
                                        f"{input_node.link.link.name}.{input_field.name}"
                                    )
                                    fields[input_field.name] = new_field
            for i in range(1, len(self.src_input_nodes)):
                for link_order in ordering_list:
                    if "link_label" in link_order and link_order["link_label"] == f"Intermediate {i}":
                        for input_node in self.src_input_nodes:
                            if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                                for input_field in input_node.schema.schema.fields:
                                    if input_field.name not in fields:
                                        new_field = model.FieldModel(
                                            name=input_field.name,
                                            type=input_field.type,
                                            metadata=input_field.metadata.copy(),
                                            nullable=input_field.nullable,
                                            app_data=input_field.app_data,
                                        )
                                        new_field.metadata.source_field_id = (
                                            f"{input_node.link.link.name}.{input_field.name}"
                                        )
                                        fields[input_field.name] = new_field
            for link_order in ordering_list:
                if "link_label" in link_order and link_order["link_label"] == "Right":
                    for input_node in self.src_input_nodes:
                        if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                            for input_field in input_node.schema.schema.fields:
                                if input_field.name not in fields:
                                    new_field = model.FieldModel(
                                        name=input_field.name,
                                        type=input_field.type,
                                        metadata=input_field.metadata.copy(),
                                        nullable=input_field.nullable,
                                        app_data=input_field.app_data,
                                    )
                                    new_field.metadata.source_field_id = (
                                        f"{input_node.link.link.name}.{input_field.name}"
                                    )
                                    fields[input_field.name] = new_field

            new_schema = model.RecordSchema(id="", fields=list(fields.values()))
            return new_schema

        elif (
            hasattr(self.src_ext.node.configuration.operator, "value")
            and self.src_ext.node.configuration.operator.value == "fullouterjoin"
        ) or self.src_ext.node.configuration.operator == "fullouterjoin":
            ordering_list = self.src_ext.node.configuration.inputlink_ordering_list or []
            if not len(self.src_ext.node.configuration.key_properties):
                logger.warning(
                    f"\nNo key properties have been set for join stage {self.src_ext.node.label}. Cannot compute schema.\n",
                )
                return None
            if not len(ordering_list):
                logger.warning(
                    f"\nInput link ordering has not been set for join stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
                )
                for i, input_node in enumerate(self.src_input_nodes):
                    if i == 0:
                        ordering_list.append(
                            {
                                "link_label": "Left",
                                "link_name": input_node.link.link.name,
                            }
                        )
                    elif i == len(self.src_input_nodes) - 1:
                        ordering_list.append(
                            {
                                "link_label": "Right",
                                "link_name": input_node.link.link.name,
                            }
                        )
                    else:
                        ordering_list.append(
                            {
                                "link_label": f"Intermediate {i}",
                                "link_name": input_node.link.link.name,
                            }
                        )
            if len(self.src_input_nodes) != 2:
                logger.warning(
                    f"\nJoin stage {self.src_ext.node.label} does not have exactly two inputs for full outer join. Cannot compute schema.\n",
                )
                return None
            key_properties = self.src_ext.node.configuration.key_properties
            fields = {}
            for link_order in ordering_list:
                if "link_label" in link_order and link_order["link_label"] == "Left":
                    for input_node in self.src_input_nodes:
                        if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                            for input_field in input_node.schema.schema.fields:
                                is_key_prop = False
                                for key_prop in key_properties:
                                    if "key" in key_prop and input_field.name == key_prop["key"]:
                                        is_key_prop = True
                                        new_field = model.FieldModel(
                                            name=f"leftRec_{input_field.name}",
                                            type=input_field.type,
                                            metadata=input_field.metadata.copy(),
                                            nullable=input_field.nullable,
                                            app_data=input_field.app_data,
                                        )
                                        new_field.metadata.source_field_id = (
                                            f"{input_node.link.link.name}.{input_field.name}"
                                        )
                                        fields[f"leftRec_{input_field.name}"] = new_field
                                if not is_key_prop:
                                    new_field = model.FieldModel(
                                        name=input_field.name,
                                        type=input_field.type,
                                        metadata=input_field.metadata.copy(),
                                        nullable=input_field.nullable,
                                        app_data=input_field.app_data,
                                    )
                                    new_field.metadata.source_field_id = (
                                        f"{input_node.link.link.name}.{input_field.name}"
                                    )
                                    fields[input_field.name] = new_field
            for link_order in ordering_list:
                if "link_label" in link_order and link_order["link_label"] == "Right":
                    for input_node in self.src_input_nodes:
                        if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                            for input_field in input_node.schema.schema.fields:
                                is_key_prop = False
                                for key_prop in key_properties:
                                    if "key" in key_prop and input_field.name == key_prop["key"]:
                                        is_key_prop = True
                                        new_field = model.FieldModel(
                                            name=f"rightRec_{input_field.name}",
                                            type=input_field.type,
                                            metadata=input_field.metadata.copy(),
                                            nullable=input_field.nullable,
                                            app_data=input_field.app_data,
                                        )
                                        new_field.metadata.source_field_id = (
                                            f"{input_node.link.link.name}.{input_field.name}"
                                        )
                                        fields[f"rightRec_{input_field.name}"] = new_field
                                if not is_key_prop and input_field.name not in fields:
                                    new_field = model.FieldModel(
                                        name=input_field.name,
                                        type=input_field.type,
                                        metadata=input_field.metadata.copy(),
                                        nullable=input_field.nullable,
                                        app_data=input_field.app_data,
                                    )
                                    new_field.metadata.source_field_id = (
                                        f"{input_node.link.link.name}.{input_field.name}"
                                    )
                                    fields[input_field.name] = new_field

            new_schema = model.RecordSchema(id="", fields=list(fields.values()))
            return new_schema

    def compute_lookup(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, lookup)
        ordering_list = self.src_ext.node.configuration.inputlink_ordering_list or []
        if not len(ordering_list):
            logger.warning(
                f"\nInput link ordering has not been set for lookup stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
                # style="yellow",
            )
            for input_node in self.src_input_nodes:
                if input_node.link.link.type == "PRIMARY":
                    ordering_list.append(
                        {
                            "link_label": "Primary",
                            "link_name": input_node.link.link.name,
                        }
                    )
            lookup_num = 1
            for input_node in self.src_input_nodes:
                if input_node.link.link.type == "REFERENCE":
                    ordering_list.append(
                        {
                            "link_label": f"Lookup {lookup_num}",
                            "link_name": input_node.link.link.name,
                        }
                    )
                    lookup_num += 1
        fields = {}
        for link_order in ordering_list:
            if "link_label" in link_order and link_order["link_label"] == "Primary":
                for input_node in self.src_input_nodes:
                    if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                        for input_field in input_node.schema.schema.fields:
                            new_field = model.FieldModel(
                                name=input_field.name,
                                type=input_field.type,
                                metadata=input_field.metadata.copy(),
                                nullable=input_field.nullable,
                                app_data=input_field.app_data,
                            )
                            new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                            fields[input_field.name] = new_field
        for i in range(1, len(self.src_input_nodes)):
            for link_order in ordering_list:
                if "link_label" in link_order and link_order["link_label"] == f"Lookup {i}":
                    for input_node in self.src_input_nodes:
                        if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                            for input_field in input_node.schema.schema.fields:
                                if input_field.name not in fields:
                                    new_field = model.FieldModel(
                                        name=input_field.name,
                                        type=input_field.type,
                                        metadata=input_field.metadata.copy(),
                                        nullable=input_field.nullable,
                                        app_data=input_field.app_data,
                                    )
                                    new_field.metadata.source_field_id = (
                                        f"{input_node.link.link.name}.{input_field.name}"
                                    )
                                    fields[input_field.name] = new_field
        new_schema = model.RecordSchema(id="", fields=list(fields.values()))
        return new_schema

    def compute_merge(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, merge)
        ordering_list = self.src_ext.node.configuration.inputlink_ordering_list or []
        if not len(ordering_list):
            logger.warning(
                f"\nInput link ordering has not been set for lookup stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
            )
            for i, input_node in enumerate(self.src_input_nodes):
                if i == 0:
                    ordering_list.append({"link_label": "Main", "link_name": input_node.link.link.name})
                else:
                    ordering_list.append(
                        {
                            "link_label": f"Update {i}",
                            "link_name": input_node.link.link.name,
                        }
                    )
            self.src_ext.node.configuration.inputlink_ordering_list = ordering_list
        if self.link.type == "REJECT":
            output_ordering_list = self.src_ext.node.configuration.outputlink_ordering_list or []
            if not len(output_ordering_list):
                logger.warning(
                    f"\nOutput link ordering has not been set for lookup stage {self.src_ext.node.label}. Cannot compute reject link schema.\n",
                )
                return None
            source_link_label = None
            for output_order in output_ordering_list:
                if "link_name" in output_order and output_order["link_name"] == self.link.name:
                    source_link_label = output_order["link_label"] if "link_label" in output_order else None
            if source_link_label:
                source_link_label = source_link_label.split("'")[1]
            source_link = None
            for input_order in ordering_list:
                if "link_label" in input_order and input_order["link_label"] == source_link_label:
                    source_link = output_order["link_name"] if "link_name" in output_order else None
            fields = []
            if source_link:
                for input_node in self.src_input_nodes:
                    if input_node.link.link.name == source_link:
                        for field in input_node.schema.schema.fields:
                            new_field = model.FieldModel(
                                name=input_field.name,
                                type=input_field.type,
                                metadata=input_field.metadata.copy(),
                                nullable=input_field.nullable,
                                app_data=input_field.app_data,
                            )
                            fields.append(new_field)
            new_schema = model.RecordSchema(id="", fields=fields)
            return new_schema
        else:
            fields = {}
            for link_order in ordering_list:
                if "link_label" in link_order and link_order["link_label"] == "Main":
                    for input_node in self.src_input_nodes:
                        if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                            for input_field in input_node.schema.schema.fields:
                                new_field = model.FieldModel(
                                    name=input_field.name,
                                    type=input_field.type,
                                    metadata=input_field.metadata.copy(),
                                    nullable=input_field.nullable,
                                    app_data=input_field.app_data,
                                )
                                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                                fields[input_field.name] = new_field
            for i in range(1, len(self.src_input_nodes)):
                for link_order in ordering_list:
                    if "link_label" in link_order and link_order["link_label"] == f"Update {i}":
                        for input_node in self.src_input_nodes:
                            if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                                for input_field in input_node.schema.schema.fields:
                                    if input_field.name not in fields:
                                        new_field = model.FieldModel(
                                            name=input_field.name,
                                            type=input_field.type,
                                            metadata=input_field.metadata.copy(),
                                            nullable=input_field.nullable,
                                            app_data=input_field.app_data,
                                        )
                                        new_field.metadata.source_field_id = (
                                            f"{input_node.link.link.name}.{input_field.name}"
                                        )
                                        fields[input_field.name] = new_field
            new_schema = model.RecordSchema(id="", fields=list(fields.values()))
            return new_schema

    def compute_pivot(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, pivot)
        pivot_properties = self.src_ext.node.configuration.pivot_properties
        if not len(pivot_properties):
            logger.warning(
                f"\nPivot properties have not been set for pivot stage {self.src_ext.node.label}. Cannot compute schema.\n",
            )
            return None
        if (
            hasattr(self.src_ext.node.configuration.pivot_type, "value")
            and self.src_ext.node.configuration.pivot_type.value == "pivot"
        ) or self.src_ext.node.configuration.pivot_type == "pivot":
            fields = []
            for input_node in self.src_input_nodes:
                for input_field in input_node.schema.schema.fields:
                    is_pivot_prop = False
                    for pivot_prop in pivot_properties:
                        if "derivation" in pivot_prop and pivot_prop["derivation"] == input_field.name:
                            is_pivot_prop = True
                            new_field = model.FieldModel(
                                name=pivot_prop["name"],
                                type=input_field.type,
                                metadata=input_field.metadata.copy(),
                                nullable=input_field.nullable,
                                app_data=input_field.app_data,
                            )
                            if "sqlType" in pivot_prop:
                                new_field.app_data["odbc_type"] = pivot_prop["sqlType"]
                            if "length" in pivot_prop:
                                new_field.metadata.max_length = int(pivot_prop["length"])
                            if "scale" in pivot_prop:
                                new_field.metadata.decimal_scale = pivot_prop["scale"]
                            fields.append(new_field)
                    if not is_pivot_prop:
                        new_field = model.FieldModel(
                            name=input_field.name,
                            type=input_field.type,
                            metadata=input_field.metadata.copy(),
                            nullable=input_field.nullable,
                            app_data=input_field.app_data,
                        )
                        new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                        fields.append(new_field)
            pivot_index = False
            for pivot_prop in pivot_properties:
                if "isPivotIndex" in pivot_prop and pivot_prop["isPivotIndex"]:
                    pivot_index = True
                    new_field = model.FieldModel(
                        name=pivot_prop["name"],
                        type="integer",
                        metadata=model.Metadata(
                            description="This is a pivot index column",
                            min_length=0,
                            max_length=0,
                            is_signed=True,
                            decimal_precision=0,
                            decimal_scale=0,
                        ),
                        nullable=True,
                        app_data={
                            "time_scale": 0,
                            "odbc_type": "BIGINT",
                            "type_code": "INT64",
                        },
                    )
                    fields.append(new_field)
            if not pivot_index and self.src_ext.node.configuration.pivot_index:
                new_field = model.FieldModel(
                    name="Pivot_index",
                    type="integer",
                    metadata=model.Metadata(
                        description="This is a pivot index column",
                        min_length=0,
                        max_length=0,
                        is_signed=True,
                        decimal_precision=0,
                        decimal_scale=0,
                        is_key=False,
                    ),
                    nullable=True,
                    app_data={
                        "time_scale": 0,
                        "odbc_type": "BIGINT",
                        "type_code": "INT64",
                    },
                )
                fields.append(new_field)
            new_schema = model.RecordSchema(id="", fields=fields)
            return new_schema
        else:
            fields = []
            for input_node in self.src_input_nodes:
                for input_field in input_node.schema.schema.fields:
                    is_pivot_prop = False
                    for pivot_prop in pivot_properties:
                        if "name" in pivot_prop and pivot_prop["name"] == input_field.name:
                            is_pivot_prop = True
                            if "sqlType" in pivot_prop and pivot_prop["sqlType"] in self.type_data:
                                sql_type = pivot_prop["sqlType"]
                                new_field = model.FieldModel(
                                    name=pivot_prop["name"],
                                    type=self.type_data[sql_type]["type"],
                                    metadata=model.Metadata(
                                        max_length=pivot_prop["length"],
                                        min_length=pivot_prop["length"],
                                        decimal_scale=pivot_prop["scale"],
                                        is_signed=pivot_prop["signed"],
                                    ),
                                    nullable=input_field.nullable,
                                    app_data={
                                        "odbc_type": sql_type,
                                        "type_code": self.type_data[sql_type]["type_code"],
                                        "is_unicode_string": pivot_prop["unicode"] or None,
                                    },
                                )
                                fields.append(new_field)
                                if "aggFunction" in pivot_prop:
                                    for agg_function in pivot_prop["aggFunction"]:
                                        if "sqlType" in agg_function and agg_function["sqlType"] in self.type_data:
                                            sql_type = agg_function["sqlType"]
                                            new_field = model.FieldModel(
                                                name=f"{pivot_prop['name']}_{agg_function['functionName']}",
                                                type=self.type_data[sql_type]["type"],
                                                metadata=model.Metadata(
                                                    decimal_precision=agg_function["precision"],
                                                    max_length=agg_function["length"],
                                                    min_length=agg_function["length"],
                                                    decimal_scale=agg_function["scale"],
                                                ),
                                                nullable=input_field.nullable,
                                                app_data={
                                                    "odbc_type": sql_type,
                                                    "type_code": self.type_data[sql_type]["type_code"],
                                                },
                                            )
                                            fields.append(new_field)
                    if not is_pivot_prop:
                        new_field = model.FieldModel(
                            name=input_field.name,
                            type=input_field.type,
                            metadata=input_field.metadata.copy(),
                            nullable=input_field.nullable,
                            app_data=input_field.app_data,
                        )
                        new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                        fields.append(new_field)
            pivot_index = False
            for pivot_prop in pivot_properties:
                if "isPivotIndex" in pivot_prop and pivot_prop["isPivotIndex"]:
                    pivot_index = True
                    new_field = model.FieldModel(
                        name=pivot_prop["name"],
                        type="integer",
                        metadata=model.Metadata(
                            description="This is a pivot index column",
                            min_length=0,
                            max_length=0,
                            is_signed=True,
                            decimal_precision=0,
                            decimal_scale=0,
                        ),
                        nullable=True,
                        app_data={
                            "time_scale": 0,
                            "odbc_type": "BIGINT",
                            "type_code": "INT64",
                        },
                    )
                    fields.append(new_field)
            if not pivot_index and self.src_ext.node.configuration.pivot_index:
                new_field = model.FieldModel(
                    name="Pivot_index",
                    type="integer",
                    metadata=model.Metadata(
                        description="This is a pivot index column",
                        min_length=0,
                        max_length=0,
                        is_signed=True,
                        decimal_precision=0,
                        decimal_scale=0,
                        is_key=False,
                    ),
                    nullable=True,
                    app_data={
                        "time_scale": 0,
                        "odbc_type": "BIGINT",
                        "type_code": "INT64",
                    },
                )
                fields.append(new_field)
            new_schema = model.RecordSchema(id="", fields=fields)
            return new_schema

    def compute_checksum(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, checksum)
        fields = []
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                fields.append(new_field)
        new_field = model.FieldModel(
            name="checksum",
            type="string",
            metadata=model.Metadata(
                is_key=False,
                min_length=32,
                decimal_precision=0,
                decimal_scale=0,
                max_length=32,
                is_signed=True,
            ),
            nullable=False,
            app_data={
                "odbc_type": "CHAR",
                "is_unicode_string": False,
                "type_code": "STRING",
            },
        )
        fields.append(new_field)

        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_column_export(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, column_export
        )
        export_column = self.src_ext.node.configuration.field
        max_length = self.src_ext.node.configuration.max_length
        col_type = (
            self.src_ext.node.configuration.type.value
            if hasattr(self.src_ext.node.configuration.type, "value")
            else self.src_ext.node.configuration.type
        )
        explicit = (
            hasattr(self.src_ext.node.configuration.selection, "value")
            and self.src_ext.node.configuration.selection.value == "explicit"
        ) or self.src_ext.node.configuration.selection == "explicit"
        schema = self.src_ext.node.configuration.schema_
        fields = []
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                if (
                    (
                        hasattr(
                            self.src_ext.node.configuration.keep_exported_fields,
                            "value",
                        )
                        and self.src_ext.node.configuration.keep_exported_fields.value == " "
                    )
                    or self.src_ext.node.configuration.keep_exported_fields == " "
                ) and (explicit and input_field.name in schema):
                    continue
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                fields.append(new_field)
        if col_type == "ustring":
            # unicode var char
            new_field = model.FieldModel(
                name=export_column,
                type="binary",
                metadata=model.Metadata(
                    max_length=max_length,
                    min_length=0,
                    decimal_precision=0,
                    decimal_scale=0,
                    is_key=False,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "is_unicode_string": False,
                    "odbc_type": "VARBINARY",
                    "type_code": "BINARY",
                },
            )
            fields.append(new_field)
        elif col_type == "string":
            # var char
            new_field = model.FieldModel(
                name=export_column,
                type="string",
                metadata=model.Metadata(
                    max_length=max_length,
                    min_length=0,
                    decimal_precision=0,
                    decimal_scale=0,
                    is_key=False,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "is_unicode_string": False,
                    "odbc_type": "VARCHAR",
                    "type_code": "STRING",
                },
            )
            fields.append(new_field)
        elif col_type == "raw":
            # binary
            new_field = model.FieldModel(
                name=export_column,
                type="string",
                metadata=model.Metadata(
                    max_length=max_length,
                    min_length=0,
                    decimal_precision=0,
                    decimal_scale=0,
                    is_key=False,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "is_unicode_string": True,
                    "odbc_type": "VARCHAR",
                    "type_code": "STRING",
                },
            )
            fields.append(new_field)
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_column_generator(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, column_generator
        )
        schema = self.src_ext.node.configuration.schema_ or []
        fields = []
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                fields.append(new_field)
        for col_name in schema:
            new_field = model.FieldModel(
                name=col_name,
                type="string",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    max_length=0,
                    is_signed=True,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "VARCHAR",
                    "is_unicode_string": False,
                    "type_code": "STRING",
                },
            )
            fields.append(new_field)

        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_column_import(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, column_import
        )
        schema = self.src_ext.node.configuration.schema_ or []
        field = self.src_ext.node.configuration.field
        fields = {}
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                if input_field.name != field:
                    new_field = model.FieldModel(
                        name=input_field.name,
                        type=input_field.type,
                        metadata=input_field.metadata.copy(),
                        nullable=input_field.nullable,
                        app_data=input_field.app_data,
                    )
                    new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                    fields[input_field.name] = new_field
        for column_schema in schema:
            if "ColumnName" in column_schema and column_schema["ColumnName"] not in fields:
                new_field = model.FieldModel(
                    name=column_schema["ColumnName"],
                    type="string",
                    metadata=model.Metadata(
                        is_key=False,
                        min_length=0,
                        decimal_scale=0,
                        decimal_precision=0,
                        max_length=0,
                        is_signed=True,
                    ),
                    nullable=False,
                    app_data={
                        "odbc_type": "VARCHAR",
                        "is_unicode_string": False,
                        "type_code": "STRING",
                    },
                )
                fields[column_schema["ColumnName"]] = new_field

        new_schema = model.RecordSchema(id="", fields=list(fields.values()))
        return new_schema

    def compute_combine_records(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, combine_records
        )
        subrec_name = self.src_ext.node.configuration.subrecname
        fields = []
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                fields.append(new_field)
        if subrec_name:
            new_field = model.FieldModel(
                name=subrec_name,
                type="string",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=32,
                    decimal_scale=0,
                    decimal_precision=0,
                    max_length=32,
                    is_signed=False,
                    source_field_id=f"{input_node.link.link.name}.{subrec_name}",
                ),
                app_data={
                    "odbc_type": "CHAR",
                    "is_unicode_string": False,
                    "type_code": "STRING",
                },
            )
            fields.append(new_field)
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_difference(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, difference)
        fields = {}
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                if input_field.name not in fields:
                    new_field = model.FieldModel(
                        name=input_field.name,
                        type=input_field.type,
                        metadata=input_field.metadata.copy(),
                        nullable=input_field.nullable,
                        app_data=input_field.app_data,
                    )
                    new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                    fields[input_field.name] = new_field
        new_field = model.FieldModel(
            name="diff",
            type="integer",
            metadata=model.Metadata(
                is_key=False,
                min_length=0,
                decimal_scale=0,
                decimal_precision=0,
                max_length=0,
                is_signed=0,
            ),
            nullable=False,
            app_data={
                "odbc_type": "TINYINT",
                "is_unicode_string": False,
                "type_code": "INT8",
            },
        )
        fields["diff"] = new_field
        new_schema = model.RecordSchema(id="", fields=list(fields.values()))
        return new_schema

    def compute_make_subrecord(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, make_subrecord
        )
        subrec_name = self.src_ext.node.configuration.subrecname
        fields = []
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                fields.append(new_field)
        if subrec_name:
            new_field = model.FieldModel(
                name=subrec_name,
                type="string",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=32,
                    decimal_scale=0,
                    decimal_precision=0,
                    max_length=32,
                    is_signed=False,
                ),
                app_data={
                    "odbc_type": "CHAR",
                    "is_unicode_string": False,
                    "type_code": "STRING",
                },
            )
            fields.append(new_field)
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_make_vector(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, make_vector
        )
        col_name = self.src_ext.node.configuration.name
        fields = []
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                fields.append(new_field)
        if col_name:
            new_field = model.FieldModel(
                name=col_name,
                type="string",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=32,
                    decimal_scale=0,
                    decimal_precision=0,
                    max_length=32,
                    is_signed=False,
                    source_field_id=col_name,
                ),
                app_data={
                    "odbc_type": "CHAR",
                    "is_unicode_string": False,
                    "type_code": "STRING",
                },
            )
            fields.append(new_field)
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_sort(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, sort)
        fields = []
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                fields.append(new_field)
        key_change = (
            self.src_ext.node.configuration.flag_key.value
            if hasattr(self.src_ext.node.configuration.flag_key, "value")
            else self.src_ext.node.configuration.flag_key
        )
        cluster_key_change = (
            self.src_ext.node.configuration.flag_cluster.value
            if hasattr(self.src_ext.node.configuration.flag_cluster, "value")
            else self.src_ext.node.configuration.flag_cluster
        )
        if key_change == "flagKey":
            new_field = model.FieldModel(
                name="keyChange",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    max_length=0,
                    is_signed=True,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "TINYINT",
                    "is_unicode_string": False,
                    "type_code": "INT8",
                },
            )
            fields.append(new_field)
        if cluster_key_change == "flagCluster":
            new_field = model.FieldModel(
                name="clusterKeyChange",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    max_length=0,
                    is_signed=True,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "TINYINT",
                    "is_unicode_string": False,
                    "type_code": "INT8",
                },
            )
            fields.append(new_field)
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_surrogate_key_generator(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, surrogate_key_generator
        )
        fields = []
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                fields.append(new_field)
        col_name = self.src_ext.node.configuration.output_key
        if col_name:
            new_field = model.FieldModel(
                name=col_name,
                type="integer",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "BIGINT",
                    "is_unicode_string": False,
                    "type_code": "INT64",
                },
            )
            fields.append(new_field)
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_generic(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(self.src_ext.node.configuration, generic)
        ordering_list = self.src_ext.node.configuration.inputlink_ordering_list or []
        if not len(ordering_list):
            logger.warning(
                f"\nInput link ordering has not been set for generic stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
            )
            for i, input_node in enumerate(self.src_input_nodes):
                ordering_list.append({"link_label": f"{i}", "link_name": input_node.link.link.name})
            self.src_ext.node.configuration.inputlink_ordering_list = ordering_list
        fields = {}
        for i in range(len(self.src_input_nodes)):
            for link_order in ordering_list:
                if "link_label" in link_order and link_order["link_label"] == str(i):
                    for input_node in self.src_input_nodes:
                        if "link_name" in link_order and input_node.link.link.name == link_order["link_name"]:
                            for input_field in input_node.schema.schema.fields:
                                if input_field.name not in fields:
                                    new_field = model.FieldModel(
                                        name=input_field.name,
                                        type=input_field.type,
                                        metadata=input_field.metadata.copy(),
                                        nullable=input_field.nullable,
                                        app_data=input_field.app_data,
                                    )
                                    new_field.metadata.source_field_id = (
                                        f"{input_node.link.link.name}.{input_field.name}"
                                    )
                                    fields[input_field.name] = new_field

        new_schema = model.RecordSchema(id="", fields=list(fields.values()))
        return new_schema

    def compute_change_capture(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, change_capture
        )
        if len(self.src_input_nodes) != 2:
            logger.warning(
                f"\nChange capture stage {self.src_ext.node.label} does not have 2 inputs. Auto column metadata propagation can not be computed.\n",
            )
            return None
        first_link_name = None
        second_link_name = None
        if self.src_ext.node.configuration.inputlink_ordering_list is not None:
            for link in self.src_ext.node.configuration.inputlink_ordering_list:
                if "link_label" in link and link["link_label"].lower() == "before":
                    first_link_name = link["link_name"] if "link_name" in link else None
                elif "link_label" in link and link["link_label"].lower() == "after":
                    second_link_name = link["link_name"] if "link_name" in link else None
        if not first_link_name and not second_link_name:
            logger.warning(
                f"\nInput link ordering has not been set for change capture stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
            )
            # INFER FROM VALUE PROPERTIES?
            first_link_name = self.src_input_nodes[0].link.link.name
            second_link_name = self.src_input_nodes[1].link.link.name
        elif not first_link_name:
            for input_node in self.src_input_nodes:
                if input_node.link.link.name != second_link_name:
                    first_link_name = input_node.link.link.name
        elif not second_link_name:
            for input_node in self.src_input_nodes:
                if input_node.link.link.name != first_link_name:
                    second_link_name = input_node.link.link.name

        first_link_node = None
        second_link_node = None
        for input_node in self.src_input_nodes:
            if input_node.link.link.name == first_link_name:
                first_link_node = input_node.link.link
            if input_node.link.link.name == second_link_name:
                second_link_node = input_node.link.link

        if not first_link_node or not second_link_node:
            logger.warning(
                f"\nLink ordering assignment for change capture stage {self.src_ext.node.label} does not match link names\n",
            )
            return None

        value_properties = [val["value"] for val in self.src_ext.node.configuration.value_properties]
        fields = {}
        for input_field in second_link_node.schema.configuration.fields:
            new_field = model.FieldModel(
                name=input_field.name,
                type=input_field.type,
                metadata=input_field.metadata.copy(),
                nullable=input_field.nullable,
                app_data=input_field.app_data,
            )
            new_field.metadata.source_field_id = f"{first_link_name}.{input_field.name}"
            fields[input_field.name] = new_field

        for input_field in first_link_node.schema.configuration.fields:
            if input_field.name not in fields and input_field.name not in value_properties:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{first_link_name}.{input_field.name}"
                fields[input_field.name] = new_field

        col_name = self.src_ext.node.configuration.code_field or "change_code"
        new_field = model.FieldModel(
            name=col_name,
            type="integer",
            metadata=model.Metadata(
                is_key=False,
                min_length=0,
                decimal_scale=0,
                decimal_precision=0,
                max_length=0,
                is_signed=True,
            ),
            nullable=True,
            app_data={
                "odbc_type": "TINYINT",
                "is_unicode_string": False,
                "type_code": "INT8",
            },
        )
        fields[col_name] = new_field
        new_schema = model.RecordSchema(id="", fields=list(fields.values()))
        return new_schema

    def compute_change_apply(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, change_apply
        )
        if len(self.src_input_nodes) != 2:
            logger.warning(
                f"\nChange apply stage {self.src_ext.node.label} does not have 2 inputs. Auto column metadata propagation can not be computed.\n",
            )
            return None
        first_link_name = None
        second_link_name = None
        if self.src_ext.node.configuration.inputlink_ordering_list is not None:
            for link in self.src_ext.node.configuration.inputlink_ordering_list:
                if "link_label" in link and link["link_label"].lower() == "before":
                    first_link_name = link["link_name"] if "link_name" in link else None
                elif "link_label" in link and link["link_label"].lower() == "change":
                    second_link_name = link["link_name"] if "link_name" in link else None
        if not first_link_name and not second_link_name:
            logger.warning(
                f"\nInput link ordering has not been set for change apply stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
            )
            # INFER FROM VALUE PROPERTIES?
            first_link_name = self.src_input_nodes[0].link.link.name
            second_link_name = self.src_input_nodes[1].link.link.name
        elif not first_link_name:
            for input_node in self.src_input_nodes:
                if input_node.link.link.name != second_link_name:
                    first_link_name = input_node.link.link.name
        elif not second_link_name:
            for input_node in self.src_input_nodes:
                if input_node.link.link.name != first_link_name:
                    second_link_name = input_node.link.link.name

        first_link_node = None
        second_link_node = None
        for input_node in self.src_input_nodes:
            if input_node.link.link.name == first_link_name:
                first_link_node = input_node.link.link
            if input_node.link.link.name == second_link_name:
                second_link_node = input_node.link.link

        if not first_link_node or not second_link_node:
            logger.warning(
                f"\nLink ordering assignment for change apply stage {self.src_ext.node.label} does not match link names\n",
            )
            return None

        # NEED BETTER WAY TO INFER WHICH IS CHANGE CODE
        change_col = self.src_ext.node.configuration.code_field or "change_code"
        fields = []
        for input_field in second_link_node.schema.configuration.fields:
            if input_field.name != change_col:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{first_link_name}.{input_field.name}"
                fields.append(new_field)
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_complex_flat_file(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, complex_flat_file
        )
        output_columns = self.src_ext.node.configuration.output_columns or []
        found_link = False
        selected_columns = None
        for output_col in output_columns:
            if output_col.output_name == self.link.name:
                found_link = True
                selected_columns = output_col.output_columns
                break
        fields = []
        if found_link:
            for record in self.src_ext.node.configuration.records:
                for column in record.columns:
                    if column.name in selected_columns:
                        fields.append(column._to_output_field())
        else:
            for record in self.src_ext.node.configuration.records:
                for column in record.columns:
                    fields.append(column._to_output_field())

        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_address_verification(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, address_verification
        )
        parse_properties = self.src_ext.node.configuration.parse_properties
        error = False
        for parse_prop in parse_properties:
            if "error" in parse_prop and parse_prop["error"] == "On":
                error = True
        if error and self.src_ext.node.metadata["out_degree"] == 2:
            ordering_list = self.src_ext.node.configuration.outputlink_ordering_list
            if not len(ordering_list):
                logger.warning(
                    f"\nOutput link ordering has not been set for address verification stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
                )
                ordering_list.append({"link_label": "Output", "link_name": self.link.name})
            elif len(ordering_list) == 1:
                order = ordering_list[0]
                if "link_label" in order and order["link_label"] == "Output":
                    ordering_list.append({"link_label": "Error", "link_name": self.link.name})
                elif "link_label" in order and order["link_label"] == "Error":
                    ordering_list.append({"link_label": "Output", "link_name": self.link.name})
        if not error and self.src_ext.node.metadata["out_degree"] == 2:
            ordering_list = self.src_ext.node.configuration.outputlink_ordering_list
            if not len(ordering_list):
                logger.warning(
                    f"\nOutput link ordering has not been set for address verification stage {self.src_ext.node.label}. Link ordering will be randomly assigned.\n",
                )
                ordering_list.append({"link_label": "Output", "link_name": self.link.name})
            elif len(ordering_list) == 1:
                order = ordering_list[0]
                if "link_label" in order and order["link_label"] == "Output":
                    ordering_list.append({"link_label": "Unnamed 1", "link_name": self.link.name})
                elif "link_label" in order and order["link_label"] == "Unnamed 1":
                    ordering_list.append({"link_label": "Output", "link_name": self.link.name})
        if not error and self.src_ext.node.metadata["out_degree"] == 1:
            ordering_list = self.src_ext.node.configuration.outputlink_ordering_list
            if not len(ordering_list):
                ordering_list.append({"link_label": "Output", "link_name": self.link.name})

        error_link = False
        unnamed_link = False
        if error:
            ordering_list = self.src_ext.node.configuration.outputlink_ordering_list
            for order in ordering_list:
                if "link_name" in order and order["link_name"] == self.link.name:
                    if "link_label" in order and order["link_label"] == "Error":
                        error_link = True
                    if "link_label" in order and "unnamed" in order["link_label"].lower():
                        unnamed_link = True

        fields = []
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                fields.append(new_field)

        if error_link:
            new_field = model.FieldModel(
                name="ErrorCode_QSAV",
                type="integer",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_precision=0,
                    decimal_scale=0,
                    description="Error ID",
                    max_length=0,
                    is_signed=False,
                ),
                nullable=True,
                app_data={"odbc_type": "INTEGER", "type_code": "INT32"},
            )
            fields.append(new_field)

            new_field = model.FieldModel(
                name="ErrorMessage_QSAV",
                type="string",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=False,
                    decimal_precision=0,
                    decimal_scale=0,
                    description="Error message text that is associated with error ID",
                    max_length=200,
                    is_signed=False,
                ),
                nullable=True,
                app_data={
                    "odbc_type": "VARCHAR",
                    "is_unicode_string": True,
                    "type_code": "STRING",
                },
            )
            fields.append(new_field)

        elif not unnamed_link:
            column_data = [
                {
                    "name": "AccuracyCode_QSAV",
                    "description": "Code that describes validation status",
                    "max_length": 20,
                    "min_length": 0,
                },
                {
                    "name": "AddressQualityIndex_QSAV",
                    "description": "Address Quality Index to indicate quality of an address",
                    "max_length": 2,
                    "min_length": 0,
                },
                {
                    "name": "Organization_QSAV",
                    "description": "Business name for an address",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "Department_QSAV",
                    "description": "Department of an organization",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "Function_QSAV",
                    "description": "Job title or purpose",
                    "max_length": 60,
                    "min_length": 0,
                },
                {
                    "name": "Contact_QSAV",
                    "description": "Contact name",
                    "max_length": 60,
                    "min_length": 0,
                },
                {
                    "name": "Building_QSAV",
                    "description": "Name of a location",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "Subbuilding_QSAV",
                    "description": "Secondary name. Example: unit number",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "HouseNumber_QSAV",
                    "description": "House number of a location",
                    "max_length": 30,
                    "min_length": 0,
                },
                {
                    "name": "Street_QSAV",
                    "description": "Most common street or block data element",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DependentStreet_QSAV",
                    "description": "Dependent street or block data element",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "POBOX_QSAV",
                    "description": "Post box for an address",
                    "max_length": 30,
                    "min_length": 0,
                },
                {
                    "name": "Locality_QSAV",
                    "description": "Most common population center element. Example: city",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DependentLocality_QSAV",
                    "description": "Smaller population center element. Example: neighborhood",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DoubleDependentLocality_QSAV",
                    "description": "Smallest population center element. Example: village",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "PostCode_QSAV",
                    "description": "Complete postal code",
                    "max_length": 20,
                    "min_length": 0,
                },
                {
                    "name": "PostalCodePrimary_QSAV",
                    "description": "Primary postal code. Example: ZIP code",
                    "max_length": 10,
                    "min_length": 0,
                },
                {
                    "name": "PostalCodeSecondary_QSAV",
                    "description": "Secondary postal code. Example: ZIP+4",
                    "max_length": 10,
                    "min_length": 0,
                },
                {
                    "name": "SuperAdministrativeArea_QSAV",
                    "description": "Largest geographic unit",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "AdministrativeArea_QSAV",
                    "description": "Most common geographic unit. Example: province",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "SubAdministrativeArea_QSAV",
                    "description": "Smallest geographic unit. Example: county",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "Country_QSAV",
                    "description": "Official country name",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "ISO3166_2_QSAV",
                    "description": "2-character ISO country code",
                    "max_length": 10,
                    "min_length": 0,
                },
                {
                    "name": "ISO3166_3_QSAV",
                    "description": "3-character ISO country code",
                    "max_length": 10,
                    "min_length": 0,
                },
                {
                    "name": "ISO3166_N_QSAV",
                    "description": "3-digit ISO country code",
                    "max_length": 10,
                    "min_length": 0,
                },
                {
                    "name": "Address_QSAV",
                    "description": "Complete and formatted address",
                    "max_length": 1024,
                    "min_length": 0,
                },
                {
                    "name": "Residue_QSAV",
                    "description": "Information that was removed during processing",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DeliveryAddress1_QSAV",
                    "description": "First line of address for delivery",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DeliveryAddress2_QSAV",
                    "description": "Second line of address for delivery",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DeliveryAddress3_QSAV",
                    "description": "Third line of address for delivery",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DeliveryAddress4_QSAV",
                    "description": "Fourth line of address for delivery",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DeliveryAddress5_QSAV",
                    "description": "Fifth line of address for delivery",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DeliveryAddress6_QSAV",
                    "description": "Sixth line of address for delivery",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DeliveryAddress7_QSAV",
                    "description": "Seventh line of address for delivery",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "DeliveryAddress8_QSAV",
                    "description": "Eighth line of address for delivery",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "FormattedAddress1_QSAV",
                    "description": "First line of output address",
                    "max_length": 150,
                    "min_length": 0,
                },
                {
                    "name": "FormattedAddress2_QSAV",
                    "description": "Second line of output address",
                    "max_length": 150,
                    "min_length": 0,
                },
                {
                    "name": "FormattedAddress3_QSAV",
                    "description": "Third line of output address",
                    "max_length": 150,
                    "min_length": 0,
                },
                {
                    "name": "FormattedAddress4_QSAV",
                    "description": "Fourth line of output address",
                    "max_length": 150,
                    "min_length": 0,
                },
                {
                    "name": "FormattedAddress5_QSAV",
                    "description": "Fifth line of output address",
                    "max_length": 150,
                    "min_length": 0,
                },
                {
                    "name": "FormattedAddress6_QSAV",
                    "description": "Sixth line of output address",
                    "max_length": 150,
                    "min_length": 0,
                },
                {
                    "name": "FormattedAddress7_QSAV",
                    "description": "Seventh line of output address",
                    "max_length": 150,
                    "min_length": 0,
                },
                {
                    "name": "FormattedAddress8_QSAV",
                    "description": "Eighth line of output address",
                    "max_length": 150,
                    "min_length": 0,
                },
                {
                    "name": "FormattedAddress9_QSAV",
                    "description": "Ninth line of output address",
                    "max_length": 150,
                    "min_length": 0,
                },
                {
                    "name": "FormattedAddress10_QSAV",
                    "description": "Tenth line of output address",
                    "max_length": 150,
                    "min_length": 0,
                },
                {
                    "name": "AddressFormat_QSAV",
                    "description": "Schema for the address format based on components returned",
                    "max_length": 200,
                    "min_length": 0,
                },
                {
                    "name": "DeliveryAddress_QSAV",
                    "description": "Shows full address without Organization, Locality, AdministrativeArea and PostalCode",
                    "max_length": 200,
                    "min_length": 0,
                },
                {
                    "name": "DeliveryAddressFormat_QSAV",
                    "description": "Shows the composition of the DeliveryAddress field in elements",
                    "max_length": 200,
                    "min_length": 0,
                },
                {
                    "name": "LocalityExtra_QSAV",
                    "description": "Additional regional designation not contained in other Locality output fields",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "LocalitySpecial_QSAV",
                    "description": "Additional supplementary regional designation not contained in other Locality output fields",
                    "max_length": 50,
                    "min_length": 0,
                },
                {
                    "name": "PremiseExtra_QSAV",
                    "description": "Additional parsed non postal authority premise information",
                    "max_length": 50,
                    "min_length": 0,
                },
            ]
            for col_data in column_data:
                new_field = model.FieldModel(
                    name=col_data["name"],
                    type="string",
                    metadata=model.Metadata(
                        is_key=False,
                        min_length=col_data["min_length"],
                        decimal_scale=0,
                        decimal_precision=0,
                        description=col_data["description"],
                        max_length=col_data["max_length"],
                        is_signed=False,
                    ),
                    nullable=True,
                    app_data={
                        "odbc_type": "VARCHAR",
                        "is_unicode_string": True,
                        "type_code": "STRING",
                    },
                )
                fields.append(new_field)
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_investigate(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, investigate
        )
        fields = [
            model.FieldModel(
                name="qsInvColumnName",
                type="string",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    description="Investigate pattern report: input column name(s) being investigated",
                    max_length=0,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "VARCHAR",
                    "is_unicode_string": True,
                    "type_code": "STRING",
                },
            ),
            model.FieldModel(
                name="qsInvPattern",
                type="string",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    description="Investigate pattern report: generated format pattern",
                    max_length=0,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "VARCHAR",
                    "is_unicode_string": True,
                    "type_code": "STRING",
                },
            ),
            model.FieldModel(
                name="qsInvSample",
                type="string",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    description="Investigate pattern report: sample data value",
                    max_length=0,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "VARCHAR",
                    "is_unicode_string": True,
                    "type_code": "STRING",
                },
            ),
            model.FieldModel(
                name="qsInvCount",
                type="double",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    description="Investigate pattern token reports: frequency count of occurrences",
                    max_length=0,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "DOUBLE",
                    "is_unicode_string": True,
                    "type_code": "DFLOAT",
                },
            ),
            model.FieldModel(
                name="qsInvPercent",
                type="double",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    description="Investigate pattern report: frequency count of occurrences expressed as percentage of whole",
                    max_length=0,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "FLOAT",
                    "is_unicode_string": True,
                    "type_code": "SFLOAT",
                },
            ),
        ]
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_match_frequency(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, match_frequency
        )
        fields = [
            model.FieldModel(
                name="qsFreqValue",
                type="string",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    description="Frequency output: variable name or value",
                    max_length=0,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "VARCHAR",
                    "is_unicode_string": True,
                    "type_code": "STRING",
                },
            ),
            model.FieldModel(
                name="qsFreqCounts",
                type="string",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    description="Frequency output: frequency counts",
                    max_length=0,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "VARCHAR",
                    "is_unicode_string": True,
                    "type_code": "STRING",
                },
            ),
            model.FieldModel(
                name="qsFreqColumnID",
                type="integer",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    description="Frequency output: variable numeric identifier",
                    max_length=0,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "INTEGER",
                    "is_unicode_string": False,
                    "type_code": "INT32",
                },
            ),
            model.FieldModel(
                name="qsFreqHeaderFlag",
                type="integer",
                metadata=model.Metadata(
                    is_key=False,
                    min_length=0,
                    decimal_scale=0,
                    decimal_precision=0,
                    description="Frequency output: flag to indicate variable header record, or regular record",
                    max_length=0,
                    is_signed=False,
                ),
                nullable=False,
                app_data={
                    "odbc_type": "TINYINT",
                    "is_unicode_string": False,
                    "type_code": "INT8",
                },
            ),
        ]
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_standardize(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, standardize
        )
        from ibm_watsonx_data_integration.services.datastage.models.standarize_data import STANDARDIZE_DATA

        ruleset_props = self.src_ext.node.configuration.ruleset_properties
        fields = []
        for ruleset_prop in ruleset_props:
            if "ruleset" in ruleset_prop and ruleset_prop["ruleset"] in STANDARDIZE_DATA:
                for field_data in STANDARDIZE_DATA[ruleset_prop["ruleset"]]:
                    new_field = model.FieldModel(
                        name=field_data["name"],
                        type="string",
                        metadata=model.Metadata(
                            is_key=False,
                            min_length=0,
                            decimal_precision=0,
                            decimal_scale=0,
                            description=field_data["description"],
                            max_length=field_data["max_length"],
                            is_signed=False,
                        ),
                        nullable=True,
                        app_data={
                            "odbc_type": "VARCHAR",
                            "is_unicode_string": True,
                            "type_code": "STRING",
                        },
                    )
                    fields.append(new_field)
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_build_stage(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, build_stage
        )
        if (
            not hasattr(self.src_ext.node, "build_stage")
            or not self.src_ext.node.build_stage
            or not isinstance(self.src_ext.node.build_stage, BuildStage)
        ):
            return None
        if not len(self.src_ext.node.build_stage.outputs) > 0:
            return None
        num_output = len(self.src_ext.node.metadata["children"])
        ordering_list = self.src_ext.node.configuration.outputlink_ordering_list
        if not len(ordering_list):
            ordering_list.append(
                {
                    "link_name": self.link.name,
                    "link_label": self.src_ext.node.build_stage.outputs[0].port_name,
                }
            )
            self.src_ext.node.configuration.outputlink_ordering_list = ordering_list
        elif len(ordering_list) < num_output:
            for output in self.src_ext.node.build_stage.outputs:
                found = False
                for item in ordering_list:
                    if "link_label" in item and item["link_label"] == output.port_name:
                        found = True
                if not found:
                    ordering_list.append({"link_name": self.link.name, "link_label": output.port_name})
                    break
            self.src_ext.node.configuration.outputlink_ordering_list = ordering_list

        fields = []
        for order_item in ordering_list:
            if "link_name" in order_item and order_item["link_name"] == self.link.name:
                if "link_label" in order_item:
                    for output in self.src_ext.node.build_stage.outputs:
                        if output.port_name == order_item["link_label"]:
                            if isinstance(output.data_definition, DataDefinition):
                                fields = [field.configuration for field in output.data_definition._get_fields()]
                                break

        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_wrapped_stage(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, wrapped_stage
        )
        if (
            not hasattr(self.src_ext.node, "wrapped_stage")
            or not self.src_ext.node.wrapped_stage
            or not isinstance(self.src_ext.node.wrapped_stage, WrappedStage)
        ):
            return None
        if not len(self.src_ext.node.wrapped_stage.outputs) > 0:
            return None
        num_output = len(self.src_ext.node.metadata["children"])
        ordering_list = self.src_ext.node.configuration.outputlink_ordering_list
        if not len(ordering_list):
            ordering_list.append(
                {
                    "link_name": self.link.name,
                    "link_label": self.src_ext.node.wrapped_stage.outputs[0].port_name,
                }
            )
            self.src_ext.node.configuration.outputlink_ordering_list = ordering_list
        elif len(ordering_list) < num_output:
            for output in self.src_ext.node.wrapped_stage.outputs:
                found = False
                for item in ordering_list:
                    if "link_label" in item and item["link_label"] == output.port_name:
                        found = True
                if not found:
                    ordering_list.append({"link_name": self.link.name, "link_label": output.port_name})
                    break
            self.src_ext.node.configuration.outputlink_ordering_list = ordering_list

        fields = []
        for order_item in ordering_list:
            if "link_name" in order_item and order_item["link_name"] == self.link.name:
                if "link_label" in order_item:
                    for output in self.src_ext.node.wrapped_stage.outputs:
                        if output.port_name == order_item["link_label"]:
                            if isinstance(output.data_definition, DataDefinition):
                                fields = [field.configuration for field in output.data_definition._get_fields()]
                                break

        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_custom_stage(self):
        assert isinstance(self.src_ext.node, StageNode) and isinstance(
            self.src_ext.node.configuration, custom_stage
        )
        if (
            not hasattr(self.src_ext.node, "custom_stage")
            or not self.src_ext.node.custom_stage
            or not isinstance(self.src_ext.node.custom_stage, CustomStage)
        ):
            return None
        mapping_additions = self.src_ext.node.custom_stage.mapping_additions
        if not len(mapping_additions):
            return None

        col_data = {
            "string[n]": {
                "nullable": False,
                "metadata": {
                    "max_length": 100,
                    "min_length": 100,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": True,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": False,
                    "odbc_type": "CHAR",
                    "type_code": "STRING",
                    "time_scale": 0,
                },
                "type": "string",
            },
            "ustring[n]": {
                "nullable": False,
                "metadata": {
                    "max_length": 100,
                    "min_length": 100,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": False,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": True,
                    "odbc_type": "CHAR",
                    "type_code": "STRING",
                    "time_scale": 0,
                },
                "type": "string",
            },
            "string[max=n]": {
                "nullable": False,
                "metadata": {
                    "max_length": 100,
                    "min_length": 0,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": False,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": False,
                    "odbc_type": "VARCHAR",
                    "type_code": "STRING",
                    "time_scale": 0,
                },
                "type": "string",
            },
            "ustring[max=n]": {
                "nullable": False,
                "metadata": {
                    "max_length": 100,
                    "min_length": 0,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": False,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": True,
                    "odbc_type": "VARCHAR",
                    "type_code": "STRING",
                    "time_scale": 0,
                },
                "type": "string",
            },
            "int8": {
                "nullable": False,
                "metadata": {
                    "max_length": 6,
                    "min_length": 0,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": True,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": False,
                    "odbc_type": "TINYINT",
                    "type_code": "INT8",
                    "time_scale": 0,
                },
                "type": "integer",
            },
            "uint8": {
                "nullable": False,
                "metadata": {
                    "max_length": 6,
                    "min_length": 0,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": False,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": False,
                    "odbc_type": "TINYINT",
                    "type_code": "INT8",
                    "time_scale": 0,
                },
                "type": "integer",
            },
            "int16": {
                "nullable": False,
                "metadata": {
                    "max_length": 6,
                    "min_length": 0,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": True,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": False,
                    "odbc_type": "SMALLINT",
                    "type_code": "INT16",
                    "time_scale": 0,
                },
                "type": "integer",
            },
            "uint16": {
                "nullable": False,
                "metadata": {
                    "max_length": 6,
                    "min_length": 0,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": False,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": False,
                    "odbc_type": "SMALLINT",
                    "type_code": "INT16",
                    "time_scale": 0,
                },
                "type": "integer",
            },
            "int32": {
                "nullable": False,
                "metadata": {
                    "max_length": 6,
                    "min_length": 0,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": True,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": False,
                    "odbc_type": "INTEGER",
                    "type_code": "INT32",
                    "time_scale": 0,
                },
                "type": "integer",
            },
            "uint32": {
                "nullable": False,
                "metadata": {
                    "max_length": 6,
                    "min_length": 0,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": False,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": False,
                    "odbc_type": "INTEGER",
                    "type_code": "INT32",
                    "time_scale": 0,
                },
                "type": "integer",
            },
            "int64": {
                "nullable": False,
                "metadata": {
                    "max_length": 6,
                    "min_length": 0,
                    "decimal_precision": 0,
                    "decimal_scale": 0,
                    "is_key": False,
                    "is_signed": True,
                    "item_index": 0,
                    "description": "",
                },
                "app_data": {
                    "is_unicode_string": False,
                    "odbc_type": "BIGINT",
                    "type_code": "INT64",
                    "time_scale": 0,
                },
                "type": "integer",
            },
        }

        fields = []
        for mapping in mapping_additions:
            type = mapping.parallel_type.value if hasattr(mapping.parallel_type, "value") else mapping.parallel_type
            if type in col_data:
                field_data = col_data[type]
                field_data["name"] = mapping.column_name
                new_field = model.FieldModel(**field_data)
                fields.append(new_field)

        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_subflow(self):
        assert isinstance(self.src_ext.node, SuperNode)
        if not self.link.maps_from_link:
            return None
        input_link = self.link.maps_from_link

        fields = []
        for link in self.src_ext.node.subflow_dag.links():
            if link.name == input_link:
                for input_field in link.schema.configuration.fields:
                    new_field = model.FieldModel(
                        name=input_field.name,
                        type=input_field.type,
                        metadata=input_field.metadata.copy(),
                        nullable=input_field.nullable,
                        app_data=input_field.app_data,
                    )
                    fields.append(new_field)

        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema

    def compute_general(self):
        fields = []
        for input_node in self.src_input_nodes:
            for input_field in input_node.schema.schema.fields:
                new_field = model.FieldModel(
                    name=input_field.name,
                    type=input_field.type,
                    metadata=input_field.metadata.copy(),
                    nullable=input_field.nullable,
                    app_data=input_field.app_data,
                )
                new_field.metadata.source_field_id = f"{input_node.link.link.name}.{input_field.name}"
                fields.append(new_field)
        new_schema = model.RecordSchema(id="", fields=fields)
        return new_schema
