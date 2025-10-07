import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import JAVA_INTEGRATION
from pydantic import Field
from typing import ClassVar


class java_integration(BaseStage):

    op_name: ClassVar[str] = "JavaStagePX"
    node_type: ClassVar[str] = "execution_node"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/JavaStagePX.svg"
    label: ClassVar[str] = "Java Integration"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    # java_library: JavaLibrary = None
    # max_inputs: Optional[int] = -1
    # max_outputs: Optional[int] = -1
    # min_inputs: Optional[int] = 0
    # min_outputs: Optional[int] = 0
    # max_reject_outputs: Optional[int] = -1
    # min_reject_outputs: Optional[int] = 0
    # in_column_mapping: Optional[Dict[str, str]] = None
    # out_column_mapping: Optional[Dict[str, str]] = None
    # in_bean_class: Optional[Dict[str, str]] = None
    # out_bean_class: Optional[Dict[str, str]] = None
    abort_after_percent: int | None = Field(0, alias="abort_after_percent")
    asset_name: str | None = Field(None, alias="asset_name")
    auto_column_propagation: bool | None = Field(None, alias="auto_column_propagation")
    buf_free_run: int | None = Field(50, alias="buf_free_run")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode: JAVA_INTEGRATION.BufMode | None = Field(JAVA_INTEGRATION.BufMode.default, alias="buf_mode")
    buf_mode_ronly: JAVA_INTEGRATION.BufModeRonly | None = Field(
        JAVA_INTEGRATION.BufModeRonly.default, alias="buf_mode_ronly"
    )
    class_properties: list | None = Field([], alias="class_properties")
    classpath: str = Field(None, alias="classpath")
    coll_type: JAVA_INTEGRATION.CollType | None = Field(JAVA_INTEGRATION.CollType.auto, alias="coll_type")
    combinability: JAVA_INTEGRATION.Combinability | None = Field(
        JAVA_INTEGRATION.Combinability.auto, alias="combinability"
    )
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    custom_properties: str | None = Field(None, alias="custom_properties")
    disk_write_inc: int | None = Field(1048576, alias="disk_write_inc")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execmode: JAVA_INTEGRATION.Execmode | None = Field(JAVA_INTEGRATION.Execmode.default_par, alias="execmode")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    function_name: str = Field(None, alias="function_name")
    heap_size: int | None = Field(256, alias="heap_size")
    hide: bool | None = Field(False, alias="hide")
    in_column_mapping: str | None = Field(None, alias="in_column_mapping")
    in_custom_link_properties: str | None = Field(None, alias="in_custom_link_properties")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    is_reject_link: bool | None = Field(False, alias="is_reject_link")
    is_reject_output: bool | None = Field(False, alias="is_reject_output")
    key_col_select: JAVA_INTEGRATION.KeyColSelect | None = Field(
        JAVA_INTEGRATION.KeyColSelect.default, alias="keyColSelect"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    lookup_type: JAVA_INTEGRATION.LookupType | None = Field(JAVA_INTEGRATION.LookupType.empty, alias="lookup_type")
    max_mem_buf_size: int | None = Field(3145728, alias="max_mem_buf_size")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    other_options: str | None = Field(None, alias="other_options")
    out_column_mapping: str | None = Field(None, alias="out_column_mapping")
    out_custom_link_properties: str | None = Field(None, alias="out_custom_link_properties")
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
    part_type: JAVA_INTEGRATION.PartType | None = Field(JAVA_INTEGRATION.PartType.auto, alias="part_type")
    part_unique: bool | None = Field(None, alias="part_unique")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve: JAVA_INTEGRATION.Preserve | None = Field(JAVA_INTEGRATION.Preserve.default_propagate, alias="preserve")
    queue_upper_size: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    reject_condition_properties_option: JAVA_INTEGRATION.RejectConditionPropertiesOption | None = Field(
        None, alias="rejectConditionProperties_option"
    )
    reject_condition_row_rejected: bool | None = Field(False, alias="reject_condition_row_rejected")
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_from_link: int | None = Field(None, alias="reject_from_link")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_rows_properties_set: JAVA_INTEGRATION.RejectRowsPropertiesSet | None = Field(
        [], alias="rejectRowsPropertiesSet"
    )
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: JAVA_INTEGRATION.RejectUses | None = Field(JAVA_INTEGRATION.RejectUses.Rows, alias="reject_uses")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    stage_description: list | None = Field("", alias="stageDescription")
    user_class_name: str = Field(None, alias="user_class_name")
    user_defined_function: bool | None = Field(False, alias="user_defined_function")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("preserve") if (self.output_count and self.output_count > 0) else exclude.add("preserve")
        include.add("function_name") if (self.user_defined_function) else exclude.add("function_name")
        (
            include.add("custom_properties")
            if (((self.classpath)) and (not self.user_defined_function))
            else exclude.add("custom_properties")
        )
        (
            include.add("in_custom_link_properties")
            if (((self.classpath)) and (not self.user_defined_function))
            else exclude.add("in_custom_link_properties")
        )
        (
            include.add("is_reject_link")
            if (((self.classpath)) and (not self.user_defined_function) and (not self.is_reject_output))
            else exclude.add("is_reject_link")
        )
        (
            include.add("out_custom_link_properties")
            if (((self.classpath)) and (not self.user_defined_function) and (not self.is_reject_output))
            else exclude.add("out_custom_link_properties")
        )
        include.add("in_column_mapping") if (()) else exclude.add("in_column_mapping")
        (
            include.add("out_column_mapping")
            if ((()) and (not self.is_reject_output))
            else exclude.add("out_column_mapping")
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
        include.add("abort_after_percent") if (self.reject_uses == "Percent") else exclude.add("abort_after_percent")
        include.add("reject_threshold") if (self.reject_uses == "Percent") else exclude.add("reject_threshold")
        include.add("reject_number") if (self.reject_uses == "Rows") else exclude.add("reject_number")
        (
            include.add("reject_condition_properties_option")
            if (self.is_reject_output)
            else exclude.add("reject_condition_properties_option")
        )
        (
            include.add("reject_rows_properties_set")
            if (self.is_reject_output)
            else exclude.add("reject_rows_properties_set")
        )
        include.add("reject_uses") if (self.is_reject_output) else exclude.add("reject_uses")
        return include, exclude

    def get_input_ports_props(self, link: str = None) -> dict:
        include, exclude = self.validate()
        props = {"in_custom_link_properties", "runtime_column_propagation"}
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
        properties = self.model_dump(include=props - exclude, by_alias=True, exclude_none=True, warnings=False)
        if self.in_column_mapping:
            properties["in_column_mapping"] = self.in_column_mapping[link]
        if self.in_bean_class:
            properties["in_bean_class"] = self.in_bean_class[link]
        return properties

    def get_input_cardinality(self) -> dict:
        return {"min": self.min_inputs, "max": self.max_inputs}

    def get_output_ports_props(self, link: str = None) -> dict:
        include, exclude = self.validate()
        props = {
            "is_reject_link",
            "is_reject_output",
            "lookup_type",
            "out_custom_link_properties",
            "reject_condition_row_rejected",
            "reject_data_element_errorcode",
            "reject_data_element_errortext",
            "reject_from_link",
            "reject_number",
            "reject_threshold",
            "reject_uses",
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
        properties = self.model_dump(include=props - exclude, by_alias=True, exclude_none=True, warnings=False)
        if self.out_column_mapping:
            properties["out_column_mapping"] = self.out_column_mapping[link]
        if self.out_bean_class:
            properties["out_bean_class"] = self.out_bean_class[link]
        return properties

    def get_output_cardinality(self) -> dict:
        return {"min": self.min_outputs, "max": self.max_outputs}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "abort_after_percent",
            "asset_name",
            "auto_column_propagation",
            "buf_free_run",
            "buf_free_run_ronly",
            "buf_mode",
            "buf_mode_ronly",
            "class_properties",
            "classpath",
            "coll_type",
            "combinability",
            "current_output_link_type",
            "custom_properties",
            "disk_write_inc",
            "disk_write_inc_ronly",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execmode",
            "flow_dirty",
            "function_name",
            "heap_size",
            "hide",
            "in_bean_class",
            "in_column_mapping",
            "in_custom_link_properties",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "is_reject_link",
            "is_reject_output",
            "key_col_select",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "lookup_type",
            "max_mem_buf_size",
            "max_mem_buf_size_ronly",
            "other_options",
            "out_bean_class",
            "out_column_mapping",
            "out_custom_link_properties",
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
            "reject_condition_properties_option",
            "reject_from_link",
            "reject_number",
            "reject_rows_properties_set",
            "reject_threshold",
            "reject_uses",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "stage_description",
            "user_class_name",
            "user_defined_function",
        }
        required = {
            "classpath",
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "function_name",
            "output_acp_should_hide",
            "user_class_name",
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
                "SupportsRef": True,
                "maxRejectOutputs": self.max_reject_outputs,
                "minRejectOutputs": self.min_reject_outputs,
                "maxReferenceInputs": 0,
                "minReferenceInputs": 0,
            }
        }
