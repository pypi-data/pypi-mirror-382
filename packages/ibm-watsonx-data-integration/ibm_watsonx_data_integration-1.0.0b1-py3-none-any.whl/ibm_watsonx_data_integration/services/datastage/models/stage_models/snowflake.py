import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.snowflake_connection import SnowflakeConn
from ibm_watsonx_data_integration.services.datastage.models.enums import SNOWFLAKE
from pydantic import Field
from typing import ClassVar


class snowflake(BaseStage):

    op_name: ClassVar[str] = "SnowflakeConnectorPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/SnowflakeConnectorPX.svg"
    label: ClassVar[str] = "Snowflake"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: SnowflakeConn = SnowflakeConn()
    add_procedure_return_value_to_schema: bool | None = Field(False, alias="add_proccode_column")
    batch_size: int | None = Field(2000, alias="batch_size")
    before_sql: str | None = Field(None, alias="static_before_sql")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: SNOWFLAKE.BufModeRonly | None = Field(SNOWFLAKE.BufModeRonly.default, alias="buf_mode_ronly")
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: SNOWFLAKE.BufferingMode | None = Field(SNOWFLAKE.BufferingMode.default, alias="buf_mode")
    byte_limit: str | None = Field(None, alias="byte_limit")
    call_procedure_statement: str | None = Field(None, alias="call_statement")
    collecting: SNOWFLAKE.Collecting | None = Field(SNOWFLAKE.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: SNOWFLAKE.CombinabilityMode | None = Field(
        SNOWFLAKE.CombinabilityMode.auto, alias="combinability"
    )
    conn_query_timeout: int | None = Field(None, alias="conn_query_timeout")
    create_statement: str | None = Field(None, alias="create_statement")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    decimal_rounding_mode: SNOWFLAKE.DecimalRoundingMode | None = Field(
        SNOWFLAKE.DecimalRoundingMode.floor, alias="decimal_rounding_mode"
    )
    default_maximum_length_for_columns: int | None = Field(20000, alias="default_max_string_binary_precision")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    ds_auto_commit_mode: SNOWFLAKE.DSAutoCommitMode | None = Field(
        SNOWFLAKE.DSAutoCommitMode.enable, alias="_auto_commit_mode"
    )
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
    ds_begin_end_sql: bool | None = Field(False, alias="_begin_end_sql")
    ds_begin_sql: str | None = Field(None, alias="_begin_sql")
    ds_custom_statements: str | None = Field(None, alias="_custom_statements")
    ds_custom_statements_read_from_file_custom: bool | None = Field(
        False, alias="_custom_statements._read_from_file_custom"
    )
    ds_delete_statement: str = Field(None, alias="_delete_statement")
    ds_delete_statement_read_from_file_delete: bool | None = Field(
        False, alias="_delete_statement._read_from_file_delete"
    )
    ds_enable_partitioned_reads: bool | None = Field(False, alias="_enable_partitioned_reads")
    ds_enable_quoted_ids: bool | None = Field(False, alias="_enable_quoted_ids")
    ds_end_of_wave: SNOWFLAKE.DSEndOfWave | None = Field(SNOWFLAKE.DSEndOfWave._no, alias="_end_of_wave")
    ds_end_sql: str | None = Field(None, alias="_end_sql")
    ds_generate_sql: bool | None = Field(True, alias="_generate_sql")
    ds_insert_statement: str = Field(None, alias="_insert_statement")
    ds_insert_statement_read_from_file_insert: bool | None = Field(
        False, alias="_insert_statement._read_from_file_insert"
    )
    ds_isolation_level: SNOWFLAKE.DSIsolationLevel | None = Field(
        SNOWFLAKE.DSIsolationLevel.default, alias="_isolation_level"
    )
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    ds_limit_rows_limit: int | None = Field(None, alias="_limit_rows._limit")
    ds_load_from_file_azure_encryption: SNOWFLAKE.DSLoadFromFileAzureEncryption | None = Field(
        SNOWFLAKE.DSLoadFromFileAzureEncryption.none, alias="_load_from_file._azure._encryption"
    )
    ds_load_from_file_azure_file_format_name: str = Field(None, alias="_load_from_file._azure._file_format_name")
    ds_load_from_file_azure_file_name: str = Field(None, alias="_load_from_file._azure._file_name")
    ds_load_from_file_azure_master_key: str | None = Field(None, alias="_load_from_file._azure._master_key")
    ds_load_from_file_azure_sastoken: str = Field(None, alias="_load_from_file._azure._sastoken")
    ds_load_from_file_azure_storage_area_name: str = Field(None, alias="_load_from_file._azure._storage_area_name")
    ds_load_from_file_azure_use_existing_file_format: bool = Field(
        True, alias="_load_from_file._azure._use_existing_file_format"
    )
    ds_load_from_file_copy_options_on_error: SNOWFLAKE.DSLoadFromFileCopyOptionsOnError | None = Field(
        SNOWFLAKE.DSLoadFromFileCopyOptionsOnError.abort_statement, alias="_load_from_file._copy_options._on_error"
    )
    ds_load_from_file_copy_options_other_copy_options: str | None = Field(
        None, alias="_load_from_file._copy_options._other_copy_options"
    )
    ds_load_from_file_create_staging_area: bool | None = Field(True, alias="_load_from_file._create_staging_area")
    ds_load_from_file_credentials_file_name: str | None = Field(None, alias="_load_from_file._credentials_file_name")
    ds_load_from_file_delete_staging_area: bool | None = Field(False, alias="_load_from_file._delete_staging_area")
    ds_load_from_file_directory_path: str = Field(None, alias="_load_from_file._directory_path")
    ds_load_from_file_file_format: SNOWFLAKE.DSLoadFromFileFileFormat | None = Field(
        SNOWFLAKE.DSLoadFromFileFileFormat.csv, alias="_load_from_file._file_format"
    )
    ds_load_from_file_file_format_binary_as_text: bool | None = Field(
        False, alias="_load_from_file._file_format._binary_as_text"
    )
    ds_load_from_file_file_format_compression: SNOWFLAKE.DSLoadFromFileFileFormatCompression | None = Field(
        SNOWFLAKE.DSLoadFromFileFileFormatCompression.none, alias="_load_from_file._file_format._compression"
    )
    ds_load_from_file_file_format_date_format: str | None = Field(
        None, alias="_load_from_file._file_format._date_format"
    )
    ds_load_from_file_file_format_encoding: str | None = Field(None, alias="_load_from_file._file_format._encoding")
    ds_load_from_file_file_format_field_delimiter: str | None = Field(
        None, alias="_load_from_file._file_format._field_delimiter"
    )
    ds_load_from_file_file_format_other_format_options: str | None = Field(
        None, alias="_load_from_file._file_format._other_format_options"
    )
    ds_load_from_file_file_format_record_delimiter: str | None = Field(
        None, alias="_load_from_file._file_format._record_delimiter"
    )
    ds_load_from_file_file_format_skip_byte_order_mark: bool | None = Field(
        False, alias="_load_from_file._file_format._skip_byte_order_mark"
    )
    ds_load_from_file_file_format_snappy_compression: bool | None = Field(
        False, alias="_load_from_file._file_format._snappy_compression"
    )
    ds_load_from_file_file_format_time_format: str | None = Field(
        None, alias="_load_from_file._file_format._time_format"
    )
    ds_load_from_file_file_format_timestamp_format: str | None = Field(
        None, alias="_load_from_file._file_format._timestamp_format"
    )
    ds_load_from_file_gcs_file_format: str = Field(None, alias="_load_from_file._gcs._file_format")
    ds_load_from_file_gcs_file_name: str = Field(None, alias="_load_from_file._gcs._file_name")
    ds_load_from_file_gcs_storage_integration: str = Field(None, alias="_load_from_file._gcs._storage_integration")
    ds_load_from_file_gcs_use_existing_file_format: bool = Field(
        True, alias="_load_from_file._gcs._use_existing_file_format"
    )
    ds_load_from_file_max_file_size: int | None = Field(64, alias="_load_from_file._max_file_size")
    ds_load_from_file_purge_copied_files: bool | None = Field(True, alias="_load_from_file._purge_copied_files")
    ds_load_from_file_s3_access_key: str = Field(None, alias="_load_from_file._s3._access_key")
    ds_load_from_file_s3_bucket_name: str = Field(None, alias="_load_from_file._s3._bucket_name")
    ds_load_from_file_s3_encryption: SNOWFLAKE.DSLoadFromFileS3Encryption | None = Field(
        SNOWFLAKE.DSLoadFromFileS3Encryption.none, alias="_load_from_file._s3._encryption"
    )
    ds_load_from_file_s3_file_name: str = Field(None, alias="_load_from_file._s3._file_name")
    ds_load_from_file_s3_secret_key: str = Field(None, alias="_load_from_file._s3._secret_key")
    ds_load_from_file_staging_area_format_encoding: str | None = Field(
        "UTF-8", alias="_load_from_file._staging_area_format._encoding"
    )
    ds_load_from_file_staging_area_format_escape_character: str | None = Field(
        "", alias="_load_from_file._staging_area_format._escape_character"
    )
    ds_load_from_file_staging_area_format_field_delimiter: str | None = Field(
        ",", alias="_load_from_file._staging_area_format._field_delimiter"
    )
    ds_load_from_file_staging_area_format_null_value: str | None = Field(
        "", alias="_load_from_file._staging_area_format._null_value"
    )
    ds_load_from_file_staging_area_format_other_file_format_options: str | None = Field(
        "", alias="_load_from_file._staging_area_format._other_file_format_options"
    )
    ds_load_from_file_staging_area_format_quotes: SNOWFLAKE.DSLoadFromFileStagingAreaFormatQuotes | None = Field(
        SNOWFLAKE.DSLoadFromFileStagingAreaFormatQuotes.none, alias="_load_from_file._staging_area_format._quotes"
    )
    ds_load_from_file_staging_area_format_record_delimiter: str | None = Field(
        "<NL>", alias="_load_from_file._staging_area_format._record_delimiter"
    )
    ds_load_from_file_staging_area_name: str = Field(None, alias="_load_from_file._staging_area_name")
    ds_load_from_file_staging_area_type: SNOWFLAKE.DSLoadFromFileStagingAreaType | None = Field(
        SNOWFLAKE.DSLoadFromFileStagingAreaType.internal_location, alias="_load_from_file._staging_area_type"
    )
    ds_load_from_file_use_credentials_file: bool | None = Field(False, alias="_load_from_file._use_credentials_file")
    ds_read_mode: int | None = Field(0, alias="_read_mode")
    ds_record_count: int | None = Field(2000, alias="_record_count")
    ds_record_ordering: SNOWFLAKE.DSRecordOrdering | None = Field(
        SNOWFLAKE.DSRecordOrdering.zero, alias="_record_ordering"
    )
    ds_record_ordering_properties: list | None = Field([], alias="_record_ordering_properties")
    ds_run_end_sql_if_no_records_processed: bool | None = Field(False, alias="_run_end_sql_if_no_records_processed")
    ds_select_statement: str = Field(None, alias="_select_statement")
    ds_select_statement_other_clause: str | None = Field(None, alias="_select_statement._other_clause")
    ds_select_statement_read_from_file_select: bool | None = Field(
        False, alias="_select_statement._read_from_file_select"
    )
    ds_select_statement_where_clause: str | None = Field(None, alias="_select_statement._where_clause")
    ds_session_array_size: int | None = Field(1, alias="_session._array_size")
    ds_session_batch_size: int | None = Field(2000, alias="_session._batch_size")
    ds_session_character_set_for_non_unicode_columns: SNOWFLAKE.DSSessionCharacterSetForNonUnicodeColumns | None = (
        Field(
            SNOWFLAKE.DSSessionCharacterSetForNonUnicodeColumns._default,
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
    ds_session_fetch_size: int | None = Field(0, alias="_session._fetch_size")
    ds_session_generate_all_columns_as_unicode: bool | None = Field(
        False, alias="_session._generate_all_columns_as_unicode"
    )
    ds_session_keep_conductor_connection_alive: bool | None = Field(
        True, alias="_session._keep_conductor_connection_alive"
    )
    ds_session_report_schema_mismatch: bool | None = Field(False, alias="_session._report_schema_mismatch")
    ds_table_action: SNOWFLAKE.DSTableAction = Field(SNOWFLAKE.DSTableAction._append, alias="_table_action")
    ds_table_action_generate_create_statement: bool | None = Field(
        True, alias="_table_action._generate_create_statement"
    )
    ds_table_action_generate_create_statement_create_statement: str = Field(
        None, alias="_table_action._generate_create_statement._create_statement"
    )
    ds_table_action_generate_create_statement_fail_on_error: bool | None = Field(
        True, alias="_table_action._generate_create_statement._fail_on_error"
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
    ds_update_statement: str = Field(None, alias="_update_statement")
    ds_update_statement_read_from_file_update: bool | None = Field(
        False, alias="_update_statement._read_from_file_update"
    )
    ds_use_datastage: bool | None = Field(True, alias="_use_datastage")
    ds_use_merge_statement: bool | None = Field(True, alias="_use_merge_statement")
    ds_write_mode: SNOWFLAKE.DSWriteMode | None = Field(SNOWFLAKE.DSWriteMode.insert, alias="_write_mode")
    enable_after_sql: str | None = Field("", alias="before_after.after")
    enable_after_sql_node: str | None = Field("", alias="before_after.after_node")
    enable_before_sql: str | None = Field("", alias="before_after.before")
    enable_before_sql_node: str | None = Field("", alias="before_after.before_node")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    error_warning: str | None = Field(None, alias="error_warning")
    execution_mode: SNOWFLAKE.ExecutionMode | None = Field(SNOWFLAKE.ExecutionMode.default_par, alias="execmode")
    existing_table_action: SNOWFLAKE.ExistingTableAction | None = Field(
        SNOWFLAKE.ExistingTableAction.append, alias="existing_table_action"
    )
    fail_on_error_after_partition_sql: bool | None = Field(None, alias="static_after_partition_sql_fail_on_error")
    fail_on_error_after_sql: bool | None = Field(True, alias="before_after.after.fail_on_error")
    fail_on_error_after_sql_node: bool | None = Field(True, alias="before_after.after_node.fail_on_error")
    fail_on_error_before_partition_sql: bool | None = Field(None, alias="static_before_partition_sql_fail_on_error")
    fail_on_error_before_sql: bool | None = Field(None, alias="static_before_sql_fail_on_error")
    fail_on_error_before_sql: bool | None = Field(True, alias="before_after.before.fail_on_error")
    fail_on_error_before_sql_node: bool | None = Field(True, alias="before_after.before_node.fail_on_error")
    fatal_error: str | None = Field(None, alias="error_fatal")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    forward_row_data: bool | None = Field(False, alias="forward_row_data")
    generate_unicode_type_columns: bool | None = Field(False, alias="generate_unicode_columns")
    has_reference_output: bool | None = Field(False, alias="has_ref_output")
    has_reject_output: bool | None = Field(False, alias="has_reject_output")
    hide: bool | None = Field(False, alias="hide")
    hostname_or_ip_address: str | None = Field("@account_name@.snowflakecomputing.com", alias="host")
    infer_schema: bool | None = Field(True, alias="rcp")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    is_reject_output: bool | None = Field(False, alias="is_reject_output")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    key_column_names: str | None = Field(None, alias="key_column_names")
    lookup_type: SNOWFLAKE.LookupType | None = Field(SNOWFLAKE.LookupType.empty, alias="lookup_type")
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
    partition_after_sql: str | None = Field(None, alias="static_after_partition_sql")
    partition_before_sql: str | None = Field(None, alias="static_before_partition_sql")
    partition_type: SNOWFLAKE.PartitionType | None = Field(SNOWFLAKE.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    port: int | None = Field(443, alias="port")
    preserve_partitioning: SNOWFLAKE.PreservePartitioning | None = Field(
        SNOWFLAKE.PreservePartitioning.default_propagate, alias="preserve"
    )
    proc_param_properties: list | None = Field([], alias="procParamProperties")
    procedure_name: str | None = Field(None, alias="procedure_name")
    push_filters: str | None = Field(None, alias="push_filters")
    pushed_filters: str | None = Field(None, alias="pushed_filters")
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    read_method: SNOWFLAKE.ReadMethod | None = Field(SNOWFLAKE.ReadMethod.general, alias="read_mode")
    reject_condition_row_is_rejected: bool | None = Field(False, alias="reject_condition_row_is_rejected")
    reject_condition_row_not_deleted: bool | None = Field(False, alias="reject_condition_row_not_deleted")
    reject_condition_row_not_inserted: bool | None = Field(False, alias="reject_condition_row_not_inserted")
    reject_condition_row_not_updated: bool | None = Field(False, alias="reject_condition_row_not_updated")
    reject_condition_sql_error: bool | None = Field(False, alias="reject_condition_sql_error")
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_from_link: int | None = Field(None, alias="reject_from_link")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: SNOWFLAKE.RejectUses | None = Field(SNOWFLAKE.RejectUses.rows, alias="reject_uses")
    rejected_filters: str | None = Field(None, alias="rejected_filters")
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    sampling_percentage: str | None = Field(None, alias="sampling_percentage")
    sampling_seed: int | None = Field(None, alias="sampling_seed")
    sampling_type: SNOWFLAKE.SamplingType | None = Field(SNOWFLAKE.SamplingType.none, alias="sampling_type")
    schema_name: str | None = Field(None, alias="schema_name")
    select_statement: str = Field(None, alias="select_statement")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: SNOWFLAKE.KeyColSelect | None = Field(SNOWFLAKE.KeyColSelect.default, alias="keyColSelect")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    static_statement: str = Field(None, alias="static_statement")
    table_action: SNOWFLAKE.TableAction | None = Field(SNOWFLAKE.TableAction.append, alias="table_action")
    table_name: str = Field(None, alias="table_name")
    transform: str | None = Field("false", alias="transform")
    unique: bool | None = Field(None, alias="part_unique")
    update_statement: str | None = Field(None, alias="update_statement")
    user_defined_function: bool | None = Field(None, alias="user_defined_function")
    write_mode: SNOWFLAKE.WriteMode | None = Field(SNOWFLAKE.WriteMode.insert, alias="write_mode")

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
            include.add("ds_record_ordering_properties")
            if (((self.input_count and self.input_count > 1)) and (self.ds_record_ordering == 2))
            else exclude.add("ds_record_ordering_properties")
        )
        include.add("reject_uses") if (self.is_reject_output) else exclude.add("reject_uses")
        include.add("reject_number") if (self.is_reject_output) else exclude.add("reject_number")
        (
            include.add("reject_data_element_errorcode")
            if (self.is_reject_output)
            else exclude.add("reject_data_element_errorcode")
        )
        (
            include.add("reject_data_element_errortext")
            if (self.is_reject_output)
            else exclude.add("reject_data_element_errortext")
        )
        (
            include.add("reject_condition_sql_error")
            if (self.is_reject_output)
            else exclude.add("reject_condition_sql_error")
        )
        (
            include.add("reject_condition_row_not_inserted")
            if (self.is_reject_output)
            else exclude.add("reject_condition_row_not_inserted")
        )
        (
            include.add("reject_condition_row_not_updated")
            if (self.is_reject_output)
            else exclude.add("reject_condition_row_not_updated")
        )
        (
            include.add("reject_condition_row_not_deleted")
            if (self.is_reject_output)
            else exclude.add("reject_condition_row_not_deleted")
        )
        (
            include.add("reject_from_link")
            if (self.input_count and self.input_count > 1)
            else exclude.add("reject_from_link")
        )
        (
            include.add("reject_threshold")
            if (((self.reject_uses == "percent")) and (self.is_reject_output))
            else exclude.add("reject_threshold")
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
            include.add("ds_before_after_after_sql_node_fail_on_error")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node_fail_on_error")
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
        include.add("ds_end_sql") if (self.ds_begin_end_sql) else exclude.add("ds_end_sql")
        (
            include.add("ds_select_statement")
            if (not self.ds_generate_sql)
            else exclude.add("ds_select_statement")
        )
        (
            include.add("ds_enable_partitioned_reads")
            if (
                ((not self.ds_generate_sql))
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
            else exclude.add("ds_enable_partitioned_reads")
        )
        include.add("ds_begin_sql") if (self.ds_begin_end_sql) else exclude.add("ds_begin_sql")
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
            include.add("ds_before_after_before_sql_read_from_file_before_sql")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_read_from_file_before_sql")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("ds_run_end_sql_if_no_records_processed")
            if (self.ds_begin_end_sql)
            else exclude.add("ds_run_end_sql_if_no_records_processed")
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
            include.add("call_procedure_statement")
            if (
                ((not self.table_name))
                and (not self.select_statement)
                and (not self.procedure_name)
                and (

                        self.read_method
                        and (
                            (hasattr(self.read_method, "value") and self.read_method.value == "call_statement")
                            or (self.read_method == "call_statement")
                        )

                )
            )
            else exclude.add("call_procedure_statement")
        )
        (
            include.add("select_statement")
            if (
                ((not self.schema_name))
                and (not self.table_name)
                and (not self.procedure_name)
                and (not self.call_procedure_statement)
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
                and (not self.procedure_name)
                and (not self.call_procedure_statement)
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
            include.add("forward_row_data")
            if (
                ((not self.select_statement))
                and (not self.table_name)
                and (
                    (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                or (self.read_method == "call")
                            )
                        )
                    )
                    or (

                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call_statement")
                                or (self.read_method == "call_statement")
                            )

                    )
                )
            )
            else exclude.add("forward_row_data")
        )
        (
            include.add("add_procedure_return_value_to_schema")
            if (
                ((not self.select_statement))
                and (not self.table_name)
                and (
                    (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                or (self.read_method == "call")
                            )
                        )
                    )
                    or (

                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call_statement")
                                or (self.read_method == "call_statement")
                            )

                    )
                )
            )
            else exclude.add("add_procedure_return_value_to_schema")
        )
        (
            include.add("schema_name")
            if (
                ((not self.select_statement))
                and (not self.call_procedure_statement)
                and (
                    (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                or (self.read_method == "call")
                            )
                        )
                    )
                    or (

                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "general")
                                or (self.read_method == "general")
                            )

                    )
                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("error_warning")
            if (
                ((not self.select_statement))
                and (not self.table_name)
                and (
                    (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                or (self.read_method == "call")
                            )
                        )
                    )
                    or (

                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call_statement")
                                or (self.read_method == "call_statement")
                            )

                    )
                )
            )
            else exclude.add("error_warning")
        )
        (
            include.add("user_defined_function")
            if (

                    (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                or (self.read_method == "call")
                            )
                        )
                    )
                    or (

                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call_statement")
                                or (self.read_method == "call_statement")
                            )

                    )

            )
            else exclude.add("user_defined_function")
        )
        (
            include.add("procedure_name")
            if (
                ((not self.call_procedure_statement))
                and (not self.select_statement)
                and (not self.table_name)
                and (

                        self.read_method
                        and (
                            (hasattr(self.read_method, "value") and self.read_method.value == "call")
                            or (self.read_method == "call")
                        )

                )
            )
            else exclude.add("procedure_name")
        )
        (
            include.add("fatal_error")
            if (
                ((not self.select_statement))
                and (not self.table_name)
                and (
                    (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                or (self.read_method == "call")
                            )
                        )
                    )
                    or (

                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "call_statement")
                                or (self.read_method == "call_statement")
                            )

                    )
                )
            )
            else exclude.add("fatal_error")
        )
        (
            include.add("row_limit")
            if (

                    (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value != "call")
                                or (self.read_method != "call")
                            )
                        )
                    )
                    and (

                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value != "call_statement")
                                or (self.read_method != "call_statement")
                            )

                    )

            )
            else exclude.add("row_limit")
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
            include.add("call_procedure_statement")
            if (

                    (
                        (
                            (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                            and (
                                ((not self.select_statement))
                                or ((self.select_statement and "#" in str(self.select_statement)))
                            )
                            and (
                                ((not self.procedure_name))
                                or ((self.procedure_name and "#" in str(self.procedure_name)))
                            )
                            and (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (
                                                hasattr(self.read_method, "value")
                                                and self.read_method.value == "call_statement"
                                            )
                                            or (self.read_method == "call_statement")
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
            else exclude.add("call_procedure_statement")
        )
        (
            include.add("select_statement")
            if (

                    (
                        (
                            (((not self.schema_name)) or ((self.schema_name and "#" in str(self.schema_name))))
                            and (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                            and (
                                ((not self.procedure_name))
                                or ((self.procedure_name and "#" in str(self.procedure_name)))
                            )
                            and (
                                ((not self.call_procedure_statement))
                                or ((self.call_procedure_statement and "#" in str(self.call_procedure_statement)))
                            )
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
                                ((not self.procedure_name))
                                or ((self.procedure_name and "#" in str(self.procedure_name)))
                            )
                            and (
                                ((not self.call_procedure_statement))
                                or ((self.call_procedure_statement and "#" in str(self.call_procedure_statement)))
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
            include.add("forward_row_data")
            if (

                    (
                        (
                            (
                                ((not self.select_statement))
                                or ((self.select_statement and "#" in str(self.select_statement)))
                            )
                            and (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                            and (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                            or (self.read_method == "call")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_method
                                        and (
                                            (
                                                hasattr(self.read_method, "value")
                                                and self.read_method.value == "call_statement"
                                            )
                                            or (self.read_method == "call_statement")
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
            else exclude.add("forward_row_data")
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
            include.add("add_procedure_return_value_to_schema")
            if (

                    (
                        (
                            (
                                ((not self.select_statement))
                                or ((self.select_statement and "#" in str(self.select_statement)))
                            )
                            and (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                            and (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                            or (self.read_method == "call")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_method
                                        and (
                                            (
                                                hasattr(self.read_method, "value")
                                                and self.read_method.value == "call_statement"
                                            )
                                            or (self.read_method == "call_statement")
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
            else exclude.add("add_procedure_return_value_to_schema")
        )
        (
            include.add("ds_end_sql")
            if (

                    (
                        (
                            (
                                ((self.ds_begin_end_sql))
                                or ((self.ds_begin_end_sql and "#" in str(self.ds_begin_end_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_end_sql")
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
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
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
            else exclude.add("ds_enable_partitioned_reads")
        )
        (
            include.add("ds_begin_sql")
            if (

                    (
                        (
                            (
                                ((self.ds_begin_end_sql))
                                or ((self.ds_begin_end_sql and "#" in str(self.ds_begin_end_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_begin_sql")
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
                                ((not self.call_procedure_statement))
                                or ((self.call_procedure_statement and "#" in str(self.call_procedure_statement)))
                            )
                            and (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                            or (self.read_method == "call")
                                        )
                                    )
                                )
                                or (
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
            include.add("error_warning")
            if (

                    (
                        (
                            (
                                ((not self.select_statement))
                                or ((self.select_statement and "#" in str(self.select_statement)))
                            )
                            and (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                            and (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                            or (self.read_method == "call")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_method
                                        and (
                                            (
                                                hasattr(self.read_method, "value")
                                                and self.read_method.value == "call_statement"
                                            )
                                            or (self.read_method == "call_statement")
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
            else exclude.add("error_warning")
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
            include.add("user_defined_function")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                            or (self.read_method == "call")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_method
                                        and (
                                            (
                                                hasattr(self.read_method, "value")
                                                and self.read_method.value == "call_statement"
                                            )
                                            or (self.read_method == "call_statement")
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
            else exclude.add("user_defined_function")
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
            include.add("procedure_name")
            if (

                    (
                        (
                            (
                                ((not self.call_procedure_statement))
                                or ((self.call_procedure_statement and "#" in str(self.call_procedure_statement)))
                            )
                            and (
                                ((not self.select_statement))
                                or ((self.select_statement and "#" in str(self.select_statement)))
                            )
                            and (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                            and (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                            or (self.read_method == "call")
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
            else exclude.add("procedure_name")
        )
        (
            include.add("fatal_error")
            if (

                    (
                        (
                            (
                                ((not self.select_statement))
                                or ((self.select_statement and "#" in str(self.select_statement)))
                            )
                            and (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                            and (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value == "call")
                                            or (self.read_method == "call")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_method
                                        and (
                                            (
                                                hasattr(self.read_method, "value")
                                                and self.read_method.value == "call_statement"
                                            )
                                            or (self.read_method == "call_statement")
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
            else exclude.add("fatal_error")
        )
        (
            include.add("row_limit")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        (
                                            (
                                                self.read_method
                                                and (
                                                    (
                                                        hasattr(self.read_method, "value")
                                                        and self.read_method.value != "call"
                                                    )
                                                    or (self.read_method != "call")
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
                                    and (
                                        (
                                            (
                                                self.read_method
                                                and (
                                                    (
                                                        hasattr(self.read_method, "value")
                                                        and self.read_method.value != "call_statement"
                                                    )
                                                    or (self.read_method != "call_statement")
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
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("row_limit")
        )
        (
            include.add("lookup_type")
            if (((((self.has_reference_output)))) and (self.ds_use_datastage))
            else exclude.add("lookup_type")
        )
        (
            include.add("ds_run_end_sql_if_no_records_processed")
            if (

                    (
                        (
                            (
                                ((self.ds_begin_end_sql))
                                or ((self.ds_begin_end_sql and "#" in str(self.ds_begin_end_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_run_end_sql_if_no_records_processed")
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

        include.add("fail_on_error_before_sql") if (()) else exclude.add("fail_on_error_before_sql")
        include.add("partition_before_sql") if (()) else exclude.add("partition_before_sql")
        include.add("fail_on_error_after_partition_sql") if (()) else exclude.add("fail_on_error_after_partition_sql")
        include.add("before_sql") if (()) else exclude.add("before_sql")
        include.add("fail_on_error_before_partition_sql") if (()) else exclude.add("fail_on_error_before_partition_sql")
        include.add("partition_after_sql") if (()) else exclude.add("partition_after_sql")
        include.add("pushed_filters") if (not self.ds_use_datastage) else exclude.add("pushed_filters")
        include.add("ds_record_count") if (self.ds_use_datastage) else exclude.add("ds_record_count")
        (
            include.add("ds_session_keep_conductor_connection_alive")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_keep_conductor_connection_alive")
        )
        include.add("ds_begin_end_sql") if (self.ds_use_datastage) else exclude.add("ds_begin_end_sql")
        include.add("rejected_filters") if (not self.ds_use_datastage) else exclude.add("rejected_filters")
        include.add("ds_auto_commit_mode") if (self.ds_use_datastage) else exclude.add("ds_auto_commit_mode")
        (
            include.add("ds_session_fetch_size")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_fetch_size")
        )
        include.add("sampling_type") if (not self.ds_use_datastage) else exclude.add("sampling_type")
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
            include.add("fail_on_error_before_sql")
            if (not self.ds_use_datastage)
            else exclude.add("fail_on_error_before_sql")
        )
        include.add("read_method") if (not self.ds_use_datastage) else exclude.add("read_method")
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
        include.add("ds_isolation_level") if (self.ds_use_datastage) else exclude.add("ds_isolation_level")
        (
            include.add("ds_session_report_schema_mismatch")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_report_schema_mismatch")
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
        include.add("transform") if (not self.ds_use_datastage) else exclude.add("transform")
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
            include.add("enable_before_sql_node")
            if (not self.ds_use_datastage)
            else exclude.add("enable_before_sql_node")
        )
        include.add("ds_end_of_wave") if (self.ds_use_datastage) else exclude.add("ds_end_of_wave")
        include.add("ds_generate_sql") if (self.ds_use_datastage) else exclude.add("ds_generate_sql")
        include.add("ds_before_after") if (self.ds_use_datastage) else exclude.add("ds_before_after")
        (
            include.add("decimal_rounding_mode")
            if (not self.ds_use_datastage)
            else exclude.add("decimal_rounding_mode")
        )
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
            include.add("reject_threshold")
            if (((self.reject_uses == "percent")) and (self.is_reject_output))
            else exclude.add("reject_threshold")
        )
        (
            include.add("runtime_column_propagation")
            if (
                ((not self.enable_schemaless_design))
                and (

                        self.read_method
                        and (
                            (hasattr(self.read_method, "value") and self.read_method.value != "call")
                            or (self.read_method != "call")
                        )

                )
                and (

                        self.read_method
                        and (
                            (hasattr(self.read_method, "value") and self.read_method.value != "call_statement")
                            or (self.read_method != "call_statement")
                        )

                )
            )
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
        include.add("conn_query_timeout") if (()) else exclude.add("conn_query_timeout")
        include.add("defer_credentials") if (()) else exclude.add("defer_credentials")
        include.add("hostname_or_ip_address") if (()) else exclude.add("hostname_or_ip_address")
        include.add("port") if (()) else exclude.add("port")
        (
            include.add("ds_begin_sql")
            if (self.ds_begin_end_sql == "true" or self.ds_begin_end_sql)
            else exclude.add("ds_begin_sql")
        )
        (
            include.add("procedure_name")
            if (not self.call_procedure_statement)
            and (not self.select_statement)
            and (not self.table_name)
            and (
                self.read_method
                and (
                    (hasattr(self.read_method, "value") and self.read_method.value == "call")
                    or (self.read_method == "call")
                )
            )
            else exclude.add("procedure_name")
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
            include.add("ds_end_sql")
            if (self.ds_begin_end_sql == "true" or self.ds_begin_end_sql)
            else exclude.add("ds_end_sql")
        )
        (
            include.add("ds_select_statement_other_clause")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_select_statement_other_clause")
        )
        (
            include.add("fatal_error")
            if (not self.select_statement)
            and (not self.table_name)
            and (
                self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call" in str(self.read_method.value)
                    )
                    or ("call" in str(self.read_method))
                )
                and self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call_statement" in str(self.read_method.value)
                    )
                    or ("call_statement" in str(self.read_method))
                )
            )
            else exclude.add("fatal_error")
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
            include.add("error_warning")
            if (not self.select_statement)
            and (not self.table_name)
            and (
                self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call" in str(self.read_method.value)
                    )
                    or ("call" in str(self.read_method))
                )
                and self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call_statement" in str(self.read_method.value)
                    )
                    or ("call_statement" in str(self.read_method))
                )
            )
            else exclude.add("error_warning")
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
            include.add("call_procedure_statement")
            if (not self.table_name)
            and (not self.select_statement)
            and (not self.procedure_name)
            and (
                self.read_method
                and (
                    (hasattr(self.read_method, "value") and self.read_method.value == "call_statement")
                    or (self.read_method == "call_statement")
                )
            )
            else exclude.add("call_procedure_statement")
        )
        (
            include.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
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
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
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
            else exclude.add("ds_enable_partitioned_reads")
        )
        (
            include.add("row_limit")
            if (
                self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call" not in str(self.read_method.value)
                    )
                    or ("call" not in str(self.read_method))
                )
                and self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call_statement" not in str(self.read_method.value)
                    )
                    or ("call_statement" not in str(self.read_method))
                )
            )
            else exclude.add("row_limit")
        )
        (
            include.add("lookup_type")
            if (self.has_reference_output == "true" or self.has_reference_output)
            else exclude.add("lookup_type")
        )
        (
            include.add("user_defined_function")
            if (
                self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call" in str(self.read_method.value)
                    )
                    or ("call" in str(self.read_method))
                )
                and self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call_statement" in str(self.read_method.value)
                    )
                    or ("call_statement" in str(self.read_method))
                )
            )
            else exclude.add("user_defined_function")
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
            include.add("ds_run_end_sql_if_no_records_processed")
            if (self.ds_begin_end_sql == "true" or self.ds_begin_end_sql)
            else exclude.add("ds_run_end_sql_if_no_records_processed")
        )
        (
            include.add("ds_before_after_before_sql_node_fail_on_error")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node_fail_on_error")
        )
        (
            include.add("schema_name")
            if (not self.select_statement)
            and (not self.call_procedure_statement)
            and (
                self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call" in str(self.read_method.value)
                    )
                    or ("call" in str(self.read_method))
                )
                and self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "general" in str(self.read_method.value)
                    )
                    or ("general" in str(self.read_method))
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
            and (not self.procedure_name)
            and (not self.call_procedure_statement)
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
            and (not self.procedure_name)
            and (not self.call_procedure_statement)
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
            include.add("add_procedure_return_value_to_schema")
            if (not self.select_statement)
            and (not self.table_name)
            and (
                self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call" in str(self.read_method.value)
                    )
                    or ("call" in str(self.read_method))
                )
                and self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call_statement" in str(self.read_method.value)
                    )
                    or ("call_statement" in str(self.read_method))
                )
            )
            else exclude.add("add_procedure_return_value_to_schema")
        )
        (
            include.add("forward_row_data")
            if (not self.select_statement)
            and (not self.table_name)
            and (
                self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call" in str(self.read_method.value)
                    )
                    or ("call" in str(self.read_method))
                )
                and self.read_method
                and (
                    (
                        hasattr(self.read_method, "value")
                        and self.read_method.value
                        and "call_statement" in str(self.read_method.value)
                    )
                    or ("call_statement" in str(self.read_method))
                )
            )
            else exclude.add("forward_row_data")
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
            include.add("ds_load_from_file_staging_area_format_quotes")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_quotes")
        )
        (
            include.add("ds_load_from_file_s3_encryption")
            if (
                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_s3_encryption")
        )
        (
            include.add("ds_begin_end_sql")
            if (((self.ds_write_mode == "insert")) or (not self.ds_use_merge_statement))
            else exclude.add("ds_begin_end_sql")
        )
        (
            include.add("ds_load_from_file_azure_sastoken")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_azure")
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_azure_sastoken")
        )
        (
            include.add("ds_table_action_generate_drop_statement")
            if (
                (((self.ds_write_mode == "insert")) or ((self.ds_write_mode == "load_from_file")))
                and (self.ds_table_action == "_replace")
            )
            else exclude.add("ds_table_action_generate_drop_statement")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_fail_on_error")
            if (
                (((self.ds_write_mode == "insert")) or ((self.ds_write_mode == "load_from_file")))
                and (self.ds_table_action == "_truncate")
            )
            else exclude.add("ds_table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("ds_load_from_file_use_credentials_file")
            if (
                (((self.ds_load_from_file_staging_area_type == "external_s3")))
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_use_credentials_file")
        )
        (
            include.add("ds_update_statement_read_from_file_update")
            if (
                (((self.ds_write_mode == "insert_update")) or ((self.ds_write_mode == "update")))
                and (not self.ds_generate_sql)
            )
            else exclude.add("ds_update_statement_read_from_file_update")
        )
        (
            include.add("ds_load_from_file_staging_area_format_other_file_format_options")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_other_file_format_options")
        )
        (
            include.add("ds_table_action_generate_create_statement_create_statement")
            if (
                (((self.ds_write_mode == "insert")) or ((self.ds_write_mode == "load_from_file")))
                and (((self.ds_table_action == "_create")) or (self.ds_table_action == "_replace"))
                and (not self.ds_table_action_generate_create_statement)
            )
            else exclude.add("ds_table_action_generate_create_statement_create_statement")
        )
        (
            include.add("ds_load_from_file_staging_area_type")
            if (
                (((self.ds_write_mode == "load_from_file")))
                or (
                    (
                        ((self.ds_write_mode == "delete"))
                        or ((self.ds_write_mode == "delete_insert"))
                        or ((self.ds_write_mode == "insert_update"))
                        or ((self.ds_write_mode == "update"))
                    )
                    and (self.ds_use_merge_statement)
                )
            )
            else exclude.add("ds_load_from_file_staging_area_type")
        )
        (
            include.add("ds_session_batch_size")
            if (
                (((self.ds_write_mode == "custom")) or ((self.ds_write_mode == "insert")))
                or (
                    (((self.ds_write_mode == "delete")) or ((self.ds_write_mode == "update")))
                    and (not self.ds_use_merge_statement)
                )
            )
            else exclude.add("ds_session_batch_size")
        )
        (
            include.add("ds_load_from_file_max_file_size")
            if (
                (((self.ds_load_from_file_staging_area_type == "internal_location")))
                and (
                    (((self.ds_write_mode == "load_from_file")))
                    or (
                        (
                            ((self.ds_write_mode == "delete"))
                            or ((self.ds_write_mode == "delete_insert"))
                            or ((self.ds_write_mode == "insert_update"))
                            or ((self.ds_write_mode == "update"))
                        )
                        and (self.ds_use_merge_statement)
                    )
                )
            )
            else exclude.add("ds_load_from_file_max_file_size")
        )
        (
            include.add("ds_load_from_file_gcs_file_format")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_gcs")
                and (self.ds_load_from_file_gcs_use_existing_file_format)
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_gcs_file_format")
        )
        (
            include.add("ds_load_from_file_file_format_record_delimiter")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_record_delimiter")
        )
        (
            include.add("ds_load_from_file_azure_file_name")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_azure")
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_azure_file_name")
        )
        (
            include.add("ds_use_merge_statement")
            if (

                    ((self.ds_write_mode == "delete"))
                    or (self.ds_write_mode == "delete_insert")
                    or (self.ds_write_mode == "insert_update")
                    or (self.ds_write_mode == "update")

            )
            else exclude.add("ds_use_merge_statement")
        )
        (
            include.add("ds_load_from_file_gcs_use_existing_file_format")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_gcs")
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_gcs_use_existing_file_format")
        )
        (
            include.add("ds_load_from_file_file_format_encoding")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_encoding")
        )
        (
            include.add("ds_load_from_file_file_format_skip_byte_order_mark")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_skip_byte_order_mark")
        )
        (
            include.add("ds_load_from_file_s3_secret_key")
            if (
                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_s3_secret_key")
        )
        (
            include.add("ds_delete_statement_read_from_file_delete")
            if (
                (((self.ds_write_mode == "delete")) or ((self.ds_write_mode == "delete_insert")))
                and (not self.ds_generate_sql)
            )
            else exclude.add("ds_delete_statement_read_from_file_delete")
        )
        (
            include.add("ds_load_from_file_staging_area_format_encoding")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_encoding")
        )
        (
            include.add("ds_table_action_generate_truncate_statement")
            if (
                (((self.ds_write_mode == "insert")) or ((self.ds_write_mode == "load_from_file")))
                and (self.ds_table_action == "_truncate")
            )
            else exclude.add("ds_table_action_generate_truncate_statement")
        )
        (
            include.add("ds_load_from_file_s3_access_key")
            if (
                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_s3_access_key")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_truncate_statement")
            if (
                (((self.ds_write_mode == "insert")) or ((self.ds_write_mode == "load_from_file")))
                and (self.ds_table_action == "_truncate")
                and (not self.ds_table_action_generate_truncate_statement)
            )
            else exclude.add("ds_table_action_generate_truncate_statement_truncate_statement")
        )
        (
            include.add("ds_load_from_file_staging_area_name")
            if (

                    ((self.ds_load_from_file_staging_area_type == "external_azure"))
                    or (self.ds_load_from_file_staging_area_type == "external_gcs")
                    or (self.ds_load_from_file_staging_area_type == "external_s3")
                    or (self.ds_load_from_file_staging_area_type == "internal_location")

            )
            else exclude.add("ds_load_from_file_staging_area_name")
        )
        (
            include.add("ds_load_from_file_file_format_date_format")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_date_format")
        )
        (
            include.add("ds_update_statement")
            if (
                (((self.ds_write_mode == "insert_update")) or ((self.ds_write_mode == "update")))
                and (not self.ds_generate_sql)
            )
            else exclude.add("ds_update_statement")
        )
        (
            include.add("ds_load_from_file_file_format_timestamp_format")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_timestamp_format")
        )
        (
            include.add("ds_record_count")
            if (((self.ds_write_mode == "insert")) or (not self.ds_use_merge_statement))
            else exclude.add("ds_record_count")
        )
        (
            include.add("ds_load_from_file_file_format_field_delimiter")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_field_delimiter")
        )
        (
            include.add("ds_load_from_file_file_format_other_format_options")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_other_format_options")
        )
        (
            include.add("ds_load_from_file_file_format")
            if (
                (
                    (
                        ((self.ds_load_from_file_staging_area_type == "external_azure"))
                        or ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                    )
                    or ((self.ds_load_from_file_create_staging_area))
                )
                and (
                    ((self.ds_load_from_file_staging_area_type == "external_s3"))
                    or (not self.ds_load_from_file_azure_use_existing_file_format)
                    or (not self.ds_load_from_file_gcs_use_existing_file_format)
                )
            )
            else exclude.add("ds_load_from_file_file_format")
        )
        (
            include.add("ds_load_from_file_create_staging_area")
            if (

                    ((self.ds_load_from_file_staging_area_type == "external_azure"))
                    or (self.ds_load_from_file_staging_area_type == "external_gcs")
                    or (self.ds_load_from_file_staging_area_type == "external_s3")
                    or (self.ds_load_from_file_staging_area_type == "internal_location")

            )
            else exclude.add("ds_load_from_file_create_staging_area")
        )
        (
            include.add("ds_load_from_file_directory_path")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_directory_path")
        )
        (
            include.add("ds_auto_commit_mode")
            if (((self.ds_write_mode == "insert")) or (not self.ds_use_merge_statement))
            else exclude.add("ds_auto_commit_mode")
        )
        (
            include.add("ds_load_from_file_copy_options_other_copy_options")
            if (

                    ((self.ds_load_from_file_staging_area_type == "external_azure"))
                    or (self.ds_load_from_file_staging_area_type == "external_gcs")
                    or (self.ds_load_from_file_staging_area_type == "external_s3")
                    or (self.ds_load_from_file_staging_area_type == "internal_location")

            )
            else exclude.add("ds_load_from_file_copy_options_other_copy_options")
        )
        (
            include.add("ds_table_action")
            if (((self.ds_write_mode == "insert")) or (self.ds_write_mode == "load_from_file"))
            else exclude.add("ds_table_action")
        )
        (
            include.add("ds_load_from_file_file_format_snappy_compression")
            if (self.ds_load_from_file_file_format == "parquet")
            else exclude.add("ds_load_from_file_file_format_snappy_compression")
        )
        (
            include.add("ds_load_from_file_credentials_file_name")
            if (self.ds_load_from_file_use_credentials_file)
            else exclude.add("ds_load_from_file_credentials_file_name")
        )
        (
            include.add("ds_load_from_file_staging_area_format_field_delimiter")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_field_delimiter")
        )
        (
            include.add("ds_load_from_file_file_format_time_format")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_time_format")
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
            include.add("ds_load_from_file_staging_area_format_escape_character")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_escape_character")
        )
        (
            include.add("ds_load_from_file_purge_copied_files")
            if (

                    ((self.ds_load_from_file_staging_area_type == "external_azure"))
                    or (self.ds_load_from_file_staging_area_type == "external_gcs")
                    or (self.ds_load_from_file_staging_area_type == "external_s3")
                    or (self.ds_load_from_file_staging_area_type == "internal_location")

            )
            else exclude.add("ds_load_from_file_purge_copied_files")
        )
        (
            include.add("ds_delete_statement")
            if (
                (((self.ds_write_mode == "delete")) or ((self.ds_write_mode == "delete_insert")))
                and (not self.ds_generate_sql)
            )
            else exclude.add("ds_delete_statement")
        )
        (
            include.add("ds_load_from_file_copy_options_on_error")
            if (

                    ((self.ds_load_from_file_staging_area_type == "external_azure"))
                    or (self.ds_load_from_file_staging_area_type == "external_gcs")
                    or (self.ds_load_from_file_staging_area_type == "external_s3")
                    or (self.ds_load_from_file_staging_area_type == "internal_location")

            )
            else exclude.add("ds_load_from_file_copy_options_on_error")
        )
        (
            include.add("ds_load_from_file_file_format_compression")
            if (((self.ds_load_from_file_file_format == "avro")) or (self.ds_load_from_file_file_format == "csv"))
            else exclude.add("ds_load_from_file_file_format_compression")
        )
        (
            include.add("ds_load_from_file_azure_use_existing_file_format")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_azure")
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_azure_use_existing_file_format")
        )
        (
            include.add("ds_isolation_level")
            if (((self.ds_write_mode == "insert")) or (not self.ds_use_merge_statement))
            else exclude.add("ds_isolation_level")
        )
        (
            include.add("ds_session_report_schema_mismatch")
            if (
                (
                    (
                        ((self.ds_write_mode == "delete"))
                        or ((self.ds_write_mode == "delete_insert"))
                        or ((self.ds_write_mode == "insert_update"))
                        or ((self.ds_write_mode == "update"))
                    )
                    and ((not self.ds_use_merge_statement))
                    and ((self.ds_generate_sql))
                )
                or ((((self.ds_write_mode == "insert"))) and (self.ds_generate_sql))
            )
            else exclude.add("ds_session_report_schema_mismatch")
        )
        (
            include.add("ds_load_from_file_s3_file_name")
            if (
                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_s3_file_name")
        )
        (
            include.add("ds_load_from_file_staging_area_format_null_value")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_null_value")
        )
        (
            include.add("ds_load_from_file_file_format_binary_as_text")
            if (self.ds_load_from_file_file_format == "parquet")
            else exclude.add("ds_load_from_file_file_format_binary_as_text")
        )
        (
            include.add("ds_insert_statement_read_from_file_insert")
            if (
                (
                    ((self.ds_write_mode == "delete_insert"))
                    or ((self.ds_write_mode == "insert"))
                    or ((self.ds_write_mode == "insert_update"))
                )
                and (not self.ds_generate_sql)
            )
            else exclude.add("ds_insert_statement_read_from_file_insert")
        )
        (
            include.add("ds_load_from_file_azure_storage_area_name")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_azure")
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_azure_storage_area_name")
        )
        (
            include.add("ds_table_name")
            if (
                (((self.ds_write_mode == "insert_overwrite")) or ((self.ds_write_mode == "load_from_file")))
                or (self.ds_generate_sql)
                or (self.ds_use_merge_statement)
            )
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_load_from_file_staging_area_format_record_delimiter")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_record_delimiter")
        )
        (
            include.add("ds_table_action_generate_create_statement_fail_on_error")
            if (
                (((self.ds_write_mode == "insert")) or ((self.ds_write_mode == "load_from_file")))
                and (((self.ds_table_action == "_create")) or (self.ds_table_action == "_replace"))
            )
            else exclude.add("ds_table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("ds_load_from_file_azure_encryption")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_azure")
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_azure_encryption")
        )
        (
            include.add("ds_load_from_file_gcs_file_name")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_gcs")
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_gcs_file_name")
        )
        (
            include.add("ds_load_from_file_gcs_storage_integration")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_gcs")
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_gcs_storage_integration")
        )
        (
            include.add("ds_insert_statement")
            if (
                (
                    ((self.ds_write_mode == "delete_insert"))
                    or ((self.ds_write_mode == "insert"))
                    or ((self.ds_write_mode == "insert_update"))
                )
                and (not self.ds_generate_sql)
            )
            else exclude.add("ds_insert_statement")
        )
        (
            include.add("ds_table_action_generate_drop_statement_drop_statement")
            if (
                (((self.ds_write_mode == "insert")) or ((self.ds_write_mode == "load_from_file")))
                and (self.ds_table_action == "_replace")
                and (not self.ds_table_action_generate_drop_statement)
            )
            else exclude.add("ds_table_action_generate_drop_statement_drop_statement")
        )
        (
            include.add("ds_custom_statements_read_from_file_custom")
            if (self.ds_write_mode == "custom")
            else exclude.add("ds_custom_statements_read_from_file_custom")
        )
        (
            include.add("ds_load_from_file_s3_bucket_name")
            if (
                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_s3_bucket_name")
        )
        (
            include.add("ds_table_action_generate_drop_statement_fail_on_error")
            if (
                (((self.ds_write_mode == "insert")) or ((self.ds_write_mode == "load_from_file")))
                and (self.ds_table_action == "_replace")
            )
            else exclude.add("ds_table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("ds_load_from_file_delete_staging_area")
            if (
                (
                    ((self.ds_load_from_file_staging_area_type == "external_azure"))
                    or ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                    or ((self.ds_load_from_file_staging_area_type == "external_s3"))
                    or ((self.ds_load_from_file_staging_area_type == "internal_location"))
                )
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_delete_staging_area")
        )
        (
            include.add("ds_generate_sql")
            if (
                ((self.ds_write_mode == "insert"))
                or (((not self.ds_use_merge_statement)) and (self.ds_use_merge_statement))
            )
            else exclude.add("ds_generate_sql")
        )
        (
            include.add("ds_load_from_file_azure_file_format_name")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_azure")
                and (self.ds_load_from_file_azure_use_existing_file_format)
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_azure_file_format_name")
        )
        (
            include.add("ds_load_from_file_azure_master_key")
            if (
                (((self.ds_write_mode == "load_from_file")))
                and (self.ds_load_from_file_staging_area_type == "external_azure")
                and (self.ds_load_from_file_create_staging_area)
            )
            else exclude.add("ds_load_from_file_azure_master_key")
        )
        (
            include.add("ds_table_action_generate_create_statement")
            if (
                (((self.ds_write_mode == "insert")) or ((self.ds_write_mode == "load_from_file")))
                and (((self.ds_table_action == "_create")) or (self.ds_table_action == "_replace"))
            )
            else exclude.add("ds_table_action_generate_create_statement")
        )
        (
            include.add("ds_custom_statements")
            if (self.ds_write_mode == "custom")
            else exclude.add("ds_custom_statements")
        )
        (
            include.add("table_name")
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
            else exclude.add("table_name")
        )
        (
            include.add("create_statement")
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
            else exclude.add("create_statement")
        )
        (
            include.add("table_action")
            if (
                (
                    (
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "merge")
                                    or (self.write_mode == "merge")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "update_statement_table_action"
                                    )
                                    or (self.write_mode == "update_statement_table_action")
                                )
                            )
                        )
                    )
                )
                and (
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
            )
            else exclude.add("table_action")
        )
        (
            include.add("static_statement")
            if (
                ((not self.schema_name))
                and (not self.table_name)
                and (not self.update_statement)
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
            include.add("schema_name")
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
            else exclude.add("schema_name")
        )
        (
            include.add("key_column_names")
            if (
                (((not self.update_statement)) and ((not self.static_statement)))
                and (
                    (
                        (
                            (
                                self.existing_table_action
                                and (
                                    (
                                        hasattr(self.existing_table_action, "value")
                                        and self.existing_table_action.value == "append"
                                    )
                                    or (self.existing_table_action == "append")
                                )
                            )
                        )
                        or (
                            (
                                self.existing_table_action
                                and (
                                    (
                                        hasattr(self.existing_table_action, "value")
                                        and self.existing_table_action.value == "merge"
                                    )
                                    or (self.existing_table_action == "merge")
                                )
                            )
                        )
                        or (
                            (
                                self.existing_table_action
                                and (
                                    (
                                        hasattr(self.existing_table_action, "value")
                                        and self.existing_table_action.value == "update"
                                    )
                                    or (self.existing_table_action == "update")
                                )
                            )
                        )
                    )
                    or (
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "merge")
                                    or (self.write_mode == "merge")
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
            )
            else exclude.add("key_column_names")
        )
        (
            include.add("update_statement")
            if (
                ((not self.static_statement))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_statement")
                                or (self.write_mode == "update_statement")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (
                                    hasattr(self.write_mode, "value")
                                    and self.write_mode.value == "update_statement_table_action"
                                )
                                or (self.write_mode == "update_statement_table_action")
                            )

                    )
                )
            )
            else exclude.add("update_statement")
        )
        (
            include.add("batch_size")
            if (((not self.has_reject_output)) or (not self.has_reject_output))
            else exclude.add("batch_size")
        )
        (
            include.add("ds_load_from_file_staging_area_format_quotes")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_staging_area_format_quotes")
        )
        (
            include.add("ds_load_from_file_s3_encryption")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_s3_encryption")
        )
        (
            include.add("ds_begin_end_sql")
            if (

                    (
                        ((self.ds_write_mode == "insert"))
                        or ((not self.ds_use_merge_statement))
                        or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                        or ((self.ds_use_merge_statement and "#" in str(self.ds_use_merge_statement)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_begin_end_sql")
        )
        (
            include.add("ds_load_from_file_azure_sastoken")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_azure"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_azure_sastoken")
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
            else exclude.add("table_name")
        )
        (
            include.add("create_statement")
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
            else exclude.add("create_statement")
        )
        (
            include.add("ds_table_action_generate_drop_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
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
            include.add("ds_table_action_generate_truncate_statement_fail_on_error")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_table_action == "_truncate"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("ds_load_from_file_use_credentials_file")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_use_credentials_file")
        )
        (
            include.add("ds_update_statement_read_from_file_update")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "insert_update"))
                                or ((self.ds_write_mode == "update"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_update_statement_read_from_file_update")
        )
        (
            include.add("ds_load_from_file_staging_area_format_other_file_format_options")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_staging_area_format_other_file_format_options")
        )
        (
            include.add("ds_table_action_generate_create_statement_create_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_table_action == "_create"))
                                or ((self.ds_table_action == "_replace"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                            and (
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
            include.add("ds_load_from_file_staging_area_type")
            if (

                    (
                        (
                            ((self.ds_write_mode == "load_from_file"))
                            or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                        )
                        or (
                            (
                                (
                                    ((self.ds_write_mode == "delete"))
                                    or ((self.ds_write_mode == "delete_insert"))
                                    or ((self.ds_write_mode == "insert_update"))
                                    or ((self.ds_write_mode == "update"))
                                    or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                                )
                                and (
                                    ((self.ds_use_merge_statement))
                                    or ((self.ds_use_merge_statement and "#" in str(self.ds_use_merge_statement)))
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_staging_area_type")
        )
        (
            include.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
            if (

                    (
                        ((self.ds_session_character_set_for_non_unicode_columns == "_custom"))
                        or (
                            (
                                self.ds_session_character_set_for_non_unicode_columns
                                and "#" in str(self.ds_session_character_set_for_non_unicode_columns)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
        )
        (
            include.add("ds_session_batch_size")
            if (

                    (
                        (
                            ((self.ds_write_mode == "custom"))
                            or ((self.ds_write_mode == "insert"))
                            or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                        )
                        or (
                            (
                                (
                                    ((self.ds_write_mode == "delete"))
                                    or ((self.ds_write_mode == "update"))
                                    or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                                )
                                and (
                                    ((not self.ds_use_merge_statement))
                                    or ((self.ds_use_merge_statement and "#" in str(self.ds_use_merge_statement)))
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_session_batch_size")
        )
        (
            include.add("ds_load_from_file_max_file_size")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_staging_area_type == "internal_location"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                (
                                    ((self.ds_write_mode == "load_from_file"))
                                    or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                                )
                                or (
                                    (
                                        (
                                            ((self.ds_write_mode == "delete"))
                                            or ((self.ds_write_mode == "delete_insert"))
                                            or ((self.ds_write_mode == "insert_update"))
                                            or ((self.ds_write_mode == "update"))
                                            or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                                        )
                                        and (
                                            ((self.ds_use_merge_statement))
                                            or (
                                                (
                                                    self.ds_use_merge_statement
                                                    and "#" in str(self.ds_use_merge_statement)
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_max_file_size")
        )
        (
            include.add("ds_load_from_file_gcs_file_format")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_gcs_use_existing_file_format))
                                or (
                                    (
                                        self.ds_load_from_file_gcs_use_existing_file_format
                                        and "#" in str(self.ds_load_from_file_gcs_use_existing_file_format)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_gcs_file_format")
        )
        (
            include.add("ds_load_from_file_file_format_record_delimiter")
            if (

                    (
                        ((self.ds_load_from_file_file_format == "csv"))
                        or ((self.ds_load_from_file_file_format and "#" in str(self.ds_load_from_file_file_format)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_record_delimiter")
        )
        (
            include.add("ds_load_from_file_azure_file_name")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_azure"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_azure_file_name")
        )
        (
            include.add("ds_use_merge_statement")
            if (

                    (
                        ((self.ds_write_mode == "delete"))
                        or ((self.ds_write_mode == "delete_insert"))
                        or ((self.ds_write_mode == "insert_update"))
                        or ((self.ds_write_mode == "update"))
                        or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_use_merge_statement")
        )
        (
            include.add("ds_load_from_file_gcs_use_existing_file_format")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_gcs_use_existing_file_format")
        )
        (
            include.add("ds_load_from_file_file_format_encoding")
            if (

                    (
                        ((self.ds_load_from_file_file_format == "csv"))
                        or ((self.ds_load_from_file_file_format and "#" in str(self.ds_load_from_file_file_format)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_encoding")
        )
        (
            include.add("ds_load_from_file_file_format_skip_byte_order_mark")
            if (

                    (
                        ((self.ds_load_from_file_file_format == "csv"))
                        or ((self.ds_load_from_file_file_format and "#" in str(self.ds_load_from_file_file_format)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_skip_byte_order_mark")
        )
        (
            include.add("ds_load_from_file_s3_secret_key")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_s3_secret_key")
        )
        (
            include.add("ds_delete_statement_read_from_file_delete")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "delete"))
                                or ((self.ds_write_mode == "delete_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_delete_statement_read_from_file_delete")
        )
        (
            include.add("table_action")
            if (

                    (
                        (
                            (
                                (
                                    (
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
                                                        and self.write_mode.value == "merge"
                                                    )
                                                    or (self.write_mode == "merge")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.write_mode
                                                and (
                                                    (
                                                        hasattr(self.write_mode, "value")
                                                        and self.write_mode.value == "update_statement_table_action"
                                                    )
                                                    or (self.write_mode == "update_statement_table_action")
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
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("table_action")
        )
        (
            include.add("ds_load_from_file_staging_area_format_encoding")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_staging_area_format_encoding")
        )
        (
            include.add("ds_table_action_generate_truncate_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
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
            include.add("ds_load_from_file_s3_access_key")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_s3_access_key")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_truncate_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_table_action == "_truncate"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                            and (
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
            include.add("ds_load_from_file_staging_area_name")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "external_azure"))
                        or ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                        or ((self.ds_load_from_file_staging_area_type == "external_s3"))
                        or ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_staging_area_name")
        )
        (
            include.add("ds_load_from_file_file_format_date_format")
            if (

                    (
                        ((self.ds_load_from_file_file_format == "csv"))
                        or ((self.ds_load_from_file_file_format and "#" in str(self.ds_load_from_file_file_format)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_date_format")
        )
        (
            include.add("ds_update_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "insert_update"))
                                or ((self.ds_write_mode == "update"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_update_statement")
        )
        (
            include.add("ds_load_from_file_file_format_timestamp_format")
            if (

                    (
                        ((self.ds_load_from_file_file_format == "csv"))
                        or ((self.ds_load_from_file_file_format and "#" in str(self.ds_load_from_file_file_format)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_timestamp_format")
        )
        (
            include.add("static_statement")
            if (

                    (
                        (
                            (((not self.schema_name)) or ((self.schema_name and "#" in str(self.schema_name))))
                            and (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                            and (
                                ((not self.update_statement))
                                or ((self.update_statement and "#" in str(self.update_statement)))
                            )
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
            include.add("ds_record_count")
            if (

                    (
                        ((self.ds_write_mode == "insert"))
                        or ((not self.ds_use_merge_statement))
                        or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                        or ((self.ds_use_merge_statement and "#" in str(self.ds_use_merge_statement)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_record_count")
        )
        (
            include.add("ds_load_from_file_file_format_field_delimiter")
            if (

                    (
                        ((self.ds_load_from_file_file_format == "csv"))
                        or ((self.ds_load_from_file_file_format and "#" in str(self.ds_load_from_file_file_format)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_field_delimiter")
        )
        (
            include.add("ds_load_from_file_file_format_other_format_options")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_file_format == "csv"))
                                or (
                                    (
                                        self.ds_load_from_file_file_format
                                        and "#" in str(self.ds_load_from_file_file_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_other_format_options")
        )
        (
            include.add("ds_load_from_file_file_format")
            if (

                    (
                        (
                            (
                                (
                                    ((self.ds_load_from_file_staging_area_type == "external_azure"))
                                    or ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                                    or (
                                        (
                                            self.ds_load_from_file_staging_area_type
                                            and "#" in str(self.ds_load_from_file_staging_area_type)
                                        )
                                    )
                                )
                                or ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                                or ((not self.ds_load_from_file_azure_use_existing_file_format))
                                or ((not self.ds_load_from_file_gcs_use_existing_file_format))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                                or (
                                    (
                                        self.ds_load_from_file_azure_use_existing_file_format
                                        and "#" in str(self.ds_load_from_file_azure_use_existing_file_format)
                                    )
                                )
                                or (
                                    (
                                        self.ds_load_from_file_gcs_use_existing_file_format
                                        and "#" in str(self.ds_load_from_file_gcs_use_existing_file_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format")
        )
        (
            include.add("ds_load_from_file_create_staging_area")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "external_azure"))
                        or ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                        or ((self.ds_load_from_file_staging_area_type == "external_s3"))
                        or ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_create_staging_area")
        )
        (
            include.add("ds_load_from_file_directory_path")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_directory_path")
        )
        (
            include.add("ds_auto_commit_mode")
            if (

                    (
                        ((self.ds_write_mode == "insert"))
                        or ((not self.ds_use_merge_statement))
                        or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                        or ((self.ds_use_merge_statement and "#" in str(self.ds_use_merge_statement)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_auto_commit_mode")
        )
        (
            include.add("ds_load_from_file_copy_options_other_copy_options")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "external_azure"))
                        or ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                        or ((self.ds_load_from_file_staging_area_type == "external_s3"))
                        or ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_copy_options_other_copy_options")
        )
        (
            include.add("ds_table_action")
            if (

                    (
                        ((self.ds_write_mode == "insert"))
                        or ((self.ds_write_mode == "load_from_file"))
                        or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action")
        )
        (
            include.add("ds_load_from_file_file_format_snappy_compression")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_file_format == "parquet"))
                                or (
                                    (
                                        self.ds_load_from_file_file_format
                                        and "#" in str(self.ds_load_from_file_file_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_snappy_compression")
        )
        (
            include.add("ds_load_from_file_credentials_file_name")
            if ((((self.ds_load_from_file_use_credentials_file))) and (self.ds_use_datastage))
            else exclude.add("ds_load_from_file_credentials_file_name")
        )
        (
            include.add("ds_load_from_file_staging_area_format_field_delimiter")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_staging_area_format_field_delimiter")
        )
        (
            include.add("ds_load_from_file_file_format_time_format")
            if (

                    (
                        ((self.ds_load_from_file_file_format == "csv"))
                        or ((self.ds_load_from_file_file_format and "#" in str(self.ds_load_from_file_file_format)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_time_format")
        )
        (
            include.add("ds_table_action_table_action_first")
            if (

                    (
                        ((self.ds_table_action == "_create"))
                        or ((self.ds_table_action == "_replace"))
                        or ((self.ds_table_action == "_truncate"))
                        or ((self.ds_table_action and "#" in str(self.ds_table_action)))
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
            else exclude.add("schema_name")
        )
        (
            include.add("ds_load_from_file_staging_area_format_escape_character")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_staging_area_format_escape_character")
        )
        (
            include.add("ds_load_from_file_purge_copied_files")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "external_azure"))
                        or ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                        or ((self.ds_load_from_file_staging_area_type == "external_s3"))
                        or ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_purge_copied_files")
        )
        (
            include.add("ds_delete_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "delete"))
                                or ((self.ds_write_mode == "delete_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_delete_statement")
        )
        (
            include.add("ds_load_from_file_copy_options_on_error")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "external_azure"))
                        or ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                        or ((self.ds_load_from_file_staging_area_type == "external_s3"))
                        or ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_copy_options_on_error")
        )
        (
            include.add("ds_load_from_file_file_format_compression")
            if (

                    (
                        ((self.ds_load_from_file_file_format == "avro"))
                        or ((self.ds_load_from_file_file_format == "csv"))
                        or ((self.ds_load_from_file_file_format and "#" in str(self.ds_load_from_file_file_format)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_compression")
        )
        (
            include.add("key_column_names")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        ((not self.update_statement))
                                        or ((self.update_statement and "#" in str(self.update_statement)))
                                    )
                                    and (
                                        ((not self.static_statement))
                                        or ((self.static_statement and "#" in str(self.static_statement)))
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        (
                                            self.existing_table_action
                                            and (
                                                (
                                                    hasattr(self.existing_table_action, "value")
                                                    and self.existing_table_action.value == "append"
                                                )
                                                or (self.existing_table_action == "append")
                                            )
                                        )
                                    )
                                    or (
                                        (
                                            self.existing_table_action
                                            and (
                                                (
                                                    hasattr(self.existing_table_action, "value")
                                                    and self.existing_table_action.value == "merge"
                                                )
                                                or (self.existing_table_action == "merge")
                                            )
                                        )
                                    )
                                    or (
                                        (
                                            self.existing_table_action
                                            and (
                                                (
                                                    hasattr(self.existing_table_action, "value")
                                                    and self.existing_table_action.value == "update"
                                                )
                                                or (self.existing_table_action == "update")
                                            )
                                        )
                                    )
                                )
                                or (
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
                                                (hasattr(self.write_mode, "value") and self.write_mode.value == "merge")
                                                or (self.write_mode == "merge")
                                            )
                                        )
                                    )
                                    or (
                                        (
                                            self.write_mode
                                            and (
                                                (
                                                    hasattr(self.write_mode, "value")
                                                    and self.write_mode.value == "update"
                                                )
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("key_column_names")
        )
        (
            include.add("ds_load_from_file_azure_use_existing_file_format")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_azure"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_azure_use_existing_file_format")
        )
        (
            include.add("ds_isolation_level")
            if (

                    (
                        ((self.ds_write_mode == "insert"))
                        or ((not self.ds_use_merge_statement))
                        or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                        or ((self.ds_use_merge_statement and "#" in str(self.ds_use_merge_statement)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_isolation_level")
        )
        (
            include.add("ds_session_report_schema_mismatch")
            if (

                    (
                        (
                            (
                                (
                                    ((self.ds_write_mode == "delete"))
                                    or ((self.ds_write_mode == "delete_insert"))
                                    or ((self.ds_write_mode == "insert_update"))
                                    or ((self.ds_write_mode == "update"))
                                    or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                                )
                                and (
                                    ((not self.ds_use_merge_statement))
                                    or ((self.ds_use_merge_statement and "#" in str(self.ds_use_merge_statement)))
                                )
                                and (
                                    ((self.ds_generate_sql))
                                    or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                                )
                            )
                        )
                        or (
                            (
                                (
                                    ((self.ds_write_mode == "insert"))
                                    or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                                )
                                and (
                                    ((self.ds_generate_sql))
                                    or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_session_report_schema_mismatch")
        )
        (
            include.add("ds_load_from_file_s3_file_name")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_s3_file_name")
        )
        (
            include.add("ds_load_from_file_staging_area_format_null_value")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_staging_area_format_null_value")
        )
        (
            include.add("ds_load_from_file_file_format_binary_as_text")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_file_format == "parquet"))
                                or (
                                    (
                                        self.ds_load_from_file_file_format
                                        and "#" in str(self.ds_load_from_file_file_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_file_format_binary_as_text")
        )
        (
            include.add("ds_insert_statement_read_from_file_insert")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "delete_insert"))
                                or ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "insert_update"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_insert_statement_read_from_file_insert")
        )
        (
            include.add("ds_load_from_file_azure_storage_area_name")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_azure"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_azure_storage_area_name")
        )
        (
            include.add("ds_table_name")
            if (

                    (
                        (
                            ((self.ds_write_mode == "insert_overwrite"))
                            or ((self.ds_write_mode == "load_from_file"))
                            or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                        )
                        or ((self.ds_generate_sql))
                        or ((self.ds_use_merge_statement))
                        or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                        or ((self.ds_use_merge_statement and "#" in str(self.ds_use_merge_statement)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_load_from_file_staging_area_format_record_delimiter")
            if (

                    (
                        ((self.ds_load_from_file_staging_area_type == "internal_location"))
                        or (
                            (
                                self.ds_load_from_file_staging_area_type
                                and "#" in str(self.ds_load_from_file_staging_area_type)
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_staging_area_format_record_delimiter")
        )
        (
            include.add("update_statement")
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
                                        self.write_mode
                                        and (
                                            (
                                                hasattr(self.write_mode, "value")
                                                and self.write_mode.value == "update_statement"
                                            )
                                            or (self.write_mode == "update_statement")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.write_mode
                                        and (
                                            (
                                                hasattr(self.write_mode, "value")
                                                and self.write_mode.value == "update_statement_table_action"
                                            )
                                            or (self.write_mode == "update_statement_table_action")
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
            else exclude.add("update_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement_fail_on_error")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_table_action == "_create"))
                                or ((self.ds_table_action == "_replace"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("ds_load_from_file_azure_encryption")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_azure"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_azure_encryption")
        )
        (
            include.add("ds_load_from_file_gcs_file_name")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_gcs_file_name")
        )
        (
            include.add("batch_size")
            if (

                    (((not self.has_reject_output)) or ((not self.has_reject_output)))
                    and (not self.ds_use_datastage)

            )
            else exclude.add("batch_size")
        )
        (
            include.add("ds_load_from_file_gcs_storage_integration")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_gcs_storage_integration")
        )
        (
            include.add("ds_insert_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "delete_insert"))
                                or ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "insert_update"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
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
                                ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_table_action == "_replace"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                            and (
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
            include.add("ds_custom_statements_read_from_file_custom")
            if (

                    (((self.ds_write_mode == "custom")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_custom_statements_read_from_file_custom")
        )
        (
            include.add("ds_load_from_file_s3_bucket_name")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_staging_area_type == "external_s3"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_s3_bucket_name")
        )
        (
            include.add("ds_table_action_generate_drop_statement_fail_on_error")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_table_action == "_replace"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("ds_load_from_file_delete_staging_area")
            if (

                    (
                        (
                            (
                                ((self.ds_load_from_file_staging_area_type == "external_azure"))
                                or ((self.ds_load_from_file_staging_area_type == "external_gcs"))
                                or ((self.ds_load_from_file_staging_area_type == "external_s3"))
                                or ((self.ds_load_from_file_staging_area_type == "internal_location"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_delete_staging_area")
        )
        (
            include.add("ds_generate_sql")
            if (

                    (
                        ((self.ds_write_mode == "insert"))
                        or (
                            (
                                (
                                    ((not self.ds_use_merge_statement))
                                    or ((self.ds_use_merge_statement and "#" in str(self.ds_use_merge_statement)))
                                )
                                and (
                                    ((self.ds_use_merge_statement))
                                    or ((self.ds_use_merge_statement and "#" in str(self.ds_use_merge_statement)))
                                )
                            )
                        )
                        or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_generate_sql")
        )
        (
            include.add("ds_load_from_file_azure_file_format_name")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_azure"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_azure_use_existing_file_format))
                                or (
                                    (
                                        self.ds_load_from_file_azure_use_existing_file_format
                                        and "#" in str(self.ds_load_from_file_azure_use_existing_file_format)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_azure_file_format_name")
        )
        (
            include.add("ds_load_from_file_azure_master_key")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_load_from_file_staging_area_type == "external_azure"))
                                or (
                                    (
                                        self.ds_load_from_file_staging_area_type
                                        and "#" in str(self.ds_load_from_file_staging_area_type)
                                    )
                                )
                            )
                            and (
                                ((self.ds_load_from_file_create_staging_area))
                                or (
                                    (
                                        self.ds_load_from_file_create_staging_area
                                        and "#" in str(self.ds_load_from_file_create_staging_area)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_load_from_file_azure_master_key")
        )
        (
            include.add("ds_table_action_generate_create_statement")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "load_from_file"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
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

                    (((self.ds_write_mode == "custom")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_custom_statements")
        )
        (
            include.add("ds_session_drop_unmatched_fields")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_drop_unmatched_fields")
        )
        include.add("write_mode") if (not self.ds_use_datastage) else exclude.add("write_mode")
        include.add("ds_write_mode") if (self.ds_use_datastage) else exclude.add("ds_write_mode")
        (
            include.add("existing_table_action")
            if (not self.ds_use_datastage)
            else exclude.add("existing_table_action")
        )
        (
            include.add("runtime_column_propagation")
            if (not self.enable_schemaless_design)
            else exclude.add("runtime_column_propagation")
        )
        (
            include.add("ds_load_from_file_staging_area_format_encoding")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_encoding")
        )
        (
            include.add("ds_load_from_file_create_staging_area")
            if (
                self.ds_load_from_file_staging_area_type
                and "external_azure" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "external_gcs" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "external_s3" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "internal_location" in str(self.ds_load_from_file_staging_area_type)
            )
            else exclude.add("ds_load_from_file_create_staging_area")
        )
        (
            include.add("ds_session_report_schema_mismatch")
            if (
                (
                    self.ds_write_mode
                    and "delete" in str(self.ds_write_mode)
                    and self.ds_write_mode
                    and "delete_insert" in str(self.ds_write_mode)
                    and self.ds_write_mode
                    and "insert_update" in str(self.ds_write_mode)
                    and self.ds_write_mode
                    and "update" in str(self.ds_write_mode)
                )
                and (self.ds_use_merge_statement == "false" or not self.ds_use_merge_statement)
                and (self.ds_generate_sql == "true" or self.ds_generate_sql)
            )
            or (
                (self.ds_write_mode and "insert" in str(self.ds_write_mode))
                and (self.ds_generate_sql == "true" or self.ds_generate_sql)
            )
            else exclude.add("ds_session_report_schema_mismatch")
        )
        (
            include.add("ds_table_action_generate_create_statement_fail_on_error")
            if (
                self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            and (
                self.ds_table_action
                and "_create" in str(self.ds_table_action)
                and self.ds_table_action
                and "_replace" in str(self.ds_table_action)
            )
            else exclude.add("ds_table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("ds_table_action")
            if (
                self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            else exclude.add("ds_table_action")
        )
        (
            include.add("ds_load_from_file_s3_file_name")
            if (self.ds_load_from_file_staging_area_type == "external_s3")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_s3_file_name")
        )
        (
            include.add("ds_use_merge_statement")
            if (
                self.ds_write_mode
                and "delete" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "delete_insert" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "insert_update" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "update" in str(self.ds_write_mode)
            )
            else exclude.add("ds_use_merge_statement")
        )
        (
            include.add("ds_load_from_file_staging_area_format_record_delimiter")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_record_delimiter")
        )
        (
            include.add("ds_load_from_file_gcs_file_format")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_gcs")
            and (
                self.ds_load_from_file_gcs_use_existing_file_format == "true"
                or self.ds_load_from_file_gcs_use_existing_file_format
            )
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_gcs_file_format")
        )
        (
            include.add("ds_load_from_file_staging_area_format_escape_character")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_escape_character")
        )
        (
            include.add("ds_load_from_file_file_format_date_format")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_date_format")
        )
        (
            include.add("ds_load_from_file_credentials_file_name")
            if (
                self.ds_load_from_file_use_credentials_file == "true"
                or self.ds_load_from_file_use_credentials_file
            )
            else exclude.add("ds_load_from_file_credentials_file_name")
        )
        (
            include.add("ds_load_from_file_azure_file_format_name")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_azure")
            and (
                self.ds_load_from_file_azure_use_existing_file_format == "true"
                or self.ds_load_from_file_azure_use_existing_file_format
            )
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_azure_file_format_name")
        )
        (
            include.add("ds_auto_commit_mode")
            if (self.ds_write_mode == "insert")
            or (self.ds_use_merge_statement == "false" or not self.ds_use_merge_statement)
            else exclude.add("ds_auto_commit_mode")
        )
        (
            include.add("ds_load_from_file_staging_area_format_null_value")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_null_value")
        )
        (
            include.add("static_statement")
            if (not self.schema_name)
            and (not self.table_name)
            and (not self.update_statement)
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
            include.add("ds_load_from_file_file_format_timestamp_format")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_timestamp_format")
        )
        (
            include.add("ds_load_from_file_gcs_file_name")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_gcs")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_gcs_file_name")
        )
        (
            include.add("ds_table_action_generate_drop_statement_fail_on_error")
            if (
                self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            and (self.ds_table_action and "_replace" in str(self.ds_table_action))
            else exclude.add("ds_table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("ds_load_from_file_directory_path")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_directory_path")
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
            else exclude.add("table_name")
        )
        (
            include.add("batch_size")
            if (not self.has_reject_output) or (self.has_reject_output != "true" or not self.has_reject_output)
            else exclude.add("batch_size")
        )
        (
            include.add("ds_load_from_file_file_format_time_format")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_time_format")
        )
        (
            include.add("ds_update_statement")
            if (
                self.ds_write_mode
                and "insert_update" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "update" in str(self.ds_write_mode)
            )
            and (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_update_statement")
        )
        (
            include.add("ds_load_from_file_use_credentials_file")
            if (
                self.ds_load_from_file_staging_area_type
                and "external_s3" in str(self.ds_load_from_file_staging_area_type)
            )
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_use_credentials_file")
        )
        (
            include.add("key_column_names")
            if ((not self.update_statement) and (not self.static_statement))
            and (
                (
                    self.existing_table_action
                    and (
                        (
                            hasattr(self.existing_table_action, "value")
                            and self.existing_table_action.value
                            and "append" in str(self.existing_table_action.value)
                        )
                        or ("append" in str(self.existing_table_action))
                    )
                    or self.existing_table_action
                    and (
                        (
                            hasattr(self.existing_table_action, "value")
                            and self.existing_table_action.value
                            and "merge" in str(self.existing_table_action.value)
                        )
                        or ("merge" in str(self.existing_table_action))
                    )
                    or self.existing_table_action
                    and (
                        (
                            hasattr(self.existing_table_action, "value")
                            and self.existing_table_action.value
                            and "update" in str(self.existing_table_action.value)
                        )
                        or ("update" in str(self.existing_table_action))
                    )
                )
                or (
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
                            and "merge" in str(self.write_mode.value)
                        )
                        or ("merge" in str(self.write_mode))
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
                )
            )
            else exclude.add("key_column_names")
        )
        (
            include.add("ds_load_from_file_file_format_field_delimiter")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_field_delimiter")
        )
        (
            include.add("ds_load_from_file_azure_storage_area_name")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_azure")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_azure_storage_area_name")
        )
        (
            include.add("ds_load_from_file_s3_secret_key")
            if (self.ds_load_from_file_staging_area_type == "external_s3")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_s3_secret_key")
        )
        (
            include.add("ds_delete_statement_read_from_file_delete")
            if (
                self.ds_write_mode
                and "delete" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "delete_insert" in str(self.ds_write_mode)
            )
            and (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_delete_statement_read_from_file_delete")
        )
        (
            include.add("ds_load_from_file_file_format_binary_as_text")
            if (self.ds_load_from_file_file_format and "parquet" in str(self.ds_load_from_file_file_format))
            else exclude.add("ds_load_from_file_file_format_binary_as_text")
        )
        (
            include.add("ds_delete_statement")
            if (
                self.ds_write_mode
                and "delete" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "delete_insert" in str(self.ds_write_mode)
            )
            and (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_delete_statement")
        )
        (
            include.add("ds_load_from_file_staging_area_format_field_delimiter")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_field_delimiter")
        )
        (
            include.add("ds_load_from_file_max_file_size")
            if (
                self.ds_load_from_file_staging_area_type
                and "internal_location" in str(self.ds_load_from_file_staging_area_type)
            )
            and (
                (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
                or (
                    (
                        self.ds_write_mode
                        and "delete" in str(self.ds_write_mode)
                        and self.ds_write_mode
                        and "delete_insert" in str(self.ds_write_mode)
                        and self.ds_write_mode
                        and "insert_update" in str(self.ds_write_mode)
                        and self.ds_write_mode
                        and "update" in str(self.ds_write_mode)
                    )
                    and (self.ds_use_merge_statement == "true" or self.ds_use_merge_statement)
                )
            )
            else exclude.add("ds_load_from_file_max_file_size")
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
                    and self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "merge" in str(self.write_mode.value)
                        )
                        or ("merge" in str(self.write_mode))
                    )
                    and self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update_statement_table_action" in str(self.write_mode.value)
                        )
                        or ("update_statement_table_action" in str(self.write_mode))
                    )

            )
            and (
                (not self.static_statement)
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
            )
            else exclude.add("table_action")
        )
        (
            include.add("ds_table_action_generate_drop_statement_drop_statement")
            if (
                self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            and (self.ds_table_action and "_replace" in str(self.ds_table_action))
            and (
                self.ds_table_action_generate_drop_statement == "false"
                or not self.ds_table_action_generate_drop_statement
            )
            else exclude.add("ds_table_action_generate_drop_statement_drop_statement")
        )
        (
            include.add("ds_load_from_file_file_format_record_delimiter")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_record_delimiter")
        )
        (
            include.add("ds_record_count")
            if (self.ds_write_mode == "insert")
            or (self.ds_use_merge_statement == "false" or not self.ds_use_merge_statement)
            else exclude.add("ds_record_count")
        )
        (
            include.add("ds_load_from_file_azure_sastoken")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_azure")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_azure_sastoken")
        )
        (
            include.add("ds_load_from_file_staging_area_type")
            if (self.ds_use_merge_statement == "true" or self.ds_use_merge_statement)
            else exclude.add("ds_load_from_file_staging_area_type")
        )
        (
            include.add("ds_isolation_level")
            if (self.ds_write_mode == "insert")
            or (self.ds_use_merge_statement == "false" or not self.ds_use_merge_statement)
            else exclude.add("ds_isolation_level")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_fail_on_error")
            if (
                self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            and (self.ds_table_action and "_truncate" in str(self.ds_table_action))
            else exclude.add("ds_table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("ds_table_action_generate_create_statement_create_statement")
            if (
                self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            and (
                self.ds_table_action
                and "_create" in str(self.ds_table_action)
                and self.ds_table_action
                and "_replace" in str(self.ds_table_action)
            )
            and (
                self.ds_table_action_generate_create_statement == "false"
                or not self.ds_table_action_generate_create_statement
            )
            else exclude.add("ds_table_action_generate_create_statement_create_statement")
        )
        (
            include.add("ds_generate_sql")
            if (self.ds_write_mode == "insert")
            or (
                (self.ds_use_merge_statement == "false" or not self.ds_use_merge_statement)
                and (self.ds_use_merge_statement)
            )
            else exclude.add("ds_generate_sql")
        )
        (
            include.add("ds_table_action_generate_drop_statement")
            if (
                self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            and (self.ds_table_action and "_replace" in str(self.ds_table_action))
            else exclude.add("ds_table_action_generate_drop_statement")
        )
        (
            include.add("ds_custom_statements")
            if (self.ds_write_mode and "custom" in str(self.ds_write_mode))
            else exclude.add("ds_custom_statements")
        )
        (
            include.add("ds_table_action_table_action_first")
            if (
                self.ds_table_action
                and "_create" in str(self.ds_table_action)
                or self.ds_table_action
                and "_replace" in str(self.ds_table_action)
                or self.ds_table_action
                and "_truncate" in str(self.ds_table_action)
            )
            else exclude.add("ds_table_action_table_action_first")
        )
        (
            include.add("ds_update_statement_read_from_file_update")
            if (
                self.ds_write_mode
                and "insert_update" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "update" in str(self.ds_write_mode)
            )
            and (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_update_statement_read_from_file_update")
        )
        (
            include.add("ds_custom_statements_read_from_file_custom")
            if (self.ds_write_mode and "custom" in str(self.ds_write_mode))
            else exclude.add("ds_custom_statements_read_from_file_custom")
        )
        (
            include.add("ds_insert_statement")
            if (
                self.ds_write_mode
                and "delete_insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert_update" in str(self.ds_write_mode)
            )
            and (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_insert_statement")
        )
        (
            include.add("ds_load_from_file_staging_area_name")
            if (
                self.ds_load_from_file_staging_area_type
                and "external_azure" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "external_gcs" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "external_s3" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "internal_location" in str(self.ds_load_from_file_staging_area_type)
            )
            else exclude.add("ds_load_from_file_staging_area_name")
        )
        (
            include.add("ds_load_from_file_file_format_snappy_compression")
            if (self.ds_load_from_file_file_format and "parquet" in str(self.ds_load_from_file_file_format))
            else exclude.add("ds_load_from_file_file_format_snappy_compression")
        )
        (
            include.add("create_statement")
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
            else exclude.add("create_statement")
        )
        (
            include.add("ds_begin_end_sql")
            if (self.ds_write_mode == "insert")
            or (self.ds_use_merge_statement == "false" or not self.ds_use_merge_statement)
            else exclude.add("ds_begin_end_sql")
        )
        (
            include.add("ds_load_from_file_copy_options_other_copy_options")
            if (
                self.ds_load_from_file_staging_area_type
                and "external_azure" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "external_gcs" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "external_s3" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "internal_location" in str(self.ds_load_from_file_staging_area_type)
            )
            else exclude.add("ds_load_from_file_copy_options_other_copy_options")
        )
        (
            include.add("ds_load_from_file_s3_bucket_name")
            if (self.ds_load_from_file_staging_area_type == "external_s3")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_s3_bucket_name")
        )
        (
            include.add("ds_load_from_file_azure_use_existing_file_format")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_azure")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_azure_use_existing_file_format")
        )
        (
            include.add("ds_load_from_file_gcs_storage_integration")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_gcs")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_gcs_storage_integration")
        )
        (
            include.add("ds_insert_statement_read_from_file_insert")
            if (
                self.ds_write_mode
                and "delete_insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert_update" in str(self.ds_write_mode)
            )
            and (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_insert_statement_read_from_file_insert")
        )
        (
            include.add("ds_load_from_file_file_format")
            if (
                (
                    self.ds_load_from_file_staging_area_type
                    and "external_azure" in str(self.ds_load_from_file_staging_area_type)
                    or self.ds_load_from_file_staging_area_type
                    and "external_gcs" in str(self.ds_load_from_file_staging_area_type)
                )
                or (
                    self.ds_load_from_file_create_staging_area == "true"
                    or self.ds_load_from_file_create_staging_area
                )
            )
            and (
                (self.ds_load_from_file_staging_area_type == "external_s3")
                or (
                    self.ds_load_from_file_azure_use_existing_file_format == "false"
                    or not self.ds_load_from_file_azure_use_existing_file_format
                )
                or (
                    self.ds_load_from_file_gcs_use_existing_file_format == "false"
                    or not self.ds_load_from_file_gcs_use_existing_file_format
                )
            )
            else exclude.add("ds_load_from_file_file_format")
        )
        (
            include.add("ds_load_from_file_file_format_compression")
            if (
                self.ds_load_from_file_file_format
                and "avro" in str(self.ds_load_from_file_file_format)
                or self.ds_load_from_file_file_format
                and "csv" in str(self.ds_load_from_file_file_format)
            )
            else exclude.add("ds_load_from_file_file_format_compression")
        )
        (
            include.add("ds_load_from_file_staging_area_type")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            or (
                (
                    self.ds_write_mode
                    and "delete" in str(self.ds_write_mode)
                    and self.ds_write_mode
                    and "delete_insert" in str(self.ds_write_mode)
                    and self.ds_write_mode
                    and "insert_update" in str(self.ds_write_mode)
                    and self.ds_write_mode
                    and "update" in str(self.ds_write_mode)
                )
                and (self.ds_use_merge_statement == "true" or self.ds_use_merge_statement)
            )
            else exclude.add("ds_load_from_file_staging_area_type")
        )
        (
            include.add("ds_load_from_file_staging_area_format_other_file_format_options")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_other_file_format_options")
        )
        (
            include.add("ds_load_from_file_copy_options_on_error")
            if (
                self.ds_load_from_file_staging_area_type
                and "external_azure" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "external_gcs" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "external_s3" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "internal_location" in str(self.ds_load_from_file_staging_area_type)
            )
            else exclude.add("ds_load_from_file_copy_options_on_error")
        )
        (
            include.add("ds_table_action_generate_truncate_statement")
            if (
                self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            and (self.ds_table_action and "_truncate" in str(self.ds_table_action))
            else exclude.add("ds_table_action_generate_truncate_statement")
        )
        (
            include.add("ds_load_from_file_azure_file_name")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_azure")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_azure_file_name")
        )
        (
            include.add("ds_load_from_file_staging_area_format_quotes")
            if (self.ds_load_from_file_staging_area_type == "internal_location")
            else exclude.add("ds_load_from_file_staging_area_format_quotes")
        )
        (
            include.add("ds_load_from_file_file_format_encoding")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_encoding")
        )
        (
            include.add("ds_load_from_file_azure_encryption")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_azure")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_azure_encryption")
        )
        (
            include.add("ds_load_from_file_gcs_use_existing_file_format")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_gcs")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_gcs_use_existing_file_format")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_truncate_statement")
            if (
                self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            and (self.ds_table_action and "_truncate" in str(self.ds_table_action))
            and (
                self.ds_table_action_generate_truncate_statement == "false"
                or not self.ds_table_action_generate_truncate_statement
            )
            else exclude.add("ds_table_action_generate_truncate_statement_truncate_statement")
        )
        (
            include.add("ds_load_from_file_file_format_skip_byte_order_mark")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_skip_byte_order_mark")
        )
        (
            include.add("update_statement")
            if (not self.static_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_statement" in str(self.write_mode.value)
                    )
                    or ("update_statement" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_statement_table_action" in str(self.write_mode.value)
                    )
                    or ("update_statement_table_action" in str(self.write_mode))
                )
            )
            else exclude.add("update_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement")
            if (
                self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            and (
                self.ds_table_action
                and "_create" in str(self.ds_table_action)
                and self.ds_table_action
                and "_replace" in str(self.ds_table_action)
            )
            else exclude.add("ds_table_action_generate_create_statement")
        )
        (
            include.add("ds_table_name")
            if (
                self.ds_write_mode
                and "insert_overwrite" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "load_from_file" in str(self.ds_write_mode)
            )
            or (self.ds_generate_sql == "true" or self.ds_generate_sql)
            or (self.ds_use_merge_statement == "true" or self.ds_use_merge_statement)
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_load_from_file_s3_encryption")
            if (self.ds_load_from_file_staging_area_type == "external_s3")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_s3_encryption")
        )
        (
            include.add("ds_load_from_file_file_format_other_format_options")
            if (self.ds_load_from_file_file_format == "csv")
            else exclude.add("ds_load_from_file_file_format_other_format_options")
        )
        (
            include.add("ds_load_from_file_purge_copied_files")
            if (
                self.ds_load_from_file_staging_area_type
                and "external_azure" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "external_gcs" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "external_s3" in str(self.ds_load_from_file_staging_area_type)
                or self.ds_load_from_file_staging_area_type
                and "internal_location" in str(self.ds_load_from_file_staging_area_type)
            )
            else exclude.add("ds_load_from_file_purge_copied_files")
        )
        (
            include.add("ds_session_batch_size")
            if (
                self.ds_write_mode
                and "custom" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
            )
            or (
                (
                    self.ds_write_mode
                    and "delete" in str(self.ds_write_mode)
                    and self.ds_write_mode
                    and "update" in str(self.ds_write_mode)
                )
                and (self.ds_use_merge_statement == "false" or not self.ds_use_merge_statement)
            )
            else exclude.add("ds_session_batch_size")
        )
        (
            include.add("ds_load_from_file_s3_access_key")
            if (self.ds_load_from_file_staging_area_type == "external_s3")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_s3_access_key")
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
            else exclude.add("schema_name")
        )
        (
            include.add("ds_load_from_file_delete_staging_area")
            if (
                self.ds_load_from_file_staging_area_type
                and "external_azure" in str(self.ds_load_from_file_staging_area_type)
                and self.ds_load_from_file_staging_area_type
                and "external_gcs" in str(self.ds_load_from_file_staging_area_type)
                and self.ds_load_from_file_staging_area_type
                and "external_s3" in str(self.ds_load_from_file_staging_area_type)
                and self.ds_load_from_file_staging_area_type
                and "internal_location" in str(self.ds_load_from_file_staging_area_type)
            )
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_delete_staging_area")
        )
        (
            include.add("ds_load_from_file_azure_master_key")
            if (self.ds_write_mode and "load_from_file" in str(self.ds_write_mode))
            and (self.ds_load_from_file_staging_area_type == "external_azure")
            and (
                self.ds_load_from_file_create_staging_area == "true"
                or self.ds_load_from_file_create_staging_area
            )
            else exclude.add("ds_load_from_file_azure_master_key")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "add_procedure_return_value_to_schema",
            "before_sql",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "byte_limit",
            "call_procedure_statement",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "conn_query_timeout",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "decimal_rounding_mode",
            "default_maximum_length_for_columns",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_additional_properties",
            "ds_auto_commit_mode",
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
            "ds_begin_end_sql",
            "ds_begin_sql",
            "ds_enable_partitioned_reads",
            "ds_enable_quoted_ids",
            "ds_end_of_wave",
            "ds_end_sql",
            "ds_generate_sql",
            "ds_isolation_level",
            "ds_java_heap_size",
            "ds_limit_rows_limit",
            "ds_read_mode",
            "ds_record_count",
            "ds_record_ordering",
            "ds_record_ordering_properties",
            "ds_run_end_sql_if_no_records_processed",
            "ds_select_statement",
            "ds_select_statement_other_clause",
            "ds_select_statement_read_from_file_select",
            "ds_select_statement_where_clause",
            "ds_session_array_size",
            "ds_session_character_set_for_non_unicode_columns",
            "ds_session_character_set_for_non_unicode_columns_character_set_name",
            "ds_session_default_length_for_columns",
            "ds_session_default_length_for_long_columns",
            "ds_session_fetch_size",
            "ds_session_generate_all_columns_as_unicode",
            "ds_session_keep_conductor_connection_alive",
            "ds_session_report_schema_mismatch",
            "ds_table_name",
            "ds_use_datastage",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_sql",
            "enable_before_sql_node",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "error_warning",
            "execution_mode",
            "fail_on_error_after_partition_sql",
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_partition_sql",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "fatal_error",
            "flow_dirty",
            "forward_row_data",
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
            "partition_after_sql",
            "partition_before_sql",
            "partition_type",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "preserve_partitioning",
            "proc_param_properties",
            "procedure_name",
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
            "transform",
            "unique",
            "user_defined_function",
        }
        required = {
            "account_name",
            "authentication_method",
            "current_output_link_type",
            "database",
            "ds_select_statement",
            "ds_session_character_set_for_non_unicode_columns_character_set_name",
            "ds_table_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "output_acp_should_hide",
            "password",
            "private_key",
            "select_statement",
            "table_name",
            "username",
            "warehouse",
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
            "batch_size",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "conn_query_timeout",
            "create_statement",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_additional_properties",
            "ds_auto_commit_mode",
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
            "ds_begin_end_sql",
            "ds_begin_sql",
            "ds_custom_statements",
            "ds_custom_statements_read_from_file_custom",
            "ds_delete_statement",
            "ds_delete_statement_read_from_file_delete",
            "ds_enable_quoted_ids",
            "ds_end_sql",
            "ds_generate_sql",
            "ds_insert_statement",
            "ds_insert_statement_read_from_file_insert",
            "ds_isolation_level",
            "ds_java_heap_size",
            "ds_load_from_file_azure_encryption",
            "ds_load_from_file_azure_file_format_name",
            "ds_load_from_file_azure_file_name",
            "ds_load_from_file_azure_master_key",
            "ds_load_from_file_azure_sastoken",
            "ds_load_from_file_azure_storage_area_name",
            "ds_load_from_file_azure_use_existing_file_format",
            "ds_load_from_file_copy_options_on_error",
            "ds_load_from_file_copy_options_other_copy_options",
            "ds_load_from_file_create_staging_area",
            "ds_load_from_file_credentials_file_name",
            "ds_load_from_file_delete_staging_area",
            "ds_load_from_file_directory_path",
            "ds_load_from_file_file_format",
            "ds_load_from_file_file_format_binary_as_text",
            "ds_load_from_file_file_format_compression",
            "ds_load_from_file_file_format_date_format",
            "ds_load_from_file_file_format_encoding",
            "ds_load_from_file_file_format_field_delimiter",
            "ds_load_from_file_file_format_other_format_options",
            "ds_load_from_file_file_format_record_delimiter",
            "ds_load_from_file_file_format_skip_byte_order_mark",
            "ds_load_from_file_file_format_snappy_compression",
            "ds_load_from_file_file_format_time_format",
            "ds_load_from_file_file_format_timestamp_format",
            "ds_load_from_file_gcs_file_format",
            "ds_load_from_file_gcs_file_name",
            "ds_load_from_file_gcs_storage_integration",
            "ds_load_from_file_gcs_use_existing_file_format",
            "ds_load_from_file_max_file_size",
            "ds_load_from_file_purge_copied_files",
            "ds_load_from_file_s3_access_key",
            "ds_load_from_file_s3_bucket_name",
            "ds_load_from_file_s3_encryption",
            "ds_load_from_file_s3_file_name",
            "ds_load_from_file_s3_secret_key",
            "ds_load_from_file_staging_area_format_encoding",
            "ds_load_from_file_staging_area_format_escape_character",
            "ds_load_from_file_staging_area_format_field_delimiter",
            "ds_load_from_file_staging_area_format_null_value",
            "ds_load_from_file_staging_area_format_other_file_format_options",
            "ds_load_from_file_staging_area_format_quotes",
            "ds_load_from_file_staging_area_format_record_delimiter",
            "ds_load_from_file_staging_area_name",
            "ds_load_from_file_staging_area_type",
            "ds_load_from_file_use_credentials_file",
            "ds_record_count",
            "ds_record_ordering",
            "ds_record_ordering_properties",
            "ds_run_end_sql_if_no_records_processed",
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
            "ds_table_action_generate_drop_statement",
            "ds_table_action_generate_drop_statement_drop_statement",
            "ds_table_action_generate_drop_statement_fail_on_error",
            "ds_table_action_generate_truncate_statement",
            "ds_table_action_generate_truncate_statement_fail_on_error",
            "ds_table_action_generate_truncate_statement_truncate_statement",
            "ds_table_action_table_action_first",
            "ds_table_name",
            "ds_update_statement",
            "ds_update_statement_read_from_file_update",
            "ds_use_datastage",
            "ds_use_merge_statement",
            "ds_write_mode",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_sql",
            "enable_before_sql_node",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execution_mode",
            "existing_table_action",
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "flow_dirty",
            "has_reject_output",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_column_names",
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
            "proc_param_properties",
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
            "update_statement",
            "write_mode",
        }
        required = {
            "account_name",
            "authentication_method",
            "current_output_link_type",
            "database",
            "ds_delete_statement",
            "ds_insert_statement",
            "ds_load_from_file_azure_file_format_name",
            "ds_load_from_file_azure_file_name",
            "ds_load_from_file_azure_sastoken",
            "ds_load_from_file_azure_storage_area_name",
            "ds_load_from_file_azure_use_existing_file_format",
            "ds_load_from_file_directory_path",
            "ds_load_from_file_gcs_file_format",
            "ds_load_from_file_gcs_file_name",
            "ds_load_from_file_gcs_storage_integration",
            "ds_load_from_file_gcs_use_existing_file_format",
            "ds_load_from_file_s3_access_key",
            "ds_load_from_file_s3_bucket_name",
            "ds_load_from_file_s3_file_name",
            "ds_load_from_file_s3_secret_key",
            "ds_load_from_file_staging_area_name",
            "ds_session_character_set_for_non_unicode_columns_character_set_name",
            "ds_table_action",
            "ds_table_action_generate_create_statement_create_statement",
            "ds_table_action_generate_drop_statement_drop_statement",
            "ds_table_action_generate_truncate_statement_truncate_statement",
            "ds_table_name",
            "ds_update_statement",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "output_acp_should_hide",
            "password",
            "private_key",
            "static_statement",
            "username",
            "warehouse",
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
            "ds_record_ordering_properties",
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
        return {"min": 0, "max": -1}

    def get_output_ports_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "is_reject_output",
            "reject_condition_row_is_rejected",
            "reject_condition_row_not_deleted",
            "reject_condition_row_not_inserted",
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
        return {"min": 0, "max": -1}

    def get_allowed_as_source_props(self) -> bool:
        return True

    def get_allowed_as_target_props(self) -> bool:
        return True
