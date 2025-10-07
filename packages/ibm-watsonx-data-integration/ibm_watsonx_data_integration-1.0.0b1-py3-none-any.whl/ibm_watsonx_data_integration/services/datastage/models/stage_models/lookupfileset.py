import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import LOOKUPFILESET
from pydantic import Field
from typing import ClassVar


class lookupfileset(BaseStage):

    op_name: ClassVar[str] = "PxLookupFileSet"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/PxLookupFileSet.svg"
    label: ClassVar[str] = "Lookup file set"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    allow_dups: LOOKUPFILESET.AllowDups | None = Field(LOOKUPFILESET.AllowDups.false, alias="allow_dups")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: LOOKUPFILESET.BufModeRonly | None = Field(
        LOOKUPFILESET.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: LOOKUPFILESET.BufferingMode | None = Field(LOOKUPFILESET.BufferingMode.default, alias="buf_mode")
    collecting: LOOKUPFILESET.Collecting | None = Field(LOOKUPFILESET.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: LOOKUPFILESET.CombinabilityMode | None = Field(
        LOOKUPFILESET.CombinabilityMode.auto, alias="combinability"
    )
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_asset_name: str = Field(None, alias="dataAssetName")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    diskpool: str | None = Field(None, alias="diskpool")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execution_mode: LOOKUPFILESET.ExecutionMode | None = Field(
        LOOKUPFILESET.ExecutionMode.default_par, alias="execmode"
    )
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    key_high: str | None = Field("", alias="keyHigh")
    key_high_ci_cs: LOOKUPFILESET.KeyHighCiCs | None = Field(LOOKUPFILESET.KeyHighCiCs.cs, alias="keyHigh-ci-cs")
    key_high_keep: LOOKUPFILESET.KeyHighKeep | None = Field(LOOKUPFILESET.KeyHighKeep.false, alias="keyHigh-keep")
    key_low: str | None = Field("", alias="keyLow")
    key_low_ci_cs: LOOKUPFILESET.KeyLowCiCs | None = Field(LOOKUPFILESET.KeyLowCiCs.cs, alias="keyLow-ci-cs")
    key_low_keep: LOOKUPFILESET.KeyLowKeep | None = Field(LOOKUPFILESET.KeyLowKeep.false, alias="keyLow-keep")
    key_ordered: str | None = Field("", alias="keyOrdered")
    key_ordered_ci_cs: LOOKUPFILESET.KeyOrderedCiCs | None = Field(
        LOOKUPFILESET.KeyOrderedCiCs.cs, alias="keyOrdered-ci-cs"
    )
    key_ordered_keep: LOOKUPFILESET.KeyOrderedKeep | None = Field(
        LOOKUPFILESET.KeyOrderedKeep.false, alias="keyOrdered-keep"
    )
    key_properties: list | None = Field([], alias="keyProperties")
    lookup_file_set: str = Field(None, alias="fileset")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    partition_type: LOOKUPFILESET.PartitionType | None = Field(LOOKUPFILESET.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    range: LOOKUPFILESET.Range | None = Field(LOOKUPFILESET.Range.false, alias="range")
    register_data_asset: bool | None = Field(False, alias="registerDataAsset")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    save: str = Field(None, alias="save")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: LOOKUPFILESET.KeyColSelect | None = Field(LOOKUPFILESET.KeyColSelect.default, alias="keyColSelect")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    table: str = Field("table", alias="table")
    unique: bool | None = Field(None, alias="part_unique")

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("key_low") if (()) else exclude.add("key_low")
        include.add("key_high") if (()) else exclude.add("key_high")
        include.add("key_ordered") if (()) else exclude.add("key_ordered")
        include.add("diskpool") if (()) else exclude.add("diskpool")

        include.add("key_ordered") if (((self.range == "range")) and (())) else exclude.add("key_ordered")
        include.add("key_ordered_keep") if (((self.range == "range")) and (())) else exclude.add("key_ordered_keep")
        include.add("key_ordered_ci_cs") if (((self.range == "range")) and (())) else exclude.add("key_ordered_ci_cs")
        include.add("key_low") if (()) else exclude.add("key_low")
        include.add("key_low_keep") if (()) else exclude.add("key_low_keep")
        include.add("key_low_ci_cs") if (()) else exclude.add("key_low_ci_cs")
        include.add("key_high") if (()) else exclude.add("key_high")
        include.add("key_high_keep") if (()) else exclude.add("key_high_keep")
        include.add("key_high_ci_cs") if (()) else exclude.add("key_high_ci_cs")
        (
            include.add("key_high")
            if (((self.range == "range")) and (()) and (not self.key_ordered))
            else exclude.add("key_high")
        )
        (
            include.add("key_high_keep")
            if (((self.range == "range")) and (()) and (not self.key_ordered))
            else exclude.add("key_high_keep")
        )
        (
            include.add("key_high_ci_cs")
            if (((self.range == "range")) and (()) and (not self.key_ordered))
            else exclude.add("key_high_ci_cs")
        )
        (
            include.add("key_low")
            if (((self.range == "range")) and (()) and (not self.key_ordered))
            else exclude.add("key_low")
        )
        (
            include.add("key_low_keep")
            if (((self.range == "range")) and (()) and (not self.key_ordered))
            else exclude.add("key_low_keep")
        )
        (
            include.add("key_low_ci_cs")
            if (((self.range == "range")) and (()) and (not self.key_ordered))
            else exclude.add("key_low_ci_cs")
        )
        include.add("data_asset_name") if (self.register_data_asset) else exclude.add("data_asset_name")
        (
            include.add("maximum_memory_buffer_size_bytes")
            if (self.buffering_mode != "nobuffer")
            else exclude.add("maximum_memory_buffer_size_bytes")
        )
        (
            include.add("buffer_free_run_percent")
            if (self.buffering_mode != "nobuffer")
            else exclude.add("buffer_free_run_percent")
        )
        (
            include.add("queue_upper_bound_size_bytes")
            if (self.buffering_mode != "nobuffer")
            else exclude.add("queue_upper_bound_size_bytes")
        )
        (
            include.add("disk_write_increment_bytes")
            if (self.buffering_mode != "nobuffer")
            else exclude.add("disk_write_increment_bytes")
        )
        (
            include.add("runtime_column_propagation")
            if (not self.enable_schemaless_design)
            else exclude.add("runtime_column_propagation")
        )
        (
            include.add("column_metadata_change_propagation")
            if (not self.output_acp_should_hide)
            else exclude.add("column_metadata_change_propagation")
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
            include.add("stable")
            if (
                ((self.show_part_type))
                and (self.partition_type != "auto")
                and (self.partition_type != "db2connector")
                and (self.show_sort_options)
            )
            else exclude.add("stable")
        )
        (
            include.add("unique")
            if (
                ((self.show_part_type))
                and (self.partition_type != "auto")
                and (self.partition_type != "db2connector")
                and (self.show_sort_options)
            )
            else exclude.add("unique")
        )
        (
            include.add("key_cols_part")
            if (
                (
                    ((self.show_part_type))
                    and ((not self.show_coll_type))
                    and ((self.partition_type != "auto"))
                    and ((self.partition_type != "db2connector"))
                    and ((self.partition_type != "modulus"))
                )
                or (
                    ((self.show_part_type))
                    and (not self.show_coll_type)
                    and (self.partition_type == "modulus")
                    and (self.perform_sort_modulus)
                )
            )
            else exclude.add("key_cols_part")
        )
        (
            include.add("db2_source_connection_required")
            if (((self.partition_type == "db2part")) and (self.show_part_type))
            else exclude.add("db2_source_connection_required")
        )
        (
            include.add("db2_database_name")
            if (((self.partition_type == "db2part")) and (self.show_part_type))
            else exclude.add("db2_database_name")
        )
        (
            include.add("db2_instance_name")
            if (((self.partition_type == "db2part")) and (self.show_part_type))
            else exclude.add("db2_instance_name")
        )
        (
            include.add("db2_table_name")
            if (((self.partition_type == "db2part")) and (self.show_part_type))
            else exclude.add("db2_table_name")
        )
        (
            include.add("perform_sort")
            if (
                ((self.show_part_type))
                and (((self.partition_type == "hash")) or (self.partition_type == "range"))
            )
            else exclude.add("perform_sort")
        )
        (
            include.add("perform_sort_modulus")
            if (((self.show_part_type)) and (self.partition_type == "modulus"))
            else exclude.add("perform_sort_modulus")
        )
        (
            include.add("sorting_key")
            if (
                ((self.show_part_type))
                and (self.partition_type == "modulus")
                and (not self.perform_sort_modulus)
            )
            else exclude.add("sorting_key")
        )
        (
            include.add("sort_instructions")
            if (
                ((self.show_part_type))
                and (
                    ((self.partition_type == "db2part"))
                    or (self.partition_type == "entire")
                    or (self.partition_type == "random")
                    or (self.partition_type == "roundrobin")
                    or (self.partition_type == "same")
                )
            )
            else exclude.add("sort_instructions")
        )
        (
            include.add("sort_instructions_text")
            if (
                ((self.show_part_type))
                and (
                    ((self.partition_type == "db2part"))
                    or (self.partition_type == "entire")
                    or (self.partition_type == "random")
                    or (self.partition_type == "roundrobin")
                    or (self.partition_type == "same")
                )
            )
            else exclude.add("sort_instructions_text")
        )
        include.add("collecting") if (self.show_coll_type) else exclude.add("collecting")
        include.add("partition_type") if (self.show_part_type) else exclude.add("partition_type")
        (
            include.add("perform_sort_coll")
            if (
                (
                    ((self.show_coll_type))
                    and (
                        ((self.collecting == "ordered"))
                        or ((self.collecting == "roundrobin_coll"))
                        or ((self.collecting == "sortmerge"))
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
                and (self.collecting != "auto")
                and (((self.collecting == "sortmerge")) or (self.perform_sort_coll))
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
                        and ((self.collecting != "auto"))
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
                        and ((self.collecting != "auto"))
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
        (
            include.add("key_high")
            if (((self.range == "range")) and (()) and (not self.key_ordered))
            else exclude.add("key_high")
        )
        (
            include.add("key_high_keep")
            if (((self.range == "range")) and (()) and (not self.key_ordered))
            else exclude.add("key_high_keep")
        )
        (
            include.add("key_low")
            if (((self.range == "range")) and (()) and (not self.key_ordered))
            else exclude.add("key_low")
        )
        (
            include.add("key_low_keep")
            if (((self.range == "range")) and (()) and (not self.key_ordered))
            else exclude.add("key_low_keep")
        )
        (
            include.add("key_ordered")
            if (
                (((self.range == "range")) and (()) and ((not self.key_low)))
                and (((self.range == "range")) and (()) and (not self.key_high))
            )
            else exclude.add("key_ordered")
        )
        (
            include.add("key_ordered_keep")
            if (
                (((self.range == "range")) and (()) and ((not self.key_low)))
                and (((self.range == "range")) and (()) and (not self.key_high))
            )
            else exclude.add("key_ordered_keep")
        )
        (
            include.add("key_low_ci_cs")
            if ((()) and (()) and (not self.key_ordered) and (self.range == "range"))
            else exclude.add("key_low_ci_cs")
        )
        (
            include.add("key_high_ci_cs")
            if ((()) and (()) and (not self.key_ordered) and (self.range == "range"))
            else exclude.add("key_high_ci_cs")
        )
        (
            include.add("key_ordered_ci_cs")
            if (
                ((()) and (()) and ((not self.key_high)) and ((self.range == "range")))
                and ((()) and (()) and (not self.key_low))
            )
            else exclude.add("key_ordered_ci_cs")
        )
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        return include, exclude

    def get_input_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "additional_properties_set_option",
            "additional_properties_set_target",
            "allow_dups",
            "data_asset_name",
            "diskpool",
            "key_high",
            "key_high_ci_cs",
            "key_high_keep",
            "key_low",
            "key_low_ci_cs",
            "key_low_keep",
            "key_ordered",
            "key_ordered_ci_cs",
            "key_ordered_keep",
            "key_properties",
            "range",
            "register_data_asset",
            "runtime_column_propagation",
            "save",
            "table",
        }
        required = {"data_asset_name", "save", "table"}
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
        return {"min": 0, "max": 1}

    def get_output_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = {"lookup_file_set"}
        required = {"lookup_file_set"}
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
        return {"min": 0, "max": 1}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execution_mode",
            "flow_dirty",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "lookup_file_set",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "part_stable_coll",
            "part_stable_ordered",
            "part_stable_roundrobin_coll",
            "part_unique_coll",
            "part_unique_ordered",
            "part_unique_roundrobin_coll",
            "partition_type",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "unique",
        }
        required = {
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "lookup_file_set",
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

    def get_target_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execution_mode",
            "flow_dirty",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "lookup_file_set",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "part_stable_coll",
            "part_stable_ordered",
            "part_stable_roundrobin_coll",
            "part_unique_coll",
            "part_unique_ordered",
            "part_unique_roundrobin_coll",
            "partition_type",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "unique",
        }
        required = {
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "lookup_file_set",
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
