import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.oracle_datastage_connection import (
    OracleDatastageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.enums import ORACLE_DATASTAGE
from pydantic import Field
from typing import ClassVar


class oracle_datastage(BaseStage):

    op_name: ClassVar[str] = "OracleConnectorPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/OracleConnectorPX.svg"
    label: ClassVar[str] = "Oracle Database for DataStage"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: OracleDatastageConn = OracleDatastageConn()
    abort_when_create_table_statement_fails: bool | None = Field(
        True, alias="generate_create_statement.fail_on_error"
    )
    abort_when_drop_table_statement_fails: bool | None = Field(True, alias="generate_drop_statement.fail_on_error")
    abort_when_truncate_table_statement_fails: bool | None = Field(
        True, alias="generate_truncate_statement.fail_on_error"
    )
    after_sql_node_statement: str | None = Field(None, alias="after_sql_node")
    after_sql_statement: str | None = Field(None, alias="after_sql")
    allow_concurrent_load_sessions: bool | None = Field(True, alias="enable_parallel_load_sessions")
    array_size: int | None = Field(2000, alias="array_size")
    before_load: bool | None = Field(False, alias="before_load")
    before_load_disable_constraints: bool | None = Field(False, alias="before_load.disable_constraints")
    before_load_disable_triggers: bool | None = Field(False, alias="before_load.disable_triggers")
    before_sql_node_statement: str | None = Field(None, alias="before_sql_node")
    before_sql_statement: str | None = Field(None, alias="before_sql")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: ORACLE_DATASTAGE.BufModeRonly | None = Field(
        ORACLE_DATASTAGE.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffer_size: int | None = Field(1024, alias="buffer_size_in_kilobytes")
    buffering_mode: ORACLE_DATASTAGE.BufferingMode | None = Field(
        ORACLE_DATASTAGE.BufferingMode.default, alias="buf_mode"
    )
    cache_size: int | None = Field(1000, alias="cache_size")
    collecting: ORACLE_DATASTAGE.Collecting | None = Field(ORACLE_DATASTAGE.Collecting.auto, alias="coll_type")
    column_delimiter: ORACLE_DATASTAGE.ColumnDelimiter | None = Field(
        ORACLE_DATASTAGE.ColumnDelimiter.space, alias="delimiter"
    )
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    column_name_for_partitioned_reads: str = Field(None, alias="read_strategy_column_name")
    columns_for_lob_references: str = Field(None, alias="pass_lob_locator.column")
    combinability_mode: ORACLE_DATASTAGE.CombinabilityMode | None = Field(
        ORACLE_DATASTAGE.CombinabilityMode.auto, alias="combinability"
    )
    control_file_name: str | None = Field(None, alias="cont_file")
    create_table_statement: str = Field(None, alias="create_statement")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_file_name: str | None = Field(None, alias="data_file")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    degree_of_parallelism: int | None = Field(None, alias="degree_of_parallelism")
    delete_statement: str = Field(None, alias="delete_statement")
    directory_for_data_and_control_files: str | None = Field(None, alias="directory_cont_file")
    disable_cache_when_full: bool | None = Field(False, alias="disable_when_full")
    disable_logging: bool | None = Field(False, alias="disable_redo_log")
    disconnect: ORACLE_DATASTAGE.Disconnect | None = Field(ORACLE_DATASTAGE.Disconnect.never, alias="disconnect")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    drop_table_statement: str = Field(None, alias="drop_statement")
    drop_unmatched_fields: bool | None = Field(False, alias="drop_unmatched_fields")
    ds_record_ordering: ORACLE_DATASTAGE.DSRecordOrdering | None = Field(
        ORACLE_DATASTAGE.DSRecordOrdering.zero, alias="_record_ordering"
    )
    ds_record_ordering_key_column: list | None = Field([], alias="_record_ordering._key_column")
    enable_before_and_after_sql: bool | None = Field(False, alias="before_after")
    enable_constraints: bool | None = Field(False, alias="enable_constraints")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_lob_references: bool | None = Field(False, alias="pass_lob_locator")
    enable_partitioned_reads: bool | None = Field(False, alias="enable_partitioned_reads")
    enable_quoted_identifiers: bool | None = Field(True, alias="enable_quoted_ids")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    enable_triggers: bool | None = Field(False, alias="enable_triggers")
    exceptions_table_name: str | None = Field(None, alias="exceptions_table_name")
    execution_mode: ORACLE_DATASTAGE.ExecutionMode | None = Field(
        ORACLE_DATASTAGE.ExecutionMode.default_par, alias="execmode"
    )
    fail_for_data_truncation: bool | None = Field(True, alias="treat_fetch_truncate_as_error")
    fail_if_no_rows_are_deleted: bool | None = Field(False, alias="fail_if_no_rows_deleted")
    fail_if_no_rows_are_updated: bool | None = Field(False, alias="fail_if_no_rows_updated")
    fail_on_error_for_after_sql_node_statement: bool | None = Field(True, alias="after_sql_node.fail_on_error")
    fail_on_error_for_after_sql_statement: bool | None = Field(True, alias="after_sql.fail_on_error")
    fail_on_error_for_before_sql_node_statement: bool | None = Field(True, alias="before_sql_node.fail_on_error")
    fail_on_error_for_before_sql_statement: bool | None = Field(True, alias="before_sql.fail_on_error")
    fail_on_error_for_index_rebuilding: bool | None = Field(False, alias="fail_on_rebuild_index")
    fail_on_row_error_px: bool | None = Field(True, alias="fail_on_row_error_px")
    fail_on_row_error_se: bool | None = Field(False, alias="fail_on_row_error_se")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    generate_create_table_statement_at_runtime: bool | None = Field(False, alias="generate_create_statement")
    generate_drop_table_statement_at_runtime: bool | None = Field(False, alias="generate_drop_statement")
    generate_sql_at_runtime: bool | None = Field(False, alias="generate_sql")
    generate_truncate_table_statement_at_runtime: bool | None = Field(False, alias="generate_truncate_statement")
    has_reference_output: bool | None = Field(False, alias="has_ref_output")
    has_reject_output: bool | None = Field(False, alias="has_reject_output")
    hide: bool | None = Field(False, alias="hide")
    inactivity_period: int = Field(300, alias="inactivity_period")
    index_maintenance_option: ORACLE_DATASTAGE.IndexMaintenanceOption | None = Field(
        ORACLE_DATASTAGE.IndexMaintenanceOption.do_not_skip_unusable, alias="skip_indexes"
    )
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    input_link_ordering: list | None = Field(
        [{"link_label": "0", "link_name": "Link_62"}], alias="InputlinkOrderingList"
    )
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    insert_statement: str = Field(None, alias="insert_statement")
    interval_between_retries: int = Field(10, alias="retry_interval")
    isolation_level: ORACLE_DATASTAGE.IsolationLevel | None = Field(
        ORACLE_DATASTAGE.IsolationLevel.read_committed, alias="isolation_level"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    limit: int | None = Field(None, alias="limit")
    limit_number_of_returned_rows: bool | None = Field(False, alias="limit_rows")
    load_options: str | None = Field(None, alias="load_opt")
    log_column_values_on_first_row_error: bool | None = Field(False, alias="log_column_values")
    log_key_values_only: bool | None = Field(False, alias="log_keys_only")
    logging_clause: ORACLE_DATASTAGE.LoggingClause | None = Field(
        ORACLE_DATASTAGE.LoggingClause.logging, alias="logging_clause"
    )
    lookup_type: ORACLE_DATASTAGE.LookupType | None = Field(ORACLE_DATASTAGE.LookupType.empty, alias="lookup_type")
    manage_application_failover: bool | None = Field(False, alias="application_failover_control")
    manual_mode: bool | None = Field(None, alias="manual_mode")
    mark_end_of_wave: ORACLE_DATASTAGE.MarkEndOfWave | None = Field(
        ORACLE_DATASTAGE.MarkEndOfWave.no, alias="end_of_wave"
    )
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    number_of_retries: int | None = Field(10, alias="number_of_retries")
    other_clause: str | None = Field(None, alias="other_clause")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(1, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    parallel_clause: ORACLE_DATASTAGE.ParallelClause | None = Field(
        ORACLE_DATASTAGE.ParallelClause.do_not_include_parallel_clause, alias="parallel_clause"
    )
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    partition_name: str = Field(None, alias="partition_name")
    partition_or_subpartition_name_for_partitioned_reads: str | None = Field(
        None, alias="read_strategy_partition_name"
    )
    partition_type: ORACLE_DATASTAGE.PartitionType | None = Field(
        ORACLE_DATASTAGE.PartitionType.auto, alias="part_type"
    )
    partitioned_reads_method: ORACLE_DATASTAGE.PartitionedReadsMethod | None = Field(
        ORACLE_DATASTAGE.PartitionedReadsMethod.rowid_range, alias="partitioned_reads_strategy"
    )
    perform_operations_after_bulk_load: bool | None = Field(False, alias="after_load")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    perform_table_action_first: bool | None = Field(True, alias="table_action_first")
    pl_sql_block: str = Field(None, alias="pl_sql_statement")
    prefetch_buffer_size: int | None = Field(0, alias="prefetch_memory_size")
    prefetch_row_count: int | None = Field(1, alias="prefetch_row_count")
    preserve_partitioning: ORACLE_DATASTAGE.PreservePartitioning | None = Field(
        ORACLE_DATASTAGE.PreservePartitioning.default_propagate, alias="preserve"
    )
    preserve_trailing_blanks: bool | None = Field(True, alias="preserve_trailing_blanks")
    process_exception_rows: bool | None = Field(False, alias="process_exception_rows")
    process_warning_messages_as_fatal_errors: bool | None = Field(False, alias="treat_warnings_as_errors")
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    read_after_sql_node_statement_from_file: bool | None = Field(False, alias="after_sql_node.read_from_file")
    read_after_sql_statement_from_file: bool | None = Field(False, alias="after_sql.read_from_file")
    read_before_sql_node_statement_from_file: bool | None = Field(False, alias="before_sql_node.read_from_file")
    read_before_sql_statement_from_file: bool | None = Field(False, alias="before_sql.read_from_file")
    read_delete_statement_from_file: bool | None = Field(False, alias="read_from_file_delete")
    read_insert_statement_from_file: bool | None = Field(False, alias="read_from_file_insert")
    read_mode: ORACLE_DATASTAGE.ReadMode | None = Field(ORACLE_DATASTAGE.ReadMode.select, alias="read_mode")
    read_pl_sql_block_from_file: bool | None = Field(False, alias="read_from_file_pl_sql_block")
    read_select_statement_from_file: bool | None = Field(False, alias="read_from_file_select")
    read_update_statement_from_file: bool | None = Field(False, alias="read_from_file_update")
    rebuild_indexes: bool | None = Field(False, alias="rebuild_indexes")
    reconnect: bool | None = Field(False, alias="reconnect")
    record_count: int | None = Field(2000, alias="record_count")
    reject_condition_row_not_deleted_delete_mode: bool | None = Field(
        False, alias="reject_condition_row_not_deleted_delete_mode"
    )
    reject_condition_row_not_updated_insert_then_update_mode: bool | None = Field(
        False, alias="reject_condition_row_not_updated_insert_then_update_mode"
    )
    reject_condition_row_not_updated_update_mode: bool | None = Field(
        False, alias="reject_condition_row_not_updated_update_mode"
    )
    reject_condition_sql_error_character_set_conversion: bool | None = Field(
        False, alias="reject_condition_sql_error_character_set_conversion"
    )
    reject_condition_sql_error_constraint_violation: bool | None = Field(
        False, alias="reject_condition_sql_error_constraint_violation"
    )
    reject_condition_sql_error_data_truncation: bool | None = Field(
        False, alias="reject_condition_sql_error_data_truncation"
    )
    reject_condition_sql_error_data_type_conversion: bool | None = Field(
        False, alias="reject_condition_sql_error_data_type_conversion"
    )
    reject_condition_sql_error_other: bool | None = Field(False, alias="reject_condition_sql_error_other")
    reject_condition_sql_error_partitioning: bool | None = Field(
        False, alias="reject_condition_sql_error_partitioning"
    )
    reject_condition_sql_error_xml_processing: bool | None = Field(
        False, alias="reject_condition_sql_error_xml_processing"
    )
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_from_link: int | None = Field(None, alias="reject_from_link")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: ORACLE_DATASTAGE.RejectUses | None = Field(ORACLE_DATASTAGE.RejectUses.rows, alias="reject_uses")
    replay_before_sql_node_statement: bool | None = Field(False, alias="replay_before_sql_node")
    replay_before_sql_statement: bool | None = Field(False, alias="replay_before_sql")
    resume_write: bool | None = Field(False, alias="resume_write")
    retry_count: int = Field(3, alias="retry_count")
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    schema_name: str | None = Field(None, alias="schema_name")
    select_statement: str = Field(None, alias="select_statement")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: ORACLE_DATASTAGE.KeyColSelect | None = Field(
        ORACLE_DATASTAGE.KeyColSelect.default, alias="keyColSelect"
    )
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    subpartition_name: str = Field(None, alias="subpartition_name")
    table_action: ORACLE_DATASTAGE.TableAction = Field(ORACLE_DATASTAGE.TableAction.append, alias="table_action")
    table_name: str = Field(None, alias="table_name")
    table_name_for_partitioned_reads: str | None = Field(None, alias="read_strategy_table_name")
    table_name_for_partitioned_writes: str | None = Field(None, alias="write_strategy_table_name")
    table_scope: ORACLE_DATASTAGE.TableScope | None = Field(
        ORACLE_DATASTAGE.TableScope.entire_table, alias="table_scope"
    )
    time_between_retries: int | None = Field(10, alias="wait_time")
    transfer_bfile_contents: bool | None = Field(False, alias="transfer_bfile_cont")
    truncate_table_statement: str = Field(None, alias="truncate_statement")
    unique: bool | None = Field(None, alias="part_unique")
    update_statement: str = Field(None, alias="update_statement")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    use_oracle_date_cache: bool | None = Field(False, alias="use_date_cache")
    where_clause: str | None = Field(None, alias="where_clause")
    write_mode: ORACLE_DATASTAGE.WriteMode | None = Field(ORACLE_DATASTAGE.WriteMode.insert, alias="write_mode")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("preserve_partitioning")
            if (self.output_count and self.output_count > 0)
            else exclude.add("preserve_partitioning")
        )
        (
            include.add("reject_uses")
            if (self.reject_from_link and self.reject_from_link > -1)
            else exclude.add("reject_uses")
        )
        (
            include.add("reject_number")
            if (self.reject_from_link and self.reject_from_link > -1)
            else exclude.add("reject_number")
        )
        (
            include.add("reject_data_element_errorcode")
            if (self.reject_from_link and self.reject_from_link > -1)
            else exclude.add("reject_data_element_errorcode")
        )
        (
            include.add("reject_data_element_errortext")
            if (self.reject_from_link and self.reject_from_link > -1)
            else exclude.add("reject_data_element_errortext")
        )
        include.add("reject_threshold") if (self.reject_uses == "percent") else exclude.add("reject_threshold")
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
            include.add("disconnect")
            if (


                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )


            )
            else exclude.add("disconnect")
        )
        (
            include.add("read_before_sql_statement_from_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("read_before_sql_statement_from_file")
        )
        include.add("where_clause") if (self.generate_sql_at_runtime) else exclude.add("where_clause")
        (
            include.add("replay_before_sql_node_statement")
            if (self.manage_application_failover)
            else exclude.add("replay_before_sql_node_statement")
        )
        (
            include.add("after_sql_node_statement")
            if (self.enable_before_and_after_sql)
            else exclude.add("after_sql_node_statement")
        )
        (
            include.add("fail_on_error_for_after_sql_node_statement")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_for_after_sql_node_statement")
        )
        (
            include.add("select_statement")
            if (
                ((not self.table_name))
                and (not self.generate_sql_at_runtime)
                and (


                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                or (self.read_mode == "0")
                            )


                )
            )
            else exclude.add("select_statement")
        )
        (
            include.add("table_name")
            if (
                ((not self.select_statement))
                and (not self.read_select_statement_from_file)
                and (not self.pl_sql_block)
                and (not self.read_pl_sql_block_from_file)
                and (self.generate_sql_at_runtime)
            )
            else exclude.add("table_name")
        )
        (
            include.add("replay_before_sql_statement")
            if (self.manage_application_failover)
            else exclude.add("replay_before_sql_statement")
        )
        (
            include.add("read_before_sql_node_statement_from_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("read_before_sql_node_statement_from_file")
        )
        (
            include.add("pl_sql_block")
            if (



                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "1")
                                or (self.read_mode == "1")
                            )



            )
            else exclude.add("pl_sql_block")
        )
        (
            include.add("read_after_sql_node_statement_from_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("read_after_sql_node_statement_from_file")
        )
        (
            include.add("reconnect")
            if (
                (
                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                or (self.read_mode == "0")
                            )
                        )
                    )
                )
                and (

                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )

                )
            )
            else exclude.add("reconnect")
        )
        (
            include.add("partitioned_reads_method")
            if (self.enable_partitioned_reads)
            else exclude.add("partitioned_reads_method")
        )
        (
            include.add("subpartition_name")
            if (



                            self.table_scope
                            and (
                                (hasattr(self.table_scope, "value") and self.table_scope.value == "2")
                                or (self.table_scope == "2")
                            )



            )
            else exclude.add("subpartition_name")
        )
        (
            include.add("retry_count")
            if (
                (
                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                or (self.read_mode == "0")
                            )
                        )
                    )
                )
                and (self.reconnect)
                and (

                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )

                )
            )
            else exclude.add("retry_count")
        )
        (
            include.add("columns_for_lob_references")
            if (
                (
                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                or (self.read_mode == "0")
                            )
                        )
                    )
                )
                and (self.enable_lob_references)
            )
            else exclude.add("columns_for_lob_references")
        )
        (
            include.add("limit")
            if (
                ((self.limit_number_of_returned_rows))
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
            else exclude.add("limit")
        )
        (
            include.add("fail_on_error_for_after_sql_statement")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_for_after_sql_statement")
        )
        (
            include.add("fail_on_error_for_before_sql_node_statement")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_for_before_sql_node_statement")
        )
        (
            include.add("interval_between_retries")
            if (
                (
                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                or (self.read_mode == "0")
                            )
                        )
                    )
                )
                and (self.reconnect)
                and (

                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )

                )
            )
            else exclude.add("interval_between_retries")
        )
        (
            include.add("preserve_trailing_blanks")
            if (
                (
                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                or (self.read_mode == "0")
                            )
                        )
                    )
                )
                and (

                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )

                )
            )
            else exclude.add("preserve_trailing_blanks")
        )
        (
            include.add("read_after_sql_statement_from_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("read_after_sql_statement_from_file")
        )
        (
            include.add("array_size")
            if (
                (
                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                or (self.read_mode == "0")
                            )
                        )
                    )
                )
                and (not self.enable_lob_references)
            )
            else exclude.add("array_size")
        )
        (
            include.add("partition_name")
            if (



                            self.table_scope
                            and (
                                (hasattr(self.table_scope, "value") and self.table_scope.value == "1")
                                or (self.table_scope == "1")
                            )



            )
            else exclude.add("partition_name")
        )
        (
            include.add("number_of_retries")
            if (self.manage_application_failover)
            else exclude.add("number_of_retries")
        )
        (
            include.add("partition_or_subpartition_name_for_partitioned_reads")
            if (
                ((self.enable_partitioned_reads))
                and (
                    (
                        (
                            self.partitioned_reads_method
                            and (
                                (
                                    hasattr(self.partitioned_reads_method, "value")
                                    and self.partitioned_reads_method.value == "0"
                                )
                                or (self.partitioned_reads_method == "0")
                            )
                        )
                    )
                    or (

                            self.partitioned_reads_method
                            and (
                                (
                                    hasattr(self.partitioned_reads_method, "value")
                                    and self.partitioned_reads_method.value == "3"
                                )
                                or (self.partitioned_reads_method == "3")
                            )

                    )
                )
            )
            else exclude.add("partition_or_subpartition_name_for_partitioned_reads")
        )
        (
            include.add("before_sql_node_statement")
            if (self.enable_before_and_after_sql)
            else exclude.add("before_sql_node_statement")
        )
        include.add("resume_write") if (self.manage_application_failover) else exclude.add("resume_write")
        (
            include.add("before_sql_statement")
            if (self.enable_before_and_after_sql)
            else exclude.add("before_sql_statement")
        )
        (
            include.add("limit_number_of_returned_rows")
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
            else exclude.add("limit_number_of_returned_rows")
        )
        (
            include.add("time_between_retries")
            if (self.manage_application_failover)
            else exclude.add("time_between_retries")
        )
        (
            include.add("inactivity_period")
            if (
                (
                    (
                        (
                            self.disconnect
                            and (
                                (hasattr(self.disconnect, "value") and self.disconnect.value == "1")
                                or (self.disconnect == "1")
                            )
                        )
                    )
                )
                and (

                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )

                )
            )
            else exclude.add("inactivity_period")
        )
        (
            include.add("table_name_for_partitioned_reads")
            if (((self.enable_partitioned_reads)) and (not self.generate_sql_at_runtime))
            else exclude.add("table_name_for_partitioned_reads")
        )
        (
            include.add("after_sql_statement")
            if (self.enable_before_and_after_sql)
            else exclude.add("after_sql_statement")
        )
        (
            include.add("read_select_statement_from_file")
            if (
                ((not self.table_name))
                and (not self.generate_sql_at_runtime)
                and (


                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                or (self.read_mode == "0")
                            )


                )
            )
            else exclude.add("read_select_statement_from_file")
        )
        (
            include.add("column_name_for_partitioned_reads")
            if (
                ((self.enable_partitioned_reads))
                and (
                    (
                        (
                            self.partitioned_reads_method
                            and (
                                (
                                    hasattr(self.partitioned_reads_method, "value")
                                    and self.partitioned_reads_method.value == "2"
                                )
                                or (self.partitioned_reads_method == "2")
                            )
                        )
                    )
                    or (

                            self.partitioned_reads_method
                            and (
                                (
                                    hasattr(self.partitioned_reads_method, "value")
                                    and self.partitioned_reads_method.value == "3"
                                )
                                or (self.partitioned_reads_method == "3")
                            )

                    )
                )
            )
            else exclude.add("column_name_for_partitioned_reads")
        )
        (
            include.add("enable_lob_references")
            if (



                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                or (self.read_mode == "0")
                            )



            )
            else exclude.add("enable_lob_references")
        )
        (
            include.add("generate_sql_at_runtime")
            if (



                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                or (self.read_mode == "0")
                            )



            )
            else exclude.add("generate_sql_at_runtime")
        )
        include.add("table_scope") if (self.generate_sql_at_runtime) else exclude.add("table_scope")
        (
            include.add("read_pl_sql_block_from_file")
            if (



                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "1")
                                or (self.read_mode == "1")
                            )



            )
            else exclude.add("read_pl_sql_block_from_file")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("fail_on_error_for_before_sql_statement")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_for_before_sql_statement")
        )
        include.add("other_clause") if (self.generate_sql_at_runtime) else exclude.add("other_clause")
        (
            include.add("fail_for_data_truncation")
            if (not self.process_warning_messages_as_fatal_errors)
            else exclude.add("fail_for_data_truncation")
        )
        (
            include.add("disconnect")
            if (
                (
                    (
                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )
                    )
                )
                or (

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
            else exclude.add("disconnect")
        )
        (
            include.add("read_before_sql_statement_from_file")
            if (
                ((self.enable_before_and_after_sql))
                or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))
            )
            else exclude.add("read_before_sql_statement_from_file")
        )
        (
            include.add("where_clause")
            if (


                        ((self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("where_clause")
        )
        (
            include.add("replay_before_sql_node_statement")
            if (
                ((self.manage_application_failover))
                or (self.manage_application_failover and "#" in str(self.manage_application_failover))
            )
            else exclude.add("replay_before_sql_node_statement")
        )
        (
            include.add("after_sql_node_statement")
            if (
                ((self.enable_before_and_after_sql))
                or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))
            )
            else exclude.add("after_sql_node_statement")
        )
        (
            include.add("fail_on_error_for_after_sql_node_statement")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_for_after_sql_node_statement")
        )
        (
            include.add("select_statement")
            if (

                    (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                    and (
                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
                    )
                    and (
                        (
                            (
                                self.read_mode
                                and (
                                    (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                    or (self.read_mode == "0")
                                )
                            )
                        )
                        or (

                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value
                                        and "#" in str(self.read_mode.value)
                                    )
                                    or ("#" in str(self.read_mode))
                                )

                        )
                    )

            )
            else exclude.add("select_statement")
        )
        (
            include.add("table_name")
            if (

                    (((not self.select_statement)) or ((self.select_statement and "#" in str(self.select_statement))))
                    and (
                        ((not self.read_select_statement_from_file))
                        or (self.read_select_statement_from_file and "#" in str(self.read_select_statement_from_file))
                    )
                    and (((not self.pl_sql_block)) or (self.pl_sql_block and "#" in str(self.pl_sql_block)))
                    and (
                        ((not self.read_pl_sql_block_from_file))
                        or (self.read_pl_sql_block_from_file and "#" in str(self.read_pl_sql_block_from_file))
                    )
                    and (
                        ((self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
                    )

            )
            else exclude.add("table_name")
        )
        (
            include.add("replay_before_sql_statement")
            if (
                ((self.manage_application_failover))
                or (self.manage_application_failover and "#" in str(self.manage_application_failover))
            )
            else exclude.add("replay_before_sql_statement")
        )
        (
            include.add("read_before_sql_node_statement_from_file")
            if (
                ((self.enable_before_and_after_sql))
                or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))
            )
            else exclude.add("read_before_sql_node_statement_from_file")
        )
        (
            include.add("pl_sql_block")
            if (
                (
                    (
                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "1")
                            or (self.read_mode == "1")
                        )
                    )
                )
                or (

                        self.read_mode
                        and (
                            (
                                hasattr(self.read_mode, "value")
                                and self.read_mode.value
                                and "#" in str(self.read_mode.value)
                            )
                            or ("#" in str(self.read_mode))
                        )

                )
            )
            else exclude.add("pl_sql_block")
        )
        (
            include.add("read_after_sql_node_statement_from_file")
            if (
                ((self.enable_before_and_after_sql))
                or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))
            )
            else exclude.add("read_after_sql_node_statement_from_file")
        )
        (
            include.add("reconnect")
            if (

                    (
                        (
                            (
                                self.read_mode
                                and (
                                    (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                    or (self.read_mode == "0")
                                )
                            )
                        )
                        or (
                            (
                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value
                                        and "#" in str(self.read_mode.value)
                                    )
                                    or ("#" in str(self.read_mode))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.lookup_type
                                and (
                                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                                    or (self.lookup_type == "pxbridge")
                                )
                            )
                        )
                        or (

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
            else exclude.add("reconnect")
        )
        (
            include.add("partitioned_reads_method")
            if (


                        ((self.enable_partitioned_reads))
                        or (self.enable_partitioned_reads and "#" in str(self.enable_partitioned_reads))


            )
            else exclude.add("partitioned_reads_method")
        )
        (
            include.add("subpartition_name")
            if (
                (
                    (
                        self.table_scope
                        and (
                            (hasattr(self.table_scope, "value") and self.table_scope.value == "2")
                            or (self.table_scope == "2")
                        )
                    )
                )
                or (

                        self.table_scope
                        and (
                            (
                                hasattr(self.table_scope, "value")
                                and self.table_scope.value
                                and "#" in str(self.table_scope.value)
                            )
                            or ("#" in str(self.table_scope))
                        )

                )
            )
            else exclude.add("subpartition_name")
        )
        (
            include.add("retry_count")
            if (

                    (
                        (
                            (
                                self.read_mode
                                and (
                                    (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                    or (self.read_mode == "0")
                                )
                            )
                        )
                        or (
                            (
                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value
                                        and "#" in str(self.read_mode.value)
                                    )
                                    or ("#" in str(self.read_mode))
                                )
                            )
                        )
                    )
                    and (((self.reconnect)) or (self.reconnect and "#" in str(self.reconnect)))
                    and (
                        (
                            (
                                self.lookup_type
                                and (
                                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                                    or (self.lookup_type == "pxbridge")
                                )
                            )
                        )
                        or (

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
            else exclude.add("retry_count")
        )
        (
            include.add("columns_for_lob_references")
            if (

                    (
                        (
                            (
                                self.read_mode
                                and (
                                    (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                    or (self.read_mode == "0")
                                )
                            )
                        )
                        or (
                            (
                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value
                                        and "#" in str(self.read_mode.value)
                                    )
                                    or ("#" in str(self.read_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.enable_lob_references))
                        or (self.enable_lob_references and "#" in str(self.enable_lob_references))
                    )

            )
            else exclude.add("columns_for_lob_references")
        )
        (
            include.add("limit")
            if (

                    (
                        ((self.limit_number_of_returned_rows))
                        or ((self.limit_number_of_returned_rows and "#" in str(self.limit_number_of_returned_rows)))
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
                        or (

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
            else exclude.add("limit")
        )
        (
            include.add("fail_on_error_for_after_sql_statement")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_for_after_sql_statement")
        )
        (
            include.add("fail_on_error_for_before_sql_node_statement")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_for_before_sql_node_statement")
        )
        (
            include.add("interval_between_retries")
            if (

                    (
                        (
                            (
                                self.read_mode
                                and (
                                    (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                    or (self.read_mode == "0")
                                )
                            )
                        )
                        or (
                            (
                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value
                                        and "#" in str(self.read_mode.value)
                                    )
                                    or ("#" in str(self.read_mode))
                                )
                            )
                        )
                    )
                    and (((self.reconnect)) or (self.reconnect and "#" in str(self.reconnect)))
                    and (
                        (
                            (
                                self.lookup_type
                                and (
                                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                                    or (self.lookup_type == "pxbridge")
                                )
                            )
                        )
                        or (

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
            else exclude.add("interval_between_retries")
        )
        (
            include.add("preserve_trailing_blanks")
            if (

                    (
                        (
                            (
                                self.read_mode
                                and (
                                    (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                    or (self.read_mode == "0")
                                )
                            )
                        )
                        or (
                            (
                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value
                                        and "#" in str(self.read_mode.value)
                                    )
                                    or ("#" in str(self.read_mode))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.lookup_type
                                and (
                                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                                    or (self.lookup_type == "pxbridge")
                                )
                            )
                        )
                        or (

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
            else exclude.add("preserve_trailing_blanks")
        )
        (
            include.add("read_after_sql_statement_from_file")
            if (
                ((self.enable_before_and_after_sql))
                or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))
            )
            else exclude.add("read_after_sql_statement_from_file")
        )
        (
            include.add("array_size")
            if (

                    (
                        (
                            (
                                self.read_mode
                                and (
                                    (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                    or (self.read_mode == "0")
                                )
                            )
                        )
                        or (
                            (
                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value
                                        and "#" in str(self.read_mode.value)
                                    )
                                    or ("#" in str(self.read_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((not self.enable_lob_references))
                        or (self.enable_lob_references and "#" in str(self.enable_lob_references))
                    )

            )
            else exclude.add("array_size")
        )
        (
            include.add("partition_name")
            if (
                (
                    (
                        self.table_scope
                        and (
                            (hasattr(self.table_scope, "value") and self.table_scope.value == "1")
                            or (self.table_scope == "1")
                        )
                    )
                )
                or (

                        self.table_scope
                        and (
                            (
                                hasattr(self.table_scope, "value")
                                and self.table_scope.value
                                and "#" in str(self.table_scope.value)
                            )
                            or ("#" in str(self.table_scope))
                        )

                )
            )
            else exclude.add("partition_name")
        )
        (
            include.add("number_of_retries")
            if (
                ((self.manage_application_failover))
                or (self.manage_application_failover and "#" in str(self.manage_application_failover))
            )
            else exclude.add("number_of_retries")
        )
        (
            include.add("partition_or_subpartition_name_for_partitioned_reads")
            if (

                    (
                        ((self.enable_partitioned_reads))
                        or ((self.enable_partitioned_reads and "#" in str(self.enable_partitioned_reads)))
                    )
                    and (
                        (
                            (
                                self.partitioned_reads_method
                                and (
                                    (
                                        hasattr(self.partitioned_reads_method, "value")
                                        and self.partitioned_reads_method.value == "0"
                                    )
                                    or (self.partitioned_reads_method == "0")
                                )
                            )
                        )
                        or (

                                self.partitioned_reads_method
                                and (
                                    (
                                        hasattr(self.partitioned_reads_method, "value")
                                        and self.partitioned_reads_method.value == "3"
                                    )
                                    or (self.partitioned_reads_method == "3")
                                )

                        )
                        or (

                                self.partitioned_reads_method
                                and (
                                    (
                                        hasattr(self.partitioned_reads_method, "value")
                                        and self.partitioned_reads_method.value
                                        and "#" in str(self.partitioned_reads_method.value)
                                    )
                                    or ("#" in str(self.partitioned_reads_method))
                                )

                        )
                    )

            )
            else exclude.add("partition_or_subpartition_name_for_partitioned_reads")
        )
        (
            include.add("before_sql_node_statement")
            if (
                ((self.enable_before_and_after_sql))
                or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))
            )
            else exclude.add("before_sql_node_statement")
        )
        (
            include.add("resume_write")
            if (


                        ((self.manage_application_failover))
                        or (self.manage_application_failover and "#" in str(self.manage_application_failover))


            )
            else exclude.add("resume_write")
        )
        (
            include.add("before_sql_statement")
            if (
                ((self.enable_before_and_after_sql))
                or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))
            )
            else exclude.add("before_sql_statement")
        )
        (
            include.add("limit_number_of_returned_rows")
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
                or (

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
            else exclude.add("limit_number_of_returned_rows")
        )
        (
            include.add("time_between_retries")
            if (
                ((self.manage_application_failover))
                or (self.manage_application_failover and "#" in str(self.manage_application_failover))
            )
            else exclude.add("time_between_retries")
        )
        (
            include.add("inactivity_period")
            if (

                    (
                        (
                            (
                                self.disconnect
                                and (
                                    (hasattr(self.disconnect, "value") and self.disconnect.value == "1")
                                    or (self.disconnect == "1")
                                )
                            )
                        )
                        or (
                            (
                                self.disconnect
                                and (
                                    (
                                        hasattr(self.disconnect, "value")
                                        and self.disconnect.value
                                        and "#" in str(self.disconnect.value)
                                    )
                                    or ("#" in str(self.disconnect))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.lookup_type
                                and (
                                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                                    or (self.lookup_type == "pxbridge")
                                )
                            )
                        )
                        or (

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
            else exclude.add("inactivity_period")
        )
        (
            include.add("table_name_for_partitioned_reads")
            if (

                    (
                        ((self.enable_partitioned_reads))
                        or ((self.enable_partitioned_reads and "#" in str(self.enable_partitioned_reads)))
                    )
                    and (
                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
                    )

            )
            else exclude.add("table_name_for_partitioned_reads")
        )
        (
            include.add("after_sql_statement")
            if (
                ((self.enable_before_and_after_sql))
                or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))
            )
            else exclude.add("after_sql_statement")
        )
        (
            include.add("read_select_statement_from_file")
            if (

                    (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                    and (
                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
                    )
                    and (
                        (
                            (
                                self.read_mode
                                and (
                                    (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                                    or (self.read_mode == "0")
                                )
                            )
                        )
                        or (

                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value
                                        and "#" in str(self.read_mode.value)
                                    )
                                    or ("#" in str(self.read_mode))
                                )

                        )
                    )

            )
            else exclude.add("read_select_statement_from_file")
        )
        (
            include.add("column_name_for_partitioned_reads")
            if (

                    (
                        ((self.enable_partitioned_reads))
                        or ((self.enable_partitioned_reads and "#" in str(self.enable_partitioned_reads)))
                    )
                    and (
                        (
                            (
                                self.partitioned_reads_method
                                and (
                                    (
                                        hasattr(self.partitioned_reads_method, "value")
                                        and self.partitioned_reads_method.value == "2"
                                    )
                                    or (self.partitioned_reads_method == "2")
                                )
                            )
                        )
                        or (

                                self.partitioned_reads_method
                                and (
                                    (
                                        hasattr(self.partitioned_reads_method, "value")
                                        and self.partitioned_reads_method.value == "3"
                                    )
                                    or (self.partitioned_reads_method == "3")
                                )

                        )
                        or (

                                self.partitioned_reads_method
                                and (
                                    (
                                        hasattr(self.partitioned_reads_method, "value")
                                        and self.partitioned_reads_method.value
                                        and "#" in str(self.partitioned_reads_method.value)
                                    )
                                    or ("#" in str(self.partitioned_reads_method))
                                )

                        )
                    )

            )
            else exclude.add("column_name_for_partitioned_reads")
        )
        (
            include.add("enable_lob_references")
            if (
                (
                    (
                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                            or (self.read_mode == "0")
                        )
                    )
                )
                or (

                        self.read_mode
                        and (
                            (
                                hasattr(self.read_mode, "value")
                                and self.read_mode.value
                                and "#" in str(self.read_mode.value)
                            )
                            or ("#" in str(self.read_mode))
                        )

                )
            )
            else exclude.add("enable_lob_references")
        )
        (
            include.add("generate_sql_at_runtime")
            if (
                (
                    (
                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "0")
                            or (self.read_mode == "0")
                        )
                    )
                )
                or (

                        self.read_mode
                        and (
                            (
                                hasattr(self.read_mode, "value")
                                and self.read_mode.value
                                and "#" in str(self.read_mode.value)
                            )
                            or ("#" in str(self.read_mode))
                        )

                )
            )
            else exclude.add("generate_sql_at_runtime")
        )
        (
            include.add("table_scope")
            if (
                ((self.generate_sql_at_runtime))
                or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
            )
            else exclude.add("table_scope")
        )
        (
            include.add("read_pl_sql_block_from_file")
            if (
                (
                    (
                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "1")
                            or (self.read_mode == "1")
                        )
                    )
                )
                or (

                        self.read_mode
                        and (
                            (
                                hasattr(self.read_mode, "value")
                                and self.read_mode.value
                                and "#" in str(self.read_mode.value)
                            )
                            or ("#" in str(self.read_mode))
                        )

                )
            )
            else exclude.add("read_pl_sql_block_from_file")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("fail_on_error_for_before_sql_statement")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_for_before_sql_statement")
        )
        (
            include.add("other_clause")
            if (


                        ((self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("other_clause")
        )
        (
            include.add("fail_for_data_truncation")
            if (
                ((not self.process_warning_messages_as_fatal_errors))
                or (

                        self.process_warning_messages_as_fatal_errors
                        and "#" in str(self.process_warning_messages_as_fatal_errors)

                )
            )
            else exclude.add("fail_for_data_truncation")
        )
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
        include.add("use_cas_lite_service") if (((()) or (())) and (())) else exclude.add("use_cas_lite_service")
        include.add("use_cas_lite_service") if (()) else exclude.add("use_cas_lite_service")
        include.add("defer_credentials") if (()) else exclude.add("defer_credentials")
        (
            include.add("replay_before_sql_node_statement")
            if (self.manage_application_failover == "true" or self.manage_application_failover)
            else exclude.add("replay_before_sql_node_statement")
        )
        (
            include.add("before_sql_node_statement")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("before_sql_node_statement")
        )
        (
            include.add("interval_between_retries")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "0" in str(self.read_mode.value))
                    or ("0" in str(self.read_mode))
                )
            )
            and (self.reconnect == "true" or self.reconnect)
            and (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("interval_between_retries")
        )
        (
            include.add("preserve_trailing_blanks")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "0" in str(self.read_mode.value))
                    or ("0" in str(self.read_mode))
                )
            )
            and (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("preserve_trailing_blanks")
        )
        (
            include.add("reconnect")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "0" in str(self.read_mode.value))
                    or ("0" in str(self.read_mode))
                )
            )
            and (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("reconnect")
        )
        (
            include.add("limit_number_of_returned_rows")
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
            else exclude.add("limit_number_of_returned_rows")
        )
        (
            include.add("generate_sql_at_runtime")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "0" in str(self.read_mode.value))
                    or ("0" in str(self.read_mode))
                )
            )
            else exclude.add("generate_sql_at_runtime")
        )
        (
            include.add("read_select_statement_from_file")
            if (not self.table_name)
            and (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "0" in str(self.read_mode.value))
                    or ("0" in str(self.read_mode))
                )
            )
            else exclude.add("read_select_statement_from_file")
        )
        (
            include.add("fail_on_error_for_before_sql_node_statement")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_for_before_sql_node_statement")
        )
        (
            include.add("read_before_sql_statement_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_before_sql_statement_from_file")
        )
        (
            include.add("enable_lob_references")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "0" in str(self.read_mode.value))
                    or ("0" in str(self.read_mode))
                )
            )
            else exclude.add("enable_lob_references")
        )
        (
            include.add("inactivity_period")
            if (
                self.disconnect
                and (
                    (hasattr(self.disconnect, "value") and self.disconnect.value and "1" in str(self.disconnect.value))
                    or ("1" in str(self.disconnect))
                )
            )
            and (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("inactivity_period")
        )
        (
            include.add("fail_on_error_for_before_sql_statement")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_for_before_sql_statement")
        )
        (
            include.add("before_sql_statement")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("before_sql_statement")
        )
        (
            include.add("fail_on_error_for_after_sql_node_statement")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_for_after_sql_node_statement")
        )
        (
            include.add("read_before_sql_node_statement_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_before_sql_node_statement_from_file")
        )
        (
            include.add("partitioned_reads_method")
            if (self.enable_partitioned_reads == "true" or self.enable_partitioned_reads)
            else exclude.add("partitioned_reads_method")
        )
        (
            include.add("table_name_for_partitioned_reads")
            if (self.enable_partitioned_reads == "true" or self.enable_partitioned_reads)
            and (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("table_name_for_partitioned_reads")
        )
        (
            include.add("after_sql_statement")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("after_sql_statement")
        )
        (
            include.add("pl_sql_block")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "1" in str(self.read_mode.value))
                    or ("1" in str(self.read_mode))
                )
            )
            else exclude.add("pl_sql_block")
        )
        (
            include.add("after_sql_node_statement")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("after_sql_node_statement")
        )
        (
            include.add("read_after_sql_node_statement_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_after_sql_node_statement_from_file")
        )
        (
            include.add("other_clause")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("other_clause")
        )
        (
            include.add("limit")
            if (self.limit_number_of_returned_rows == "true" or self.limit_number_of_returned_rows)
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
            else exclude.add("limit")
        )
        (
            include.add("partition_or_subpartition_name_for_partitioned_reads")
            if (self.enable_partitioned_reads == "true" or self.enable_partitioned_reads)
            and (
                self.partitioned_reads_method
                and (
                    (
                        hasattr(self.partitioned_reads_method, "value")
                        and self.partitioned_reads_method.value
                        and "0" in str(self.partitioned_reads_method.value)
                    )
                    or ("0" in str(self.partitioned_reads_method))
                )
                and self.partitioned_reads_method
                and (
                    (
                        hasattr(self.partitioned_reads_method, "value")
                        and self.partitioned_reads_method.value
                        and "3" in str(self.partitioned_reads_method.value)
                    )
                    or ("3" in str(self.partitioned_reads_method))
                )
            )
            else exclude.add("partition_or_subpartition_name_for_partitioned_reads")
        )
        (
            include.add("number_of_retries")
            if (self.manage_application_failover == "true" or self.manage_application_failover)
            else exclude.add("number_of_retries")
        )
        (
            include.add("replay_before_sql_statement")
            if (self.manage_application_failover == "true" or self.manage_application_failover)
            else exclude.add("replay_before_sql_statement")
        )
        (
            include.add("array_size")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "0" in str(self.read_mode.value))
                    or ("0" in str(self.read_mode))
                )
            )
            and (self.enable_lob_references == "false" or not self.enable_lob_references)
            else exclude.add("array_size")
        )
        (
            include.add("read_after_sql_statement_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_after_sql_statement_from_file")
        )
        (
            include.add("disconnect")
            if (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("disconnect")
        )
        (
            include.add("where_clause")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("where_clause")
        )
        (
            include.add("lookup_type")
            if (self.has_reference_output == "true" or self.has_reference_output)
            else exclude.add("lookup_type")
        )
        (
            include.add("read_pl_sql_block_from_file")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "1" in str(self.read_mode.value))
                    or ("1" in str(self.read_mode))
                )
            )
            else exclude.add("read_pl_sql_block_from_file")
        )
        (
            include.add("partition_name")
            if (
                self.table_scope
                and (
                    (
                        hasattr(self.table_scope, "value")
                        and self.table_scope.value
                        and "1" in str(self.table_scope.value)
                    )
                    or ("1" in str(self.table_scope))
                )
            )
            else exclude.add("partition_name")
        )
        (
            include.add("subpartition_name")
            if (
                self.table_scope
                and (
                    (
                        hasattr(self.table_scope, "value")
                        and self.table_scope.value
                        and "2" in str(self.table_scope.value)
                    )
                    or ("2" in str(self.table_scope))
                )
            )
            else exclude.add("subpartition_name")
        )
        (
            include.add("table_scope")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("table_scope")
        )
        (
            include.add("column_name_for_partitioned_reads")
            if (self.enable_partitioned_reads == "true" or self.enable_partitioned_reads)
            and (
                self.partitioned_reads_method
                and (
                    (
                        hasattr(self.partitioned_reads_method, "value")
                        and self.partitioned_reads_method.value
                        and "2" in str(self.partitioned_reads_method.value)
                    )
                    or ("2" in str(self.partitioned_reads_method))
                )
                and self.partitioned_reads_method
                and (
                    (
                        hasattr(self.partitioned_reads_method, "value")
                        and self.partitioned_reads_method.value
                        and "3" in str(self.partitioned_reads_method.value)
                    )
                    or ("3" in str(self.partitioned_reads_method))
                )
            )
            else exclude.add("column_name_for_partitioned_reads")
        )
        (
            include.add("columns_for_lob_references")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "0" in str(self.read_mode.value))
                    or ("0" in str(self.read_mode))
                )
            )
            and (self.enable_lob_references == "true" or self.enable_lob_references)
            else exclude.add("columns_for_lob_references")
        )
        (
            include.add("table_name")
            if (not self.select_statement)
            and (not self.read_select_statement_from_file)
            and (not self.pl_sql_block)
            and (not self.read_pl_sql_block_from_file)
            and (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("table_name")
        )
        (
            include.add("select_statement")
            if (not self.table_name)
            and (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "0" in str(self.read_mode.value))
                    or ("0" in str(self.read_mode))
                )
            )
            else exclude.add("select_statement")
        )
        (
            include.add("fail_for_data_truncation")
            if (
                self.process_warning_messages_as_fatal_errors == "false"
                or not self.process_warning_messages_as_fatal_errors
            )
            else exclude.add("fail_for_data_truncation")
        )
        (
            include.add("fail_on_error_for_after_sql_statement")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_for_after_sql_statement")
        )
        (
            include.add("time_between_retries")
            if (self.manage_application_failover == "true" or self.manage_application_failover)
            else exclude.add("time_between_retries")
        )
        (
            include.add("resume_write")
            if (self.manage_application_failover == "true" or self.manage_application_failover)
            else exclude.add("resume_write")
        )
        (
            include.add("retry_count")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "0" in str(self.read_mode.value))
                    or ("0" in str(self.read_mode))
                )
            )
            and (self.reconnect == "true" or self.reconnect)
            and (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("retry_count")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("log_column_values_on_first_row_error")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                or (self.write_mode == "8")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )

            )
            else exclude.add("log_column_values_on_first_row_error")
        )
        include.add("control_file_name") if (self.manual_mode) else exclude.add("control_file_name")
        (
            include.add("table_name")
            if (
                ((self.generate_sql_at_runtime))
                or (self.generate_truncate_table_statement_at_runtime)
                or (self.generate_drop_table_statement_at_runtime)
                or (self.generate_create_table_statement_at_runtime)
                or (


                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "6")
                                or (self.write_mode == "6")
                            )


                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("fail_if_no_rows_are_updated")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )

            )
            else exclude.add("fail_if_no_rows_are_updated")
        )
        (
            include.add("fail_if_no_rows_are_deleted")
            if (



                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )



            )
            else exclude.add("fail_if_no_rows_are_deleted")
        )
        (
            include.add("column_delimiter")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                or (self.write_mode == "8")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )

            )
            else exclude.add("column_delimiter")
        )
        (
            include.add("retry_count")
            if (
                (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                or (self.write_mode == "8")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )
                        )
                    )
                )
                and (self.reconnect)
            )
            else exclude.add("retry_count")
        )
        (
            include.add("drop_table_statement")
            if (
                ((not self.generate_drop_table_statement_at_runtime))
                and (


                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "2")
                                or (self.table_action == "2")
                            )


                )
            )
            else exclude.add("drop_table_statement")
        )
        (
            include.add("create_table_statement")
            if (
                ((not self.generate_create_table_statement_at_runtime))
                and (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "1")
                                or (self.table_action == "1")
                            )
                        )
                    )
                    or (

                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "2")
                                or (self.table_action == "2")
                            )

                    )
                )
            )
            else exclude.add("create_table_statement")
        )
        (
            include.add("truncate_table_statement")
            if (
                ((not self.generate_truncate_table_statement_at_runtime))
                and (


                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "3")
                                or (self.table_action == "3")
                            )


                )
            )
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("interval_between_retries")
            if (
                (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                or (self.write_mode == "8")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )
                        )
                    )
                )
                and (self.reconnect)
            )
            else exclude.add("interval_between_retries")
        )
        (
            include.add("fail_on_row_error_px")
            if (not self.has_reject_output)
            else exclude.add("fail_on_row_error_px")
        )
        (
            include.add("array_size")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "6")
                                or (self.write_mode == "6")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )

            )
            else exclude.add("array_size")
        )
        (
            include.add("table_name_for_partitioned_writes")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "0")
                                or (self.table_action == "0")
                            )
                        )
                    )
                )
                and (not self.generate_sql_at_runtime)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )
                )
            )
            else exclude.add("table_name_for_partitioned_writes")
        )
        (
            include.add("delete_statement")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                )
            )
            else exclude.add("delete_statement")
        )
        include.add("cache_size") if (self.use_oracle_date_cache) else exclude.add("cache_size")
        (
            include.add("abort_when_drop_table_statement_fails")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "2")
                                or (self.table_action == "2")
                            )
                        )
                    )
                )
                or (self.generate_drop_table_statement_at_runtime)
            )
            else exclude.add("abort_when_drop_table_statement_fails")
        )
        (
            include.add("abort_when_create_table_statement_fails")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "1")
                                or (self.table_action == "1")
                            )
                        )
                    )
                    or (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "2")
                                or (self.table_action == "2")
                            )
                        )
                    )
                )
                or (self.generate_create_table_statement_at_runtime)
            )
            else exclude.add("abort_when_create_table_statement_fails")
        )
        (
            include.add("read_pl_sql_block_from_file")
            if (



                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                or (self.write_mode == "8")
                            )



            )
            else exclude.add("read_pl_sql_block_from_file")
        )
        (
            include.add("table_scope")
            if (
                ((self.generate_sql_at_runtime))
                or (


                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "6")
                                or (self.write_mode == "6")
                            )


                )
            )
            else exclude.add("table_scope")
        )
        (
            include.add("generate_create_table_statement_at_runtime")
            if (

                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "1")
                                or (self.table_action == "1")
                            )
                        )
                    )
                    or (

                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "2")
                                or (self.table_action == "2")
                            )

                    )

            )
            else exclude.add("generate_create_table_statement_at_runtime")
        )
        (
            include.add("record_count")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                or (self.write_mode == "8")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )

            )
            else exclude.add("record_count")
        )
        (
            include.add("generate_drop_table_statement_at_runtime")
            if (



                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "2")
                                or (self.table_action == "2")
                            )



            )
            else exclude.add("generate_drop_table_statement_at_runtime")
        )
        (
            include.add("read_insert_statement_from_file")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )
                )
            )
            else exclude.add("read_insert_statement_from_file")
        )
        (
            include.add("read_update_statement_from_file")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                )
            )
            else exclude.add("read_update_statement_from_file")
        )
        (
            include.add("read_delete_statement_from_file")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                )
            )
            else exclude.add("read_delete_statement_from_file")
        )
        (
            include.add("process_exception_rows")
            if (self.exceptions_table_name != "")
            else exclude.add("process_exception_rows")
        )
        (
            include.add("insert_statement")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )
                )
            )
            else exclude.add("insert_statement")
        )
        (
            include.add("generate_truncate_table_statement_at_runtime")
            if (



                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "3")
                                or (self.table_action == "3")
                            )



            )
            else exclude.add("generate_truncate_table_statement_at_runtime")
        )
        (
            include.add("pl_sql_block")
            if (



                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                or (self.write_mode == "8")
                            )



            )
            else exclude.add("pl_sql_block")
        )
        (
            include.add("reconnect")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                or (self.write_mode == "8")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )

            )
            else exclude.add("reconnect")
        )
        (
            include.add("abort_when_truncate_table_statement_fails")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "3")
                                or (self.table_action == "3")
                            )
                        )
                    )
                )
                or (self.generate_truncate_table_statement_at_runtime)
            )
            else exclude.add("abort_when_truncate_table_statement_fails")
        )
        (
            include.add("update_statement")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                )
            )
            else exclude.add("update_statement")
        )
        include.add("load_options") if (self.manual_mode) else exclude.add("load_options")
        (
            include.add("log_key_values_only")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                or (self.write_mode == "8")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )

            )
            else exclude.add("log_key_values_only")
        )
        include.add("buffer_size") if (self.allow_concurrent_load_sessions) else exclude.add("buffer_size")
        (
            include.add("resume_write")
            if (
                (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )
                        )
                    )
                )
                and (self.manage_application_failover)
            )
            else exclude.add("resume_write")
        )
        (
            include.add("isolation_level")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                or (self.write_mode == "8")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )

            )
            else exclude.add("isolation_level")
        )
        (
            include.add("inactivity_period")
            if (



                            self.disconnect
                            and (
                                (hasattr(self.disconnect, "value") and self.disconnect.value == "1")
                                or (self.disconnect == "1")
                            )



            )
            else exclude.add("inactivity_period")
        )
        (
            include.add("generate_sql_at_runtime")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                or (self.write_mode == "0")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                or (self.write_mode == "1")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                or (self.write_mode == "2")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                or (self.write_mode == "3")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                or (self.write_mode == "4")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                or (self.write_mode == "5")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                or (self.write_mode == "9")
                            )

                    )

            )
            else exclude.add("generate_sql_at_runtime")
        )
        (
            include.add("log_column_values_on_first_row_error")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                            or (self.write_mode == "0")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                            or (self.write_mode == "1")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                            or (self.write_mode == "2")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                            or (self.write_mode == "3")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                            or (self.write_mode == "4")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                            or (self.write_mode == "5")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                            or (self.write_mode == "8")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                            or (self.write_mode == "9")
                        )

                )
                or (

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
            else exclude.add("log_column_values_on_first_row_error")
        )
        (
            include.add("control_file_name")
            if (((self.manual_mode)) or (self.manual_mode and "#" in str(self.manual_mode)))
            else exclude.add("control_file_name")
        )
        (
            include.add("table_name")
            if (
                ((self.generate_sql_at_runtime))
                or (self.generate_truncate_table_statement_at_runtime)
                or (self.generate_drop_table_statement_at_runtime)
                or (self.generate_create_table_statement_at_runtime)
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "6")
                                or (self.write_mode == "6")
                            )
                        )
                    )
                    or (

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
                or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
                or (

                        self.generate_truncate_table_statement_at_runtime
                        and "#" in str(self.generate_truncate_table_statement_at_runtime)

                )
                or (

                        self.generate_drop_table_statement_at_runtime
                        and "#" in str(self.generate_drop_table_statement_at_runtime)

                )
                or (

                        self.generate_create_table_statement_at_runtime
                        and "#" in str(self.generate_create_table_statement_at_runtime)

                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("fail_if_no_rows_are_updated")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                            or (self.write_mode == "1")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                            or (self.write_mode == "3")
                        )

                )
                or (

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
            else exclude.add("fail_if_no_rows_are_updated")
        )
        (
            include.add("fail_if_no_rows_are_deleted")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                            or (self.write_mode == "2")
                        )
                    )
                )
                or (

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
            else exclude.add("fail_if_no_rows_are_deleted")
        )
        (
            include.add("column_delimiter")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                            or (self.write_mode == "0")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                            or (self.write_mode == "1")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                            or (self.write_mode == "2")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                            or (self.write_mode == "3")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                            or (self.write_mode == "4")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                            or (self.write_mode == "5")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                            or (self.write_mode == "8")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                            or (self.write_mode == "9")
                        )

                )
                or (

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
            else exclude.add("column_delimiter")
        )
        (
            include.add("retry_count")
            if (

                    (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                    or (self.write_mode == "0")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                    or (self.write_mode == "1")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                    or (self.write_mode == "2")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                    or (self.write_mode == "3")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                    or (self.write_mode == "4")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                    or (self.write_mode == "5")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                    or (self.write_mode == "8")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                    or (self.write_mode == "9")
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
                    and (((self.reconnect)) or (self.reconnect and "#" in str(self.reconnect)))

            )
            else exclude.add("retry_count")
        )
        (
            include.add("drop_table_statement")
            if (

                    (
                        ((not self.generate_drop_table_statement_at_runtime))
                        or (
                            (
                                self.generate_drop_table_statement_at_runtime
                                and "#" in str(self.generate_drop_table_statement_at_runtime)
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "2")
                                    or (self.table_action == "2")
                                )
                            )
                        )
                        or (

                                self.table_action
                                and (
                                    (
                                        hasattr(self.table_action, "value")
                                        and self.table_action.value
                                        and "#" in str(self.table_action.value)
                                    )
                                    or ("#" in str(self.table_action))
                                )

                        )
                    )

            )
            else exclude.add("drop_table_statement")
        )
        (
            include.add("create_table_statement")
            if (

                    (
                        ((not self.generate_create_table_statement_at_runtime))
                        or (
                            (
                                self.generate_create_table_statement_at_runtime
                                and "#" in str(self.generate_create_table_statement_at_runtime)
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "1")
                                    or (self.table_action == "1")
                                )
                            )
                        )
                        or (

                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "2")
                                    or (self.table_action == "2")
                                )

                        )
                        or (

                                self.table_action
                                and (
                                    (
                                        hasattr(self.table_action, "value")
                                        and self.table_action.value
                                        and "#" in str(self.table_action.value)
                                    )
                                    or ("#" in str(self.table_action))
                                )

                        )
                    )

            )
            else exclude.add("create_table_statement")
        )
        (
            include.add("truncate_table_statement")
            if (

                    (
                        ((not self.generate_truncate_table_statement_at_runtime))
                        or (
                            (
                                self.generate_truncate_table_statement_at_runtime
                                and "#" in str(self.generate_truncate_table_statement_at_runtime)
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "3")
                                    or (self.table_action == "3")
                                )
                            )
                        )
                        or (

                                self.table_action
                                and (
                                    (
                                        hasattr(self.table_action, "value")
                                        and self.table_action.value
                                        and "#" in str(self.table_action.value)
                                    )
                                    or ("#" in str(self.table_action))
                                )

                        )
                    )

            )
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("interval_between_retries")
            if (

                    (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                    or (self.write_mode == "0")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                    or (self.write_mode == "1")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                    or (self.write_mode == "2")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                    or (self.write_mode == "3")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                    or (self.write_mode == "4")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                    or (self.write_mode == "5")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                                    or (self.write_mode == "8")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                    or (self.write_mode == "9")
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
                    and (((self.reconnect)) or (self.reconnect and "#" in str(self.reconnect)))

            )
            else exclude.add("interval_between_retries")
        )
        (
            include.add("fail_on_row_error_px")
            if (not self.has_reject_output)
            else exclude.add("fail_on_row_error_px")
        )
        (
            include.add("array_size")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                            or (self.write_mode == "0")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                            or (self.write_mode == "1")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                            or (self.write_mode == "2")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                            or (self.write_mode == "3")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                            or (self.write_mode == "4")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                            or (self.write_mode == "5")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "6")
                            or (self.write_mode == "6")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                            or (self.write_mode == "9")
                        )

                )
                or (

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
            else exclude.add("array_size")
        )
        (
            include.add("table_name_for_partitioned_writes")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "0")
                                    or (self.table_action == "0")
                                )
                            )
                        )
                        or (
                            (
                                self.table_action
                                and (
                                    (
                                        hasattr(self.table_action, "value")
                                        and self.table_action.value
                                        and "#" in str(self.table_action.value)
                                    )
                                    or ("#" in str(self.table_action))
                                )
                            )
                        )
                    )
                    and (
                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                    or (self.write_mode == "0")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                    or (self.write_mode == "1")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                    or (self.write_mode == "2")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                    or (self.write_mode == "3")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                    or (self.write_mode == "4")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                    or (self.write_mode == "5")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                    or (self.write_mode == "9")
                                )

                        )
                        or (

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
            else exclude.add("table_name_for_partitioned_writes")
        )
        (
            include.add("delete_statement")
            if (

                    (
                        ((not self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                    or (self.write_mode == "2")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                    or (self.write_mode == "5")
                                )

                        )
                        or (

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
            else exclude.add("delete_statement")
        )
        (
            include.add("cache_size")
            if (
                ((self.use_oracle_date_cache))
                or (self.use_oracle_date_cache and "#" in str(self.use_oracle_date_cache))
            )
            else exclude.add("cache_size")
        )
        (
            include.add("abort_when_drop_table_statement_fails")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "2")
                                or (self.table_action == "2")
                            )
                        )
                    )
                    or (
                        (
                            self.table_action
                            and (
                                (
                                    hasattr(self.table_action, "value")
                                    and self.table_action.value
                                    and "#" in str(self.table_action.value)
                                )
                                or ("#" in str(self.table_action))
                            )
                        )
                    )
                )
                or (self.generate_drop_table_statement_at_runtime)
                or (

                        self.generate_drop_table_statement_at_runtime
                        and "#" in str(self.generate_drop_table_statement_at_runtime)

                )
            )
            else exclude.add("abort_when_drop_table_statement_fails")
        )
        (
            include.add("abort_when_create_table_statement_fails")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "1")
                                or (self.table_action == "1")
                            )
                        )
                    )
                    or (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "2")
                                or (self.table_action == "2")
                            )
                        )
                    )
                    or (
                        (
                            self.table_action
                            and (
                                (
                                    hasattr(self.table_action, "value")
                                    and self.table_action.value
                                    and "#" in str(self.table_action.value)
                                )
                                or ("#" in str(self.table_action))
                            )
                        )
                    )
                )
                or (self.generate_create_table_statement_at_runtime)
                or (

                        self.generate_create_table_statement_at_runtime
                        and "#" in str(self.generate_create_table_statement_at_runtime)

                )
            )
            else exclude.add("abort_when_create_table_statement_fails")
        )
        (
            include.add("read_pl_sql_block_from_file")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                            or (self.write_mode == "8")
                        )
                    )
                )
                or (

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
            else exclude.add("read_pl_sql_block_from_file")
        )
        (
            include.add("table_scope")
            if (
                ((self.generate_sql_at_runtime))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "6")
                                or (self.write_mode == "6")
                            )
                        )
                    )
                    or (

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
                or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
            )
            else exclude.add("table_scope")
        )
        (
            include.add("generate_create_table_statement_at_runtime")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "1")
                            or (self.table_action == "1")
                        )
                    )
                )
                or (

                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "2")
                            or (self.table_action == "2")
                        )

                )
                or (

                        self.table_action
                        and (
                            (
                                hasattr(self.table_action, "value")
                                and self.table_action.value
                                and "#" in str(self.table_action.value)
                            )
                            or ("#" in str(self.table_action))
                        )

                )
            )
            else exclude.add("generate_create_table_statement_at_runtime")
        )
        (
            include.add("record_count")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                            or (self.write_mode == "0")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                            or (self.write_mode == "1")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                            or (self.write_mode == "2")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                            or (self.write_mode == "3")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                            or (self.write_mode == "4")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                            or (self.write_mode == "5")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                            or (self.write_mode == "8")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                            or (self.write_mode == "9")
                        )

                )
                or (

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
            else exclude.add("record_count")
        )
        (
            include.add("generate_drop_table_statement_at_runtime")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "2")
                            or (self.table_action == "2")
                        )
                    )
                )
                or (

                        self.table_action
                        and (
                            (
                                hasattr(self.table_action, "value")
                                and self.table_action.value
                                and "#" in str(self.table_action.value)
                            )
                            or ("#" in str(self.table_action))
                        )

                )
            )
            else exclude.add("generate_drop_table_statement_at_runtime")
        )
        (
            include.add("read_insert_statement_from_file")
            if (

                    (
                        ((not self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                    or (self.write_mode == "0")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                    or (self.write_mode == "3")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                    or (self.write_mode == "4")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                    or (self.write_mode == "5")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                    or (self.write_mode == "9")
                                )

                        )
                        or (

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
            else exclude.add("read_insert_statement_from_file")
        )
        (
            include.add("read_update_statement_from_file")
            if (

                    (
                        ((not self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                    or (self.write_mode == "1")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                    or (self.write_mode == "3")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                    or (self.write_mode == "4")
                                )

                        )
                        or (

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
            else exclude.add("read_update_statement_from_file")
        )
        (
            include.add("read_delete_statement_from_file")
            if (

                    (
                        ((not self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                    or (self.write_mode == "2")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                    or (self.write_mode == "5")
                                )

                        )
                        or (

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
            else exclude.add("read_delete_statement_from_file")
        )
        (
            include.add("process_exception_rows")
            if (
                ((self.exceptions_table_name != ""))
                or (self.exceptions_table_name and "#" in str(self.exceptions_table_name))
            )
            else exclude.add("process_exception_rows")
        )
        (
            include.add("insert_statement")
            if (

                    (
                        ((not self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                    or (self.write_mode == "0")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                    or (self.write_mode == "3")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                    or (self.write_mode == "4")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                    or (self.write_mode == "5")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                    or (self.write_mode == "9")
                                )

                        )
                        or (

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
            else exclude.add("insert_statement")
        )
        (
            include.add("generate_truncate_table_statement_at_runtime")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "3")
                            or (self.table_action == "3")
                        )
                    )
                )
                or (

                        self.table_action
                        and (
                            (
                                hasattr(self.table_action, "value")
                                and self.table_action.value
                                and "#" in str(self.table_action.value)
                            )
                            or ("#" in str(self.table_action))
                        )

                )
            )
            else exclude.add("generate_truncate_table_statement_at_runtime")
        )
        (
            include.add("pl_sql_block")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                            or (self.write_mode == "8")
                        )
                    )
                )
                or (

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
            else exclude.add("pl_sql_block")
        )
        (
            include.add("reconnect")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                            or (self.write_mode == "0")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                            or (self.write_mode == "1")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                            or (self.write_mode == "2")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                            or (self.write_mode == "3")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                            or (self.write_mode == "4")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                            or (self.write_mode == "5")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                            or (self.write_mode == "8")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                            or (self.write_mode == "9")
                        )

                )
                or (

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
            else exclude.add("reconnect")
        )
        (
            include.add("abort_when_truncate_table_statement_fails")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "3")
                                or (self.table_action == "3")
                            )
                        )
                    )
                    or (
                        (
                            self.table_action
                            and (
                                (
                                    hasattr(self.table_action, "value")
                                    and self.table_action.value
                                    and "#" in str(self.table_action.value)
                                )
                                or ("#" in str(self.table_action))
                            )
                        )
                    )
                )
                or (self.generate_truncate_table_statement_at_runtime)
                or (

                        self.generate_truncate_table_statement_at_runtime
                        and "#" in str(self.generate_truncate_table_statement_at_runtime)

                )
            )
            else exclude.add("abort_when_truncate_table_statement_fails")
        )
        (
            include.add("update_statement")
            if (

                    (
                        ((not self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                    or (self.write_mode == "1")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                    or (self.write_mode == "3")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                    or (self.write_mode == "4")
                                )

                        )
                        or (

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
            else exclude.add("update_statement")
        )
        (
            include.add("load_options")
            if (((self.manual_mode)) or (self.manual_mode and "#" in str(self.manual_mode)))
            else exclude.add("load_options")
        )
        (
            include.add("log_key_values_only")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                            or (self.write_mode == "0")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                            or (self.write_mode == "1")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                            or (self.write_mode == "2")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                            or (self.write_mode == "3")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                            or (self.write_mode == "4")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                            or (self.write_mode == "5")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                            or (self.write_mode == "8")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                            or (self.write_mode == "9")
                        )

                )
                or (

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
            else exclude.add("log_key_values_only")
        )
        (
            include.add("buffer_size")
            if (
                ((self.allow_concurrent_load_sessions))
                or (self.allow_concurrent_load_sessions and "#" in str(self.allow_concurrent_load_sessions))
            )
            else exclude.add("buffer_size")
        )
        (
            include.add("resume_write")
            if (

                    (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                                    or (self.write_mode == "0")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                                    or (self.write_mode == "1")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                                    or (self.write_mode == "2")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                                    or (self.write_mode == "3")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                                    or (self.write_mode == "4")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                                    or (self.write_mode == "5")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                                    or (self.write_mode == "9")
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
                        ((self.manage_application_failover))
                        or (self.manage_application_failover and "#" in str(self.manage_application_failover))
                    )

            )
            else exclude.add("resume_write")
        )
        (
            include.add("isolation_level")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                            or (self.write_mode == "0")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                            or (self.write_mode == "1")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                            or (self.write_mode == "2")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                            or (self.write_mode == "3")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                            or (self.write_mode == "4")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                            or (self.write_mode == "5")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "8")
                            or (self.write_mode == "8")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                            or (self.write_mode == "9")
                        )

                )
                or (

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
            else exclude.add("isolation_level")
        )
        (
            include.add("inactivity_period")
            if (
                (
                    (
                        self.disconnect
                        and (
                            (hasattr(self.disconnect, "value") and self.disconnect.value == "1")
                            or (self.disconnect == "1")
                        )
                    )
                )
                or (

                        self.disconnect
                        and (
                            (
                                hasattr(self.disconnect, "value")
                                and self.disconnect.value
                                and "#" in str(self.disconnect.value)
                            )
                            or ("#" in str(self.disconnect))
                        )

                )
            )
            else exclude.add("inactivity_period")
        )
        (
            include.add("generate_sql_at_runtime")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "0")
                            or (self.write_mode == "0")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "1")
                            or (self.write_mode == "1")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "2")
                            or (self.write_mode == "2")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "3")
                            or (self.write_mode == "3")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "4")
                            or (self.write_mode == "4")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "5")
                            or (self.write_mode == "5")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "9")
                            or (self.write_mode == "9")
                        )

                )
                or (

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
            else exclude.add("generate_sql_at_runtime")
        )
        (
            include.add("column_delimiter")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "8" in str(self.write_mode.value))
                    or ("8" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("column_delimiter")
        )
        (
            include.add("generate_truncate_table_statement_at_runtime")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "3" in str(self.table_action.value)
                    )
                    or ("3" in str(self.table_action))
                )
            )
            else exclude.add("generate_truncate_table_statement_at_runtime")
        )
        (
            include.add("table_name_for_partitioned_writes")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "0" in str(self.table_action.value)
                    )
                    or ("0" in str(self.table_action))
                )
            )
            and (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("table_name_for_partitioned_writes")
        )
        (
            include.add("read_update_statement_from_file")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
            )
            else exclude.add("read_update_statement_from_file")
        )
        (
            include.add("inactivity_period")
            if (
                self.disconnect
                and (
                    (hasattr(self.disconnect, "value") and self.disconnect.value and "1" in str(self.disconnect.value))
                    or ("1" in str(self.disconnect))
                )
            )
            else exclude.add("inactivity_period")
        )
        (
            include.add("drop_table_statement")
            if (
                self.generate_drop_table_statement_at_runtime == "false"
                or not self.generate_drop_table_statement_at_runtime
            )
            and (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "2" in str(self.table_action.value)
                    )
                    or ("2" in str(self.table_action))
                )
            )
            else exclude.add("drop_table_statement")
        )
        (
            include.add("create_table_statement")
            if (
                self.generate_create_table_statement_at_runtime == "false"
                or not self.generate_create_table_statement_at_runtime
            )
            and (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "1" in str(self.table_action.value)
                    )
                    or ("1" in str(self.table_action))
                )
                and self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "2" in str(self.table_action.value)
                    )
                    or ("2" in str(self.table_action))
                )
            )
            else exclude.add("create_table_statement")
        )
        (
            include.add("record_count")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "8" in str(self.write_mode.value))
                    or ("8" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("record_count")
        )
        (
            include.add("isolation_level")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "8" in str(self.write_mode.value))
                    or ("8" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("isolation_level")
        )
        (
            include.add("generate_create_table_statement_at_runtime")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "1" in str(self.table_action.value)
                    )
                    or ("1" in str(self.table_action))
                )
                or self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "2" in str(self.table_action.value)
                    )
                    or ("2" in str(self.table_action))
                )
            )
            else exclude.add("generate_create_table_statement_at_runtime")
        )
        (
            include.add("fail_if_no_rows_are_updated")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
            )
            else exclude.add("fail_if_no_rows_are_updated")
        )
        (
            include.add("table_scope")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            or (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "6" in str(self.write_mode.value))
                    or ("6" in str(self.write_mode))
                )
            )
            else exclude.add("table_scope")
        )
        (
            include.add("abort_when_drop_table_statement_fails")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "2" in str(self.table_action.value)
                    )
                    or ("2" in str(self.table_action))
                )
            )
            or (
                self.generate_drop_table_statement_at_runtime == "true"
                or self.generate_drop_table_statement_at_runtime
            )
            else exclude.add("abort_when_drop_table_statement_fails")
        )
        (
            include.add("table_name")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            or (
                self.generate_truncate_table_statement_at_runtime == "true"
                or self.generate_truncate_table_statement_at_runtime
            )
            or (
                self.generate_drop_table_statement_at_runtime == "true"
                or self.generate_drop_table_statement_at_runtime
            )
            or (
                self.generate_create_table_statement_at_runtime == "true"
                or self.generate_create_table_statement_at_runtime
            )
            or (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "6" in str(self.write_mode.value))
                    or ("6" in str(self.write_mode))
                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("insert_statement")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("insert_statement")
        )
        (
            include.add("log_column_values_on_first_row_error")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "8" in str(self.write_mode.value))
                    or ("8" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("log_column_values_on_first_row_error")
        )
        (
            include.add("abort_when_truncate_table_statement_fails")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "3" in str(self.table_action.value)
                    )
                    or ("3" in str(self.table_action))
                )
            )
            or (
                self.generate_truncate_table_statement_at_runtime == "true"
                or self.generate_truncate_table_statement_at_runtime
            )
            else exclude.add("abort_when_truncate_table_statement_fails")
        )
        (
            include.add("resume_write")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            and (self.manage_application_failover == "true" or self.manage_application_failover)
            else exclude.add("resume_write")
        )
        (
            include.add("delete_statement")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
            )
            else exclude.add("delete_statement")
        )
        (
            include.add("retry_count")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "8" in str(self.write_mode.value))
                    or ("8" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            and (self.reconnect == "true" or self.reconnect)
            else exclude.add("retry_count")
        )
        (
            include.add("fail_if_no_rows_are_deleted")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
            )
            else exclude.add("fail_if_no_rows_are_deleted")
        )
        (
            include.add("interval_between_retries")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "8" in str(self.write_mode.value))
                    or ("8" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            and (self.reconnect == "true" or self.reconnect)
            else exclude.add("interval_between_retries")
        )
        (
            include.add("reconnect")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "8" in str(self.write_mode.value))
                    or ("8" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("reconnect")
        )
        (
            include.add("generate_sql_at_runtime")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("generate_sql_at_runtime")
        )
        (
            include.add("cache_size")
            if (self.use_oracle_date_cache == "true" or self.use_oracle_date_cache)
            else exclude.add("cache_size")
        )
        (
            include.add("buffer_size")
            if (self.allow_concurrent_load_sessions == "true" or self.allow_concurrent_load_sessions)
            else exclude.add("buffer_size")
        )
        (
            include.add("log_key_values_only")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "8" in str(self.write_mode.value))
                    or ("8" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("log_key_values_only")
        )
        (
            include.add("fail_on_row_error_px")
            if (self.has_reject_output == "false" or not self.has_reject_output)
            else exclude.add("fail_on_row_error_px")
        )
        (
            include.add("generate_drop_table_statement_at_runtime")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "2" in str(self.table_action.value)
                    )
                    or ("2" in str(self.table_action))
                )
            )
            else exclude.add("generate_drop_table_statement_at_runtime")
        )
        (
            include.add("pl_sql_block")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "8" in str(self.write_mode.value))
                    or ("8" in str(self.write_mode))
                )
            )
            else exclude.add("pl_sql_block")
        )
        (
            include.add("update_statement")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
            )
            else exclude.add("update_statement")
        )
        (
            include.add("array_size")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "1" in str(self.write_mode.value))
                    or ("1" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "6" in str(self.write_mode.value))
                    or ("6" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("array_size")
        )
        (
            include.add("control_file_name")
            if (self.manual_mode == "true" or self.manual_mode)
            else exclude.add("control_file_name")
        )
        (
            include.add("read_pl_sql_block_from_file")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "8" in str(self.write_mode.value))
                    or ("8" in str(self.write_mode))
                )
            )
            else exclude.add("read_pl_sql_block_from_file")
        )
        (
            include.add("read_insert_statement_from_file")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "0" in str(self.write_mode.value))
                    or ("0" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "3" in str(self.write_mode.value))
                    or ("3" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "4" in str(self.write_mode.value))
                    or ("4" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "9" in str(self.write_mode.value))
                    or ("9" in str(self.write_mode))
                )
            )
            else exclude.add("read_insert_statement_from_file")
        )
        (
            include.add("truncate_table_statement")
            if (
                self.generate_truncate_table_statement_at_runtime == "false"
                or not self.generate_truncate_table_statement_at_runtime
            )
            and (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "3" in str(self.table_action.value)
                    )
                    or ("3" in str(self.table_action))
                )
            )
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("load_options")
            if (self.manual_mode == "true" or self.manual_mode)
            else exclude.add("load_options")
        )
        (
            include.add("read_delete_statement_from_file")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "2" in str(self.write_mode.value))
                    or ("2" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value and "5" in str(self.write_mode.value))
                    or ("5" in str(self.write_mode))
                )
            )
            else exclude.add("read_delete_statement_from_file")
        )
        (
            include.add("process_exception_rows")
            if (self.exceptions_table_name != "")
            else exclude.add("process_exception_rows")
        )
        (
            include.add("abort_when_create_table_statement_fails")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "1" in str(self.table_action.value)
                    )
                    or ("1" in str(self.table_action))
                )
                or self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "2" in str(self.table_action.value)
                    )
                    or ("2" in str(self.table_action))
                )
            )
            or (
                self.generate_create_table_statement_at_runtime == "true"
                or self.generate_create_table_statement_at_runtime
            )
            else exclude.add("abort_when_create_table_statement_fails")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "after_sql_node_statement",
            "after_sql_statement",
            "array_size",
            "before_sql_node_statement",
            "before_sql_statement",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "collecting",
            "column_metadata_change_propagation",
            "column_name_for_partitioned_reads",
            "columns_for_lob_references",
            "combinability_mode",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disconnect",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_record_ordering",
            "ds_record_ordering_key_column",
            "enable_before_and_after_sql",
            "enable_flow_acp_control",
            "enable_lob_references",
            "enable_partitioned_reads",
            "enable_quoted_identifiers",
            "enable_schemaless_design",
            "execution_mode",
            "fail_for_data_truncation",
            "fail_on_error_for_after_sql_node_statement",
            "fail_on_error_for_after_sql_statement",
            "fail_on_error_for_before_sql_node_statement",
            "fail_on_error_for_before_sql_statement",
            "flow_dirty",
            "generate_sql_at_runtime",
            "has_reference_output",
            "hide",
            "inactivity_period",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "interval_between_retries",
            "isolation_level",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "limit",
            "limit_number_of_returned_rows",
            "lookup_type",
            "manage_application_failover",
            "mark_end_of_wave",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "number_of_retries",
            "other_clause",
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
            "partition_name",
            "partition_or_subpartition_name_for_partitioned_reads",
            "partition_type",
            "partitioned_reads_method",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "pl_sql_block",
            "prefetch_buffer_size",
            "prefetch_row_count",
            "preserve_partitioning",
            "preserve_trailing_blanks",
            "process_warning_messages_as_fatal_errors",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_after_sql_node_statement_from_file",
            "read_after_sql_statement_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statement_from_file",
            "read_mode",
            "read_pl_sql_block_from_file",
            "read_select_statement_from_file",
            "reconnect",
            "record_count",
            "replay_before_sql_node_statement",
            "replay_before_sql_statement",
            "resume_write",
            "retry_count",
            "row_limit",
            "runtime_column_propagation",
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
            "subpartition_name",
            "table_name",
            "table_name_for_partitioned_reads",
            "table_scope",
            "time_between_retries",
            "transfer_bfile_contents",
            "unique",
            "where_clause",
        }
        required = {
            "column_name_for_partitioned_reads",
            "columns_for_lob_references",
            "connection_string",
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname",
            "inactivity_period",
            "interval_between_retries",
            "output_acp_should_hide",
            "partition_name",
            "pl_sql_block",
            "port",
            "retry_count",
            "select_statement",
            "servicename",
            "subpartition_name",
            "table_name",
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
            "abort_when_create_table_statement_fails",
            "abort_when_drop_table_statement_fails",
            "abort_when_truncate_table_statement_fails",
            "after_sql_node_statement",
            "after_sql_statement",
            "allow_concurrent_load_sessions",
            "array_size",
            "before_load",
            "before_load_disable_constraints",
            "before_load_disable_triggers",
            "before_sql_node_statement",
            "before_sql_statement",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffer_size",
            "buffering_mode",
            "cache_size",
            "collecting",
            "column_delimiter",
            "column_metadata_change_propagation",
            "combinability_mode",
            "control_file_name",
            "create_table_statement",
            "current_output_link_type",
            "data_file_name",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "degree_of_parallelism",
            "delete_statement",
            "directory_for_data_and_control_files",
            "disable_cache_when_full",
            "disable_logging",
            "disconnect",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "drop_table_statement",
            "drop_unmatched_fields",
            "ds_record_ordering",
            "ds_record_ordering_key_column",
            "enable_before_and_after_sql",
            "enable_constraints",
            "enable_flow_acp_control",
            "enable_quoted_identifiers",
            "enable_schemaless_design",
            "enable_triggers",
            "exceptions_table_name",
            "execution_mode",
            "fail_if_no_rows_are_deleted",
            "fail_if_no_rows_are_updated",
            "fail_on_error_for_after_sql_node_statement",
            "fail_on_error_for_after_sql_statement",
            "fail_on_error_for_before_sql_node_statement",
            "fail_on_error_for_before_sql_statement",
            "fail_on_error_for_index_rebuilding",
            "fail_on_row_error_px",
            "fail_on_row_error_se",
            "flow_dirty",
            "generate_create_table_statement_at_runtime",
            "generate_drop_table_statement_at_runtime",
            "generate_sql_at_runtime",
            "generate_truncate_table_statement_at_runtime",
            "has_reject_output",
            "hide",
            "inactivity_period",
            "index_maintenance_option",
            "input_count",
            "input_link_description",
            "input_link_ordering",
            "inputcol_properties",
            "insert_statement",
            "interval_between_retries",
            "isolation_level",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "load_options",
            "log_column_values_on_first_row_error",
            "log_key_values_only",
            "logging_clause",
            "manage_application_failover",
            "manual_mode",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "number_of_retries",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "parallel_clause",
            "part_stable_coll",
            "part_stable_ordered",
            "part_stable_roundrobin_coll",
            "part_unique_coll",
            "part_unique_ordered",
            "part_unique_roundrobin_coll",
            "partition_name",
            "partition_type",
            "perform_operations_after_bulk_load",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "perform_table_action_first",
            "pl_sql_block",
            "preserve_partitioning",
            "preserve_trailing_blanks",
            "process_exception_rows",
            "process_warning_messages_as_fatal_errors",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_after_sql_node_statement_from_file",
            "read_after_sql_statement_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statement_from_file",
            "read_delete_statement_from_file",
            "read_insert_statement_from_file",
            "read_pl_sql_block_from_file",
            "read_update_statement_from_file",
            "rebuild_indexes",
            "reconnect",
            "record_count",
            "replay_before_sql_node_statement",
            "replay_before_sql_statement",
            "resume_write",
            "retry_count",
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
            "subpartition_name",
            "table_action",
            "table_name",
            "table_name_for_partitioned_writes",
            "table_scope",
            "time_between_retries",
            "truncate_table_statement",
            "unique",
            "update_statement",
            "use_oracle_date_cache",
            "write_mode",
        }
        required = {
            "connection_string",
            "create_table_statement",
            "current_output_link_type",
            "delete_statement",
            "drop_table_statement",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname",
            "inactivity_period",
            "insert_statement",
            "interval_between_retries",
            "output_acp_should_hide",
            "partition_name",
            "pl_sql_block",
            "port",
            "retry_count",
            "servicename",
            "subpartition_name",
            "table_action",
            "table_name",
            "truncate_table_statement",
            "update_statement",
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
                "active": 1,
                "SupportsRef": True,
                "maxRejectOutputs": -1,
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
        props = {
            "reject_condition_row_not_deleted_delete_mode",
            "reject_condition_row_not_updated_insert_then_update_mode",
            "reject_condition_row_not_updated_update_mode",
            "reject_condition_sql_error_character_set_conversion",
            "reject_condition_sql_error_constraint_violation",
            "reject_condition_sql_error_data_truncation",
            "reject_condition_sql_error_data_type_conversion",
            "reject_condition_sql_error_other",
            "reject_condition_sql_error_partitioning",
            "reject_condition_sql_error_xml_processing",
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
        return self.model_dump(include=props - exclude, by_alias=True, exclude_none=True, warnings=False)

    def get_output_cardinality(self) -> dict:
        return {"min": 0, "max": 1}

    def get_allowed_as_source_props(self) -> bool:
        return True

    def get_allowed_as_target_props(self) -> bool:
        return True
