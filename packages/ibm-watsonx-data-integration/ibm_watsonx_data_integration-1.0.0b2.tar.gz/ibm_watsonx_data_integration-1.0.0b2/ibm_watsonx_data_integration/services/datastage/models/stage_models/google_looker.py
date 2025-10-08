import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.google_looker_connection import GoogleLookerConn
from ibm_watsonx_data_integration.services.datastage.models.enums import GOOGLE_LOOKER
from pydantic import Field
from typing import ClassVar


class google_looker(BaseStage):

    op_name: ClassVar[str] = "looker"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/looker.svg"
    label: ClassVar[str] = "Google Looker"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: GoogleLookerConn = GoogleLookerConn()
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: GOOGLE_LOOKER.BufModeRonly | None = Field(
        GOOGLE_LOOKER.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: GOOGLE_LOOKER.BufferingMode | None = Field(GOOGLE_LOOKER.BufferingMode.default, alias="buf_mode")
    byte_limit: str | None = Field(None, alias="byte_limit")
    cell_range: str | None = Field(None, alias="range")
    collecting: GOOGLE_LOOKER.Collecting | None = Field(GOOGLE_LOOKER.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: GOOGLE_LOOKER.CombinabilityMode | None = Field(
        GOOGLE_LOOKER.CombinabilityMode.auto, alias="combinability"
    )
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execution_mode: GOOGLE_LOOKER.ExecutionMode | None = Field(
        GOOGLE_LOOKER.ExecutionMode.default_par, alias="execmode"
    )
    file_format: GOOGLE_LOOKER.FileFormat | None = Field(GOOGLE_LOOKER.FileFormat.csv, alias="file_format")
    file_name: str = Field(None, alias="file_name")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    hide: bool | None = Field(False, alias="hide")
    infer_as_varchar: bool | None = Field(None, alias="infer_as_varchar")
    infer_null_as_empty_string: bool | None = Field(False, alias="infer_null_as_empty_string")
    infer_record_count: int | None = Field(1000, alias="infer_record_count")
    infer_schema: bool | None = Field(None, alias="infer_schema")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    invalid_data_handling: GOOGLE_LOOKER.InvalidDataHandling | None = Field(
        GOOGLE_LOOKER.InvalidDataHandling.fail, alias="invalid_data_handling"
    )
    json_infer_record_count: int | None = Field(None, alias="json_infer_record_count")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(1, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    partition_type: GOOGLE_LOOKER.PartitionType | None = Field(GOOGLE_LOOKER.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: GOOGLE_LOOKER.PreservePartitioning | None = Field(
        GOOGLE_LOOKER.PreservePartitioning.default_propagate, alias="preserve"
    )
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    read_mode: GOOGLE_LOOKER.ReadMode | None = Field(GOOGLE_LOOKER.ReadMode.read_single, alias="read_mode")
    row_limit: int | None = Field(None, alias="row_limit")
    row_start: int | None = Field(None, alias="row_start")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: GOOGLE_LOOKER.KeyColSelect | None = Field(GOOGLE_LOOKER.KeyColSelect.default, alias="keyColSelect")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    store_shared_strings_in_the_temporary_file: bool | None = Field(None, alias="use_sst_temp_file")
    type_mapping: str | None = Field(None, alias="type_mapping")
    unique: bool | None = Field(None, alias="part_unique")
    use_4_digit_years_in_date_formats: bool | None = Field(None, alias="use_4_digit_year")
    worksheet_name: str | None = Field(None, alias="sheet_name")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("preserve_partitioning")
            if (self.output_count and self.output_count > 0)
            else exclude.add("preserve_partitioning")
        )
        (
            include.add("store_shared_strings_in_the_temporary_file")
            if (
                (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                            or (self.file_format == "excel")
                        )
                    )
                )
                or (

                        self.file_format
                        and (
                            (
                                hasattr(self.file_format, "value")
                                and self.file_format.value
                                and "#" in str(self.file_format.value)
                            )
                            or ("#" in str(self.file_format))
                        )

                )
            )
            else exclude.add("store_shared_strings_in_the_temporary_file")
        )
        (
            include.add("type_mapping")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (((self.infer_schema)) or (self.infer_schema and "#" in str(self.infer_schema)))

            )
            else exclude.add("type_mapping")
        )
        (
            include.add("invalid_data_handling")
            if (
                (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                            or (self.file_format == "csv")
                        )
                    )
                )
                or (

                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                            or (self.file_format == "delimited")
                        )

                )
                or (

                        self.file_format
                        and (
                            (
                                hasattr(self.file_format, "value")
                                and self.file_format.value
                                and "#" in str(self.file_format.value)
                            )
                            or ("#" in str(self.file_format))
                        )

                )
            )
            else exclude.add("invalid_data_handling")
        )
        (
            include.add("use_4_digit_years_in_date_formats")
            if (
                (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                            or (self.file_format == "excel")
                        )
                    )
                )
                or (

                        self.file_format
                        and (
                            (
                                hasattr(self.file_format, "value")
                                and self.file_format.value
                                and "#" in str(self.file_format.value)
                            )
                            or ("#" in str(self.file_format))
                        )

                )
            )
            else exclude.add("use_4_digit_years_in_date_formats")
        )

        include.add("infer_as_varchar") if (()) else exclude.add("infer_as_varchar")
        include.add("infer_schema") if (()) else exclude.add("infer_schema")
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
                    (
                        ((self.show_part_type))
                        and ((not self.show_coll_type))
                        and ((self.partition_type != "auto"))
                        and ((self.partition_type != "db2connector"))
                        and ((self.partition_type != "modulus"))
                    )
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
                    (
                        ((self.show_coll_type))
                        and (
                            ((self.collecting == "ordered"))
                            or ((self.collecting == "roundrobin_coll"))
                            or ((self.collecting == "sortmerge"))
                        )
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
                            (
                                ((not self.show_part_type))
                                and ((self.show_coll_type))
                                and ((self.collecting != "auto"))
                                and ((self.show_sort_options))
                            )
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
                            (
                                ((not self.show_part_type))
                                and ((self.show_coll_type))
                                and ((self.collecting != "auto"))
                                and ((self.show_sort_options))
                            )
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
        include.add("defer_credentials") if (()) else exclude.add("defer_credentials")
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("store_shared_strings_in_the_temporary_file")
            if (



                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                or (self.file_format == "excel")
                            )



            )
            else exclude.add("store_shared_strings_in_the_temporary_file")
        )
        (
            include.add("type_mapping")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                )
                and (self.infer_schema)
            )
            else exclude.add("type_mapping")
        )
        (
            include.add("invalid_data_handling")
            if (

                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )

                    )

            )
            else exclude.add("invalid_data_handling")
        )
        (
            include.add("use_4_digit_years_in_date_formats")
            if (



                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                or (self.file_format == "excel")
                            )



            )
            else exclude.add("use_4_digit_years_in_date_formats")
        )
        (
            include.add("invalid_data_handling")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
            )
            else exclude.add("invalid_data_handling")
        )
        (
            include.add("type_mapping")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
            )
            and (self.infer_schema == "true" or self.infer_schema)
            else exclude.add("type_mapping")
        )
        (
            include.add("store_shared_strings_in_the_temporary_file")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "excel" in str(self.file_format.value)
                    )
                    or ("excel" in str(self.file_format))
                )
            )
            else exclude.add("store_shared_strings_in_the_temporary_file")
        )
        (
            include.add("infer_as_varchar")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "json" in str(self.file_format.value)
                    )
                    or ("json" in str(self.file_format))
                )
            )
            and (self.infer_schema == "true" or self.infer_schema)
            and (self.type_mapping != "true" or not self.type_mapping)
            else exclude.add("infer_as_varchar")
        )
        (
            include.add("use_4_digit_years_in_date_formats")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "excel" in str(self.file_format.value)
                    )
                    or ("excel" in str(self.file_format))
                )
            )
            else exclude.add("use_4_digit_years_in_date_formats")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "byte_limit",
            "cell_range",
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
            "file_format",
            "file_name",
            "flow_dirty",
            "hide",
            "infer_as_varchar",
            "infer_null_as_empty_string",
            "infer_record_count",
            "infer_schema",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "invalid_data_handling",
            "json_infer_record_count",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
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
            "preserve_partitioning",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_mode",
            "row_limit",
            "row_start",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "store_shared_strings_in_the_temporary_file",
            "type_mapping",
            "unique",
            "use_4_digit_years_in_date_formats",
            "worksheet_name",
        }
        required = {
            "client_id",
            "client_secret",
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "file_name",
            "hostname_or_ip_address",
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

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate_parameters()
        props = {
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "byte_limit",
            "cell_range",
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
            "file_format",
            "file_name",
            "flow_dirty",
            "hide",
            "infer_as_varchar",
            "infer_null_as_empty_string",
            "infer_record_count",
            "infer_schema",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "invalid_data_handling",
            "json_infer_record_count",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
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
            "preserve_partitioning",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_mode",
            "row_limit",
            "row_start",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "store_shared_strings_in_the_temporary_file",
            "type_mapping",
            "unique",
            "use_4_digit_years_in_date_formats",
            "worksheet_name",
        }
        required = {
            "client_id",
            "client_secret",
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "file_name",
            "hostname_or_ip_address",
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
                "active": 0,
                "SupportsRef": True,
                "maxRejectOutputs": 0,
                "minRejectOutputs": 0,
                "maxReferenceInputs": 0,
                "minReferenceInputs": 0,
            }
        }

    def get_input_ports_props(self) -> dict:
        include, exclude = self.validate_target()
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
        return {"min": 0, "max": 0}

    def get_output_ports_props(self) -> dict:
        include, exclude = self.validate_source()
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
        return {"min": 0, "max": 1}

    def get_allowed_as_source_props(self) -> bool:
        return True

    def get_target_props(self) -> dict:
        include, exclude = self.validate_target()
        props = {}
        required = set()
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
