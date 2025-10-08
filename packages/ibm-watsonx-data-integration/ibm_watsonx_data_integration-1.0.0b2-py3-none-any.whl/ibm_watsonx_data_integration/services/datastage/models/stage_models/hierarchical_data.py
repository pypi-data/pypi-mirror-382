import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import HIERARCHICAL_DATA
from pydantic import Field
from typing import ClassVar


class hierarchical_data(BaseStage):

    op_name: ClassVar[str] = "XMLStagePX"
    node_type: ClassVar[str] = "execution_node"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/XMLStagePX.svg"
    label: ClassVar[str] = "Hierarchical Data"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    auto_column_propagation: bool | None = Field(None, alias="auto_column_propagation")
    buf_free_run: int | None = Field(50, alias="buf_free_run")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode: HIERARCHICAL_DATA.BufMode | None = Field(HIERARCHICAL_DATA.BufMode.default, alias="buf_mode")
    buf_mode_ronly: HIERARCHICAL_DATA.BufModeRonly | None = Field(
        HIERARCHICAL_DATA.BufModeRonly.default, alias="buf_mode_ronly"
    )
    classpath: str | None = Field("", alias="Classpath")
    coll_type: HIERARCHICAL_DATA.CollType | None = Field(HIERARCHICAL_DATA.CollType.auto, alias="coll_type")
    column_properties: str | None = Field("", alias="column_properties")
    combinability: HIERARCHICAL_DATA.Combinability | None = Field(
        HIERARCHICAL_DATA.Combinability.auto, alias="combinability"
    )
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    debug_test_data: str | None = Field(None, alias="debug_test_data")
    disk_write_inc: int | None = Field(1048576, alias="disk_write_inc")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    e2_assembly: str | None = Field(None, alias="e2_assembly")
    e2_assembly_errors: int = Field(1, alias="e2_assembly_errors")
    e2_assembly_file: str | None = Field(None, alias="e2_assembly_file")
    e2_assembly_pipeline: str | None = Field("", alias="e2_assembly_pipeline")
    enable_disk_based: bool | None = Field(True, alias="enable_disk_based")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_logging: bool | None = Field(True, alias="enable_logging")
    enable_output_trigger_columns: bool | None = Field(False, alias="enable_output_trigger_columns")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    enable_split_data_into_batches: bool | None = Field(False, alias="enable_split_data_into_batches")
    execmode: HIERARCHICAL_DATA.Execmode | None = Field(HIERARCHICAL_DATA.Execmode.default_seq, alias="execmode")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    heap_size: int | None = Field(256, alias="heap_size")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    is_x_m_l_stage: bool | None = Field(True, alias="isXMLStage")
    key_col_select: HIERARCHICAL_DATA.KeyColSelect | None = Field(
        HIERARCHICAL_DATA.KeyColSelect.default, alias="keyColSelect"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    last_modified: str | None = Field(None, alias="last_modified")
    limit_output_rows: bool | None = Field(False, alias="limit_output_rows")
    log_level: HIERARCHICAL_DATA.LogLevel = Field(HIERARCHICAL_DATA.LogLevel.warning, alias="log_level")
    max_mem_buf_size: int | None = Field(3145728, alias="max_mem_buf_size")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    max_num_output_rows: int = Field(None, alias="max_num_output_rows")
    maximum_stack_size: int | None = Field(256, alias="maximum_stack_size")
    num_assembly_threads: int = Field(1, alias="num_assembly_threads")
    open_sub_canvas: bool | None = Field(False, alias="openSubCanvas")
    other_options: str | None = Field("", alias="OtherOptions")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    output_row_trigger_column: str | None = Field(None, alias="output_row_trigger_column")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    params: str | None = Field(None, alias="params")
    part_client_dbname: str | None = Field(None, alias="part_client_dbname")
    part_client_instance: str | None = Field(None, alias="part_client_instance")
    part_dbconnection: str | None = Field("", alias="part_dbconnection")
    part_stable: bool | None = Field(None, alias="part_stable")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_table: str | None = Field(None, alias="part_table")
    part_type: HIERARCHICAL_DATA.PartType | None = Field(HIERARCHICAL_DATA.PartType.auto, alias="part_type")
    part_unique: bool | None = Field(None, alias="part_unique")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve: HIERARCHICAL_DATA.Preserve | None = Field(
        HIERARCHICAL_DATA.Preserve.default_propagate, alias="preserve"
    )
    queue_upper_size: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    security_info: str = Field(None, alias="security_info")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    split_batch_key: str = Field(None, alias="split_batch_key")
    split_batch_key_value_order: HIERARCHICAL_DATA.SplitBatchKeyValueOrder = Field(
        HIERARCHICAL_DATA.SplitBatchKeyValueOrder.ascending, alias="split_batch_key_value_order"
    )
    stage_description: list | None = Field("", alias="stageDescription")
    stage_type: str = Field("XMLStage", alias="stage_type")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("preserve") if (self.output_count and self.output_count > 0) else exclude.add("preserve")
        include.add("log_level") if (self.enable_logging) else exclude.add("log_level")
        (
            include.add("max_num_output_rows")
            if (self.limit_output_rows)
            else exclude.add("max_num_output_rows")
        )
        (
            include.add("split_batch_key")
            if (self.enable_split_data_into_batches)
            else exclude.add("split_batch_key")
        )
        (
            include.add("split_batch_key_value_order")
            if (self.enable_split_data_into_batches)
            else exclude.add("split_batch_key_value_order")
        )
        (
            include.add("output_row_trigger_column")
            if (self.enable_output_trigger_columns)
            else exclude.add("output_row_trigger_column")
        )
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
        props = {"runtime_column_propagation"}
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
        return {"min": 0, "max": -1}

    def get_output_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = set()
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
        return {"min": 0, "max": -1}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "auto_column_propagation",
            "buf_free_run",
            "buf_free_run_ronly",
            "buf_mode",
            "buf_mode_ronly",
            "classpath",
            "coll_type",
            "column_properties",
            "combinability",
            "current_output_link_type",
            "debug_test_data",
            "disk_write_inc",
            "disk_write_inc_ronly",
            "e2_assembly",
            "e2_assembly_errors",
            "e2_assembly_file",
            "e2_assembly_pipeline",
            "enable_disk_based",
            "enable_flow_acp_control",
            "enable_logging",
            "enable_output_trigger_columns",
            "enable_schemaless_design",
            "enable_split_data_into_batches",
            "execmode",
            "flow_dirty",
            "heap_size",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "is_x_m_l_stage",
            "key_col_select",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "last_modified",
            "limit_output_rows",
            "log_level",
            "max_mem_buf_size",
            "max_mem_buf_size_ronly",
            "max_num_output_rows",
            "maximum_stack_size",
            "num_assembly_threads",
            "open_sub_canvas",
            "other_options",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "output_row_trigger_column",
            "outputcol_properties",
            "params",
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
            "runtime_column_propagation",
            "security_info",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "split_batch_key",
            "split_batch_key_value_order",
            "stage_description",
            "stage_type",
        }
        required = {
            "current_output_link_type",
            "e2_assembly_errors",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "log_level",
            "max_num_output_rows",
            "num_assembly_threads",
            "output_acp_should_hide",
            "split_batch_key",
            "split_batch_key_value_order",
            "stage_type",
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
                "active": 0,
                "SupportsRef": False,
                "maxRejectOutputs": 0,
                "minRejectOutputs": 0,
                "maxReferenceInputs": 0,
                "minReferenceInputs": 0,
            }
        }
