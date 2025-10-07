import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.jdbc_connection import JdbcConn
from ibm_watsonx_data_integration.services.datastage.models.enums import JDBC
from pydantic import Field
from typing import ClassVar


class jdbc(BaseStage):

    op_name: ClassVar[str] = "JDBCConnectorPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/JDBCConnectorPX.svg"
    label: ClassVar[str] = "Generic JDBC"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: JdbcConn = JdbcConn()
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: JDBC.BufModeRonly | None = Field(JDBC.BufModeRonly.default, alias="buf_mode_ronly")
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: JDBC.BufferingMode | None = Field(JDBC.BufferingMode.default, alias="buf_mode")
    byte_limit: str | None = Field(None, alias="byte_limit")
    catalog_name: str | None = Field(None, alias="catalog_name")
    collecting: JDBC.Collecting | None = Field(JDBC.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: JDBC.CombinabilityMode | None = Field(JDBC.CombinabilityMode.auto, alias="combinability")
    create_statement: str | None = Field(None, alias="create_statement")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    decimal_rounding_mode: JDBC.DecimalRoundingMode | None = Field(
        JDBC.DecimalRoundingMode.floor, alias="decimal_rounding_mode"
    )
    default_maximum_length_for_columns: int | None = Field(20000, alias="default_max_string_binary_precision")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    ds_before_after: bool | None = Field(False, alias="_before_after")
    ds_before_after_after_sql: str | None = Field("", alias="_before_after.after_sql")
    ds_before_after_after_sql_fail_on_error: bool | None = Field(True, alias="_before_after.after_sql.fail_on_error")
    ds_before_after_after_sql_node: str | None = Field("", alias="_before_after.after_sql_node")
    ds_before_after_after_sql_node_fail_on_error: bool | None = Field(
        True, alias="_before_after.after_sql_node.fail_on_error"
    )
    ds_before_after_after_sql_node_read_from_file_after_sql_node: bool | None = Field(
        False, alias="_before_after.after_sql_node.read_from_file_after_sql_node"
    )
    ds_before_after_after_sql_read_from_file_after_sql: bool | None = Field(
        False, alias="_before_after.after_sql.read_from_file_after_sql"
    )
    ds_before_after_before_sql: str | None = Field("", alias="_before_after.before_sql")
    ds_before_after_before_sql_fail_on_error: bool | None = Field(
        True, alias="_before_after.before_sql.fail_on_error"
    )
    ds_before_after_before_sql_node: str | None = Field("", alias="_before_after.before_sql_node")
    ds_before_after_before_sql_node_fail_on_error: bool | None = Field(
        True, alias="_before_after.before_sql_node.fail_on_error"
    )
    ds_before_after_before_sql_node_read_from_file_before_sql_node: bool | None = Field(
        False, alias="_before_after.before_sql_node.read_from_file_before_sql_node"
    )
    ds_before_after_before_sql_read_from_file_before_sql: bool | None = Field(
        False, alias="_before_after.before_sql.read_from_file_before_sql"
    )
    ds_enable_quoted_i_ds: bool | None = Field(False, alias="_enable_quoted_i_ds")
    ds_generate_sql: bool | None = Field(True, alias="_generate_sql")
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    ds_limit_rows: bool | None = Field(False, alias="_limit_rows")
    ds_limit_rows_limit: int | None = Field(1000, alias="_limit_rows.limit")
    ds_read_mode: JDBC.DSReadMode | None = Field(JDBC.DSReadMode.select, alias="_read_mode")
    ds_record_ordering: JDBC.DSRecordOrdering | None = Field(JDBC.DSRecordOrdering.zero, alias="_record_ordering")
    ds_record_ordering_properties: list | None = Field([], alias="_record_ordering_properties")
    ds_session_array_size: int | None = Field(1, alias="_session.array_size")
    ds_session_batch_size: int | None = Field(2000, alias="_session.batch_size")
    ds_session_character_set_for_non_unicode_columns: JDBC.DSSessionCharacterSetForNonUnicodeColumns | None = Field(
        JDBC.DSSessionCharacterSetForNonUnicodeColumns.default, alias="_session.character_set_for_non_unicode_columns"
    )
    ds_session_character_set_for_non_unicode_columns_character_set_name: str = Field(
        "", alias="_session.character_set_for_non_unicode_columns.character_set_name"
    )
    ds_session_default_length_for_columns: int | None = Field(200, alias="_session.default_length_for_columns")
    ds_session_default_length_for_long_columns: int | None = Field(
        20000, alias="_session.default_length_for_long_columns"
    )
    ds_session_drop_unmatched_fields: bool | None = Field(False, alias="_session.drop_unmatched_fields")
    ds_session_fail_on_truncation: bool | None = Field(True, alias="_session.fail_on_truncation")
    ds_session_fetch_size: int | None = Field(0, alias="_session.fetch_size")
    ds_session_generate_all_columns_as_unicode: bool | None = Field(
        False, alias="_session.generate_all_columns_as_unicode"
    )
    ds_session_keep_conductor_connection_alive: bool | None = Field(
        True, alias="_session.keep_conductor_connection_alive"
    )
    ds_session_report_schema_mismatch: bool | None = Field(False, alias="_session.report_schema_mismatch")
    ds_sql_custom_statements: str | None = Field(None, alias="_sql.custom_statements")
    ds_sql_custom_statements_read_from_file_custom: bool | None = Field(
        False, alias="_sql.custom_statements.read_from_file_custom"
    )
    ds_sql_delete_statement: str = Field(None, alias="_sql.delete_statement")
    ds_sql_delete_statement_read_from_file_delete: bool | None = Field(
        False, alias="_sql.delete_statement.read_from_file_delete"
    )
    ds_sql_enable_partitioned_reads: bool | None = Field(False, alias="_sql.enable_partitioned_reads")
    ds_sql_insert_statement: str = Field(None, alias="_sql.insert_statement")
    ds_sql_insert_statement_read_from_file_insert: bool | None = Field(
        False, alias="_sql.insert_statement.read_from_file_insert"
    )
    ds_sql_select_statement: str = Field(None, alias="_sql.select_statement")
    ds_sql_select_statement_other_clause: str | None = Field(None, alias="_sql.select_statement.other_clause")
    ds_sql_select_statement_read_from_file_select: bool | None = Field(
        False, alias="_sql.select_statement.read_from_file_select"
    )
    ds_sql_select_statement_where_clause: str | None = Field(None, alias="_sql.select_statement.where_clause")
    ds_sql_update_statement: str = Field(None, alias="_sql.update_statement")
    ds_sql_update_statement_read_from_file_update: bool | None = Field(
        False, alias="_sql.update_statement.read_from_file_update"
    )
    ds_table_action: JDBC.DSTableAction = Field(JDBC.DSTableAction.append, alias="_table_action")
    ds_table_action_generate_create_statement: bool | None = Field(
        True, alias="_table_action.generate_create_statement"
    )
    ds_table_action_generate_create_statement_create_statement: str = Field(
        "", alias="_table_action.generate_create_statement.create_statement"
    )
    ds_table_action_generate_create_statement_fail_on_error: bool | None = Field(
        True, alias="_table_action.generate_create_statement.fail_on_error"
    )
    ds_table_action_generate_drop_statement: bool | None = Field(True, alias="_table_action.generate_drop_statement")
    ds_table_action_generate_drop_statement_drop_statement: str = Field(
        "", alias="_table_action.generate_drop_statement.drop_statement"
    )
    ds_table_action_generate_drop_statement_fail_on_error: bool | None = Field(
        False, alias="_table_action.generate_drop_statement.fail_on_error"
    )
    ds_table_action_generate_truncate_statement: bool | None = Field(
        True, alias="_table_action.generate_truncate_statement"
    )
    ds_table_action_generate_truncate_statement_fail_on_error: bool | None = Field(
        True, alias="_table_action.generate_truncate_statement.fail_on_error"
    )
    ds_table_action_generate_truncate_statement_truncate_statement: str = Field(
        "", alias="_table_action.generate_truncate_statement.truncate_statement"
    )
    ds_table_action_table_action_first: bool | None = Field(True, alias="_table_action.table_action_first")
    ds_table_name: str = Field(None, alias="_table_name")
    ds_transaction_autocommit_mode: JDBC.DSTransactionAutocommitMode | None = Field(
        JDBC.DSTransactionAutocommitMode.disable, alias="_transaction.autocommit_mode"
    )
    ds_transaction_begin_end: bool | None = Field(False, alias="_transaction.begin_end")
    ds_transaction_begin_end_begin_sql: str | None = Field(None, alias="_transaction.begin_end.begin_sql")
    ds_transaction_begin_end_end_sql: str | None = Field(None, alias="_transaction.begin_end.end_sql")
    ds_transaction_begin_end_run_end_sql_if_no_records_processed: bool | None = Field(
        False, alias="_transaction.begin_end.run_end_sql_if_no_records_processed"
    )
    ds_transaction_end_of_wave: JDBC.DSTransactionEndOfWave | None = Field(
        JDBC.DSTransactionEndOfWave.no, alias="_transaction.end_of_wave"
    )
    ds_transaction_isolation_level: JDBC.DSTransactionIsolationLevel | None = Field(
        JDBC.DSTransactionIsolationLevel.default, alias="_transaction.isolation_level"
    )
    ds_transaction_record_count: int | None = Field(2000, alias="_transaction.record_count")
    ds_use_datastage: bool | None = Field(True, alias="_use_datastage")
    ds_write_mode: JDBC.DSWriteMode | None = Field(JDBC.DSWriteMode.insert, alias="_write_mode")
    enable_after_sql: str | None = Field("", alias="before_after.after")
    enable_after_sql_node: str | None = Field("", alias="before_after.after_node")
    enable_before_sql: str | None = Field("", alias="before_after.before")
    enable_before_sql_node: str | None = Field("", alias="before_after.before_node")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execution_mode: JDBC.ExecutionMode | None = Field(JDBC.ExecutionMode.default_par, alias="execmode")
    fail_on_error_after_sql: bool | None = Field(True, alias="before_after.after.fail_on_error")
    fail_on_error_after_sql_node: bool | None = Field(True, alias="before_after.after_node.fail_on_error")
    fail_on_error_before_sql: bool | None = Field(True, alias="before_after.before.fail_on_error")
    fail_on_error_before_sql_node: bool | None = Field(True, alias="before_after.before_node.fail_on_error")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    generate_unicode_type_columns: bool | None = Field(False, alias="generate_unicode_columns")
    has_reject_output: bool | None = Field(False, alias="has_reject_output")
    heap_size: int | None = Field(256, alias="heap_size")
    hide: bool | None = Field(False, alias="hide")
    infer_schema: bool | None = Field(True, alias="rcp")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    input_link_ordering: list | None = Field(
        [{"link_label": "0", "link_name": "Link_24"}], alias="InputlinkOrderingList"
    )
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    is_reject_output: bool | None = Field(False, alias="is_reject_output")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    key_column_names: str | None = Field(None, alias="key_column_names")
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
    partition_type: JDBC.PartitionType | None = Field(JDBC.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: JDBC.PreservePartitioning | None = Field(
        JDBC.PreservePartitioning.default_propagate, alias="preserve"
    )
    push_filters: str | None = Field(None, alias="push_filters")
    pushed_filters: str | None = Field(None, alias="pushed_filters")
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    read_method: JDBC.ReadMethod | None = Field(JDBC.ReadMethod.general, alias="read_mode")
    reject_condition_row_not_deleted: bool | None = Field(False, alias="reject_condition_row_not_deleted")
    reject_condition_row_not_inserted: bool | None = Field(False, alias="reject_condition_row_not_inserted")
    reject_condition_row_not_updated: bool | None = Field(False, alias="reject_condition_row_not_updated")
    reject_condition_sql_error: bool | None = Field(False, alias="reject_condition_sql_error")
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_from_link: int | None = Field(None, alias="reject_from_link")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: JDBC.RejectUses | None = Field(JDBC.RejectUses.rows, alias="reject_uses")
    rejected_filters: str | None = Field(None, alias="rejected_filters")
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    schema_name: str | None = Field(None, alias="schema_name")
    select_statement: str = Field(None, alias="select_statement")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: JDBC.KeyColSelect | None = Field(JDBC.KeyColSelect.default, alias="keyColSelect")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    static_statement: str = Field(None, alias="static_statement")
    table_action: JDBC.TableAction | None = Field(JDBC.TableAction.append, alias="table_action")
    table_name: str = Field(None, alias="table_name")
    truncate_statement: str | None = Field(None, alias="truncate_statement")
    trust_all_ssl_certificates: bool | None = Field(False, alias="trust_all_ssl_cert")
    unique: bool | None = Field(None, alias="part_unique")
    update_statement: str | None = Field(None, alias="update_statement")
    use_column_name_in_the_statements: bool | None = Field(None, alias="use_column_name")
    write_mode: JDBC.WriteMode | None = Field(JDBC.WriteMode.insert, alias="write_mode")

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
            include.add("ds_before_after_before_sql_node_fail_on_error")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node_fail_on_error")
        )
        (
            include.add("ds_sql_select_statement")
            if (not self.ds_generate_sql)
            else exclude.add("ds_sql_select_statement")
        )
        (
            include.add("ds_before_after_after_sql")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql")
        )
        (
            include.add("ds_session_report_schema_mismatch")
            if (self.ds_generate_sql)
            else exclude.add("ds_session_report_schema_mismatch")
        )
        (
            include.add("ds_before_after_before_sql_fail_on_error")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_fail_on_error")
        )
        (
            include.add("ds_before_after_before_sql")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql")
        )
        (
            include.add("ds_sql_enable_partitioned_reads")
            if (not self.ds_generate_sql)
            else exclude.add("ds_sql_enable_partitioned_reads")
        )
        (
            include.add("ds_before_after_after_sql_node")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node")
        )
        (
            include.add("ds_transaction_begin_end_begin_sql")
            if (self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_begin_sql")
        )
        (
            include.add("ds_before_after_before_sql_read_from_file_before_sql")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_read_from_file_before_sql")
        )
        include.add("ds_table_name") if (self.ds_generate_sql) else exclude.add("ds_table_name")
        (
            include.add("ds_before_after_after_sql_fail_on_error")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_fail_on_error")
        )
        (
            include.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
            if (self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
        )
        (
            include.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
        )
        (
            include.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
            if (self.ds_session_character_set_for_non_unicode_columns == "custom")
            else exclude.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
        )
        (
            include.add("ds_transaction_begin_end_end_sql")
            if (self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_end_sql")
        )
        (
            include.add("ds_before_after_after_sql_read_from_file_after_sql")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_read_from_file_after_sql")
        )
        (
            include.add("ds_before_after_before_sql_node_read_from_file_before_sql_node")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node_read_from_file_before_sql_node")
        )
        (
            include.add("ds_before_after_after_sql_node_fail_on_error")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node_fail_on_error")
        )
        (
            include.add("ds_before_after_before_sql_node")
            if (self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node")
        )
        (
            include.add("ds_sql_select_statement_read_from_file_select")
            if (not self.ds_generate_sql)
            else exclude.add("ds_sql_select_statement_read_from_file_select")
        )
        include.add("ds_limit_rows_limit") if (self.ds_limit_rows) else exclude.add("ds_limit_rows_limit")
        (
            include.add("select_statement")
            if (
                ((not self.table_name))
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
            include.add("catalog_name")
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
            else exclude.add("catalog_name")
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
            include.add("ds_sql_select_statement")
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
            else exclude.add("ds_sql_select_statement")
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
        (
            include.add("ds_session_report_schema_mismatch")
            if (

                    (((self.ds_generate_sql)) or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_session_report_schema_mismatch")
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
            include.add("select_statement")
            if (

                    (
                        (
                            (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
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
            include.add("ds_sql_enable_partitioned_reads")
            if (

                    (((not self.ds_generate_sql)) or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_sql_enable_partitioned_reads")
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
            include.add("ds_transaction_begin_end_begin_sql")
            if (

                    (
                        (
                            (
                                ((self.ds_transaction_begin_end))
                                or ((self.ds_transaction_begin_end and "#" in str(self.ds_transaction_begin_end)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_transaction_begin_end_begin_sql")
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
            include.add("ds_table_name")
            if (

                    (((self.ds_generate_sql)) or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_name")
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
            include.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
            if (

                    (
                        (
                            (
                                ((self.ds_transaction_begin_end))
                                or ((self.ds_transaction_begin_end and "#" in str(self.ds_transaction_begin_end)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
        )
        (
            include.add("catalog_name")
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
            else exclude.add("catalog_name")
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
            include.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
            if (

                    (
                        (
                            (
                                ((self.ds_session_character_set_for_non_unicode_columns == "custom"))
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
            include.add("ds_transaction_begin_end_end_sql")
            if (

                    (
                        (
                            (
                                ((self.ds_transaction_begin_end))
                                or ((self.ds_transaction_begin_end and "#" in str(self.ds_transaction_begin_end)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_transaction_begin_end_end_sql")
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
            include.add("ds_sql_select_statement_read_from_file_select")
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
            else exclude.add("ds_sql_select_statement_read_from_file_select")
        )
        (
            include.add("ds_limit_rows_limit")
            if (

                    (((((self.ds_limit_rows)) or ((self.ds_limit_rows and "#" in str(self.ds_limit_rows))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_limit_rows_limit")
        )

        include.add("ds_java_heap_size") if (not self.ds_use_datastage) else exclude.add("ds_java_heap_size")
        include.add("pushed_filters") if (not self.ds_use_datastage) else exclude.add("pushed_filters")
        (
            include.add("ds_session_default_length_for_columns")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_default_length_for_columns")
        )
        (
            include.add("ds_transaction_isolation_level")
            if (self.ds_use_datastage)
            else exclude.add("ds_transaction_isolation_level")
        )
        (
            include.add("ds_session_keep_conductor_connection_alive")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_keep_conductor_connection_alive")
        )
        include.add("rejected_filters") if (not self.ds_use_datastage) else exclude.add("rejected_filters")
        (
            include.add("ds_session_fetch_size")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_fetch_size")
        )
        (
            include.add("ds_session_character_set_for_non_unicode_columns")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_character_set_for_non_unicode_columns")
        )
        include.add("heap_size") if (self.ds_use_datastage) else exclude.add("heap_size")
        (
            include.add("ds_sql_select_statement_other_clause")
            if (self.ds_use_datastage)
            else exclude.add("ds_sql_select_statement_other_clause")
        )
        (
            include.add("ds_transaction_autocommit_mode")
            if (self.ds_use_datastage)
            else exclude.add("ds_transaction_autocommit_mode")
        )
        (
            include.add("fail_on_error_after_sql_node")
            if (not self.ds_use_datastage)
            else exclude.add("fail_on_error_after_sql_node")
        )
        (
            include.add("ds_enable_quoted_i_ds")
            if (self.ds_use_datastage)
            else exclude.add("ds_enable_quoted_i_ds")
        )
        (
            include.add("ds_session_generate_all_columns_as_unicode")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_generate_all_columns_as_unicode")
        )
        (
            include.add("ds_sql_select_statement_where_clause")
            if (self.ds_use_datastage)
            else exclude.add("ds_sql_select_statement_where_clause")
        )
        (
            include.add("fail_on_error_before_sql")
            if (not self.ds_use_datastage)
            else exclude.add("fail_on_error_before_sql")
        )
        include.add("read_method") if (not self.ds_use_datastage) else exclude.add("read_method")
        (
            include.add("ds_session_default_length_for_long_columns")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_default_length_for_long_columns")
        )
        (
            include.add("enable_after_sql_node")
            if (not self.ds_use_datastage)
            else exclude.add("enable_after_sql_node")
        )
        (
            include.add("fail_on_error_before_sql_node")
            if (not self.ds_use_datastage)
            else exclude.add("fail_on_error_before_sql_node")
        )
        (
            include.add("ds_transaction_begin_end")
            if (self.ds_use_datastage)
            else exclude.add("ds_transaction_begin_end")
        )
        include.add("ds_read_mode") if (self.ds_use_datastage) else exclude.add("ds_read_mode")
        include.add("enable_before_sql") if (not self.ds_use_datastage) else exclude.add("enable_before_sql")
        (
            include.add("ds_session_array_size")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_array_size")
        )
        (
            include.add("ds_transaction_end_of_wave")
            if (self.ds_use_datastage)
            else exclude.add("ds_transaction_end_of_wave")
        )
        include.add("byte_limit") if (not self.ds_use_datastage) else exclude.add("byte_limit")
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
        include.add("ds_limit_rows") if (self.ds_use_datastage) else exclude.add("ds_limit_rows")
        (
            include.add("ds_transaction_record_count")
            if (self.ds_use_datastage)
            else exclude.add("ds_transaction_record_count")
        )
        (
            include.add("ds_session_fail_on_truncation")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_fail_on_truncation")
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
        include.add("use_column_name_in_the_statements") if (()) else exclude.add("use_column_name_in_the_statements")
        include.add("trust_all_ssl_certificates") if (()) else exclude.add("trust_all_ssl_certificates")
        (
            include.add("ds_sql_select_statement_read_from_file_select")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_sql_select_statement_read_from_file_select")
        )
        (
            include.add("ds_limit_rows_limit")
            if (self.ds_limit_rows == "true" or self.ds_limit_rows)
            else exclude.add("ds_limit_rows_limit")
        )
        (
            include.add("ds_before_after_before_sql_node")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node")
        )
        (
            include.add("ds_before_after_after_sql_read_from_file_after_sql")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_read_from_file_after_sql")
        )
        (
            include.add("ds_before_after_before_sql")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql")
        )
        (
            include.add("ds_before_after_before_sql_read_from_file_before_sql")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_read_from_file_before_sql")
        )
        (
            include.add("ds_before_after_before_sql_fail_on_error")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_fail_on_error")
        )
        (
            include.add("ds_before_after_before_sql_node_read_from_file_before_sql_node")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node_read_from_file_before_sql_node")
        )
        (
            include.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
            if (self.ds_transaction_begin_end == "true" or self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_run_end_sql_if_no_records_processed")
        )
        (
            include.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node_read_from_file_after_sql_node")
        )
        (
            include.add("catalog_name")
            if (not self.select_statement)
            and (
                self.read_method
                and (
                    (hasattr(self.read_method, "value") and self.read_method.value == "general")
                    or (self.read_method == "general")
                )
            )
            else exclude.add("catalog_name")
        )
        (
            include.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
            if (self.ds_session_character_set_for_non_unicode_columns == "custom")
            else exclude.add("ds_session_character_set_for_non_unicode_columns_character_set_name")
        )
        (
            include.add("ds_session_report_schema_mismatch")
            if (self.ds_generate_sql == "true" or self.ds_generate_sql)
            else exclude.add("ds_session_report_schema_mismatch")
        )
        (
            include.add("ds_sql_enable_partitioned_reads")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_sql_enable_partitioned_reads")
        )
        (
            include.add("ds_before_after_after_sql")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql")
        )
        (
            include.add("ds_table_name")
            if (self.ds_generate_sql == "true" or self.ds_generate_sql)
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_before_after_after_sql_node")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node")
        )
        (
            include.add("ds_before_after_before_sql_node_fail_on_error")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_before_sql_node_fail_on_error")
        )
        (
            include.add("ds_before_after_after_sql_fail_on_error")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_fail_on_error")
        )
        (
            include.add("ds_transaction_begin_end_begin_sql")
            if (self.ds_transaction_begin_end == "true" or self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_begin_sql")
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
            include.add("ds_before_after_after_sql_node_fail_on_error")
            if (self.ds_before_after == "true" or self.ds_before_after)
            else exclude.add("ds_before_after_after_sql_node_fail_on_error")
        )
        (
            include.add("ds_transaction_begin_end_end_sql")
            if (self.ds_transaction_begin_end == "true" or self.ds_transaction_begin_end)
            else exclude.add("ds_transaction_begin_end_end_sql")
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
            if (not self.table_name)
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
            include.add("ds_sql_select_statement")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            else exclude.add("ds_sql_select_statement")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("ds_table_action_generate_truncate_statement_fail_on_error")
            if (self.ds_table_action == "truncate")
            else exclude.add("ds_table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("ds_sql_delete_statement_read_from_file_delete")
            if (
                ((not self.ds_generate_sql))
                and (((self.ds_write_mode == "delete")) or (self.ds_write_mode == "delete_then_insert"))
            )
            else exclude.add("ds_sql_delete_statement_read_from_file_delete")
        )
        (
            include.add("ds_session_batch_size")
            if (
                (
                    ((self.ds_write_mode == "custom"))
                    or ((self.ds_write_mode == "delete"))
                    or ((self.ds_write_mode == "insert"))
                    or ((self.ds_write_mode == "update"))
                )
                and (not self.has_reject_output)
            )
            else exclude.add("ds_session_batch_size")
        )
        (
            include.add("ds_table_action_generate_drop_statement_drop_statement")
            if (((not self.ds_table_action_generate_drop_statement)) and (self.ds_table_action == "replace"))
            else exclude.add("ds_table_action_generate_drop_statement_drop_statement")
        )
        (
            include.add("ds_sql_insert_statement")
            if (
                ((not self.ds_generate_sql))
                and (
                    ((self.ds_write_mode == "delete_then_insert"))
                    or (self.ds_write_mode == "insert")
                    or (self.ds_write_mode == "insert_new_rows_only")
                    or (self.ds_write_mode == "insert_then_update")
                    or (self.ds_write_mode == "update_then_insert")
                )
            )
            else exclude.add("ds_sql_insert_statement")
        )
        (
            include.add("ds_sql_custom_statements_read_from_file_custom")
            if (self.ds_write_mode == "custom")
            else exclude.add("ds_sql_custom_statements_read_from_file_custom")
        )
        (
            include.add("ds_table_name")
            if (
                ((self.ds_generate_sql))
                or (self.ds_table_action_generate_create_statement)
                or (self.ds_table_action_generate_drop_statement)
                or (self.ds_table_action_generate_truncate_statement)
            )
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_truncate_statement")
            if (
                ((not self.ds_table_action_generate_truncate_statement)) and (self.ds_table_action == "truncate")
            )
            else exclude.add("ds_table_action_generate_truncate_statement_truncate_statement")
        )
        (
            include.add("ds_table_action_generate_drop_statement_fail_on_error")
            if (self.ds_table_action == "replace")
            else exclude.add("ds_table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("ds_table_action_generate_create_statement_fail_on_error")
            if (((self.ds_table_action == "create")) or (self.ds_table_action == "replace"))
            else exclude.add("ds_table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("ds_sql_custom_statements")
            if (self.ds_write_mode == "custom")
            else exclude.add("ds_sql_custom_statements")
        )
        (
            include.add("ds_table_action_generate_create_statement_create_statement")
            if (
                ((not self.ds_table_action_generate_create_statement))
                and (((self.ds_table_action == "create")) or (self.ds_table_action == "replace"))
            )
            else exclude.add("ds_table_action_generate_create_statement_create_statement")
        )
        (
            include.add("ds_sql_insert_statement_read_from_file_insert")
            if (
                ((not self.ds_generate_sql))
                and (
                    ((self.ds_write_mode == "delete_then_insert"))
                    or (self.ds_write_mode == "insert")
                    or (self.ds_write_mode == "insert_new_rows_only")
                    or (self.ds_write_mode == "insert_then_update")
                    or (self.ds_write_mode == "update_then_insert")
                )
            )
            else exclude.add("ds_sql_insert_statement_read_from_file_insert")
        )
        (
            include.add("ds_sql_delete_statement")
            if (
                ((not self.ds_generate_sql))
                and (((self.ds_write_mode == "delete")) or (self.ds_write_mode == "delete_then_insert"))
            )
            else exclude.add("ds_sql_delete_statement")
        )
        (
            include.add("ds_sql_update_statement")
            if (
                ((not self.ds_generate_sql))
                and (
                    ((self.ds_write_mode == "insert_then_update"))
                    or (self.ds_write_mode == "update")
                    or (self.ds_write_mode == "update_then_insert")
                )
            )
            else exclude.add("ds_sql_update_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement")
            if (((self.ds_table_action == "create")) or (self.ds_table_action == "replace"))
            else exclude.add("ds_table_action_generate_create_statement")
        )
        (
            include.add("ds_sql_update_statement_read_from_file_update")
            if (
                ((not self.ds_generate_sql))
                and (
                    ((self.ds_write_mode == "insert_then_update"))
                    or (self.ds_write_mode == "update")
                    or (self.ds_write_mode == "update_then_insert")
                )
            )
            else exclude.add("ds_sql_update_statement_read_from_file_update")
        )
        (
            include.add("ds_table_action_generate_truncate_statement")
            if (self.ds_table_action == "truncate")
            else exclude.add("ds_table_action_generate_truncate_statement")
        )
        (
            include.add("ds_generate_sql")
            if (

                    ((self.ds_write_mode == "delete"))
                    or (self.ds_write_mode == "delete_then_insert")
                    or (self.ds_write_mode == "insert")
                    or (self.ds_write_mode == "insert_new_rows_only")
                    or (self.ds_write_mode == "insert_then_update")
                    or (self.ds_write_mode == "update")
                    or (self.ds_write_mode == "update_then_insert")

            )
            else exclude.add("ds_generate_sql")
        )
        (
            include.add("ds_table_action_generate_drop_statement")
            if (self.ds_table_action == "replace")
            else exclude.add("ds_table_action_generate_drop_statement")
        )
        (
            include.add("ds_table_action_table_action_first")
            if (

                    ((self.ds_table_action == "create"))
                    or (self.ds_table_action == "replace")
                    or (self.ds_table_action == "truncate")

            )
            else exclude.add("ds_table_action_table_action_first")
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
            include.add("truncate_statement")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "merge")
                                or (self.write_mode == "merge")
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
            else exclude.add("truncate_statement")
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
            include.add("catalog_name")
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
            else exclude.add("catalog_name")
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
            else exclude.add("key_column_names")
        )
        (
            include.add("static_statement")
            if (
                (
                    ((not self.catalog_name))
                    and (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "static_statement")
                                or (self.write_mode == "static_statement")
                            )
                        )
                    )
                )
                and (
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
            )
            else exclude.add("static_statement")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_fail_on_error")
            if (

                    (
                        ((self.ds_table_action == "truncate"))
                        or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("ds_sql_delete_statement_read_from_file_delete")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "delete"))
                                or ((self.ds_write_mode == "delete_then_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_sql_delete_statement_read_from_file_delete")
        )
        (
            include.add("ds_session_batch_size")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "custom"))
                                or ((self.ds_write_mode == "delete"))
                                or ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "update"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and ((not self.has_reject_output))
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_session_batch_size")
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
                            and (
                                ((self.ds_table_action == "replace"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_drop_statement_drop_statement")
        )
        (
            include.add("ds_sql_insert_statement")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "delete_then_insert"))
                                or ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "insert_new_rows_only"))
                                or ((self.ds_write_mode == "insert_then_update"))
                                or ((self.ds_write_mode == "update_then_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_sql_insert_statement")
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
            include.add("ds_sql_custom_statements_read_from_file_custom")
            if (

                    (((self.ds_write_mode == "custom")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_sql_custom_statements_read_from_file_custom")
        )
        (
            include.add("ds_table_name")
            if (

                    (
                        ((self.ds_generate_sql))
                        or ((self.ds_table_action_generate_create_statement))
                        or ((self.ds_table_action_generate_drop_statement))
                        or ((self.ds_table_action_generate_truncate_statement))
                        or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
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
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_name")
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
                            and (
                                ((self.ds_table_action == "truncate"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_truncate_statement_truncate_statement")
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
            include.add("ds_table_action_generate_drop_statement_fail_on_error")
            if (

                    (
                        ((self.ds_table_action == "replace"))
                        or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("ds_table_action_generate_create_statement_fail_on_error")
            if (

                    (
                        ((self.ds_table_action == "create"))
                        or ((self.ds_table_action == "replace"))
                        or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("truncate_statement")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.table_action
                                        and (
                                            (
                                                hasattr(self.table_action, "value")
                                                and self.table_action.value == "truncate"
                                            )
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
            else exclude.add("truncate_statement")
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
            include.add("ds_sql_custom_statements")
            if (

                    (((self.ds_write_mode == "custom")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_sql_custom_statements")
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
                            and (
                                ((self.ds_table_action == "create"))
                                or ((self.ds_table_action == "replace"))
                                or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement_create_statement")
        )
        (
            include.add("ds_sql_insert_statement_read_from_file_insert")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "delete_then_insert"))
                                or ((self.ds_write_mode == "insert"))
                                or ((self.ds_write_mode == "insert_new_rows_only"))
                                or ((self.ds_write_mode == "insert_then_update"))
                                or ((self.ds_write_mode == "update_then_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_sql_insert_statement_read_from_file_insert")
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
            include.add("catalog_name")
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
            else exclude.add("catalog_name")
        )
        (
            include.add("ds_sql_delete_statement")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "delete"))
                                or ((self.ds_write_mode == "delete_then_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_sql_delete_statement")
        )
        (
            include.add("ds_sql_update_statement")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "insert_then_update"))
                                or ((self.ds_write_mode == "update"))
                                or ((self.ds_write_mode == "update_then_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_sql_update_statement")
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
            include.add("ds_table_action_generate_create_statement")
            if (

                    (
                        ((self.ds_table_action == "create"))
                        or ((self.ds_table_action == "replace"))
                        or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_create_statement")
        )
        (
            include.add("ds_sql_update_statement_read_from_file_update")
            if (

                    (
                        (
                            (
                                ((not self.ds_generate_sql))
                                or ((self.ds_generate_sql and "#" in str(self.ds_generate_sql)))
                            )
                            and (
                                ((self.ds_write_mode == "insert_then_update"))
                                or ((self.ds_write_mode == "update"))
                                or ((self.ds_write_mode == "update_then_insert"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_sql_update_statement_read_from_file_update")
        )
        (
            include.add("ds_table_action_generate_truncate_statement")
            if (

                    (
                        ((self.ds_table_action == "truncate"))
                        or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_truncate_statement")
        )
        (
            include.add("ds_generate_sql")
            if (

                    (
                        ((self.ds_write_mode == "delete"))
                        or ((self.ds_write_mode == "delete_then_insert"))
                        or ((self.ds_write_mode == "insert"))
                        or ((self.ds_write_mode == "insert_new_rows_only"))
                        or ((self.ds_write_mode == "insert_then_update"))
                        or ((self.ds_write_mode == "update"))
                        or ((self.ds_write_mode == "update_then_insert"))
                        or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_generate_sql")
        )
        (
            include.add("ds_table_action_generate_drop_statement")
            if (

                    (
                        ((self.ds_table_action == "replace"))
                        or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_generate_drop_statement")
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
            else exclude.add("key_column_names")
        )
        (
            include.add("ds_table_action_table_action_first")
            if (

                    (
                        ((self.ds_table_action == "create"))
                        or ((self.ds_table_action == "replace"))
                        or ((self.ds_table_action == "truncate"))
                        or ((self.ds_table_action and "#" in str(self.ds_table_action)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_table_action_table_action_first")
        )
        (
            include.add("static_statement")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        ((not self.catalog_name))
                                        or ((self.catalog_name and "#" in str(self.catalog_name)))
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
                            and (
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
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("static_statement")
        )
        include.add("write_mode") if (not self.ds_use_datastage) else exclude.add("write_mode")
        (
            include.add("ds_session_drop_unmatched_fields")
            if (self.ds_use_datastage)
            else exclude.add("ds_session_drop_unmatched_fields")
        )
        include.add("ds_table_action") if (self.ds_use_datastage) else exclude.add("ds_table_action")
        include.add("ds_write_mode") if (self.ds_use_datastage) else exclude.add("ds_write_mode")
        (
            include.add("ds_table_action_table_action_first")
            if (
                self.ds_table_action
                and "create" in str(self.ds_table_action)
                or self.ds_table_action
                and "replace" in str(self.ds_table_action)
                or self.ds_table_action
                and "truncate" in str(self.ds_table_action)
            )
            else exclude.add("ds_table_action_table_action_first")
        )
        (
            include.add("key_column_names")
            if ((not self.update_statement) and (not self.static_statement))
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
            else exclude.add("key_column_names")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_truncate_statement")
            if (
                self.ds_table_action_generate_truncate_statement == "false"
                or not self.ds_table_action_generate_truncate_statement
            )
            and (self.ds_table_action == "truncate")
            else exclude.add("ds_table_action_generate_truncate_statement_truncate_statement")
        )
        (
            include.add("ds_table_action_generate_create_statement_fail_on_error")
            if (
                self.ds_table_action
                and "create" in str(self.ds_table_action)
                or self.ds_table_action
                and "replace" in str(self.ds_table_action)
            )
            else exclude.add("ds_table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("ds_table_action_generate_create_statement_create_statement")
            if (
                self.ds_table_action_generate_create_statement == "false"
                or not self.ds_table_action_generate_create_statement
            )
            and (
                self.ds_table_action
                and "create" in str(self.ds_table_action)
                and self.ds_table_action
                and "replace" in str(self.ds_table_action)
            )
            else exclude.add("ds_table_action_generate_create_statement_create_statement")
        )
        (
            include.add("ds_table_action_generate_drop_statement_drop_statement")
            if (
                self.ds_table_action_generate_drop_statement == "false"
                or not self.ds_table_action_generate_drop_statement
            )
            and (self.ds_table_action == "replace")
            else exclude.add("ds_table_action_generate_drop_statement_drop_statement")
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
            include.add("ds_sql_custom_statements")
            if (self.ds_write_mode == "custom")
            else exclude.add("ds_sql_custom_statements")
        )
        (
            include.add("ds_sql_update_statement")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (
                self.ds_write_mode
                and "insert_then_update" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "update" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "update_then_insert" in str(self.ds_write_mode)
            )
            else exclude.add("ds_sql_update_statement")
        )
        (
            include.add("ds_table_action_generate_truncate_statement")
            if (self.ds_table_action == "truncate")
            else exclude.add("ds_table_action_generate_truncate_statement")
        )
        (
            include.add("catalog_name")
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
            else exclude.add("catalog_name")
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
            include.add("ds_table_action_generate_drop_statement")
            if (self.ds_table_action == "replace")
            else exclude.add("ds_table_action_generate_drop_statement")
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
            include.add("ds_sql_custom_statements_read_from_file_custom")
            if (self.ds_write_mode == "custom")
            else exclude.add("ds_sql_custom_statements_read_from_file_custom")
        )
        (
            include.add("static_statement")
            if (
                (not self.catalog_name)
                and (
                    self.write_mode
                    and (
                        (hasattr(self.write_mode, "value") and self.write_mode.value == "static_statement")
                        or (self.write_mode == "static_statement")
                    )
                )
            )
            and (
                (not self.schema_name)
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
            include.add("ds_table_name")
            if (self.ds_generate_sql == "true" or self.ds_generate_sql)
            or (
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
            else exclude.add("ds_table_name")
        )
        (
            include.add("ds_table_action_generate_truncate_statement_fail_on_error")
            if (self.ds_table_action == "truncate")
            else exclude.add("ds_table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("ds_sql_insert_statement_read_from_file_insert")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (
                self.ds_write_mode
                and "delete_then_insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert_new_rows_only" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert_then_update" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "update_then_insert" in str(self.ds_write_mode)
            )
            else exclude.add("ds_sql_insert_statement_read_from_file_insert")
        )
        (
            include.add("ds_table_action_generate_create_statement")
            if (
                self.ds_table_action
                and "create" in str(self.ds_table_action)
                or self.ds_table_action
                and "replace" in str(self.ds_table_action)
            )
            else exclude.add("ds_table_action_generate_create_statement")
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
            include.add("truncate_statement")
            if (
                self.table_action
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
            else exclude.add("truncate_statement")
        )
        (
            include.add("ds_sql_insert_statement")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (
                self.ds_write_mode
                and "delete_then_insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert_new_rows_only" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert_then_update" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "update_then_insert" in str(self.ds_write_mode)
            )
            else exclude.add("ds_sql_insert_statement")
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
            include.add("ds_table_action_generate_drop_statement_fail_on_error")
            if (self.ds_table_action == "replace")
            else exclude.add("ds_table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("ds_session_batch_size")
            if (
                self.ds_write_mode
                and "custom" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "delete" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "update" in str(self.ds_write_mode)
            )
            and (self.has_reject_output == "false" or not self.has_reject_output)
            else exclude.add("ds_session_batch_size")
        )
        (
            include.add("ds_sql_update_statement_read_from_file_update")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (
                self.ds_write_mode
                and "insert_then_update" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "update" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "update_then_insert" in str(self.ds_write_mode)
            )
            else exclude.add("ds_sql_update_statement_read_from_file_update")
        )
        (
            include.add("ds_generate_sql")
            if (
                self.ds_write_mode
                and "delete" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "delete_then_insert" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "insert" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "insert_new_rows_only" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "insert_then_update" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "update" in str(self.ds_write_mode)
                or self.ds_write_mode
                and "update_then_insert" in str(self.ds_write_mode)
            )
            else exclude.add("ds_generate_sql")
        )
        (
            include.add("ds_sql_delete_statement_read_from_file_delete")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (
                self.ds_write_mode
                and "delete" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "delete_then_insert" in str(self.ds_write_mode)
            )
            else exclude.add("ds_sql_delete_statement_read_from_file_delete")
        )
        (
            include.add("ds_sql_delete_statement")
            if (self.ds_generate_sql == "false" or not self.ds_generate_sql)
            and (
                self.ds_write_mode
                and "delete" in str(self.ds_write_mode)
                and self.ds_write_mode
                and "delete_then_insert" in str(self.ds_write_mode)
            )
            else exclude.add("ds_sql_delete_statement")
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
            "catalog_name",
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
            "ds_enable_quoted_i_ds",
            "ds_generate_sql",
            "ds_java_heap_size",
            "ds_limit_rows",
            "ds_limit_rows_limit",
            "ds_read_mode",
            "ds_record_ordering",
            "ds_record_ordering_properties",
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
            "ds_sql_enable_partitioned_reads",
            "ds_sql_select_statement",
            "ds_sql_select_statement_other_clause",
            "ds_sql_select_statement_read_from_file_select",
            "ds_sql_select_statement_where_clause",
            "ds_table_name",
            "ds_transaction_autocommit_mode",
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
            "heap_size",
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
            "use_column_name_in_the_statements",
        }
        required = {
            "current_output_link_type",
            "ds_session_character_set_for_non_unicode_columns_character_set_name",
            "ds_sql_select_statement",
            "ds_table_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "jdbc_driver_class",
            "jdbc_url",
            "output_acp_should_hide",
            "select_statement",
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
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "catalog_name",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "create_statement",
            "current_output_link_type",
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
            "ds_enable_quoted_i_ds",
            "ds_generate_sql",
            "ds_java_heap_size",
            "ds_record_ordering",
            "ds_record_ordering_properties",
            "ds_session_array_size",
            "ds_session_batch_size",
            "ds_session_character_set_for_non_unicode_columns",
            "ds_session_character_set_for_non_unicode_columns_character_set_name",
            "ds_session_default_length_for_columns",
            "ds_session_default_length_for_long_columns",
            "ds_session_drop_unmatched_fields",
            "ds_session_fail_on_truncation",
            "ds_session_keep_conductor_connection_alive",
            "ds_session_report_schema_mismatch",
            "ds_sql_custom_statements",
            "ds_sql_custom_statements_read_from_file_custom",
            "ds_sql_delete_statement",
            "ds_sql_delete_statement_read_from_file_delete",
            "ds_sql_insert_statement",
            "ds_sql_insert_statement_read_from_file_insert",
            "ds_sql_update_statement",
            "ds_sql_update_statement_read_from_file_update",
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
            "ds_transaction_autocommit_mode",
            "ds_transaction_begin_end",
            "ds_transaction_begin_end_begin_sql",
            "ds_transaction_begin_end_end_sql",
            "ds_transaction_begin_end_run_end_sql_if_no_records_processed",
            "ds_transaction_isolation_level",
            "ds_transaction_record_count",
            "ds_use_datastage",
            "ds_write_mode",
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
            "has_reject_output",
            "heap_size",
            "hide",
            "input_count",
            "input_link_description",
            "input_link_ordering",
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
            "truncate_statement",
            "unique",
            "update_statement",
            "use_column_name_in_the_statements",
            "write_mode",
        }
        required = {
            "current_output_link_type",
            "ds_session_character_set_for_non_unicode_columns_character_set_name",
            "ds_sql_delete_statement",
            "ds_sql_insert_statement",
            "ds_sql_update_statement",
            "ds_table_action",
            "ds_table_action_generate_create_statement_create_statement",
            "ds_table_action_generate_drop_statement_drop_statement",
            "ds_table_action_generate_truncate_statement_truncate_statement",
            "ds_table_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "jdbc_driver_class",
            "jdbc_url",
            "output_acp_should_hide",
            "static_statement",
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
                "maxRejectOutputs": 2147483647,
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
