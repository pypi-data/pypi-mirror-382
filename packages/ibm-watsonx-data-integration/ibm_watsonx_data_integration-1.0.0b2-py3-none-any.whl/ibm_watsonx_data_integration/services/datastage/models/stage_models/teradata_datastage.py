import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.teradata_datastage_connection import (
    TeradataDatastageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.enums import TERADATA_DATASTAGE
from pydantic import Field
from typing import ClassVar


class teradata_datastage(BaseStage):

    op_name: ClassVar[str] = "TeradataConnectorPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/TeradataConnectorPX.svg"
    label: ClassVar[str] = "Teradata database for DataStage"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: TeradataDatastageConn = TeradataDatastageConn()
    access_method: TERADATA_DATASTAGE.AccessMethod | None = Field(
        TERADATA_DATASTAGE.AccessMethod.immediate, alias="access_method"
    )
    after_sql_file: str | None = Field(None, alias="before_after.after_sql_file")
    allow_duplicate_rows: TERADATA_DATASTAGE.TableActionGenerateCreateStatementCreateTableOptionsAllowDuplicateRows | None = Field(
        TERADATA_DATASTAGE.TableActionGenerateCreateStatementCreateTableOptionsAllowDuplicateRows.default,
        alias="table_action.generate_create_statement.create_table_options.allow_duplicate_rows",
    )
    array_size: int | None = Field(2000, alias="session.array_size")
    before_sql_file: str | None = Field(None, alias="before_after.before_sql_file")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: TERADATA_DATASTAGE.BufModeRonly | None = Field(
        TERADATA_DATASTAGE.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffer_usage: TERADATA_DATASTAGE.ImmediateAccessBufferUsage | None = Field(
        TERADATA_DATASTAGE.ImmediateAccessBufferUsage.share, alias="immediate_access.buffer_usage"
    )
    buffering_mode: TERADATA_DATASTAGE.BufferingMode | None = Field(
        TERADATA_DATASTAGE.BufferingMode.default, alias="buf_mode"
    )
    character_set: str | None = Field(None, alias="sql.user_defined.file.character_set")
    character_set_after_sql_file: str | None = Field(None, alias="before_after.after_sql_file.character_set")
    character_set_before_sql_file: str | None = Field(None, alias="before_after.before_sql_file.character_set")
    checkpoint_timeout: int | None = Field(0, alias="parallel_synchronization.checkpoint_timeout")
    cleanup_mode: TERADATA_DATASTAGE.BulkAccessCleanupMode | None = Field(
        TERADATA_DATASTAGE.BulkAccessCleanupMode.drop, alias="bulk_access.cleanup_mode"
    )
    collecting: TERADATA_DATASTAGE.Collecting | None = Field(TERADATA_DATASTAGE.Collecting.auto, alias="coll_type")
    column_delimiter: TERADATA_DATASTAGE.LoggingLogColumnValuesDelimiter | None = Field(
        TERADATA_DATASTAGE.LoggingLogColumnValuesDelimiter.space, alias="logging.log_column_values.delimiter"
    )
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    columns: str = Field("", alias="session.pass_lob_locator.column")
    combinability_mode: TERADATA_DATASTAGE.CombinabilityMode | None = Field(
        TERADATA_DATASTAGE.CombinabilityMode.auto, alias="combinability"
    )
    create_table_statement: str = Field("", alias="table_action.generate_create_statement.create_statement")
    credentials_input_method_ssl: TERADATA_DATASTAGE.CredentialsInputMethodSsl | None = Field(
        TERADATA_DATASTAGE.CredentialsInputMethodSsl.enter_credentials_manually, alias="credentials_input_method_ssl"
    )
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_block_size: int | None = Field(
        0, alias="table_action.generate_create_statement.create_table_options.data_block_size"
    )
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    default_port: int | None = Field(1025, alias="default_port")
    delete_multiple_rows: bool | None = Field(False, alias="bulk_access.update_load.delete_multiple_rows")
    delete_statement: str = Field(None, alias="sql.delete_statement")
    delimiter: str | None = Field(":", alias="host_port_separator")
    describe_strings_in_bytes: bool | None = Field(False, alias="describe_strings_in_bytes")
    disconnect: TERADATA_DATASTAGE.Disconnect | None = Field(TERADATA_DATASTAGE.Disconnect.never, alias="disconnect")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    drop_table_statement: str = Field("", alias="table_action.generate_drop_statement.drop_statement")
    duplicate_insert_rows: TERADATA_DATASTAGE.BulkAccessErrorControlDuplicateInsertRows | None = Field(
        TERADATA_DATASTAGE.BulkAccessErrorControlDuplicateInsertRows.default,
        alias="bulk_access.error_control.duplicate_insert_rows",
    )
    duplicate_update_rows: TERADATA_DATASTAGE.BulkAccessErrorControlDuplicateUpdateRows | None = Field(
        TERADATA_DATASTAGE.BulkAccessErrorControlDuplicateUpdateRows.default,
        alias="bulk_access.error_control.duplicate_update_rows",
    )
    enable_after_sql: str | None = Field("", alias="before_after.after")
    enable_after_sql_node: str | None = Field("", alias="before_after.after_node")
    enable_before_and_after_sql: bool | None = Field(False, alias="before_after")
    enable_before_sql: str | None = Field("", alias="before_after.before")
    enable_before_sql_node: str | None = Field("", alias="before_after.before_node")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_lob_references: bool | None = Field(False, alias="session.pass_lob_locator")
    enable_quoted_identifiers: bool | None = Field(True, alias="enable_quoted_i_ds")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    end_of_data: bool | None = Field(False, alias="transaction.end_of_wave.end_of_data")
    end_of_wave: TERADATA_DATASTAGE.TransactionEndOfWave | None = Field(
        TERADATA_DATASTAGE.TransactionEndOfWave.none, alias="transaction.end_of_wave"
    )
    end_row: int | None = Field(0, alias="limit_settings.end_row")
    end_timeout: int | None = Field(0, alias="parallel_synchronization.end_timeout")
    error_limit: int | None = Field(0, alias="bulk_access.error_limit")
    error_table_1: str | None = Field(None, alias="bulk_access.error_table1")
    error_table_2: str | None = Field(None, alias="bulk_access.error_table2")
    execution_mode: TERADATA_DATASTAGE.ExecutionMode | None = Field(
        TERADATA_DATASTAGE.ExecutionMode.default_par, alias="execmode"
    )
    fail_on_error: bool | None = Field(True, alias="sql.user_defined.request_type.fail_on_error")
    fail_on_error_after_sql: bool | None = Field(True, alias="before_after.after.fail_on_error")
    fail_on_error_after_sql_file: bool | None = Field(True, alias="before_after.after_sql_file.fail_on_error")
    fail_on_error_after_sql_node: bool | None = Field(True, alias="before_after.after_node.fail_on_error")
    fail_on_error_before_sql: bool | None = Field(True, alias="before_after.before.fail_on_error")
    fail_on_error_before_sql_file: bool | None = Field(True, alias="before_after.before_sql_file.fail_on_error")
    fail_on_error_before_sql_node: bool | None = Field(True, alias="before_after.before_node.fail_on_error")
    fail_on_error_create_statement: bool | None = Field(
        True, alias="table_action.generate_create_statement.fail_on_error"
    )
    fail_on_error_drop_statement: bool | None = Field(
        False, alias="table_action.generate_drop_statement.fail_on_error"
    )
    fail_on_error_truncate_statement: bool | None = Field(
        True, alias="table_action.generate_truncate_statement.fail_on_error"
    )
    fail_on_mload_errors: bool | None = Field(True, alias="bulk_access.fail_on_mloa_derrs")
    fail_on_size_mismatch: bool | None = Field(True, alias="session.schema_reconciliation.fail_on_size_mismatch")
    fail_on_type_mismatch: bool | None = Field(True, alias="session.schema_reconciliation.fail_on_type_mismatch")
    file: str = Field(None, alias="sql.user_defined.file")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    free_space_percent: int | None = Field(
        0, alias="table_action.generate_create_statement.create_table_options.table_free_space.free_space_percent"
    )
    generate_create_statement_at_runtime: bool | None = Field(True, alias="table_action.generate_create_statement")
    generate_drop_statement_at_runtime: bool | None = Field(True, alias="table_action.generate_drop_statement")
    generate_sql_at_runtime: bool | None = Field(False, alias="generate_sql")
    generate_truncate_statement_at_runtime: bool | None = Field(
        True, alias="table_action.generate_truncate_statement"
    )
    generate_uow_id: bool = Field(False, alias="tmsmevents.generate_uowid")
    has_reference_output: bool | None = Field(False, alias="has_ref_output")
    hide: bool | None = Field(False, alias="hide")
    inactivity_period: int = Field(300, alias="disconnect.inactivity_period")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    input_method: TERADATA_DATASTAGE.InputMethod | None = Field(
        TERADATA_DATASTAGE.InputMethod.enter_credentials_manually, alias="credentials_input_method"
    )
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    insert_statement: str = Field(None, alias="sql.insert_statement")
    interval_between_retries: int = Field(10, alias="reconnect.retry_interval")
    isolation_level: TERADATA_DATASTAGE.SessionIsolationLevel | None = Field(
        TERADATA_DATASTAGE.SessionIsolationLevel.default, alias="session.isolation_level"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    key_column: list | None = Field([], alias="record_ordering.key_column")
    limit: int | None = Field(1000, alias="limit_rows.limit")
    limit_number_of_returned_rows: bool | None = Field(False, alias="limit_rows")
    load_type: TERADATA_DATASTAGE.BulkAccessLoadType | None = Field(
        TERADATA_DATASTAGE.BulkAccessLoadType.load, alias="bulk_access.load_type"
    )
    log_column_values_on_first_row_error: bool | None = Field(False, alias="logging.log_column_values")
    log_key_values_only: bool | None = Field(False, alias="logging.log_column_values.log_keys_only")
    log_table: str | None = Field(None, alias="bulk_access.log_table")
    lookup_type: TERADATA_DATASTAGE.LookupType | None = Field(
        TERADATA_DATASTAGE.LookupType.empty, alias="lookup_type"
    )
    macro_database: str | None = Field(None, alias="bulk_access.stream_load.macro_database")
    make_duplicate_copies: TERADATA_DATASTAGE.TableActionGenerateCreateStatementCreateTableOptionsMakeDuplicateCopies | None = Field(
        TERADATA_DATASTAGE.TableActionGenerateCreateStatementCreateTableOptionsMakeDuplicateCopies.default,
        alias="table_action.generate_create_statement.create_table_options.make_duplicate_copies",
    )
    max_buffer_size: int | None = Field(0, alias="limit_settings.max_buffer_size")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    max_partition_sessions: int | None = Field(0, alias="limit_settings.max_partition_sessions")
    max_sessions: int | None = Field(0, alias="limit_settings.max_sessions")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    migrated_job: bool | None = Field(False, alias="is_migrated_job")
    min_sessions: int | None = Field(0, alias="limit_settings.min_sessions")
    missing_delete_rows: TERADATA_DATASTAGE.BulkAccessErrorControlMissingDeleteRows | None = Field(
        TERADATA_DATASTAGE.BulkAccessErrorControlMissingDeleteRows.default,
        alias="bulk_access.error_control.missing_delete_rows",
    )
    missing_update_rows: TERADATA_DATASTAGE.BulkAccessErrorControlMissingUpdateRows | None = Field(
        TERADATA_DATASTAGE.BulkAccessErrorControlMissingUpdateRows.default,
        alias="bulk_access.error_control.missing_update_rows",
    )
    number_of_retries: int = Field(3, alias="reconnect.retry_count")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(1, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    pack_size: int | None = Field(0, alias="bulk_access.stream_load.pack_size")
    parallel_synchronization: bool | None = Field(False, alias="parallel_synchronization")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    partition_by_expression: str | None = Field(
        None, alias="table_action.generate_create_statement.create_table_options.partition_by_expression"
    )
    partition_type: TERADATA_DATASTAGE.PartitionType | None = Field(
        TERADATA_DATASTAGE.PartitionType.auto, alias="part_type"
    )
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: TERADATA_DATASTAGE.PreservePartitioning | None = Field(
        TERADATA_DATASTAGE.PreservePartitioning.default_propagate, alias="preserve"
    )
    primary_index_type: TERADATA_DATASTAGE.TableActionGenerateCreateStatementCreateTableOptionsPrimaryIndexType | None = Field(
        TERADATA_DATASTAGE.TableActionGenerateCreateStatementCreateTableOptionsPrimaryIndexType.non_unique,
        alias="table_action.generate_create_statement.create_table_options.primary_index_type",
    )
    progress_interval: int | None = Field(100000, alias="limit_settings.progress_interval")
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    read_delete_statement_from_file: bool | None = Field(False, alias="sql.delete_statement.read_from_file_delete")
    read_insert_statement_from_file: bool | None = Field(False, alias="sql.insert_statement.read_from_file_insert")
    read_select_statement_from_file: bool | None = Field(False, alias="sql.select_statement.read_from_file_select")
    read_update_statement_from_file: bool | None = Field(False, alias="sql.update_statement.read_from_file_update")
    reconnect: bool | None = Field(False, alias="reconnect")
    record_count: int | None = Field(2000, alias="transaction.record_count")
    record_ordering: TERADATA_DATASTAGE.RecordOrdering | None = Field(
        TERADATA_DATASTAGE.RecordOrdering.zero, alias="record_ordering"
    )
    request_type: TERADATA_DATASTAGE.SqlUserDefinedRequestType | None = Field(
        TERADATA_DATASTAGE.SqlUserDefinedRequestType.individual, alias="sql.user_defined.request_type"
    )
    robust: TERADATA_DATASTAGE.BulkAccessStreamLoadRobust | None = Field(
        TERADATA_DATASTAGE.BulkAccessStreamLoadRobust.yes, alias="bulk_access.stream_load.robust"
    )
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    schema_name: str | None = Field(None, alias="schema_name")
    select_statement: str = Field(None, alias="sql.select_statement")
    select_statement_column: str | None = Field(None, alias="sql.select_statement.columns.column")
    serialize: TERADATA_DATASTAGE.BulkAccessStreamLoadSerialize | None = Field(
        TERADATA_DATASTAGE.BulkAccessStreamLoadSerialize.yes, alias="bulk_access.stream_load.serialize"
    )
    serialize_modified_properties: bool | None = Field(True, alias="serialize_modified_properties")
    server_character_set: str | None = Field(
        None, alias="table_action.generate_create_statement.create_table_options.server_character_set"
    )
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sleep: int | None = Field(0, alias="bulk_access.sleep")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: TERADATA_DATASTAGE.KeyColSelect | None = Field(
        TERADATA_DATASTAGE.KeyColSelect.default, alias="keyColSelect"
    )
    source_contains_temporal_colummns: bool | None = Field(False, alias="source_temporal_support")
    source_temporal_columns: TERADATA_DATASTAGE.SourceTemporalSupportTemporalColumns | None = Field(
        TERADATA_DATASTAGE.SourceTemporalSupportTemporalColumns.none, alias="source_temporal_support.temporal_columns"
    )
    source_temporal_qualifier_period_expression: str | None = Field(
        None, alias="target_temporal_support.temporal_qualifier.period_expression"
    )
    source_transaction_time_column: str = Field(
        None, alias="source_temporal_support.temporal_columns.transaction_time_column"
    )
    source_transaction_time_qualifier_date_timestamp_expression: str = Field(
        None, alias="source_temporal_support.transaction_time_qualifier.date_timestamp_expression"
    )
    source_valid_time_qualifier: TERADATA_DATASTAGE.SourceTemporalSupportValidTimeQualifier | None = Field(
        TERADATA_DATASTAGE.SourceTemporalSupportValidTimeQualifier.none,
        alias="source_temporal_support.valid_time_qualifier",
    )
    source_valid_time_qualifier_date_timestamp_expression: str = Field(
        None, alias="source_temporal_support.valid_time_qualifier.date_timestamp_expression"
    )
    source_valid_time_qualifier_period_expression: str | None = Field(
        None, alias="source_temporal_support.valid_time_qualifier.period_expression"
    )
    source_validate_time_column: str = Field(None, alias="source_temporal_support.temporal_columns.valid_time_column")
    sql_delete_statement: str | None = Field(None, alias="sql.delete_statement.tables.table")
    sql_delete_statement_character_set_name: str | None = Field(
        None, alias="sql.delete_statement.read_from_file_delete.character_set"
    )
    sql_delete_statement_parameters: str | None = Field(None, alias="sql.delete_statement.parameters.parameter")
    sql_delete_statement_where_clause: str | None = Field(None, alias="sql.delete_statement.where_clause")
    sql_insert_statement: str | None = Field(None, alias="sql.insert_statement.tables.table")
    sql_insert_statement_character_set_name: str | None = Field(
        None, alias="sql.insert_statement.read_from_file_insert.character_set"
    )
    sql_insert_statement_parameters: str | None = Field(None, alias="sql.insert_statement.parameters.parameter")
    sql_insert_statement_where_clause: str | None = Field(None, alias="sql.insert_statement.where_clause")
    sql_other_clause: str | None = Field(None, alias="sql.other_clause")
    sql_select_statement_character_set_name: str | None = Field(
        None, alias="sql.select_statement.read_from_file_select.character_set"
    )
    sql_select_statement_other_clause: str | None = Field(None, alias="sql.select_statement.other_clause")
    sql_select_statement_parameters: str | None = Field(None, alias="sql.select_statement.parameters.parameter")
    sql_select_statement_table_name: str | None = Field(None, alias="sql.select_statement.tables.table")
    sql_select_statement_where_clause: str | None = Field(None, alias="sql.select_statement.where_clause")
    sql_update_statement: str | None = Field(None, alias="sql.update_statement.tables.table")
    sql_update_statement_character_set_name: str | None = Field(
        None, alias="sql.update_statement.read_from_file_update.character_set"
    )
    sql_update_statement_parameters: str | None = Field(None, alias="sql.update_statement.parameters.parameter")
    sql_update_statement_where_clause: str | None = Field(None, alias="sql.update_statement.where_clause")
    sql_where_clause: str | None = Field(None, alias="sql.where_clause")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    start_mode: TERADATA_DATASTAGE.BulkAccessStartMode | None = Field(
        TERADATA_DATASTAGE.BulkAccessStartMode.clean, alias="bulk_access.start_mode"
    )
    start_row: int | None = Field(0, alias="limit_settings.start_row")
    sync_database: str | None = Field(None, alias="parallel_synchronization.sync_database")
    sync_id: str | None = Field(None, alias="parallel_synchronization.sync_id")
    sync_password: str | None = Field(None, alias="parallel_synchronization.sync_password")
    sync_poll: int | None = Field(0, alias="parallel_synchronization.sync_poll")
    sync_server: str | None = Field(None, alias="parallel_synchronization.sync_server")
    sync_table: str = Field(None, alias="parallel_synchronization.sync_table")
    sync_table_action: TERADATA_DATASTAGE.ParallelSynchronizationSyncTableAction | None = Field(
        TERADATA_DATASTAGE.ParallelSynchronizationSyncTableAction.create,
        alias="parallel_synchronization.sync_table_action",
    )
    sync_table_cleanup: TERADATA_DATASTAGE.ParallelSynchronizationSyncTableCleanup | None = Field(
        TERADATA_DATASTAGE.ParallelSynchronizationSyncTableCleanup.keep,
        alias="parallel_synchronization.sync_table_cleanup",
    )
    sync_table_write_mode: TERADATA_DATASTAGE.ParallelSynchronizationSyncTableWriteMode | None = Field(
        TERADATA_DATASTAGE.ParallelSynchronizationSyncTableWriteMode.insert,
        alias="parallel_synchronization.sync_table_write_mode",
    )
    sync_timeout: int | None = Field(0, alias="parallel_synchronization.sync_timeout")
    sync_user: str | None = Field(None, alias="parallel_synchronization.sync_user")
    table_action: TERADATA_DATASTAGE.TableAction = Field(TERADATA_DATASTAGE.TableAction.append, alias="table_action")
    table_free_space: TERADATA_DATASTAGE.TableActionGenerateCreateStatementCreateTableOptionsTableFreeSpace | None = Field(
        TERADATA_DATASTAGE.TableActionGenerateCreateStatementCreateTableOptionsTableFreeSpace.default,
        alias="table_action.generate_create_statement.create_table_options.table_free_space",
    )
    table_name: str = Field(None, alias="table_name")
    target_temporal_columns: TERADATA_DATASTAGE.TargetTemporalSupportTemporalColumns | None = Field(
        TERADATA_DATASTAGE.TargetTemporalSupportTemporalColumns.none, alias="target_temporal_support.temporal_columns"
    )
    target_transaction_time_column: str = Field(
        None, alias="target_temporal_support.temporal_columns.transaction_time_column"
    )
    target_validate_time_column: str = Field(None, alias="target_temporal_support.temporal_columns.valid_time_column")
    temporal_qualifier: TERADATA_DATASTAGE.TargetTemporalSupportTemporalQualifier | None = Field(
        TERADATA_DATASTAGE.TargetTemporalSupportTemporalQualifier.none,
        alias="target_temporal_support.temporal_qualifier",
    )
    temporal_support: bool | None = Field(False, alias="target_temporal_support")
    tenacity: int | None = Field(0, alias="bulk_access.tenacity")
    tmsm_event_options: bool | None = Field(False, alias="tmsmevents")
    transaction_time_qualifier: TERADATA_DATASTAGE.SourceTemporalSupportTransactionTimeQualifier | None = Field(
        TERADATA_DATASTAGE.SourceTemporalSupportTransactionTimeQualifier.none,
        alias="source_temporal_support.transaction_time_qualifier",
    )
    truncate_table_statement: str = Field("", alias="table_action.generate_truncate_statement.truncate_statement")
    unique: bool | None = Field(None, alias="part_unique")
    unused_field_action: TERADATA_DATASTAGE.SessionSchemaReconciliationUnusedFieldAction | None = Field(
        TERADATA_DATASTAGE.SessionSchemaReconciliationUnusedFieldAction.abort,
        alias="session.schema_reconciliation.unused_field_action",
    )
    uow_class: str | None = Field(None, alias="tmsmevents.uowclass")
    uow_id: str = Field(None, alias="tmsmevents.generate_uowid.uowid")
    uow_source: str | None = Field(None, alias="tmsmevents.uowsourcesystem")
    update_statement: str = Field(None, alias="sql.update_statement")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    user_defined_sql: TERADATA_DATASTAGE.SqlUserDefined = Field(
        TERADATA_DATASTAGE.SqlUserDefined.statements, alias="sql.user_defined"
    )
    user_defined_sql_statements: str = Field(None, alias="sql.user_defined.statements")
    work_table: str | None = Field(None, alias="bulk_access.work_table")
    write_mode: TERADATA_DATASTAGE.WriteMode = Field(TERADATA_DATASTAGE.WriteMode.insert, alias="write_mode")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("preserve_partitioning")
            if (self.output_count and self.output_count > 0)
            else exclude.add("preserve_partitioning")
        )
        (
            include.add("record_ordering")
            if (self.input_count and self.input_count > 1)
            else exclude.add("record_ordering")
        )
        (
            include.add("key_column")
            if (((self.input_count and self.input_count > 1)) and (self.record_ordering == 2))
            else exclude.add("key_column")
        )

        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("sql_select_statement_table_name")
            if (not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_table_name")
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
        include.add("end_timeout") if (self.parallel_synchronization) else exclude.add("end_timeout")
        (
            include.add("sleep")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("sleep")
        )
        (
            include.add("table_name")
            if (((not self.select_statement)) and (self.generate_sql_at_runtime))
            else exclude.add("table_name")
        )
        (
            include.add("transaction_time_qualifier")
            if (self.source_contains_temporal_colummns)
            else exclude.add("transaction_time_qualifier")
        )
        (
            include.add("source_validate_time_column")
            if (
                ((self.source_contains_temporal_colummns))
                and (
                    ((self.source_temporal_columns == "bi-temporal"))
                    or (self.source_temporal_columns == "valid_time")
                )
            )
            else exclude.add("source_validate_time_column")
        )
        (
            include.add("source_valid_time_qualifier_date_timestamp_expression")
            if (((self.source_contains_temporal_colummns)) and (self.source_valid_time_qualifier == "as_of"))
            else exclude.add("source_valid_time_qualifier_date_timestamp_expression")
        )
        (
            include.add("character_set_before_sql_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("character_set_before_sql_file")
        )
        (
            include.add("inactivity_period")
            if (
                (
                    (
                        self.disconnect
                        and (
                            (hasattr(self.disconnect, "value") and self.disconnect.value == "period_of_inactivity")
                            or (self.disconnect == "period_of_inactivity")
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
            include.add("source_valid_time_qualifier")
            if (self.source_contains_temporal_colummns)
            else exclude.add("source_valid_time_qualifier")
        )
        include.add("sync_table") if (self.parallel_synchronization) else exclude.add("sync_table")
        (
            include.add("fail_on_error_after_sql_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql_file")
        )
        (
            include.add("sql_select_statement_where_clause")
            if (not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_where_clause")
        )
        include.add("sync_id") if (self.parallel_synchronization) else exclude.add("sync_id")
        (
            include.add("sql_other_clause")
            if (
                ((self.generate_sql_at_runtime))
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
            else exclude.add("sql_other_clause")
        )
        (
            include.add("source_transaction_time_qualifier_date_timestamp_expression")
            if (((self.source_contains_temporal_colummns)) and (self.transaction_time_qualifier == "as_of"))
            else exclude.add("source_transaction_time_qualifier_date_timestamp_expression")
        )
        (
            include.add("fail_on_error_after_sql_node")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql_node")
        )
        (
            include.add("min_sessions")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("min_sessions")
        )
        (
            include.add("sql_where_clause")
            if (
                ((self.generate_sql_at_runtime))
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
            else exclude.add("sql_where_clause")
        )
        (
            include.add("max_partition_sessions")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("max_partition_sessions")
        )
        (
            include.add("tenacity")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("tenacity")
        )
        (
            include.add("source_transaction_time_column")
            if (
                ((self.source_contains_temporal_colummns))
                and (
                    ((self.source_temporal_columns == "bi-temporal"))
                    or (self.source_temporal_columns == "transaction_time")
                )
            )
            else exclude.add("source_transaction_time_column")
        )
        (
            include.add("read_select_statement_from_file")
            if (((not self.table_name)) and (not self.generate_sql_at_runtime))
            else exclude.add("read_select_statement_from_file")
        )
        (
            include.add("select_statement")
            if (((not self.table_name)) and (not self.generate_sql_at_runtime))
            else exclude.add("select_statement")
        )
        (
            include.add("fail_on_error_before_sql_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql_file")
        )
        (
            include.add("fail_on_error_before_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql")
        )
        (
            include.add("number_of_retries")
            if (
                ((self.reconnect))
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
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
            else exclude.add("number_of_retries")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("enable_after_sql_node")
            if (self.enable_before_and_after_sql)
            else exclude.add("enable_after_sql_node")
        )
        (
            include.add("fail_on_error_before_sql_node")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql_node")
        )
        (
            include.add("sync_table_action")
            if (self.parallel_synchronization)
            else exclude.add("sync_table_action")
        )
        (
            include.add("sql_select_statement_parameters")
            if (not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_parameters")
        )
        include.add("limit") if (self.limit_number_of_returned_rows) else exclude.add("limit")
        (
            include.add("interval_between_retries")
            if (
                ((self.reconnect))
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
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
            else exclude.add("interval_between_retries")
        )
        (
            include.add("enable_before_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("enable_before_sql")
        )
        include.add("columns") if (self.enable_lob_references) else exclude.add("columns")
        (
            include.add("max_sessions")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("max_sessions")
        )
        (
            include.add("end_of_data")
            if (((self.end_of_wave == "after")) or (self.end_of_wave == "before"))
            else exclude.add("end_of_data")
        )
        (
            include.add("before_sql_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("before_sql_file")
        )
        (
            include.add("reconnect")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
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
            include.add("sql_select_statement_other_clause")
            if (not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_other_clause")
        )
        (
            include.add("enable_after_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("enable_after_sql")
        )
        include.add("sync_user") if (self.parallel_synchronization) else exclude.add("sync_user")
        include.add("sync_timeout") if (self.parallel_synchronization) else exclude.add("sync_timeout")
        (
            include.add("source_temporal_columns")
            if (self.source_contains_temporal_colummns)
            else exclude.add("source_temporal_columns")
        )
        include.add("sync_password") if (self.parallel_synchronization) else exclude.add("sync_password")
        include.add("sync_database") if (self.parallel_synchronization) else exclude.add("sync_database")
        (
            include.add("source_contains_temporal_colummns")
            if (self.generate_sql_at_runtime)
            else exclude.add("source_contains_temporal_colummns")
        )
        (
            include.add("select_statement_column")
            if (not self.generate_sql_at_runtime)
            else exclude.add("select_statement_column")
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
            include.add("sync_table_write_mode")
            if (
                ((self.parallel_synchronization))
                and (((self.sync_table_action == "append")) or (self.sync_table_action == "create"))
            )
            else exclude.add("sync_table_write_mode")
        )
        (
            include.add("sync_table_cleanup")
            if (self.parallel_synchronization)
            else exclude.add("sync_table_cleanup")
        )
        (
            include.add("enable_before_sql_node")
            if (self.enable_before_and_after_sql)
            else exclude.add("enable_before_sql_node")
        )
        (
            include.add("sql_select_statement_character_set_name")
            if (self.read_select_statement_from_file)
            else exclude.add("sql_select_statement_character_set_name")
        )
        include.add("sync_poll") if (self.parallel_synchronization) else exclude.add("sync_poll")
        (
            include.add("after_sql_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("after_sql_file")
        )
        include.add("sync_server") if (self.parallel_synchronization) else exclude.add("sync_server")
        (
            include.add("character_set_after_sql_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("character_set_after_sql_file")
        )
        (
            include.add("source_valid_time_qualifier_period_expression")
            if (
                ((self.source_contains_temporal_colummns))
                and (
                    ((self.source_valid_time_qualifier == "non-sequenced"))
                    or (self.source_valid_time_qualifier == "sequenced")
                )
            )
            else exclude.add("source_valid_time_qualifier_period_expression")
        )
        (
            include.add("unused_field_action")
            if (


                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )


            )
            else exclude.add("unused_field_action")
        )
        (
            include.add("fail_on_error_after_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql")
        )
        (
            include.add("sql_select_statement_table_name")
            if (


                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("sql_select_statement_table_name")
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
            include.add("end_timeout")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("end_timeout")
        )
        (
            include.add("sleep")
            if (


                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )


            )
            else exclude.add("sleep")
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
            include.add("transaction_time_qualifier")
            if (


                        ((self.source_contains_temporal_colummns))
                        or (

                                self.source_contains_temporal_colummns
                                and "#" in str(self.source_contains_temporal_colummns)

                        )


            )
            else exclude.add("transaction_time_qualifier")
        )
        (
            include.add("source_validate_time_column")
            if (

                    (
                        ((self.source_contains_temporal_colummns))
                        or (
                            (
                                self.source_contains_temporal_colummns
                                and "#" in str(self.source_contains_temporal_colummns)
                            )
                        )
                    )
                    and (
                        ((self.source_temporal_columns == "bi-temporal"))
                        or (self.source_temporal_columns == "valid_time")
                        or (self.source_temporal_columns and "#" in str(self.source_temporal_columns))
                    )

            )
            else exclude.add("source_validate_time_column")
        )
        (
            include.add("source_valid_time_qualifier_date_timestamp_expression")
            if (

                    (
                        ((self.source_contains_temporal_colummns))
                        or (
                            (
                                self.source_contains_temporal_colummns
                                and "#" in str(self.source_contains_temporal_colummns)
                            )
                        )
                    )
                    and (
                        ((self.source_valid_time_qualifier == "as_of"))
                        or (self.source_valid_time_qualifier and "#" in str(self.source_valid_time_qualifier))
                    )

            )
            else exclude.add("source_valid_time_qualifier_date_timestamp_expression")
        )
        (
            include.add("character_set_before_sql_file")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("character_set_before_sql_file")
        )
        (
            include.add("inactivity_period")
            if (

                    (
                        (
                            (
                                self.disconnect
                                and (
                                    (
                                        hasattr(self.disconnect, "value")
                                        and self.disconnect.value == "period_of_inactivity"
                                    )
                                    or (self.disconnect == "period_of_inactivity")
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
            include.add("source_valid_time_qualifier")
            if (


                        ((self.source_contains_temporal_colummns))
                        or (

                                self.source_contains_temporal_colummns
                                and "#" in str(self.source_contains_temporal_colummns)

                        )


            )
            else exclude.add("source_valid_time_qualifier")
        )
        (
            include.add("sync_table")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("sync_table")
        )
        (
            include.add("fail_on_error_after_sql_file")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_after_sql_file")
        )
        (
            include.add("sql_select_statement_where_clause")
            if (


                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("sql_select_statement_where_clause")
        )
        (
            include.add("sync_id")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("sync_id")
        )
        (
            include.add("sql_other_clause")
            if (

                    (
                        ((self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
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
            else exclude.add("sql_other_clause")
        )
        (
            include.add("source_transaction_time_qualifier_date_timestamp_expression")
            if (

                    (
                        ((self.source_contains_temporal_colummns))
                        or (
                            (
                                self.source_contains_temporal_colummns
                                and "#" in str(self.source_contains_temporal_colummns)
                            )
                        )
                    )
                    and (
                        ((self.transaction_time_qualifier == "as_of"))
                        or (self.transaction_time_qualifier and "#" in str(self.transaction_time_qualifier))
                    )

            )
            else exclude.add("source_transaction_time_qualifier_date_timestamp_expression")
        )
        (
            include.add("fail_on_error_after_sql_node")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_after_sql_node")
        )
        (
            include.add("min_sessions")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                or (

                        self.access_method
                        and (
                            (
                                hasattr(self.access_method, "value")
                                and self.access_method.value
                                and "#" in str(self.access_method.value)
                            )
                            or ("#" in str(self.access_method))
                        )

                )
            )
            else exclude.add("min_sessions")
        )
        (
            include.add("sql_where_clause")
            if (

                    (
                        ((self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
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
            else exclude.add("sql_where_clause")
        )
        (
            include.add("max_partition_sessions")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                or (

                        self.access_method
                        and (
                            (
                                hasattr(self.access_method, "value")
                                and self.access_method.value
                                and "#" in str(self.access_method.value)
                            )
                            or ("#" in str(self.access_method))
                        )

                )
            )
            else exclude.add("max_partition_sessions")
        )
        (
            include.add("tenacity")
            if (


                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )


            )
            else exclude.add("tenacity")
        )
        (
            include.add("source_transaction_time_column")
            if (

                    (
                        ((self.source_contains_temporal_colummns))
                        or (
                            (
                                self.source_contains_temporal_colummns
                                and "#" in str(self.source_contains_temporal_colummns)
                            )
                        )
                    )
                    and (
                        ((self.source_temporal_columns == "bi-temporal"))
                        or (self.source_temporal_columns == "transaction_time")
                        or (self.source_temporal_columns and "#" in str(self.source_temporal_columns))
                    )

            )
            else exclude.add("source_transaction_time_column")
        )
        (
            include.add("read_select_statement_from_file")
            if (

                    (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                    and (
                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
                    )

            )
            else exclude.add("read_select_statement_from_file")
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
            include.add("fail_on_error_before_sql_file")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_before_sql_file")
        )
        (
            include.add("fail_on_error_before_sql")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_before_sql")
        )
        (
            include.add("number_of_retries")
            if (

                    (((self.reconnect)) or ((self.reconnect and "#" in str(self.reconnect))))
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
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
            else exclude.add("number_of_retries")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("enable_after_sql_node")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("enable_after_sql_node")
        )
        (
            include.add("fail_on_error_before_sql_node")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_before_sql_node")
        )
        (
            include.add("sync_table_action")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("sync_table_action")
        )
        (
            include.add("sql_select_statement_parameters")
            if (


                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("sql_select_statement_parameters")
        )
        (
            include.add("limit")
            if (


                        ((self.limit_number_of_returned_rows))
                        or (self.limit_number_of_returned_rows and "#" in str(self.limit_number_of_returned_rows))


            )
            else exclude.add("limit")
        )
        (
            include.add("interval_between_retries")
            if (

                    (((self.reconnect)) or ((self.reconnect and "#" in str(self.reconnect))))
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
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
            else exclude.add("interval_between_retries")
        )
        (
            include.add("enable_before_sql")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("enable_before_sql")
        )
        (
            include.add("columns")
            if (


                        ((self.enable_lob_references))
                        or (self.enable_lob_references and "#" in str(self.enable_lob_references))


            )
            else exclude.add("columns")
        )
        (
            include.add("max_sessions")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                or (

                        self.access_method
                        and (
                            (
                                hasattr(self.access_method, "value")
                                and self.access_method.value
                                and "#" in str(self.access_method.value)
                            )
                            or ("#" in str(self.access_method))
                        )

                )
            )
            else exclude.add("max_sessions")
        )
        (
            include.add("end_of_data")
            if (


                        ((self.end_of_wave == "after"))
                        or (self.end_of_wave == "before")
                        or (self.end_of_wave and "#" in str(self.end_of_wave))


            )
            else exclude.add("end_of_data")
        )
        (
            include.add("before_sql_file")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("before_sql_file")
        )
        (
            include.add("reconnect")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
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
            include.add("sql_select_statement_other_clause")
            if (


                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("sql_select_statement_other_clause")
        )
        (
            include.add("enable_after_sql")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("enable_after_sql")
        )
        (
            include.add("sync_user")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("sync_user")
        )
        (
            include.add("sync_timeout")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("sync_timeout")
        )
        (
            include.add("source_temporal_columns")
            if (


                        ((self.source_contains_temporal_colummns))
                        or (

                                self.source_contains_temporal_colummns
                                and "#" in str(self.source_contains_temporal_colummns)

                        )


            )
            else exclude.add("source_temporal_columns")
        )
        (
            include.add("sync_password")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("sync_password")
        )
        (
            include.add("sync_database")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("sync_database")
        )
        (
            include.add("source_contains_temporal_colummns")
            if (
                ((self.generate_sql_at_runtime))
                or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
            )
            else exclude.add("source_contains_temporal_colummns")
        )
        (
            include.add("select_statement_column")
            if (


                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("select_statement_column")
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
            include.add("sync_table_write_mode")
            if (

                    (
                        ((self.parallel_synchronization))
                        or ((self.parallel_synchronization and "#" in str(self.parallel_synchronization)))
                    )
                    and (
                        ((self.sync_table_action == "append"))
                        or (self.sync_table_action == "create")
                        or (self.sync_table_action and "#" in str(self.sync_table_action))
                    )

            )
            else exclude.add("sync_table_write_mode")
        )
        (
            include.add("sync_table_cleanup")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("sync_table_cleanup")
        )
        (
            include.add("enable_before_sql_node")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("enable_before_sql_node")
        )
        (
            include.add("sql_select_statement_character_set_name")
            if (


                        ((self.read_select_statement_from_file))
                        or (self.read_select_statement_from_file and "#" in str(self.read_select_statement_from_file))


            )
            else exclude.add("sql_select_statement_character_set_name")
        )
        (
            include.add("sync_poll")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("sync_poll")
        )
        (
            include.add("after_sql_file")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("after_sql_file")
        )
        (
            include.add("sync_server")
            if (


                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))


            )
            else exclude.add("sync_server")
        )
        (
            include.add("character_set_after_sql_file")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("character_set_after_sql_file")
        )
        (
            include.add("source_valid_time_qualifier_period_expression")
            if (

                    (
                        ((self.source_contains_temporal_colummns))
                        or (
                            (
                                self.source_contains_temporal_colummns
                                and "#" in str(self.source_contains_temporal_colummns)
                            )
                        )
                    )
                    and (
                        ((self.source_valid_time_qualifier == "non-sequenced"))
                        or (self.source_valid_time_qualifier == "sequenced")
                        or (self.source_valid_time_qualifier and "#" in str(self.source_valid_time_qualifier))
                    )

            )
            else exclude.add("source_valid_time_qualifier_period_expression")
        )
        (
            include.add("unused_field_action")
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
            else exclude.add("unused_field_action")
        )
        (
            include.add("fail_on_error_after_sql")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_after_sql")
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
        include.add("default_port") if (()) else exclude.add("default_port")
        include.add("delimiter") if (()) else exclude.add("delimiter")
        include.add("use_cas_lite_service") if (()) else exclude.add("use_cas_lite_service")
        (
            include.add("credentials_input_method_ssl")
            if ((()) and ((()) or (()) or (())))
            else exclude.add("credentials_input_method_ssl")
        )
        (
            include.add("fail_on_error_after_sql_node")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql_node")
        )
        (
            include.add("read_select_statement_from_file")
            if (not self.table_name)
            and (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("read_select_statement_from_file")
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
            include.add("source_contains_temporal_colummns")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("source_contains_temporal_colummns")
        )
        (
            include.add("select_statement_column")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("select_statement_column")
        )
        (
            include.add("fail_on_error_before_sql_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql_file")
        )
        (
            include.add("enable_after_sql_node")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("enable_after_sql_node")
        )
        (
            include.add("max_partition_sessions")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("max_partition_sessions")
        )
        (
            include.add("sync_timeout")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("sync_timeout")
        )
        (
            include.add("sync_table_action")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("sync_table_action")
        )
        (
            include.add("sql_select_statement_other_clause")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_other_clause")
        )
        (
            include.add("sql_select_statement_where_clause")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_where_clause")
        )
        (
            include.add("after_sql_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("after_sql_file")
        )
        (
            include.add("transaction_time_qualifier")
            if (self.source_contains_temporal_colummns == "true" or self.source_contains_temporal_colummns)
            else exclude.add("transaction_time_qualifier")
        )
        (
            include.add("character_set_after_sql_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("character_set_after_sql_file")
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
            include.add("unused_field_action")
            if (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("unused_field_action")
        )
        (
            include.add("lookup_type")
            if (self.has_reference_output == "true" or self.has_reference_output)
            else exclude.add("lookup_type")
        )
        (
            include.add("sql_where_clause")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
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
            else exclude.add("sql_where_clause")
        )
        (
            include.add("sync_table_cleanup")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("sync_table_cleanup")
        )
        (
            include.add("max_sessions")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("max_sessions")
        )
        (
            include.add("character_set_before_sql_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("character_set_before_sql_file")
        )
        (
            include.add("table_name")
            if (not self.select_statement)
            and (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("table_name")
        )
        (
            include.add("min_sessions")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("min_sessions")
        )
        (
            include.add("sync_poll")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("sync_poll")
        )
        (
            include.add("columns")
            if (self.enable_lob_references == "true" or self.enable_lob_references)
            else exclude.add("columns")
        )
        (
            include.add("sync_id")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("sync_id")
        )
        (
            include.add("reconnect")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
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
            include.add("before_sql_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("before_sql_file")
        )
        (
            include.add("source_valid_time_qualifier_date_timestamp_expression")
            if (self.source_contains_temporal_colummns == "true" or self.source_contains_temporal_colummns)
            and (self.source_valid_time_qualifier == "as_of")
            else exclude.add("source_valid_time_qualifier_date_timestamp_expression")
        )
        (
            include.add("enable_after_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("enable_after_sql")
        )
        (
            include.add("end_timeout")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("end_timeout")
        )
        (
            include.add("fail_on_error_before_sql_node")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql_node")
        )
        (
            include.add("sleep")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("sleep")
        )
        (
            include.add("interval_between_retries")
            if (self.reconnect == "true" or self.reconnect)
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
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
            include.add("enable_before_sql_node")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("enable_before_sql_node")
        )
        (
            include.add("source_valid_time_qualifier")
            if (self.source_contains_temporal_colummns == "true" or self.source_contains_temporal_colummns)
            else exclude.add("source_valid_time_qualifier")
        )
        (
            include.add("sql_select_statement_character_set_name")
            if (self.read_select_statement_from_file == "true" or self.read_select_statement_from_file)
            else exclude.add("sql_select_statement_character_set_name")
        )
        (
            include.add("sync_table")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("sync_table")
        )
        (
            include.add("source_valid_time_qualifier_period_expression")
            if (self.source_contains_temporal_colummns == "true" or self.source_contains_temporal_colummns)
            and (
                self.source_valid_time_qualifier
                and "non-sequenced" in str(self.source_valid_time_qualifier)
                and self.source_valid_time_qualifier
                and "sequenced" in str(self.source_valid_time_qualifier)
            )
            else exclude.add("source_valid_time_qualifier_period_expression")
        )
        (
            include.add("select_statement")
            if (not self.table_name)
            and (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("select_statement")
        )
        (
            include.add("fail_on_error_after_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql")
        )
        (
            include.add("sync_database")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("sync_database")
        )
        (
            include.add("sync_table_write_mode")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            and (
                self.sync_table_action
                and "append" in str(self.sync_table_action)
                and self.sync_table_action
                and "create" in str(self.sync_table_action)
            )
            else exclude.add("sync_table_write_mode")
        )
        (
            include.add("source_transaction_time_column")
            if (self.source_contains_temporal_colummns == "true" or self.source_contains_temporal_colummns)
            and (
                self.source_temporal_columns
                and "bi-temporal" in str(self.source_temporal_columns)
                and self.source_temporal_columns
                and "transaction_time" in str(self.source_temporal_columns)
            )
            else exclude.add("source_transaction_time_column")
        )
        (
            include.add("sql_other_clause")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
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
            else exclude.add("sql_other_clause")
        )
        (
            include.add("enable_before_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("enable_before_sql")
        )
        (
            include.add("end_of_data")
            if (
                self.end_of_wave
                and "after" in str(self.end_of_wave)
                and self.end_of_wave
                and "before" in str(self.end_of_wave)
            )
            else exclude.add("end_of_data")
        )
        (
            include.add("source_validate_time_column")
            if (self.source_contains_temporal_colummns == "true" or self.source_contains_temporal_colummns)
            and (
                self.source_temporal_columns
                and "bi-temporal" in str(self.source_temporal_columns)
                and self.source_temporal_columns
                and "valid_time" in str(self.source_temporal_columns)
            )
            else exclude.add("source_validate_time_column")
        )
        (
            include.add("fail_on_error_before_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql")
        )
        (
            include.add("sql_select_statement_parameters")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_parameters")
        )
        (
            include.add("sql_select_statement_table_name")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_table_name")
        )
        (
            include.add("sync_password")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("sync_password")
        )
        (
            include.add("source_temporal_columns")
            if (self.source_contains_temporal_colummns == "true" or self.source_contains_temporal_colummns)
            else exclude.add("source_temporal_columns")
        )
        (
            include.add("inactivity_period")
            if (
                self.disconnect
                and (
                    (hasattr(self.disconnect, "value") and self.disconnect.value == "period_of_inactivity")
                    or (self.disconnect == "period_of_inactivity")
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
            include.add("limit")
            if (self.limit_number_of_returned_rows == "true" or self.limit_number_of_returned_rows)
            else exclude.add("limit")
        )
        (
            include.add("number_of_retries")
            if (self.reconnect == "true" or self.reconnect)
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
            and (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("number_of_retries")
        )
        (
            include.add("fail_on_error_after_sql_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql_file")
        )
        (
            include.add("sync_server")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("sync_server")
        )
        (
            include.add("sync_user")
            if (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("sync_user")
        )
        (
            include.add("source_transaction_time_qualifier_date_timestamp_expression")
            if (self.source_contains_temporal_colummns == "true" or self.source_contains_temporal_colummns)
            and (self.transaction_time_qualifier == "as_of")
            else exclude.add("source_transaction_time_qualifier_date_timestamp_expression")
        )
        (
            include.add("tenacity")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("tenacity")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("target_temporal_columns")
            if (self.temporal_support)
            else exclude.add("target_temporal_columns")
        )
        (
            include.add("sql_insert_statement_character_set_name")
            if (self.read_insert_statement_from_file)
            else exclude.add("sql_insert_statement_character_set_name")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            )
            else exclude.add("update_statement")
        )
        include.add("uow_source") if (self.tmsm_event_options) else exclude.add("uow_source")
        (
            include.add("table_name")
            if (
                (
                    (
                        (
                            self.access_method
                            and (
                                (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                or (self.access_method == "bulk")
                            )
                        )
                    )
                    and (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )
                        )
                    )
                )
                or (
                    ((self.generate_sql_at_runtime))
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
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
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
                    )
                )
                or (
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
                                (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                                or (self.table_action == "truncate")
                            )

                    )
                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("sql_delete_statement")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
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
                )
            )
            else exclude.add("sql_delete_statement")
        )
        (
            include.add("sql_update_statement_parameters")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            )
            else exclude.add("sql_update_statement_parameters")
        )
        (
            include.add("temporal_support")
            if (
                (
                    ((self.generate_sql_at_runtime))
                    or (
                        ((self.generate_create_statement_at_runtime))
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
                                            and self.write_mode.value == "user-defined_sql"
                                        )
                                        or (self.write_mode == "user-defined_sql")
                                    )
                                )
                            )
                        )
                    )
                )
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )

                    )
                )
            )
            else exclude.add("temporal_support")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
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
            include.add("log_table")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("log_table")
        )
        (
            include.add("temporal_qualifier")
            if (((self.generate_sql_at_runtime)) and (self.temporal_support))
            else exclude.add("temporal_qualifier")
        )
        (
            include.add("error_limit")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("error_limit")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
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
        (
            include.add("read_delete_statement_from_file")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
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
                )
            )
            else exclude.add("read_delete_statement_from_file")
        )
        (
            include.add("sql_delete_statement_character_set_name")
            if (self.read_delete_statement_from_file)
            else exclude.add("sql_delete_statement_character_set_name")
        )
        (
            include.add("robust")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (self.load_type == "stream")
            )
            else exclude.add("robust")
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
            include.add("delete_multiple_rows")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (self.load_type == "update")
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                            or (self.write_mode == "delete")
                        )

                )
            )
            else exclude.add("delete_multiple_rows")
        )
        include.add("generate_uow_id") if (self.tmsm_event_options) else exclude.add("generate_uow_id")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
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
            include.add("pack_size")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (self.load_type == "stream")
            )
            else exclude.add("pack_size")
        )
        (
            include.add("sql_delete_statement_where_clause")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
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
                )
            )
            else exclude.add("sql_delete_statement_where_clause")
        )
        (
            include.add("checkpoint_timeout")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (self.parallel_synchronization)
            )
            else exclude.add("checkpoint_timeout")
        )
        (
            include.add("make_duplicate_copies")
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
                and (self.generate_create_statement_at_runtime)
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

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("make_duplicate_copies")
        )
        (
            include.add("sql_update_statement")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            )
            else exclude.add("sql_update_statement")
        )
        (
            include.add("interval_between_retries")
            if (
                ((self.reconnect))
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
                        )

                )
            )
            else exclude.add("interval_between_retries")
        )
        include.add("uow_class") if (self.tmsm_event_options) else exclude.add("uow_class")
        (
            include.add("target_validate_time_column")
            if (
                ((self.temporal_support))
                and (
                    ((self.target_temporal_columns == "bi-temporal"))
                    or (self.target_temporal_columns == "valid_time")
                )
            )
            else exclude.add("target_validate_time_column")
        )
        (
            include.add("uow_id")
            if (((self.tmsm_event_options)) and (not self.generate_uow_id))
            else exclude.add("uow_id")
        )
        (
            include.add("reconnect")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
                        )


            )
            else exclude.add("reconnect")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
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
            include.add("file")
            if (
                ((self.user_defined_sql == "file"))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
                        )

                )
            )
            else exclude.add("file")
        )
        (
            include.add("sql_insert_statement_parameters")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            else exclude.add("sql_insert_statement_parameters")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            )
            else exclude.add("read_update_statement_from_file")
        )
        (
            include.add("table_action")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )

            )
            else exclude.add("table_action")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
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
            include.add("macro_database")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (self.load_type == "stream")
            )
            else exclude.add("macro_database")
        )
        (
            include.add("work_table")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (((self.load_type == "load")) or (self.load_type == "update"))
            )
            else exclude.add("work_table")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
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
            include.add("character_set")
            if (
                ((self.user_defined_sql == "file"))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
                        )

                )
            )
            else exclude.add("character_set")
        )
        (
            include.add("generate_sql_at_runtime")
            if (

                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            else exclude.add("generate_sql_at_runtime")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
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
                )
            )
            else exclude.add("delete_statement")
        )
        (
            include.add("partition_by_expression")
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
                and (self.generate_create_statement_at_runtime)
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

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("partition_by_expression")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            else exclude.add("insert_statement")
        )
        (
            include.add("user_defined_sql_statements")
            if (
                ((self.user_defined_sql == "statements"))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
                        )

                )
            )
            else exclude.add("user_defined_sql_statements")
        )
        (
            include.add("sql_delete_statement_parameters")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
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
                )
            )
            else exclude.add("sql_delete_statement_parameters")
        )
        (
            include.add("inactivity_period")
            if (


                        self.disconnect
                        and (
                            (hasattr(self.disconnect, "value") and self.disconnect.value == "period_of_inactivity")
                            or (self.disconnect == "period_of_inactivity")
                        )


            )
            else exclude.add("inactivity_period")
        )
        (
            include.add("allow_duplicate_rows")
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
                and (self.generate_create_statement_at_runtime)
                and (((self.primary_index_type == "non-unique")) or (self.primary_index_type == "unique"))
                and (not self.temporal_support)
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

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("allow_duplicate_rows")
        )
        (
            include.add("log_key_values_only")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
                        )
                    )
                )
                and (self.log_column_values_on_first_row_error)
            )
            else exclude.add("log_key_values_only")
        )
        (
            include.add("target_transaction_time_column")
            if (
                ((self.temporal_support))
                and (
                    ((self.target_temporal_columns == "bi-temporal"))
                    or (self.target_temporal_columns == "transaction_time")
                )
            )
            else exclude.add("target_transaction_time_column")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
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
            include.add("duplicate_insert_rows")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (((self.load_type == "stream")) or (self.load_type == "update"))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            else exclude.add("duplicate_insert_rows")
        )
        (
            include.add("data_block_size")
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
                and (self.generate_create_statement_at_runtime)
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

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("data_block_size")
        )
        (
            include.add("serialize_modified_properties")
            if (self.generate_uow_id)
            else exclude.add("serialize_modified_properties")
        )
        (
            include.add("sql_insert_statement")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            else exclude.add("sql_insert_statement")
        )
        (
            include.add("source_temporal_qualifier_period_expression")
            if (
                ((self.generate_sql_at_runtime))
                and (self.temporal_support)
                and (self.temporal_qualifier == "sequenced_valid_time")
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
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
                )
            )
            else exclude.add("source_temporal_qualifier_period_expression")
        )
        (
            include.add("sql_insert_statement_where_clause")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            else exclude.add("sql_insert_statement_where_clause")
        )
        (
            include.add("sql_update_statement_character_set_name")
            if (self.read_update_statement_from_file)
            else exclude.add("sql_update_statement_character_set_name")
        )
        (
            include.add("number_of_retries")
            if (
                ((self.reconnect))
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
                        )

                )
            )
            else exclude.add("number_of_retries")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
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
            include.add("sql_update_statement_where_clause")
            if (
                ((not self.generate_sql_at_runtime))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            )
            else exclude.add("sql_update_statement_where_clause")
        )
        (
            include.add("missing_delete_rows")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (((self.load_type == "stream")) or (self.load_type == "update"))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                or (self.write_mode == "delete")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("missing_delete_rows")
        )
        (
            include.add("serialize")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (self.load_type == "stream")
            )
            else exclude.add("serialize")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
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
            include.add("error_table_2")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (((self.load_type == "load")) or (self.load_type == "update"))
            )
            else exclude.add("error_table_2")
        )
        (
            include.add("cleanup_mode")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("cleanup_mode")
        )
        (
            include.add("error_table_1")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("error_table_1")
        )
        (
            include.add("table_free_space")
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
                and (self.generate_create_statement_at_runtime)
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

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("table_free_space")
        )
        (
            include.add("missing_update_rows")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (((self.load_type == "stream")) or (self.load_type == "update"))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("missing_update_rows")
        )
        (
            include.add("server_character_set")
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
                and (self.generate_create_statement_at_runtime)
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

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("server_character_set")
        )
        (
            include.add("fail_on_mload_errors")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (self.load_type == "update")
            )
            else exclude.add("fail_on_mload_errors")
        )
        (
            include.add("free_space_percent")
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
                and (self.generate_create_statement_at_runtime)
                and (self.table_free_space == "yes")
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

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("free_space_percent")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            else exclude.add("read_insert_statement_from_file")
        )
        (
            include.add("request_type")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
                        )
                    )
                )
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
                        )

                )
            )
            else exclude.add("request_type")
        )
        (
            include.add("buffer_usage")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
                        )
                    )
                )
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
            else exclude.add("buffer_usage")
        )
        (
            include.add("start_mode")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("start_mode")
        )
        (
            include.add("duplicate_update_rows")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )
                    )
                )
                and (((self.load_type == "stream")) or (self.load_type == "update"))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("duplicate_update_rows")
        )
        (
            include.add("column_delimiter")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
                        )
                    )
                )
                and (self.log_column_values_on_first_row_error)
            )
            else exclude.add("column_delimiter")
        )
        (
            include.add("log_column_values_on_first_row_error")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
                        )


            )
            else exclude.add("log_column_values_on_first_row_error")
        )
        (
            include.add("load_type")
            if (


                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                            or (self.access_method == "bulk")
                        )


            )
            else exclude.add("load_type")
        )
        (
            include.add("primary_index_type")
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
                and (self.generate_create_statement_at_runtime)
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

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("primary_index_type")
        )
        (
            include.add("fail_on_error")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
                        )
                    )
                )
                and (self.request_type == "individual")
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
                        )

                )
            )
            else exclude.add("fail_on_error")
        )
        (
            include.add("target_temporal_columns")
            if (
                ((self.temporal_support)) or (self.temporal_support and "#" in str(self.temporal_support))
            )
            else exclude.add("target_temporal_columns")
        )
        (
            include.add("sql_insert_statement_character_set_name")
            if (


                        ((self.read_insert_statement_from_file))
                        or (self.read_insert_statement_from_file and "#" in str(self.read_insert_statement_from_file))


            )
            else exclude.add("sql_insert_statement_character_set_name")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("update_statement")
        )
        (
            include.add("uow_source")
            if (


                        ((self.tmsm_event_options))
                        or (self.tmsm_event_options and "#" in str(self.tmsm_event_options))


            )
            else exclude.add("uow_source")
        )
        (
            include.add("table_name")
            if (
                (
                    (
                        (
                            (
                                (
                                    self.access_method
                                    and (
                                        (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                        or (self.access_method == "bulk")
                                    )
                                )
                            )
                            or (
                                (
                                    self.access_method
                                    and (
                                        (
                                            hasattr(self.access_method, "value")
                                            and self.access_method.value
                                            and "#" in str(self.access_method.value)
                                        )
                                        or ("#" in str(self.access_method))
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
                                            and self.write_mode.value == "user-defined_sql"
                                        )
                                        or (self.write_mode == "user-defined_sql")
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
                            ((self.generate_sql_at_runtime))
                            or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                        )
                        and (
                            (
                                (
                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                        or (self.write_mode == "delete")
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
                                            and self.write_mode.value == "insert_then_update"
                                        )
                                        or (self.write_mode == "insert_then_update")
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
                                            and self.write_mode.value
                                            and "#" in str(self.write_mode.value)
                                        )
                                        or ("#" in str(self.write_mode))
                                    )

                            )
                        )

                )
                or (
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
                                (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                                or (self.table_action == "truncate")
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
            else exclude.add("table_name")
        )
        (
            include.add("sql_delete_statement")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
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
            else exclude.add("sql_delete_statement")
        )
        (
            include.add("sql_update_statement_parameters")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("sql_update_statement_parameters")
        )
        (
            include.add("temporal_support")
            if (

                    (
                        ((self.generate_sql_at_runtime))
                        or (
                            (
                                (
                                    ((self.generate_create_statement_at_runtime))
                                    or (
                                        (
                                            self.generate_create_statement_at_runtime
                                            and "#" in str(self.generate_create_statement_at_runtime)
                                        )
                                    )
                                )
                                and (
                                    (
                                        (
                                            self.table_action
                                            and (
                                                (
                                                    hasattr(self.table_action, "value")
                                                    and self.table_action.value == "create"
                                                )
                                                or (self.table_action == "create")
                                            )
                                        )
                                    )
                                    or (
                                        (
                                            self.table_action
                                            and (
                                                (
                                                    hasattr(self.table_action, "value")
                                                    and self.table_action.value == "replace"
                                                )
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
                                                (
                                                    hasattr(self.write_mode, "value")
                                                    and self.write_mode.value == "insert"
                                                )
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
                                                    and self.write_mode.value == "user-defined_sql"
                                                )
                                                or (self.write_mode == "user-defined_sql")
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
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
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
            else exclude.add("temporal_support")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            include.add("log_table")
            if (


                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )


            )
            else exclude.add("log_table")
        )
        (
            include.add("temporal_qualifier")
            if (

                    (
                        ((self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                    )
                    and (
                        ((self.temporal_support))
                        or (self.temporal_support and "#" in str(self.temporal_support))
                    )

            )
            else exclude.add("temporal_qualifier")
        )
        (
            include.add("error_limit")
            if (


                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )


            )
            else exclude.add("error_limit")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
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
            include.add("sql_delete_statement_character_set_name")
            if (


                        ((self.read_delete_statement_from_file))
                        or (self.read_delete_statement_from_file and "#" in str(self.read_delete_statement_from_file))


            )
            else exclude.add("sql_delete_statement_character_set_name")
        )
        (
            include.add("robust")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (((self.load_type == "stream")) or (self.load_type and "#" in str(self.load_type)))

            )
            else exclude.add("robust")
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
            include.add("delete_multiple_rows")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (((self.load_type == "update")) or (self.load_type and "#" in str(self.load_type)))
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
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

            )
            else exclude.add("delete_multiple_rows")
        )
        (
            include.add("generate_uow_id")
            if (


                        ((self.tmsm_event_options))
                        or (self.tmsm_event_options and "#" in str(self.tmsm_event_options))


            )
            else exclude.add("generate_uow_id")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            include.add("pack_size")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (((self.load_type == "stream")) or (self.load_type and "#" in str(self.load_type)))

            )
            else exclude.add("pack_size")
        )
        (
            include.add("sql_delete_statement_where_clause")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
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
            else exclude.add("sql_delete_statement_where_clause")
        )
        (
            include.add("checkpoint_timeout")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
                        ((self.parallel_synchronization))
                        or (self.parallel_synchronization and "#" in str(self.parallel_synchronization))
                    )

            )
            else exclude.add("checkpoint_timeout")
        )
        (
            include.add("make_duplicate_copies")
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
                        ((self.generate_create_statement_at_runtime))
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            else exclude.add("make_duplicate_copies")
        )
        (
            include.add("sql_update_statement")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("sql_update_statement")
        )
        (
            include.add("interval_between_retries")
            if (

                    (((self.reconnect)) or ((self.reconnect and "#" in str(self.reconnect))))
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )
                    )

            )
            else exclude.add("interval_between_retries")
        )
        (
            include.add("uow_class")
            if (


                        ((self.tmsm_event_options))
                        or (self.tmsm_event_options and "#" in str(self.tmsm_event_options))


            )
            else exclude.add("uow_class")
        )
        (
            include.add("target_validate_time_column")
            if (

                    (
                        ((self.temporal_support))
                        or ((self.temporal_support and "#" in str(self.temporal_support)))
                    )
                    and (
                        ((self.target_temporal_columns == "bi-temporal"))
                        or (self.target_temporal_columns == "valid_time")
                        or (self.target_temporal_columns and "#" in str(self.target_temporal_columns))
                    )

            )
            else exclude.add("target_validate_time_column")
        )
        (
            include.add("uow_id")
            if (

                    (
                        ((self.tmsm_event_options))
                        or ((self.tmsm_event_options and "#" in str(self.tmsm_event_options)))
                    )
                    and (
                        ((not self.generate_uow_id))
                        or (self.generate_uow_id and "#" in str(self.generate_uow_id))
                    )

            )
            else exclude.add("uow_id")
        )
        (
            include.add("reconnect")
            if (
                (
                    (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                            or (self.access_method == "immediate")
                        )
                    )
                )
                or (

                        self.access_method
                        and (
                            (
                                hasattr(self.access_method, "value")
                                and self.access_method.value
                                and "#" in str(self.access_method.value)
                            )
                            or ("#" in str(self.access_method))
                        )

                )
            )
            else exclude.add("reconnect")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            include.add("file")
            if (

                    (
                        ((self.user_defined_sql == "file"))
                        or ((self.user_defined_sql and "#" in str(self.user_defined_sql)))
                    )
                    and (
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

            )
            else exclude.add("file")
        )
        (
            include.add("sql_insert_statement_parameters")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("sql_insert_statement_parameters")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("read_update_statement_from_file")
        )
        (
            include.add("table_action")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            include.add("macro_database")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (((self.load_type == "stream")) or (self.load_type and "#" in str(self.load_type)))

            )
            else exclude.add("macro_database")
        )
        (
            include.add("work_table")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
                        ((self.load_type == "load"))
                        or (self.load_type == "update")
                        or (self.load_type and "#" in str(self.load_type))
                    )

            )
            else exclude.add("work_table")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            include.add("character_set")
            if (

                    (
                        ((self.user_defined_sql == "file"))
                        or ((self.user_defined_sql and "#" in str(self.user_defined_sql)))
                    )
                    and (
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

            )
            else exclude.add("character_set")
        )
        (
            include.add("generate_sql_at_runtime")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                            or (self.write_mode == "delete")
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
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                            or (self.write_mode == "insert_then_update")
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
            else exclude.add("generate_sql_at_runtime")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
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
            include.add("partition_by_expression")
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
                        ((self.generate_create_statement_at_runtime))
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            else exclude.add("partition_by_expression")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("insert_statement")
        )
        (
            include.add("user_defined_sql_statements")
            if (

                    (
                        ((self.user_defined_sql == "statements"))
                        or ((self.user_defined_sql and "#" in str(self.user_defined_sql)))
                    )
                    and (
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

            )
            else exclude.add("user_defined_sql_statements")
        )
        (
            include.add("sql_delete_statement_parameters")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
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
            else exclude.add("sql_delete_statement_parameters")
        )
        (
            include.add("inactivity_period")
            if (


                        (
                            (
                                self.disconnect
                                and (
                                    (
                                        hasattr(self.disconnect, "value")
                                        and self.disconnect.value == "period_of_inactivity"
                                    )
                                    or (self.disconnect == "period_of_inactivity")
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
            include.add("allow_duplicate_rows")
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
                        ((self.generate_create_statement_at_runtime))
                        or (

                                self.generate_create_statement_at_runtime
                                and "#" in str(self.generate_create_statement_at_runtime)

                        )
                    )
                    and (
                        ((self.primary_index_type == "non-unique"))
                        or (self.primary_index_type == "unique")
                        or (self.primary_index_type and "#" in str(self.primary_index_type))
                    )
                    and (
                        ((not self.temporal_support))
                        or (self.temporal_support and "#" in str(self.temporal_support))
                    )
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
            else exclude.add("allow_duplicate_rows")
        )
        (
            include.add("log_key_values_only")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
                        ((self.log_column_values_on_first_row_error))
                        or (

                                self.log_column_values_on_first_row_error
                                and "#" in str(self.log_column_values_on_first_row_error)

                        )
                    )

            )
            else exclude.add("log_key_values_only")
        )
        (
            include.add("target_transaction_time_column")
            if (

                    (
                        ((self.temporal_support))
                        or ((self.temporal_support and "#" in str(self.temporal_support)))
                    )
                    and (
                        ((self.target_temporal_columns == "bi-temporal"))
                        or (self.target_temporal_columns == "transaction_time")
                        or (self.target_temporal_columns and "#" in str(self.target_temporal_columns))
                    )

            )
            else exclude.add("target_transaction_time_column")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            include.add("duplicate_insert_rows")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
                        ((self.load_type == "stream"))
                        or (self.load_type == "update")
                        or (self.load_type and "#" in str(self.load_type))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("duplicate_insert_rows")
        )
        (
            include.add("data_block_size")
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
                        ((self.generate_create_statement_at_runtime))
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            else exclude.add("data_block_size")
        )
        (
            include.add("serialize_modified_properties")
            if (((self.generate_uow_id)) or (self.generate_uow_id and "#" in str(self.generate_uow_id)))
            else exclude.add("serialize_modified_properties")
        )
        (
            include.add("sql_insert_statement")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("sql_insert_statement")
        )
        (
            include.add("source_temporal_qualifier_period_expression")
            if (

                    (
                        ((self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                    )
                    and (
                        ((self.temporal_support))
                        or (self.temporal_support and "#" in str(self.temporal_support))
                    )
                    and (
                        ((self.temporal_qualifier == "sequenced_valid_time"))
                        or (self.temporal_qualifier and "#" in str(self.temporal_qualifier))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
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
            else exclude.add("source_temporal_qualifier_period_expression")
        )
        (
            include.add("sql_insert_statement_where_clause")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("sql_insert_statement_where_clause")
        )
        (
            include.add("sql_update_statement_character_set_name")
            if (


                        ((self.read_update_statement_from_file))
                        or (self.read_update_statement_from_file and "#" in str(self.read_update_statement_from_file))


            )
            else exclude.add("sql_update_statement_character_set_name")
        )
        (
            include.add("number_of_retries")
            if (

                    (((self.reconnect)) or ((self.reconnect and "#" in str(self.reconnect))))
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )
                    )

            )
            else exclude.add("number_of_retries")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            include.add("sql_update_statement_where_clause")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("sql_update_statement_where_clause")
        )
        (
            include.add("missing_delete_rows")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
                        ((self.load_type == "stream"))
                        or (self.load_type == "update")
                        or (self.load_type and "#" in str(self.load_type))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                                    or (self.write_mode == "delete")
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
            else exclude.add("missing_delete_rows")
        )
        (
            include.add("serialize")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (((self.load_type == "stream")) or (self.load_type and "#" in str(self.load_type)))

            )
            else exclude.add("serialize")
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            include.add("error_table_2")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
                        ((self.load_type == "load"))
                        or (self.load_type == "update")
                        or (self.load_type and "#" in str(self.load_type))
                    )

            )
            else exclude.add("error_table_2")
        )
        (
            include.add("cleanup_mode")
            if (


                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )


            )
            else exclude.add("cleanup_mode")
        )
        (
            include.add("error_table_1")
            if (


                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )


            )
            else exclude.add("error_table_1")
        )
        (
            include.add("table_free_space")
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
                        ((self.generate_create_statement_at_runtime))
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            else exclude.add("table_free_space")
        )
        (
            include.add("missing_update_rows")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
                        ((self.load_type == "stream"))
                        or (self.load_type == "update")
                        or (self.load_type and "#" in str(self.load_type))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("missing_update_rows")
        )
        (
            include.add("server_character_set")
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
                        ((self.generate_create_statement_at_runtime))
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            else exclude.add("server_character_set")
        )
        (
            include.add("fail_on_mload_errors")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (((self.load_type == "update")) or (self.load_type and "#" in str(self.load_type)))

            )
            else exclude.add("fail_on_mload_errors")
        )
        (
            include.add("free_space_percent")
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
                        ((self.generate_create_statement_at_runtime))
                        or (

                                self.generate_create_statement_at_runtime
                                and "#" in str(self.generate_create_statement_at_runtime)

                        )
                    )
                    and (
                        ((self.table_free_space == "yes"))
                        or (self.table_free_space and "#" in str(self.table_free_space))
                    )
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
            else exclude.add("free_space_percent")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
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
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("read_insert_statement_from_file")
        )
        (
            include.add("request_type")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
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

            )
            else exclude.add("request_type")
        )
        (
            include.add("buffer_usage")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
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
                                        and self.write_mode.value == "delete_then_insert"
                                    )
                                    or (self.write_mode == "delete_then_insert")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("buffer_usage")
        )
        (
            include.add("start_mode")
            if (


                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )


            )
            else exclude.add("start_mode")
        )
        (
            include.add("duplicate_update_rows")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
                        ((self.load_type == "stream"))
                        or (self.load_type == "update")
                        or (self.load_type and "#" in str(self.load_type))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_then_update"
                                    )
                                    or (self.write_mode == "insert_then_update")
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
            else exclude.add("duplicate_update_rows")
        )
        (
            include.add("column_delimiter")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
                        ((self.log_column_values_on_first_row_error))
                        or (

                                self.log_column_values_on_first_row_error
                                and "#" in str(self.log_column_values_on_first_row_error)

                        )
                    )

            )
            else exclude.add("column_delimiter")
        )
        (
            include.add("log_column_values_on_first_row_error")
            if (


                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )


            )
            else exclude.add("log_column_values_on_first_row_error")
        )
        (
            include.add("load_type")
            if (


                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                                    or (self.access_method == "bulk")
                                )
                            )
                        )
                        or (

                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )

                        )


            )
            else exclude.add("load_type")
        )
        (
            include.add("primary_index_type")
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
                        ((self.generate_create_statement_at_runtime))
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
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
            else exclude.add("primary_index_type")
        )
        (
            include.add("fail_on_error")
            if (

                    (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                                    or (self.access_method == "immediate")
                                )
                            )
                        )
                        or (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value
                                        and "#" in str(self.access_method.value)
                                    )
                                    or ("#" in str(self.access_method))
                                )
                            )
                        )
                    )
                    and (
                        ((self.request_type == "individual")) or (self.request_type and "#" in str(self.request_type))
                    )
                    and (
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

            )
            else exclude.add("fail_on_error")
        )
        (
            include.add("allow_duplicate_rows")
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
                self.generate_create_statement_at_runtime == "true" or self.generate_create_statement_at_runtime
            )
            and (
                self.primary_index_type
                and "non-unique" in str(self.primary_index_type)
                and self.primary_index_type
                and "unique" in str(self.primary_index_type)
            )
            and (self.temporal_support == "false" or not self.temporal_support)
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
            else exclude.add("allow_duplicate_rows")
        )
        (
            include.add("uow_class")
            if (self.tmsm_event_options == "true" or self.tmsm_event_options)
            else exclude.add("uow_class")
        )
        (
            include.add("source_temporal_qualifier_period_expression")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            and (self.temporal_support == "true" or self.temporal_support)
            and (self.temporal_qualifier == "sequenced_valid_time")
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
                )
            )
            else exclude.add("source_temporal_qualifier_period_expression")
        )
        (
            include.add("sql_insert_statement_parameters")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
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
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
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
            else exclude.add("sql_insert_statement_parameters")
        )
        (
            include.add("sql_insert_statement")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
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
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
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
            else exclude.add("sql_insert_statement")
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
            include.add("free_space_percent")
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
                self.generate_create_statement_at_runtime == "true" or self.generate_create_statement_at_runtime
            )
            and (self.table_free_space == "yes")
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
            else exclude.add("free_space_percent")
        )
        (
            include.add("serialize")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (self.load_type == "stream")
            else exclude.add("serialize")
        )
        (
            include.add("character_set")
            if (self.user_defined_sql == "file")
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("character_set")
        )
        (
            include.add("make_duplicate_copies")
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
                self.generate_create_statement_at_runtime == "true" or self.generate_create_statement_at_runtime
            )
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
            else exclude.add("make_duplicate_copies")
        )
        (
            include.add("log_table")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("log_table")
        )
        (
            include.add("sql_delete_statement_character_set_name")
            if (self.read_delete_statement_from_file == "true" or self.read_delete_statement_from_file)
            else exclude.add("sql_delete_statement_character_set_name")
        )
        (
            include.add("sql_delete_statement")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
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
            )
            else exclude.add("sql_delete_statement")
        )
        (
            include.add("table_name")
            if (
                (
                    self.access_method
                    and (
                        (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                        or (self.access_method == "bulk")
                    )
                )
                and (
                    self.write_mode
                    and (
                        (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                        or (self.write_mode == "user-defined_sql")
                    )
                )
            )
            or (
                (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
                and (
                    self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "delete" in str(self.write_mode.value)
                        )
                        or ("delete" in str(self.write_mode))
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
                            and "insert_then_update" in str(self.write_mode.value)
                        )
                        or ("insert_then_update" in str(self.write_mode))
                    )
                    and self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update" in str(self.write_mode.value)
                        )
                        or ("update" in str(self.write_mode))
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
            )
            or (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "create" in str(self.table_action.value)
                    )
                    or ("create" in str(self.table_action))
                )
                or self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
                or self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "truncate" in str(self.table_action.value)
                    )
                    or ("truncate" in str(self.table_action))
                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("load_type")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("load_type")
        )
        (
            include.add("checkpoint_timeout")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (self.parallel_synchronization == "true" or self.parallel_synchronization)
            else exclude.add("checkpoint_timeout")
        )
        (
            include.add("missing_delete_rows")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (
                self.load_type
                and "stream" in str(self.load_type)
                and self.load_type
                and "update" in str(self.load_type)
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
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
                        and "user-defined_sql" in str(self.write_mode.value)
                    )
                    or ("user-defined_sql" in str(self.write_mode))
                )
            )
            else exclude.add("missing_delete_rows")
        )
        (
            include.add("cleanup_mode")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("cleanup_mode")
        )
        (
            include.add("fail_on_mload_errors")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (self.load_type == "update")
            else exclude.add("fail_on_mload_errors")
        )
        (
            include.add("partition_by_expression")
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
                self.generate_create_statement_at_runtime == "true" or self.generate_create_statement_at_runtime
            )
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
            else exclude.add("partition_by_expression")
        )
        (
            include.add("target_temporal_columns")
            if (self.temporal_support == "true" or self.temporal_support)
            else exclude.add("target_temporal_columns")
        )
        (
            include.add("file")
            if (self.user_defined_sql == "file")
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("file")
        )
        (
            include.add("interval_between_retries")
            if (self.reconnect == "true" or self.reconnect)
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
            else exclude.add("interval_between_retries")
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
            include.add("sql_delete_statement_parameters")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
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
            )
            else exclude.add("sql_delete_statement_parameters")
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
            include.add("table_action")
            if (
                self.write_mode
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
            include.add("missing_update_rows")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (
                self.load_type
                and "stream" in str(self.load_type)
                and self.load_type
                and "update" in str(self.load_type)
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
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
            else exclude.add("missing_update_rows")
        )
        (
            include.add("uow_id")
            if (self.tmsm_event_options == "true" or self.tmsm_event_options)
            and (self.generate_uow_id == "false" or not self.generate_uow_id)
            else exclude.add("uow_id")
        )
        (
            include.add("macro_database")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (self.load_type == "stream")
            else exclude.add("macro_database")
        )
        (
            include.add("log_key_values_only")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
            and (
                self.log_column_values_on_first_row_error == "true" or self.log_column_values_on_first_row_error
            )
            else exclude.add("log_key_values_only")
        )
        (
            include.add("inactivity_period")
            if (
                self.disconnect
                and (
                    (hasattr(self.disconnect, "value") and self.disconnect.value == "period_of_inactivity")
                    or (self.disconnect == "period_of_inactivity")
                )
            )
            else exclude.add("inactivity_period")
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
            include.add("temporal_qualifier")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            and (self.temporal_support == "true" or self.temporal_support)
            else exclude.add("temporal_qualifier")
        )
        (
            include.add("column_delimiter")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
            and (
                self.log_column_values_on_first_row_error == "true" or self.log_column_values_on_first_row_error
            )
            else exclude.add("column_delimiter")
        )
        (
            include.add("sql_update_statement")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
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
            else exclude.add("sql_update_statement")
        )
        (
            include.add("uow_source")
            if (self.tmsm_event_options == "true" or self.tmsm_event_options)
            else exclude.add("uow_source")
        )
        (
            include.add("serialize_modified_properties")
            if (self.generate_uow_id == "true" or self.generate_uow_id)
            else exclude.add("serialize_modified_properties")
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
            include.add("delete_statement")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
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
            )
            else exclude.add("delete_statement")
        )
        (
            include.add("start_mode")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("start_mode")
        )
        (
            include.add("sql_update_statement_parameters")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
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
            else exclude.add("sql_update_statement_parameters")
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
            include.add("error_table_1")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("error_table_1")
        )
        (
            include.add("sql_insert_statement_character_set_name")
            if (self.read_insert_statement_from_file == "true" or self.read_insert_statement_from_file)
            else exclude.add("sql_insert_statement_character_set_name")
        )
        (
            include.add("read_delete_statement_from_file")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
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
            )
            else exclude.add("read_delete_statement_from_file")
        )
        (
            include.add("pack_size")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (self.load_type == "stream")
            else exclude.add("pack_size")
        )
        (
            include.add("user_defined_sql_statements")
            if (self.user_defined_sql == "statements")
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("user_defined_sql_statements")
        )
        (
            include.add("log_column_values_on_first_row_error")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
            else exclude.add("log_column_values_on_first_row_error")
        )
        (
            include.add("sql_update_statement_character_set_name")
            if (self.read_update_statement_from_file == "true" or self.read_update_statement_from_file)
            else exclude.add("sql_update_statement_character_set_name")
        )
        (
            include.add("table_free_space")
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
                self.generate_create_statement_at_runtime == "true" or self.generate_create_statement_at_runtime
            )
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
            else exclude.add("table_free_space")
        )
        (
            include.add("buffer_usage")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
            and (
                self.write_mode
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
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
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
            else exclude.add("buffer_usage")
        )
        (
            include.add("temporal_support")
            if (
                (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
                or (
                    (
                        self.generate_create_statement_at_runtime == "true"
                        or self.generate_create_statement_at_runtime
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
                )
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
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
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
                )
            )
            else exclude.add("temporal_support")
        )
        (
            include.add("sql_update_statement_where_clause")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
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
            else exclude.add("sql_update_statement_where_clause")
        )
        (
            include.add("robust")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (self.load_type == "stream")
            else exclude.add("robust")
        )
        (
            include.add("update_statement")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
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
            else exclude.add("update_statement")
        )
        (
            include.add("generate_uow_id")
            if (self.tmsm_event_options == "true" or self.tmsm_event_options)
            else exclude.add("generate_uow_id")
        )
        (
            include.add("error_table_2")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (
                self.load_type and "load" in str(self.load_type) and self.load_type and "update" in str(self.load_type)
            )
            else exclude.add("error_table_2")
        )
        (
            include.add("server_character_set")
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
                self.generate_create_statement_at_runtime == "true" or self.generate_create_statement_at_runtime
            )
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
            else exclude.add("server_character_set")
        )
        (
            include.add("target_validate_time_column")
            if (self.temporal_support == "true" or self.temporal_support)
            and (
                self.target_temporal_columns
                and "bi-temporal" in str(self.target_temporal_columns)
                and self.target_temporal_columns
                and "valid_time" in str(self.target_temporal_columns)
            )
            else exclude.add("target_validate_time_column")
        )
        (
            include.add("duplicate_update_rows")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (
                self.load_type
                and "stream" in str(self.load_type)
                and self.load_type
                and "update" in str(self.load_type)
            )
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
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
            else exclude.add("duplicate_update_rows")
        )
        (
            include.add("reconnect")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
            else exclude.add("reconnect")
        )
        (
            include.add("primary_index_type")
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
                self.generate_create_statement_at_runtime == "true" or self.generate_create_statement_at_runtime
            )
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
            else exclude.add("primary_index_type")
        )
        (
            include.add("generate_sql_at_runtime")
            if (
                self.write_mode
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
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
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
            else exclude.add("generate_sql_at_runtime")
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
            include.add("delete_multiple_rows")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (self.load_type == "update")
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                    or (self.write_mode == "delete")
                )
            )
            else exclude.add("delete_multiple_rows")
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
            include.add("insert_statement")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
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
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
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
            else exclude.add("insert_statement")
        )
        (
            include.add("sql_insert_statement_where_clause")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
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
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
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
            else exclude.add("sql_insert_statement_where_clause")
        )
        (
            include.add("target_transaction_time_column")
            if (self.temporal_support == "true" or self.temporal_support)
            and (
                self.target_temporal_columns
                and "bi-temporal" in str(self.target_temporal_columns)
                and self.target_temporal_columns
                and "transaction_time" in str(self.target_temporal_columns)
            )
            else exclude.add("target_transaction_time_column")
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
            include.add("request_type")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("request_type")
        )
        (
            include.add("work_table")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (
                self.load_type and "load" in str(self.load_type) and self.load_type and "update" in str(self.load_type)
            )
            else exclude.add("work_table")
        )
        (
            include.add("read_update_statement_from_file")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" in str(self.write_mode.value)
                    )
                    or ("update" in str(self.write_mode))
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
            else exclude.add("read_update_statement_from_file")
        )
        (
            include.add("read_insert_statement_from_file")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
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
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
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
            else exclude.add("read_insert_statement_from_file")
        )
        (
            include.add("data_block_size")
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
                self.generate_create_statement_at_runtime == "true" or self.generate_create_statement_at_runtime
            )
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
            else exclude.add("data_block_size")
        )
        (
            include.add("error_limit")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            else exclude.add("error_limit")
        )
        (
            include.add("number_of_retries")
            if (self.reconnect == "true" or self.reconnect)
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
            else exclude.add("number_of_retries")
        )
        (
            include.add("fail_on_error")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "immediate")
                    or (self.access_method == "immediate")
                )
            )
            and (self.request_type == "individual")
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("fail_on_error")
        )
        (
            include.add("duplicate_insert_rows")
            if (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk")
                    or (self.access_method == "bulk")
                )
            )
            and (
                self.load_type
                and "stream" in str(self.load_type)
                and self.load_type
                and "update" in str(self.load_type)
            )
            and (
                self.write_mode
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
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
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
            else exclude.add("duplicate_insert_rows")
        )
        (
            include.add("sql_delete_statement_where_clause")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" in str(self.write_mode.value)
                    )
                    or ("delete" in str(self.write_mode))
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
            )
            else exclude.add("sql_delete_statement_where_clause")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "access_method",
            "after_sql_file",
            "array_size",
            "before_sql_file",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "character_set_after_sql_file",
            "character_set_before_sql_file",
            "collecting",
            "column_metadata_change_propagation",
            "columns",
            "combinability_mode",
            "credentials_input_method_ssl",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "describe_strings_in_bytes",
            "disconnect",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_and_after_sql",
            "enable_before_sql",
            "enable_before_sql_node",
            "enable_flow_acp_control",
            "enable_lob_references",
            "enable_quoted_identifiers",
            "enable_schemaless_design",
            "end_of_data",
            "end_of_wave",
            "end_timeout",
            "execution_mode",
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_file",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_file",
            "fail_on_error_before_sql_node",
            "fail_on_size_mismatch",
            "fail_on_type_mismatch",
            "flow_dirty",
            "generate_sql_at_runtime",
            "has_reference_output",
            "hide",
            "inactivity_period",
            "input_count",
            "input_link_description",
            "input_method",
            "inputcol_properties",
            "interval_between_retries",
            "isolation_level",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_column",
            "limit",
            "limit_number_of_returned_rows",
            "lookup_type",
            "max_buffer_size",
            "max_mem_buf_size_ronly",
            "max_partition_sessions",
            "max_sessions",
            "maximum_memory_buffer_size_bytes",
            "migrated_job",
            "min_sessions",
            "number_of_retries",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "parallel_synchronization",
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
            "progress_interval",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_select_statement_from_file",
            "reconnect",
            "record_count",
            "record_ordering",
            "row_limit",
            "runtime_column_propagation",
            "schema_name",
            "select_statement",
            "select_statement_column",
            "serialize_modified_properties",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sleep",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "source_contains_temporal_colummns",
            "source_temporal_columns",
            "source_transaction_time_column",
            "source_transaction_time_qualifier_date_timestamp_expression",
            "source_valid_time_qualifier",
            "source_valid_time_qualifier_date_timestamp_expression",
            "source_valid_time_qualifier_period_expression",
            "source_validate_time_column",
            "sql_other_clause",
            "sql_select_statement_character_set_name",
            "sql_select_statement_other_clause",
            "sql_select_statement_parameters",
            "sql_select_statement_table_name",
            "sql_select_statement_where_clause",
            "sql_where_clause",
            "stable",
            "stage_description",
            "sync_database",
            "sync_id",
            "sync_password",
            "sync_poll",
            "sync_server",
            "sync_table",
            "sync_table_action",
            "sync_table_cleanup",
            "sync_table_write_mode",
            "sync_timeout",
            "sync_user",
            "table_name",
            "tenacity",
            "transaction_time_qualifier",
            "unique",
            "unused_field_action",
        }
        required = {
            "columns",
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "inactivity_period",
            "interval_between_retries",
            "maximum_bytes_per_character",
            "nls_map_name",
            "number_of_retries",
            "output_acp_should_hide",
            "password",
            "select_statement",
            "server",
            "source_transaction_time_column",
            "source_transaction_time_qualifier_date_timestamp_expression",
            "source_valid_time_qualifier_date_timestamp_expression",
            "source_validate_time_column",
            "sync_table",
            "table_name",
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
            "access_method",
            "after_sql_file",
            "allow_duplicate_rows",
            "array_size",
            "before_sql_file",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffer_usage",
            "buffering_mode",
            "character_set",
            "character_set_after_sql_file",
            "character_set_before_sql_file",
            "checkpoint_timeout",
            "cleanup_mode",
            "collecting",
            "column_delimiter",
            "column_metadata_change_propagation",
            "columns",
            "combinability_mode",
            "create_table_statement",
            "credentials_input_method_ssl",
            "current_output_link_type",
            "data_block_size",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "delete_multiple_rows",
            "delete_statement",
            "disconnect",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "drop_table_statement",
            "duplicate_insert_rows",
            "duplicate_update_rows",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_and_after_sql",
            "enable_before_sql",
            "enable_before_sql_node",
            "enable_flow_acp_control",
            "enable_lob_references",
            "enable_quoted_identifiers",
            "enable_schemaless_design",
            "end_row",
            "end_timeout",
            "error_limit",
            "error_table_1",
            "error_table_2",
            "execution_mode",
            "fail_on_error",
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_file",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_file",
            "fail_on_error_before_sql_node",
            "fail_on_error_create_statement",
            "fail_on_error_drop_statement",
            "fail_on_error_truncate_statement",
            "fail_on_mload_errors",
            "file",
            "flow_dirty",
            "free_space_percent",
            "generate_create_statement_at_runtime",
            "generate_drop_statement_at_runtime",
            "generate_sql_at_runtime",
            "generate_truncate_statement_at_runtime",
            "generate_uow_id",
            "hide",
            "inactivity_period",
            "input_count",
            "input_link_description",
            "input_method",
            "inputcol_properties",
            "insert_statement",
            "interval_between_retries",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_column",
            "load_type",
            "log_column_values_on_first_row_error",
            "log_key_values_only",
            "log_table",
            "macro_database",
            "make_duplicate_copies",
            "max_buffer_size",
            "max_mem_buf_size_ronly",
            "max_partition_sessions",
            "max_sessions",
            "maximum_memory_buffer_size_bytes",
            "migrated_job",
            "min_sessions",
            "missing_delete_rows",
            "missing_update_rows",
            "number_of_retries",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "pack_size",
            "parallel_synchronization",
            "part_stable_coll",
            "part_stable_ordered",
            "part_stable_roundrobin_coll",
            "part_unique_coll",
            "part_unique_ordered",
            "part_unique_roundrobin_coll",
            "partition_by_expression",
            "partition_type",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "preserve_partitioning",
            "primary_index_type",
            "progress_interval",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_delete_statement_from_file",
            "read_insert_statement_from_file",
            "read_update_statement_from_file",
            "reconnect",
            "record_count",
            "record_ordering",
            "request_type",
            "robust",
            "runtime_column_propagation",
            "schema_name",
            "serialize",
            "serialize_modified_properties",
            "server_character_set",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sleep",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "source_temporal_qualifier_period_expression",
            "sql_delete_statement",
            "sql_delete_statement_character_set_name",
            "sql_delete_statement_parameters",
            "sql_delete_statement_where_clause",
            "sql_insert_statement",
            "sql_insert_statement_character_set_name",
            "sql_insert_statement_parameters",
            "sql_insert_statement_where_clause",
            "sql_update_statement",
            "sql_update_statement_character_set_name",
            "sql_update_statement_parameters",
            "sql_update_statement_where_clause",
            "stable",
            "stage_description",
            "start_mode",
            "start_row",
            "sync_database",
            "sync_id",
            "sync_password",
            "sync_poll",
            "sync_server",
            "sync_table",
            "sync_table_action",
            "sync_table_cleanup",
            "sync_table_write_mode",
            "sync_timeout",
            "sync_user",
            "table_action",
            "table_free_space",
            "table_name",
            "target_temporal_columns",
            "target_transaction_time_column",
            "target_validate_time_column",
            "temporal_qualifier",
            "temporal_support",
            "tenacity",
            "tmsm_event_options",
            "truncate_table_statement",
            "unique",
            "unused_field_action",
            "uow_class",
            "uow_id",
            "uow_source",
            "update_statement",
            "user_defined_sql",
            "user_defined_sql_statements",
            "work_table",
            "write_mode",
        }
        required = {
            "columns",
            "create_table_statement",
            "current_output_link_type",
            "delete_statement",
            "drop_table_statement",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "file",
            "generate_uow_id",
            "inactivity_period",
            "insert_statement",
            "interval_between_retries",
            "maximum_bytes_per_character",
            "nls_map_name",
            "number_of_retries",
            "output_acp_should_hide",
            "password",
            "server",
            "sync_table",
            "table_action",
            "table_name",
            "target_transaction_time_column",
            "target_validate_time_column",
            "truncate_table_statement",
            "uow_id",
            "update_statement",
            "user_defined_sql",
            "user_defined_sql_statements",
            "username",
            "write_mode",
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
            "execution_mode",
            "input_count",
            "key_column",
            "output_count",
            "preserve_partitioning",
            "record_ordering",
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
