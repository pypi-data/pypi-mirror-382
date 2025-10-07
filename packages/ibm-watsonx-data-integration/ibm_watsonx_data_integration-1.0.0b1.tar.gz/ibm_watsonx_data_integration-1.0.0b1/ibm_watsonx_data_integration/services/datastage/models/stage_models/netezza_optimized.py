import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.netezza_optimized_connection import (
    NetezzaOptimizedConn,
)
from ibm_watsonx_data_integration.services.datastage.models.enums import NETEZZA_OPTIMIZED
from pydantic import Field
from typing import ClassVar


class netezza_optimized(BaseStage):

    op_name: ClassVar[str] = "NetezzaConnectorPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/NetezzaConnectorPX.svg"
    label: ClassVar[str] = "IBM Netezza Performance Server for DataStage"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: NetezzaOptimizedConn = NetezzaOptimizedConn()
    action_column: str = Field(None, alias="sql.action_column")
    after_sql: str | None = Field("", alias="before_after_sql.after_sql")
    after_sql_node: str | None = Field("", alias="before_after_sql.after_sql_node")
    array_size: int | None = Field(2000, alias="session.array_size")
    atomic_mode: bool | None = Field(True, alias="sql.atomic_mode")
    atomic_mode_after_sql: bool | None = Field(True, alias="before_after_sql.after_sql.fail_on_error.atomic_mode")
    atomic_mode_after_sql_node: bool | None = Field(
        True, alias="before_after_sql.after_sql_node.fail_on_error.atomic_mode"
    )
    atomic_mode_before_sql: bool | None = Field(True, alias="before_after_sql.before_sql.fail_on_error.atomic_mode")
    atomic_mode_before_sql_node: bool | None = Field(
        True, alias="before_after_sql.before_sql_node.fail_on_error.atomic_mode"
    )
    before_after_sql_after_sql_fail_on_error_log_level_for_after_sql: NETEZZA_OPTIMIZED.BeforeAfterSqlAfterSqlFailOnErrorLogLevelForAfterSql | None = Field(
        NETEZZA_OPTIMIZED.BeforeAfterSqlAfterSqlFailOnErrorLogLevelForAfterSql.warning,
        alias="before_after_sql.after_sql.fail_on_error.log_level_for_after_sql",
    )
    before_after_sql_after_sql_node_fail_on_error_log_level_for_after_sql_node: NETEZZA_OPTIMIZED.BeforeAfterSqlAfterSqlNodeFailOnErrorLogLevelForAfterSqlNode | None = Field(
        NETEZZA_OPTIMIZED.BeforeAfterSqlAfterSqlNodeFailOnErrorLogLevelForAfterSqlNode.warning,
        alias="before_after_sql.after_sql_node.fail_on_error.log_level_for_after_sql_node",
    )
    before_after_sql_after_sql_node_read_from_file: bool | None = Field(
        False, alias="before_after_sql.after_sql_node.read_from_file"
    )
    before_after_sql_after_sql_read_from_file: bool | None = Field(
        False, alias="before_after_sql.after_sql.read_from_file"
    )
    before_after_sql_before_sql_fail_on_error_log_level_for_before_sql: NETEZZA_OPTIMIZED.BeforeAfterSqlBeforeSqlFailOnErrorLogLevelForBeforeSql | None = Field(
        NETEZZA_OPTIMIZED.BeforeAfterSqlBeforeSqlFailOnErrorLogLevelForBeforeSql.warning,
        alias="before_after_sql.before_sql.fail_on_error.log_level_for_before_sql",
    )
    before_after_sql_before_sql_node_fail_on_error_log_level_for_before_sql_node: NETEZZA_OPTIMIZED.BeforeAfterSqlBeforeSqlNodeFailOnErrorLogLevelForBeforeSqlNode | None = Field(
        NETEZZA_OPTIMIZED.BeforeAfterSqlBeforeSqlNodeFailOnErrorLogLevelForBeforeSqlNode.warning,
        alias="before_after_sql.before_sql_node.fail_on_error.log_level_for_before_sql_node",
    )
    before_after_sql_before_sql_node_read_from_file: bool | None = Field(
        False, alias="before_after_sql.before_sql_node.read_from_file"
    )
    before_after_sql_before_sql_read_from_file: bool | None = Field(
        False, alias="before_after_sql.before_sql.read_from_file"
    )
    before_sql: str | None = Field("", alias="before_after_sql.before_sql")
    before_sql_node: str | None = Field("", alias="before_after_sql.before_sql_node")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: NETEZZA_OPTIMIZED.BufModeRonly | None = Field(
        NETEZZA_OPTIMIZED.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: NETEZZA_OPTIMIZED.BufferingMode | None = Field(
        NETEZZA_OPTIMIZED.BufferingMode.default, alias="buf_mode"
    )
    byte_limit: str | None = Field(None, alias="byte_limit")
    check_duplicate_rows: bool | None = Field(False, alias="sql.check_duplicate_rows")
    collecting: NETEZZA_OPTIMIZED.Collecting | None = Field(NETEZZA_OPTIMIZED.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    column_name: str | None = Field(None, alias="sql.enable_record_ordering.order_key.column_name")
    combinability_mode: NETEZZA_OPTIMIZED.CombinabilityMode | None = Field(
        NETEZZA_OPTIMIZED.CombinabilityMode.auto, alias="combinability"
    )
    create_statement: str | None = Field("", alias="session.temporary_work_table.create_statement")
    create_table_statement: str = Field("", alias="table_action.generate_create_statement.create_statement")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    direct_insert: bool | None = Field(False, alias="sql.direct_insert")
    directory_for_log_files: str | None = Field(None, alias="session.load_options.directory_for_log_files")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    distribution_key: NETEZZA_OPTIMIZED.TableActionGenerateCreateStatementDistributionKey | None = Field(
        NETEZZA_OPTIMIZED.TableActionGenerateCreateStatementDistributionKey.random,
        alias="table_action.generate_create_statement.distribution_key",
    )
    drop_table: bool | None = Field(True, alias="session.temporary_work_table.drop_table")
    drop_table_statement: str = Field("", alias="table_action.generate_drop_statement.drop_statement")
    duplicate_row_action: NETEZZA_OPTIMIZED.SqlCheckDuplicateRowsDuplicateRowAction | None = Field(
        NETEZZA_OPTIMIZED.SqlCheckDuplicateRowsDuplicateRowAction.filter,
        alias="sql.check_duplicate_rows.duplicate_row_action",
    )
    enable_before_after_sql_for_child_element: bool | None = Field(False, alias="before_after_sql")
    enable_case_sensitive_identifiers: bool | None = Field(True, alias="enable_case_sensitive_i_ds")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_partitioned_reads: bool | None = Field(False, alias="sql.enable_partitioned_reads")
    enable_record_ordering: bool | None = Field(False, alias="sql.enable_record_ordering")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    enable_use_of_merge_join_plan_type: NETEZZA_OPTIMIZED.SessionTemporaryWorkTableEnableMergeJoin | None = Field(
        NETEZZA_OPTIMIZED.SessionTemporaryWorkTableEnableMergeJoin.database_default,
        alias="session.temporary_work_table.enable_merge_join",
    )
    execution_mode: NETEZZA_OPTIMIZED.ExecutionMode | None = Field(
        NETEZZA_OPTIMIZED.ExecutionMode.default_par, alias="execmode"
    )
    fail_on_error_after_sql: bool | None = Field(True, alias="before_after_sql.after_sql.fail_on_error")
    fail_on_error_after_sql_node: bool | None = Field(True, alias="before_after_sql.after_sql_node.fail_on_error")
    fail_on_error_before_sql: bool | None = Field(True, alias="before_after_sql.before_sql.fail_on_error")
    fail_on_error_before_sql_node: bool | None = Field(True, alias="before_after_sql.before_sql_node.fail_on_error")
    fail_on_error_create_statement: bool | None = Field(
        True, alias="table_action.generate_create_statement.fail_on_error"
    )
    fail_on_error_drop_statement: bool | None = Field(
        False, alias="table_action.generate_drop_statement.fail_on_error"
    )
    fail_on_error_truncate_statement: bool | None = Field(
        True, alias="table_action.generate_truncate_statement.fail_on_error"
    )
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    generate_create_statement_at_runtime: bool | None = Field(True, alias="table_action.generate_create_statement")
    generate_create_statement_distribution_key_column_names: str = Field(
        "", alias="table_action.generate_create_statement.distribution_key.key_columns"
    )
    generate_drop_statement_at_runtime: bool | None = Field(True, alias="table_action.generate_drop_statement")
    generate_sql_at_runtime: bool | None = Field(True, alias="generate_sql")
    generate_statistics: bool | None = Field(False, alias="session.load_options.generate_statistics")
    generate_statistics_mode: NETEZZA_OPTIMIZED.SessionLoadOptionsGenerateStatisticsGenerateStatisticsMode | None = (
        Field(
            NETEZZA_OPTIMIZED.SessionLoadOptionsGenerateStatisticsGenerateStatisticsMode.table,
            alias="session.load_options.generate_statistics.generate_statistics_mode",
        )
    )
    generate_statistics_on_columns: str | None = Field(
        None, alias="session.load_options.generate_statistics.generate_statistics_columns"
    )
    generate_truncate_statement_at_runtime: bool | None = Field(
        True, alias="table_action.generate_truncate_statement"
    )
    has_reference_output: bool | None = Field(False, alias="has_ref_output")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    key_columns: str = Field(None, alias="sql.key_columns")
    limit: int | None = Field(1000, alias="limit_rows.limit")
    limit_number_of_returned_rows: bool | None = Field(False, alias="limit_rows")
    lookup_type: NETEZZA_OPTIMIZED.LookupType | None = Field(NETEZZA_OPTIMIZED.LookupType.empty, alias="lookup_type")
    mark_end_of_wave: bool | None = Field(False, alias="transaction.mark_end_of_wave")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    maximum_reject_count: int | None = Field(1, alias="session.load_options.max_reject_count")
    message_type_for_create_statement_errors: NETEZZA_OPTIMIZED.TableActionGenerateCreateStatementFailOnErrorLogLevelForCreateStatement | None = Field(
        NETEZZA_OPTIMIZED.TableActionGenerateCreateStatementFailOnErrorLogLevelForCreateStatement.warning,
        alias="table_action.generate_create_statement.fail_on_error.log_level_for_create_statement",
    )
    message_type_for_drop_statement_errors: NETEZZA_OPTIMIZED.TableActionGenerateDropStatementFailOnErrorLogLevelForDropStatement | None = Field(
        NETEZZA_OPTIMIZED.TableActionGenerateDropStatementFailOnErrorLogLevelForDropStatement.warning,
        alias="table_action.generate_drop_statement.fail_on_error.log_level_for_drop_statement",
    )
    message_type_for_truncate_statement_errors: NETEZZA_OPTIMIZED.TableActionGenerateTruncateStatementFailOnErrorLogLevelForTruncateStatement | None = Field(
        NETEZZA_OPTIMIZED.TableActionGenerateTruncateStatementFailOnErrorLogLevelForTruncateStatement.warning,
        alias="table_action.generate_truncate_statement.fail_on_error.log_level_for_truncate_statement",
    )
    other_options: str | None = Field(None, alias="session.load_options.other_options")
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
    partition_type: NETEZZA_OPTIMIZED.PartitionType | None = Field(
        NETEZZA_OPTIMIZED.PartitionType.auto, alias="part_type"
    )
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: NETEZZA_OPTIMIZED.PreservePartitioning | None = Field(
        NETEZZA_OPTIMIZED.PreservePartitioning.default_propagate, alias="preserve"
    )
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    read_create_statement_from_file: bool | None = Field(
        False, alias="table_action.generate_create_statement.read_create_statement_from_file"
    )
    read_drop_statement_from_file: bool | None = Field(
        False, alias="table_action.generate_drop_statement.read_drop_statement_from_file"
    )
    read_truncate_statement_from_file: bool | None = Field(
        False, alias="table_action.generate_truncate_statement.read_truncate_statement_from_file"
    )
    reconciliation_input_link_mismatch_column_action: NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedLinkColumnActionRequestInputLink | None = Field(
        NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedLinkColumnActionRequestInputLink.drop,
        alias="session.schema_reconciliation.unmatched_link_column_action_request_input_link",
    )
    reconciliation_input_mismatch_column_action: NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedLinkColumnAction | None = Field(
        NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedLinkColumnAction.drop,
        alias="session.schema_reconciliation.unmatched_link_column_action",
    )
    reconciliation_mismatch_message: NETEZZA_OPTIMIZED.SessionSchemaReconciliationMismatchReportingAction | None = (
        Field(
            NETEZZA_OPTIMIZED.SessionSchemaReconciliationMismatchReportingAction.warning,
            alias="session.schema_reconciliation.mismatch_reporting_action",
        )
    )
    reconciliation_source_input_link_mismatch_column_action: NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedLinkColumnActionSource | None = Field(
        NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedLinkColumnActionSource.drop,
        alias="session.schema_reconciliation.unmatched_link_column_action_source",
    )
    reconciliation_source_mismatch_message: NETEZZA_OPTIMIZED.SessionSchemaReconciliationMismatchReportingActionSource | None = Field(
        NETEZZA_OPTIMIZED.SessionSchemaReconciliationMismatchReportingActionSource.warning,
        alias="session.schema_reconciliation.mismatch_reporting_action_source",
    )
    reconciliation_source_table_or_query_column_mismatch_action: NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedTableOrQueryColumnActionSource | None = Field(
        NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedTableOrQueryColumnActionSource.ignore,
        alias="session.schema_reconciliation.unmatched_table_or_query_column_action_source",
    )
    reconciliation_source_type_mismatch_action: NETEZZA_OPTIMIZED.SessionSchemaReconciliationTypeMismatchActionSource | None = Field(
        NETEZZA_OPTIMIZED.SessionSchemaReconciliationTypeMismatchActionSource.drop,
        alias="session.schema_reconciliation.type_mismatch_action_source",
    )
    reconciliation_table_or_query_column_mismatch_action: NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedTableOrQueryColumnActionRequest | None = Field(
        NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedTableOrQueryColumnActionRequest.ignore,
        alias="session.schema_reconciliation.unmatched_table_or_query_column_action_request",
    )
    reconciliation_type_mismatch_action: NETEZZA_OPTIMIZED.SessionSchemaReconciliationTypeMismatchAction | None = (
        Field(
            NETEZZA_OPTIMIZED.SessionSchemaReconciliationTypeMismatchAction.drop,
            alias="session.schema_reconciliation.type_mismatch_action",
        )
    )
    record_count: int | None = Field(2000, alias="transaction.record_count")
    reject_table_name: str | None = Field(None, alias="session.load_options.validate_p_ks.reject_table_name")
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    schema_name: str | None = Field(None, alias="schema_name")
    select_statement: str = Field(None, alias="sql.select_statement")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: NETEZZA_OPTIMIZED.KeyColSelect | None = Field(
        NETEZZA_OPTIMIZED.KeyColSelect.default, alias="keyColSelect"
    )
    sql_read_user_defined_sql_from_file: bool | None = Field(
        False, alias="sql.user_defined_sql.read_user_defined_sql_from_file"
    )
    sql_select_statement_read_user_defined_sql_from_file: bool | None = Field(
        False, alias="sql.select_statement.read_user_defined_sql_from_file"
    )
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    table_action: NETEZZA_OPTIMIZED.TableAction = Field(NETEZZA_OPTIMIZED.TableAction.append, alias="table_action")
    table_name: str = Field(None, alias="table_name")
    temporary_work_table_mode: NETEZZA_OPTIMIZED.SessionTemporaryWorkTable | None = Field(
        NETEZZA_OPTIMIZED.SessionTemporaryWorkTable.automatic, alias="session.temporary_work_table"
    )
    temporary_work_table_name: str = Field(None, alias="session.temporary_work_table.table_name")
    truncate_column_names: bool | None = Field(False, alias="truncate_column_names")
    truncate_length: int = Field(128, alias="truncate_column_names.truncate_length")
    truncate_table: bool | None = Field(False, alias="session.temporary_work_table.truncate_table")
    truncate_table_statement: str = Field("", alias="table_action.generate_truncate_statement.truncate_statement")
    unique: bool | None = Field(None, alias="part_unique")
    unique_key_column: str = Field(None, alias="sql.use_unique_key_column.unique_key_column")
    unix_named_pipe_directory_for_load: str | None = Field(
        None, alias="session.load_options.directory_for_named_pipe"
    )
    unix_named_pipe_directory_for_unload: str | None = Field(
        None, alias="session.unload_options.directory_for_named_pipe"
    )
    unmatched_table_column_action: NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedTableColumnAction | None = (
        Field(
            NETEZZA_OPTIMIZED.SessionSchemaReconciliationUnmatchedTableColumnAction.ignore_nullable,
            alias="session.schema_reconciliation.unmatched_table_column_action",
        )
    )
    update_columns: str | None = Field(None, alias="sql.update_columns")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    use_unique_key_column: bool | None = Field(False, alias="sql.use_unique_key_column")
    user_defined_sql: str = Field(None, alias="sql.user_defined_sql")
    validate_primary_keys: bool | None = Field(False, alias="session.load_options.validate_p_ks")
    write_mode: NETEZZA_OPTIMIZED.WriteMode | None = Field(NETEZZA_OPTIMIZED.WriteMode.insert, alias="write_mode")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("preserve_partitioning")
            if (self.output_count and self.output_count > 0)
            else exclude.add("preserve_partitioning")
        )
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("before_sql")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("before_sql")
        )
        (
            include.add("before_after_sql_before_sql_fail_on_error_log_level_for_before_sql")
            if (
                ((self.enable_before_after_sql_for_child_element))
                and (not self.fail_on_error_before_sql)
            )
            else exclude.add("before_after_sql_before_sql_fail_on_error_log_level_for_before_sql")
        )
        (
            include.add("before_after_sql_after_sql_node_read_from_file")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("before_after_sql_after_sql_node_read_from_file")
        )
        (
            include.add("before_after_sql_after_sql_node_fail_on_error_log_level_for_after_sql_node")
            if (
                ((self.enable_before_after_sql_for_child_element))
                and (not self.fail_on_error_after_sql_node)
            )
            else exclude.add("before_after_sql_after_sql_node_fail_on_error_log_level_for_after_sql_node")
        )
        (
            include.add("before_after_sql_before_sql_read_from_file")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("before_after_sql_before_sql_read_from_file")
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
            include.add("fail_on_error_before_sql")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("fail_on_error_before_sql")
        )
        (
            include.add("reconciliation_source_input_link_mismatch_column_action")
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
            else exclude.add("reconciliation_source_input_link_mismatch_column_action")
        )
        (
            include.add("before_after_sql_before_sql_node_read_from_file")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("before_after_sql_before_sql_node_read_from_file")
        )
        (
            include.add("enable_partitioned_reads")
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
            else exclude.add("enable_partitioned_reads")
        )
        (
            include.add("atomic_mode_before_sql_node")
            if (
                ((self.enable_before_after_sql_for_child_element))
                and (self.fail_on_error_before_sql_node)
            )
            else exclude.add("atomic_mode_before_sql_node")
        )
        (
            include.add("table_name")
            if (((not self.select_statement)) and (self.generate_sql_at_runtime))
            else exclude.add("table_name")
        )
        (
            include.add("reconciliation_input_link_mismatch_column_action")
            if (


                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )


            )
            else exclude.add("reconciliation_input_link_mismatch_column_action")
        )
        (
            include.add("reconciliation_source_type_mismatch_action")
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
            else exclude.add("reconciliation_source_type_mismatch_action")
        )
        (
            include.add("fail_on_error_after_sql")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("fail_on_error_after_sql")
        )
        (
            include.add("atomic_mode_before_sql")
            if (
                ((self.enable_before_after_sql_for_child_element)) and (self.fail_on_error_before_sql)
            )
            else exclude.add("atomic_mode_before_sql")
        )
        (
            include.add("atomic_mode_after_sql_node")
            if (
                ((self.enable_before_after_sql_for_child_element))
                and (self.fail_on_error_after_sql_node)
            )
            else exclude.add("atomic_mode_after_sql_node")
        )
        (
            include.add("before_sql_node")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("before_sql_node")
        )
        (
            include.add("before_after_sql_before_sql_node_fail_on_error_log_level_for_before_sql_node")
            if (
                ((self.enable_before_after_sql_for_child_element))
                and (not self.fail_on_error_before_sql_node)
            )
            else exclude.add("before_after_sql_before_sql_node_fail_on_error_log_level_for_before_sql_node")
        )
        (
            include.add("reconciliation_source_table_or_query_column_mismatch_action")
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
            else exclude.add("reconciliation_source_table_or_query_column_mismatch_action")
        )
        (
            include.add("reconciliation_table_or_query_column_mismatch_action")
            if (


                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )


            )
            else exclude.add("reconciliation_table_or_query_column_mismatch_action")
        )
        (
            include.add("before_after_sql_after_sql_read_from_file")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("before_after_sql_after_sql_read_from_file")
        )
        (
            include.add("after_sql_node")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("after_sql_node")
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
            include.add("atomic_mode_after_sql")
            if (((self.enable_before_after_sql_for_child_element)) and (self.fail_on_error_after_sql))
            else exclude.add("atomic_mode_after_sql")
        )
        (
            include.add("select_statement")
            if (((not self.table_name)) and (not self.generate_sql_at_runtime))
            else exclude.add("select_statement")
        )
        (
            include.add("reconciliation_source_mismatch_message")
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
            else exclude.add("reconciliation_source_mismatch_message")
        )
        (
            include.add("array_size")
            if (


                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )


            )
            else exclude.add("array_size")
        )
        (
            include.add("after_sql")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("after_sql")
        )
        (
            include.add("reconciliation_mismatch_message")
            if (


                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )


            )
            else exclude.add("reconciliation_mismatch_message")
        )
        (
            include.add("fail_on_error_before_sql_node")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("fail_on_error_before_sql_node")
        )
        (
            include.add("before_after_sql_after_sql_fail_on_error_log_level_for_after_sql")
            if (
                ((self.enable_before_after_sql_for_child_element)) and (not self.fail_on_error_after_sql)
            )
            else exclude.add("before_after_sql_after_sql_fail_on_error_log_level_for_after_sql")
        )
        (
            include.add("fail_on_error_after_sql_node")
            if (self.enable_before_after_sql_for_child_element)
            else exclude.add("fail_on_error_after_sql_node")
        )
        (
            include.add("sql_select_statement_read_user_defined_sql_from_file")
            if (not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_read_user_defined_sql_from_file")
        )
        (
            include.add("unix_named_pipe_directory_for_unload")
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
            else exclude.add("unix_named_pipe_directory_for_unload")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("reconciliation_type_mismatch_action")
            if (


                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )


            )
            else exclude.add("reconciliation_type_mismatch_action")
        )
        (
            include.add("before_sql")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("before_sql")
        )
        (
            include.add("before_after_sql_before_sql_fail_on_error_log_level_for_before_sql")
            if (

                    (
                        ((self.enable_before_after_sql_for_child_element))
                        or (
                            (
                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)
                            )
                        )
                    )
                    and (
                        ((not self.fail_on_error_before_sql))
                        or (self.fail_on_error_before_sql and "#" in str(self.fail_on_error_before_sql))
                    )

            )
            else exclude.add("before_after_sql_before_sql_fail_on_error_log_level_for_before_sql")
        )
        (
            include.add("before_after_sql_after_sql_node_read_from_file")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("before_after_sql_after_sql_node_read_from_file")
        )
        (
            include.add("before_after_sql_after_sql_node_fail_on_error_log_level_for_after_sql_node")
            if (

                    (
                        ((self.enable_before_after_sql_for_child_element))
                        or (
                            (
                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)
                            )
                        )
                    )
                    and (
                        ((not self.fail_on_error_after_sql_node))
                        or (self.fail_on_error_after_sql_node and "#" in str(self.fail_on_error_after_sql_node))
                    )

            )
            else exclude.add("before_after_sql_after_sql_node_fail_on_error_log_level_for_after_sql_node")
        )
        (
            include.add("before_after_sql_before_sql_read_from_file")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("before_after_sql_before_sql_read_from_file")
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
            include.add("fail_on_error_before_sql")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("fail_on_error_before_sql")
        )
        (
            include.add("reconciliation_source_input_link_mismatch_column_action")
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
            else exclude.add("reconciliation_source_input_link_mismatch_column_action")
        )
        (
            include.add("before_after_sql_before_sql_node_read_from_file")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("before_after_sql_before_sql_node_read_from_file")
        )
        (
            include.add("enable_partitioned_reads")
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
            else exclude.add("enable_partitioned_reads")
        )
        (
            include.add("atomic_mode_before_sql_node")
            if (

                    (
                        ((self.enable_before_after_sql_for_child_element))
                        or (
                            (
                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)
                            )
                        )
                    )
                    and (
                        ((self.fail_on_error_before_sql_node))
                        or (self.fail_on_error_before_sql_node and "#" in str(self.fail_on_error_before_sql_node))
                    )

            )
            else exclude.add("atomic_mode_before_sql_node")
        )
        (
            include.add("table_name")
            if (

                    (((not self.select_statement)) or ((self.select_statement and "#" in str(self.select_statement))))
                    and (
                        ((self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
                    )

            )
            else exclude.add("table_name")
        )
        (
            include.add("reconciliation_input_link_mismatch_column_action")
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
            else exclude.add("reconciliation_input_link_mismatch_column_action")
        )
        (
            include.add("reconciliation_source_type_mismatch_action")
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
            else exclude.add("reconciliation_source_type_mismatch_action")
        )
        (
            include.add("fail_on_error_after_sql")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("fail_on_error_after_sql")
        )
        (
            include.add("atomic_mode_before_sql")
            if (

                    (
                        ((self.enable_before_after_sql_for_child_element))
                        or (
                            (
                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)
                            )
                        )
                    )
                    and (
                        ((self.fail_on_error_before_sql))
                        or (self.fail_on_error_before_sql and "#" in str(self.fail_on_error_before_sql))
                    )

            )
            else exclude.add("atomic_mode_before_sql")
        )
        (
            include.add("atomic_mode_after_sql_node")
            if (

                    (
                        ((self.enable_before_after_sql_for_child_element))
                        or (
                            (
                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)
                            )
                        )
                    )
                    and (
                        ((self.fail_on_error_after_sql_node))
                        or (self.fail_on_error_after_sql_node and "#" in str(self.fail_on_error_after_sql_node))
                    )

            )
            else exclude.add("atomic_mode_after_sql_node")
        )
        (
            include.add("before_sql_node")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("before_sql_node")
        )
        (
            include.add("before_after_sql_before_sql_node_fail_on_error_log_level_for_before_sql_node")
            if (

                    (
                        ((self.enable_before_after_sql_for_child_element))
                        or (
                            (
                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)
                            )
                        )
                    )
                    and (
                        ((not self.fail_on_error_before_sql_node))
                        or (self.fail_on_error_before_sql_node and "#" in str(self.fail_on_error_before_sql_node))
                    )

            )
            else exclude.add("before_after_sql_before_sql_node_fail_on_error_log_level_for_before_sql_node")
        )
        (
            include.add("reconciliation_source_table_or_query_column_mismatch_action")
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
            else exclude.add("reconciliation_source_table_or_query_column_mismatch_action")
        )
        (
            include.add("reconciliation_table_or_query_column_mismatch_action")
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
            else exclude.add("reconciliation_table_or_query_column_mismatch_action")
        )
        (
            include.add("before_after_sql_after_sql_read_from_file")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("before_after_sql_after_sql_read_from_file")
        )
        (
            include.add("after_sql_node")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("after_sql_node")
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
            include.add("atomic_mode_after_sql")
            if (

                    (
                        ((self.enable_before_after_sql_for_child_element))
                        or (
                            (
                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)
                            )
                        )
                    )
                    and (
                        ((self.fail_on_error_after_sql))
                        or (self.fail_on_error_after_sql and "#" in str(self.fail_on_error_after_sql))
                    )

            )
            else exclude.add("atomic_mode_after_sql")
        )
        (
            include.add("select_statement")
            if (

                    (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                    and (
                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
                    )

            )
            else exclude.add("select_statement")
        )
        (
            include.add("reconciliation_source_mismatch_message")
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
            else exclude.add("reconciliation_source_mismatch_message")
        )
        (
            include.add("array_size")
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
            else exclude.add("array_size")
        )
        (
            include.add("after_sql")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("after_sql")
        )
        (
            include.add("reconciliation_mismatch_message")
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
            else exclude.add("reconciliation_mismatch_message")
        )
        (
            include.add("fail_on_error_before_sql_node")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("fail_on_error_before_sql_node")
        )
        (
            include.add("before_after_sql_after_sql_fail_on_error_log_level_for_after_sql")
            if (

                    (
                        ((self.enable_before_after_sql_for_child_element))
                        or (
                            (
                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)
                            )
                        )
                    )
                    and (
                        ((not self.fail_on_error_after_sql))
                        or (self.fail_on_error_after_sql and "#" in str(self.fail_on_error_after_sql))
                    )

            )
            else exclude.add("before_after_sql_after_sql_fail_on_error_log_level_for_after_sql")
        )
        (
            include.add("fail_on_error_after_sql_node")
            if (


                        ((self.enable_before_after_sql_for_child_element))
                        or (

                                self.enable_before_after_sql_for_child_element
                                and "#" in str(self.enable_before_after_sql_for_child_element)

                        )


            )
            else exclude.add("fail_on_error_after_sql_node")
        )
        (
            include.add("sql_select_statement_read_user_defined_sql_from_file")
            if (


                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("sql_select_statement_read_user_defined_sql_from_file")
        )
        (
            include.add("unix_named_pipe_directory_for_unload")
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
            else exclude.add("unix_named_pipe_directory_for_unload")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("reconciliation_type_mismatch_action")
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
            else exclude.add("reconciliation_type_mismatch_action")
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
            include.add("atomic_mode_after_sql")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            and (self.fail_on_error_after_sql == "true" or self.fail_on_error_after_sql)
            else exclude.add("atomic_mode_after_sql")
        )
        (
            include.add("reconciliation_input_link_mismatch_column_action")
            if (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("reconciliation_input_link_mismatch_column_action")
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
            include.add("fail_on_error_after_sql_node")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("fail_on_error_after_sql_node")
        )
        (
            include.add("array_size")
            if (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("array_size")
        )
        (
            include.add("reconciliation_source_input_link_mismatch_column_action")
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
            else exclude.add("reconciliation_source_input_link_mismatch_column_action")
        )
        (
            include.add("fail_on_error_before_sql_node")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("fail_on_error_before_sql_node")
        )
        (
            include.add("reconciliation_source_mismatch_message")
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
            else exclude.add("reconciliation_source_mismatch_message")
        )
        (
            include.add("before_after_sql_before_sql_read_from_file")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("before_after_sql_before_sql_read_from_file")
        )
        (
            include.add("select_statement")
            if (not self.table_name)
            and (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("select_statement")
        )
        (
            include.add("reconciliation_mismatch_message")
            if (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("reconciliation_mismatch_message")
        )
        (
            include.add("reconciliation_source_type_mismatch_action")
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
            else exclude.add("reconciliation_source_type_mismatch_action")
        )
        (
            include.add("before_after_sql_after_sql_node_fail_on_error_log_level_for_after_sql_node")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            and (self.fail_on_error_after_sql_node == "false" or not self.fail_on_error_after_sql_node)
            else exclude.add("before_after_sql_after_sql_node_fail_on_error_log_level_for_after_sql_node")
        )
        (
            include.add("fail_on_error_before_sql")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("fail_on_error_before_sql")
        )
        (
            include.add("before_after_sql_before_sql_node_fail_on_error_log_level_for_before_sql_node")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            and (self.fail_on_error_before_sql_node == "false" or not self.fail_on_error_before_sql_node)
            else exclude.add("before_after_sql_before_sql_node_fail_on_error_log_level_for_before_sql_node")
        )
        (
            include.add("reconciliation_type_mismatch_action")
            if (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("reconciliation_type_mismatch_action")
        )
        (
            include.add("after_sql_node")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("after_sql_node")
        )
        (
            include.add("unix_named_pipe_directory_for_unload")
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
            else exclude.add("unix_named_pipe_directory_for_unload")
        )
        (
            include.add("before_after_sql_before_sql_node_read_from_file")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("before_after_sql_before_sql_node_read_from_file")
        )
        (
            include.add("reconciliation_table_or_query_column_mismatch_action")
            if (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("reconciliation_table_or_query_column_mismatch_action")
        )
        (
            include.add("fail_on_error_after_sql")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("fail_on_error_after_sql")
        )
        (
            include.add("before_after_sql_after_sql_node_read_from_file")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("before_after_sql_after_sql_node_read_from_file")
        )
        (
            include.add("before_sql_node")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("before_sql_node")
        )
        (
            include.add("before_after_sql_before_sql_fail_on_error_log_level_for_before_sql")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            and (self.fail_on_error_before_sql == "false" or not self.fail_on_error_before_sql)
            else exclude.add("before_after_sql_before_sql_fail_on_error_log_level_for_before_sql")
        )
        (
            include.add("sql_select_statement_read_user_defined_sql_from_file")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_read_user_defined_sql_from_file")
        )
        (
            include.add("lookup_type")
            if (self.has_reference_output == "true" or self.has_reference_output)
            else exclude.add("lookup_type")
        )
        (
            include.add("after_sql")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("after_sql")
        )
        (
            include.add("atomic_mode_before_sql")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            and (self.fail_on_error_before_sql == "true" or self.fail_on_error_before_sql)
            else exclude.add("atomic_mode_before_sql")
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
            include.add("atomic_mode_after_sql_node")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            and (self.fail_on_error_after_sql_node == "true" or self.fail_on_error_after_sql_node)
            else exclude.add("atomic_mode_after_sql_node")
        )
        (
            include.add("enable_partitioned_reads")
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
            else exclude.add("enable_partitioned_reads")
        )
        (
            include.add("table_name")
            if (not self.select_statement)
            and (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("table_name")
        )
        (
            include.add("before_after_sql_after_sql_fail_on_error_log_level_for_after_sql")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            and (self.fail_on_error_after_sql == "false" or not self.fail_on_error_after_sql)
            else exclude.add("before_after_sql_after_sql_fail_on_error_log_level_for_after_sql")
        )
        (
            include.add("reconciliation_source_table_or_query_column_mismatch_action")
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
            else exclude.add("reconciliation_source_table_or_query_column_mismatch_action")
        )
        (
            include.add("before_after_sql_after_sql_read_from_file")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("before_after_sql_after_sql_read_from_file")
        )
        (
            include.add("before_sql")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            else exclude.add("before_sql")
        )
        (
            include.add("atomic_mode_before_sql_node")
            if (
                self.enable_before_after_sql_for_child_element == "true"
                or self.enable_before_after_sql_for_child_element
            )
            and (self.fail_on_error_before_sql_node == "true" or self.fail_on_error_before_sql_node)
            else exclude.add("atomic_mode_before_sql_node")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("unique_key_column")
            if (self.use_unique_key_column)
            else exclude.add("unique_key_column")
        )
        (
            include.add("generate_statistics_mode")
            if (self.generate_statistics)
            else exclude.add("generate_statistics_mode")
        )
        (
            include.add("table_name")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )

            )
            else exclude.add("table_name")
        )
        (
            include.add("action_column")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                            or (self.write_mode == "action_column")
                        )


            )
            else exclude.add("action_column")
        )
        (
            include.add("distribution_key")
            if (
                (
                    ((self.generate_create_statement_at_runtime))
                    or ((not self.read_create_statement_from_file))
                )
                and (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                or (self.table_action == "create")
                            )
                        )
                    )
                    or (

                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                or (self.table_action == "replace")
                            )

                    )
                )
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("distribution_key")
        )
        (
            include.add("drop_table")
            if (
                ((not self.direct_insert))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("drop_table")
        )
        (
            include.add("user_defined_sql")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
                        )


            )
            else exclude.add("user_defined_sql")
        )
        (
            include.add("fail_on_error_drop_statement")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                            or (self.table_action == "replace")
                        )
                    )
                )
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("fail_on_error_drop_statement")
        )
        (
            include.add("validate_primary_keys")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )

            )
            else exclude.add("validate_primary_keys")
        )
        (
            include.add("enable_use_of_merge_join_plan_type")
            if (
                ((not self.direct_insert))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("enable_use_of_merge_join_plan_type")
        )
        (
            include.add("duplicate_row_action")
            if (self.check_duplicate_rows)
            else exclude.add("duplicate_row_action")
        )
        (
            include.add("fail_on_error_create_statement")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                or (self.table_action == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                or (self.table_action == "replace")
                            )
                        )
                    )
                )
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("fail_on_error_create_statement")
        )
        (
            include.add("read_truncate_statement_from_file")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                            or (self.table_action == "truncate")
                        )
                    )
                )
                and (not self.generate_truncate_statement_at_runtime)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("read_truncate_statement_from_file")
        )
        (
            include.add("use_unique_key_column")
            if (
                ((self.check_duplicate_rows))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                )
            )
            else exclude.add("use_unique_key_column")
        )
        (
            include.add("create_table_statement")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                or (self.table_action == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                or (self.table_action == "replace")
                            )
                        )
                    )
                )
                and (not self.generate_create_statement_at_runtime)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("create_table_statement")
        )
        include.add("truncate_length") if (self.truncate_column_names) else exclude.add("truncate_length")
        (
            include.add("read_drop_statement_from_file")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                            or (self.table_action == "replace")
                        )
                    )
                )
                and (not self.generate_drop_statement_at_runtime)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("read_drop_statement_from_file")
        )
        (
            include.add("update_columns")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )

            )
            else exclude.add("update_columns")
        )
        (
            include.add("generate_statistics_on_columns")
            if (((self.generate_statistics)) and (self.generate_statistics_mode == "table"))
            else exclude.add("generate_statistics_on_columns")
        )
        (
            include.add("unmatched_table_column_action")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )

            )
            else exclude.add("unmatched_table_column_action")
        )
        include.add("column_name") if (self.enable_record_ordering) else exclude.add("column_name")
        (
            include.add("truncate_table_statement")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                            or (self.table_action == "truncate")
                        )
                    )
                )
                and (not self.generate_truncate_statement_at_runtime)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("fail_on_error_truncate_statement")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                            or (self.table_action == "truncate")
                        )
                    )
                )
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("fail_on_error_truncate_statement")
        )
        (
            include.add("generate_truncate_statement_at_runtime")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                            or (self.table_action == "truncate")
                        )
                    )
                )
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("generate_truncate_statement_at_runtime")
        )
        (
            include.add("enable_record_ordering")
            if (
                (
                    ((not self.direct_insert))
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
                            )
                        )
                    )
                )
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                )
            )
            else exclude.add("enable_record_ordering")
        )
        (
            include.add("sql_read_user_defined_sql_from_file")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
                        )


            )
            else exclude.add("sql_read_user_defined_sql_from_file")
        )
        (
            include.add("read_create_statement_from_file")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                or (self.table_action == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                or (self.table_action == "replace")
                            )
                        )
                    )
                )
                and (not self.generate_create_statement_at_runtime)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("read_create_statement_from_file")
        )
        (
            include.add("reject_table_name")
            if (
                ((self.validate_primary_keys))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                )
            )
            else exclude.add("reject_table_name")
        )
        (
            include.add("truncate_table")
            if (
                ((self.temporary_work_table_mode == "existing"))
                and (
                    ((not self.direct_insert))
                    or (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "update_then_insert"
                                    )
                                    or (self.write_mode == "update_then_insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
                                )

                        )
                    )
                )
            )
            else exclude.add("truncate_table")
        )
        (
            include.add("generate_drop_statement_at_runtime")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                            or (self.table_action == "replace")
                        )
                    )
                )
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("generate_drop_statement_at_runtime")
        )
        (
            include.add("temporary_work_table_mode")
            if (
                ((not self.direct_insert))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("temporary_work_table_mode")
        )
        (
            include.add("message_type_for_truncate_statement_errors")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                            or (self.table_action == "truncate")
                        )
                    )
                )
                and (not self.fail_on_error_truncate_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("message_type_for_truncate_statement_errors")
        )
        (
            include.add("temporary_work_table_name")
            if (
                (
                    ((self.temporary_work_table_mode == "existing"))
                    or ((self.temporary_work_table_mode == "user-defined"))
                )
                and (
                    ((not self.direct_insert))
                    or (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "update_then_insert"
                                    )
                                    or (self.write_mode == "update_then_insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
                                )

                        )
                    )
                )
            )
            else exclude.add("temporary_work_table_name")
        )
        (
            include.add("table_action")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )

            )
            else exclude.add("table_action")
        )
        (
            include.add("key_columns")
            if (
                ((self.check_duplicate_rows))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                )
            )
            else exclude.add("key_columns")
        )
        (
            include.add("drop_table_statement")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                            or (self.table_action == "replace")
                        )
                    )
                )
                and (not self.generate_drop_statement_at_runtime)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("drop_table_statement")
        )
        (
            include.add("atomic_mode")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )

            )
            else exclude.add("atomic_mode")
        )
        (
            include.add("check_duplicate_rows")
            if (
                (
                    ((not self.direct_insert))
                    and (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
                        )
                    )
                )
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                )
            )
            else exclude.add("check_duplicate_rows")
        )
        (
            include.add("generate_create_statement_at_runtime")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                or (self.table_action == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                or (self.table_action == "replace")
                            )
                        )
                    )
                )
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("generate_create_statement_at_runtime")
        )
        (
            include.add("message_type_for_create_statement_errors")
            if (
                (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                or (self.table_action == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                or (self.table_action == "replace")
                            )
                        )
                    )
                )
                and (not self.fail_on_error_create_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("message_type_for_create_statement_errors")
        )
        (
            include.add("message_type_for_drop_statement_errors")
            if (
                (
                    (
                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                            or (self.table_action == "replace")
                        )
                    )
                )
                and (not self.fail_on_error_drop_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("message_type_for_drop_statement_errors")
        )
        (
            include.add("direct_insert")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                            or (self.write_mode == "insert")
                        )


            )
            else exclude.add("direct_insert")
        )
        (
            include.add("generate_create_statement_distribution_key_column_names")
            if (
                (
                    ((self.generate_create_statement_at_runtime))
                    or ((not self.read_create_statement_from_file))
                )
                and (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                or (self.table_action == "create")
                            )
                        )
                    )
                    or (

                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                or (self.table_action == "replace")
                            )

                    )
                )
                and (self.distribution_key == "user-defined")
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("generate_create_statement_distribution_key_column_names")
        )
        (
            include.add("create_statement")
            if (
                ((self.temporary_work_table_mode == "user-defined"))
                and (
                    ((not self.direct_insert))
                    or (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "update_then_insert"
                                    )
                                    or (self.write_mode == "update_then_insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
                                )

                        )
                    )
                )
            )
            else exclude.add("create_statement")
        )
        (
            include.add("unique_key_column")
            if (


                        ((self.use_unique_key_column))
                        or (self.use_unique_key_column and "#" in str(self.use_unique_key_column))


            )
            else exclude.add("unique_key_column")
        )
        (
            include.add("generate_statistics_mode")
            if (


                        ((self.generate_statistics))
                        or (self.generate_statistics and "#" in str(self.generate_statistics))


            )
            else exclude.add("generate_statistics_mode")
        )
        (
            include.add("table_name")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                            or (self.write_mode == "action_column")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                            or (self.write_mode == "delete")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                            or (self.write_mode == "delete_then_insert")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                            or (self.write_mode == "insert")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                            or (self.write_mode == "update")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                            or (self.write_mode == "update_then_insert")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
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
            else exclude.add("table_name")
        )
        (
            include.add("action_column")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                            or (self.write_mode == "action_column")
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
            else exclude.add("action_column")
        )
        (
            include.add("distribution_key")
            if (

                    (
                        ((self.generate_create_statement_at_runtime))
                        or ((not self.read_create_statement_from_file))
                        or (
                            (
                                self.generate_create_statement_at_runtime
                                and "#" in str(self.generate_create_statement_at_runtime)
                            )
                        )
                        or ((self.read_create_statement_from_file and "#" in str(self.read_create_statement_from_file)))
                    )
                    and (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                    or (self.table_action == "create")
                                )
                            )
                        )
                        or (

                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("distribution_key")
        )
        (
            include.add("drop_table")
            if (
                ((not self.direct_insert))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
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
                or (self.direct_insert and "#" in str(self.direct_insert))
            )
            else exclude.add("drop_table")
        )
        (
            include.add("user_defined_sql")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
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
            else exclude.add("user_defined_sql")
        )
        (
            include.add("fail_on_error_drop_statement")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("fail_on_error_drop_statement")
        )
        (
            include.add("validate_primary_keys")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                            or (self.write_mode == "action_column")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                            or (self.write_mode == "delete_then_insert")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                            or (self.write_mode == "insert")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                            or (self.write_mode == "update_then_insert")
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
            else exclude.add("validate_primary_keys")
        )
        (
            include.add("enable_use_of_merge_join_plan_type")
            if (
                ((not self.direct_insert))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
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
                or (self.direct_insert and "#" in str(self.direct_insert))
            )
            else exclude.add("enable_use_of_merge_join_plan_type")
        )
        (
            include.add("duplicate_row_action")
            if (


                        ((self.check_duplicate_rows))
                        or (self.check_duplicate_rows and "#" in str(self.check_duplicate_rows))


            )
            else exclude.add("duplicate_row_action")
        )
        (
            include.add("fail_on_error_create_statement")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                    or (self.table_action == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("fail_on_error_create_statement")
        )
        (
            include.add("read_truncate_statement_from_file")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                                    or (self.table_action == "truncate")
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
                        ((not self.generate_truncate_statement_at_runtime))
                        or (

                                self.generate_truncate_statement_at_runtime
                                and "#" in str(self.generate_truncate_statement_at_runtime)

                        )
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("read_truncate_statement_from_file")
        )
        (
            include.add("use_unique_key_column")
            if (
                ((self.check_duplicate_rows))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
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
                or (self.check_duplicate_rows and "#" in str(self.check_duplicate_rows))
            )
            else exclude.add("use_unique_key_column")
        )
        (
            include.add("create_table_statement")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                    or (self.table_action == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                        ((not self.generate_create_statement_at_runtime))
                        or (

                                self.generate_create_statement_at_runtime
                                and "#" in str(self.generate_create_statement_at_runtime)

                        )
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("create_table_statement")
        )
        (
            include.add("truncate_length")
            if (


                        ((self.truncate_column_names))
                        or (self.truncate_column_names and "#" in str(self.truncate_column_names))


            )
            else exclude.add("truncate_length")
        )
        (
            include.add("read_drop_statement_from_file")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                        ((not self.generate_drop_statement_at_runtime))
                        or (

                                self.generate_drop_statement_at_runtime
                                and "#" in str(self.generate_drop_statement_at_runtime)

                        )
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("read_drop_statement_from_file")
        )
        (
            include.add("update_columns")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                            or (self.write_mode == "action_column")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                            or (self.write_mode == "update")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                            or (self.write_mode == "update_then_insert")
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
            else exclude.add("update_columns")
        )
        (
            include.add("generate_statistics_on_columns")
            if (

                    (
                        ((self.generate_statistics))
                        or ((self.generate_statistics and "#" in str(self.generate_statistics)))
                    )
                    and (
                        ((self.generate_statistics_mode == "table"))
                        or (self.generate_statistics_mode and "#" in str(self.generate_statistics_mode))
                    )

            )
            else exclude.add("generate_statistics_on_columns")
        )
        (
            include.add("unmatched_table_column_action")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                            or (self.write_mode == "action_column")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                            or (self.write_mode == "delete_then_insert")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                            or (self.write_mode == "insert")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                            or (self.write_mode == "update_then_insert")
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
            else exclude.add("unmatched_table_column_action")
        )
        (
            include.add("column_name")
            if (


                        ((self.enable_record_ordering))
                        or (self.enable_record_ordering and "#" in str(self.enable_record_ordering))


            )
            else exclude.add("column_name")
        )
        (
            include.add("truncate_table_statement")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                                    or (self.table_action == "truncate")
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
                        ((not self.generate_truncate_statement_at_runtime))
                        or (

                                self.generate_truncate_statement_at_runtime
                                and "#" in str(self.generate_truncate_statement_at_runtime)

                        )
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("fail_on_error_truncate_statement")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                                    or (self.table_action == "truncate")
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
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("fail_on_error_truncate_statement")
        )
        (
            include.add("generate_truncate_statement_at_runtime")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                                    or (self.table_action == "truncate")
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
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("generate_truncate_statement_at_runtime")
        )
        (
            include.add("enable_record_ordering")
            if (
                (
                    (
                        (((not self.direct_insert)) or ((self.direct_insert and "#" in str(self.direct_insert))))
                        and (
                            (
                                (
                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                        or (self.write_mode == "insert")
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
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
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
            else exclude.add("enable_record_ordering")
        )
        (
            include.add("sql_read_user_defined_sql_from_file")
            if (


                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("sql_read_user_defined_sql_from_file")
        )
        (
            include.add("read_create_statement_from_file")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                    or (self.table_action == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                        ((not self.generate_create_statement_at_runtime))
                        or (

                                self.generate_create_statement_at_runtime
                                and "#" in str(self.generate_create_statement_at_runtime)

                        )
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("read_create_statement_from_file")
        )
        (
            include.add("reject_table_name")
            if (

                    ((self.validate_primary_keys))
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "update_then_insert"
                                    )
                                    or (self.write_mode == "update_then_insert")
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
            else exclude.add("reject_table_name")
        )
        (
            include.add("truncate_table")
            if (

                    (
                        ((self.temporary_work_table_mode == "existing"))
                        or ((self.temporary_work_table_mode and "#" in str(self.temporary_work_table_mode)))
                    )
                    and (
                        ((not self.direct_insert))
                        or (
                            (
                                (
                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                        or (self.write_mode == "action_column")
                                    )
                                )
                            )
                            or (

                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                        or (self.write_mode == "delete")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (
                                            hasattr(self.write_mode, "value")
                                            and self.write_mode.value == "delete_then_insert"
                                        )
                                        or (self.write_mode == "delete_then_insert")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                        or (self.write_mode == "update")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (
                                            hasattr(self.write_mode, "value")
                                            and self.write_mode.value == "update_then_insert"
                                        )
                                        or (self.write_mode == "update_then_insert")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (
                                            hasattr(self.write_mode, "value")
                                            and self.write_mode.value == "user-defined_sql"
                                        )
                                        or (self.write_mode == "user-defined_sql")
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
                        or (self.direct_insert and "#" in str(self.direct_insert))
                    )

            )
            else exclude.add("truncate_table")
        )
        (
            include.add("generate_drop_statement_at_runtime")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("generate_drop_statement_at_runtime")
        )
        (
            include.add("temporary_work_table_mode")
            if (
                ((not self.direct_insert))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
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
                or (self.direct_insert and "#" in str(self.direct_insert))
            )
            else exclude.add("temporary_work_table_mode")
        )
        (
            include.add("message_type_for_truncate_statement_errors")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                                    or (self.table_action == "truncate")
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
                        ((not self.fail_on_error_truncate_statement))
                        or (

                                self.fail_on_error_truncate_statement
                                and "#" in str(self.fail_on_error_truncate_statement)

                        )
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("message_type_for_truncate_statement_errors")
        )
        (
            include.add("temporary_work_table_name")
            if (

                    (
                        ((self.temporary_work_table_mode == "existing"))
                        or ((self.temporary_work_table_mode == "user-defined"))
                        or ((self.temporary_work_table_mode and "#" in str(self.temporary_work_table_mode)))
                    )
                    and (
                        ((not self.direct_insert))
                        or (
                            (
                                (
                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                        or (self.write_mode == "action_column")
                                    )
                                )
                            )
                            or (

                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                        or (self.write_mode == "delete")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (
                                            hasattr(self.write_mode, "value")
                                            and self.write_mode.value == "delete_then_insert"
                                        )
                                        or (self.write_mode == "delete_then_insert")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                        or (self.write_mode == "update")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (
                                            hasattr(self.write_mode, "value")
                                            and self.write_mode.value == "update_then_insert"
                                        )
                                        or (self.write_mode == "update_then_insert")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (
                                            hasattr(self.write_mode, "value")
                                            and self.write_mode.value == "user-defined_sql"
                                        )
                                        or (self.write_mode == "user-defined_sql")
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
                        or (self.direct_insert and "#" in str(self.direct_insert))
                    )

            )
            else exclude.add("temporary_work_table_name")
        )
        (
            include.add("table_action")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                            or (self.write_mode == "action_column")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                            or (self.write_mode == "insert")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
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
            else exclude.add("table_action")
        )
        (
            include.add("key_columns")
            if (
                ((self.check_duplicate_rows))
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
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
                or (self.check_duplicate_rows and "#" in str(self.check_duplicate_rows))
            )
            else exclude.add("key_columns")
        )
        (
            include.add("drop_table_statement")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                        ((not self.generate_drop_statement_at_runtime))
                        or (

                                self.generate_drop_statement_at_runtime
                                and "#" in str(self.generate_drop_statement_at_runtime)

                        )
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("drop_table_statement")
        )
        (
            include.add("atomic_mode")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                            or (self.write_mode == "action_column")
                        )
                    )
                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                            or (self.write_mode == "delete_then_insert")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                            or (self.write_mode == "update_then_insert")
                        )

                )
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
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
            else exclude.add("atomic_mode")
        )
        (
            include.add("check_duplicate_rows")
            if (
                (
                    (
                        (((not self.direct_insert)) or ((self.direct_insert and "#" in str(self.direct_insert))))
                        and (
                            (
                                (
                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                        or (self.write_mode == "insert")
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
                or (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                or (self.write_mode == "action_column")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
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
            else exclude.add("check_duplicate_rows")
        )
        (
            include.add("generate_create_statement_at_runtime")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                    or (self.table_action == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("generate_create_statement_at_runtime")
        )
        (
            include.add("message_type_for_create_statement_errors")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                    or (self.table_action == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                        ((not self.fail_on_error_create_statement))
                        or (self.fail_on_error_create_statement and "#" in str(self.fail_on_error_create_statement))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("message_type_for_create_statement_errors")
        )
        (
            include.add("message_type_for_drop_statement_errors")
            if (

                    (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                        ((not self.fail_on_error_drop_statement))
                        or (self.fail_on_error_drop_statement and "#" in str(self.fail_on_error_drop_statement))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("message_type_for_drop_statement_errors")
        )
        (
            include.add("direct_insert")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                            or (self.write_mode == "insert")
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
            else exclude.add("direct_insert")
        )
        (
            include.add("generate_create_statement_distribution_key_column_names")
            if (

                    (
                        ((self.generate_create_statement_at_runtime))
                        or ((not self.read_create_statement_from_file))
                        or (
                            (
                                self.generate_create_statement_at_runtime
                                and "#" in str(self.generate_create_statement_at_runtime)
                            )
                        )
                        or ((self.read_create_statement_from_file and "#" in str(self.read_create_statement_from_file)))
                    )
                    and (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "create")
                                    or (self.table_action == "create")
                                )
                            )
                        )
                        or (

                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                                    or (self.table_action == "replace")
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
                    and (
                        ((self.distribution_key == "user-defined"))
                        or (self.distribution_key and "#" in str(self.distribution_key))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                    or (self.write_mode == "action_column")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                    or (self.write_mode == "user-defined_sql")
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
            else exclude.add("generate_create_statement_distribution_key_column_names")
        )
        (
            include.add("create_statement")
            if (

                    (
                        ((self.temporary_work_table_mode == "user-defined"))
                        or ((self.temporary_work_table_mode and "#" in str(self.temporary_work_table_mode)))
                    )
                    and (
                        ((not self.direct_insert))
                        or (
                            (
                                (
                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                                        or (self.write_mode == "action_column")
                                    )
                                )
                            )
                            or (

                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                        or (self.write_mode == "delete")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (
                                            hasattr(self.write_mode, "value")
                                            and self.write_mode.value == "delete_then_insert"
                                        )
                                        or (self.write_mode == "delete_then_insert")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                        or (self.write_mode == "update")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (
                                            hasattr(self.write_mode, "value")
                                            and self.write_mode.value == "update_then_insert"
                                        )
                                        or (self.write_mode == "update_then_insert")
                                    )

                            )
                            or (

                                    self.write_mode
                                    and (
                                        (
                                            hasattr(self.write_mode, "value")
                                            and self.write_mode.value == "user-defined_sql"
                                        )
                                        or (self.write_mode == "user-defined_sql")
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
                        or (self.direct_insert and "#" in str(self.direct_insert))
                    )

            )
            else exclude.add("create_statement")
        )
        (
            include.add("unmatched_table_column_action")
            if (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
            )
            else exclude.add("unmatched_table_column_action")
        )
        (
            include.add("truncate_table")
            if (self.temporary_work_table_mode == "existing")
            and (
                (self.direct_insert == "false" or not self.direct_insert)
                or (
                    self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "action_column" in str(self.write_mode.value)
                        )
                        or ("action_column" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "delete" in str(self.write_mode.value)
                        )
                        or ("delete" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "delete_then_insert" in str(self.write_mode.value)
                        )
                        or ("delete_then_insert" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update" in str(self.write_mode.value)
                        )
                        or ("update" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update_then_insert" in str(self.write_mode.value)
                        )
                        or ("update_then_insert" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "user-defined_sql" in str(self.write_mode.value)
                        )
                        or ("user-defined_sql" in str(self.write_mode))
                    )
                )
            )
            else exclude.add("truncate_table")
        )
        (
            include.add("user_defined_sql")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("user_defined_sql")
        )
        (
            include.add("generate_drop_statement_at_runtime")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                    or (self.table_action == "replace")
                )
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("generate_drop_statement_at_runtime")
        )
        (
            include.add("generate_truncate_statement_at_runtime")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                    or (self.table_action == "truncate")
                )
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("generate_truncate_statement_at_runtime")
        )
        (
            include.add("message_type_for_truncate_statement_errors")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                    or (self.table_action == "truncate")
                )
            )
            and (self.fail_on_error_truncate_statement == "false" or not self.fail_on_error_truncate_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("message_type_for_truncate_statement_errors")
        )
        (
            include.add("reject_table_name")
            if (self.validate_primary_keys == "true" or self.validate_primary_keys)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
            )
            else exclude.add("reject_table_name")
        )
        (
            include.add("check_duplicate_rows")
            if (
                (self.direct_insert == "false" or not self.direct_insert)
                and (
                    self.write_mode
                    and (
                        (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                        or (self.write_mode == "insert")
                    )
                )
            )
            or (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
            )
            else exclude.add("check_duplicate_rows")
        )
        (
            include.add("fail_on_error_drop_statement")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                    or (self.table_action == "replace")
                )
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("fail_on_error_drop_statement")
        )
        (
            include.add("generate_statistics_on_columns")
            if (self.generate_statistics == "true" or self.generate_statistics)
            and (self.generate_statistics_mode == "table")
            else exclude.add("generate_statistics_on_columns")
        )
        (
            include.add("atomic_mode")
            if (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("atomic_mode")
        )
        (
            include.add("create_table_statement")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "create" in str(self.table_action.value)
                    )
                    or ("create" in str(self.table_action))
                )
                and self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            and (
                self.generate_create_statement_at_runtime == "false"
                or not self.generate_create_statement_at_runtime
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("create_table_statement")
        )
        (
            include.add("generate_create_statement_distribution_key_column_names")
            if (
                (
                    self.generate_create_statement_at_runtime == "true"
                    or self.generate_create_statement_at_runtime
                )
                or (self.read_create_statement_from_file == "false" or not self.read_create_statement_from_file)
            )
            and (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "create" in str(self.table_action.value)
                    )
                    or ("create" in str(self.table_action))
                )
                and self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            and (self.distribution_key == "user-defined")
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("generate_create_statement_distribution_key_column_names")
        )
        (
            include.add("temporary_work_table_mode")
            if (self.direct_insert == "false" or not self.direct_insert)
            or (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("temporary_work_table_mode")
        )
        (
            include.add("read_drop_statement_from_file")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                    or (self.table_action == "replace")
                )
            )
            and (self.generate_drop_statement_at_runtime == "false" or not self.generate_drop_statement_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("read_drop_statement_from_file")
        )
        (
            include.add("create_statement")
            if (self.temporary_work_table_mode == "user-defined")
            and (
                (self.direct_insert == "false" or not self.direct_insert)
                or (
                    self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "action_column" in str(self.write_mode.value)
                        )
                        or ("action_column" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "delete" in str(self.write_mode.value)
                        )
                        or ("delete" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "delete_then_insert" in str(self.write_mode.value)
                        )
                        or ("delete_then_insert" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update" in str(self.write_mode.value)
                        )
                        or ("update" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update_then_insert" in str(self.write_mode.value)
                        )
                        or ("update_then_insert" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "user-defined_sql" in str(self.write_mode.value)
                        )
                        or ("user-defined_sql" in str(self.write_mode))
                    )
                )
            )
            else exclude.add("create_statement")
        )
        (
            include.add("direct_insert")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                    or (self.write_mode == "insert")
                )
            )
            else exclude.add("direct_insert")
        )
        (
            include.add("action_column")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "action_column")
                    or (self.write_mode == "action_column")
                )
            )
            else exclude.add("action_column")
        )
        (
            include.add("temporary_work_table_name")
            if (
                self.temporary_work_table_mode
                and "existing" in str(self.temporary_work_table_mode)
                and self.temporary_work_table_mode
                and "user-defined" in str(self.temporary_work_table_mode)
            )
            and (
                (self.direct_insert == "false" or not self.direct_insert)
                or (
                    self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "action_column" in str(self.write_mode.value)
                        )
                        or ("action_column" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "delete" in str(self.write_mode.value)
                        )
                        or ("delete" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "delete_then_insert" in str(self.write_mode.value)
                        )
                        or ("delete_then_insert" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update" in str(self.write_mode.value)
                        )
                        or ("update" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update_then_insert" in str(self.write_mode.value)
                        )
                        or ("update_then_insert" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "user-defined_sql" in str(self.write_mode.value)
                        )
                        or ("user-defined_sql" in str(self.write_mode))
                    )
                )
            )
            else exclude.add("temporary_work_table_name")
        )
        (
            include.add("enable_use_of_merge_join_plan_type")
            if (self.direct_insert == "false" or not self.direct_insert)
            or (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("enable_use_of_merge_join_plan_type")
        )
        (
            include.add("distribution_key")
            if (
                (
                    self.generate_create_statement_at_runtime == "true"
                    or self.generate_create_statement_at_runtime
                )
                or (self.read_create_statement_from_file == "false" or not self.read_create_statement_from_file)
            )
            and (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "create" in str(self.table_action.value)
                    )
                    or ("create" in str(self.table_action))
                )
                and self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("distribution_key")
        )
        (
            include.add("table_name")
            if (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("truncate_length")
            if (self.truncate_column_names == "true" or self.truncate_column_names)
            else exclude.add("truncate_length")
        )
        (
            include.add("drop_table")
            if (self.direct_insert == "false" or not self.direct_insert)
            or (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("drop_table")
        )
        (
            include.add("duplicate_row_action")
            if (self.check_duplicate_rows == "true" or self.check_duplicate_rows)
            else exclude.add("duplicate_row_action")
        )
        (
            include.add("validate_primary_keys")
            if (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
            )
            else exclude.add("validate_primary_keys")
        )
        (
            include.add("read_truncate_statement_from_file")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                    or (self.table_action == "truncate")
                )
            )
            and (
                self.generate_truncate_statement_at_runtime == "false"
                or not self.generate_truncate_statement_at_runtime
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("read_truncate_statement_from_file")
        )
        (
            include.add("drop_table_statement")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                    or (self.table_action == "replace")
                )
            )
            and (self.generate_drop_statement_at_runtime == "false" or not self.generate_drop_statement_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("drop_table_statement")
        )
        (
            include.add("unique_key_column")
            if (self.use_unique_key_column == "true" or self.use_unique_key_column)
            else exclude.add("unique_key_column")
        )
        (
            include.add("fail_on_error_create_statement")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "create" in str(self.table_action.value)
                    )
                    or ("create" in str(self.table_action))
                )
                and self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("fail_on_error_create_statement")
        )
        (
            include.add("message_type_for_create_statement_errors")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "create" in str(self.table_action.value)
                    )
                    or ("create" in str(self.table_action))
                )
                and self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            and (self.fail_on_error_create_statement == "false" or not self.fail_on_error_create_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("message_type_for_create_statement_errors")
        )
        (
            include.add("sql_read_user_defined_sql_from_file")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("sql_read_user_defined_sql_from_file")
        )
        (
            include.add("generate_create_statement_at_runtime")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "create" in str(self.table_action.value)
                    )
                    or ("create" in str(self.table_action))
                )
                and self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("generate_create_statement_at_runtime")
        )
        (
            include.add("read_create_statement_from_file")
            if (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "create" in str(self.table_action.value)
                    )
                    or ("create" in str(self.table_action))
                )
                and self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            and (
                self.generate_create_statement_at_runtime == "false"
                or not self.generate_create_statement_at_runtime
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("read_create_statement_from_file")
        )
        (
            include.add("truncate_table_statement")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                    or (self.table_action == "truncate")
                )
            )
            and (
                self.generate_truncate_statement_at_runtime == "false"
                or not self.generate_truncate_statement_at_runtime
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("table_action")
            if (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("table_action")
        )
        (
            include.add("message_type_for_drop_statement_errors")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                    or (self.table_action == "replace")
                )
            )
            and (self.fail_on_error_drop_statement == "false" or not self.fail_on_error_drop_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("message_type_for_drop_statement_errors")
        )
        (
            include.add("generate_statistics_mode")
            if (self.generate_statistics == "true" or self.generate_statistics)
            else exclude.add("generate_statistics_mode")
        )
        (
            include.add("use_unique_key_column")
            if (self.check_duplicate_rows == "true" or self.check_duplicate_rows)
            or (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
            )
            else exclude.add("use_unique_key_column")
        )
        (
            include.add("update_columns")
            if (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
            )
            else exclude.add("update_columns")
        )
        (
            include.add("key_columns")
            if (self.check_duplicate_rows == "true" or self.check_duplicate_rows)
            or (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
            )
            else exclude.add("key_columns")
        )
        (
            include.add("fail_on_error_truncate_statement")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                    or (self.table_action == "truncate")
                )
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" in str(self.write_mode.value)
                    )
                    or ("insert" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("fail_on_error_truncate_statement")
        )
        (
            include.add("enable_record_ordering")
            if (
                (self.direct_insert == "false" or not self.direct_insert)
                and (
                    self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "insert" in str(self.write_mode.value)
                        )
                        or ("insert" in str(self.write_mode))
                    )
                )
            )
            or (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "action_column" in str(self.write_mode.value)
                    )
                    or ("action_column" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete_then_insert" in str(self.write_mode.value)
                    )
                    or ("delete_then_insert" in str(self.write_mode))
                )
                or self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_then_insert" in str(self.write_mode.value)
                    )
                    or ("update_then_insert" in str(self.write_mode))
                )
            )
            else exclude.add("enable_record_ordering")
        )
        (
            include.add("column_name")
            if (self.enable_record_ordering == "true" or self.enable_record_ordering)
            else exclude.add("column_name")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "after_sql",
            "after_sql_node",
            "array_size",
            "atomic_mode_after_sql",
            "atomic_mode_after_sql_node",
            "atomic_mode_before_sql",
            "atomic_mode_before_sql_node",
            "before_after_sql_after_sql_fail_on_error_log_level_for_after_sql",
            "before_after_sql_after_sql_node_fail_on_error_log_level_for_after_sql_node",
            "before_after_sql_after_sql_node_read_from_file",
            "before_after_sql_after_sql_read_from_file",
            "before_after_sql_before_sql_fail_on_error_log_level_for_before_sql",
            "before_after_sql_before_sql_node_fail_on_error_log_level_for_before_sql_node",
            "before_after_sql_before_sql_node_read_from_file",
            "before_after_sql_before_sql_read_from_file",
            "before_sql",
            "before_sql_node",
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
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "enable_before_after_sql_for_child_element",
            "enable_case_sensitive_identifiers",
            "enable_flow_acp_control",
            "enable_partitioned_reads",
            "enable_schemaless_design",
            "execution_mode",
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "flow_dirty",
            "generate_sql_at_runtime",
            "has_reference_output",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "limit",
            "limit_number_of_returned_rows",
            "lookup_type",
            "mark_end_of_wave",
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
            "reconciliation_input_link_mismatch_column_action",
            "reconciliation_mismatch_message",
            "reconciliation_source_input_link_mismatch_column_action",
            "reconciliation_source_mismatch_message",
            "reconciliation_source_table_or_query_column_mismatch_action",
            "reconciliation_source_type_mismatch_action",
            "reconciliation_table_or_query_column_mismatch_action",
            "reconciliation_type_mismatch_action",
            "record_count",
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
            "sql_select_statement_read_user_defined_sql_from_file",
            "stable",
            "stage_description",
            "table_name",
            "unique",
            "unix_named_pipe_directory_for_unload",
        }
        required = {
            "current_output_link_type",
            "database",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname",
            "output_acp_should_hide",
            "password",
            "port",
            "select_statement",
            "table_name",
            "twt_separate_connection_database_name",
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
            "action_column",
            "after_sql",
            "after_sql_node",
            "atomic_mode",
            "atomic_mode_after_sql",
            "atomic_mode_after_sql_node",
            "atomic_mode_before_sql",
            "atomic_mode_before_sql_node",
            "before_after_sql_after_sql_fail_on_error_log_level_for_after_sql",
            "before_after_sql_after_sql_node_fail_on_error_log_level_for_after_sql_node",
            "before_after_sql_after_sql_node_read_from_file",
            "before_after_sql_after_sql_read_from_file",
            "before_after_sql_before_sql_fail_on_error_log_level_for_before_sql",
            "before_after_sql_before_sql_node_fail_on_error_log_level_for_before_sql_node",
            "before_after_sql_before_sql_node_read_from_file",
            "before_after_sql_before_sql_read_from_file",
            "before_sql",
            "before_sql_node",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "check_duplicate_rows",
            "collecting",
            "column_metadata_change_propagation",
            "column_name",
            "combinability_mode",
            "create_statement",
            "create_table_statement",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "direct_insert",
            "directory_for_log_files",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "distribution_key",
            "drop_table",
            "drop_table_statement",
            "duplicate_row_action",
            "enable_before_after_sql_for_child_element",
            "enable_case_sensitive_identifiers",
            "enable_flow_acp_control",
            "enable_record_ordering",
            "enable_schemaless_design",
            "enable_use_of_merge_join_plan_type",
            "execution_mode",
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "fail_on_error_create_statement",
            "fail_on_error_drop_statement",
            "fail_on_error_truncate_statement",
            "flow_dirty",
            "generate_create_statement_at_runtime",
            "generate_create_statement_distribution_key_column_names",
            "generate_drop_statement_at_runtime",
            "generate_statistics",
            "generate_statistics_mode",
            "generate_statistics_on_columns",
            "generate_truncate_statement_at_runtime",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_columns",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "maximum_reject_count",
            "message_type_for_create_statement_errors",
            "message_type_for_drop_statement_errors",
            "message_type_for_truncate_statement_errors",
            "other_options",
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
            "read_create_statement_from_file",
            "read_drop_statement_from_file",
            "read_truncate_statement_from_file",
            "reconciliation_input_mismatch_column_action",
            "reconciliation_mismatch_message",
            "reconciliation_type_mismatch_action",
            "reject_table_name",
            "runtime_column_propagation",
            "schema_name",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "sql_read_user_defined_sql_from_file",
            "stable",
            "stage_description",
            "table_action",
            "table_name",
            "temporary_work_table_mode",
            "temporary_work_table_name",
            "truncate_column_names",
            "truncate_length",
            "truncate_table",
            "truncate_table_statement",
            "unique",
            "unique_key_column",
            "unix_named_pipe_directory_for_load",
            "unmatched_table_column_action",
            "update_columns",
            "use_unique_key_column",
            "user_defined_sql",
            "validate_primary_keys",
            "write_mode",
        }
        required = {
            "action_column",
            "create_table_statement",
            "current_output_link_type",
            "database",
            "drop_table_statement",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "generate_create_statement_distribution_key_column_names",
            "hostname",
            "key_columns",
            "output_acp_should_hide",
            "password",
            "port",
            "table_action",
            "table_name",
            "temporary_work_table_name",
            "truncate_length",
            "truncate_table_statement",
            "twt_separate_connection_database_name",
            "unique_key_column",
            "user_defined_sql",
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
        props = {"execution_mode", "input_count", "output_count", "preserve_partitioning"}
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
                "maxRejectOutputs": 1,
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
        return {"min": 0, "max": 1}

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

    def get_allowed_as_target_props(self) -> bool:
        return True
