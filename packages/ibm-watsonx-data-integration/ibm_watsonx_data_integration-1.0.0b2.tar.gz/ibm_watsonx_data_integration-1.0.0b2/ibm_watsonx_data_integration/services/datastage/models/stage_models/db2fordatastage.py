import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.db2fordatastage_connection import (
    Db2fordatastageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.enums import DB2FORDATASTAGE
from pydantic import Field
from typing import ClassVar


class db2fordatastage(BaseStage):

    op_name: ClassVar[str] = "DB2ConnectorPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/DB2ConnectorPX.svg"
    label: ClassVar[str] = "IBM Db2 for DataStage"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: Db2fordatastageConn = Db2fordatastageConn()
    advanced_connection_settings: bool | None = Field(True, alias="advanced")
    allow_access_mode: DB2FORDATASTAGE.LoadControlAllowAccessMode | None = Field(
        DB2FORDATASTAGE.LoadControlAllowAccessMode.no_access, alias="load_control.allow_access_mode"
    )
    allow_changes: bool | None = Field(False, alias="load_to_zos.image_copy_function.allow_changes")
    array_size: int | None = Field(2000, alias="session.array_size")
    atomic_arrays: DB2FORDATASTAGE.SessionInsertBufferingAtomicArrays | None = Field(
        DB2FORDATASTAGE.SessionInsertBufferingAtomicArrays.auto, alias="session.insert_buffering.atomic_arrays"
    )
    auto_commit_mode: DB2FORDATASTAGE.SessionAutocommitMode | None = Field(
        DB2FORDATASTAGE.SessionAutocommitMode.off, alias="session.autocommit_mode"
    )
    batch_pipe_system_id: str = Field(None, alias="load_to_zos.batch_pipe_system_id")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: DB2FORDATASTAGE.BufModeRonly | None = Field(
        DB2FORDATASTAGE.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffer_pool: str | None = Field(None, alias="table_action.generate_create_statement.create_table_bufferpool")
    buffering_mode: DB2FORDATASTAGE.BufferingMode | None = Field(
        DB2FORDATASTAGE.BufferingMode.default, alias="buf_mode"
    )
    bulk_load_to_db2_on_z_os: bool | None = Field(False, alias="load_to_zos")
    bulk_load_with_lob_or_xml_columns: bool | None = Field(False, alias="load_control.bulkload_with_lob_xml")
    ccsid: str = Field(None, alias="load_to_zos.encoding.ccsid")
    change_limit_percent_1: int | None = Field(None, alias="load_to_zos.image_copy_function.change_limit_percent1")
    change_limit_percent_2: int | None = Field(None, alias="load_to_zos.image_copy_function.change_limit_percent2")
    check_pending_cascade: DB2FORDATASTAGE.LoadControlCheckPendingCascade | None = Field(
        DB2FORDATASTAGE.LoadControlCheckPendingCascade.deferred, alias="load_control.check_pending_cascade"
    )
    check_truncation: bool | None = Field(False, alias="load_control.partitioned_db_config.check_truncation")
    clean_up_on_failure: bool | None = Field(False, alias="load_control.cleanup_on_fail")
    collecting: DB2FORDATASTAGE.Collecting | None = Field(DB2FORDATASTAGE.Collecting.auto, alias="coll_type")
    column_delimiter: DB2FORDATASTAGE.LoggingLogColumnValuesDelimiter | None = Field(
        DB2FORDATASTAGE.LoggingLogColumnValuesDelimiter.space, alias="logging.log_column_values.delimiter"
    )
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    columns: str = Field("", alias="session.pass_lob_locator.column")
    combinability_mode: DB2FORDATASTAGE.CombinabilityMode | None = Field(
        DB2FORDATASTAGE.CombinabilityMode.auto, alias="combinability"
    )
    compress: DB2FORDATASTAGE.TableActionGenerateCreateStatementCreateTableCompress | None = Field(
        DB2FORDATASTAGE.TableActionGenerateCreateStatementCreateTableCompress.database_default,
        alias="table_action.generate_create_statement.create_table_compress",
    )
    concurrent_access_level: DB2FORDATASTAGE.LoadToZosShrLevel | None = Field(
        DB2FORDATASTAGE.LoadToZosShrLevel.none, alias="load_to_zos.shr_level"
    )
    copy_loaded_data: DB2FORDATASTAGE.LoadControlCopyLoadedData | None = Field(
        DB2FORDATASTAGE.LoadControlCopyLoadedData.no_copy, alias="load_control.copy_loaded_data"
    )
    cpu_parallelism: int | None = Field(0, alias="load_control.cpu_parallelism")
    create_table_statement: str = Field("", alias="table_action.generate_create_statement.create_statement")
    credentials_input_method_ssl: DB2FORDATASTAGE.CredentialsInputMethodSsl | None = Field(
        DB2FORDATASTAGE.CredentialsInputMethodSsl.enter_credentials_manually, alias="credentials_input_method_ssl"
    )
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_buffer_size: int | None = Field(0, alias="load_control.data_buffer_size")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    delete_statement: str = Field(None, alias="sql.delete_statement")
    device_type: str | None = Field("SYSDA", alias="load_to_zos.device_type")
    direct_insert: bool | None = Field(True, alias="sql.direct_insert")
    directory_for_data_and_command_files: str = Field(None, alias="load_control.data_file_path")
    directory_for_data_files: str | None = Field(None, alias="load_to_zos.transfer.data_file_path")
    directory_for_log_files: str | None = Field(None, alias="session.use_external_tables.log_directory")
    directory_for_named_pipe: str | None = Field(
        "/tmp", alias="session.use_external_tables.directory_for_named_pipe"
    )
    directory_for_named_pipe_unix_only: str | None = Field("/tmp", alias="load_control.directory_for_named_pipe")
    disk_parallelism: int | None = Field(0, alias="load_control.disk_parallelism")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    distribute_by: DB2FORDATASTAGE.TableActionGenerateCreateStatementCreateTableDistributeBy | None = Field(
        DB2FORDATASTAGE.TableActionGenerateCreateStatementCreateTableDistributeBy.none,
        alias="table_action.generate_create_statement.create_table_distribute_by",
    )
    drop_table: bool | None = Field(True, alias="session.temporary_work_table.drop_table")
    drop_table_statement: str = Field("", alias="table_action.generate_drop_statement.drop_statement")
    drop_unmatched_fields: bool | None = Field(True, alias="session.schema_reconciliation.drop_unmatched_fields")
    dsn_prefix: str | None = Field(None, alias="load_to_zos.dsn_prefix")
    enable_after_sql: str | None = Field("", alias="before_after.after")
    enable_after_sql_node: str | None = Field("", alias="before_after.after_node")
    enable_before_and_after_sql: bool | None = Field(False, alias="before_after")
    enable_before_sql: str | None = Field("", alias="before_after.before")
    enable_before_sql_node: str | None = Field("", alias="before_after.before_node")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_lob_references: bool | None = Field(False, alias="session.pass_lob_locator")
    enable_partitioned_reads: bool | None = Field(False, alias="sql.enable_partitioning")
    enable_quoted_identifiers: bool | None = Field(True, alias="enable_quoted_i_ds")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    encoding: DB2FORDATASTAGE.LoadToZosEncoding | None = Field(
        DB2FORDATASTAGE.LoadToZosEncoding.ebcdic, alias="load_to_zos.encoding"
    )
    end_of_data: bool | None = Field(False, alias="transaction.end_of_wave.end_of_data")
    end_of_wave: DB2FORDATASTAGE.TransactionEndOfWave | None = Field(
        DB2FORDATASTAGE.TransactionEndOfWave.none, alias="transaction.end_of_wave"
    )
    exception_table_name: str | None = Field(None, alias="load_control.exception_table")
    execution_mode: DB2FORDATASTAGE.ExecutionMode | None = Field(
        DB2FORDATASTAGE.ExecutionMode.default_par, alias="execmode"
    )
    external_table_collect_statistics_during_load: bool | None = Field(
        False, alias="session.use_external_tables.statistics"
    )
    external_tables_other_options: str | None = Field("", alias="session.use_external_tables.other_options")
    fail_on_code_page_mismatch: bool | None = Field(
        False, alias="session.schema_reconciliation.fail_on_code_page_mismatch"
    )
    fail_on_error: bool | None = Field(True, alias="sql.user_defined_sql.fail_on_error")
    fail_on_error_after_sql: bool | None = Field(True, alias="before_after.after.fail_on_error")
    fail_on_error_after_sql_node: bool | None = Field(True, alias="before_after.after_node.fail_on_error")
    fail_on_error_before_sql: bool | None = Field(True, alias="before_after.before.fail_on_error")
    fail_on_error_before_sql_node: bool | None = Field(True, alias="before_after.before_node.fail_on_error")
    fail_on_error_create_statement: bool | None = Field(
        True, alias="table_action.generate_create_statement.fail_on_error"
    )
    fail_on_error_drop_statement: bool | None = Field(
        True, alias="table_action.generate_drop_statement.fail_on_error"
    )
    fail_on_error_truncate_statement: bool | None = Field(
        True, alias="table_action.generate_truncate_statement.fail_on_error"
    )
    fail_on_row_error: bool | None = Field(True, alias="session.fail_on_row_error_px")
    fail_on_size_mismatch: bool | None = Field(True, alias="session.schema_reconciliation.fail_on_size_mismatch")
    fail_on_type_mismatch: bool | None = Field(True, alias="session.schema_reconciliation.fail_on_type_mismatch")
    file_type: DB2FORDATASTAGE.LoadControlFileType | None = Field(
        DB2FORDATASTAGE.LoadControlFileType.asc, alias="load_control.file_type"
    )
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    generate_create_statement_at_runtime: bool | None = Field(True, alias="table_action.generate_create_statement")
    generate_create_statement_distribute_by_hash_key_column_names: str = Field(
        None, alias="table_action.generate_create_statement.create_table_distribute_by.hash_key_columns"
    )
    generate_drop_statement_at_runtime: bool | None = Field(True, alias="table_action.generate_drop_statement")
    generate_partitioning_sql: bool | None = Field(
        True, alias="sql.enable_partitioning.partitioning_method.gen_partitioning_sql"
    )
    generate_sql_at_runtime: bool | None = Field(False, alias="generate_sql")
    generate_truncate_statement_at_runtime: bool | None = Field(
        True, alias="table_action.generate_truncate_statement"
    )
    graphic_character_set: str | None = Field(None, alias="load_to_zos.encoding.graphic_character_set")
    has_reference_output: bool | None = Field(False, alias="has_ref_output")
    has_reject_output: bool | None = Field(False, alias="has_reject_output")
    hfs_file_directory: str = Field(None, alias="load_to_zos.transfer.uss_file_directory")
    hide: bool | None = Field(False, alias="hide")
    higher_port_number: int = Field(None, alias="load_control.partitioned_db_config.port_range.max_value")
    hold_quiesce: bool | None = Field(False, alias="load_control.hold_quiesce")
    image_copy_function: DB2FORDATASTAGE.LoadToZosImageCopyFunction | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunction.no, alias="load_to_zos.image_copy_function"
    )
    index_in: str | None = Field(None, alias="table_action.generate_create_statement.create_table_index_in")
    indexing_mode: DB2FORDATASTAGE.LoadControlIndexingMode | None = Field(
        DB2FORDATASTAGE.LoadControlIndexingMode.automatic_selection, alias="load_control.indexing_mode"
    )
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    input_link_ordering: list | None = Field(
        [{"link_label": "0", "link_name": "Link_36"}], alias="InputlinkOrderingList"
    )
    input_method: DB2FORDATASTAGE.InputMethod | None = Field(
        DB2FORDATASTAGE.InputMethod.enter_credentials_manually, alias="credentials_input_method"
    )
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    insert_buffering: DB2FORDATASTAGE.SessionInsertBuffering | None = Field(
        DB2FORDATASTAGE.SessionInsertBuffering.default, alias="session.insert_buffering"
    )
    insert_statement: str = Field(None, alias="sql.insert_statement")
    interval_between_retries: int = Field(10, alias="load_to_zos.transfer.retry_connection.retry_interval")
    isolate_partition_errors: DB2FORDATASTAGE.LoadControlPartitionedDbConfigIsolatePartErrors | None = Field(
        DB2FORDATASTAGE.LoadControlPartitionedDbConfigIsolatePartErrors.load_errors_only,
        alias="load_control.partitioned_db_config.isolate_part_errors",
    )
    isolation_level: DB2FORDATASTAGE.SessionIsolationLevel | None = Field(
        DB2FORDATASTAGE.SessionIsolationLevel.cursor_stability, alias="session.isolation_level"
    )
    keep_existing_records_in_table_space: bool | None = Field(True, alias="load_to_zos.resume")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    key_column: list | None = Field([], alias="record_ordering.key_column")
    key_columns: str | None = Field(None, alias="sql.key_columns")
    library_used_to_copy: str = Field("", alias="load_control.copy_loaded_data.copy_load_library_name")
    limit: int | None = Field(1000, alias="limit_rows.limit")
    limit_number_of_returned_rows: bool | None = Field(False, alias="limit_rows")
    limit_parallelism: bool | None = Field(False, alias="limit_parallelism")
    load_control_dump_file: str | None = Field(None, alias="load_control.file_type_modifiers.dump_file")
    load_control_files_only: bool | None = Field(False, alias="load_control.files_only")
    load_control_load_method: DB2FORDATASTAGE.LoadControlLoadMethod | None = Field(
        DB2FORDATASTAGE.LoadControlLoadMethod.named_pipes, alias="load_control.load_method"
    )
    load_control_statistics: bool | None = Field(False, alias="load_control.statistics")
    load_mode: DB2FORDATASTAGE.LoadControlLoadMode | None = Field(
        DB2FORDATASTAGE.LoadControlLoadMode.insert, alias="load_control.load_mode"
    )
    load_timeout: int | None = Field(300, alias="load_control.load_timeout")
    load_to_zos_data_file_attributes_discard_data_set_data_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.discard_data_set.data_class"
    )
    load_to_zos_data_file_attributes_discard_data_set_dataset_name: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.discard_data_set.dataset_name"
    )
    load_to_zos_data_file_attributes_discard_data_set_file_disposition_abnormal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesDiscardDataSetFileDispositionAbnormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesDiscardDataSetFileDispositionAbnormalTermination.catalog,
        alias="load_to_zos.data_file_attributes.discard_data_set.file_disposition.abnormal_termination",
    )
    load_to_zos_data_file_attributes_discard_data_set_file_disposition_normal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesDiscardDataSetFileDispositionNormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesDiscardDataSetFileDispositionNormalTermination.catalog,
        alias="load_to_zos.data_file_attributes.discard_data_set.file_disposition.normal_termination",
    )
    load_to_zos_data_file_attributes_discard_data_set_file_disposition_status: DB2FORDATASTAGE.LoadToZosDataFileAttributesDiscardDataSetFileDispositionStatus | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesDiscardDataSetFileDispositionStatus.replace,
        alias="load_to_zos.data_file_attributes.discard_data_set.file_disposition.status",
    )
    load_to_zos_data_file_attributes_discard_data_set_management_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.discard_data_set.management_class"
    )
    load_to_zos_data_file_attributes_discard_data_set_number_of_buffers: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.discard_data_set.number_of_buffers"
    )
    load_to_zos_data_file_attributes_discard_data_set_primary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.discard_data_set.primary_allocation"
    )
    load_to_zos_data_file_attributes_discard_data_set_secondary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.discard_data_set.secondary_allocation"
    )
    load_to_zos_data_file_attributes_discard_data_set_space_type: DB2FORDATASTAGE.LoadToZosDataFileAttributesDiscardDataSetSpaceType | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesDiscardDataSetSpaceType.cylinders,
        alias="load_to_zos.data_file_attributes.discard_data_set.space_type",
    )
    load_to_zos_data_file_attributes_discard_data_set_storage_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.discard_data_set.storage_class"
    )
    load_to_zos_data_file_attributes_discard_data_set_unit: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.discard_data_set.unit"
    )
    load_to_zos_data_file_attributes_discard_data_set_volumes: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.discard_data_set.volumes"
    )
    load_to_zos_data_file_attributes_error_data_set_data_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.error_data_set.data_class"
    )
    load_to_zos_data_file_attributes_error_data_set_dataset_name: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.error_data_set.dataset_name"
    )
    load_to_zos_data_file_attributes_error_data_set_file_disposition_abnormal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesErrorDataSetFileDispositionAbnormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesErrorDataSetFileDispositionAbnormalTermination.catalog,
        alias="load_to_zos.data_file_attributes.error_data_set.file_disposition.abnormal_termination",
    )
    load_to_zos_data_file_attributes_error_data_set_file_disposition_normal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesErrorDataSetFileDispositionNormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesErrorDataSetFileDispositionNormalTermination.catalog,
        alias="load_to_zos.data_file_attributes.error_data_set.file_disposition.normal_termination",
    )
    load_to_zos_data_file_attributes_error_data_set_file_disposition_status: DB2FORDATASTAGE.LoadToZosDataFileAttributesErrorDataSetFileDispositionStatus | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesErrorDataSetFileDispositionStatus.replace,
        alias="load_to_zos.data_file_attributes.error_data_set.file_disposition.status",
    )
    load_to_zos_data_file_attributes_error_data_set_management_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.error_data_set.management_class"
    )
    load_to_zos_data_file_attributes_error_data_set_number_of_buffers: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.error_data_set.number_of_buffers"
    )
    load_to_zos_data_file_attributes_error_data_set_primary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.error_data_set.primary_allocation"
    )
    load_to_zos_data_file_attributes_error_data_set_secondary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.error_data_set.secondary_allocation"
    )
    load_to_zos_data_file_attributes_error_data_set_space_type: DB2FORDATASTAGE.LoadToZosDataFileAttributesErrorDataSetSpaceType | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesErrorDataSetSpaceType.cylinders,
        alias="load_to_zos.data_file_attributes.error_data_set.space_type",
    )
    load_to_zos_data_file_attributes_error_data_set_storage_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.error_data_set.storage_class"
    )
    load_to_zos_data_file_attributes_error_data_set_unit: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.error_data_set.unit"
    )
    load_to_zos_data_file_attributes_error_data_set_volumes: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.error_data_set.volumes"
    )
    load_to_zos_data_file_attributes_input_data_files_data_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.input_data_files.data_class"
    )
    load_to_zos_data_file_attributes_input_data_files_dataset_name: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.input_data_files.dataset_name"
    )
    load_to_zos_data_file_attributes_input_data_files_file_disposition_abnormal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesInputDataFilesFileDispositionAbnormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesInputDataFilesFileDispositionAbnormalTermination.keep,
        alias="load_to_zos.data_file_attributes.input_data_files.file_disposition.abnormal_termination",
    )
    load_to_zos_data_file_attributes_input_data_files_file_disposition_normal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesInputDataFilesFileDispositionNormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesInputDataFilesFileDispositionNormalTermination.keep,
        alias="load_to_zos.data_file_attributes.input_data_files.file_disposition.normal_termination",
    )
    load_to_zos_data_file_attributes_input_data_files_file_disposition_status: DB2FORDATASTAGE.LoadToZosDataFileAttributesInputDataFilesFileDispositionStatus | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesInputDataFilesFileDispositionStatus.replace,
        alias="load_to_zos.data_file_attributes.input_data_files.file_disposition.status",
    )
    load_to_zos_data_file_attributes_input_data_files_management_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.input_data_files.management_class"
    )
    load_to_zos_data_file_attributes_input_data_files_number_of_buffers: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.input_data_files.number_of_buffers"
    )
    load_to_zos_data_file_attributes_input_data_files_primary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.input_data_files.primary_allocation"
    )
    load_to_zos_data_file_attributes_input_data_files_secondary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.input_data_files.secondary_allocation"
    )
    load_to_zos_data_file_attributes_input_data_files_space_type: DB2FORDATASTAGE.LoadToZosDataFileAttributesInputDataFilesSpaceType | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesInputDataFilesSpaceType.cylinders,
        alias="load_to_zos.data_file_attributes.input_data_files.space_type",
    )
    load_to_zos_data_file_attributes_input_data_files_storage_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.input_data_files.storage_class"
    )
    load_to_zos_data_file_attributes_input_data_files_unit: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.input_data_files.unit"
    )
    load_to_zos_data_file_attributes_input_data_files_volumes: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.input_data_files.volumes"
    )
    load_to_zos_data_file_attributes_map_data_set_data_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.map_data_set.data_class"
    )
    load_to_zos_data_file_attributes_map_data_set_dataset_name: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.map_data_set.dataset_name"
    )
    load_to_zos_data_file_attributes_map_data_set_file_disposition_abnormal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesMapDataSetFileDispositionAbnormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesMapDataSetFileDispositionAbnormalTermination.catalog,
        alias="load_to_zos.data_file_attributes.map_data_set.file_disposition.abnormal_termination",
    )
    load_to_zos_data_file_attributes_map_data_set_file_disposition_normal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesMapDataSetFileDispositionNormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesMapDataSetFileDispositionNormalTermination.catalog,
        alias="load_to_zos.data_file_attributes.map_data_set.file_disposition.normal_termination",
    )
    load_to_zos_data_file_attributes_map_data_set_file_disposition_status: DB2FORDATASTAGE.LoadToZosDataFileAttributesMapDataSetFileDispositionStatus | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesMapDataSetFileDispositionStatus.replace,
        alias="load_to_zos.data_file_attributes.map_data_set.file_disposition.status",
    )
    load_to_zos_data_file_attributes_map_data_set_management_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.map_data_set.management_class"
    )
    load_to_zos_data_file_attributes_map_data_set_number_of_buffers: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.map_data_set.number_of_buffers"
    )
    load_to_zos_data_file_attributes_map_data_set_primary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.map_data_set.primary_allocation"
    )
    load_to_zos_data_file_attributes_map_data_set_secondary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.map_data_set.secondary_allocation"
    )
    load_to_zos_data_file_attributes_map_data_set_space_type: DB2FORDATASTAGE.LoadToZosDataFileAttributesMapDataSetSpaceType | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesMapDataSetSpaceType.cylinders,
        alias="load_to_zos.data_file_attributes.map_data_set.space_type",
    )
    load_to_zos_data_file_attributes_map_data_set_storage_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.map_data_set.storage_class"
    )
    load_to_zos_data_file_attributes_map_data_set_unit: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.map_data_set.unit"
    )
    load_to_zos_data_file_attributes_map_data_set_volumes: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.map_data_set.volumes"
    )
    load_to_zos_data_file_attributes_work1_data_set_data_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work1_data_set.data_class"
    )
    load_to_zos_data_file_attributes_work1_data_set_dataset_name: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work1_data_set.dataset_name"
    )
    load_to_zos_data_file_attributes_work1_data_set_file_disposition_abnormal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesWork1DataSetFileDispositionAbnormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesWork1DataSetFileDispositionAbnormalTermination.delete,
        alias="load_to_zos.data_file_attributes.work1_data_set.file_disposition.abnormal_termination",
    )
    load_to_zos_data_file_attributes_work1_data_set_file_disposition_normal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesWork1DataSetFileDispositionNormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesWork1DataSetFileDispositionNormalTermination.delete,
        alias="load_to_zos.data_file_attributes.work1_data_set.file_disposition.normal_termination",
    )
    load_to_zos_data_file_attributes_work1_data_set_file_disposition_status: DB2FORDATASTAGE.LoadToZosDataFileAttributesWork1DataSetFileDispositionStatus | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesWork1DataSetFileDispositionStatus.replace,
        alias="load_to_zos.data_file_attributes.work1_data_set.file_disposition.status",
    )
    load_to_zos_data_file_attributes_work1_data_set_management_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work1_data_set.management_class"
    )
    load_to_zos_data_file_attributes_work1_data_set_number_of_buffers: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.work1_data_set.number_of_buffers"
    )
    load_to_zos_data_file_attributes_work1_data_set_primary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.work1_data_set.primary_allocation"
    )
    load_to_zos_data_file_attributes_work1_data_set_secondary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.work1_data_set.secondary_allocation"
    )
    load_to_zos_data_file_attributes_work1_data_set_space_type: DB2FORDATASTAGE.LoadToZosDataFileAttributesWork1DataSetSpaceType | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesWork1DataSetSpaceType.cylinders,
        alias="load_to_zos.data_file_attributes.work1_data_set.space_type",
    )
    load_to_zos_data_file_attributes_work1_data_set_storage_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work1_data_set.storage_class"
    )
    load_to_zos_data_file_attributes_work1_data_set_unit: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work1_data_set.unit"
    )
    load_to_zos_data_file_attributes_work1_data_set_volumes: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work1_data_set.volumes"
    )
    load_to_zos_data_file_attributes_work2_data_set_data_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work2_data_set.data_class"
    )
    load_to_zos_data_file_attributes_work2_data_set_dataset_name: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work2_data_set.dataset_name"
    )
    load_to_zos_data_file_attributes_work2_data_set_file_disposition_abnormal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesWork2DataSetFileDispositionAbnormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesWork2DataSetFileDispositionAbnormalTermination.delete,
        alias="load_to_zos.data_file_attributes.work2_data_set.file_disposition.abnormal_termination",
    )
    load_to_zos_data_file_attributes_work2_data_set_file_disposition_normal_termination: DB2FORDATASTAGE.LoadToZosDataFileAttributesWork2DataSetFileDispositionNormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesWork2DataSetFileDispositionNormalTermination.delete,
        alias="load_to_zos.data_file_attributes.work2_data_set.file_disposition.normal_termination",
    )
    load_to_zos_data_file_attributes_work2_data_set_file_disposition_status: DB2FORDATASTAGE.LoadToZosDataFileAttributesWork2DataSetFileDispositionStatus | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesWork2DataSetFileDispositionStatus.replace,
        alias="load_to_zos.data_file_attributes.work2_data_set.file_disposition.status",
    )
    load_to_zos_data_file_attributes_work2_data_set_management_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work2_data_set.management_class"
    )
    load_to_zos_data_file_attributes_work2_data_set_number_of_buffers: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.work2_data_set.number_of_buffers"
    )
    load_to_zos_data_file_attributes_work2_data_set_primary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.work2_data_set.primary_allocation"
    )
    load_to_zos_data_file_attributes_work2_data_set_secondary_allocation: int | None = Field(
        None, alias="load_to_zos.data_file_attributes.work2_data_set.secondary_allocation"
    )
    load_to_zos_data_file_attributes_work2_data_set_space_type: DB2FORDATASTAGE.LoadToZosDataFileAttributesWork2DataSetSpaceType | None = Field(
        DB2FORDATASTAGE.LoadToZosDataFileAttributesWork2DataSetSpaceType.cylinders,
        alias="load_to_zos.data_file_attributes.work2_data_set.space_type",
    )
    load_to_zos_data_file_attributes_work2_data_set_storage_class: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work2_data_set.storage_class"
    )
    load_to_zos_data_file_attributes_work2_data_set_unit: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work2_data_set.unit"
    )
    load_to_zos_data_file_attributes_work2_data_set_volumes: str | None = Field(
        None, alias="load_to_zos.data_file_attributes.work2_data_set.volumes"
    )
    load_to_zos_encoding_character_set: str | None = Field(None, alias="load_to_zos.encoding.character_set")
    load_to_zos_files_only: bool | None = Field(False, alias="load_to_zos.files_only")
    load_to_zos_image_copy_function_image_copy_backup_file_data_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_backup_file.data_class"
    )
    load_to_zos_image_copy_function_image_copy_backup_file_dataset_name: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_backup_file.dataset_name"
    )
    load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_abnormal_termination: DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionAbnormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionAbnormalTermination.catalog,
        alias="load_to_zos.image_copy_function.image_copy_backup_file.file_disposition.abnormal_termination",
    )
    load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_normal_termination: DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionNormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionNormalTermination.catalog,
        alias="load_to_zos.image_copy_function.image_copy_backup_file.file_disposition.normal_termination",
    )
    load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_status: DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionStatus | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyBackupFileFileDispositionStatus.replace,
        alias="load_to_zos.image_copy_function.image_copy_backup_file.file_disposition.status",
    )
    load_to_zos_image_copy_function_image_copy_backup_file_management_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_backup_file.management_class"
    )
    load_to_zos_image_copy_function_image_copy_backup_file_number_of_buffers: int | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_backup_file.number_of_buffers"
    )
    load_to_zos_image_copy_function_image_copy_backup_file_primary_allocation: int | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_backup_file.primary_allocation"
    )
    load_to_zos_image_copy_function_image_copy_backup_file_secondary_allocation: int | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_backup_file.secondary_allocation"
    )
    load_to_zos_image_copy_function_image_copy_backup_file_space_type: DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyBackupFileSpaceType | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyBackupFileSpaceType.cylinders,
        alias="load_to_zos.image_copy_function.image_copy_backup_file.space_type",
    )
    load_to_zos_image_copy_function_image_copy_backup_file_storage_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_backup_file.storage_class"
    )
    load_to_zos_image_copy_function_image_copy_backup_file_unit: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_backup_file.unit"
    )
    load_to_zos_image_copy_function_image_copy_backup_file_volumes: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_backup_file.volumes"
    )
    load_to_zos_image_copy_function_image_copy_file_data_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_file.data_class"
    )
    load_to_zos_image_copy_function_image_copy_file_dataset_name: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_file.dataset_name"
    )
    load_to_zos_image_copy_function_image_copy_file_file_disposition_abnormal_termination: DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyFileFileDispositionAbnormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyFileFileDispositionAbnormalTermination.catalog,
        alias="load_to_zos.image_copy_function.image_copy_file.file_disposition.abnormal_termination",
    )
    load_to_zos_image_copy_function_image_copy_file_file_disposition_normal_termination: DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyFileFileDispositionNormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyFileFileDispositionNormalTermination.catalog,
        alias="load_to_zos.image_copy_function.image_copy_file.file_disposition.normal_termination",
    )
    load_to_zos_image_copy_function_image_copy_file_file_disposition_status: DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyFileFileDispositionStatus | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyFileFileDispositionStatus.replace,
        alias="load_to_zos.image_copy_function.image_copy_file.file_disposition.status",
    )
    load_to_zos_image_copy_function_image_copy_file_management_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_file.management_class"
    )
    load_to_zos_image_copy_function_image_copy_file_number_of_buffers: int | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_file.number_of_buffers"
    )
    load_to_zos_image_copy_function_image_copy_file_primary_allocation: int | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_file.primary_allocation"
    )
    load_to_zos_image_copy_function_image_copy_file_secondary_allocation: int | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_file.secondary_allocation"
    )
    load_to_zos_image_copy_function_image_copy_file_space_type: DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyFileSpaceType | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionImageCopyFileSpaceType.cylinders,
        alias="load_to_zos.image_copy_function.image_copy_file.space_type",
    )
    load_to_zos_image_copy_function_image_copy_file_storage_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_file.storage_class"
    )
    load_to_zos_image_copy_function_image_copy_file_unit: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_file.unit"
    )
    load_to_zos_image_copy_function_image_copy_file_volumes: str | None = Field(
        None, alias="load_to_zos.image_copy_function.image_copy_file.volumes"
    )
    load_to_zos_image_copy_function_recovery_backup_data_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_backup.data_class"
    )
    load_to_zos_image_copy_function_recovery_backup_dataset_name: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_backup.dataset_name"
    )
    load_to_zos_image_copy_function_recovery_backup_file_disposition_abnormal_termination: DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryBackupFileDispositionAbnormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryBackupFileDispositionAbnormalTermination.catalog,
        alias="load_to_zos.image_copy_function.recovery_backup.file_disposition.abnormal_termination",
    )
    load_to_zos_image_copy_function_recovery_backup_file_disposition_normal_termination: DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryBackupFileDispositionNormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryBackupFileDispositionNormalTermination.catalog,
        alias="load_to_zos.image_copy_function.recovery_backup.file_disposition.normal_termination",
    )
    load_to_zos_image_copy_function_recovery_backup_file_disposition_status: DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryBackupFileDispositionStatus | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryBackupFileDispositionStatus.replace,
        alias="load_to_zos.image_copy_function.recovery_backup.file_disposition.status",
    )
    load_to_zos_image_copy_function_recovery_backup_management_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_backup.management_class"
    )
    load_to_zos_image_copy_function_recovery_backup_number_of_buffers: int | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_backup.number_of_buffers"
    )
    load_to_zos_image_copy_function_recovery_backup_primary_allocation: int | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_backup.primary_allocation"
    )
    load_to_zos_image_copy_function_recovery_backup_secondary_allocation: int | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_backup.secondary_allocation"
    )
    load_to_zos_image_copy_function_recovery_backup_space_type: DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryBackupSpaceType | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryBackupSpaceType.cylinders,
        alias="load_to_zos.image_copy_function.recovery_backup.space_type",
    )
    load_to_zos_image_copy_function_recovery_backup_storage_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_backup.storage_class"
    )
    load_to_zos_image_copy_function_recovery_backup_unit: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_backup.unit"
    )
    load_to_zos_image_copy_function_recovery_backup_volumes: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_backup.volumes"
    )
    load_to_zos_image_copy_function_recovery_file_data_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_file.data_class"
    )
    load_to_zos_image_copy_function_recovery_file_dataset_name: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_file.dataset_name"
    )
    load_to_zos_image_copy_function_recovery_file_file_disposition_abnormal_termination: DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryFileFileDispositionAbnormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryFileFileDispositionAbnormalTermination.catalog,
        alias="load_to_zos.image_copy_function.recovery_file.file_disposition.abnormal_termination",
    )
    load_to_zos_image_copy_function_recovery_file_file_disposition_normal_termination: DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryFileFileDispositionNormalTermination | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryFileFileDispositionNormalTermination.catalog,
        alias="load_to_zos.image_copy_function.recovery_file.file_disposition.normal_termination",
    )
    load_to_zos_image_copy_function_recovery_file_file_disposition_status: DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryFileFileDispositionStatus | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryFileFileDispositionStatus.replace,
        alias="load_to_zos.image_copy_function.recovery_file.file_disposition.status",
    )
    load_to_zos_image_copy_function_recovery_file_management_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_file.management_class"
    )
    load_to_zos_image_copy_function_recovery_file_number_of_buffers: int | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_file.number_of_buffers"
    )
    load_to_zos_image_copy_function_recovery_file_primary_allocation: int | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_file.primary_allocation"
    )
    load_to_zos_image_copy_function_recovery_file_secondary_allocation: int | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_file.secondary_allocation"
    )
    load_to_zos_image_copy_function_recovery_file_space_type: DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryFileSpaceType | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionRecoveryFileSpaceType.cylinders,
        alias="load_to_zos.image_copy_function.recovery_file.space_type",
    )
    load_to_zos_image_copy_function_recovery_file_storage_class: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_file.storage_class"
    )
    load_to_zos_image_copy_function_recovery_file_unit: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_file.unit"
    )
    load_to_zos_image_copy_function_recovery_file_volumes: str | None = Field(
        None, alias="load_to_zos.image_copy_function.recovery_file.volumes"
    )
    load_to_zos_image_copy_image_copy_backup_file: bool | None = Field(
        False, alias="load_to_zos.image_copy_function.image_copy_backup_file"
    )
    load_to_zos_image_copy_recovery_recovery_backup_file: bool | None = Field(
        False, alias="load_to_zos.image_copy_function.recovery_backup"
    )
    load_to_zos_image_copy_recovery_recovery_file: bool | None = Field(
        False, alias="load_to_zos.image_copy_function.recovery_file"
    )
    load_to_zos_load_method: DB2FORDATASTAGE.LoadToZosLoadMethod | None = Field(
        DB2FORDATASTAGE.LoadToZosLoadMethod.mvs_datasets, alias="load_to_zos.load_method"
    )
    load_to_zos_statistics: DB2FORDATASTAGE.LoadToZosStatistics | None = Field(
        DB2FORDATASTAGE.LoadToZosStatistics.none, alias="load_to_zos.statistics"
    )
    load_to_zos_transfer_password: str | None = Field(None, alias="load_to_zos.transfer.password")
    load_with_logging: bool | None = Field(False, alias="load_to_zos.load_with_logging")
    loaded_data_copy_location: str = Field("", alias="load_control.copy_loaded_data.copy_to_device_or_directory")
    lob_path_list: str | None = Field(None, alias="load_control.lob_path_list")
    lock_wait_mode: DB2FORDATASTAGE.LockWaitMode | None = Field(
        DB2FORDATASTAGE.LockWaitMode.use_the_lock_timeout_database_configuration_parameter, alias="lock_wait_mode"
    )
    lock_wait_time: int = Field(None, alias="lock_wait_mode.lock_wait_mode_time")
    lock_with_force: bool | None = Field(False, alias="load_control.lock_with_force")
    log_column_values_on_first_row_error: bool | None = Field(False, alias="logging.log_column_values")
    log_key_values_only: bool | None = Field(False, alias="logging.log_column_values.log_keys_only")
    lookup_type: DB2FORDATASTAGE.LookupType | None = Field(DB2FORDATASTAGE.LookupType.empty, alias="lookup_type")
    lower_port_number: int = Field(None, alias="load_control.partitioned_db_config.port_range.min_value")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    maximum_partitioning_agents: int | None = Field(
        25, alias="load_control.partitioned_db_config.max_num_part_agents"
    )
    maximum_reject_count: int | None = Field(1, alias="session.use_external_tables.max_errors")
    message_file: str = Field("loadMsgs.out", alias="load_control.message_file")
    migrated_job: bool | None = Field(False, alias="migrated_job")
    name_of_table_space: str | None = Field(None, alias="load_control.allow_access_mode.table_space")
    non_recoverable_load: bool | None = Field(False, alias="load_control.non_recoverable_tx")
    number_of_retries: int = Field(3, alias="load_to_zos.transfer.retry_connection.retry_count")
    omit_header: bool | None = Field(False, alias="load_control.partitioned_db_config.omit_header")
    organize_by: DB2FORDATASTAGE.TableActionGenerateCreateStatementCreateTableOrganizeBy | None = Field(
        DB2FORDATASTAGE.TableActionGenerateCreateStatementCreateTableOrganizeBy.database_default,
        alias="table_action.generate_create_statement.create_table_organize_by",
    )
    other_options: str | None = Field("", alias="table_action.generate_create_statement.create_table_other_options")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(1, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    output_partition_numbers: str | None = Field(
        None, alias="load_control.partitioned_db_config.output_db_part_nums"
    )
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    pad_character: str | None = Field(None, alias="pad_character")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    partition_collecting_statistics: int | None = Field(
        -1, alias="load_control.partitioned_db_config.run_stat_db_partnum"
    )
    partition_number: int | None = Field(None, alias="load_to_zos.partition_number")
    partition_type: DB2FORDATASTAGE.PartitionType | None = Field(
        DB2FORDATASTAGE.PartitionType.auto, alias="part_type"
    )
    partitioned_database_configuration: bool | None = Field(False, alias="load_control.partitioned_db_config")
    partitioned_distribution_file: str | None = Field(None, alias="load_control.partitioned_db_config.dist_file")
    partitioned_reads_column_name: str = Field(None, alias="sql.enable_partitioning.partitioning_method.key_field")
    partitioned_reads_method: DB2FORDATASTAGE.SqlEnablePartitioningPartitioningMethod | None = Field(
        DB2FORDATASTAGE.SqlEnablePartitioningPartitioningMethod.minimum_and_maximum_range,
        alias="sql.enable_partitioning.partitioning_method",
    )
    partitioned_reads_table_name: str = Field(None, alias="sql.enable_partitioning.partitioning_method.table_name")
    partitioning_partition_numbers: str | None = Field(
        None, alias="load_control.partitioned_db_config.partitioning_db_part_nums"
    )
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    perform_table_action_first: bool | None = Field(True, alias="table_action.table_action_first")
    port_range: bool | None = Field(None, alias="load_control.partitioned_db_config.port_range")
    prefix_for_expression_columns: str | None = Field("EXPR", alias="prefix_for_expression_columns")
    preserve_partitioning: DB2FORDATASTAGE.PreservePartitioning | None = Field(
        DB2FORDATASTAGE.PreservePartitioning.default_propagate, alias="preserve"
    )
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    read_after_sql_node_statements_from_file: bool | None = Field(
        False, alias="before_after.after_node.read_from_file_after_sql_node"
    )
    read_after_sql_statements_from_file: bool | None = Field(
        False, alias="before_after.after.read_from_file_after_sql"
    )
    read_before_sql_node_statement_from_file: bool | None = Field(
        False, alias="before_after.before_node.read_from_file_before_sql_node"
    )
    read_before_sql_statements_from_file: bool | None = Field(
        False, alias="before_after.before.read_from_file_before_sql"
    )
    read_create_statement_from_file: bool | None = Field(
        False, alias="table_action.generate_create_statement.read_create_statement_from_file"
    )
    read_drop_statement_from_file: bool | None = Field(
        False, alias="table_action.generate_drop_statement.read_drop_statement_from_file"
    )
    read_select_statement_from_file: bool | None = Field(False, alias="sql.select_statement.read_from_file_select")
    read_truncate_statement_from_file: bool | None = Field(
        False, alias="table_action.generate_truncate_statement.read_truncate_statement_from_file"
    )
    record_count: int | None = Field(2000, alias="transaction.record_count")
    record_ordering: DB2FORDATASTAGE.RecordOrdering | None = Field(
        DB2FORDATASTAGE.RecordOrdering.zero, alias="record_ordering"
    )
    reject_condition_row_not_updated: bool | None = Field(False, alias="reject_condition_row_not_updated")
    reject_condition_sql_error: bool | None = Field(False, alias="reject_condition_sql_error")
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_from_link: int | None = Field(None, alias="reject_from_link")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: DB2FORDATASTAGE.RejectUses | None = Field(DB2FORDATASTAGE.RejectUses.rows, alias="reject_uses")
    remove_intermediate_data_file: bool | None = Field(True, alias="load_control.remove_intermediate_data_file")
    reoptimization: DB2FORDATASTAGE.Reoptimization | None = Field(
        DB2FORDATASTAGE.Reoptimization.none, alias="re_optimization"
    )
    report_only: bool | None = Field(False, alias="load_to_zos.image_copy_function.report_only")
    restart_phase: DB2FORDATASTAGE.LoadControlRestartPhase | None = Field(
        DB2FORDATASTAGE.LoadControlRestartPhase.load, alias="load_control.restart_phase"
    )
    retry_on_connection_failure: bool | None = Field(True, alias="load_to_zos.transfer.retry_connection")
    row_count: int | None = Field(0, alias="load_control.i_row_count")
    row_count_estimate: int | None = Field(1000, alias="load_to_zos.row_count_estimate")
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    save_count: int | None = Field(0, alias="load_control.save_count")
    schema_name: str | None = Field(None, alias="schema_name")
    scope: DB2FORDATASTAGE.LoadToZosImageCopyFunctionScope | None = Field(
        DB2FORDATASTAGE.LoadToZosImageCopyFunctionScope.full, alias="load_to_zos.image_copy_function.scope"
    )
    select_statement: str = Field(None, alias="sql.select_statement")
    select_statement_column: str | None = Field(None, alias="sql.select_statement.columns.column")
    set_copy_pending: bool | None = Field(False, alias="load_to_zos.set_copy_pending")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_buffer_size: int | None = Field(0, alias="load_control.sort_buffer_size")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: DB2FORDATASTAGE.KeyColSelect | None = Field(
        DB2FORDATASTAGE.KeyColSelect.default, alias="keyColSelect"
    )
    sql_delete_statement: str | None = Field(None, alias="sql.delete_statement.tables.table")
    sql_delete_statement_parameters: str | None = Field(None, alias="sql.delete_statement.parameters.parameter")
    sql_delete_statement_where_clause: str | None = Field(None, alias="sql.delete_statement.where_clause")
    sql_insert_statement: str | None = Field(None, alias="sql.insert_statement.tables.table")
    sql_insert_statement_parameters: str | None = Field(None, alias="sql.insert_statement.parameters.parameter")
    sql_insert_statement_where_clause: str | None = Field(None, alias="sql.insert_statement.where_clause")
    sql_other_clause: str | None = Field(None, alias="sql.other_clause")
    sql_select_statement_other_clause: str | None = Field(None, alias="sql.select_statement.other_clause")
    sql_select_statement_parameters: str | None = Field(None, alias="sql.select_statement.parameters.parameter")
    sql_select_statement_table_name: str | None = Field(None, alias="sql.select_statement.tables.table")
    sql_select_statement_where_clause: str | None = Field(None, alias="sql.select_statement.where_clause")
    sql_update_statement: str | None = Field(None, alias="sql.update_statement.tables.table")
    sql_update_statement_parameters: str | None = Field(None, alias="sql.update_statement.parameters.parameter")
    sql_update_statement_where_clause: str | None = Field(None, alias="sql.update_statement.where_clause")
    sql_user_defined_sql_file_character_set: str | None = Field(
        None, alias="sql.user_defined_sql.file.character_set"
    )
    sql_where_clause: str | None = Field(None, alias="sql.where_clause")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    statistics_on_columns: str | None = Field(
        None, alias="session.use_external_tables.statistics.run_stats_on_columns"
    )
    status_interval: int | None = Field(100, alias="load_control.partitioned_db_config.status_interval")
    system_pages: bool | None = Field(True, alias="load_to_zos.image_copy_function.system_pages")
    table_action: DB2FORDATASTAGE.TableAction = Field(DB2FORDATASTAGE.TableAction.append, alias="table_action")
    table_action_generate_create_statement_create_table_in: str | None = Field(
        None, alias="table_action.generate_create_statement.create_table_in"
    )
    table_name: str = Field(None, alias="table_name")
    target_table_on_db2_for_z_os: bool | None = Field(
        False, alias="table_action.generate_create_statement.create_table_on_zos"
    )
    temporary_files_directory: str | None = Field(None, alias="load_control.directory_for_tmp_files")
    temporary_work_table_mode: DB2FORDATASTAGE.SessionTemporaryWorkTable | None = Field(
        DB2FORDATASTAGE.SessionTemporaryWorkTable.automatic, alias="session.temporary_work_table"
    )
    temporary_work_table_name: str = Field(None, alias="session.temporary_work_table.table_name")
    time_commit_interval: int | None = Field(0, alias="transaction.time_interval")
    total_number_of_player_processes: int = Field(None, alias="limit_parallelism.player_process_limit")
    trace: int | None = Field(0, alias="load_control.partitioned_db_config.trace")
    transfer_command: str | None = Field(None, alias="load_to_zos.transfer.transfer_cmd")
    transfer_to: str = Field(None, alias="load_to_zos.transfer.transfer_to")
    transfer_type: DB2FORDATASTAGE.LoadToZosTransferTransferType | None = Field(
        DB2FORDATASTAGE.LoadToZosTransferTransferType.ftp, alias="load_to_zos.transfer.transfer_type"
    )
    truncate_table: bool | None = Field(False, alias="session.temporary_work_table.truncate_table")
    truncate_table_statement: str = Field("", alias="table_action.generate_truncate_statement.truncate_statement")
    type: DB2FORDATASTAGE.TableActionGenerateCreateStatementCreateTableCompressCreateTableCompressLuw | None = Field(
        DB2FORDATASTAGE.TableActionGenerateCreateStatementCreateTableCompressCreateTableCompressLuw.adaptive,
        alias="table_action.generate_create_statement.create_table_compress.create_table_compress_luw",
    )
    unique: bool | None = Field(None, alias="part_unique")
    unique_key_column: str = Field(None, alias="sql.use_unique_key_column.unique_key_column")
    update_columns: str | None = Field(None, alias="sql.update_columns")
    update_statement: str = Field(None, alias="sql.update_statement")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    use_direct_connections: bool | None = Field(False, alias="use_direct_connections")
    use_et_source: bool | None = Field(True, alias="use_et_source")
    use_external_tables: bool | None = Field(False, alias="session.use_external_tables")
    use_unique_key_column: bool | None = Field(False, alias="sql.use_unique_key_column")
    user: str | None = Field(None, alias="load_to_zos.transfer.user")
    user_defined_sql: DB2FORDATASTAGE.SqlUserDefinedSql = Field(
        DB2FORDATASTAGE.SqlUserDefinedSql.statements, alias="sql.user_defined_sql"
    )
    user_defined_sql_file_name: str = Field(None, alias="sql.user_defined_sql.file")
    user_defined_sql_statements: str = Field(None, alias="sql.user_defined_sql.statements")
    user_defined_sql_supress_warnings: bool | None = Field(False, alias="sql.user_defined_sql.suppress_warnings")
    uss_pipe_directory: str = Field(None, alias="load_to_zos.uss_pipe_directory")
    utility_id: str | None = Field("DB2ZLOAD", alias="load_to_zos.utility_id")
    value_compression: bool | None = Field(
        False, alias="table_action.generate_create_statement.create_table_value_compression"
    )
    warning_count: int | None = Field(0, alias="load_control.warning_count")
    without_prompting: bool | None = Field(False, alias="load_control.without_prompting")
    write_mode: DB2FORDATASTAGE.WriteMode = Field(DB2FORDATASTAGE.WriteMode.insert, alias="write_mode")
    xml_column_as_lob: bool | None = Field(False, alias="xml_column_as_lob")

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
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("use_et_source")
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
            else exclude.add("use_et_source")
        )
        (
            include.add("partitioned_reads_table_name")
            if (
                ((self.enable_partitioned_reads))
                and (
                    ((self.partitioned_reads_method == "db2_connector"))
                    or (self.partitioned_reads_method == "minimum_and_maximum_range")
                )
            )
            else exclude.add("partitioned_reads_table_name")
        )
        (
            include.add("sql_select_statement_table_name")
            if (not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_table_name")
        )
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
            include.add("sql_select_statement_parameters")
            if (not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_parameters")
        )
        include.add("limit") if (self.limit_number_of_returned_rows) else exclude.add("limit")
        (
            include.add("pad_character")
            if (


                        self.lookup_type
                        and (
                            (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                            or (self.lookup_type == "pxbridge")
                        )


            )
            else exclude.add("pad_character")
        )
        (
            include.add("read_before_sql_node_statement_from_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("read_before_sql_node_statement_from_file")
        )
        (
            include.add("partitioned_reads_column_name")
            if (
                ((self.enable_partitioned_reads))
                and (
                    ((self.partitioned_reads_method == "minimum_and_maximum_range"))
                    or (self.partitioned_reads_method == "modulus")
                )
            )
            else exclude.add("partitioned_reads_column_name")
        )
        (
            include.add("read_after_sql_node_statements_from_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("read_after_sql_node_statements_from_file")
        )
        (
            include.add("table_name")
            if (((not self.select_statement)) and (self.generate_sql_at_runtime))
            else exclude.add("table_name")
        )
        (
            include.add("directory_for_named_pipe")
            if (self.use_external_tables)
            else exclude.add("directory_for_named_pipe")
        )
        include.add("columns") if (self.enable_lob_references) else exclude.add("columns")
        (
            include.add("enable_before_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("enable_before_sql")
        )
        (
            include.add("sql_select_statement_other_clause")
            if (not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_other_clause")
        )
        (
            include.add("end_of_data")
            if (((self.end_of_wave == "after")) or (self.end_of_wave == "before"))
            else exclude.add("end_of_data")
        )
        (
            include.add("enable_after_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("enable_after_sql")
        )
        (
            include.add("external_tables_other_options")
            if (self.use_external_tables)
            else exclude.add("external_tables_other_options")
        )
        (
            include.add("partitioned_reads_method")
            if (self.enable_partitioned_reads)
            else exclude.add("partitioned_reads_method")
        )
        (
            include.add("sql_select_statement_where_clause")
            if (not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_where_clause")
        )
        (
            include.add("sql_other_clause")
            if (self.generate_sql_at_runtime)
            else exclude.add("sql_other_clause")
        )
        (
            include.add("lock_wait_time")
            if (


                        self.lock_wait_mode
                        and (
                            (hasattr(self.lock_wait_mode, "value") and self.lock_wait_mode.value == "user_specified")
                            or (self.lock_wait_mode == "user_specified")
                        )


            )
            else exclude.add("lock_wait_time")
        )
        (
            include.add("select_statement_column")
            if (not self.generate_sql_at_runtime)
            else exclude.add("select_statement_column")
        )
        (
            include.add("fail_on_error_after_sql_node")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql_node")
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
            include.add("sql_where_clause")
            if (self.generate_sql_at_runtime)
            else exclude.add("sql_where_clause")
        )
        (
            include.add("enable_before_sql_node")
            if (self.enable_before_and_after_sql)
            else exclude.add("enable_before_sql_node")
        )
        (
            include.add("read_select_statement_from_file")
            if (not self.generate_sql_at_runtime)
            else exclude.add("read_select_statement_from_file")
        )
        (
            include.add("select_statement")
            if (((not self.table_name)) and (not self.generate_sql_at_runtime))
            else exclude.add("select_statement")
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
            include.add("read_after_sql_statements_from_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("read_after_sql_statements_from_file")
        )
        (
            include.add("read_before_sql_statements_from_file")
            if (self.enable_before_and_after_sql)
            else exclude.add("read_before_sql_statements_from_file")
        )
        (
            include.add("fail_on_error_before_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql")
        )
        (
            include.add("generate_partitioning_sql")
            if (
                ((not self.generate_sql_at_runtime))
                and (self.enable_partitioned_reads)
                and (self.partitioned_reads_method == "db2_connector")
            )
            else exclude.add("generate_partitioning_sql")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        include.add("use_external_tables") if (self.use_et_source) else exclude.add("use_external_tables")
        (
            include.add("fail_on_error_after_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql")
        )
        (
            include.add("use_et_source")
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
            else exclude.add("use_et_source")
        )
        (
            include.add("partitioned_reads_table_name")
            if (

                    (
                        ((self.enable_partitioned_reads))
                        or ((self.enable_partitioned_reads and "#" in str(self.enable_partitioned_reads)))
                    )
                    and (
                        ((self.partitioned_reads_method == "db2_connector"))
                        or (self.partitioned_reads_method == "minimum_and_maximum_range")
                        or (self.partitioned_reads_method and "#" in str(self.partitioned_reads_method))
                    )

            )
            else exclude.add("partitioned_reads_table_name")
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
            include.add("pad_character")
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
            else exclude.add("pad_character")
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
            include.add("partitioned_reads_column_name")
            if (

                    (
                        ((self.enable_partitioned_reads))
                        or ((self.enable_partitioned_reads and "#" in str(self.enable_partitioned_reads)))
                    )
                    and (
                        ((self.partitioned_reads_method == "minimum_and_maximum_range"))
                        or (self.partitioned_reads_method == "modulus")
                        or (self.partitioned_reads_method and "#" in str(self.partitioned_reads_method))
                    )

            )
            else exclude.add("partitioned_reads_column_name")
        )
        (
            include.add("read_after_sql_node_statements_from_file")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("read_after_sql_node_statements_from_file")
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
            include.add("directory_for_named_pipe")
            if (


                        ((self.use_external_tables))
                        or (self.use_external_tables and "#" in str(self.use_external_tables))


            )
            else exclude.add("directory_for_named_pipe")
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
            include.add("enable_before_sql")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("enable_before_sql")
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
            include.add("end_of_data")
            if (


                        ((self.end_of_wave == "after"))
                        or (self.end_of_wave == "before")
                        or (self.end_of_wave and "#" in str(self.end_of_wave))


            )
            else exclude.add("end_of_data")
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
            include.add("external_tables_other_options")
            if (


                        ((self.use_external_tables))
                        or (self.use_external_tables and "#" in str(self.use_external_tables))


            )
            else exclude.add("external_tables_other_options")
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
            include.add("sql_select_statement_where_clause")
            if (


                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("sql_select_statement_where_clause")
        )
        (
            include.add("sql_other_clause")
            if (


                        ((self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("sql_other_clause")
        )
        (
            include.add("lock_wait_time")
            if (


                        (
                            (
                                self.lock_wait_mode
                                and (
                                    (
                                        hasattr(self.lock_wait_mode, "value")
                                        and self.lock_wait_mode.value == "user_specified"
                                    )
                                    or (self.lock_wait_mode == "user_specified")
                                )
                            )
                        )
                        or (

                                self.lock_wait_mode
                                and (
                                    (
                                        hasattr(self.lock_wait_mode, "value")
                                        and self.lock_wait_mode.value
                                        and "#" in str(self.lock_wait_mode.value)
                                    )
                                    or ("#" in str(self.lock_wait_mode))
                                )

                        )


            )
            else exclude.add("lock_wait_time")
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
            include.add("fail_on_error_after_sql_node")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_after_sql_node")
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
            include.add("sql_where_clause")
            if (


                        ((self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


            )
            else exclude.add("sql_where_clause")
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
            include.add("read_select_statement_from_file")
            if (


                        ((not self.generate_sql_at_runtime))
                        or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))


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
            include.add("read_after_sql_statements_from_file")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("read_after_sql_statements_from_file")
        )
        (
            include.add("read_before_sql_statements_from_file")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("read_before_sql_statements_from_file")
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
            include.add("generate_partitioning_sql")
            if (

                    (
                        ((not self.generate_sql_at_runtime))
                        or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
                    )
                    and (
                        ((self.enable_partitioned_reads))
                        or (self.enable_partitioned_reads and "#" in str(self.enable_partitioned_reads))
                    )
                    and (
                        ((self.partitioned_reads_method == "db2_connector"))
                        or (self.partitioned_reads_method and "#" in str(self.partitioned_reads_method))
                    )

            )
            else exclude.add("generate_partitioning_sql")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
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
        include.add("advanced_connection_settings") if (()) else exclude.add("advanced_connection_settings")
        include.add("defer_credentials") if (()) else exclude.add("defer_credentials")
        include.add("use_cas_lite_service") if (()) else exclude.add("use_cas_lite_service")
        include.add("use_direct_connections") if (()) else exclude.add("use_direct_connections")
        (
            include.add("credentials_input_method_ssl")
            if ((()) and ((()) or (())))
            else exclude.add("credentials_input_method_ssl")
        )
        (
            include.add("fail_on_error_after_sql_node")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql_node")
        )
        (
            include.add("read_before_sql_statements_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_before_sql_statements_from_file")
        )
        (
            include.add("read_select_statement_from_file")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
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
            include.add("generate_partitioning_sql")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            and (self.enable_partitioned_reads == "true" or self.enable_partitioned_reads)
            and (self.partitioned_reads_method == "db2_connector")
            else exclude.add("generate_partitioning_sql")
        )
        (
            include.add("partitioned_reads_column_name")
            if (self.enable_partitioned_reads == "true" or self.enable_partitioned_reads)
            and (
                self.partitioned_reads_method
                and "minimum_and_maximum_range" in str(self.partitioned_reads_method)
                and self.partitioned_reads_method
                and "modulus" in str(self.partitioned_reads_method)
            )
            else exclude.add("partitioned_reads_column_name")
        )
        (
            include.add("pad_character")
            if (
                self.lookup_type
                and (
                    (hasattr(self.lookup_type, "value") and self.lookup_type.value == "pxbridge")
                    or (self.lookup_type == "pxbridge")
                )
            )
            else exclude.add("pad_character")
        )
        (
            include.add("enable_after_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("enable_after_sql")
        )
        (
            include.add("fail_on_error_before_sql_node")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql_node")
        )
        (
            include.add("partitioned_reads_table_name")
            if (self.enable_partitioned_reads == "true" or self.enable_partitioned_reads)
            and (
                self.partitioned_reads_method
                and "db2_connector" in str(self.partitioned_reads_method)
                and self.partitioned_reads_method
                and "minimum_and_maximum_range" in str(self.partitioned_reads_method)
            )
            else exclude.add("partitioned_reads_table_name")
        )
        (
            include.add("select_statement_column")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("select_statement_column")
        )
        (
            include.add("read_after_sql_node_statements_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_after_sql_node_statements_from_file")
        )
        (
            include.add("enable_before_sql_node")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("enable_before_sql_node")
        )
        (
            include.add("enable_after_sql_node")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("enable_after_sql_node")
        )
        (
            include.add("select_statement")
            if (not self.table_name)
            and (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("select_statement")
        )
        (
            include.add("lock_wait_time")
            if (
                self.lock_wait_mode
                and (
                    (hasattr(self.lock_wait_mode, "value") and self.lock_wait_mode.value == "user_specified")
                    or (self.lock_wait_mode == "user_specified")
                )
            )
            else exclude.add("lock_wait_time")
        )
        (
            include.add("fail_on_error_after_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql")
        )
        (
            include.add("use_external_tables")
            if (self.use_et_source == "true" or self.use_et_source)
            else exclude.add("use_external_tables")
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
            include.add("use_et_source")
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
            else exclude.add("use_et_source")
        )
        (
            include.add("sql_other_clause")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
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
            include.add("sql_select_statement_other_clause")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_other_clause")
        )
        (
            include.add("fail_on_error_before_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql")
        )
        (
            include.add("sql_select_statement_where_clause")
            if (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("sql_select_statement_where_clause")
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
            include.add("read_before_sql_node_statement_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_before_sql_node_statement_from_file")
        )
        (
            include.add("lookup_type")
            if (self.has_reference_output == "true" or self.has_reference_output)
            else exclude.add("lookup_type")
        )
        (
            include.add("sql_where_clause")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("sql_where_clause")
        )
        (
            include.add("limit")
            if (self.limit_number_of_returned_rows == "true" or self.limit_number_of_returned_rows)
            else exclude.add("limit")
        )
        (
            include.add("directory_for_named_pipe")
            if (self.use_external_tables == "true" or self.use_external_tables)
            else exclude.add("directory_for_named_pipe")
        )
        (
            include.add("partitioned_reads_method")
            if (self.enable_partitioned_reads == "true" or self.enable_partitioned_reads)
            else exclude.add("partitioned_reads_method")
        )
        (
            include.add("table_name")
            if (not self.select_statement)
            and (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("table_name")
        )
        (
            include.add("read_after_sql_statements_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_after_sql_statements_from_file")
        )
        (
            include.add("columns")
            if (self.enable_lob_references == "true" or self.enable_lob_references)
            else exclude.add("columns")
        )
        (
            include.add("external_tables_other_options")
            if (self.use_external_tables == "true" or self.use_external_tables)
            else exclude.add("external_tables_other_options")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

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
        (
            include.add("load_to_zos_image_copy_function_recovery_file_file_disposition_normal_termination")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_secondary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_secondary_allocation")
        )
        (
            include.add("directory_for_log_files")
            if (self.use_external_tables)
            else exclude.add("directory_for_log_files")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_unit")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_unit")
        )
        (
            include.add("table_name")
            if (
                ((self.generate_sql_at_runtime))
                or (not self.direct_insert)
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
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("load_control_dump_file")
            if (
                ((not self.bulk_load_with_lob_or_xml_columns))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("load_control_dump_file")
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
            include.add("load_to_zos_image_copy_function_recovery_backup_secondary_allocation")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_secondary_allocation")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_dataset_name")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_dataset_name")
        )
        (
            include.add("statistics_on_columns")
            if (((self.use_external_tables)) and (self.external_table_collect_statistics_during_load))
            else exclude.add("statistics_on_columns")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_storage_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_storage_class")
        )
        (
            include.add("load_to_zos_image_copy_recovery_recovery_backup_file")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_recovery_recovery_backup_file")
        )
        include.add("device_type") if (self.bulk_load_to_db2_on_z_os) else exclude.add("device_type")
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_status")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_status")
        )
        (
            include.add("report_only")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (self.image_copy_function == "incremental")
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("report_only")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_secondary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_secondary_allocation")
        )
        (
            include.add("bulk_load_with_lob_or_xml_columns")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("bulk_load_with_lob_or_xml_columns")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_normal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_management_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_management_class")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_dataset_name")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_dataset_name")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_storage_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_storage_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_data_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_data_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_status")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_status")
        )
        (
            include.add("omit_header")
            if (
                ((self.partitioned_database_configuration))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("omit_header")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_management_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_management_class")
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
            )
            else exclude.add("read_truncate_statement_from_file")
        )
        (
            include.add("maximum_reject_count")
            if (self.use_external_tables)
            else exclude.add("maximum_reject_count")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_space_type")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_management_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_management_class")
        )
        (
            include.add("load_control_load_method")
            if (
                ((not self.bulk_load_with_lob_or_xml_columns))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("load_control_load_method")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_normal_termination")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add(
                "load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_normal_termination"
            )
        )
        (
            include.add("update_columns")
            if (
                (
                    ((self.use_external_tables))
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
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )
                            )
                        )
                        or (
                            (
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
                )
                or (
                    ((not self.direct_insert))
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
                    )
                )
            )
            else exclude.add("update_columns")
        )
        (
            include.add("fail_on_error")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
                        )


            )
            else exclude.add("fail_on_error")
        )
        (
            include.add("ccsid")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.encoding == "ccsid"))
            else exclude.add("ccsid")
        )
        (
            include.add("compress")
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
                    (((not self.target_table_on_db2_for_z_os)) and ((self.organize_by == "row")))
                    or (self.target_table_on_db2_for_z_os)
                )
            )
            else exclude.add("compress")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_primary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_data_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_data_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_management_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_management_class")
        )
        (
            include.add("load_control_statistics")
            if (
                ((self.load_mode == "replace"))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("load_control_statistics")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_storage_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_storage_class")
        )
        (
            include.add("generate_create_statement_distribute_by_hash_key_column_names")
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
                and (self.distribute_by == "hash")
                and (not self.target_table_on_db2_for_z_os)
            )
            else exclude.add("generate_create_statement_distribute_by_hash_key_column_names")
        )
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
            )
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("use_external_tables")
            if (
                (
                    ((self.generate_sql_at_runtime))
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
                or (not self.direct_insert)
            )
            else exclude.add("use_external_tables")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_unit")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_unit")
        )
        (
            include.add("port_range")
            if (
                ((self.partitioned_database_configuration))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("port_range")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_dataset_name")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_dataset_name")
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
            )
            else exclude.add("read_create_statement_from_file")
        )
        (
            include.add("sort_buffer_size")
            if (
                (
                    ((self.indexing_mode == "automatic_selection"))
                    or ((self.indexing_mode == "extend_existing_indexes"))
                    or ((self.indexing_mode == "rebuild_table_indexes"))
                )
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("sort_buffer_size")
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
            include.add("total_number_of_player_processes")
            if (self.limit_parallelism)
            else exclude.add("total_number_of_player_processes")
        )
        (
            include.add("lock_with_force")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("lock_with_force")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_storage_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_storage_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_abnormal_termination")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_abnormal_termination")
        )
        (
            include.add("set_copy_pending")
            if (((self.bulk_load_to_db2_on_z_os)) and (not self.load_with_logging))
            else exclude.add("set_copy_pending")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_normal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_number_of_buffers")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_number_of_buffers")
        )
        (
            include.add("table_action_generate_create_statement_create_table_in")
            if (

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
            else exclude.add("table_action_generate_create_statement_create_table_in")
        )
        (
            include.add("change_limit_percent_1")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (self.image_copy_function == "incremental")
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("change_limit_percent_1")
        )
        (
            include.add("temporary_work_table_mode")
            if (not self.direct_insert)
            else exclude.add("temporary_work_table_mode")
        )
        (
            include.add("change_limit_percent_2")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (self.image_copy_function == "incremental")
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("change_limit_percent_2")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_abnormal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_abnormal_termination")
        )
        (
            include.add("buffer_pool")
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
                and (self.target_table_on_db2_for_z_os)
            )
            else exclude.add("buffer_pool")
        )
        (
            include.add("key_columns")
            if (
                (
                    ((self.use_external_tables))
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
                            (
                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
                                )
                            )
                        )
                        or (
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
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )
                            )
                        )
                        or (
                            (
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
                )
                or (
                    ((not self.direct_insert))
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
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
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
            )
            else exclude.add("key_columns")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_status")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_status")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_storage_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_storage_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_management_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_management_class")
        )
        (
            include.add("generate_create_statement_at_runtime")
            if (

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
            else exclude.add("generate_create_statement_at_runtime")
        )
        (
            include.add("organize_by")
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
                and (not self.target_table_on_db2_for_z_os)
            )
            else exclude.add("organize_by")
        )
        (
            include.add("hfs_file_directory")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (((self.transfer_type == "lftp")) or (self.transfer_type == "sftp"))
            )
            else exclude.add("hfs_file_directory")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_secondary_allocation")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_secondary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_normal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_normal_termination")
        )
        (
            include.add("partitioned_distribution_file")
            if (
                ((self.partitioned_database_configuration))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("partitioned_distribution_file")
        )
        (
            include.add("insert_buffering")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                            or (self.write_mode == "insert")
                        )


            )
            else exclude.add("insert_buffering")
        )
        (
            include.add("temporary_files_directory")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("temporary_files_directory")
        )
        (
            include.add("bulk_load_to_db2_on_z_os")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )


            )
            else exclude.add("bulk_load_to_db2_on_z_os")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_normal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_statistics")
            if (self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_statistics")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
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
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_primary_allocation")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_abnormal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_space_type")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_space_type")
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
            include.add("load_to_zos_data_file_attributes_map_data_set_number_of_buffers")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_number_of_buffers")
        )
        (
            include.add("atomic_arrays")
            if (
                (
                    ((self.insert_buffering == "default"))
                    or ((self.insert_buffering == "ignore_duplicates"))
                    or ((self.insert_buffering == "on"))
                )
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                            or (self.write_mode == "insert")
                        )

                )
            )
            else exclude.add("atomic_arrays")
        )
        (
            include.add("output_partition_numbers")
            if (
                ((self.partitioned_database_configuration))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("output_partition_numbers")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_file_disposition_status")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_file_disposition_status")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_secondary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_secondary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_unit")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_unit")
        )
        (
            include.add("user_defined_sql_supress_warnings")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
                        )


            )
            else exclude.add("user_defined_sql_supress_warnings")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_primary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_primary_allocation")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
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
            include.add("other_options")
            if (

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
            else exclude.add("other_options")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_unit")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_unit")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_space_type")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_number_of_buffers")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_number_of_buffers")
        )
        include.add("drop_table") if (not self.direct_insert) else exclude.add("drop_table")
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
            include.add("load_to_zos_data_file_attributes_work2_data_set_management_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_management_class")
        )
        (
            include.add("log_key_values_only")
            if (
                ((self.log_column_values_on_first_row_error))
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )
                )
            )
            else exclude.add("log_key_values_only")
        )
        include.add("utility_id") if (self.bulk_load_to_db2_on_z_os) else exclude.add("utility_id")
        (
            include.add("use_unique_key_column")
            if (

                    ((not self.direct_insert))
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
                    )

            )
            else exclude.add("use_unique_key_column")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_secondary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_secondary_allocation")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
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
            include.add("load_to_zos_data_file_attributes_input_data_files_number_of_buffers")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_number_of_buffers")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_data_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_data_class")
        )
        (
            include.add("allow_access_mode")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("allow_access_mode")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_primary_allocation")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_primary_allocation")
        )
        (
            include.add("status_interval")
            if (
                ((self.partitioned_database_configuration))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("status_interval")
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
            include.add("load_to_zos_image_copy_function_recovery_file_number_of_buffers")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_number_of_buffers")
        )
        (
            include.add("lock_wait_mode")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )

            )
            else exclude.add("lock_wait_mode")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_primary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_storage_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_storage_class")
        )
        (
            include.add("copy_loaded_data")
            if (
                ((not self.non_recoverable_load))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("copy_loaded_data")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_secondary_allocation")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_secondary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_data_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_data_class")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_unit")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_unit")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_management_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_management_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_secondary_allocation")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_secondary_allocation")
        )
        (
            include.add("type")
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
                and (not self.target_table_on_db2_for_z_os)
                and (self.organize_by == "row")
                and (self.compress == "yes")
            )
            else exclude.add("type")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_primary_allocation")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_primary_allocation")
        )
        (
            include.add("concurrent_access_level")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (

                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "append")
                            or (self.table_action == "append")
                        )

                )
            )
            else exclude.add("concurrent_access_level")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_storage_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_storage_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_normal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_normal_termination")
        )
        (
            include.add("maximum_partitioning_agents")
            if (
                ((self.partitioned_database_configuration))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("maximum_partitioning_agents")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_number_of_buffers")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_number_of_buffers")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_space_type")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_space_type")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_status")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_status")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_dataset_name")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_dataset_name")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_primary_allocation")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_primary_allocation")
        )
        (
            include.add("lower_port_number")
            if (
                ((self.partitioned_database_configuration))
                and (self.port_range)
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("lower_port_number")
        )
        (
            include.add("remove_intermediate_data_file")
            if (
                ((not self.load_control_files_only))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("remove_intermediate_data_file")
        )
        include.add("transfer_to") if (self.bulk_load_to_db2_on_z_os) else exclude.add("transfer_to")
        (
            include.add("interval_between_retries")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.retry_on_connection_failure))
            else exclude.add("interval_between_retries")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_number_of_buffers")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_number_of_buffers")
        )
        (
            include.add("trace")
            if (
                ((self.partitioned_database_configuration))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("trace")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_data_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_data_class")
        )
        (
            include.add("data_buffer_size")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("data_buffer_size")
        )
        (
            include.add("number_of_retries")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.retry_on_connection_failure))
            else exclude.add("number_of_retries")
        )
        (
            include.add("load_to_zos_transfer_password")
            if (self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_transfer_password")
        )
        (
            include.add("load_to_zos_image_copy_image_copy_backup_file")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_image_copy_backup_file")
        )
        (
            include.add("direct_insert")
            if (
                (
                    (
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
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
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
            )
            else exclude.add("direct_insert")
        )
        (
            include.add("clean_up_on_failure")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("clean_up_on_failure")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_unit")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_unit")
        )
        (
            include.add("hold_quiesce")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("hold_quiesce")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_unit")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_unit")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_volumes")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_volumes")
        )
        (
            include.add("load_to_zos_image_copy_recovery_recovery_file")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_recovery_recovery_file")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_space_type")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_space_type")
        )
        (
            include.add("system_pages")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (((self.image_copy_function == "full")) or (self.image_copy_function == "incremental"))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("system_pages")
        )
        (
            include.add("unique_key_column")
            if (
                (
                    ((not self.direct_insert))
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
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )
                            )
                        )
                        or (
                            (
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
                )
                and (self.use_unique_key_column)
            )
            else exclude.add("unique_key_column")
        )
        (
            include.add("transfer_command")
            if (self.bulk_load_to_db2_on_z_os)
            else exclude.add("transfer_command")
        )
        (
            include.add("time_commit_interval")
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
            else exclude.add("time_commit_interval")
        )
        (
            include.add("higher_port_number")
            if (
                ((self.partitioned_database_configuration))
                and (self.port_range)
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("higher_port_number")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_abnormal_termination")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add(
                "load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_abnormal_termination"
            )
        )
        (
            include.add("value_compression")
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
                and (not self.target_table_on_db2_for_z_os)
                and (self.organize_by == "row")
            )
            else exclude.add("value_compression")
        )
        (
            include.add("load_to_zos_files_only")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.load_to_zos_load_method == "mvs_datasets"))
            else exclude.add("load_to_zos_files_only")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_data_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_data_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_storage_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_storage_class")
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
            include.add("name_of_table_space")
            if (
                ((self.allow_access_mode == "read"))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("name_of_table_space")
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
            else exclude.add("fail_on_error_drop_statement")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_volumes")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_volumes")
        )
        (
            include.add("graphic_character_set")
            if (self.bulk_load_to_db2_on_z_os)
            else exclude.add("graphic_character_set")
        )
        (
            include.add("message_file")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("message_file")
        )
        (
            include.add("target_table_on_db2_for_z_os")
            if (

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
            else exclude.add("target_table_on_db2_for_z_os")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_dataset_name")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_dataset_name")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_secondary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_secondary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_unit")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_unit")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_management_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_management_class")
        )
        (
            include.add("perform_table_action_first")
            if (

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
            else exclude.add("perform_table_action_first")
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
            )
            else exclude.add("create_table_statement")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_volumes")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_volumes")
        )
        (
            include.add("check_truncation")
            if (
                ((self.partitioned_database_configuration))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("check_truncation")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_dataset_name")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_dataset_name")
        )
        (
            include.add("allow_changes")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("allow_changes")
        )
        (
            include.add("image_copy_function")
            if (self.bulk_load_to_db2_on_z_os)
            else exclude.add("image_copy_function")
        )
        (
            include.add("partitioning_partition_numbers")
            if (
                ((self.partitioned_database_configuration))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("partitioning_partition_numbers")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_number_of_buffers")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_number_of_buffers")
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
            include.add("load_to_zos_data_file_attributes_input_data_files_volumes")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_volumes")
        )
        (
            include.add("warning_count")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("warning_count")
        )
        (
            include.add("load_with_logging")
            if (self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_with_logging")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_volumes")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_status")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_status")
        )
        include.add("dsn_prefix") if (self.bulk_load_to_db2_on_z_os) else exclude.add("dsn_prefix")
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
            include.add("retry_on_connection_failure")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (((self.transfer_type == "ftp")) or (self.transfer_type == "lftp"))
            )
            else exclude.add("retry_on_connection_failure")
        )
        (
            include.add("indexing_mode")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("indexing_mode")
        )
        (
            include.add("scope")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("scope")
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
            else exclude.add("generate_drop_statement_at_runtime")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_storage_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_storage_class")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
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
            include.add("load_to_zos_image_copy_function_recovery_file_storage_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_storage_class")
        )
        (
            include.add("directory_for_named_pipe_unix_only")
            if (
                (
                    (((self.load_control_load_method == "named_pipes")))
                    or (
                        ((not self.bulk_load_with_lob_or_xml_columns))
                        and ((self.load_control_load_method == "named_pipes"))
                    )
                )
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("directory_for_named_pipe_unix_only")
        )
        (
            include.add("load_to_zos_load_method")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_load_method")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_status")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_status")
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
            )
            else exclude.add("drop_table_statement")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_abnormal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_primary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_primary_allocation")
        )
        (
            include.add("partition_number")
            if (self.bulk_load_to_db2_on_z_os)
            else exclude.add("partition_number")
        )
        (
            include.add("distribute_by")
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
                and (not self.target_table_on_db2_for_z_os)
            )
            else exclude.add("distribute_by")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_volumes")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_dataset_name")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_dataset_name")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_management_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_management_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_dataset_name")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_dataset_name")
        )
        (
            include.add("external_table_collect_statistics_during_load")
            if (self.use_external_tables)
            else exclude.add("external_table_collect_statistics_during_load")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_normal_termination")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_normal_termination")
        )
        (
            include.add("load_control_files_only")
            if (
                (
                    (((self.load_control_load_method == "sequential_files")))
                    or (
                        ((not self.bulk_load_with_lob_or_xml_columns))
                        and ((self.load_control_load_method == "sequential_files"))
                    )
                )
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("load_control_files_only")
        )
        include.add("encoding") if (self.bulk_load_to_db2_on_z_os) else exclude.add("encoding")
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_data_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_data_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_primary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_primary_allocation")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_space_type")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_normal_termination")
            if (
                (((self.load_to_zos_load_method == "mvs_datasets")) or ((self.transfer_type == "ftp")))
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_normal_termination")
        )
        (
            include.add("restart_phase")
            if (
                ((self.load_mode == "restart"))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("restart_phase")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_abnormal_termination")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_unit")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_unit")
        )
        (
            include.add("directory_for_data_and_command_files")
            if (
                (
                    (((self.load_control_load_method == "sequential_files")))
                    or (
                        ((not self.bulk_load_with_lob_or_xml_columns))
                        and ((self.load_control_load_method == "sequential_files"))
                    )
                )
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("directory_for_data_and_command_files")
        )
        (
            include.add("batch_pipe_system_id")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.load_to_zos_load_method == "batch_pipes"))
            else exclude.add("batch_pipe_system_id")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_space_type")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_space_type")
        )
        (
            include.add("row_count_estimate")
            if (self.bulk_load_to_db2_on_z_os)
            else exclude.add("row_count_estimate")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_abnormal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("save_count")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("save_count")
        )
        (
            include.add("limit_parallelism")
            if (
                (
                    ((self.use_external_tables))
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
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
                                )
                            )
                        )
                        or (
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
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )
                            )
                        )
                        or (
                            (
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
                )
                or (


                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                or (self.write_mode == "bulk_load")
                            )


                )
            )
            else exclude.add("limit_parallelism")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_space_type")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_space_type")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_volumes")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_volumes")
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
            include.add("load_to_zos_data_file_attributes_input_data_files_primary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_primary_allocation")
        )
        (
            include.add("loaded_data_copy_location")
            if (
                ((self.copy_loaded_data == "use_device_or_directory"))
                and (not self.non_recoverable_load)
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("loaded_data_copy_location")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_status")
            if (
                (((self.load_to_zos_load_method == "mvs_datasets")) or ((self.transfer_type == "ftp")))
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_status")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_volumes")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_dataset_name")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_dataset_name")
        )
        (
            include.add("without_prompting")
            if (
                ((not self.bulk_load_with_lob_or_xml_columns))
                and (self.load_control_load_method == "sequential_files")
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("without_prompting")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_file_disposition_abnormal_termination")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_file_disposition_abnormal_termination")
        )
        (
            include.add("uss_pipe_directory")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.load_to_zos_load_method == "uss_pipes"))
            else exclude.add("uss_pipe_directory")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_status")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_status")
        )
        (
            include.add("fail_on_error_create_statement")
            if (

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
            else exclude.add("fail_on_error_create_statement")
        )
        (
            include.add("sql_user_defined_sql_file_character_set")
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
            else exclude.add("sql_user_defined_sql_file_character_set")
        )
        (
            include.add("file_type")
            if (
                ((not self.bulk_load_with_lob_or_xml_columns))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("file_type")
        )
        (
            include.add("user_defined_sql_file_name")
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
            else exclude.add("user_defined_sql_file_name")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_management_class")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_management_class")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
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
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_number_of_buffers")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_image_copy_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_number_of_buffers")
        )
        (
            include.add("load_timeout")
            if (
                ((not self.bulk_load_with_lob_or_xml_columns))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("load_timeout")
        )
        (
            include.add("load_mode")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "append")
                            or (self.table_action == "append")
                        )

                )
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("load_mode")
        )
        (
            include.add("load_to_zos_encoding_character_set")
            if (self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_encoding_character_set")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_volumes")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_space_type")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_dataset_name")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_dataset_name")
        )
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
            )
            else exclude.add("read_drop_statement_from_file")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_volumes")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_volumes")
        )
        (
            include.add("lob_path_list")
            if (
                ((not self.bulk_load_with_lob_or_xml_columns))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("lob_path_list")
        )
        (
            include.add("exception_table_name")
            if (
                ((not self.bulk_load_with_lob_or_xml_columns))
                and (not self.bulk_load_to_db2_on_z_os)
                and (
                    (
                        (
                            self.table_action
                            and (
                                (hasattr(self.table_action, "value") and self.table_action.value == "append")
                                or (self.table_action == "append")
                            )
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
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("exception_table_name")
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
            else exclude.add("fail_on_error_truncate_statement")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_normal_termination")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
                and (self.load_to_zos_load_method == "mvs_datasets")
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_abnormal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_abnormal_termination")
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
            else exclude.add("generate_truncate_statement_at_runtime")
        )
        include.add("user") if (self.bulk_load_to_db2_on_z_os) else exclude.add("user")
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_secondary_allocation")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_secondary_allocation")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_data_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_data_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_status")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_status")
        )
        (
            include.add("partition_collecting_statistics")
            if (
                ((self.partitioned_database_configuration))
                and (self.load_control_statistics)
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("partition_collecting_statistics")
        )
        include.add("transfer_type") if (self.bulk_load_to_db2_on_z_os) else exclude.add("transfer_type")
        (
            include.add("truncate_table")
            if (((self.temporary_work_table_mode == "existing")) and (not self.direct_insert))
            else exclude.add("truncate_table")
        )
        (
            include.add("disk_parallelism")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("disk_parallelism")
        )
        (
            include.add("row_count")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("row_count")
        )
        (
            include.add("keep_existing_records_in_table_space")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (self.concurrent_access_level == "none")
                and (

                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "append")
                            or (self.table_action == "append")
                        )

                )
            )
            else exclude.add("keep_existing_records_in_table_space")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_space_type")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_abnormal_termination")
            if (
                ((self.load_to_zos_load_method == "mvs_datasets"))
                and (self.transfer_type == "ftp")
                and (self.bulk_load_to_db2_on_z_os)
            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_unit")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_unit")
        )
        (
            include.add("isolate_partition_errors")
            if (
                ((self.partitioned_database_configuration))
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("isolate_partition_errors")
        )
        (
            include.add("temporary_work_table_name")
            if (((self.temporary_work_table_mode == "existing")) and (not self.direct_insert))
            else exclude.add("temporary_work_table_name")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_number_of_buffers")
            if (((self.bulk_load_to_db2_on_z_os)) and (self.transfer_type == "ftp"))
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_number_of_buffers")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_data_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_data_class")
        )
        (
            include.add("library_used_to_copy")
            if (
                ((self.copy_loaded_data == "use_shared_library"))
                and (not self.non_recoverable_load)
                and (not self.bulk_load_to_db2_on_z_os)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("library_used_to_copy")
        )
        (
            include.add("column_delimiter")
            if (
                ((self.log_column_values_on_first_row_error))
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )

                    )

            )
            else exclude.add("log_column_values_on_first_row_error")
        )
        (
            include.add("fail_on_row_error")
            if (
                (
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
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "delete_then_insert")
                                or (self.write_mode == "delete_then_insert")
                            )
                        )
                    )
                    or (
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_then_update")
                                or (self.write_mode == "insert_then_update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                or (self.write_mode == "update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_then_insert")
                                or (self.write_mode == "update_then_insert")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                                or (self.write_mode == "user-defined_sql")
                            )
                        )
                    )
                )
                and (not self.has_reject_output)
            )
            else exclude.add("fail_on_row_error")
        )
        (
            include.add("directory_for_data_files")
            if (self.bulk_load_to_db2_on_z_os)
            else exclude.add("directory_for_data_files")
        )
        (
            include.add("partitioned_database_configuration")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("partitioned_database_configuration")
        )
        (
            include.add("non_recoverable_load")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("non_recoverable_load")
        )
        (
            include.add("index_in")
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
                and (not self.target_table_on_db2_for_z_os)
            )
            else exclude.add("index_in")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_data_class")
            if (
                ((self.bulk_load_to_db2_on_z_os))
                and (
                    ((self.image_copy_function == "concurrent"))
                    or (self.image_copy_function == "full")
                    or (self.image_copy_function == "incremental")
                )
                and (self.load_to_zos_image_copy_recovery_recovery_backup_file)
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_data_class")
        )
        (
            include.add("check_pending_cascade")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("check_pending_cascade")
        )
        (
            include.add("cpu_parallelism")
            if (
                ((not self.bulk_load_to_db2_on_z_os))
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
            )
            else exclude.add("cpu_parallelism")
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
            include.add("load_to_zos_image_copy_function_recovery_file_file_disposition_normal_termination")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_secondary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_secondary_allocation")
        )
        (
            include.add("directory_for_log_files")
            if (


                        ((self.use_external_tables))
                        or (self.use_external_tables and "#" in str(self.use_external_tables))


            )
            else exclude.add("directory_for_log_files")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_unit")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_unit")
        )
        (
            include.add("table_name")
            if (
                ((self.generate_sql_at_runtime))
                or (not self.direct_insert)
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
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
                        )

                )
                or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
                or (self.direct_insert and "#" in str(self.direct_insert))
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
            include.add("load_control_dump_file")
            if (

                    (
                        ((not self.bulk_load_with_lob_or_xml_columns))
                        or (
                            (
                                self.bulk_load_with_lob_or_xml_columns
                                and "#" in str(self.bulk_load_with_lob_or_xml_columns)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("load_control_dump_file")
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
            include.add("load_to_zos_image_copy_function_recovery_backup_secondary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_secondary_allocation")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_dataset_name")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_dataset_name")
        )
        (
            include.add("statistics_on_columns")
            if (

                    (
                        ((self.use_external_tables))
                        or ((self.use_external_tables and "#" in str(self.use_external_tables)))
                    )
                    and (
                        ((self.external_table_collect_statistics_during_load))
                        or (

                                self.external_table_collect_statistics_during_load
                                and "#" in str(self.external_table_collect_statistics_during_load)

                        )
                    )

            )
            else exclude.add("statistics_on_columns")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_storage_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_storage_class")
        )
        (
            include.add("load_to_zos_image_copy_recovery_recovery_backup_file")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_recovery_recovery_backup_file")
        )
        (
            include.add("device_type")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("device_type")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_status")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_status")
        )
        (
            include.add("report_only")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "incremental"))
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("report_only")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_secondary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_secondary_allocation")
        )
        (
            include.add("bulk_load_with_lob_or_xml_columns")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("bulk_load_with_lob_or_xml_columns")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_normal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_management_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_management_class")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_dataset_name")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_dataset_name")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_storage_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_storage_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_data_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_data_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_status")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_status")
        )
        (
            include.add("omit_header")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("omit_header")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_management_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_management_class")
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

            )
            else exclude.add("read_truncate_statement_from_file")
        )
        (
            include.add("maximum_reject_count")
            if (


                        ((self.use_external_tables))
                        or (self.use_external_tables and "#" in str(self.use_external_tables))


            )
            else exclude.add("maximum_reject_count")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_space_type")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_management_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_management_class")
        )
        (
            include.add("load_control_load_method")
            if (

                    (
                        ((not self.bulk_load_with_lob_or_xml_columns))
                        or (
                            (
                                self.bulk_load_with_lob_or_xml_columns
                                and "#" in str(self.bulk_load_with_lob_or_xml_columns)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("load_control_load_method")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_normal_termination")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add(
                "load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_normal_termination"
            )
        )
        (
            include.add("update_columns")
            if (
                (
                    (
                        (
                            ((self.use_external_tables))
                            or ((self.use_external_tables and "#" in str(self.use_external_tables)))
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
                                (
                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                        or (self.write_mode == "update")
                                    )
                                )
                            )
                            or (
                                (
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

                        (((not self.direct_insert)) or ((self.direct_insert and "#" in str(self.direct_insert))))
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
            )
            else exclude.add("update_columns")
        )
        (
            include.add("fail_on_error")
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
            else exclude.add("fail_on_error")
        )
        (
            include.add("ccsid")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.encoding == "ccsid")) or (self.encoding and "#" in str(self.encoding)))

            )
            else exclude.add("ccsid")
        )
        (
            include.add("compress")
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
                                (
                                    ((not self.target_table_on_db2_for_z_os))
                                    or (
                                        (
                                            self.target_table_on_db2_for_z_os
                                            and "#" in str(self.target_table_on_db2_for_z_os)
                                        )
                                    )
                                )
                                and (
                                    ((self.organize_by == "row"))
                                    or ((self.organize_by and "#" in str(self.organize_by)))
                                )
                            )
                        )
                        or (self.target_table_on_db2_for_z_os)
                        or (self.target_table_on_db2_for_z_os and "#" in str(self.target_table_on_db2_for_z_os))
                    )

            )
            else exclude.add("compress")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_primary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_data_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_data_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_management_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_management_class")
        )
        (
            include.add("load_control_statistics")
            if (

                    (((self.load_mode == "replace")) or ((self.load_mode and "#" in str(self.load_mode))))
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("load_control_statistics")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_storage_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_storage_class")
        )
        (
            include.add("generate_create_statement_distribute_by_hash_key_column_names")
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
                    and (((self.distribute_by == "hash")) or (self.distribute_by and "#" in str(self.distribute_by)))
                    and (
                        ((not self.target_table_on_db2_for_z_os))
                        or (self.target_table_on_db2_for_z_os and "#" in str(self.target_table_on_db2_for_z_os))
                    )

            )
            else exclude.add("generate_create_statement_distribute_by_hash_key_column_names")
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

            )
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("use_external_tables")
            if (
                (
                    (
                        (
                            ((self.generate_sql_at_runtime))
                            or ((self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime)))
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
                or (not self.direct_insert)
                or (self.direct_insert and "#" in str(self.direct_insert))
            )
            else exclude.add("use_external_tables")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_unit")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_unit")
        )
        (
            include.add("port_range")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("port_range")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_dataset_name")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_dataset_name")
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

            )
            else exclude.add("read_create_statement_from_file")
        )
        (
            include.add("sort_buffer_size")
            if (

                    (
                        ((self.indexing_mode == "automatic_selection"))
                        or ((self.indexing_mode == "extend_existing_indexes"))
                        or ((self.indexing_mode == "rebuild_table_indexes"))
                        or ((self.indexing_mode and "#" in str(self.indexing_mode)))
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("sort_buffer_size")
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
            include.add("total_number_of_player_processes")
            if (


                        ((self.limit_parallelism))
                        or (self.limit_parallelism and "#" in str(self.limit_parallelism))


            )
            else exclude.add("total_number_of_player_processes")
        )
        (
            include.add("lock_with_force")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("lock_with_force")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_storage_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_storage_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_abnormal_termination")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_abnormal_termination")
        )
        (
            include.add("set_copy_pending")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((not self.load_with_logging))
                        or (self.load_with_logging and "#" in str(self.load_with_logging))
                    )

            )
            else exclude.add("set_copy_pending")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_normal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_number_of_buffers")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_number_of_buffers")
        )
        (
            include.add("table_action_generate_create_statement_create_table_in")
            if (
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
            else exclude.add("table_action_generate_create_statement_create_table_in")
        )
        (
            include.add("change_limit_percent_1")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "incremental"))
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("change_limit_percent_1")
        )
        (
            include.add("temporary_work_table_mode")
            if (((not self.direct_insert)) or (self.direct_insert and "#" in str(self.direct_insert)))
            else exclude.add("temporary_work_table_mode")
        )
        (
            include.add("change_limit_percent_2")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "incremental"))
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("change_limit_percent_2")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_abnormal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_abnormal_termination")
        )
        (
            include.add("buffer_pool")
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
                        ((self.target_table_on_db2_for_z_os))
                        or (self.target_table_on_db2_for_z_os and "#" in str(self.target_table_on_db2_for_z_os))
                    )

            )
            else exclude.add("buffer_pool")
        )
        (
            include.add("key_columns")
            if (
                (
                    (
                        (
                            ((self.use_external_tables))
                            or ((self.use_external_tables and "#" in str(self.use_external_tables)))
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
                                (
                                    self.write_mode
                                    and (
                                        (
                                            hasattr(self.write_mode, "value")
                                            and self.write_mode.value == "insert_new_rows_only"
                                        )
                                        or (self.write_mode == "insert_new_rows_only")
                                    )
                                )
                            )
                            or (
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
                                (
                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                        or (self.write_mode == "update")
                                    )
                                )
                            )
                            or (
                                (
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

                        (((not self.direct_insert)) or ((self.direct_insert and "#" in str(self.direct_insert))))
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
                                            and self.write_mode.value == "insert_new_rows_only"
                                        )
                                        or (self.write_mode == "insert_new_rows_only")
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
            )
            else exclude.add("key_columns")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_status")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_status")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_storage_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_storage_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_management_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_management_class")
        )
        (
            include.add("generate_create_statement_at_runtime")
            if (
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
            else exclude.add("generate_create_statement_at_runtime")
        )
        (
            include.add("organize_by")
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
                        ((not self.target_table_on_db2_for_z_os))
                        or (self.target_table_on_db2_for_z_os and "#" in str(self.target_table_on_db2_for_z_os))
                    )

            )
            else exclude.add("organize_by")
        )
        (
            include.add("hfs_file_directory")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.transfer_type == "lftp"))
                        or (self.transfer_type == "sftp")
                        or (self.transfer_type and "#" in str(self.transfer_type))
                    )

            )
            else exclude.add("hfs_file_directory")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_secondary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_secondary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_normal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_normal_termination")
        )
        (
            include.add("partitioned_distribution_file")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("partitioned_distribution_file")
        )
        (
            include.add("insert_buffering")
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
            else exclude.add("insert_buffering")
        )
        (
            include.add("temporary_files_directory")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("temporary_files_directory")
        )
        (
            include.add("bulk_load_to_db2_on_z_os")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                            or (self.write_mode == "bulk_load")
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
            else exclude.add("bulk_load_to_db2_on_z_os")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_normal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_statistics")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("load_to_zos_statistics")
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
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                            or (self.write_mode == "insert_new_rows_only")
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
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_primary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_abnormal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_space_type")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_space_type")
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
            include.add("load_to_zos_data_file_attributes_map_data_set_number_of_buffers")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_number_of_buffers")
        )
        (
            include.add("atomic_arrays")
            if (

                    (
                        ((self.insert_buffering == "default"))
                        or ((self.insert_buffering == "ignore_duplicates"))
                        or ((self.insert_buffering == "on"))
                        or ((self.insert_buffering and "#" in str(self.insert_buffering)))
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
            else exclude.add("atomic_arrays")
        )
        (
            include.add("output_partition_numbers")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("output_partition_numbers")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_file_disposition_status")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_file_disposition_status")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_secondary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_secondary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_unit")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_unit")
        )
        (
            include.add("user_defined_sql_supress_warnings")
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
            else exclude.add("user_defined_sql_supress_warnings")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_primary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_primary_allocation")
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
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
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
            include.add("other_options")
            if (
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
            else exclude.add("other_options")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_unit")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_unit")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_space_type")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_number_of_buffers")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_number_of_buffers")
        )
        (
            include.add("drop_table")
            if (((not self.direct_insert)) or (self.direct_insert and "#" in str(self.direct_insert)))
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
            include.add("load_to_zos_data_file_attributes_work2_data_set_management_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_management_class")
        )
        (
            include.add("log_key_values_only")
            if (

                    (
                        ((self.log_column_values_on_first_row_error))
                        or (
                            (
                                self.log_column_values_on_first_row_error
                                and "#" in str(self.log_column_values_on_first_row_error)
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
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
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
            else exclude.add("log_key_values_only")
        )
        (
            include.add("utility_id")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("utility_id")
        )
        (
            include.add("use_unique_key_column")
            if (

                    (((not self.direct_insert)) or ((self.direct_insert and "#" in str(self.direct_insert))))
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
            else exclude.add("use_unique_key_column")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_secondary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_secondary_allocation")
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
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
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
            include.add("load_to_zos_data_file_attributes_input_data_files_number_of_buffers")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_number_of_buffers")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_data_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_data_class")
        )
        (
            include.add("allow_access_mode")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("allow_access_mode")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_primary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_primary_allocation")
        )
        (
            include.add("status_interval")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("status_interval")
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
            include.add("load_to_zos_image_copy_function_recovery_file_number_of_buffers")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_number_of_buffers")
        )
        (
            include.add("lock_wait_mode")
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
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                            or (self.write_mode == "insert_new_rows_only")
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
            else exclude.add("lock_wait_mode")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_primary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_storage_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_storage_class")
        )
        (
            include.add("copy_loaded_data")
            if (

                    (
                        ((not self.non_recoverable_load))
                        or ((self.non_recoverable_load and "#" in str(self.non_recoverable_load)))
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("copy_loaded_data")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_secondary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_secondary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_data_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_data_class")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_unit")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_unit")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_management_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_management_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_secondary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_secondary_allocation")
        )
        (
            include.add("type")
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
                        ((not self.target_table_on_db2_for_z_os))
                        or (self.target_table_on_db2_for_z_os and "#" in str(self.target_table_on_db2_for_z_os))
                    )
                    and (((self.organize_by == "row")) or (self.organize_by and "#" in str(self.organize_by)))
                    and (((self.compress == "yes")) or (self.compress and "#" in str(self.compress)))

            )
            else exclude.add("type")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_primary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_primary_allocation")
        )
        (
            include.add("concurrent_access_level")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "append")
                                    or (self.table_action == "append")
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
            else exclude.add("concurrent_access_level")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_storage_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_storage_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_normal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_normal_termination")
        )
        (
            include.add("maximum_partitioning_agents")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("maximum_partitioning_agents")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_number_of_buffers")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_number_of_buffers")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_space_type")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_space_type")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_status")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_status")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_dataset_name")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_dataset_name")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_primary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_primary_allocation")
        )
        (
            include.add("lower_port_number")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (((self.port_range)) or (self.port_range and "#" in str(self.port_range)))
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("lower_port_number")
        )
        (
            include.add("remove_intermediate_data_file")
            if (

                    (
                        ((not self.load_control_files_only))
                        or ((self.load_control_files_only and "#" in str(self.load_control_files_only)))
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("remove_intermediate_data_file")
        )
        (
            include.add("transfer_to")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("transfer_to")
        )
        (
            include.add("interval_between_retries")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.retry_on_connection_failure))
                        or (self.retry_on_connection_failure and "#" in str(self.retry_on_connection_failure))
                    )

            )
            else exclude.add("interval_between_retries")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_number_of_buffers")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_number_of_buffers")
        )
        (
            include.add("trace")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("trace")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_data_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_data_class")
        )
        (
            include.add("data_buffer_size")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("data_buffer_size")
        )
        (
            include.add("number_of_retries")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.retry_on_connection_failure))
                        or (self.retry_on_connection_failure and "#" in str(self.retry_on_connection_failure))
                    )

            )
            else exclude.add("number_of_retries")
        )
        (
            include.add("load_to_zos_transfer_password")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("load_to_zos_transfer_password")
        )
        (
            include.add("load_to_zos_image_copy_image_copy_backup_file")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_image_copy_backup_file")
        )
        (
            include.add("direct_insert")
            if (
                (
                    (
                        (
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
                                            and self.write_mode.value == "insert_new_rows_only"
                                        )
                                        or (self.write_mode == "insert_new_rows_only")
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
            )
            else exclude.add("direct_insert")
        )
        (
            include.add("clean_up_on_failure")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("clean_up_on_failure")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_unit")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_unit")
        )
        (
            include.add("hold_quiesce")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("hold_quiesce")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_unit")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_unit")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_volumes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_volumes")
        )
        (
            include.add("load_to_zos_image_copy_recovery_recovery_file")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_recovery_recovery_file")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_space_type")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_space_type")
        )
        (
            include.add("system_pages")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "full"))
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("system_pages")
        )
        (
            include.add("unique_key_column")
            if (

                    (
                        (
                            (
                                ((not self.direct_insert))
                                or ((self.direct_insert and "#" in str(self.direct_insert)))
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
                                    (
                                        self.write_mode
                                        and (
                                            (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                            or (self.write_mode == "update")
                                        )
                                    )
                                )
                                or (
                                    (
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
                    and (
                        ((self.use_unique_key_column))
                        or (self.use_unique_key_column and "#" in str(self.use_unique_key_column))
                    )

            )
            else exclude.add("unique_key_column")
        )
        (
            include.add("transfer_command")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("transfer_command")
        )
        (
            include.add("time_commit_interval")
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
                            (
                                hasattr(self.write_mode, "value")
                                and self.write_mode.value
                                and "#" in str(self.write_mode.value)
                            )
                            or ("#" in str(self.write_mode))
                        )

                )
            )
            else exclude.add("time_commit_interval")
        )
        (
            include.add("higher_port_number")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (((self.port_range)) or (self.port_range and "#" in str(self.port_range)))
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("higher_port_number")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_abnormal_termination")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add(
                "load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_abnormal_termination"
            )
        )
        (
            include.add("value_compression")
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
                        ((not self.target_table_on_db2_for_z_os))
                        or (self.target_table_on_db2_for_z_os and "#" in str(self.target_table_on_db2_for_z_os))
                    )
                    and (((self.organize_by == "row")) or (self.organize_by and "#" in str(self.organize_by)))

            )
            else exclude.add("value_compression")
        )
        (
            include.add("load_to_zos_files_only")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_files_only")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_data_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_data_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_storage_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_storage_class")
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
            include.add("name_of_table_space")
            if (

                    (
                        ((self.allow_access_mode == "read"))
                        or ((self.allow_access_mode and "#" in str(self.allow_access_mode)))
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("name_of_table_space")
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
            else exclude.add("fail_on_error_drop_statement")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_volumes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_volumes")
        )
        (
            include.add("graphic_character_set")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("graphic_character_set")
        )
        (
            include.add("message_file")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("message_file")
        )
        (
            include.add("target_table_on_db2_for_z_os")
            if (
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
            else exclude.add("target_table_on_db2_for_z_os")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_dataset_name")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_dataset_name")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_secondary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_secondary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_unit")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_unit")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_management_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_management_class")
        )
        (
            include.add("perform_table_action_first")
            if (
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
            else exclude.add("perform_table_action_first")
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

            )
            else exclude.add("create_table_statement")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_volumes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_volumes")
        )
        (
            include.add("check_truncation")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("check_truncation")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_dataset_name")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_dataset_name")
        )
        (
            include.add("allow_changes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("allow_changes")
        )
        (
            include.add("image_copy_function")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("image_copy_function")
        )
        (
            include.add("partitioning_partition_numbers")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("partitioning_partition_numbers")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_number_of_buffers")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_number_of_buffers")
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
            include.add("load_to_zos_data_file_attributes_input_data_files_volumes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_volumes")
        )
        (
            include.add("warning_count")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("warning_count")
        )
        (
            include.add("load_with_logging")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("load_with_logging")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_volumes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_status")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_status")
        )
        (
            include.add("dsn_prefix")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("dsn_prefix")
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
            include.add("retry_on_connection_failure")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.transfer_type == "ftp"))
                        or (self.transfer_type == "lftp")
                        or (self.transfer_type and "#" in str(self.transfer_type))
                    )

            )
            else exclude.add("retry_on_connection_failure")
        )
        (
            include.add("indexing_mode")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("indexing_mode")
        )
        (
            include.add("scope")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("scope")
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
            else exclude.add("generate_drop_statement_at_runtime")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_storage_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_storage_class")
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
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
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
            include.add("load_to_zos_image_copy_function_recovery_file_storage_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_storage_class")
        )
        (
            include.add("directory_for_named_pipe_unix_only")
            if (

                    (
                        (
                            (
                                (
                                    ((self.load_control_load_method == "named_pipes"))
                                    or ((self.load_control_load_method and "#" in str(self.load_control_load_method)))
                                )
                            )
                        )
                        or (
                            (
                                (
                                    ((not self.bulk_load_with_lob_or_xml_columns))
                                    or (
                                        (
                                            self.bulk_load_with_lob_or_xml_columns
                                            and "#" in str(self.bulk_load_with_lob_or_xml_columns)
                                        )
                                    )
                                )
                                and (
                                    ((self.load_control_load_method == "named_pipes"))
                                    or ((self.load_control_load_method and "#" in str(self.load_control_load_method)))
                                )
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("directory_for_named_pipe_unix_only")
        )
        (
            include.add("load_to_zos_load_method")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_load_method")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_status")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_status")
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

            )
            else exclude.add("drop_table_statement")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_abnormal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_primary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_primary_allocation")
        )
        (
            include.add("partition_number")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("partition_number")
        )
        (
            include.add("distribute_by")
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
                        ((not self.target_table_on_db2_for_z_os))
                        or (self.target_table_on_db2_for_z_os and "#" in str(self.target_table_on_db2_for_z_os))
                    )

            )
            else exclude.add("distribute_by")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_volumes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_dataset_name")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_dataset_name")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_management_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_management_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_dataset_name")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_dataset_name")
        )
        (
            include.add("external_table_collect_statistics_during_load")
            if (


                        ((self.use_external_tables))
                        or (self.use_external_tables and "#" in str(self.use_external_tables))


            )
            else exclude.add("external_table_collect_statistics_during_load")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_normal_termination")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_normal_termination")
        )
        (
            include.add("load_control_files_only")
            if (

                    (
                        (
                            (
                                (
                                    ((self.load_control_load_method == "sequential_files"))
                                    or ((self.load_control_load_method and "#" in str(self.load_control_load_method)))
                                )
                            )
                        )
                        or (
                            (
                                (
                                    ((not self.bulk_load_with_lob_or_xml_columns))
                                    or (
                                        (
                                            self.bulk_load_with_lob_or_xml_columns
                                            and "#" in str(self.bulk_load_with_lob_or_xml_columns)
                                        )
                                    )
                                )
                                and (
                                    ((self.load_control_load_method == "sequential_files"))
                                    or ((self.load_control_load_method and "#" in str(self.load_control_load_method)))
                                )
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("load_control_files_only")
        )
        (
            include.add("encoding")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("encoding")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_data_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_data_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_primary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_primary_allocation")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_space_type")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_normal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.transfer_type == "ftp"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                        or ((self.transfer_type and "#" in str(self.transfer_type)))
                    )
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_normal_termination")
        )
        (
            include.add("restart_phase")
            if (

                    (((self.load_mode == "restart")) or ((self.load_mode and "#" in str(self.load_mode))))
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("restart_phase")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_abnormal_termination")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_unit")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_unit")
        )
        (
            include.add("directory_for_data_and_command_files")
            if (

                    (
                        (
                            (
                                (
                                    ((self.load_control_load_method == "sequential_files"))
                                    or ((self.load_control_load_method and "#" in str(self.load_control_load_method)))
                                )
                            )
                        )
                        or (
                            (
                                (
                                    ((not self.bulk_load_with_lob_or_xml_columns))
                                    or (
                                        (
                                            self.bulk_load_with_lob_or_xml_columns
                                            and "#" in str(self.bulk_load_with_lob_or_xml_columns)
                                        )
                                    )
                                )
                                and (
                                    ((self.load_control_load_method == "sequential_files"))
                                    or ((self.load_control_load_method and "#" in str(self.load_control_load_method)))
                                )
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("directory_for_data_and_command_files")
        )
        (
            include.add("batch_pipe_system_id")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.load_to_zos_load_method == "batch_pipes"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("batch_pipe_system_id")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_space_type")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_space_type")
        )
        (
            include.add("row_count_estimate")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("row_count_estimate")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_abnormal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("save_count")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("save_count")
        )
        (
            include.add("limit_parallelism")
            if (
                (
                    (
                        (
                            ((self.use_external_tables))
                            or ((self.use_external_tables and "#" in str(self.use_external_tables)))
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
                                            and self.write_mode.value == "insert_new_rows_only"
                                        )
                                        or (self.write_mode == "insert_new_rows_only")
                                    )
                                )
                            )
                            or (
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
                                (
                                    self.write_mode
                                    and (
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                        or (self.write_mode == "update")
                                    )
                                )
                            )
                            or (
                                (
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
                                        (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                        or (self.write_mode == "bulk_load")
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
            else exclude.add("limit_parallelism")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_space_type")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_space_type")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_volumes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_volumes")
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
            include.add("load_to_zos_data_file_attributes_input_data_files_primary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_primary_allocation")
        )
        (
            include.add("loaded_data_copy_location")
            if (

                    (
                        ((self.copy_loaded_data == "use_device_or_directory"))
                        or ((self.copy_loaded_data and "#" in str(self.copy_loaded_data)))
                    )
                    and (
                        ((not self.non_recoverable_load))
                        or (self.non_recoverable_load and "#" in str(self.non_recoverable_load))
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("loaded_data_copy_location")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_status")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.transfer_type == "ftp"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                        or ((self.transfer_type and "#" in str(self.transfer_type)))
                    )
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_status")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_volumes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_dataset_name")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_dataset_name")
        )
        (
            include.add("without_prompting")
            if (

                    (
                        ((not self.bulk_load_with_lob_or_xml_columns))
                        or (
                            (
                                self.bulk_load_with_lob_or_xml_columns
                                and "#" in str(self.bulk_load_with_lob_or_xml_columns)
                            )
                        )
                    )
                    and (
                        ((self.load_control_load_method == "sequential_files"))
                        or (self.load_control_load_method and "#" in str(self.load_control_load_method))
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("without_prompting")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_file_disposition_abnormal_termination")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_file_disposition_abnormal_termination")
        )
        (
            include.add("uss_pipe_directory")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.load_to_zos_load_method == "uss_pipes"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("uss_pipe_directory")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_status")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_status")
        )
        (
            include.add("fail_on_error_create_statement")
            if (
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
            else exclude.add("fail_on_error_create_statement")
        )
        (
            include.add("sql_user_defined_sql_file_character_set")
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
            else exclude.add("sql_user_defined_sql_file_character_set")
        )
        (
            include.add("file_type")
            if (

                    (
                        ((not self.bulk_load_with_lob_or_xml_columns))
                        or (
                            (
                                self.bulk_load_with_lob_or_xml_columns
                                and "#" in str(self.bulk_load_with_lob_or_xml_columns)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("file_type")
        )
        (
            include.add("user_defined_sql_file_name")
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
            else exclude.add("user_defined_sql_file_name")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_management_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_management_class")
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
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
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
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_number_of_buffers")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_image_copy_backup_file))
                        or (

                                self.load_to_zos_image_copy_image_copy_backup_file
                                and "#" in str(self.load_to_zos_image_copy_image_copy_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_number_of_buffers")
        )
        (
            include.add("load_timeout")
            if (

                    (
                        ((not self.bulk_load_with_lob_or_xml_columns))
                        or (
                            (
                                self.bulk_load_with_lob_or_xml_columns
                                and "#" in str(self.bulk_load_with_lob_or_xml_columns)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("load_timeout")
        )
        (
            include.add("load_mode")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "append")
                                    or (self.table_action == "append")
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
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("load_mode")
        )
        (
            include.add("load_to_zos_encoding_character_set")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("load_to_zos_encoding_character_set")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_volumes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_space_type")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_dataset_name")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_dataset_name")
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

            )
            else exclude.add("read_drop_statement_from_file")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_volumes")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_volumes")
        )
        (
            include.add("lob_path_list")
            if (

                    (
                        ((not self.bulk_load_with_lob_or_xml_columns))
                        or (
                            (
                                self.bulk_load_with_lob_or_xml_columns
                                and "#" in str(self.bulk_load_with_lob_or_xml_columns)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("lob_path_list")
        )
        (
            include.add("exception_table_name")
            if (

                    (
                        ((not self.bulk_load_with_lob_or_xml_columns))
                        or (
                            (
                                self.bulk_load_with_lob_or_xml_columns
                                and "#" in str(self.bulk_load_with_lob_or_xml_columns)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "append")
                                    or (self.table_action == "append")
                                )
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
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("exception_table_name")
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
            else exclude.add("fail_on_error_truncate_statement")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_normal_termination")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )
                    and (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or (self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_abnormal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_abnormal_termination")
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
            else exclude.add("generate_truncate_statement_at_runtime")
        )
        (
            include.add("user")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("user")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_secondary_allocation")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_secondary_allocation")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_data_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_data_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_status")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_status")
        )
        (
            include.add("partition_collecting_statistics")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((self.load_control_statistics))
                        or (self.load_control_statistics and "#" in str(self.load_control_statistics))
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("partition_collecting_statistics")
        )
        (
            include.add("transfer_type")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("transfer_type")
        )
        (
            include.add("truncate_table")
            if (

                    (
                        ((self.temporary_work_table_mode == "existing"))
                        or ((self.temporary_work_table_mode and "#" in str(self.temporary_work_table_mode)))
                    )
                    and (((not self.direct_insert)) or (self.direct_insert and "#" in str(self.direct_insert)))

            )
            else exclude.add("truncate_table")
        )
        (
            include.add("disk_parallelism")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("disk_parallelism")
        )
        (
            include.add("row_count")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("row_count")
        )
        (
            include.add("keep_existing_records_in_table_space")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.concurrent_access_level == "none"))
                        or (self.concurrent_access_level and "#" in str(self.concurrent_access_level))
                    )
                    and (
                        (
                            (
                                self.table_action
                                and (
                                    (hasattr(self.table_action, "value") and self.table_action.value == "append")
                                    or (self.table_action == "append")
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
            else exclude.add("keep_existing_records_in_table_space")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_space_type")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_abnormal_termination")
            if (

                    (
                        ((self.load_to_zos_load_method == "mvs_datasets"))
                        or ((self.load_to_zos_load_method and "#" in str(self.load_to_zos_load_method)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))
                    and (
                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )

            )
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_unit")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_unit")
        )
        (
            include.add("isolate_partition_errors")
            if (

                    (
                        ((self.partitioned_database_configuration))
                        or (
                            (
                                self.partitioned_database_configuration
                                and "#" in str(self.partitioned_database_configuration)
                            )
                        )
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("isolate_partition_errors")
        )
        (
            include.add("temporary_work_table_name")
            if (

                    (
                        ((self.temporary_work_table_mode == "existing"))
                        or ((self.temporary_work_table_mode and "#" in str(self.temporary_work_table_mode)))
                    )
                    and (((not self.direct_insert)) or (self.direct_insert and "#" in str(self.direct_insert)))

            )
            else exclude.add("temporary_work_table_name")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_number_of_buffers")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (((self.transfer_type == "ftp")) or (self.transfer_type and "#" in str(self.transfer_type)))

            )
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_number_of_buffers")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_data_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_data_class")
        )
        (
            include.add("library_used_to_copy")
            if (

                    (
                        ((self.copy_loaded_data == "use_shared_library"))
                        or ((self.copy_loaded_data and "#" in str(self.copy_loaded_data)))
                    )
                    and (
                        ((not self.non_recoverable_load))
                        or (self.non_recoverable_load and "#" in str(self.non_recoverable_load))
                    )
                    and (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("library_used_to_copy")
        )
        (
            include.add("column_delimiter")
            if (

                    (
                        ((self.log_column_values_on_first_row_error))
                        or (
                            (
                                self.log_column_values_on_first_row_error
                                and "#" in str(self.log_column_values_on_first_row_error)
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
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
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
            else exclude.add("column_delimiter")
        )
        (
            include.add("log_column_values_on_first_row_error")
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
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                            or (self.write_mode == "insert_new_rows_only")
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
            else exclude.add("log_column_values_on_first_row_error")
        )
        (
            include.add("fail_on_row_error")
            if (

                    (
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
                                        and self.write_mode.value == "insert_new_rows_only"
                                    )
                                    or (self.write_mode == "insert_new_rows_only")
                                )
                            )
                        )
                        or (
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
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )
                            )
                        )
                        or (
                            (
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
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
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
                    and (not self.has_reject_output)

            )
            else exclude.add("fail_on_row_error")
        )
        (
            include.add("directory_for_data_files")
            if (


                        ((self.bulk_load_to_db2_on_z_os))
                        or (self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os))


            )
            else exclude.add("directory_for_data_files")
        )
        (
            include.add("partitioned_database_configuration")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("partitioned_database_configuration")
        )
        (
            include.add("non_recoverable_load")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("non_recoverable_load")
        )
        (
            include.add("index_in")
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
                        ((not self.target_table_on_db2_for_z_os))
                        or (self.target_table_on_db2_for_z_os and "#" in str(self.target_table_on_db2_for_z_os))
                    )

            )
            else exclude.add("index_in")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_data_class")
            if (

                    (
                        ((self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        ((self.image_copy_function == "concurrent"))
                        or (self.image_copy_function == "full")
                        or (self.image_copy_function == "incremental")
                        or (self.image_copy_function and "#" in str(self.image_copy_function))
                    )
                    and (
                        ((self.load_to_zos_image_copy_recovery_recovery_backup_file))
                        or (

                                self.load_to_zos_image_copy_recovery_recovery_backup_file
                                and "#" in str(self.load_to_zos_image_copy_recovery_recovery_backup_file)

                        )
                    )

            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_data_class")
        )
        (
            include.add("check_pending_cascade")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("check_pending_cascade")
        )
        (
            include.add("cpu_parallelism")
            if (

                    (
                        ((not self.bulk_load_to_db2_on_z_os))
                        or ((self.bulk_load_to_db2_on_z_os and "#" in str(self.bulk_load_to_db2_on_z_os)))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                                    or (self.write_mode == "bulk_load")
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
            else exclude.add("cpu_parallelism")
        )
        (
            include.add("load_to_zos_load_method")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_load_method")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_data_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_data_class")
        )
        (
            include.add("load_control_load_method")
            if (self.bulk_load_with_lob_or_xml_columns == "false" or not self.bulk_load_with_lob_or_xml_columns)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("load_control_load_method")
        )
        (
            include.add("partitioned_distribution_file")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("partitioned_distribution_file")
        )
        (
            include.add("compress")
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
                (
                    (self.target_table_on_db2_for_z_os == "false" or not self.target_table_on_db2_for_z_os)
                    and (self.organize_by == "row")
                )
                or (self.target_table_on_db2_for_z_os == "true" or self.target_table_on_db2_for_z_os)
            )
            else exclude.add("compress")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_abnormal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_abnormal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("directory_for_named_pipe_unix_only")
            if (
                ((self.load_control_load_method == "named_pipes"))
                or (
                    (
                        self.bulk_load_with_lob_or_xml_columns == "false"
                        or not self.bulk_load_with_lob_or_xml_columns
                    )
                    and (self.load_control_load_method == "named_pipes")
                )
            )
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("directory_for_named_pipe_unix_only")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_data_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_data_class")
        )
        (
            include.add("dsn_prefix")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("dsn_prefix")
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
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
            include.add("load_to_zos_image_copy_function_image_copy_file_number_of_buffers")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_number_of_buffers")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_abnormal_termination")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add(
                "load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_abnormal_termination"
            )
        )
        (
            include.add("allow_access_mode")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("allow_access_mode")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_management_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_management_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_unit")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_unit")
        )
        (
            include.add("ccsid")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.encoding == "ccsid")
            else exclude.add("ccsid")
        )
        (
            include.add("exception_table_name")
            if (self.bulk_load_with_lob_or_xml_columns == "false" or not self.bulk_load_with_lob_or_xml_columns)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "append" in str(self.table_action.value)
                    )
                    or ("append" in str(self.table_action))
                )
                and self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "truncate" in str(self.table_action.value)
                    )
                    or ("truncate" in str(self.table_action))
                )
            )
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("exception_table_name")
        )
        (
            include.add("load_timeout")
            if (self.bulk_load_with_lob_or_xml_columns == "false" or not self.bulk_load_with_lob_or_xml_columns)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("load_timeout")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_dataset_name")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_dataset_name")
        )
        (
            include.add("direct_insert")
            if (

                    self.write_mode
                    and (
                        (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                        or (self.write_mode == "user-defined_sql")
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
                            and "insert_new_rows_only" in str(self.write_mode.value)
                        )
                        or ("insert_new_rows_only" in str(self.write_mode))
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
            else exclude.add("direct_insert")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_unit")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_unit")
        )
        (
            include.add("limit_parallelism")
            if (
                (self.use_external_tables == "true" or self.use_external_tables)
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
                            and "insert_new_rows_only" in str(self.write_mode.value)
                        )
                        or ("insert_new_rows_only" in str(self.write_mode))
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

                    self.write_mode
                    and (
                        (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                        or (self.write_mode == "bulk_load")
                    )

            )
            else exclude.add("limit_parallelism")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_volumes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_volumes")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_unit")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_unit")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_normal_termination")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_normal_termination")
        )
        (
            include.add("type")
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
            and (self.target_table_on_db2_for_z_os == "false" or not self.target_table_on_db2_for_z_os)
            and (self.organize_by == "row")
            and (self.compress == "yes")
            else exclude.add("type")
        )
        (
            include.add("hold_quiesce")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("hold_quiesce")
        )
        (
            include.add("lower_port_number")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.port_range == "true" or self.port_range)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("lower_port_number")
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
            include.add("load_to_zos_data_file_attributes_discard_data_set_dataset_name")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_dataset_name")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_unit")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_unit")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_number_of_buffers")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_number_of_buffers")
        )
        (
            include.add("other_options")
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
                or self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            else exclude.add("other_options")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_storage_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_storage_class")
        )
        (
            include.add("load_to_zos_transfer_password")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_transfer_password")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_volumes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_volumes")
        )
        (
            include.add("number_of_retries")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.retry_on_connection_failure == "true" or self.retry_on_connection_failure)
            else exclude.add("number_of_retries")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_unit")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_unit")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_status")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_status")
        )
        (
            include.add("save_count")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("save_count")
        )
        (
            include.add("load_to_zos_image_copy_recovery_recovery_file")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_recovery_recovery_file")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_number_of_buffers")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_number_of_buffers")
        )
        (
            include.add("partition_number")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("partition_number")
        )
        (
            include.add("fail_on_row_error")
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
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
            and (self.has_reject_output == "false" or not self.has_reject_output)
            else exclude.add("fail_on_row_error")
        )
        (
            include.add("partitioned_database_configuration")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("partitioned_database_configuration")
        )
        (
            include.add("interval_between_retries")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.retry_on_connection_failure == "true" or self.retry_on_connection_failure)
            else exclude.add("interval_between_retries")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_storage_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_storage_class")
        )
        (
            include.add("indexing_mode")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("indexing_mode")
        )
        (
            include.add("user_defined_sql_supress_warnings")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("user_defined_sql_supress_warnings")
        )
        (
            include.add("data_buffer_size")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("data_buffer_size")
        )
        (
            include.add("load_control_dump_file")
            if (self.bulk_load_with_lob_or_xml_columns == "false" or not self.bulk_load_with_lob_or_xml_columns)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("load_control_dump_file")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_primary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_data_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_data_class")
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
            else exclude.add("read_create_statement_from_file")
        )
        (
            include.add("clean_up_on_failure")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("clean_up_on_failure")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_primary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_primary_allocation")
        )
        (
            include.add("uss_pipe_directory")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.load_to_zos_load_method == "uss_pipes")
            else exclude.add("uss_pipe_directory")
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
            include.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_status")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_status")
        )
        (
            include.add("lock_wait_mode")
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
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
            else exclude.add("lock_wait_mode")
        )
        (
            include.add("load_mode")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "append")
                    or (self.table_action == "append")
                )
            )
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("load_mode")
        )
        (
            include.add("directory_for_data_files")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("directory_for_data_files")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_data_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_data_class")
        )
        (
            include.add("set_copy_pending")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.load_with_logging == "false" or not self.load_with_logging)
            else exclude.add("set_copy_pending")
        )
        (
            include.add("use_unique_key_column")
            if (
                (self.direct_insert == "false" or not self.direct_insert)
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
            )
            else exclude.add("use_unique_key_column")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_space_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_volumes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_volumes")
        )
        (
            include.add("update_columns")
            if (
                (self.use_external_tables == "true" or self.use_external_tables)
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
            )
            or (
                (self.direct_insert == "false" or not self.direct_insert)
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
            )
            else exclude.add("update_columns")
        )
        (
            include.add("log_key_values_only")
            if (
                self.log_column_values_on_first_row_error == "true" or self.log_column_values_on_first_row_error
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
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
            else exclude.add("log_key_values_only")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_abnormal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("non_recoverable_load")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("non_recoverable_load")
        )
        (
            include.add("key_columns")
            if (
                (self.use_external_tables == "true" or self.use_external_tables)
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
                            and "insert_new_rows_only" in str(self.write_mode.value)
                        )
                        or ("insert_new_rows_only" in str(self.write_mode))
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
                (self.direct_insert == "false" or not self.direct_insert)
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
                            and "insert_new_rows_only" in str(self.write_mode.value)
                        )
                        or ("insert_new_rows_only" in str(self.write_mode))
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
            else exclude.add("key_columns")
        )
        (
            include.add("load_to_zos_files_only")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_files_only")
        )
        (
            include.add("user")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("user")
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
            else exclude.add("fail_on_error_truncate_statement")
        )
        (
            include.add("row_count")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("row_count")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_normal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_file_disposition_status")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_image_copy_function_recovery_file_file_disposition_status")
        )
        (
            include.add("higher_port_number")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.port_range == "true" or self.port_range)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("higher_port_number")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_storage_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_storage_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_normal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_volumes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_unit")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_unit")
        )
        (
            include.add("external_table_collect_statistics_during_load")
            if (self.use_external_tables == "true" or self.use_external_tables)
            else exclude.add("external_table_collect_statistics_during_load")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_volumes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_volumes")
        )
        (
            include.add("truncate_table")
            if (self.temporary_work_table_mode == "existing")
            and (self.direct_insert == "false" or not self.direct_insert)
            else exclude.add("truncate_table")
        )
        (
            include.add("fail_on_error")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("fail_on_error")
        )
        (
            include.add("index_in")
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
            and (self.target_table_on_db2_for_z_os == "false" or not self.target_table_on_db2_for_z_os)
            else exclude.add("index_in")
        )
        (
            include.add("isolate_partition_errors")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("isolate_partition_errors")
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
            else exclude.add("generate_drop_statement_at_runtime")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_number_of_buffers")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_number_of_buffers")
        )
        (
            include.add("user_defined_sql_file_name")
            if (self.user_defined_sql == "file")
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("user_defined_sql_file_name")
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
            include.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_abnormal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("hfs_file_directory")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.transfer_type
                and "lftp" in str(self.transfer_type)
                and self.transfer_type
                and "sftp" in str(self.transfer_type)
            )
            else exclude.add("hfs_file_directory")
        )
        (
            include.add("use_external_tables")
            if (
                (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
                and (
                    self.write_mode
                    and (
                        (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                        or (self.write_mode == "insert")
                    )
                )
            )
            or (self.direct_insert == "false" or not self.direct_insert)
            else exclude.add("use_external_tables")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_primary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_status")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_file_disposition_status")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_unit")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_unit")
        )
        (
            include.add("temporary_files_directory")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("temporary_files_directory")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_secondary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_secondary_allocation")
        )
        (
            include.add("scope")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("scope")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_primary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_primary_allocation")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_dataset_name")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_dataset_name")
        )
        (
            include.add("maximum_reject_count")
            if (self.use_external_tables == "true" or self.use_external_tables)
            else exclude.add("maximum_reject_count")
        )
        (
            include.add("sort_buffer_size")
            if (
                self.indexing_mode
                and "automatic_selection" in str(self.indexing_mode)
                and self.indexing_mode
                and "extend_existing_indexes" in str(self.indexing_mode)
                and self.indexing_mode
                and "rebuild_table_indexes" in str(self.indexing_mode)
            )
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("sort_buffer_size")
        )
        (
            include.add("partitioning_partition_numbers")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("partitioning_partition_numbers")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_storage_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_storage_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_volumes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_volumes")
        )
        (
            include.add("generate_create_statement_distribute_by_hash_key_column_names")
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
            and (self.distribute_by == "hash")
            and (self.target_table_on_db2_for_z_os == "false" or not self.target_table_on_db2_for_z_os)
            else exclude.add("generate_create_statement_distribute_by_hash_key_column_names")
        )
        (
            include.add("warning_count")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("warning_count")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_dataset_name")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_dataset_name")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_data_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_data_class")
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
            include.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_normal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_normal_termination")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_space_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_space_type")
        )
        (
            include.add("buffer_pool")
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
            and (self.target_table_on_db2_for_z_os == "true" or self.target_table_on_db2_for_z_os)
            else exclude.add("buffer_pool")
        )
        (
            include.add("graphic_character_set")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("graphic_character_set")
        )
        (
            include.add("loaded_data_copy_location")
            if (self.copy_loaded_data == "use_device_or_directory")
            and (self.non_recoverable_load == "false" or not self.non_recoverable_load)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("loaded_data_copy_location")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_unit")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_unit")
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
            else exclude.add("read_truncate_statement_from_file")
        )
        (
            include.add("organize_by")
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
            and (self.target_table_on_db2_for_z_os == "false" or not self.target_table_on_db2_for_z_os)
            else exclude.add("organize_by")
        )
        (
            include.add("restart_phase")
            if (self.load_mode == "restart")
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("restart_phase")
        )
        (
            include.add("change_limit_percent_2")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.image_copy_function == "incremental")
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("change_limit_percent_2")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_abnormal_termination")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_abnormal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_abnormal_termination")
        )
        (
            include.add("load_with_logging")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_with_logging")
        )
        (
            include.add("output_partition_numbers")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("output_partition_numbers")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_primary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_primary_allocation")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_management_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_management_class")
        )
        (
            include.add("retry_on_connection_failure")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.transfer_type
                and "ftp" in str(self.transfer_type)
                and self.transfer_type
                and "lftp" in str(self.transfer_type)
            )
            else exclude.add("retry_on_connection_failure")
        )
        (
            include.add("check_truncation")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("check_truncation")
        )
        (
            include.add("bulk_load_to_db2_on_z_os")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("bulk_load_to_db2_on_z_os")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_storage_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_storage_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_number_of_buffers")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_number_of_buffers")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_normal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_file_disposition_normal_termination")
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
            include.add("change_limit_percent_1")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.image_copy_function == "incremental")
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("change_limit_percent_1")
        )
        (
            include.add("batch_pipe_system_id")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.load_to_zos_load_method == "batch_pipes")
            else exclude.add("batch_pipe_system_id")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_status")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_status")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_primary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_primary_allocation")
        )
        (
            include.add("value_compression")
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
            and (self.target_table_on_db2_for_z_os == "false" or not self.target_table_on_db2_for_z_os)
            and (self.organize_by == "row")
            else exclude.add("value_compression")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_dataset_name")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_dataset_name")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_number_of_buffers")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_number_of_buffers")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_data_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_data_class")
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
        (
            include.add("copy_loaded_data")
            if (self.non_recoverable_load == "false" or not self.non_recoverable_load)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("copy_loaded_data")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_data_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_data_class")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_secondary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_secondary_allocation")
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
            include.add("load_to_zos_encoding_character_set")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_encoding_character_set")
        )
        (
            include.add("utility_id")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("utility_id")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_number_of_buffers")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_number_of_buffers")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_primary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_status")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_status")
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
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
            else exclude.add("create_table_statement")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_data_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_data_class")
        )
        (
            include.add("time_commit_interval")
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
                        and "insert_then_update" in str(self.write_mode.value)
                    )
                    or ("insert_then_update" in str(self.write_mode))
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
            else exclude.add("time_commit_interval")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_abnormal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_status")
            if ((self.load_to_zos_load_method == "mvs_datasets") or (self.transfer_type == "ftp"))
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_status")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_storage_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_storage_class")
        )
        (
            include.add("sql_user_defined_sql_file_character_set")
            if (self.user_defined_sql == "file")
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("sql_user_defined_sql_file_character_set")
        )
        (
            include.add("message_file")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("message_file")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_space_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_space_type")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_storage_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_storage_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_secondary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_secondary_allocation")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_normal_termination")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_file_disposition_normal_termination")
        )
        (
            include.add("encoding")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("encoding")
        )
        (
            include.add("table_name")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            or (self.direct_insert == "false" or not self.direct_insert)
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
            or (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("drop_table")
            if (self.direct_insert == "false" or not self.direct_insert)
            else exclude.add("drop_table")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_secondary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_secondary_allocation")
        )
        (
            include.add("report_only")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.image_copy_function == "incremental")
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("report_only")
        )
        (
            include.add("device_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("device_type")
        )
        (
            include.add("load_control_statistics")
            if (self.load_mode == "replace")
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("load_control_statistics")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_volumes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_primary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_secondary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_secondary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_unit")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_unit")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_space_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_space_type")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_secondary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_secondary_allocation")
        )
        (
            include.add("status_interval")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("status_interval")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_secondary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_secondary_allocation")
        )
        (
            include.add("lob_path_list")
            if (self.bulk_load_with_lob_or_xml_columns == "false" or not self.bulk_load_with_lob_or_xml_columns)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("lob_path_list")
        )
        (
            include.add("table_action_generate_create_statement_create_table_in")
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
                or self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            else exclude.add("table_action_generate_create_statement_create_table_in")
        )
        (
            include.add("disk_parallelism")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("disk_parallelism")
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
                or self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            else exclude.add("fail_on_error_create_statement")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_status")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_file_disposition_status")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_normal_termination")
            if (self.load_to_zos_load_method == "mvs_datasets")
            and (self.transfer_type == "ftp")
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_file_disposition_normal_termination")
        )
        (
            include.add("keep_existing_records_in_table_space")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.concurrent_access_level == "none")
            and (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "append")
                    or (self.table_action == "append")
                )
            )
            else exclude.add("keep_existing_records_in_table_space")
        )
        (
            include.add("total_number_of_player_processes")
            if (self.limit_parallelism == "true" or self.limit_parallelism)
            else exclude.add("total_number_of_player_processes")
        )
        (
            include.add("atomic_arrays")
            if (
                self.insert_buffering
                and "default" in str(self.insert_buffering)
                and self.insert_buffering
                and "ignore_duplicates" in str(self.insert_buffering)
                and self.insert_buffering
                and "on" in str(self.insert_buffering)
            )
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                    or (self.write_mode == "insert")
                )
            )
            else exclude.add("atomic_arrays")
        )
        (
            include.add("transfer_command")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("transfer_command")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_status")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_status")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_space_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_space_type")
        )
        (
            include.add("port_range")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("port_range")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_file_disposition_abnormal_termination")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_image_copy_function_recovery_file_file_disposition_abnormal_termination")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_number_of_buffers")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_number_of_buffers")
        )
        (
            include.add("load_control_files_only")
            if (
                ((self.load_control_load_method == "sequential_files"))
                or (
                    (
                        self.bulk_load_with_lob_or_xml_columns == "false"
                        or not self.bulk_load_with_lob_or_xml_columns
                    )
                    and (self.load_control_load_method == "sequential_files")
                )
            )
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("load_control_files_only")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_management_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_management_class")
        )
        (
            include.add("partition_collecting_statistics")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.load_control_statistics == "true" or self.load_control_statistics)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("partition_collecting_statistics")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_space_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_space_type")
        )
        (
            include.add("column_delimiter")
            if (
                self.log_column_values_on_first_row_error == "true" or self.log_column_values_on_first_row_error
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
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
            include.add("load_to_zos_image_copy_function_recovery_file_space_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_space_type")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_volumes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_volumes")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_management_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_management_class")
        )
        (
            include.add("omit_header")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("omit_header")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_storage_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_storage_class")
        )
        (
            include.add("directory_for_log_files")
            if (self.use_external_tables == "true" or self.use_external_tables)
            else exclude.add("directory_for_log_files")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_management_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_management_class")
        )
        (
            include.add("load_mode")
            if (self.bulk_load_with_lob_or_xml_columns == "true" or self.bulk_load_with_lob_or_xml_columns)
            else exclude.add("load_mode")
        )
        (
            include.add("insert_buffering")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                    or (self.write_mode == "insert")
                )
            )
            else exclude.add("insert_buffering")
        )
        (
            include.add("image_copy_function")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("image_copy_function")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_dataset_name")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_dataset_name")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_data_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_data_class")
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
            else exclude.add("generate_truncate_statement_at_runtime")
        )
        (
            include.add("row_count_estimate")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("row_count_estimate")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_space_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_space_type")
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
            else exclude.add("fail_on_error_drop_statement")
        )
        (
            include.add("file_type")
            if (self.bulk_load_with_lob_or_xml_columns == "false" or not self.bulk_load_with_lob_or_xml_columns)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("file_type")
        )
        (
            include.add("without_prompting")
            if (self.bulk_load_with_lob_or_xml_columns == "false" or not self.bulk_load_with_lob_or_xml_columns)
            and (self.load_control_load_method == "sequential_files")
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("without_prompting")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_unit")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_unit")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_dataset_name")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_dataset_name")
        )
        (
            include.add("check_pending_cascade")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("check_pending_cascade")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_number_of_buffers")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_number_of_buffers")
        )
        (
            include.add("name_of_table_space")
            if (self.allow_access_mode == "read")
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("name_of_table_space")
        )
        (
            include.add("library_used_to_copy")
            if (self.copy_loaded_data == "use_shared_library")
            and (self.non_recoverable_load == "false" or not self.non_recoverable_load)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("library_used_to_copy")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_dataset_name")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_dataset_name")
        )
        (
            include.add("allow_changes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("allow_changes")
        )
        (
            include.add("temporary_work_table_mode")
            if (self.direct_insert == "false" or not self.direct_insert)
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
            else exclude.add("read_drop_statement_from_file")
        )
        (
            include.add("bulk_load_with_lob_or_xml_columns")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("bulk_load_with_lob_or_xml_columns")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_secondary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_secondary_allocation")
        )
        (
            include.add("trace")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("trace")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_normal_termination")
            if ((self.load_to_zos_load_method == "mvs_datasets") or (self.transfer_type == "ftp"))
            and (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_file_disposition_normal_termination")
        )
        (
            include.add("log_column_values_on_first_row_error")
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
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
            else exclude.add("log_column_values_on_first_row_error")
        )
        (
            include.add("temporary_work_table_name")
            if (self.temporary_work_table_mode == "existing")
            and (self.direct_insert == "false" or not self.direct_insert)
            else exclude.add("temporary_work_table_name")
        )
        (
            include.add("load_to_zos_data_file_attributes_work2_data_set_management_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work2_data_set_management_class")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_volumes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_volumes")
        )
        (
            include.add("transfer_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("transfer_type")
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
            include.add("transfer_to")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("transfer_to")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_dataset_name")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_dataset_name")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_management_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_management_class")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_space_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_space_type")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_normal_termination")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add(
                "load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_normal_termination"
            )
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_space_type")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_space_type")
        )
        (
            include.add("cpu_parallelism")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("cpu_parallelism")
        )
        (
            include.add("directory_for_data_and_command_files")
            if (
                ((self.load_control_load_method == "sequential_files"))
                or (
                    (
                        self.bulk_load_with_lob_or_xml_columns == "false"
                        or not self.bulk_load_with_lob_or_xml_columns
                    )
                    and (self.load_control_load_method == "sequential_files")
                )
            )
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("directory_for_data_and_command_files")
        )
        (
            include.add("remove_intermediate_data_file")
            if (self.load_control_files_only == "false" or not self.load_control_files_only)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("remove_intermediate_data_file")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_secondary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_secondary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_input_data_files_storage_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_input_data_files_storage_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_primary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_primary_allocation")
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
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
            include.add("load_to_zos_image_copy_function_recovery_backup_secondary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_secondary_allocation")
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
            else exclude.add("drop_table_statement")
        )
        (
            include.add("unique_key_column")
            if (
                (self.direct_insert == "false" or not self.direct_insert)
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
            )
            and (self.use_unique_key_column == "true" or self.use_unique_key_column)
            else exclude.add("unique_key_column")
        )
        (
            include.add("target_table_on_db2_for_z_os")
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
                or self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            else exclude.add("target_table_on_db2_for_z_os")
        )
        (
            include.add("load_to_zos_statistics")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            else exclude.add("load_to_zos_statistics")
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
                or self.table_action
                and (
                    (
                        hasattr(self.table_action, "value")
                        and self.table_action.value
                        and "replace" in str(self.table_action.value)
                    )
                    or ("replace" in str(self.table_action))
                )
            )
            else exclude.add("generate_create_statement_at_runtime")
        )
        (
            include.add("distribute_by")
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
            and (self.target_table_on_db2_for_z_os == "false" or not self.target_table_on_db2_for_z_os)
            else exclude.add("distribute_by")
        )
        (
            include.add("load_to_zos_data_file_attributes_map_data_set_storage_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_map_data_set_storage_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_file_disposition_normal_termination")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_image_copy_function_recovery_file_file_disposition_normal_termination")
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
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
            include.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_abnormal_termination")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_file_disposition_abnormal_termination")
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
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
            include.add("load_to_zos_image_copy_function_image_copy_file_volumes")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_volumes")
        )
        (
            include.add("perform_table_action_first")
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
            else exclude.add("perform_table_action_first")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_file_management_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_file_management_class")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_status")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_image_copy_backup_file == "true"
                or self.load_to_zos_image_copy_image_copy_backup_file
            )
            and (self.load_to_zos_load_method == "mvs_datasets")
            else exclude.add("load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_status")
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
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("load_to_zos_data_file_attributes_work1_data_set_primary_allocation")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_work1_data_set_primary_allocation")
        )
        (
            include.add("load_to_zos_data_file_attributes_discard_data_set_number_of_buffers")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_discard_data_set_number_of_buffers")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_data_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_data_class")
        )
        (
            include.add("load_to_zos_image_copy_function_recovery_backup_dataset_name")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_backup_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_backup_file
            )
            else exclude.add("load_to_zos_image_copy_function_recovery_backup_dataset_name")
        )
        (
            include.add("load_to_zos_image_copy_recovery_recovery_backup_file")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.load_to_zos_image_copy_recovery_recovery_file == "true"
                or self.load_to_zos_image_copy_recovery_recovery_file
            )
            else exclude.add("load_to_zos_image_copy_recovery_recovery_backup_file")
        )
        (
            include.add("concurrent_access_level")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "append")
                    or (self.table_action == "append")
                )
            )
            else exclude.add("concurrent_access_level")
        )
        (
            include.add("system_pages")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("system_pages")
        )
        (
            include.add("statistics_on_columns")
            if (self.use_external_tables == "true" or self.use_external_tables)
            and (
                self.external_table_collect_statistics_during_load == "true"
                or self.external_table_collect_statistics_during_load
            )
            else exclude.add("statistics_on_columns")
        )
        (
            include.add("maximum_partitioning_agents")
            if (self.partitioned_database_configuration == "true" or self.partitioned_database_configuration)
            and (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("maximum_partitioning_agents")
        )
        (
            include.add("lock_with_force")
            if (self.bulk_load_to_db2_on_z_os == "false" or not self.bulk_load_to_db2_on_z_os)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "bulk_load")
                    or (self.write_mode == "bulk_load")
                )
            )
            else exclude.add("lock_with_force")
        )
        (
            include.add("load_to_zos_data_file_attributes_error_data_set_management_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (self.transfer_type == "ftp")
            else exclude.add("load_to_zos_data_file_attributes_error_data_set_management_class")
        )
        (
            include.add("load_to_zos_image_copy_image_copy_backup_file")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_image_copy_backup_file")
        )
        (
            include.add("load_to_zos_image_copy_function_image_copy_file_management_class")
            if (self.bulk_load_to_db2_on_z_os == "true" or self.bulk_load_to_db2_on_z_os)
            and (
                self.image_copy_function
                and "concurrent" in str(self.image_copy_function)
                and self.image_copy_function
                and "full" in str(self.image_copy_function)
                and self.image_copy_function
                and "incremental" in str(self.image_copy_function)
            )
            else exclude.add("load_to_zos_image_copy_function_image_copy_file_management_class")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "array_size",
            "auto_commit_mode",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
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
            "directory_for_named_pipe",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_and_after_sql",
            "enable_before_sql",
            "enable_before_sql_node",
            "enable_flow_acp_control",
            "enable_lob_references",
            "enable_partitioned_reads",
            "enable_quoted_identifiers",
            "enable_schemaless_design",
            "end_of_data",
            "end_of_wave",
            "execution_mode",
            "external_tables_other_options",
            "fail_on_code_page_mismatch",
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "fail_on_size_mismatch",
            "fail_on_type_mismatch",
            "flow_dirty",
            "generate_partitioning_sql",
            "generate_sql_at_runtime",
            "has_reference_output",
            "hide",
            "input_count",
            "input_link_description",
            "input_method",
            "inputcol_properties",
            "isolation_level",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_column",
            "limit",
            "limit_number_of_returned_rows",
            "lock_wait_mode",
            "lock_wait_time",
            "lookup_type",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "migrated_job",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "pad_character",
            "part_stable_coll",
            "part_stable_ordered",
            "part_stable_roundrobin_coll",
            "part_unique_coll",
            "part_unique_ordered",
            "part_unique_roundrobin_coll",
            "partition_type",
            "partitioned_reads_column_name",
            "partitioned_reads_method",
            "partitioned_reads_table_name",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "prefix_for_expression_columns",
            "preserve_partitioning",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_after_sql_node_statements_from_file",
            "read_after_sql_statements_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statements_from_file",
            "read_select_statement_from_file",
            "record_count",
            "record_ordering",
            "reoptimization",
            "row_limit",
            "runtime_column_propagation",
            "schema_name",
            "select_statement",
            "select_statement_column",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "sql_other_clause",
            "sql_select_statement_other_clause",
            "sql_select_statement_parameters",
            "sql_select_statement_table_name",
            "sql_select_statement_where_clause",
            "sql_where_clause",
            "stable",
            "stage_description",
            "table_name",
            "unique",
            "use_et_source",
            "use_external_tables",
            "xml_column_as_lob",
        }
        required = {
            "columns",
            "current_output_link_type",
            "database",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname",
            "lock_wait_time",
            "output_acp_should_hide",
            "partitioned_reads_column_name",
            "partitioned_reads_table_name",
            "password",
            "port",
            "select_statement",
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
            "allow_access_mode",
            "allow_changes",
            "array_size",
            "atomic_arrays",
            "auto_commit_mode",
            "batch_pipe_system_id",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffer_pool",
            "buffering_mode",
            "bulk_load_to_db2_on_z_os",
            "bulk_load_with_lob_or_xml_columns",
            "ccsid",
            "change_limit_percent_1",
            "change_limit_percent_2",
            "check_pending_cascade",
            "check_truncation",
            "clean_up_on_failure",
            "collecting",
            "column_delimiter",
            "column_metadata_change_propagation",
            "combinability_mode",
            "compress",
            "concurrent_access_level",
            "copy_loaded_data",
            "cpu_parallelism",
            "create_table_statement",
            "credentials_input_method_ssl",
            "current_output_link_type",
            "data_buffer_size",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "delete_statement",
            "device_type",
            "direct_insert",
            "directory_for_data_and_command_files",
            "directory_for_data_files",
            "directory_for_log_files",
            "directory_for_named_pipe",
            "directory_for_named_pipe_unix_only",
            "disk_parallelism",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "distribute_by",
            "drop_table",
            "drop_table_statement",
            "drop_unmatched_fields",
            "dsn_prefix",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_and_after_sql",
            "enable_before_sql",
            "enable_before_sql_node",
            "enable_flow_acp_control",
            "enable_quoted_identifiers",
            "enable_schemaless_design",
            "encoding",
            "exception_table_name",
            "execution_mode",
            "external_table_collect_statistics_during_load",
            "external_tables_other_options",
            "fail_on_code_page_mismatch",
            "fail_on_error",
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "fail_on_error_create_statement",
            "fail_on_error_drop_statement",
            "fail_on_error_truncate_statement",
            "fail_on_row_error",
            "fail_on_size_mismatch",
            "fail_on_type_mismatch",
            "file_type",
            "flow_dirty",
            "generate_create_statement_at_runtime",
            "generate_create_statement_distribute_by_hash_key_column_names",
            "generate_drop_statement_at_runtime",
            "generate_sql_at_runtime",
            "generate_truncate_statement_at_runtime",
            "graphic_character_set",
            "has_reject_output",
            "hfs_file_directory",
            "hide",
            "higher_port_number",
            "hold_quiesce",
            "image_copy_function",
            "index_in",
            "indexing_mode",
            "input_count",
            "input_link_description",
            "input_link_ordering",
            "input_method",
            "inputcol_properties",
            "insert_buffering",
            "insert_statement",
            "interval_between_retries",
            "isolate_partition_errors",
            "isolation_level",
            "keep_existing_records_in_table_space",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_column",
            "key_columns",
            "library_used_to_copy",
            "limit_parallelism",
            "load_control_dump_file",
            "load_control_files_only",
            "load_control_load_method",
            "load_control_statistics",
            "load_mode",
            "load_timeout",
            "load_to_zos_data_file_attributes_discard_data_set_data_class",
            "load_to_zos_data_file_attributes_discard_data_set_dataset_name",
            "load_to_zos_data_file_attributes_discard_data_set_file_disposition_abnormal_termination",
            "load_to_zos_data_file_attributes_discard_data_set_file_disposition_normal_termination",
            "load_to_zos_data_file_attributes_discard_data_set_file_disposition_status",
            "load_to_zos_data_file_attributes_discard_data_set_management_class",
            "load_to_zos_data_file_attributes_discard_data_set_number_of_buffers",
            "load_to_zos_data_file_attributes_discard_data_set_primary_allocation",
            "load_to_zos_data_file_attributes_discard_data_set_secondary_allocation",
            "load_to_zos_data_file_attributes_discard_data_set_space_type",
            "load_to_zos_data_file_attributes_discard_data_set_storage_class",
            "load_to_zos_data_file_attributes_discard_data_set_unit",
            "load_to_zos_data_file_attributes_discard_data_set_volumes",
            "load_to_zos_data_file_attributes_error_data_set_data_class",
            "load_to_zos_data_file_attributes_error_data_set_dataset_name",
            "load_to_zos_data_file_attributes_error_data_set_file_disposition_abnormal_termination",
            "load_to_zos_data_file_attributes_error_data_set_file_disposition_normal_termination",
            "load_to_zos_data_file_attributes_error_data_set_file_disposition_status",
            "load_to_zos_data_file_attributes_error_data_set_management_class",
            "load_to_zos_data_file_attributes_error_data_set_number_of_buffers",
            "load_to_zos_data_file_attributes_error_data_set_primary_allocation",
            "load_to_zos_data_file_attributes_error_data_set_secondary_allocation",
            "load_to_zos_data_file_attributes_error_data_set_space_type",
            "load_to_zos_data_file_attributes_error_data_set_storage_class",
            "load_to_zos_data_file_attributes_error_data_set_unit",
            "load_to_zos_data_file_attributes_error_data_set_volumes",
            "load_to_zos_data_file_attributes_input_data_files_data_class",
            "load_to_zos_data_file_attributes_input_data_files_dataset_name",
            "load_to_zos_data_file_attributes_input_data_files_file_disposition_abnormal_termination",
            "load_to_zos_data_file_attributes_input_data_files_file_disposition_normal_termination",
            "load_to_zos_data_file_attributes_input_data_files_file_disposition_status",
            "load_to_zos_data_file_attributes_input_data_files_management_class",
            "load_to_zos_data_file_attributes_input_data_files_number_of_buffers",
            "load_to_zos_data_file_attributes_input_data_files_primary_allocation",
            "load_to_zos_data_file_attributes_input_data_files_secondary_allocation",
            "load_to_zos_data_file_attributes_input_data_files_space_type",
            "load_to_zos_data_file_attributes_input_data_files_storage_class",
            "load_to_zos_data_file_attributes_input_data_files_unit",
            "load_to_zos_data_file_attributes_input_data_files_volumes",
            "load_to_zos_data_file_attributes_map_data_set_data_class",
            "load_to_zos_data_file_attributes_map_data_set_dataset_name",
            "load_to_zos_data_file_attributes_map_data_set_file_disposition_abnormal_termination",
            "load_to_zos_data_file_attributes_map_data_set_file_disposition_normal_termination",
            "load_to_zos_data_file_attributes_map_data_set_file_disposition_status",
            "load_to_zos_data_file_attributes_map_data_set_management_class",
            "load_to_zos_data_file_attributes_map_data_set_number_of_buffers",
            "load_to_zos_data_file_attributes_map_data_set_primary_allocation",
            "load_to_zos_data_file_attributes_map_data_set_secondary_allocation",
            "load_to_zos_data_file_attributes_map_data_set_space_type",
            "load_to_zos_data_file_attributes_map_data_set_storage_class",
            "load_to_zos_data_file_attributes_map_data_set_unit",
            "load_to_zos_data_file_attributes_map_data_set_volumes",
            "load_to_zos_data_file_attributes_work1_data_set_data_class",
            "load_to_zos_data_file_attributes_work1_data_set_dataset_name",
            "load_to_zos_data_file_attributes_work1_data_set_file_disposition_abnormal_termination",
            "load_to_zos_data_file_attributes_work1_data_set_file_disposition_normal_termination",
            "load_to_zos_data_file_attributes_work1_data_set_file_disposition_status",
            "load_to_zos_data_file_attributes_work1_data_set_management_class",
            "load_to_zos_data_file_attributes_work1_data_set_number_of_buffers",
            "load_to_zos_data_file_attributes_work1_data_set_primary_allocation",
            "load_to_zos_data_file_attributes_work1_data_set_secondary_allocation",
            "load_to_zos_data_file_attributes_work1_data_set_space_type",
            "load_to_zos_data_file_attributes_work1_data_set_storage_class",
            "load_to_zos_data_file_attributes_work1_data_set_unit",
            "load_to_zos_data_file_attributes_work1_data_set_volumes",
            "load_to_zos_data_file_attributes_work2_data_set_data_class",
            "load_to_zos_data_file_attributes_work2_data_set_dataset_name",
            "load_to_zos_data_file_attributes_work2_data_set_file_disposition_abnormal_termination",
            "load_to_zos_data_file_attributes_work2_data_set_file_disposition_normal_termination",
            "load_to_zos_data_file_attributes_work2_data_set_file_disposition_status",
            "load_to_zos_data_file_attributes_work2_data_set_management_class",
            "load_to_zos_data_file_attributes_work2_data_set_number_of_buffers",
            "load_to_zos_data_file_attributes_work2_data_set_primary_allocation",
            "load_to_zos_data_file_attributes_work2_data_set_secondary_allocation",
            "load_to_zos_data_file_attributes_work2_data_set_space_type",
            "load_to_zos_data_file_attributes_work2_data_set_storage_class",
            "load_to_zos_data_file_attributes_work2_data_set_unit",
            "load_to_zos_data_file_attributes_work2_data_set_volumes",
            "load_to_zos_encoding_character_set",
            "load_to_zos_files_only",
            "load_to_zos_image_copy_function_image_copy_backup_file_data_class",
            "load_to_zos_image_copy_function_image_copy_backup_file_dataset_name",
            "load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_abnormal_termination",
            "load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_normal_termination",
            "load_to_zos_image_copy_function_image_copy_backup_file_file_disposition_status",
            "load_to_zos_image_copy_function_image_copy_backup_file_management_class",
            "load_to_zos_image_copy_function_image_copy_backup_file_number_of_buffers",
            "load_to_zos_image_copy_function_image_copy_backup_file_primary_allocation",
            "load_to_zos_image_copy_function_image_copy_backup_file_secondary_allocation",
            "load_to_zos_image_copy_function_image_copy_backup_file_space_type",
            "load_to_zos_image_copy_function_image_copy_backup_file_storage_class",
            "load_to_zos_image_copy_function_image_copy_backup_file_unit",
            "load_to_zos_image_copy_function_image_copy_backup_file_volumes",
            "load_to_zos_image_copy_function_image_copy_file_data_class",
            "load_to_zos_image_copy_function_image_copy_file_dataset_name",
            "load_to_zos_image_copy_function_image_copy_file_file_disposition_abnormal_termination",
            "load_to_zos_image_copy_function_image_copy_file_file_disposition_normal_termination",
            "load_to_zos_image_copy_function_image_copy_file_file_disposition_status",
            "load_to_zos_image_copy_function_image_copy_file_management_class",
            "load_to_zos_image_copy_function_image_copy_file_number_of_buffers",
            "load_to_zos_image_copy_function_image_copy_file_primary_allocation",
            "load_to_zos_image_copy_function_image_copy_file_secondary_allocation",
            "load_to_zos_image_copy_function_image_copy_file_space_type",
            "load_to_zos_image_copy_function_image_copy_file_storage_class",
            "load_to_zos_image_copy_function_image_copy_file_unit",
            "load_to_zos_image_copy_function_image_copy_file_volumes",
            "load_to_zos_image_copy_function_recovery_backup_data_class",
            "load_to_zos_image_copy_function_recovery_backup_dataset_name",
            "load_to_zos_image_copy_function_recovery_backup_file_disposition_abnormal_termination",
            "load_to_zos_image_copy_function_recovery_backup_file_disposition_normal_termination",
            "load_to_zos_image_copy_function_recovery_backup_file_disposition_status",
            "load_to_zos_image_copy_function_recovery_backup_management_class",
            "load_to_zos_image_copy_function_recovery_backup_number_of_buffers",
            "load_to_zos_image_copy_function_recovery_backup_primary_allocation",
            "load_to_zos_image_copy_function_recovery_backup_secondary_allocation",
            "load_to_zos_image_copy_function_recovery_backup_space_type",
            "load_to_zos_image_copy_function_recovery_backup_storage_class",
            "load_to_zos_image_copy_function_recovery_backup_unit",
            "load_to_zos_image_copy_function_recovery_backup_volumes",
            "load_to_zos_image_copy_function_recovery_file_data_class",
            "load_to_zos_image_copy_function_recovery_file_dataset_name",
            "load_to_zos_image_copy_function_recovery_file_file_disposition_abnormal_termination",
            "load_to_zos_image_copy_function_recovery_file_file_disposition_normal_termination",
            "load_to_zos_image_copy_function_recovery_file_file_disposition_status",
            "load_to_zos_image_copy_function_recovery_file_management_class",
            "load_to_zos_image_copy_function_recovery_file_number_of_buffers",
            "load_to_zos_image_copy_function_recovery_file_primary_allocation",
            "load_to_zos_image_copy_function_recovery_file_secondary_allocation",
            "load_to_zos_image_copy_function_recovery_file_space_type",
            "load_to_zos_image_copy_function_recovery_file_storage_class",
            "load_to_zos_image_copy_function_recovery_file_unit",
            "load_to_zos_image_copy_function_recovery_file_volumes",
            "load_to_zos_image_copy_image_copy_backup_file",
            "load_to_zos_image_copy_recovery_recovery_backup_file",
            "load_to_zos_image_copy_recovery_recovery_file",
            "load_to_zos_load_method",
            "load_to_zos_statistics",
            "load_to_zos_transfer_password",
            "load_with_logging",
            "loaded_data_copy_location",
            "lob_path_list",
            "lock_wait_mode",
            "lock_wait_time",
            "lock_with_force",
            "log_column_values_on_first_row_error",
            "log_key_values_only",
            "lower_port_number",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "maximum_partitioning_agents",
            "maximum_reject_count",
            "message_file",
            "migrated_job",
            "name_of_table_space",
            "non_recoverable_load",
            "number_of_retries",
            "omit_header",
            "organize_by",
            "other_options",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "output_partition_numbers",
            "outputcol_properties",
            "pad_character",
            "part_stable_coll",
            "part_stable_ordered",
            "part_stable_roundrobin_coll",
            "part_unique_coll",
            "part_unique_ordered",
            "part_unique_roundrobin_coll",
            "partition_collecting_statistics",
            "partition_number",
            "partition_type",
            "partitioned_database_configuration",
            "partitioned_distribution_file",
            "partitioning_partition_numbers",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "perform_table_action_first",
            "port_range",
            "prefix_for_expression_columns",
            "preserve_partitioning",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_after_sql_node_statements_from_file",
            "read_after_sql_statements_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statements_from_file",
            "read_create_statement_from_file",
            "read_drop_statement_from_file",
            "read_truncate_statement_from_file",
            "record_count",
            "record_ordering",
            "remove_intermediate_data_file",
            "reoptimization",
            "report_only",
            "restart_phase",
            "retry_on_connection_failure",
            "row_count",
            "row_count_estimate",
            "runtime_column_propagation",
            "save_count",
            "schema_name",
            "scope",
            "set_copy_pending",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_buffer_size",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "sql_delete_statement",
            "sql_delete_statement_parameters",
            "sql_delete_statement_where_clause",
            "sql_insert_statement",
            "sql_insert_statement_parameters",
            "sql_insert_statement_where_clause",
            "sql_update_statement",
            "sql_update_statement_parameters",
            "sql_update_statement_where_clause",
            "sql_user_defined_sql_file_character_set",
            "stable",
            "stage_description",
            "statistics_on_columns",
            "status_interval",
            "system_pages",
            "table_action",
            "table_action_generate_create_statement_create_table_in",
            "table_name",
            "target_table_on_db2_for_z_os",
            "temporary_files_directory",
            "temporary_work_table_mode",
            "temporary_work_table_name",
            "time_commit_interval",
            "total_number_of_player_processes",
            "trace",
            "transfer_command",
            "transfer_to",
            "transfer_type",
            "truncate_table",
            "truncate_table_statement",
            "type",
            "unique",
            "unique_key_column",
            "update_columns",
            "update_statement",
            "use_external_tables",
            "use_unique_key_column",
            "user",
            "user_defined_sql",
            "user_defined_sql_file_name",
            "user_defined_sql_statements",
            "user_defined_sql_supress_warnings",
            "uss_pipe_directory",
            "utility_id",
            "value_compression",
            "warning_count",
            "without_prompting",
            "write_mode",
            "xml_column_as_lob",
        }
        required = {
            "batch_pipe_system_id",
            "ccsid",
            "create_table_statement",
            "current_output_link_type",
            "database",
            "delete_statement",
            "directory_for_data_and_command_files",
            "drop_table_statement",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "generate_create_statement_distribute_by_hash_key_column_names",
            "hfs_file_directory",
            "higher_port_number",
            "hostname",
            "insert_statement",
            "interval_between_retries",
            "isolation_level",
            "library_used_to_copy",
            "loaded_data_copy_location",
            "lock_wait_time",
            "lower_port_number",
            "message_file",
            "number_of_retries",
            "output_acp_should_hide",
            "password",
            "port",
            "prefix_for_expression_columns",
            "table_action",
            "table_name",
            "temporary_work_table_name",
            "total_number_of_player_processes",
            "transfer_to",
            "truncate_table_statement",
            "unique_key_column",
            "update_statement",
            "user_defined_sql",
            "user_defined_sql_file_name",
            "user_defined_sql_statements",
            "username",
            "uss_pipe_directory",
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
        props = {
            "reject_condition_row_not_updated",
            "reject_condition_sql_error",
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
