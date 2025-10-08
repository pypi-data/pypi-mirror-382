import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.impala_connection import ImpalaConn
from ibm_watsonx_data_integration.services.datastage.models.enums import IMPALA
from pydantic import Field
from typing import ClassVar


class impala(BaseStage):

    op_name: ClassVar[str] = "impala"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/impala.svg"
    label: ClassVar[str] = "Apache Impala"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: ImpalaConn = ImpalaConn()
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: IMPALA.BufModeRonly | None = Field(IMPALA.BufModeRonly.default, alias="buf_mode_ronly")
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: IMPALA.BufferingMode | None = Field(IMPALA.BufferingMode.default, alias="buf_mode")
    byte_limit: str | None = Field(None, alias="byte_limit")
    collecting: IMPALA.Collecting | None = Field(IMPALA.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: IMPALA.CombinabilityMode | None = Field(IMPALA.CombinabilityMode.auto, alias="combinability")
    create_data_asset: bool | None = Field(False, alias="registerDataAsset")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_asset_name: str = Field(None, alias="dataAssetName")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    decimal_rounding_mode: IMPALA.DecimalRoundingMode | None = Field(
        IMPALA.DecimalRoundingMode.floor, alias="decimal_rounding_mode"
    )
    default_maximum_length_for_columns: int | None = Field(20000, alias="default_max_string_binary_precision")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    ds_before_after: bool | None = Field(False, alias="_before_after")
    ds_before_after_after_sql: str | None = Field(None, alias="_before_after._after_sql")
    ds_before_after_after_sql_fail_on_error: bool | None = Field(
        True, alias="_before_after._after_sql._fail_on_error"
    )
    ds_before_after_after_sql_node: str | None = Field(None, alias="_before_after._after_sql_node")
    ds_before_after_after_sql_node_fail_on_error: bool | None = Field(
        True, alias="_before_after._after_sql_node._fail_on_error"
    )
    ds_before_after_after_sql_node_read_from_file_after_sql_node: bool | None = Field(
        False, alias="_before_after._after_sql_node._read_from_file_after_sql_node"
    )
    ds_before_after_after_sql_read_from_file_after_sql: bool | None = Field(
        False, alias="_before_after._after_sql._read_from_file_after_sql"
    )
    ds_before_after_before_sql: str | None = Field(None, alias="_before_after._before_sql")
    ds_before_after_before_sql_fail_on_error: bool | None = Field(
        True, alias="_before_after._before_sql._fail_on_error"
    )
    ds_before_after_before_sql_node: str | None = Field(None, alias="_before_after._before_sql_node")
    ds_before_after_before_sql_node_fail_on_error: bool | None = Field(
        True, alias="_before_after._before_sql_node._fail_on_error"
    )
    ds_before_after_before_sql_node_read_from_file_before_sql_node: bool | None = Field(
        False, alias="_before_after._before_sql_node._read_from_file_before_sql_node"
    )
    ds_before_after_before_sql_read_from_file_before_sql: bool | None = Field(
        False, alias="_before_after._before_sql._read_from_file_before_sql"
    )
    ds_custom_statements: str | None = Field(None, alias="_custom_statements")
    ds_custom_statements_read_from_file_custom: bool | None = Field(
        False, alias="_custom_statements._read_from_file_custom"
    )
    ds_delete_statement: str = Field(None, alias="_delete_statement")
    ds_delete_statement_read_from_file_delete: bool | None = Field(
        False, alias="_delete_statement._read_from_file_delete"
    )
    ds_enable_partitioned_reads: bool | None = Field(False, alias="_enable_partitioned_reads")
    ds_enable_partitioned_reads_column_name: str | None = Field(None, alias="_enable_partitioned_reads._column_name")
    ds_enable_partitioned_reads_partition_method: IMPALA.DSEnablePartitionedReadsPartitionMethod | None = Field(
        IMPALA.DSEnablePartitionedReadsPartitionMethod._hive_partition,
        alias="_enable_partitioned_reads._partition_method",
    )
    ds_enable_partitioned_reads_table_name: str | None = Field(None, alias="_enable_partitioned_reads._table_name")
    ds_enable_partitioned_write: bool | None = Field(False, alias="_enable_partitioned_write")
    ds_enable_quoted_ids: bool | None = Field(False, alias="_enable_quoted_ids")
    ds_generate_sql: bool | None = Field(True, alias="_generate_sql")
    ds_hive_parameters: str | None = Field(None, alias="_hive_parameters")
    ds_hive_parameters_fail_on_error: bool | None = Field(False, alias="_hive_parameters._fail_on_error")
    ds_insert_statement: str = Field(None, alias="_insert_statement")
    ds_insert_statement_read_from_file_insert: bool | None = Field(
        False, alias="_insert_statement._read_from_file_insert"
    )
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    ds_limit_rows_limit: int | None = Field(None, alias="_limit_rows._limit")
    ds_read_mode: IMPALA.DSReadMode | None = Field(IMPALA.DSReadMode._select, alias="_read_mode")
    ds_record_ordering: IMPALA.DSRecordOrdering | None = Field(
        IMPALA.DSRecordOrdering.zero, alias="_record_ordering"
    )
    ds_record_ordering_key_column: list | None = Field([], alias="_record_ordering._key_column")
    ds_select_statement: str = Field(None, alias="_select_statement")
    ds_select_statement_other_clause: str | None = Field(None, alias="_select_statement._other_clause")
    ds_select_statement_read_from_file_select: bool | None = Field(
        False, alias="_select_statement._read_from_file_select"
    )
    ds_select_statement_where_clause: str | None = Field(None, alias="_select_statement._where_clause")
    ds_session_array_size: int | None = Field(1, alias="_session._array_size")
    ds_session_batch_size: int | None = Field(2000, alias="_session._batch_size")
    ds_session_character_set_for_non_unicode_columns: IMPALA.DSSessionCharacterSetForNonUnicodeColumns | None = (
        Field(
            IMPALA.DSSessionCharacterSetForNonUnicodeColumns._default,
            alias="_session._character_set_for_non_unicode_columns",
        )
    )
    ds_session_character_set_for_non_unicode_columns_character_set_name: str = Field(
        None, alias="_session._character_set_for_non_unicode_columns._character_set_name"
    )
    ds_session_default_length_for_columns: int | None = Field(200, alias="_session._default_length_for_columns")
    ds_session_default_length_for_long_columns: int | None = Field(
        20000, alias="_session._default_length_for_long_columns"
    )
    ds_session_drop_unmatched_fields: bool | None = Field(False, alias="_session._drop_unmatched_fields")
    ds_session_fail_on_truncation: bool | None = Field(True, alias="_session._fail_on_truncation")
    ds_session_fetch_size: int | None = Field(0, alias="_session._fetch_size")
    ds_session_generate_all_columns_as_unicode: bool | None = Field(
        False, alias="_session._generate_all_columns_as_unicode"
    )
    ds_session_keep_conductor_connection_alive: bool | None = Field(
        True, alias="_session._keep_conductor_connection_alive"
    )
    ds_session_report_schema_mismatch: bool | None = Field(False, alias="_session._report_schema_mismatch")
    ds_table_action: IMPALA.DSTableAction = Field(IMPALA.DSTableAction._append, alias="_table_action")
    ds_table_action_generate_create_statement: bool | None = Field(
        True, alias="_table_action._generate_create_statement"
    )
    ds_table_action_generate_create_statement_create_statement: str = Field(
        None, alias="_table_action._generate_create_statement._create_statement"
    )
    ds_table_action_generate_create_statement_fail_on_error: bool | None = Field(
        True, alias="_table_action._generate_create_statement._fail_on_error"
    )
    ds_table_action_generate_create_statement_row_format: IMPALA.DSTableActionGenerateCreateStatementRowFormat | None = Field(
        IMPALA.DSTableActionGenerateCreateStatementRowFormat._storage_format,
        alias="_table_action._generate_create_statement._row_format",
    )
    ds_table_action_generate_create_statement_row_format_field_terminator: str | None = Field(
        None, alias="_table_action._generate_create_statement._row_format._field_terminator"
    )
    ds_table_action_generate_create_statement_row_format_line_terminator: str | None = Field(
        None, alias="_table_action._generate_create_statement._row_format._line_terminator"
    )
    ds_table_action_generate_create_statement_row_format_serde_library: str = Field(
        None, alias="_table_action._generate_create_statement._row_format._serde_library"
    )
    ds_table_action_generate_create_statement_storage_format: IMPALA.DSTableActionGenerateCreateStatementStorageFormat | None = Field(
        IMPALA.DSTableActionGenerateCreateStatementStorageFormat._text_file,
        alias="_table_action._generate_create_statement._storage_format",
    )
    ds_table_action_generate_create_statement_table_location: str | None = Field(
        None, alias="_table_action._generate_create_statement._table_location"
    )
    ds_table_action_generate_drop_statement: bool | None = Field(
        True, alias="_table_action._generate_drop_statement"
    )
    ds_table_action_generate_drop_statement_drop_statement: str = Field(
        None, alias="_table_action._generate_drop_statement._drop_statement"
    )
    ds_table_action_generate_drop_statement_fail_on_error: bool | None = Field(
        False, alias="_table_action._generate_drop_statement._fail_on_error"
    )
    ds_table_action_generate_truncate_statement: bool | None = Field(
        True, alias="_table_action._generate_truncate_statement"
    )
    ds_table_action_generate_truncate_statement_fail_on_error: bool | None = Field(
        True, alias="_table_action._generate_truncate_statement._fail_on_error"
    )
    ds_table_action_generate_truncate_statement_truncate_statement: str = Field(
        None, alias="_table_action._generate_truncate_statement._truncate_statement"
    )
    ds_table_action_table_action_first: bool | None = Field(True, alias="_table_action._table_action_first")
    ds_table_name: str = Field(None, alias="_table_name")
    ds_transaction_auto_commit_mode: IMPALA.DSTransactionAutoCommitMode | None = Field(
        IMPALA.DSTransactionAutoCommitMode._disable, alias="_transaction._auto_commit_mode"
    )
    ds_transaction_begin_end: bool | None = Field(False, alias="_transaction._begin_end")
    ds_transaction_begin_end_begin_sql: str | None = Field(None, alias="_transaction._begin_end._begin_sql")
    ds_transaction_begin_end_end_sql: str | None = Field(None, alias="_transaction._begin_end._end_sql")
    ds_transaction_begin_end_run_end_sql_if_no_records_processed: bool | None = Field(
        False, alias="_transaction._begin_end._run_end_sql_if_no_records_processed"
    )
    ds_transaction_end_of_wave: IMPALA.DSTransactionEndOfWave | None = Field(
        IMPALA.DSTransactionEndOfWave._no, alias="_transaction._end_of_wave"
    )
    ds_transaction_isolation_level: IMPALA.DSTransactionIsolationLevel | None = Field(
        IMPALA.DSTransactionIsolationLevel._default, alias="_transaction._isolation_level"
    )
    ds_transaction_record_count: int | None = Field(2000, alias="_transaction._record_count")
    ds_update_statement: str = Field(None, alias="_update_statement")
    ds_update_statement_read_from_file_update: bool | None = Field(
        False, alias="_update_statement._read_from_file_update"
    )
    ds_use_datastage: bool | None = Field(True, alias="_use_datastage")
    ds_write_mode: IMPALA.DSWriteMode | None = Field(IMPALA.DSWriteMode._insert, alias="_write_mode")
    enable_after_sql: str | None = Field("", alias="before_after.after")
    enable_after_sql_node: str | None = Field("", alias="before_after.after_node")
    enable_before_sql: str | None = Field("", alias="before_after.before")
    enable_before_sql_node: str | None = Field("", alias="before_after.before_node")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execution_mode: IMPALA.ExecutionMode | None = Field(IMPALA.ExecutionMode.default_par, alias="execmode")
    fail_on_error_after_sql: bool | None = Field(True, alias="before_after.after.fail_on_error")
    fail_on_error_after_sql_node: bool | None = Field(True, alias="before_after.after_node.fail_on_error")
    fail_on_error_before_sql: bool | None = Field(True, alias="before_after.before.fail_on_error")
    fail_on_error_before_sql_node: bool | None = Field(True, alias="before_after.before_node.fail_on_error")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    generate_unicode_type_columns: bool | None = Field(False, alias="generate_unicode_columns")
    has_reference_output: bool | None = Field(False, alias="has_ref_output")
    hide: bool | None = Field(False, alias="hide")
    infer_schema: bool | None = Field(True, alias="rcp")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    key_column_names: str | None = Field(None, alias="key_column_names")
    lookup_type: IMPALA.LookupType | None = Field(IMPALA.LookupType.empty, alias="lookup_type")
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
    partition_type: IMPALA.PartitionType | None = Field(IMPALA.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: IMPALA.PreservePartitioning | None = Field(
        IMPALA.PreservePartitioning.default_propagate, alias="preserve"
    )
    push_filters: str | None = Field(None, alias="push_filters")
    pushed_filters: str | None = Field(None, alias="pushed_filters")
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    read_method: IMPALA.ReadMethod | None = Field(IMPALA.ReadMethod.general, alias="read_mode")
    rejected_filters: str | None = Field(None, alias="rejected_filters")
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    sampling_percentage: str | None = Field(None, alias="sampling_percentage")
    sampling_seed: int | None = Field(None, alias="sampling_seed")
    sampling_type: IMPALA.SamplingType | None = Field(IMPALA.SamplingType.none, alias="sampling_type")
    schema_name: str | None = Field(None, alias="schema_name")
    select_statement: str = Field(None, alias="select_statement")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: IMPALA.KeyColSelect | None = Field(IMPALA.KeyColSelect.default, alias="keyColSelect")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    static_statement: str = Field(None, alias="static_statement")
    table_action: IMPALA.TableAction | None = Field(IMPALA.TableAction.append, alias="table_action")
    table_name: str = Field(None, alias="table_name")
    unique: bool | None = Field(None, alias="part_unique")
    write_mode: IMPALA.WriteMode | None = Field(IMPALA.WriteMode.insert, alias="write_mode")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("preserve_partitioning")
            if (self.output_count and self.output_count > 0)
            else exclude.add("preserve_partitioning")
        )
        (
            include.add("ds_record_ordering")
            if (self.input_count and self.input_count > 1)
            else exclude.add("ds_record_ordering")
        )

        (
            include.add("ds_record_ordering_key_column")
            if (((self.input_count and self.input_count > 1)) and (self.ds_record_ordering == 2))
            else exclude.add("ds_record_ordering_key_column")
        )
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("ds_select_statement_where_clause")
            if (not self.ds_generate_sql)
            else exclude.add("ds_select_statement_where_clause")
        )
        (
            include.add("ds_session_report_schema_mismatch")
            if (self.ds_generate_sql)
            else exclude.add("ds_session_report_schema_mismatch")
        )
        (
            include.add("ds_before_after_before_sql_node")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node")
        )
        (
            include.add("ds_before_after_before_sql_node_fail_on_error")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node_fail_on_error")
        )
        (
            include.add("ds_enable_partitioned_reads_partition_method")
            if (
                ((self.ds_enable_partitioned_reads))
                and (
                    (
                        (
                            self.lookup_type
                            and (
                                (hasattr(self.lookup_type, "value") and not self.lookup_type.value)
                                or (not self.lookup_type)
                            )
                        )
                    )
                    or (

                            self.lookup_type
                            and (
                                (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                or (self.lookup_type == "empty")
                            )

                    )
                )
            )
            else exclude.add("ds_enable_partitioned_reads_partition_method")
        )
        (
            include.add("ds_before_after_after_sql_node_fail_on_error")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node_fail_on_error")
        )
        (
            include.add("ds_enable_partitioned_reads_table_name")
            if (
                ((self.ds_enable_partitioned_reads_partition_method == "_minimum_and_maximum_range"))
                and (
                    (
                        (
                            self.lookup_type
                            and (
                                (hasattr(self.lookup_type, "value") and not self.lookup_type.value)
                                or (not self.lookup_type)
                            )
                        )
                    )
                    or (

                            self.lookup_type
                            and (
                                (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                or (self.lookup_type == "empty")
                            )

                    )
                )
            )
            else exclude.add("ds_enable_partitioned_reads_table_name")
        )
        (
            include.add("ds_before_after_after_sql_read_from_file_after_sql")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_read_from_file_after_sql")
        )
        include.add("ds_table_name") if (self.ds_generate_sql) else exclude.add("ds_table_name")
        (
            include.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
        )
        (
            include.add("ds_before_after_before_sql_fail_on_error")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_fail_on_error")
        )
        (
            include.add("ds_select_statement_read_from_file_select")
            if (not self.ds_generate_sql)
            else exclude.add("ds_select_statement_read_from_file_select")
        )
        (
            include.add("ds_before_after_before_sql_node_read_from_file_before_sql_node")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node_read_from_file_before_sql_node")
        )
        (
            include.add("ds_before_after_after_sql_node")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node")
        )
        (
            include.add("ds_enable_partitioned_reads_column_name")
            if (
                (
                    ((self.ds_enable_partitioned_reads_partition_method == "_minimum_and_maximum_range"))
                    or ((self.ds_enable_partitioned_reads_partition_method == "_modulus"))
                )
                and (
                    (
                        (
                            self.lookup_type
                            and (
                                (hasattr(self.lookup_type, "value") and not self.lookup_type.value)
                                or (not self.lookup_type)
                            )
                        )
                    )
                    or (

                            self.lookup_type
                            and (
                                (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                or (self.lookup_type == "empty")
                            )

                    )
                )
            )
            else exclude.add("ds_enable_partitioned_reads_column_name")
        )
        (
            include.add("ds_transaction_begin_end_begin_sql")
            if (self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_begin_sql")
        )
        (
            include.add("ds_select_statement")
            if (not self.ds_generate_sql)
            else exclude.add("ds_select_statement")
        )
        (
            include.add("ds_enable_partitioned_reads")
            if (
                (
                    (
                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and not self.lookup_type.value)
                            or (not self.lookup_type)
                        )
                    )
                )
                or (

                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                            or (self.lookup_type == "empty")
                        )

                )
            )
            else exclude.add("ds_enable_partitioned_reads")
        )
        (
            include.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
            if (self.ds_session_character_set_for_non_unicode_columns == "_custom")
            else exclude.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
        )
        (
            include.add("ds_before_after_before_sql")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql")
        )
        (
            include.add("ds_before_after_after_sql_fail_on_error")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_fail_on_error")
        )
        (
            include.add("ds_transaction_begin_end_end_sql")
            if (self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_end_sql")
        )
        (
            include.add("ds_before_after_before_sql_read_from_file_before_sql")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_read_from_file_before_sql")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
            if (self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
        )
        (
            include.add("ds_limit_rows_limit")
            if (
                (
                    (
                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and not self.lookup_type.value)
                            or (not self.lookup_type)
                        )
                    )
                )
                or (

                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                            or (self.lookup_type == "empty")
                        )

                )
            )
            else exclude.add("ds_limit_rows_limit")
        )
        (
            include.add("ds_select_statement_other_clause")
            if (not self.ds_generate_sql)
            else exclude.add("ds_select_statement_other_clause")
        )
        (
            include.add("ds_before_after_after_sql")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql")
        )
        (
            include.add("select_statement")
            if (
                ((not self.schema_name))
                and (not self.table_name)
                and (

                        self.read_method
                        and (
                            (hasattr(self.read_method, "value") and self.read_method.value == "select")
                            or (self.read_method == "select")
                        )

                )
            )
            else exclude.add("select_statement")
        )
        (
            include.add("table_name")
            if (
                ((not self.select_statement))
                and (

                        self.read_method
                        and (
                            (hasattr(self.read_method, "value") and self.read_method.value == "general")
                            or (self.read_method == "general")
                        )

                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("schema_name")
            if (
                ((not self.select_statement))
                and (

                        self.read_method
                        and (
                            (hasattr(self.read_method, "value") and self.read_method.value == "general")
                            or (self.read_method == "general")
                        )

                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("ds_select_statement_where_clause")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_select_statement_where_clause")
        )
        (
            include.add("ds_session_report_schema_mismatch")
            if (

                    (
                        (
                            (
                                ((self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_session_report_schema_mismatch")
        )
        (
            include.add("select_statement")
            if (

                    (
                        (
                            (((not self.schema_name)) or ((self.schema_name and "#" in str(self.schema_name))))
                            and (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                            and (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value == "select")
                                            or (self.read_method == "select")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_method
                                        and (
                                            (
                                                hasattr(self.read_method, "value")
                                                and self.read_method.value
                                                and "#" in str(self.read_method.value)
                                            )
                                            or ("#" in str(self.read_method))
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("select_statement")
        )
        (
            include.add("ds_before_after_before_sql_node")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_before_sql_node")
        )
        (
            include.add("ds_before_after_before_sql_node_fail_on_error")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_before_sql_node_fail_on_error")
        )
        (
            include.add("table_name")
            if (

                    (
                        (
                            (
                                ((not self.select_statement))
                                or ((self.select_statement and "#" in str(self.select_statement)))
                            )
                            and (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value == "general")
                                            or (self.read_method == "general")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_method
                                        and (
                                            (
                                                hasattr(self.read_method, "value")
                                                and self.read_method.value
                                                and "#" in str(self.read_method.value)
                                            )
                                            or ("#" in str(self.read_method))
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("table_name")
        )
        (
            include.add("ds_enable_partitioned_reads_partition_method")
            if (

                    (
                        (
                            (
                                ((self.ds_enable_partitioned_reads))
                                or ((self.ds_enable_partitioned_reads and "#" in str(self.ds_enable_partitioned_reads)))
                            )
                            and (
                                (
                                    (
                                        self.lookup_type
                                        and (
                                            (hasattr(self.lookup_type, "value") and not self.lookup_type.value)
                                            or (not self.lookup_type)
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.lookup_type
                                        and (
                                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                            or (self.lookup_type == "empty")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.lookup_type
                                        and (
                                            (
                                                hasattr(self.lookup_type, "value")
                                                and self.lookup_type.value
                                                and "#" in str(self.lookup_type.value)
                                            )
                                            or ("#" in str(self.lookup_type))
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_enable_partitioned_reads_partition_method")
        )
        (
            include.add("ds_before_after_after_sql_node_fail_on_error")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_after_sql_node_fail_on_error")
        )
        (
            include.add("ds_enable_partitioned_reads_table_name")
            if (

                    (
                        (
                            (
                                ((self.ds_enable_partitioned_reads_partition_method == "_minimum_and_maximum_range"))
                                or (
                                    (
                                        self.ds_enable_partitioned_reads_partition_method
                                        and "#" in str(self.ds_enable_partitioned_reads_partition_method)
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        self.lookup_type
                                        and (
                                            (hasattr(self.lookup_type, "value") and not self.lookup_type.value)
                                            or (not self.lookup_type)
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.lookup_type
                                        and (
                                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                            or (self.lookup_type == "empty")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.lookup_type
                                        and (
                                            (
                                                hasattr(self.lookup_type, "value")
                                                and self.lookup_type.value
                                                and "#" in str(self.lookup_type.value)
                                            )
                                            or ("#" in str(self.lookup_type))
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_enable_partitioned_reads_table_name")
        )
        (
            include.add("ds_before_after_after_sql_read_from_file_after_sql")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_after_sql_read_from_file_after_sql")
        )
        (
            include.add("ds_table_name")
            if (

                    (
                        (
                            (
                                ((self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
        )
        (
            include.add("ds_before_after_before_sql_fail_on_error")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_before_sql_fail_on_error")
        )
        (
            include.add("ds_select_statement_read_from_file_select")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_select_statement_read_from_file_select")
        )
        (
            include.add("ds_before_after_before_sql_node_read_from_file_before_sql_node")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_before_sql_node_read_from_file_before_sql_node")
        )
        (
            include.add("ds_before_after_after_sql_node")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_after_sql_node")
        )
        (
            include.add("ds_enable_partitioned_reads_column_name")
            if (

                    (
                        (
                            (
                                ((self.ds_enable_partitioned_reads_partition_method == "_minimum_and_maximum_range"))
                                or ((self.ds_enable_partitioned_reads_partition_method == "_modulus"))
                                or (
                                    (
                                        self.ds_enable_partitioned_reads_partition_method
                                        and "#" in str(self.ds_enable_partitioned_reads_partition_method)
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        self.lookup_type
                                        and (
                                            (hasattr(self.lookup_type, "value") and not self.lookup_type.value)
                                            or (not self.lookup_type)
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.lookup_type
                                        and (
                                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                            or (self.lookup_type == "empty")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.lookup_type
                                        and (
                                            (
                                                hasattr(self.lookup_type, "value")
                                                and self.lookup_type.value
                                                and "#" in str(self.lookup_type.value)
                                            )
                                            or ("#" in str(self.lookup_type))
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_enable_partitioned_reads_column_name")
        )
        (
            include.add("ds_transaction_begin_end_begin_sql")
            if (((((self.ds_transaction_begin_end)))) and (self.ds_use_datastage))
            else exclude.add("ds_transaction_begin_end_begin_sql")
        )
        (
            include.add("ds_select_statement")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_select_statement")
        )
        (
            include.add("ds_enable_partitioned_reads")
            if (

                    (
                        (
                            (
                                self.lookup_type
                                and (
                                    (hasattr(self.lookup_type, "value") and not self.lookup_type.value)
                                    or (not self.lookup_type)
                                )
                            )
                        )
                        or (
                            (
                                self.lookup_type
                                and (
                                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                    or (self.lookup_type == "empty")
                                )
                            )
                        )
                        or (
                            (
                                self.lookup_type
                                and (
                                    (
                                        hasattr(self.lookup_type, "value")
                                        and self.lookup_type.value
                                        and "#" in str(self.lookup_type.value)
                                    )
                                    or ("#" in str(self.lookup_type))
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_enable_partitioned_reads")
        )
        (
            include.add("schema_name")
            if (

                    (
                        (
                            (
                                ((not self.select_statement))
                                or ((self.select_statement and "#" in str(self.select_statement)))
                            )
                            and (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value == "general")
                                            or (self.read_method == "general")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_method
                                        and (
                                            (
                                                hasattr(self.read_method, "value")
                                                and self.read_method.value
                                                and "#" in str(self.read_method.value)
                                            )
                                            or ("#" in str(self.read_method))
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("schema_name")
        )
        (
            include.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
            if (

                    (
                        (
                            (
                                ((self.ds_session_character_set_for_non_unicode_columns == "_custom"))
                                or (
                                    (
                                        self.ds_session_character_set_for_non_unicode_columns
                                        and "#" in str(self.ds_session_character_set_for_non_unicode_columns)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
        )
        (
            include.add("ds_before_after_before_sql")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_before_sql")
        )
        (
            include.add("ds_before_after_after_sql_fail_on_error")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_after_sql_fail_on_error")
        )
        (
            include.add("ds_transaction_begin_end_end_sql")
            if (((((self.ds_transaction_begin_end)))) and (self.ds_use_datastage))
            else exclude.add("ds_transaction_begin_end_end_sql")
        )
        (
            include.add("ds_before_after_before_sql_read_from_file_before_sql")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_before_sql_read_from_file_before_sql")
        )
        (
            include.add("lookup_type")
            if (((((self.has_reference_output)))) and (self.ds_use_datastage))
            else exclude.add("lookup_type")
        )
        (
            include.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
            if (((((self.ds_transaction_begin_end)))) and (self.ds_use_datastage))
            else exclude.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
        )
        (
            include.add("ds_limit_rows_limit")
            if (

                    (
                        (
                            (
                                self.lookup_type
                                and (
                                    (hasattr(self.lookup_type, "value") and not self.lookup_type.value)
                                    or (not self.lookup_type)
                                )
                            )
                        )
                        or (
                            (
                                self.lookup_type
                                and (
                                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                    or (self.lookup_type == "empty")
                                )
                            )
                        )
                        or (
                            (
                                self.lookup_type
                                and (
                                    (
                                        hasattr(self.lookup_type, "value")
                                        and self.lookup_type.value
                                        and "#" in str(self.lookup_type.value)
                                    )
                                    or ("#" in str(self.lookup_type))
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_limit_rows_limit")
        )
        (
            include.add("ds_select_statement_other_clause")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_select_statement_other_clause")
        )
        (
            include.add("ds_before_after_after_sql")
            if (

                    (
                        (
                            (
                                ((self.ds_before_after))
                                or ((self.ds_before_after and "#" in str(self.ds_before_after)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_before_after_after_sql")
        )
        include.add("pushed_filters") if (not self.ds_use_datastage) else exclude.add("pushed_filters")
        (
            include.add("ds_session_keep_conductor_connection_alive")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_keep_conductor_connection_alive")
        )
        include.add("rejected_filters") if (not self.ds_use_datastage) else exclude.add("rejected_filters")
        (
            include.add("ds_session_fail_on_truncation")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_fail_on_truncation")
        )
        (
            include.add("ds_session_fetch_size")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_fetch_size")
        )
        include.add("sampling_type") if (not self.ds_use_datastage) else exclude.add("sampling_type")
        (
            include.add("ds_transaction_begin_end")
            if (self.ds_use_datastage)
            else exclude.add("ds_transaction_begin_end")
        )
        (
            include.add("ds_session_generate_all_columns_as_unicode")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_generate_all_columns_as_unicode")
        )
        (
            include.add("fail_on_error_after_sql_node")
            if (not self.ds_use_datastage)
            else exclude.add("fail_on_error_after_sql_node")
        )
        (
            include.add("has_reference_output")
            if (self.ds_use_datastage)
            else exclude.add("has_reference_output")
        )
        (
            include.add("ds_transaction_auto_commit_mode")
            if (self.ds_use_datastage)
            else exclude.add("ds_transaction_auto_commit_mode")
        )
        (
            include.add("fail_on_error_before_sql")
            if (not self.ds_use_datastage)
            else exclude.add("fail_on_error_before_sql")
        )
        include.add("read_method") if (not self.ds_use_datastage) else exclude.add("read_method")
        include.add("ds_hive_parameters") if (self.ds_use_datastage) else exclude.add("ds_hive_parameters")
        (
            include.add("ds_hive_parameters_fail_on_error")
            if (self.ds_use_datastage)
            else exclude.add("ds_hive_parameters_fail_on_error")
        )
        include.add("key_column_names") if (not self.ds_use_datastage) else exclude.add("key_column_names")
        (
            include.add("enable_after_sql_node")
            if (not self.ds_use_datastage)
            else exclude.add("enable_after_sql_node")
        )
        include.add("sampling_seed") if (not self.ds_use_datastage) else exclude.add("sampling_seed")
        (
            include.add("fail_on_error_before_sql_node")
            if (not self.ds_use_datastage)
            else exclude.add("fail_on_error_before_sql_node")
        )
        include.add("sampling_percentage") if (not self.ds_use_datastage) else exclude.add("sampling_percentage")
        (
            include.add("ds_transaction_end_of_wave")
            if (self.ds_use_datastage)
            else exclude.add("ds_transaction_end_of_wave")
        )
        (
            include.add("ds_session_default_length_for_columns")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_default_length_for_columns")
        )
        include.add("ds_read_mode") if (self.ds_use_datastage) else exclude.add("ds_read_mode")
        include.add("enable_before_sql") if (not self.ds_use_datastage) else exclude.add("enable_before_sql")
        (
            include.add("ds_session_default_length_for_long_columns")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_default_length_for_long_columns")
        )
        (
            include.add("ds_enable_quoted_ids")
            if (self.ds_use_datastage)
            else exclude.add("ds_enable_quoted_ids")
        )
        include.add("byte_limit") if (not self.ds_use_datastage) else exclude.add("byte_limit")
        (
            include.add("ds_session_array_size")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_array_size")
        )
        (
            include.add("default_maximum_length_for_columns")
            if (not self.ds_use_datastage)
            else exclude.add("default_maximum_length_for_columns")
        )
        include.add("enable_after_sql") if (not self.ds_use_datastage) else exclude.add("enable_after_sql")
        (
            include.add("generate_unicode_type_columns")
            if (not self.ds_use_datastage)
            else exclude.add("generate_unicode_type_columns")
        )
        include.add("infer_schema") if (not self.ds_use_datastage) else exclude.add("infer_schema")
        (
            include.add("ds_transaction_isolation_level")
            if (self.ds_use_datastage)
            else exclude.add("ds_transaction_isolation_level")
        )
        (
            include.add("ds_transaction_record_count")
            if (self.ds_use_datastage)
            else exclude.add("ds_transaction_record_count")
        )
        (
            include.add("enable_before_sql_node")
            if (not self.ds_use_datastage)
            else exclude.add("enable_before_sql_node")
        )
        include.add("ds_generate_sql") if (self.ds_use_datastage) else exclude.add("ds_generate_sql")
        include.add("ds_before_after") if (self.ds_use_datastage) else exclude.add("ds_before_after")
        (
            include.add("decimal_rounding_mode")
            if (not self.ds_use_datastage)
            else exclude.add("decimal_rounding_mode")
        )
        include.add("row_limit") if (not self.ds_use_datastage) else exclude.add("row_limit")
        (
            include.add("ds_session_character_set_for_non_unicode_columns")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_character_set_for_non_unicode_columns")
        )
        (
            include.add("fail_on_error_after_sql")
            if (not self.ds_use_datastage)
            else exclude.add("fail_on_error_after_sql")
        )
        include.add("push_filters") if (not self.ds_use_datastage) else exclude.add("push_filters")
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
            include.add("ds_record_ordering_key_column")
            if (((self.input_count and self.input_count > 1)) and (self.ds_record_ordering == 2))
            else exclude.add("ds_record_ordering_key_column")
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
        (
            include.add("ds_transaction_begin_end_begin_sql")
            if (self.ds_transaction_begin_end == "true" or self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_begin_sql")
        )
        (
            include.add("ds_before_after_before_sql_node_read_from_file_before_sql_node")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node_read_from_file_before_sql_node")
        )
        (
            include.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
            if (
                self.ds_session_character_set_for_non_unicode_columns
                and "_custom" in str(self.ds_session_character_set_for_non_unicode_columns)
            )
            else exclude.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
        )
        (
            include.add("ds_before_after_after_sql_fail_on_error")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_fail_on_error")
        )
        (
            include.add("ds_session_report_schema_mismatch")
            if (self.ds_generate_sql and "true" in str(self.ds_generate_sql))
            else exclude.add("ds_session_report_schema_mismatch")
        )
        (
            include.add("ds_select_statement_other_clause")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_select_statement_other_clause")
        )
        (
            include.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
            if (self.ds_transaction_begin_end == "true" or self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
        )
        (
            include.add("ds_enable_partitioned_reads_column_name")
            if (
                self.ds_enable_partitioned_reads_partition_method
                and "_minimum_and_maximum_range" in str(self.ds_enable_partitioned_reads_partition_method)
                and self.ds_enable_partitioned_reads_partition_method
                and "_modulus" in str(self.ds_enable_partitioned_reads_partition_method)
            )
            and (
                (
                    self.lookup_type
                    and ((hasattr(self.lookup_type, "value") and not self.lookup_type.value) or (not self.lookup_type))
                )
                or (
                    self.lookup_type
                    and (
                        (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                        or (self.lookup_type == "empty")
                    )
                )
            )
            else exclude.add("ds_enable_partitioned_reads_column_name")
        )
        (
            include.add("ds_before_after_before_sql")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql")
        )
        (
            include.add("ds_select_statement")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_select_statement")
        )
        (
            include.add("ds_before_after_after_sql_node")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node")
        )
        (
            include.add("ds_before_after_before_sql_read_from_file_before_sql")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_read_from_file_before_sql")
        )
        (
            include.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
        )
        (
            include.add("ds_transaction_begin_end_end_sql")
            if (self.ds_transaction_begin_end == "true" or self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_end_sql")
        )
        (
            include.add("ds_before_after_after_sql_read_from_file_after_sql")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_read_from_file_after_sql")
        )
        (
            include.add("ds_table_name")
            if (self.ds_generate_sql == "true" or self.ds_generate_sql)
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_enable_partitioned_reads")
            if (
                self.lookup_type
                and ((hasattr(self.lookup_type, "value") and not self.lookup_type.value) or (not self.lookup_type))
            )
            or (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                    or (self.lookup_type == "empty")
                )
            )
            else exclude.add("ds_enable_partitioned_reads")
        )
        (
            include.add("ds_enable_partitioned_reads_partition_method")
            if (self.ds_enable_partitioned_reads == "true" or self.ds_enable_partitioned_reads)
            and (
                (
                    self.lookup_type
                    and ((hasattr(self.lookup_type, "value") and not self.lookup_type.value) or (not self.lookup_type))
                )
                or (
                    self.lookup_type
                    and (
                        (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                        or (self.lookup_type == "empty")
                    )
                )
            )
            else exclude.add("ds_enable_partitioned_reads_partition_method")
        )
        (
            include.add("lookup_type")
            if (self.has_reference_output == "true" or self.has_reference_output)
            else exclude.add("lookup_type")
        )
        (
            include.add("ds_limit_rows_limit")
            if (
                self.lookup_type
                and ((hasattr(self.lookup_type, "value") and not self.lookup_type.value) or (not self.lookup_type))
            )
            or (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                    or (self.lookup_type == "empty")
                )
            )
            else exclude.add("ds_limit_rows_limit")
        )
        (
            include.add("ds_before_after_before_sql_node_fail_on_error")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node_fail_on_error")
        )
        (
            include.add("schema_name")
            if (not self.select_statement)
            and (
                self.read_method
                and (
                    (hasattr(self.read_method, "value") and self.read_method.value == "general")
                    or (self.read_method == "general")
                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("ds_select_statement_read_from_file_select")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_select_statement_read_from_file_select")
        )
        (
            include.add("ds_before_after_before_sql_fail_on_error")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_fail_on_error")
        )
        (
            include.add("table_name")
            if (not self.select_statement)
            and (
                self.read_method
                and (
                    (hasattr(self.read_method, "value") and self.read_method.value == "general")
                    or (self.read_method == "general")
                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("select_statement")
            if (not self.schema_name)
            and (not self.table_name)
            and (
                self.read_method
                and (
                    (hasattr(self.read_method, "value") and self.read_method.value == "select")
                    or (self.read_method == "select")
                )
            )
            else exclude.add("select_statement")
        )
        (
            include.add("ds_before_after_after_sql")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql")
        )
        (
            include.add("ds_select_statement_where_clause")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_select_statement_where_clause")
        )
        (
            include.add("ds_enable_partitioned_reads_table_name")
            if (self.ds_enable_partitioned_reads_partition_method == "_minimum_and_maximum_range")
            and (
                (
                    self.lookup_type
                    and ((hasattr(self.lookup_type, "value") and not self.lookup_type.value) or (not self.lookup_type))
                )
                or (
                    self.lookup_type
                    and (
                        (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                        or (self.lookup_type == "empty")
                    )
                )
            )
            else exclude.add("ds_enable_partitioned_reads_table_name")
        )
        (
            include.add("ds_before_after_after_sql_node_fail_on_error")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node_fail_on_error")
        )
        (
            include.add("ds_before_after_before_sql_node")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("ds_table_action_generate_create_statement_row_format_line_terminator")
            if (self.ds_table_action_generate_create_statement_row_format == "_delimited")
            else exclude.add("ds_table_action_generate_create_statement_row_format_line_terminator")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format")
            if (self.ds_table_action_generate_create_statement)
            else exclude.add("ds_table_action_generate_create_statement_row_format")
        )
        (
            include.add("ds_table_action_generate_create_statement_storage_format")
            if (self.ds_table_action_generate_create_statement)
            else exclude.add("ds_table_action_generate_create_statement_storage_format")
        )
        (
            include.add("ds_insert_statement_read_from_file_insert")
            if (((not self.ds_generate_sql)) and (self.ds_write_mode == "_insert"))
            else exclude.add("ds_insert_statement_read_from_file_insert")
        )
        (
            include.add("ds_table_name")
            if (
                ((self.ds_table_action_generate_create_statement))
                or (self.ds_table_action_generate_drop_statement)
                or (self.ds_table_action_generate_truncate_statement)
                or (self.ds_generate_sql)
            )
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_table_action_generate_drop_statement")
            if (self.ds_table_action == "_replace")
            else exclude.add("ds_table_action_generate_drop_statement")
        )
        (
            include.add("ds_delete_statement_read_from_file_delete")
            if (((not self.ds_generate_sql)) and (self.ds_write_mode == "_delete"))
            else exclude.add("ds_delete_statement_read_from_file_delete")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_fail_on_error")
            if (self.ds_table_action_generate_truncate_statement)
            else exclude.add("ds_table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("ds_table_action_generate_create_statement_fail_on_error")
            if (self.ds_table_action_generate_create_statement)
            else exclude.add("ds_table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("ds_table_action_generate_create_statement_table_location")
            if (self.ds_table_action_generate_create_statement)
            else exclude.add("ds_table_action_generate_create_statement_table_location")
        )
        (
            include.add("ds_update_statement_read_from_file_update")
            if (((not self.ds_generate_sql)) and (self.ds_write_mode == "_update"))
            else exclude.add("ds_update_statement_read_from_file_update")
        )
        (
            include.add("ds_enable_partitioned_write")
            if (self.ds_write_mode == "_insert")
            else exclude.add("ds_enable_partitioned_write")
        )
        (
            include.add("ds_table_action_generate_create_statement_create_statement")
            if (not self.ds_table_action_generate_create_statement)
            else exclude.add("ds_table_action_generate_create_statement_create_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format_field_terminator")
            if (self.ds_table_action_generate_create_statement_row_format == "_delimited")
            else exclude.add("ds_table_action_generate_create_statement_row_format_field_terminator")
        )
        (
            include.add("ds_insert_statement")
            if (((not self.ds_generate_sql)) and (self.ds_write_mode == "_insert"))
            else exclude.add("ds_insert_statement")
        )
        (
            include.add("ds_table_action_generate_drop_statement_drop_statement")
            if (not self.ds_table_action_generate_drop_statement)
            else exclude.add("ds_table_action_generate_drop_statement_drop_statement")
        )
        (
            include.add("ds_table_action_generate_truncate_statement")
            if (self.ds_table_action == "_truncate")
            else exclude.add("ds_table_action_generate_truncate_statement")
        )
        (
            include.add("ds_table_action_table_action_first")
            if (

                    ((self.ds_table_action == "_create"))
                    or (self.ds_table_action == "_replace")
                    or (self.ds_table_action == "_truncate")

            )
            else exclude.add("ds_table_action_table_action_first")
        )
        (
            include.add("ds_custom_statements_read_from_file_custom")
            if (self.ds_write_mode == "_custom")
            else exclude.add("ds_custom_statements_read_from_file_custom")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_truncate_statement")
            if (not self.ds_table_action_generate_truncate_statement)
            else exclude.add("ds_table_action_generate_truncate_statement_truncate_statement")
        )
        (
            include.add("ds_session_batch_size")
            if (

                    ((self.ds_write_mode == "_custom"))
                    or (self.ds_write_mode == "_delete")
                    or (self.ds_write_mode == "_insert")
                    or (self.ds_write_mode == "_update")

            )
            else exclude.add("ds_session_batch_size")
        )
        (
            include.add("ds_table_action_generate_drop_statement_fail_on_error")
            if (self.ds_table_action_generate_drop_statement)
            else exclude.add("ds_table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("ds_generate_sql")
            if (

                    ((self.ds_write_mode == "_delete"))
                    or (self.ds_write_mode == "_insert")
                    or (self.ds_write_mode == "_update")

            )
            else exclude.add("ds_generate_sql")
        )
        (
            include.add("ds_delete_statement")
            if (((not self.ds_generate_sql)) and (self.ds_write_mode == "_delete"))
            else exclude.add("ds_delete_statement")
        )
        (
            include.add("ds_update_statement")
            if (((not self.ds_generate_sql)) and (self.ds_write_mode == "_update"))
            else exclude.add("ds_update_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format_serde_library")
            if (self.ds_table_action_generate_create_statement_row_format == "_ser_de")
            else exclude.add("ds_table_action_generate_create_statement_row_format_serde_library")
        )
        (
            include.add("ds_table_action_generate_create_statement")
            if (((self.ds_table_action == "_create")) or (self.ds_table_action == "_replace"))
            else exclude.add("ds_table_action_generate_create_statement")
        )
        (
            include.add("ds_custom_statements")
            if (self.ds_write_mode == "_custom")
            else exclude.add("ds_custom_statements")
        )
        (
            include.add("table_name")
            if (
                ((not self.static_statement))
                and (


                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
                            )


                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("table_action")
            if (
                ((not self.static_statement))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
                            )
                        )
                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "update_statement")
                                or (self.write_mode != "update_statement")
                            )

                    )
                )
            )
            else exclude.add("table_action")
        )
        (
            include.add("schema_name")
            if (
                ((not self.static_statement))
                and (


                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
                            )


                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("static_statement")
            if (
                ((not self.schema_name))
                and (not self.table_name)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "static_statement")
                            or (self.write_mode == "static_statement")
                        )

                )
            )
            else exclude.add("static_statement")
        )
        (
            include.add("ds_session_report_schema_mismatch")
            if (

                    (((self.ds_generate_sql)) or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_session_report_schema_mismatch")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format_line_terminator")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action_generate_create_statement_row_format == "_delimited"))
                                or (
                                    (
                                        self.ds_table_action_generate_create_statement_row_format
                                        and "#" in str(self.ds_table_action_generate_create_statement_row_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_row_format_line_terminator")
        )
        (
            include.add("table_name")
            if (

                    (
                        (
                            (
                                ((not self.static_statement))
                                or ((self.static_statement and "#" in str(self.static_statement)))
                            )
                            and (
                                (
                                    (
                                        (
                                            (
                                                self.write_mode
                                                and (
                                                    (
                                                        hasattr(self.write_mode, "value")
                                                        and self.write_mode.value != "static_statement"
                                                    )
                                                    or (self.write_mode != "static_statement")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.write_mode
                                                and (
                                                    (
                                                        hasattr(self.write_mode, "value")
                                                        and self.write_mode.value
                                                        and "#" in str(self.write_mode.value)
                                                    )
                                                    or ("#" in str(self.write_mode))
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("table_name")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action_generate_create_statement))
                                or (
                                    (
                                        self.ds_table_action_generate_create_statement
                                        and "#" in str(self.ds_table_action_generate_create_statement)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_row_format")
        )
        (
            include.add("ds_table_action_generate_create_statement_storage_format")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action_generate_create_statement))
                                or (
                                    (
                                        self.ds_table_action_generate_create_statement
                                        and "#" in str(self.ds_table_action_generate_create_statement)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_storage_format")
        )
        (
            include.add("ds_insert_statement_read_from_file_insert")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_insert_statement_read_from_file_insert")
        )
        (
            include.add("ds_table_name")
            if (

                    (
                        ((self.ds_table_action_generate_create_statement))
                        or ((self.ds_table_action_generate_drop_statement))
                        or ((self.ds_table_action_generate_truncate_statement))
                        or ((self.ds_generate_sql))
                        or (
                            (
                                self.ds_table_action_generate_create_statement
                                and "#" in str(self.ds_table_action_generate_create_statement)
                            )
                        )
                        or (
                            (
                                self.ds_table_action_generate_drop_statement
                                and "#" in str(self.ds_table_action_generate_drop_statement)
                            )
                        )
                        or (
                            (
                                self.ds_table_action_generate_truncate_statement
                                and "#" in str(self.ds_table_action_generate_truncate_statement)
                            )
                        )
                        or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_table_action_generate_drop_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action == "_replace"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_drop_statement")
        )
        (
            include.add("ds_delete_statement_read_from_file_delete")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "_delete"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_delete_statement_read_from_file_delete")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_fail_on_error")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action_generate_truncate_statement))
                                or (
                                    (
                                        self.ds_table_action_generate_truncate_statement
                                        and "#" in str(self.ds_table_action_generate_truncate_statement)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("ds_table_action_generate_create_statement_fail_on_error")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action_generate_create_statement))
                                or (
                                    (
                                        self.ds_table_action_generate_create_statement
                                        and "#" in str(self.ds_table_action_generate_create_statement)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("ds_table_action_generate_create_statement_table_location")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action_generate_create_statement))
                                or (
                                    (
                                        self.ds_table_action_generate_create_statement
                                        and "#" in str(self.ds_table_action_generate_create_statement)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_table_location")
        )
        (
            include.add("table_action")
            if (

                    (
                        (
                            (
                                ((not self.static_statement))
                                or ((self.static_statement and "#" in str(self.static_statement)))
                            )
                            and (
                                (
                                    (
                                        (
                                            (
                                                self.write_mode
                                                and (
                                                    (
                                                        hasattr(self.write_mode, "value")
                                                        and self.write_mode.value != "static_statement"
                                                    )
                                                    or (self.write_mode != "static_statement")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.write_mode
                                                and (
                                                    (
                                                        hasattr(self.write_mode, "value")
                                                        and self.write_mode.value
                                                        and "#" in str(self.write_mode.value)
                                                    )
                                                    or ("#" in str(self.write_mode))
                                                )
                                            )
                                        )
                                    )
                                    and (
                                        (
                                            (
                                                self.write_mode
                                                and (
                                                    (
                                                        hasattr(self.write_mode, "value")
                                                        and self.write_mode.value != "update_statement"
                                                    )
                                                    or (self.write_mode != "update_statement")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.write_mode
                                                and (
                                                    (
                                                        hasattr(self.write_mode, "value")
                                                        and self.write_mode.value
                                                        and "#" in str(self.write_mode.value)
                                                    )
                                                    or ("#" in str(self.write_mode))
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("table_action")
        )
        (
            include.add("ds_update_statement_read_from_file_update")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "_update"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_update_statement_read_from_file_update")
        )
        (
            include.add("ds_enable_partitioned_write")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_enable_partitioned_write")
        )
        (
            include.add("ds_table_action_generate_create_statement_create_statement")
            if (

                    (
                        (
                            (
                                ((not self.ds_table_action_generate_create_statement))
                                or (
                                    (
                                        self.ds_table_action_generate_create_statement
                                        and "#" in str(self.ds_table_action_generate_create_statement)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_create_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format_field_terminator")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action_generate_create_statement_row_format == "_delimited"))
                                or (
                                    (
                                        self.ds_table_action_generate_create_statement_row_format
                                        and "#" in str(self.ds_table_action_generate_create_statement_row_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_row_format_field_terminator")
        )
        (
            include.add("ds_insert_statement")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_insert_statement")
        )
        (
            include.add("ds_table_action_generate_drop_statement_drop_statement")
            if (

                    (
                        (
                            (
                                ((not self.ds_table_action_generate_drop_statement))
                                or (
                                    (
                                        self.ds_table_action_generate_drop_statement
                                        and "#" in str(self.ds_table_action_generate_drop_statement)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_drop_statement_drop_statement")
        )
        (
            include.add("ds_table_action_generate_truncate_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action == "_truncate"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_truncate_statement")
        )
        (
            include.add("ds_table_action_table_action_first")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action == "_create"))
                                or ((self.ds_table_action == "_replace"))
                                or ((self.ds_table_action == "_truncate"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_table_action_first")
        )
        (
            include.add("schema_name")
            if (

                    (
                        (
                            (
                                ((not self.static_statement))
                                or ((self.static_statement and "#" in str(self.static_statement)))
                            )
                            and (
                                (
                                    (
                                        (
                                            (
                                                self.write_mode
                                                and (
                                                    (
                                                        hasattr(self.write_mode, "value")
                                                        and self.write_mode.value != "static_statement"
                                                    )
                                                    or (self.write_mode != "static_statement")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.write_mode
                                                and (
                                                    (
                                                        hasattr(self.write_mode, "value")
                                                        and self.write_mode.value
                                                        and "#" in str(self.write_mode.value)
                                                    )
                                                    or ("#" in str(self.write_mode))
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("schema_name")
        )
        (
            include.add("ds_custom_statements_read_from_file_custom")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "_custom"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_custom_statements_read_from_file_custom")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_truncate_statement")
            if (

                    (
                        (
                            (
                                ((not self.ds_table_action_generate_truncate_statement))
                                or (
                                    (
                                        self.ds_table_action_generate_truncate_statement
                                        and "#" in str(self.ds_table_action_generate_truncate_statement)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_truncate_statement_truncate_statement")
        )
        (
            include.add("ds_session_batch_size")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "_custom"))
                                or ((self.ds_write_mode == "_delete"))
                                or ((self.ds_write_mode == "_insert"))
                                or ((self.ds_write_mode == "_update"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_session_batch_size")
        )
        (
            include.add("ds_table_action_generate_drop_statement_fail_on_error")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action_generate_drop_statement))
                                or (
                                    (
                                        self.ds_table_action_generate_drop_statement
                                        and "#" in str(self.ds_table_action_generate_drop_statement)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("ds_generate_sql")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "_delete"))
                                or ((self.ds_write_mode == "_insert"))
                                or ((self.ds_write_mode == "_update"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_generate_sql")
        )
        (
            include.add("ds_delete_statement")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "_delete"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_delete_statement")
        )
        (
            include.add("ds_update_statement")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "_update"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_update_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format_serde_library")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action_generate_create_statement_row_format == "_ser_de"))
                                or (
                                    (
                                        self.ds_table_action_generate_create_statement_row_format
                                        and "#" in str(self.ds_table_action_generate_create_statement_row_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_row_format_serde_library")
        )
        (
            include.add("ds_table_action_generate_create_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_table_action == "_create"))
                                or ((self.ds_table_action == "_replace"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement")
        )
        (
            include.add("ds_custom_statements")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "_custom"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_custom_statements")
        )
        (
            include.add("static_statement")
            if (

                    (
                        (
                            (((not self.schema_name)) or ((self.schema_name and "#" in str(self.schema_name))))
                            and (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                            and (
                                (
                                    (
                                        self.write_mode
                                        and (
                                            (
                                                hasattr(self.write_mode, "value")
                                                and self.write_mode.value == "static_statement"
                                            )
                                            or (self.write_mode == "static_statement")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.write_mode
                                        and (
                                            (
                                                hasattr(self.write_mode, "value")
                                                and self.write_mode.value
                                                and "#" in str(self.write_mode.value)
                                            )
                                            or ("#" in str(self.write_mode))
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("static_statement")
        )
        (
            include.add("ds_session_drop_unmatched_fields")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_drop_unmatched_fields")
        )
        include.add("write_mode") if (not self.ds_use_datastage) else exclude.add("write_mode")
        include.add("ds_table_action") if (self.ds_use_datastage) else exclude.add("ds_table_action")
        include.add("ds_write_mode") if (self.ds_use_datastage) else exclude.add("ds_write_mode")
        include.add("data_asset_name") if (self.create_data_asset) else exclude.add("data_asset_name")
        include.add("create_data_asset") if (()) else exclude.add("create_data_asset")
        (
            include.add("ds_table_action_generate_drop_statement")
            if (self.ds_table_action and "_replace" in str(self.ds_table_action))
            else exclude.add("ds_table_action_generate_drop_statement")
        )
        (
            include.add("ds_table_action_generate_truncate_statement")
            if (self.ds_table_action and "_truncate" in str(self.ds_table_action))
            else exclude.add("ds_table_action_generate_truncate_statement")
        )
        (
            include.add("ds_custom_statements")
            if (self.ds_write_mode == "_custom")
            else exclude.add("ds_custom_statements")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format_serde_library")
            if (self.ds_table_action_generate_create_statement_row_format == "_ser_de")
            else exclude.add("ds_table_action_generate_create_statement_row_format_serde_library")
        )
        (
            include.add("ds_table_action_table_action_first")
            if (
                self.ds_table_action
                and "_create" in str(self.ds_table_action)
                and self.ds_table_action
                and "_replace" in str(self.ds_table_action)
                and self.ds_table_action
                and "_truncate" in str(self.ds_table_action)
            )
            else exclude.add("ds_table_action_table_action_first")
        )
        (
            include.add("ds_update_statement_read_from_file_update")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (self.ds_write_mode and "_update" in str(self.ds_write_mode))
            else exclude.add("ds_update_statement_read_from_file_update")
        )
        (
            include.add("ds_custom_statements_read_from_file_custom")
            if (self.ds_write_mode == "_custom")
            else exclude.add("ds_custom_statements_read_from_file_custom")
        )
        (
            include.add("ds_insert_statement")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (self.ds_write_mode and "_insert" in str(self.ds_write_mode))
            else exclude.add("ds_insert_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format_line_terminator")
            if (self.ds_table_action_generate_create_statement_row_format == "_delimited")
            else exclude.add("ds_table_action_generate_create_statement_row_format_line_terminator")
        )
        (
            include.add("ds_table_action_generate_create_statement_fail_on_error")
            if (
                self.ds_table_action_generate_create_statement
                and "true" in str(self.ds_table_action_generate_create_statement)
            )
            else exclude.add("ds_table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("ds_table_action_generate_create_statement_table_location")
            if (
                self.ds_table_action_generate_create_statement
                and "true" in str(self.ds_table_action_generate_create_statement)
            )
            else exclude.add("ds_table_action_generate_create_statement_table_location")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format_field_terminator")
            if (self.ds_table_action_generate_create_statement_row_format == "_delimited")
            else exclude.add("ds_table_action_generate_create_statement_row_format_field_terminator")
        )
        (
            include.add("ds_delete_statement_read_from_file_delete")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (self.ds_write_mode and "_delete" in str(self.ds_write_mode))
            else exclude.add("ds_delete_statement_read_from_file_delete")
        )
        (
            include.add("ds_enable_partitioned_write")
            if (self.ds_write_mode == "_insert")
            else exclude.add("ds_enable_partitioned_write")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_truncate_statement")
            if (
                self.ds_table_action_generate_truncate_statement
                and "false" in str(self.ds_table_action_generate_truncate_statement)
            )
            else exclude.add("ds_table_action_generate_truncate_statement_truncate_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement_row_format")
            if (
                self.ds_table_action_generate_create_statement
                and "true" in str(self.ds_table_action_generate_create_statement)
            )
            else exclude.add("ds_table_action_generate_create_statement_row_format")
        )
        (
            include.add("ds_delete_statement")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (self.ds_write_mode and "_delete" in str(self.ds_write_mode))
            else exclude.add("ds_delete_statement")
        )
        (
            include.add("table_action")
            if (not self.static_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "static_statement" not in str(self.write_mode.value)
                    )
                    or ("static_statement" not in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_statement" not in str(self.write_mode.value)
                    )
                    or ("update_statement" not in str(self.write_mode))
                )
            )
            else exclude.add("table_action")
        )
        (
            include.add("ds_table_action_generate_drop_statement_drop_statement")
            if (
                self.ds_table_action_generate_drop_statement
                and "false" in str(self.ds_table_action_generate_drop_statement)
            )
            else exclude.add("ds_table_action_generate_drop_statement_drop_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement")
            if (
                self.ds_table_action
                and "_create" in str(self.ds_table_action)
                and self.ds_table_action
                and "_replace" in str(self.ds_table_action)
            )
            else exclude.add("ds_table_action_generate_create_statement")
        )
        (
            include.add("ds_insert_statement_read_from_file_insert")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (self.ds_write_mode and "_insert" in str(self.ds_write_mode))
            else exclude.add("ds_insert_statement_read_from_file_insert")
        )
        (
            include.add("static_statement")
            if (not self.schema_name)
            and (not self.table_name)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "static_statement")
                    or (self.write_mode == "static_statement")
                )
            )
            else exclude.add("static_statement")
        )
        (
            include.add("ds_table_name")
            if (
                self.ds_table_action_generate_create_statement == "true"
                or self.ds_table_action_generate_create_statement
            )
            or (
                self.ds_table_action_generate_drop_statement == "true"
                or self.ds_table_action_generate_drop_statement
            )
            or (
                self.ds_table_action_generate_truncate_statement == "true"
                or self.ds_table_action_generate_truncate_statement
            )
            or (self.ds_generate_sql == "true" or self.ds_generate_sql)
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_table_action_generate_drop_statement_fail_on_error")
            if (
                self.ds_table_action_generate_drop_statement
                and "true" in str(self.ds_table_action_generate_drop_statement)
            )
            else exclude.add("ds_table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("ds_session_batch_size")
            if (
                self.ds_write_mode
                and "_custom" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "_delete" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "_insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "_update" in str(self.ds_write_mode)
            )
            else exclude.add("ds_session_batch_size")
        )
        (
            include.add("schema_name")
            if (not self.static_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "static_statement" not in str(self.write_mode.value)
                    )
                    or ("static_statement" not in str(self.write_mode))
                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("ds_table_action_generate_create_statement_storage_format")
            if (
                self.ds_table_action_generate_create_statement
                and "true" in str(self.ds_table_action_generate_create_statement)
            )
            else exclude.add("ds_table_action_generate_create_statement_storage_format")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_fail_on_error")
            if (
                self.ds_table_action_generate_truncate_statement
                and "true" in str(self.ds_table_action_generate_truncate_statement)
            )
            else exclude.add("ds_table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("table_name")
            if (not self.static_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "static_statement" not in str(self.write_mode.value)
                    )
                    or ("static_statement" not in str(self.write_mode))
                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("ds_table_action_generate_create_statement_create_statement")
            if (
                self.ds_table_action_generate_create_statement
                and "false" in str(self.ds_table_action_generate_create_statement)
            )
            else exclude.add("ds_table_action_generate_create_statement_create_statement")
        )
        (
            include.add("ds_generate_sql")
            if (
                self.ds_write_mode
                and "_delete" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "_insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "_update" in str(self.ds_write_mode)
            )
            else exclude.add("ds_generate_sql")
        )
        (
            include.add("ds_update_statement")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (self.ds_write_mode and "_update" in str(self.ds_write_mode))
            else exclude.add("ds_update_statement")
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
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "decimal_rounding_mode",
            "default_maximum_length_for_columns",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_before_after",
            "ds_before_after_after_sql",
            "ds_before_after_after_sql_fail_on_error",
            "ds_before_after_after_sql_node",
            "ds_before_after_after_sql_node_fail_on_error",
            "ds_before_after_after_sql_node_read_from_file_after_sql_node",
            "ds_before_after_after_sql_read_from_file_after_sql",
            "ds_before_after_before_sql",
            "ds_before_after_before_sql_fail_on_error",
            "ds_before_after_before_sql_node",
            "ds_before_after_before_sql_node_fail_on_error",
            "ds_before_after_before_sql_node_read_from_file_before_sql_node",
            "ds_before_after_before_sql_read_from_file_before_sql",
            "ds_enable_partitioned_reads",
            "ds_enable_partitioned_reads_column_name",
            "ds_enable_partitioned_reads_partition_method",
            "ds_enable_partitioned_reads_table_name",
            "ds_enable_quoted_ids",
            "ds_generate_sql",
            "ds_hive_parameters",
            "ds_hive_parameters_fail_on_error",
            "ds_java_heap_size",
            "ds_limit_rows_limit",
            "ds_read_mode",
            "ds_record_ordering",
            "ds_record_ordering_key_column",
            "ds_select_statement",
            "ds_select_statement_other_clause",
            "ds_select_statement_read_from_file_select",
            "ds_select_statement_where_clause",
            "ds_session_array_size",
            "ds_session_character_set_for_non_unicode_columns",
            "ds_session_character_set_for_non_unicode_columns_character_set_name",
            "ds_session_default_length_for_columns",
            "ds_session_default_length_for_long_columns",
            "ds_session_fail_on_truncation",
            "ds_session_fetch_size",
            "ds_session_generate_all_columns_as_unicode",
            "ds_session_keep_conductor_connection_alive",
            "ds_session_report_schema_mismatch",
            "ds_table_name",
            "ds_transaction_auto_commit_mode",
            "ds_transaction_begin_end",
            "ds_transaction_begin_end_begin_sql",
            "ds_transaction_begin_end_end_sql",
            "ds_transaction_begin_end_run_end_sql_if_no_records_processed",
            "ds_transaction_end_of_wave",
            "ds_transaction_isolation_level",
            "ds_transaction_record_count",
            "ds_use_datastage",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_sql",
            "enable_before_sql_node",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execution_mode",
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "flow_dirty",
            "generate_unicode_type_columns",
            "has_reference_output",
            "hide",
            "infer_schema",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_column_names",
            "lookup_type",
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
            "push_filters",
            "pushed_filters",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_method",
            "rejected_filters",
            "row_limit",
            "runtime_column_propagation",
            "sampling_percentage",
            "sampling_seed",
            "sampling_type",
            "schema_name",
            "select_statement",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "table_name",
            "unique",
        }
        required = {
            "current_output_link_type",
            "ds_select_statement",
            "ds_session_character_set_for_non_unicode_columns_character_set_name",
            "ds_table_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname_or_ip_address",
            "keytab_file",
            "output_acp_should_hide",
            "password",
            "port",
            "select_statement",
            "service_principal_name",
            "table_name",
            "user_principal_name",
            "username",
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

    def get_target_props(self) -> dict:
        include, exclude = self.validate_target()
        props = {
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "create_data_asset",
            "current_output_link_type",
            "data_asset_name",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_before_after",
            "ds_before_after_after_sql",
            "ds_before_after_after_sql_fail_on_error",
            "ds_before_after_after_sql_node",
            "ds_before_after_after_sql_node_fail_on_error",
            "ds_before_after_after_sql_node_read_from_file_after_sql_node",
            "ds_before_after_after_sql_read_from_file_after_sql",
            "ds_before_after_before_sql",
            "ds_before_after_before_sql_fail_on_error",
            "ds_before_after_before_sql_node",
            "ds_before_after_before_sql_node_fail_on_error",
            "ds_before_after_before_sql_node_read_from_file_before_sql_node",
            "ds_before_after_before_sql_read_from_file_before_sql",
            "ds_custom_statements",
            "ds_custom_statements_read_from_file_custom",
            "ds_delete_statement",
            "ds_delete_statement_read_from_file_delete",
            "ds_enable_partitioned_write",
            "ds_enable_quoted_ids",
            "ds_generate_sql",
            "ds_hive_parameters",
            "ds_hive_parameters_fail_on_error",
            "ds_insert_statement",
            "ds_insert_statement_read_from_file_insert",
            "ds_java_heap_size",
            "ds_record_ordering",
            "ds_record_ordering_key_column",
            "ds_session_array_size",
            "ds_session_batch_size",
            "ds_session_character_set_for_non_unicode_columns",
            "ds_session_character_set_for_non_unicode_columns_character_set_name",
            "ds_session_default_length_for_columns",
            "ds_session_default_length_for_long_columns",
            "ds_session_drop_unmatched_fields",
            "ds_session_keep_conductor_connection_alive",
            "ds_session_report_schema_mismatch",
            "ds_table_action",
            "ds_table_action_generate_create_statement",
            "ds_table_action_generate_create_statement_create_statement",
            "ds_table_action_generate_create_statement_fail_on_error",
            "ds_table_action_generate_create_statement_row_format",
            "ds_table_action_generate_create_statement_row_format_field_terminator",
            "ds_table_action_generate_create_statement_row_format_line_terminator",
            "ds_table_action_generate_create_statement_row_format_serde_library",
            "ds_table_action_generate_create_statement_storage_format",
            "ds_table_action_generate_create_statement_table_location",
            "ds_table_action_generate_drop_statement",
            "ds_table_action_generate_drop_statement_drop_statement",
            "ds_table_action_generate_drop_statement_fail_on_error",
            "ds_table_action_generate_truncate_statement",
            "ds_table_action_generate_truncate_statement_fail_on_error",
            "ds_table_action_generate_truncate_statement_truncate_statement",
            "ds_table_action_table_action_first",
            "ds_table_name",
            "ds_transaction_auto_commit_mode",
            "ds_transaction_begin_end",
            "ds_transaction_begin_end_begin_sql",
            "ds_transaction_begin_end_end_sql",
            "ds_transaction_begin_end_run_end_sql_if_no_records_processed",
            "ds_transaction_isolation_level",
            "ds_transaction_record_count",
            "ds_update_statement",
            "ds_update_statement_read_from_file_update",
            "ds_use_datastage",
            "ds_write_mode",
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
            "runtime_column_propagation",
            "schema_name",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "static_statement",
            "table_action",
            "table_name",
            "unique",
            "write_mode",
        }
        required = {
            "current_output_link_type",
            "data_asset_name",
            "ds_delete_statement",
            "ds_insert_statement",
            "ds_session_character_set_for_non_unicode_columns_character_set_name",
            "ds_table_action",
            "ds_table_action_generate_create_statement_create_statement",
            "ds_table_action_generate_create_statement_row_format_serde_library",
            "ds_table_action_generate_drop_statement_drop_statement",
            "ds_table_action_generate_truncate_statement_truncate_statement",
            "ds_table_name",
            "ds_update_statement",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname_or_ip_address",
            "keytab_file",
            "output_acp_should_hide",
            "password",
            "port",
            "service_principal_name",
            "static_statement",
            "table_name",
            "user_principal_name",
            "username",
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
            "ds_record_ordering",
            "ds_record_ordering_key_column",
            "execution_mode",
            "input_count",
            "output_count",
            "preserve_partitioning",
        }
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
        return {"min": 0, "max": -1}

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
