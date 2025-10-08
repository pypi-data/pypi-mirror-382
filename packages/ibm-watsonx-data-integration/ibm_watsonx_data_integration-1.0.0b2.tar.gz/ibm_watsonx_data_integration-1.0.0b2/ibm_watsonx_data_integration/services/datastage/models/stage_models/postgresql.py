import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.postgresql_connection import PostgresqlConn
from ibm_watsonx_data_integration.services.datastage.models.enums import POSTGRESQL
from pydantic import Field
from typing import ClassVar


class postgresql(BaseStage):

    op_name: ClassVar[str] = "postgresql"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/postgresql.svg"
    label: ClassVar[str] = "PostgreSQL"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: PostgresqlConn = PostgresqlConn()
    add_procedure_return_value_to_schema: bool | None = Field(False, alias="add_proccode_column")
    batch_size: int | None = Field(2000, alias="batch_size")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: POSTGRESQL.BufModeRonly | None = Field(POSTGRESQL.BufModeRonly.default, alias="buf_mode_ronly")
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: POSTGRESQL.BufferingMode | None = Field(POSTGRESQL.BufferingMode.default, alias="buf_mode")
    byte_limit: str | None = Field(None, alias="byte_limit")
    call_procedure_statement: str | None = Field(None, alias="call_statement")
    collecting: POSTGRESQL.Collecting | None = Field(POSTGRESQL.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: POSTGRESQL.CombinabilityMode | None = Field(
        POSTGRESQL.CombinabilityMode.auto, alias="combinability"
    )
    create_data_asset: bool | None = Field(False, alias="registerDataAsset")
    create_statement: str | None = Field(None, alias="create_statement")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_asset_name: str = Field(None, alias="dataAssetName")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    default_maximum_length_for_columns: int | None = Field(20000, alias="default_max_string_binary_precision")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    enable_after_sql: str | None = Field("", alias="before_after.after")
    enable_after_sql_node: str | None = Field("", alias="before_after.after_node")
    enable_before_sql: str | None = Field("", alias="before_after.before")
    enable_before_sql_node: str | None = Field("", alias="before_after.before_node")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execute_procedure_for_each_row: bool | None = Field(True, alias="call_each_row")
    execution_mode: POSTGRESQL.ExecutionMode | None = Field(POSTGRESQL.ExecutionMode.default_par, alias="execmode")
    existing_table_action: POSTGRESQL.ExistingTableAction | None = Field(
        POSTGRESQL.ExistingTableAction.append, alias="existing_table_action"
    )
    fail_on_error_after_sql: bool | None = Field(True, alias="before_after.after.fail_on_error")
    fail_on_error_after_sql_node: bool | None = Field(True, alias="before_after.after_node.fail_on_error")
    fail_on_error_before_sql: bool | None = Field(True, alias="before_after.before.fail_on_error")
    fail_on_error_before_sql_node: bool | None = Field(True, alias="before_after.before_node.fail_on_error")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    forward_row_data: bool | None = Field(False, alias="forward_row_data")
    generate_unicode_type_columns: bool | None = Field(False, alias="generate_unicode_columns")
    has_ref_output: bool | None = Field(False, alias="has_ref_output")
    has_reject_output: bool | None = Field(False, alias="has_reject_output")
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
    login_timeout: int | None = Field(None, alias="login_timeout")
    lookup_type: POSTGRESQL.LookupType | None = Field(POSTGRESQL.LookupType.empty, alias="lookup_type")
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
    partition_type: POSTGRESQL.PartitionType | None = Field(POSTGRESQL.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: POSTGRESQL.PreservePartitioning | None = Field(
        POSTGRESQL.PreservePartitioning.default_propagate, alias="preserve"
    )
    proc_param_properties: list | None = Field([], alias="procParamProperties")
    push_filters: str | None = Field(None, alias="push_filters")
    pushed_filters: str | None = Field(None, alias="pushed_filters")
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
    read_method: POSTGRESQL.ReadMethod | None = Field(POSTGRESQL.ReadMethod.general, alias="read_mode")
    read_select_statement_from_file: bool | None = Field(False, alias="select_statement.read_from_file_select")
    read_update_statement_from_file: bool | None = Field(False, alias="update_statement.read_from_file_update")
    reject_condition_row_is_rejected: bool | None = Field(False, alias="reject_condition_row_is_rejected")
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_from_link: int | None = Field(None, alias="reject_from_link")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: POSTGRESQL.RejectUses | None = Field(POSTGRESQL.RejectUses.rows, alias="reject_uses")
    rejected_filters: str | None = Field(None, alias="rejected_filters")
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    sampling_percentage: str | None = Field(None, alias="sampling_percentage")
    sampling_seed: int | None = Field(None, alias="sampling_seed")
    sampling_type: POSTGRESQL.SamplingType | None = Field(POSTGRESQL.SamplingType.none, alias="sampling_type")
    schema_name: str | None = Field(None, alias="schema_name")
    select_statement: str = Field(None, alias="select_statement")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: POSTGRESQL.KeyColSelect | None = Field(POSTGRESQL.KeyColSelect.default, alias="keyColSelect")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    static_statement: str = Field(None, alias="static_statement")
    stored_procedure_name: str | None = Field(None, alias="procedure_name")
    table_action: POSTGRESQL.TableAction | None = Field(POSTGRESQL.TableAction.append, alias="table_action")
    table_name: str = Field(None, alias="table_name")
    transform: str | None = Field("false", alias="transform")
    unique: bool | None = Field(None, alias="part_unique")
    update_statement: str | None = Field(None, alias="update_statement")
    user_defined_function: bool | None = Field(None, alias="user_defined_function")
    write_mode: POSTGRESQL.WriteMode | None = Field(POSTGRESQL.WriteMode.insert, alias="write_mode")

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
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("call_procedure_statement")
            if (
                ((not self.table_name))
                and (not self.select_statement)
                and (not self.stored_procedure_name)
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
            include.add("select_statement")
            if (
                ((not self.schema_name))
                and (not self.table_name)
                and (not self.stored_procedure_name)
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
            include.add("table_name")
            if (
                ((not self.select_statement))
                and (not self.stored_procedure_name)
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
            include.add("stored_procedure_name")
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
            else exclude.add("stored_procedure_name")
        )
        (
            include.add("read_select_statement_from_file")
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
            else exclude.add("read_select_statement_from_file")
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
        include.add("lookup_type") if (self.has_ref_output) else exclude.add("lookup_type")
        (
            include.add("call_procedure_statement")
            if (

                    (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                    and (
                        ((not self.select_statement)) or (self.select_statement and "#" in str(self.select_statement))
                    )
                    and (
                        ((not self.stored_procedure_name))
                        or (self.stored_procedure_name and "#" in str(self.stored_procedure_name))
                    )
                    and (
                        (
                            (
                                self.read_method
                                and (
                                    (hasattr(self.read_method, "value") and self.read_method.value == "call_statement")
                                    or (self.read_method == "call_statement")
                                )
                            )
                        )
                        or (

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
            else exclude.add("call_procedure_statement")
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
                        or (

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
            else exclude.add("user_defined_function")
        )
        (
            include.add("add_procedure_return_value_to_schema")
            if (

                    (((not self.select_statement)) or ((self.select_statement and "#" in str(self.select_statement))))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
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
                        or (

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
            else exclude.add("add_procedure_return_value_to_schema")
        )
        (
            include.add("stored_procedure_name")
            if (

                    (
                        ((not self.call_procedure_statement))
                        or ((self.call_procedure_statement and "#" in str(self.call_procedure_statement)))
                    )
                    and (
                        ((not self.select_statement)) or (self.select_statement and "#" in str(self.select_statement))
                    )
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
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
            else exclude.add("stored_procedure_name")
        )
        (
            include.add("read_select_statement_from_file")
            if (

                    (((not self.schema_name)) or ((self.schema_name and "#" in str(self.schema_name))))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
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
            else exclude.add("read_select_statement_from_file")
        )
        (
            include.add("forward_row_data")
            if (

                    (((not self.select_statement)) or ((self.select_statement and "#" in str(self.select_statement))))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
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
                        or (

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
            else exclude.add("forward_row_data")
        )
        (
            include.add("row_limit")
            if (



                            (
                                (
                                    (
                                        self.read_method
                                        and (
                                            (hasattr(self.read_method, "value") and self.read_method.value != "call")
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
            else exclude.add("row_limit")
        )
        (
            include.add("select_statement")
            if (

                    (((not self.schema_name)) or ((self.schema_name and "#" in str(self.schema_name))))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
                    and (
                        ((not self.stored_procedure_name))
                        or (self.stored_procedure_name and "#" in str(self.stored_procedure_name))
                    )
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
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
            else exclude.add("select_statement")
        )
        (
            include.add("schema_name")
            if (

                    (((not self.select_statement)) or ((self.select_statement and "#" in str(self.select_statement))))
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
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

                                self.read_method
                                and (
                                    (hasattr(self.read_method, "value") and self.read_method.value == "general")
                                    or (self.read_method == "general")
                                )

                        )
                        or (

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
            else exclude.add("schema_name")
        )
        (
            include.add("table_name")
            if (

                    (((not self.select_statement)) or ((self.select_statement and "#" in str(self.select_statement))))
                    and (
                        ((not self.stored_procedure_name))
                        or (self.stored_procedure_name and "#" in str(self.stored_procedure_name))
                    )
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
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
            else exclude.add("table_name")
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
        include.add("defer_credentials") if (()) else exclude.add("defer_credentials")
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
            include.add("stored_procedure_name")
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
            else exclude.add("stored_procedure_name")
        )
        (
            include.add("read_select_statement_from_file")
            if (not self.schema_name)
            and (not self.table_name)
            and (
                self.read_method
                and (
                    (hasattr(self.read_method, "value") and self.read_method.value == "select")
                    or (self.read_method == "select")
                )
            )
            else exclude.add("read_select_statement_from_file")
        )
        (
            include.add("table_name")
            if (not self.select_statement)
            and (not self.stored_procedure_name)
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
            and (not self.stored_procedure_name)
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
            if (self.has_ref_output == "true" or self.has_ref_output)
            else exclude.add("lookup_type")
        )
        (
            include.add("call_procedure_statement")
            if (not self.table_name)
            and (not self.select_statement)
            and (not self.stored_procedure_name)
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
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("create_statement")
            if (
                ((not self.static_statement))
                and (not self.stored_procedure_name)
                and (not self.call_procedure_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "call")
                                or (self.write_mode != "call")
                            )
                        )
                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "call_statement")
                                or (self.write_mode != "call_statement")
                            )

                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
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
            include.add("schema_name")
            if (
                ((not self.static_statement))
                and (not self.call_procedure_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "call_statement")
                                or (self.write_mode != "call_statement")
                            )
                        )
                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
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
            include.add("table_name")
            if (
                ((not self.static_statement))
                and (not self.call_procedure_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "call")
                                or (self.write_mode != "call")
                            )
                        )
                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "call_statement")
                                or (self.write_mode != "call_statement")
                            )

                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
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
                and (not self.stored_procedure_name)
                and (not self.call_procedure_statement)
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
            include.add("call_procedure_statement")
            if (
                ((not self.static_statement))
                and (not self.schema_name)
                and (not self.table_name)
                and (not self.update_statement)
                and (not self.stored_procedure_name)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "call_statement")
                            or (self.write_mode == "call_statement")
                        )

                )
            )
            else exclude.add("call_procedure_statement")
        )
        (
            include.add("read_update_statement_from_file")
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
            else exclude.add("read_update_statement_from_file")
        )
        (
            include.add("stored_procedure_name")
            if (
                ((not self.static_statement))
                and (not self.table_name)
                and (not self.update_statement)
                and (not self.call_procedure_statement)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "call")
                            or (self.write_mode == "call")
                        )

                )
            )
            else exclude.add("stored_procedure_name")
        )
        (
            include.add("batch_size")
            if (((not self.has_reject_output)) or (not self.has_reject_output))
            else exclude.add("batch_size")
        )
        (
            include.add("execute_procedure_for_each_row")
            if (
                ((not self.static_statement))
                and (not self.table_name)
                and (not self.update_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "call")
                                or (self.write_mode == "call")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "call_statement")
                                or (self.write_mode == "call_statement")
                            )

                    )
                )
            )
            else exclude.add("execute_procedure_for_each_row")
        )
        (
            include.add("call_procedure_statement")
            if (

                    (((not self.static_statement)) or ((self.static_statement and "#" in str(self.static_statement))))
                    and (((not self.schema_name)) or (self.schema_name and "#" in str(self.schema_name)))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
                    and (
                        ((not self.update_statement)) or (self.update_statement and "#" in str(self.update_statement))
                    )
                    and (
                        ((not self.stored_procedure_name))
                        or (self.stored_procedure_name and "#" in str(self.stored_procedure_name))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "call_statement")
                                    or (self.write_mode == "call_statement")
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
            else exclude.add("call_procedure_statement")
        )
        (
            include.add("read_update_statement_from_file")
            if (

                    (((not self.static_statement)) or ((self.static_statement and "#" in str(self.static_statement))))
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
            include.add("stored_procedure_name")
            if (

                    (((not self.static_statement)) or ((self.static_statement and "#" in str(self.static_statement))))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
                    and (
                        ((not self.update_statement)) or (self.update_statement and "#" in str(self.update_statement))
                    )
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "call")
                                    or (self.write_mode == "call")
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
            else exclude.add("stored_procedure_name")
        )
        (
            include.add("create_statement")
            if (

                    (((not self.static_statement)) or ((self.static_statement and "#" in str(self.static_statement))))
                    and (
                        ((not self.stored_procedure_name))
                        or (self.stored_procedure_name and "#" in str(self.stored_procedure_name))
                    )
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
                    )
                    and (

                            (
                                (
                                    (
                                        self.write_mode
                                        and (
                                            (hasattr(self.write_mode, "value") and self.write_mode.value != "call")
                                            or (self.write_mode != "call")
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
                                                and self.write_mode.value != "call_statement"
                                            )
                                            or (self.write_mode != "call_statement")
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
                            and (
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
            else exclude.add("create_statement")
        )
        (
            include.add("update_statement")
            if (

                    (((not self.static_statement)) or ((self.static_statement and "#" in str(self.static_statement))))
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
            include.add("schema_name")
            if (

                    (((not self.static_statement)) or ((self.static_statement and "#" in str(self.static_statement))))
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
                    )
                    and (

                            (
                                (
                                    (
                                        self.write_mode
                                        and (
                                            (
                                                hasattr(self.write_mode, "value")
                                                and self.write_mode.value != "call_statement"
                                            )
                                            or (self.write_mode != "call_statement")
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
                                                and self.write_mode.value != "static_statement"
                                            )
                                            or (self.write_mode != "static_statement")
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
            else exclude.add("schema_name")
        )
        (
            include.add("execute_procedure_for_each_row")
            if (

                    (((not self.static_statement)) or ((self.static_statement and "#" in str(self.static_statement))))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
                    and (
                        ((not self.update_statement)) or (self.update_statement and "#" in str(self.update_statement))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "call")
                                    or (self.write_mode == "call")
                                )
                            )
                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "call_statement")
                                    or (self.write_mode == "call_statement")
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
            else exclude.add("execute_procedure_for_each_row")
        )
        (
            include.add("table_name")
            if (

                    (((not self.static_statement)) or ((self.static_statement and "#" in str(self.static_statement))))
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
                    )
                    and (

                            (
                                (
                                    (
                                        self.write_mode
                                        and (
                                            (hasattr(self.write_mode, "value") and self.write_mode.value != "call")
                                            or (self.write_mode != "call")
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
                                                and self.write_mode.value != "call_statement"
                                            )
                                            or (self.write_mode != "call_statement")
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
                            and (
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
            else exclude.add("table_name")
        )
        (
            include.add("key_column_names")
            if (

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
            else exclude.add("key_column_names")
        )
        (
            include.add("table_action")
            if (

                    (
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
                                ((not self.static_statement))
                                or ((self.static_statement and "#" in str(self.static_statement)))
                            )
                            and (

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
            else exclude.add("table_action")
        )
        (
            include.add("static_statement")
            if (

                    (((not self.schema_name)) or ((self.schema_name and "#" in str(self.schema_name))))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
                    and (
                        ((not self.update_statement)) or (self.update_statement and "#" in str(self.update_statement))
                    )
                    and (
                        ((not self.stored_procedure_name))
                        or (self.stored_procedure_name and "#" in str(self.stored_procedure_name))
                    )
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
                    )
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "static_statement")
                                    or (self.write_mode == "static_statement")
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
            else exclude.add("static_statement")
        )
        (
            include.add("runtime_column_propagation")
            if (not self.enable_schemaless_design)
            else exclude.add("runtime_column_propagation")
        )
        include.add("data_asset_name") if (self.create_data_asset) else exclude.add("data_asset_name")
        include.add("create_data_asset") if (()) else exclude.add("create_data_asset")
        (
            include.add("schema_name")
            if (not self.static_statement)
            and (not self.call_procedure_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call_statement" not in str(self.write_mode.value)
                    )
                    or ("call_statement" not in str(self.write_mode))
                )
                and self.write_mode
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
            include.add("stored_procedure_name")
            if (not self.static_statement)
            and (not self.table_name)
            and (not self.update_statement)
            and (not self.call_procedure_statement)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "call")
                    or (self.write_mode == "call")
                )
            )
            else exclude.add("stored_procedure_name")
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
            include.add("create_statement")
            if (not self.static_statement)
            and (not self.stored_procedure_name)
            and (not self.call_procedure_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call" not in str(self.write_mode.value)
                    )
                    or ("call" not in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call_statement" not in str(self.write_mode.value)
                    )
                    or ("call_statement" not in str(self.write_mode))
                )
                and self.write_mode
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
            include.add("static_statement")
            if (not self.schema_name)
            and (not self.table_name)
            and (not self.update_statement)
            and (not self.stored_procedure_name)
            and (not self.call_procedure_statement)
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
            include.add("table_name")
            if (not self.static_statement)
            and (not self.call_procedure_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call" not in str(self.write_mode.value)
                    )
                    or ("call" not in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call_statement" not in str(self.write_mode.value)
                    )
                    or ("call_statement" not in str(self.write_mode))
                )
                and self.write_mode
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
            include.add("read_update_statement_from_file")
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
            else exclude.add("read_update_statement_from_file")
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
            include.add("call_procedure_statement")
            if (not self.static_statement)
            and (not self.schema_name)
            and (not self.table_name)
            and (not self.update_statement)
            and (not self.stored_procedure_name)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "call_statement")
                    or (self.write_mode == "call_statement")
                )
            )
            else exclude.add("call_procedure_statement")
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
            include.add("execute_procedure_for_each_row")
            if (not self.static_statement)
            and (not self.table_name)
            and (not self.update_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call" in str(self.write_mode.value)
                    )
                    or ("call" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call_statement" in str(self.write_mode.value)
                    )
                    or ("call_statement" in str(self.write_mode))
                )
            )
            else exclude.add("execute_procedure_for_each_row")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "add_procedure_return_value_to_schema",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "byte_limit",
            "call_procedure_statement",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "default_maximum_length_for_columns",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_java_heap_size",
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
            "forward_row_data",
            "generate_unicode_type_columns",
            "has_ref_output",
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
            "proc_param_properties",
            "push_filters",
            "pushed_filters",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_after_sql_node_statements_from_file",
            "read_after_sql_statements_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statements_from_file",
            "read_method",
            "read_select_statement_from_file",
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
            "stored_procedure_name",
            "table_name",
            "transform",
            "unique",
            "user_defined_function",
        }
        required = {
            "current_output_link_type",
            "database",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname_or_ip_address",
            "output_acp_should_hide",
            "password",
            "port",
            "proxy_host",
            "proxy_port",
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
            "batch_size",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "call_procedure_statement",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "create_data_asset",
            "create_statement",
            "current_output_link_type",
            "data_asset_name",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_java_heap_size",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_sql",
            "enable_before_sql_node",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execute_procedure_for_each_row",
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
            "read_after_sql_node_statements_from_file",
            "read_after_sql_statements_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statements_from_file",
            "read_update_statement_from_file",
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
            "stored_procedure_name",
            "table_action",
            "table_name",
            "unique",
            "update_statement",
            "write_mode",
        }
        required = {
            "current_output_link_type",
            "data_asset_name",
            "database",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname_or_ip_address",
            "output_acp_should_hide",
            "password",
            "port",
            "proxy_host",
            "proxy_port",
            "static_statement",
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
        return {"min": 0, "max": -1}

    def get_output_ports_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "reject_condition_row_is_rejected",
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
