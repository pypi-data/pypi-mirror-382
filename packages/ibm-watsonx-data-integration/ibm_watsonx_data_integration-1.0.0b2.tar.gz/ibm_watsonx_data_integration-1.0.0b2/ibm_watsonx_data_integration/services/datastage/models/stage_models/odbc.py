import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.odbc_connection import OdbcConn
from ibm_watsonx_data_integration.services.datastage.models.enums import ODBC
from pydantic import Field
from typing import ClassVar


class odbc(BaseStage):

    op_name: ClassVar[str] = "ODBCConnectorPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/ODBCConnectorPX.svg"
    label: ClassVar[str] = "ODBC"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: OdbcConn = OdbcConn()
    array_size: int | None = Field(2000, alias="session.array_size")
    autocommit_mode: ODBC.SessionAutocommitMode | None = Field(
        ODBC.SessionAutocommitMode.off, alias="session.autocommit_mode"
    )
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: ODBC.BufModeRonly | None = Field(ODBC.BufModeRonly.default, alias="buf_mode_ronly")
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: ODBC.BufferingMode | None = Field(ODBC.BufferingMode.default, alias="buf_mode")
    character_set: str | None = Field(None, alias="sql.user_defined_sql.file.character_set")
    code_page: ODBC.SessionCodePage | None = Field(ODBC.SessionCodePage.default, alias="session.code_page")
    code_page_name: str = Field(None, alias="session.code_page.code_page_name")
    collecting: ODBC.Collecting | None = Field(ODBC.Collecting.auto, alias="coll_type")
    column_delimiter: ODBC.LoggingLogColumnValuesDelimiter | None = Field(
        ODBC.LoggingLogColumnValuesDelimiter.space, alias="logging.log_column_values.delimiter"
    )
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    columns: str = Field("", alias="session.pass_lob_locator.column")
    combinability_mode: ODBC.CombinabilityMode | None = Field(ODBC.CombinabilityMode.auto, alias="combinability")
    create_table_statement: str = Field("", alias="table_action.generate_create_statement.create_statement")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    default_port: int | None = Field(2638, alias="default_port")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    delete_statement: str = Field(None, alias="sql.delete_statement")
    delimiter: str | None = Field(",", alias="host_port_separator")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    drop_table_statement: str = Field("", alias="table_action.generate_drop_statement.drop_statement")
    drop_unmatched_fields: bool | None = Field(True, alias="session.schema_reconciliation.drop_unmatched_fields")
    ds_record_ordering: ODBC.DSRecordOrdering | None = Field(ODBC.DSRecordOrdering.zero, alias="_record_ordering")
    ds_record_ordering_properties: list | None = Field([], alias="_record_ordering_properties")
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
    end_of_data: bool | None = Field(False, alias="transaction.end_of_wave.end_of_data")
    end_of_wave: ODBC.TransactionEndOfWave | None = Field(
        ODBC.TransactionEndOfWave.none, alias="transaction.end_of_wave"
    )
    execution_mode: ODBC.ExecutionMode | None = Field(ODBC.ExecutionMode.default_par, alias="execmode")
    fail_on_code_page_mismatch: bool | None = Field(
        False, alias="session.schema_reconciliation.fail_on_code_page_mismatch"
    )
    fail_on_error_after_sql: bool | None = Field(True, alias="before_after.after.fail_on_error")
    fail_on_error_before_sql: bool | None = Field(True, alias="before_after.before.fail_on_error")
    fail_on_error_before_sql_node: bool | None = Field(True, alias="before_after.before_node.fail_on_error")
    fail_on_error_for_after_sql_node_statements: bool | None = Field(
        True, alias="before_after.after_node.fail_on_error"
    )
    fail_on_row_error: bool | None = Field(True, alias="session.fail_on_row_error_px")
    fail_on_size_mismatch: bool | None = Field(True, alias="session.schema_reconciliation.fail_on_size_mismatch")
    fail_on_type_mismatch: bool | None = Field(True, alias="session.schema_reconciliation.fail_on_type_mismatch")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    generate_create_statement_at_run_time: bool | None = Field(True, alias="table_action.generate_create_statement")
    generate_drop_statement_at_run_time: bool | None = Field(True, alias="table_action.generate_drop_statement")
    generate_sql_at_runtime: bool | None = Field(False, alias="generate_sql")
    generate_truncate_statement_at_runtime: bool | None = Field(
        True, alias="table_action.generate_truncate_statement"
    )
    has_reference_output: bool | None = Field(False, alias="has_ref_output")
    has_reject_output: bool | None = Field(False, alias="has_reject_output")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    insert_statement: str = Field(None, alias="sql.insert_statement")
    is_reject_output: bool | None = Field(False, alias="is_reject_output")
    isolation_level: ODBC.SessionIsolationLevel | None = Field(
        ODBC.SessionIsolationLevel.read_uncommitted, alias="session.isolation_level"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    limit: int | None = Field(1000, alias="limit_rows.limit")
    limit_number_of_returned_rows: bool | None = Field(False, alias="limit_rows")
    log_column_values_on_first_row_error: bool | None = Field(False, alias="logging.log_column_values")
    log_key_values_only: bool | None = Field(False, alias="logging.log_column_values.log_keys_only")
    log_on_mech: ODBC.LogOnMech = Field(ODBC.LogOnMech.td2, alias="log_on_mech")
    lookup_type: ODBC.LookupType | None = Field(ODBC.LookupType.empty, alias="lookup_type")
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
    partition_type: ODBC.PartitionType | None = Field(ODBC.PartitionType.auto, alias="part_type")
    partitioned_reads_column_name: str = Field(None, alias="sql.enable_partitioning.partitioning_method.key_field")
    partitioned_reads_method: ODBC.SqlEnablePartitioningPartitioningMethod | None = Field(
        ODBC.SqlEnablePartitioningPartitioningMethod.minimum_and_maximum_range,
        alias="sql.enable_partitioning.partitioning_method",
    )
    partitioned_reads_table_name: str = Field(None, alias="sql.enable_partitioning.partitioning_method.table_name")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: ODBC.PreservePartitioning | None = Field(
        ODBC.PreservePartitioning.default_propagate, alias="preserve"
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
    read_select_statement_from_file: bool | None = Field(
        False, alias="sql.select_statement.read_statement_from_file"
    )
    record_count: int | None = Field(2000, alias="transaction.record_count")
    reject_condition_row_not_updated: bool | None = Field(False, alias="reject_condition_row_not_updated")
    reject_condition_sql_error: bool | None = Field(False, alias="reject_condition_sql_error")
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_from_link: int | None = Field(None, alias="reject_from_link")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: ODBC.RejectUses | None = Field(ODBC.RejectUses.rows, alias="reject_uses")
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    schema_name: str | None = Field(None, alias="schema_name")
    select_statement: str = Field(None, alias="sql.select_statement")
    select_statement_column: str | None = Field(None, alias="sql.select_statement.columns.column")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: ODBC.KeyColSelect | None = Field(ODBC.KeyColSelect.default, alias="keyColSelect")
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
    sql_user_defined_sql_fail_on_error: bool | None = Field(True, alias="sql.user_defined_sql.fail_on_error")
    sql_where_clause: str | None = Field(None, alias="sql.where_clause")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    table_action: ODBC.TableAction = Field(ODBC.TableAction.append, alias="table_action")
    table_action_generate_create_statement_fail_on_error: bool | None = Field(
        True, alias="table_action.generate_create_statement.fail_on_error"
    )
    table_action_generate_drop_statement_fail_on_error: bool | None = Field(
        False, alias="table_action.generate_drop_statement.fail_on_error"
    )
    table_action_generate_truncate_statement_fail_on_error: bool | None = Field(
        True, alias="table_action.generate_truncate_statement.fail_on_error"
    )
    table_name: str = Field(None, alias="table_name")
    truncate_table_statement: str = Field("", alias="table_action.generate_truncate_statement.truncate_statement")
    unique: bool | None = Field(None, alias="part_unique")
    update_statement: str = Field(None, alias="sql.update_statement")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    user_defined_sql: ODBC.SqlUserDefinedSql = Field(ODBC.SqlUserDefinedSql.statements, alias="sql.user_defined_sql")
    user_defined_sql_file_name: str = Field(None, alias="sql.user_defined_sql.file")
    user_defined_sql_statements: str = Field(None, alias="sql.user_defined_sql.statements")
    write_mode: ODBC.WriteMode = Field(ODBC.WriteMode.insert, alias="write_mode")

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
            include.add("reject_condition_row_not_updated")
            if (self.is_reject_output)
            else exclude.add("reject_condition_row_not_updated")
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

        include.add("code_page_name") if (self.code_page == "user-specified") else exclude.add("code_page_name")
        (
            include.add("partitioned_reads_table_name")
            if (
                ((self.enable_partitioned_reads))
                and (self.partitioned_reads_method == "minimum_and_maximum_range")
            )
            else exclude.add("partitioned_reads_table_name")
        )
        (
            include.add("sql_other_clause")
            if (self.generate_sql_at_runtime)
            else exclude.add("sql_other_clause")
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
            include.add("fail_on_error_for_after_sql_node_statements")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_for_after_sql_node_statements")
        )
        (
            include.add("sql_where_clause")
            if (self.generate_sql_at_runtime)
            else exclude.add("sql_where_clause")
        )
        include.add("limit") if (self.limit_number_of_returned_rows) else exclude.add("limit")
        (
            include.add("enable_before_sql_node")
            if (self.enable_before_and_after_sql)
            else exclude.add("enable_before_sql_node")
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
            include.add("select_statement")
            if (((not self.table_name)) and (not self.generate_sql_at_runtime))
            else exclude.add("select_statement")
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
        include.add("columns") if (self.enable_lob_references) else exclude.add("columns")
        (
            include.add("enable_before_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("enable_before_sql")
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
            include.add("end_of_data")
            if (((self.end_of_wave == "after")) or (self.end_of_wave == "before"))
            else exclude.add("end_of_data")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("enable_after_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("enable_after_sql")
        )
        (
            include.add("fail_on_error_after_sql")
            if (self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql")
        )
        (
            include.add("partitioned_reads_method")
            if (self.enable_partitioned_reads)
            else exclude.add("partitioned_reads_method")
        )
        (
            include.add("code_page_name")
            if (((self.code_page == "user-specified")) or (self.code_page and "#" in str(self.code_page)))
            else exclude.add("code_page_name")
        )
        (
            include.add("partitioned_reads_table_name")
            if (

                    (
                        ((self.enable_partitioned_reads))
                        or ((self.enable_partitioned_reads and "#" in str(self.enable_partitioned_reads)))
                    )
                    and (
                        ((self.partitioned_reads_method == "minimum_and_maximum_range"))
                        or (self.partitioned_reads_method and "#" in str(self.partitioned_reads_method))
                    )

            )
            else exclude.add("partitioned_reads_table_name")
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
            include.add("fail_on_error_for_after_sql_node_statements")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("fail_on_error_for_after_sql_node_statements")
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
            include.add("limit")
            if (


                        ((self.limit_number_of_returned_rows))
                        or (self.limit_number_of_returned_rows and "#" in str(self.limit_number_of_returned_rows))


            )
            else exclude.add("limit")
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
            include.add("end_of_data")
            if (


                        ((self.end_of_wave == "after"))
                        or (self.end_of_wave == "before")
                        or (self.end_of_wave and "#" in str(self.end_of_wave))


            )
            else exclude.add("end_of_data")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("enable_after_sql")
            if (


                        ((self.enable_before_and_after_sql))
                        or (self.enable_before_and_after_sql and "#" in str(self.enable_before_and_after_sql))


            )
            else exclude.add("enable_after_sql")
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
            include.add("partitioned_reads_method")
            if (


                        ((self.enable_partitioned_reads))
                        or (self.enable_partitioned_reads and "#" in str(self.enable_partitioned_reads))


            )
            else exclude.add("partitioned_reads_method")
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
        include.add("default_port") if (((()) or (())) and (())) else exclude.add("default_port")
        include.add("delimiter") if (((()) or (())) and (())) else exclude.add("delimiter")
        include.add("use_cas_lite_service") if (((()) or (())) and (())) else exclude.add("use_cas_lite_service")
        include.add("default_port") if (()) else exclude.add("default_port")
        include.add("delimiter") if (()) else exclude.add("delimiter")
        include.add("use_cas_lite_service") if (()) else exclude.add("use_cas_lite_service")
        include.add("defer_credentials") if (()) else exclude.add("defer_credentials")
        (
            include.add("fail_on_error_for_after_sql_node_statements")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_for_after_sql_node_statements")
        )
        (
            include.add("read_before_sql_statements_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_before_sql_statements_from_file")
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
            include.add("fail_on_error_before_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql")
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
            include.add("read_before_sql_node_statement_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_before_sql_node_statement_from_file")
        )
        (
            include.add("enable_after_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("enable_after_sql")
        )
        (
            include.add("lookup_type")
            if (self.has_reference_output == "true" or self.has_reference_output)
            else exclude.add("lookup_type")
        )
        (
            include.add("fail_on_error_before_sql_node")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_before_sql_node")
        )
        (
            include.add("partitioned_reads_table_name")
            if (self.enable_partitioned_reads == "true" or self.enable_partitioned_reads)
            and (self.partitioned_reads_method == "minimum_and_maximum_range")
            else exclude.add("partitioned_reads_table_name")
        )
        (
            include.add("sql_where_clause")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("sql_where_clause")
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
            include.add("limit")
            if (self.limit_number_of_returned_rows == "true" or self.limit_number_of_returned_rows)
            else exclude.add("limit")
        )
        (
            include.add("partitioned_reads_method")
            if (self.enable_partitioned_reads == "true" or self.enable_partitioned_reads)
            else exclude.add("partitioned_reads_method")
        )
        (
            include.add("select_statement")
            if (not self.table_name)
            and (self.generate_sql_at_runtime == "false" or not self.generate_sql_at_runtime)
            else exclude.add("select_statement")
        )
        include.add("code_page_name") if (self.code_page == "user-specified") else exclude.add("code_page_name")
        (
            include.add("fail_on_error_after_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("fail_on_error_after_sql")
        )
        (
            include.add("table_name")
            if (not self.select_statement)
            and (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("table_name")
        )
        (
            include.add("sql_other_clause")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
            else exclude.add("sql_other_clause")
        )
        (
            include.add("read_after_sql_statements_from_file")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("read_after_sql_statements_from_file")
        )
        (
            include.add("enable_before_sql")
            if (self.enable_before_and_after_sql == "true" or self.enable_before_and_after_sql)
            else exclude.add("enable_before_sql")
        )
        (
            include.add("columns")
            if (self.enable_lob_references == "true" or self.enable_lob_references)
            else exclude.add("columns")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

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
            include.add("table_name")
            if (
                ((self.generate_sql_at_runtime))
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
            include.add("generate_drop_statement_at_run_time")
            if (


                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                            or (self.table_action == "replace")
                        )


            )
            else exclude.add("generate_drop_statement_at_run_time")
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
            include.add("table_action_generate_drop_statement_fail_on_error")
            if (


                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                            or (self.table_action == "replace")
                        )


            )
            else exclude.add("table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("log_key_values_only")
            if (self.log_column_values_on_first_row_error)
            else exclude.add("log_key_values_only")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
                            )

                    )

            )
            else exclude.add("table_action")
        )
        (
            include.add("table_action_generate_create_statement_fail_on_error")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
                            )

                    )
                )
            )
            else exclude.add("table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("drop_table_statement")
            if (
                ((not self.generate_drop_statement_at_run_time))
                and (

                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                            or (self.table_action == "replace")
                        )

                )
            )
            else exclude.add("drop_table_statement")
        )
        include.add("character_set") if (self.user_defined_sql == "file") else exclude.add("character_set")
        (
            include.add("user_defined_sql_file_name")
            if (self.user_defined_sql == "file")
            else exclude.add("user_defined_sql_file_name")
        )
        (
            include.add("generate_create_statement_at_run_time")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
                            )

                    )
                )
            )
            else exclude.add("generate_create_statement_at_run_time")
        )
        (
            include.add("create_table_statement")
            if (
                ((not self.generate_create_statement_at_run_time))
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                or (self.write_mode == "insert")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                                or (self.write_mode == "insert_new_rows_only")
                            )

                    )
                )
            )
            else exclude.add("create_table_statement")
        )
        (
            include.add("column_delimiter")
            if (self.log_column_values_on_first_row_error)
            else exclude.add("column_delimiter")
        )
        (
            include.add("sql_user_defined_sql_fail_on_error")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                            or (self.write_mode == "user-defined_sql")
                        )


            )
            else exclude.add("sql_user_defined_sql_fail_on_error")
        )
        include.add("fail_on_row_error") if (not self.has_reject_output) else exclude.add("fail_on_row_error")
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
            include.add("truncate_table_statement")
            if (
                ((not self.generate_truncate_statement_at_runtime))
                and (

                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                            or (self.table_action == "truncate")
                        )

                )
            )
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("table_action_generate_truncate_statement_fail_on_error")
            if (


                        self.table_action
                        and (
                            (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                            or (self.table_action == "truncate")
                        )


            )
            else exclude.add("table_action_generate_truncate_statement_fail_on_error")
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
            include.add("table_name")
            if (
                ((self.generate_sql_at_runtime))
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
                or (self.generate_sql_at_runtime and "#" in str(self.generate_sql_at_runtime))
            )
            else exclude.add("table_name")
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
            include.add("generate_drop_statement_at_run_time")
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
            else exclude.add("generate_drop_statement_at_run_time")
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
            include.add("table_action_generate_drop_statement_fail_on_error")
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
            else exclude.add("table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("log_key_values_only")
            if (


                        ((self.log_column_values_on_first_row_error))
                        or (

                                self.log_column_values_on_first_row_error
                                and "#" in str(self.log_column_values_on_first_row_error)

                        )


            )
            else exclude.add("log_key_values_only")
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
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "insert_new_rows_only")
                            or (self.write_mode == "insert_new_rows_only")
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
            include.add("table_action_generate_create_statement_fail_on_error")
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
                                        and self.write_mode.value
                                        and "#" in str(self.write_mode.value)
                                    )
                                    or ("#" in str(self.write_mode))
                                )

                        )
                    )

            )
            else exclude.add("table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("drop_table_statement")
            if (

                    (
                        ((not self.generate_drop_statement_at_run_time))
                        or (
                            (
                                self.generate_drop_statement_at_run_time
                                and "#" in str(self.generate_drop_statement_at_run_time)
                            )
                        )
                    )
                    and (
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

            )
            else exclude.add("drop_table_statement")
        )
        (
            include.add("character_set")
            if (((self.user_defined_sql == "file")) or (self.user_defined_sql and "#" in str(self.user_defined_sql)))
            else exclude.add("character_set")
        )
        (
            include.add("user_defined_sql_file_name")
            if (((self.user_defined_sql == "file")) or (self.user_defined_sql and "#" in str(self.user_defined_sql)))
            else exclude.add("user_defined_sql_file_name")
        )
        (
            include.add("generate_create_statement_at_run_time")
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
                                        and self.write_mode.value
                                        and "#" in str(self.write_mode.value)
                                    )
                                    or ("#" in str(self.write_mode))
                                )

                        )
                    )

            )
            else exclude.add("generate_create_statement_at_run_time")
        )
        (
            include.add("create_table_statement")
            if (

                    (
                        ((not self.generate_create_statement_at_run_time))
                        or (
                            (
                                self.generate_create_statement_at_run_time
                                and "#" in str(self.generate_create_statement_at_run_time)
                            )
                        )
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
            include.add("column_delimiter")
            if (


                        ((self.log_column_values_on_first_row_error))
                        or (

                                self.log_column_values_on_first_row_error
                                and "#" in str(self.log_column_values_on_first_row_error)

                        )


            )
            else exclude.add("column_delimiter")
        )
        (
            include.add("sql_user_defined_sql_fail_on_error")
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
            else exclude.add("sql_user_defined_sql_fail_on_error")
        )
        (
            include.add("fail_on_row_error")
            if (not self.has_reject_output)
            else exclude.add("fail_on_row_error")
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
            include.add("truncate_table_statement")
            if (

                    (
                        ((not self.generate_truncate_statement_at_runtime))
                        or (
                            (
                                self.generate_truncate_statement_at_runtime
                                and "#" in str(self.generate_truncate_statement_at_runtime)
                            )
                        )
                    )
                    and (
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

            )
            else exclude.add("truncate_table_statement")
        )
        (
            include.add("table_action_generate_truncate_statement_fail_on_error")
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
            else exclude.add("table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("fail_on_row_error")
            if (self.has_reject_output == "false" or not self.has_reject_output)
            else exclude.add("fail_on_row_error")
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
            include.add("sql_user_defined_sql_fail_on_error")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "user-defined_sql")
                    or (self.write_mode == "user-defined_sql")
                )
            )
            else exclude.add("sql_user_defined_sql_fail_on_error")
        )
        (
            include.add("drop_table_statement")
            if (
                self.generate_drop_statement_at_run_time == "false" or not self.generate_drop_statement_at_run_time
            )
            and (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                    or (self.table_action == "replace")
                )
            )
            else exclude.add("drop_table_statement")
        )
        (
            include.add("table_action_generate_create_statement_fail_on_error")
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
                )
            )
            else exclude.add("table_action_generate_create_statement_fail_on_error")
        )
        (
            include.add("generate_drop_statement_at_run_time")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                    or (self.table_action == "replace")
                )
            )
            else exclude.add("generate_drop_statement_at_run_time")
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
            include.add("generate_create_statement_at_run_time")
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
                )
            )
            else exclude.add("generate_create_statement_at_run_time")
        )
        (
            include.add("user_defined_sql_file_name")
            if (self.user_defined_sql == "file")
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
            include.add("table_action_generate_drop_statement_fail_on_error")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "replace")
                    or (self.table_action == "replace")
                )
            )
            else exclude.add("table_action_generate_drop_statement_fail_on_error")
        )
        (
            include.add("create_table_statement")
            if (
                self.generate_create_statement_at_run_time == "false"
                or not self.generate_create_statement_at_run_time
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
                        and "insert_new_rows_only" in str(self.write_mode.value)
                    )
                    or ("insert_new_rows_only" in str(self.write_mode))
                )
            )
            else exclude.add("create_table_statement")
        )
        (
            include.add("truncate_table_statement")
            if (
                self.generate_truncate_statement_at_runtime == "false"
                or not self.generate_truncate_statement_at_runtime
            )
            and (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                    or (self.table_action == "truncate")
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
            )
            else exclude.add("table_action")
        )
        include.add("character_set") if (self.user_defined_sql == "file") else exclude.add("character_set")
        (
            include.add("log_key_values_only")
            if (
                self.log_column_values_on_first_row_error == "true" or self.log_column_values_on_first_row_error
            )
            else exclude.add("log_key_values_only")
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
            include.add("table_action_generate_truncate_statement_fail_on_error")
            if (
                self.table_action
                and (
                    (hasattr(self.table_action, "value") and self.table_action.value == "truncate")
                    or (self.table_action == "truncate")
                )
            )
            else exclude.add("table_action_generate_truncate_statement_fail_on_error")
        )
        (
            include.add("column_delimiter")
            if (
                self.log_column_values_on_first_row_error == "true" or self.log_column_values_on_first_row_error
            )
            else exclude.add("column_delimiter")
        )
        (
            include.add("table_name")
            if (self.generate_sql_at_runtime == "true" or self.generate_sql_at_runtime)
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
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "array_size",
            "autocommit_mode",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "code_page",
            "code_page_name",
            "collecting",
            "column_metadata_change_propagation",
            "columns",
            "combinability_mode",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_record_ordering",
            "ds_record_ordering_properties",
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
            "fail_on_code_page_mismatch",
            "fail_on_error_after_sql",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "fail_on_error_for_after_sql_node_statements",
            "fail_on_size_mismatch",
            "fail_on_type_mismatch",
            "flow_dirty",
            "generate_sql_at_runtime",
            "has_reference_output",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "isolation_level",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "limit",
            "limit_number_of_returned_rows",
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
            "partitioned_reads_column_name",
            "partitioned_reads_method",
            "partitioned_reads_table_name",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "preserve_partitioning",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_after_sql_node_statements_from_file",
            "read_after_sql_statements_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statements_from_file",
            "read_select_statement_from_file",
            "record_count",
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
        }
        required = {
            "access_token",
            "authentication_method",
            "client_id",
            "client_secret",
            "cluster_nodes",
            "code_page_name",
            "columns",
            "current_output_link_type",
            "data_source_name",
            "data_source_type",
            "database",
            "dataset",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname_or_ip_address",
            "input_method_for_service_account_key",
            "network_address",
            "output_acp_should_hide",
            "partitioned_reads_column_name",
            "partitioned_reads_table_name",
            "port",
            "project",
            "refresh_token",
            "select_statement",
            "service_account_email",
            "service_account_key_content",
            "service_name",
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
            "array_size",
            "autocommit_mode",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "character_set",
            "code_page",
            "code_page_name",
            "collecting",
            "column_delimiter",
            "column_metadata_change_propagation",
            "combinability_mode",
            "create_table_statement",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "delete_statement",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "drop_table_statement",
            "drop_unmatched_fields",
            "ds_record_ordering",
            "ds_record_ordering_properties",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_and_after_sql",
            "enable_before_sql",
            "enable_before_sql_node",
            "enable_flow_acp_control",
            "enable_quoted_identifiers",
            "enable_schemaless_design",
            "execution_mode",
            "fail_on_code_page_mismatch",
            "fail_on_error_after_sql",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "fail_on_error_for_after_sql_node_statements",
            "fail_on_row_error",
            "fail_on_size_mismatch",
            "fail_on_type_mismatch",
            "flow_dirty",
            "generate_create_statement_at_run_time",
            "generate_drop_statement_at_run_time",
            "generate_sql_at_runtime",
            "generate_truncate_statement_at_runtime",
            "has_reject_output",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "insert_statement",
            "isolation_level",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "log_column_values_on_first_row_error",
            "log_key_values_only",
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
            "read_after_sql_node_statements_from_file",
            "read_after_sql_statements_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statements_from_file",
            "record_count",
            "runtime_column_propagation",
            "schema_name",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
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
            "sql_user_defined_sql_fail_on_error",
            "stable",
            "stage_description",
            "table_action",
            "table_action_generate_create_statement_fail_on_error",
            "table_action_generate_drop_statement_fail_on_error",
            "table_action_generate_truncate_statement_fail_on_error",
            "table_name",
            "truncate_table_statement",
            "unique",
            "update_statement",
            "user_defined_sql",
            "user_defined_sql_file_name",
            "user_defined_sql_statements",
            "write_mode",
        }
        required = {
            "access_token",
            "authentication_method",
            "client_id",
            "client_secret",
            "cluster_nodes",
            "code_page_name",
            "create_table_statement",
            "current_output_link_type",
            "data_source_name",
            "data_source_type",
            "database",
            "dataset",
            "delete_statement",
            "drop_table_statement",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname_or_ip_address",
            "input_method_for_service_account_key",
            "insert_statement",
            "network_address",
            "output_acp_should_hide",
            "port",
            "project",
            "refresh_token",
            "service_account_email",
            "service_account_key_content",
            "service_name",
            "table_action",
            "table_name",
            "truncate_table_statement",
            "update_statement",
            "user_defined_sql",
            "user_defined_sql_file_name",
            "user_defined_sql_statements",
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
