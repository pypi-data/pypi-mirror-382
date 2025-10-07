import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import XML_INPUT
from pydantic import Field
from typing import ClassVar


class xml_input(BaseStage):

    op_name: ClassVar[str] = "PxXMLInput"
    node_type: ClassVar[str] = "execution_node"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/XMLInputPX.svg"
    label: ClassVar[str] = "XML Input"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    accept_nulls: bool | None = Field(False, alias="accept_nulls")
    accept_nulls_output: bool | None = Field(False, alias="accept_nulls_output")
    auto_column_propagation: bool | None = Field(None, alias="auto_column_propagation")
    buf_free_run: int | None = Field(50, alias="buf_free_run")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode: XML_INPUT.BufMode | None = Field(XML_INPUT.BufMode.default, alias="buf_mode")
    buf_mode_ronly: XML_INPUT.BufModeRonly | None = Field(XML_INPUT.BufModeRonly.default, alias="buf_mode_ronly")
    coll_type: XML_INPUT.CollType | None = Field(XML_INPUT.CollType.auto, alias="coll_type")
    combinability: XML_INPUT.Combinability | None = Field(XML_INPUT.Combinability.auto, alias="combinability")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    discard_empty_values: bool | None = Field(False, alias="discard_empty_values")
    discard_empty_values_output: bool | None = Field(False, alias="discard_empty_values_output")
    disk_write_inc: int | None = Field(1048576, alias="disk_write_inc")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_grammar_caching: bool | None = Field(False, alias="enable_grammar_caching")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execmode: XML_INPUT.Execmode | None = Field(XML_INPUT.Execmode.default_seq, alias="execmode")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    format_serialized_chunks: bool | None = Field(False, alias="format_serialized_chunks")
    format_serialized_chunks_output: bool | None = Field(False, alias="format_serialized_chunks_output")
    heap_size: int | None = Field(256, alias="heap_size")
    hide: bool | None = Field(False, alias="hide")
    include_namespaces: bool | None = Field(False, alias="include_namespaces")
    include_namespaces_output: bool | None = Field(False, alias="include_namespaces_output")
    inherit_properties: bool | None = Field(False, alias="inherit_properties")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    is_icp4d: bool | None = Field(False, alias="isIcp4d")
    is_reject_link: bool | None = Field(False, alias="is_reject_link")
    key_col_select: XML_INPUT.KeyColSelect | None = Field(XML_INPUT.KeyColSelect.default, alias="keyColSelect")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    log_reject_errors: bool | None = Field(False, alias="log_reject_errors")
    max_mem_buf_size: int | None = Field(3145728, alias="max_mem_buf_size")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    namespace_declaration: str | None = Field("", alias="namespace_declaration")
    namespace_declaration_output: str | None = Field("", alias="namespace_declaration_output")
    other_options: str | None = Field(None, alias="other_options")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    part_client_dbname: str | None = Field(None, alias="part_client_dbname")
    part_client_instance: str | None = Field(None, alias="part_client_instance")
    part_dbconnection: str | None = Field("", alias="part_dbconnection")
    part_stable: bool | None = Field(None, alias="part_stable")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_table: str | None = Field(None, alias="part_table")
    part_type: XML_INPUT.PartType | None = Field(XML_INPUT.PartType.auto, alias="part_type")
    part_unique: bool | None = Field(None, alias="part_unique")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve: XML_INPUT.Preserve | None = Field(XML_INPUT.Preserve.default_propagate, alias="preserve")
    queue_upper_size: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    reject_message_column: XML_INPUT.RejectMessageColumn | None = Field(
        XML_INPUT.RejectMessageColumn.custom, alias="reject_message_column"
    )
    replace_nulls: bool | None = Field(False, alias="replace_nulls")
    replace_nulls_output: bool | None = Field(False, alias="replace_nulls_output")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    stage_description: list | None = Field("", alias="stageDescription")
    use_custom_xslt: bool | None = Field(False, alias="use_custom_xslt")
    validate_input: bool | None = Field(False, alias="validate_input")
    xml_source_column: XML_INPUT.XmlSourceColumn | None = Field(
        XML_INPUT.XmlSourceColumn.false, alias="xml_source_column"
    )
    xml_text: XML_INPUT.XmlText | None = Field(XML_INPUT.XmlText.URL, alias="xml_text")
    xml_validation_level: XML_INPUT.XmlValidationLevel | None = Field(
        XML_INPUT.XmlValidationLevel.default, alias="xml_validation_level"
    )
    xslt_error_mapping: XML_INPUT.XsltErrorMapping | None = Field(
        XML_INPUT.XsltErrorMapping.DS_FATAL, alias="xslt_error_mapping"
    )
    xslt_fatal_mapping: XML_INPUT.XsltFatalMapping | None = Field(
        XML_INPUT.XsltFatalMapping.DS_REJECT, alias="xslt_fatal_mapping"
    )
    xslt_source: XML_INPUT.XsltSource | None = Field(XML_INPUT.XsltSource.property, alias="xslt_source")
    xslt_stylesheet: str | None = Field("", alias="xslt_stylesheet")
    xslt_text: XML_INPUT.XsltText | None = Field(XML_INPUT.XsltText.URL, alias="xslt_text")
    xslt_warning_mapping: XML_INPUT.XsltWarningMapping | None = Field(
        XML_INPUT.XsltWarningMapping.DS_WARNING, alias="xslt_warning_mapping"
    )

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("xml_validation_level") if (self.validate_input) else exclude.add("xml_validation_level")
        (
            include.add("reject_message_column")
            if (self.is_reject_link)
            else exclude.add("reject_message_column")
        )
        include.add("preserve") if (self.output_count and self.output_count > 0) else exclude.add("preserve")
        include.add("max_mem_buf_size") if (self.buf_mode != "nobuffer") else exclude.add("max_mem_buf_size")
        include.add("buf_free_run") if (self.buf_mode != "nobuffer") else exclude.add("buf_free_run")
        include.add("queue_upper_size") if (self.buf_mode != "nobuffer") else exclude.add("queue_upper_size")
        include.add("disk_write_inc") if (self.buf_mode != "nobuffer") else exclude.add("disk_write_inc")

        (
            include.add("runtime_column_propagation")
            if (not self.enable_schemaless_design)
            else exclude.add("runtime_column_propagation")
        )
        (
            include.add("auto_column_propagation")
            if (not self.output_acp_should_hide)
            else exclude.add("auto_column_propagation")
        )
        (
            include.add("max_mem_buf_size_ronly")
            if (self.buf_mode_ronly != "nobuffer")
            else exclude.add("max_mem_buf_size_ronly")
        )
        (
            include.add("buf_free_run_ronly")
            if (self.buf_mode_ronly != "nobuffer")
            else exclude.add("buf_free_run_ronly")
        )
        (
            include.add("queue_upper_size_ronly")
            if (self.buf_mode_ronly != "nobuffer")
            else exclude.add("queue_upper_size_ronly")
        )
        (
            include.add("disk_write_inc_ronly")
            if (self.buf_mode_ronly != "nobuffer")
            else exclude.add("disk_write_inc_ronly")
        )
        (
            include.add("part_stable")
            if (
                ((self.show_part_type))
                and (self.part_type != "auto")
                and (self.part_type != "db2connector")
                and (self.show_sort_options)
            )
            else exclude.add("part_stable")
        )
        (
            include.add("part_unique")
            if (
                ((self.show_part_type))
                and (self.part_type != "auto")
                and (self.part_type != "db2connector")
                and (self.show_sort_options)
            )
            else exclude.add("part_unique")
        )
        (
            include.add("key_cols_part")
            if (
                (
                    ((self.show_part_type))
                    and ((not self.show_coll_type))
                    and ((self.part_type != "auto"))
                    and ((self.part_type != "db2connector"))
                    and ((self.part_type != "modulus"))
                )
                or (
                    ((self.show_part_type))
                    and (not self.show_coll_type)
                    and (self.part_type == "modulus")
                    and (self.perform_sort_modulus)
                )
            )
            else exclude.add("key_cols_part")
        )
        (
            include.add("part_dbconnection")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("part_dbconnection")
        )
        (
            include.add("part_client_dbname")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("part_client_dbname")
        )
        (
            include.add("part_client_instance")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("part_client_instance")
        )
        (
            include.add("part_table")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("part_table")
        )
        (
            include.add("perform_sort")
            if (((self.show_part_type)) and (((self.part_type == "hash")) or (self.part_type == "range")))
            else exclude.add("perform_sort")
        )
        (
            include.add("perform_sort_modulus")
            if (((self.show_part_type)) and (self.part_type == "modulus"))
            else exclude.add("perform_sort_modulus")
        )
        (
            include.add("key_col_select")
            if (
                ((self.show_part_type))
                and (self.part_type == "modulus")
                and (not self.perform_sort_modulus)
            )
            else exclude.add("key_col_select")
        )
        (
            include.add("sort_instructions")
            if (
                ((self.show_part_type))
                and (
                    ((self.part_type == "db2part"))
                    or (self.part_type == "entire")
                    or (self.part_type == "random")
                    or (self.part_type == "roundrobin")
                    or (self.part_type == "same")
                )
            )
            else exclude.add("sort_instructions")
        )
        (
            include.add("sort_instructions_text")
            if (
                ((self.show_part_type))
                and (
                    ((self.part_type == "db2part"))
                    or (self.part_type == "entire")
                    or (self.part_type == "random")
                    or (self.part_type == "roundrobin")
                    or (self.part_type == "same")
                )
            )
            else exclude.add("sort_instructions_text")
        )
        include.add("coll_type") if (self.show_coll_type) else exclude.add("coll_type")
        include.add("part_type") if (self.show_part_type) else exclude.add("part_type")
        (
            include.add("perform_sort_coll")
            if (
                (
                    ((self.show_coll_type))
                    and (
                        ((self.coll_type == "ordered"))
                        or ((self.coll_type == "roundrobin_coll"))
                        or ((self.coll_type == "sortmerge"))
                    )
                )
                or (((not self.show_part_type)) and (not self.show_coll_type))
            )
            else exclude.add("perform_sort_coll")
        )
        (
            include.add("key_cols_coll")
            if (
                ((self.show_coll_type))
                and (not self.show_part_type)
                and (self.coll_type != "auto")
                and (((self.coll_type == "sortmerge")) or (self.perform_sort_coll))
            )
            else exclude.add("key_cols_coll")
        )
        (
            include.add("key_cols_none")
            if (
                ((not self.show_part_type))
                and (not self.show_coll_type)
                and (self.perform_sort_coll)
            )
            else exclude.add("key_cols_none")
        )
        (
            include.add("part_stable_coll")
            if (
                (((self.perform_sort_coll)))
                and (
                    (
                        ((not self.show_part_type))
                        and ((self.show_coll_type))
                        and ((self.coll_type != "auto"))
                        and ((self.show_sort_options))
                    )
                    or (
                        ((not self.show_part_type))
                        and (not self.show_coll_type)
                        and (self.show_sort_options)
                    )
                )
            )
            else exclude.add("part_stable_coll")
        )
        (
            include.add("part_unique_coll")
            if (
                (((self.perform_sort_coll)))
                and (
                    (
                        ((not self.show_part_type))
                        and ((self.show_coll_type))
                        and ((self.coll_type != "auto"))
                        and ((self.show_sort_options))
                    )
                    or (
                        ((not self.show_part_type))
                        and (not self.show_coll_type)
                        and (self.show_sort_options)
                    )
                )
            )
            else exclude.add("part_unique_coll")
        )
        return include, exclude

    def get_input_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = {"runtime_column_propagation", "xml_source_column", "xml_text"}
        required = set()
        props = props & (self.model_fields_set | required)
        conflict = exclude & self.model_fields_set & props
        if conflict:
            conflict = list(conflict)
            if len(conflict) == 1:
                warnings.warn(f"\n\033[33mFound conflicting property: {conflict[0]}\033[0m")
            else:
                warnings.warn(
                    f'\n\033[33mFound conflicting properties: {", ".join(conflict[:-1])} and {conflict[-1]}\033[0m'
                )
        exclude = exclude - self.model_fields_set
        return self.model_dump(include=props - exclude, by_alias=True, exclude_none=True, warnings=False)

    def get_input_cardinality(self) -> dict:
        return {"min": 1, "max": 1}

    def get_output_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "accept_nulls_output",
            "discard_empty_values_output",
            "format_serialized_chunks_output",
            "include_namespaces_output",
            "inherit_properties",
            "is_reject_link",
            "namespace_declaration_output",
            "reject_message_column",
            "replace_nulls_output",
            "use_custom_xslt",
            "xslt_source",
            "xslt_stylesheet",
            "xslt_text",
        }
        required = set()
        props = props & (self.model_fields_set | required)
        conflict = exclude & self.model_fields_set & props
        if conflict:
            conflict = list(conflict)
            if len(conflict) == 1:
                warnings.warn(f"\n\033[33mFound conflicting property: {conflict[0]}\033[0m")
            else:
                warnings.warn(
                    f'\n\033[33mFound conflicting properties: {", ".join(conflict[:-1])} and {conflict[-1]}\033[0m'
                )
        exclude = exclude - self.model_fields_set
        return self.model_dump(include=props - exclude, by_alias=True, exclude_none=True, warnings=False)

    def get_output_cardinality(self) -> dict:
        return {"min": 1, "max": -1}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "accept_nulls",
            "accept_nulls_output",
            "auto_column_propagation",
            "buf_free_run",
            "buf_free_run_ronly",
            "buf_mode",
            "buf_mode_ronly",
            "coll_type",
            "combinability",
            "current_output_link_type",
            "discard_empty_values",
            "discard_empty_values_output",
            "disk_write_inc",
            "disk_write_inc_ronly",
            "enable_flow_acp_control",
            "enable_grammar_caching",
            "enable_schemaless_design",
            "execmode",
            "flow_dirty",
            "format_serialized_chunks",
            "format_serialized_chunks_output",
            "heap_size",
            "hide",
            "include_namespaces",
            "include_namespaces_output",
            "inherit_properties",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "is_icp4d",
            "is_reject_link",
            "key_col_select",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "log_reject_errors",
            "max_mem_buf_size",
            "max_mem_buf_size_ronly",
            "namespace_declaration",
            "namespace_declaration_output",
            "other_options",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "part_client_dbname",
            "part_client_instance",
            "part_dbconnection",
            "part_stable",
            "part_stable_coll",
            "part_stable_ordered",
            "part_stable_roundrobin_coll",
            "part_table",
            "part_type",
            "part_unique",
            "part_unique_coll",
            "part_unique_ordered",
            "part_unique_roundrobin_coll",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "preserve",
            "queue_upper_size",
            "queue_upper_size_ronly",
            "reject_message_column",
            "replace_nulls",
            "replace_nulls_output",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "stage_description",
            "use_custom_xslt",
            "validate_input",
            "xml_source_column",
            "xml_text",
            "xml_validation_level",
            "xslt_error_mapping",
            "xslt_fatal_mapping",
            "xslt_source",
            "xslt_stylesheet",
            "xslt_text",
            "xslt_warning_mapping",
        }
        required = {
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "output_acp_should_hide",
        }
        props = props & (self.model_fields_set | required)
        conflict = exclude & self.model_fields_set & props
        if conflict:
            conflict = list(conflict)
            if len(conflict) == 1:
                warnings.warn(f"\n\033[33mFound conflicting property {conflict[0]}\033[0m")
            else:
                warnings.warn(
                    f'\n\033[33mFound conflicting properties {", ".join(conflict[:-1])} and {conflict[-1]}\033[0m'
                )
        exclude = exclude - self.model_fields_set
        return self.model_dump(include=props - exclude, by_alias=True, exclude_none=True, warnings=False)

    def get_app_data_props(self) -> dict:
        return {
            "datastage": {
                "maxRejectOutputs": 0,
                "minRejectOutputs": 0,
                "maxReferenceInputs": 0,
                "minReferenceInputs": 0,
            }
        }
