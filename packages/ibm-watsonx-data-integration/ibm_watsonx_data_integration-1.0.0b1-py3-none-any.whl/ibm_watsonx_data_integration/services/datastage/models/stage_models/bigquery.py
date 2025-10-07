import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.bigquery_connection import BigqueryConn
from ibm_watsonx_data_integration.services.datastage.models.enums import BIGQUERY
from pydantic import Field
from typing import ClassVar


class bigquery(BaseStage):

    op_name: ClassVar[str] = "bigqueryPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/bigqueryPX.svg"
    label: ClassVar[str] = "Google BigQuery"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: BigqueryConn = BigqueryConn()
    big_query_temp_bucket_name: str | None = Field(None, alias="big_query_temp_bucket_name")
    bucket: str = Field(None, alias="bucket")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: BIGQUERY.BufModeRonly | None = Field(BIGQUERY.BufModeRonly.default, alias="buf_mode_ronly")
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: BIGQUERY.BufferingMode | None = Field(BIGQUERY.BufferingMode.default, alias="buf_mode")
    byte_limit: str | None = Field(None, alias="byte_limit")
    call_procedure_statement: str | None = Field(None, alias="call_statement")
    collecting: BIGQUERY.Collecting | None = Field(BIGQUERY.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: BIGQUERY.CombinabilityMode | None = Field(
        BIGQUERY.CombinabilityMode.auto, alias="combinability"
    )
    create_data_asset: bool | None = Field(False, alias="registerDataAsset")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_asset_name: str = Field(None, alias="dataAssetName")
    database_name: str | None = Field(None, alias="database_name")
    dataset_name: str = Field(None, alias="schema_name")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    enable_after_sql: str | None = Field("", alias="before_after.after")
    enable_after_sql_node: str | None = Field("", alias="before_after.after_node")
    enable_before_sql: str | None = Field("", alias="before_after.before")
    enable_before_sql_node: str | None = Field("", alias="before_after.before_node")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_partitioned_reads: bool | None = Field(False, alias="partitioned")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execute_procedure_for_each_row: bool | None = Field(True, alias="call_each_row")
    execution_mode: BIGQUERY.ExecutionMode | None = Field(BIGQUERY.ExecutionMode.default_par, alias="execmode")
    fail_on_error_after_sql: bool | None = Field(True, alias="before_after.after.fail_on_error")
    fail_on_error_after_sql_node: bool | None = Field(True, alias="before_after.after_node.fail_on_error")
    fail_on_error_before_sql: bool | None = Field(True, alias="before_after.before.fail_on_error")
    fail_on_error_before_sql_node: bool | None = Field(True, alias="before_after.before_node.fail_on_error")
    file_format: BIGQUERY.FileFormat | None = Field(None, alias="file_format")
    file_name_prefix: str | None = Field(None, alias="file_name")
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
    lookup_type: BIGQUERY.LookupType | None = Field(BIGQUERY.LookupType.empty, alias="lookup_type")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    node_count: int | None = Field(1, alias="node_count")
    node_number: int | None = Field(0, alias="node_number")
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
    partition_type: BIGQUERY.PartitionType | None = Field(BIGQUERY.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: BIGQUERY.PreservePartitioning | None = Field(
        BIGQUERY.PreservePartitioning.default_propagate, alias="preserve"
    )
    proc_param_properties: list | None = Field([], alias="procParamProperties")
    push_filters: str | None = Field(None, alias="push_filters")
    pushed_filters: str | None = Field(None, alias="pushed_filters")
    query_timeout: int | None = Field(None, alias="query_timeout")
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
    read_method: BIGQUERY.ReadMethod | None = Field(BIGQUERY.ReadMethod.general, alias="read_mode")
    read_part_size: int | None = Field(None, alias="read_part_size")
    read_select_statement_from_file: bool | None = Field(False, alias="select_statement.read_from_file_select")
    read_update_statement_from_file: bool | None = Field(False, alias="update_statement.read_from_file_update")
    rejected_filters: str | None = Field(None, alias="rejected_filters")
    row_limit: int | None = Field(None, alias="row_limit")
    row_start: int | None = Field(None, alias="row_start")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    select_statement: str = Field(None, alias="select_statement")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: BIGQUERY.KeyColSelect | None = Field(BIGQUERY.KeyColSelect.default, alias="keyColSelect")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    static_statement: str = Field(None, alias="static_statement")
    table_action: BIGQUERY.TableAction | None = Field(BIGQUERY.TableAction.append, alias="table_action")
    table_name: str = Field(None, alias="table_name")
    transform: str | None = Field("false", alias="transform")
    unique: bool | None = Field(None, alias="part_unique")
    update_statement: str = Field(None, alias="update_statement")
    use_gcs_staging: bool | None = Field(False, alias="use_gcs_staging")
    write_mode: BIGQUERY.WriteMode | None = Field(BIGQUERY.WriteMode.insert, alias="write_mode")
    write_part_size: int | None = Field(None, alias="write_part_size")

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
            include.add("call_procedure_statement")
            if (
                ((not self.dataset_name))
                and (not self.table_name)
                and (not self.select_statement)
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
            include.add("database_name")
            if (
                (
                    ((not self.select_statement))
                    and (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "general")
                                or (self.read_method == "general")
                            )
                        )
                    )
                )
                or (self.use_gcs_staging)
            )
            else exclude.add("database_name")
        )
        include.add("file_name_prefix") if (self.use_gcs_staging) else exclude.add("file_name_prefix")
        (
            include.add("select_statement")
            if (
                ((not self.table_name))
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
            include.add("dataset_name")
            if (
                (
                    ((not self.select_statement))
                    and ((not self.call_procedure_statement))
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
                    )
                )
                or (self.use_gcs_staging)
            )
            else exclude.add("dataset_name")
        )
        (
            include.add("table_name")
            if (
                ((not self.select_statement))
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
        include.add("bucket") if (self.use_gcs_staging) else exclude.add("bucket")
        include.add("row_start") if (self.row_limit) else exclude.add("row_start")
        (
            include.add("byte_limit")
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
            else exclude.add("byte_limit")
        )
        (
            include.add("row_limit")
            if (
                (
                    (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "general")
                                or (self.read_method == "general")
                            )
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

                            self.lookup_type
                            and (
                                (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                or (self.lookup_type == "empty")
                            )

                    )
                )
            )
            else exclude.add("row_limit")
        )
        (
            include.add("use_gcs_staging")
            if (
                (
                    ((self.select_statement))
                    or (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "select")
                                or (self.read_method == "select")
                            )
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

                            self.lookup_type
                            and (
                                (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                or (self.lookup_type == "empty")
                            )

                    )
                )
            )
            else exclude.add("use_gcs_staging")
        )
        include.add("read_part_size") if (self.use_gcs_staging) else exclude.add("read_part_size")
        (
            include.add("enable_partitioned_reads")
            if (
                (
                    ((self.select_statement))
                    or (
                        (
                            self.read_method
                            and (
                                (hasattr(self.read_method, "value") and self.read_method.value == "select")
                                or (self.read_method == "select")
                            )
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

                            self.lookup_type
                            and (
                                (hasattr(self.lookup_type, "value") and self.lookup_type.value == "empty")
                                or (self.lookup_type == "empty")
                            )

                    )
                )
            )
            else exclude.add("enable_partitioned_reads")
        )
        (
            include.add("read_select_statement_from_file")
            if (
                ((not self.table_name))
                and (not self.call_procedure_statement)
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
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("call_procedure_statement")
            if (

                    (((not self.dataset_name)) or ((self.dataset_name and "#" in str(self.dataset_name))))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
                    and (
                        ((not self.select_statement)) or (self.select_statement and "#" in str(self.select_statement))
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
            include.add("database_name")
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
                or (self.use_gcs_staging)
                or (self.use_gcs_staging and "#" in str(self.use_gcs_staging))
            )
            else exclude.add("database_name")
        )
        (
            include.add("enable_partitioned_reads")
            if (

                    (
                        ((self.select_statement))
                        or (
                            (
                                self.read_method
                                and (
                                    (hasattr(self.read_method, "value") and self.read_method.value == "select")
                                    or (self.read_method == "select")
                                )
                            )
                        )
                        or ((self.select_statement and "#" in str(self.select_statement)))
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
            else exclude.add("enable_partitioned_reads")
        )
        (
            include.add("select_statement")
            if (

                    (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
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
            include.add("dataset_name")
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
                or (self.use_gcs_staging)
                or (self.use_gcs_staging and "#" in str(self.use_gcs_staging))
            )
            else exclude.add("dataset_name")
        )
        (
            include.add("table_name")
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
            include.add("read_select_statement_from_file")
            if (

                    (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
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
            else exclude.add("read_select_statement_from_file")
        )
        (
            include.add("row_start")
            if (((self.row_limit)) or (self.row_limit and "#" in str(self.row_limit)))
            else exclude.add("row_start")
        )
        (
            include.add("byte_limit")
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
            else exclude.add("byte_limit")
        )
        (
            include.add("row_limit")
            if (

                    (
                        (
                            (
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
            else exclude.add("row_limit")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("use_gcs_staging")
            if (

                    (
                        ((self.select_statement))
                        or (
                            (
                                self.read_method
                                and (
                                    (hasattr(self.read_method, "value") and self.read_method.value == "select")
                                    or (self.read_method == "select")
                                )
                            )
                        )
                        or ((self.select_statement and "#" in str(self.select_statement)))
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
            else exclude.add("use_gcs_staging")
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
            include.add("read_select_statement_from_file")
            if (not self.table_name)
            and (not self.call_procedure_statement)
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
            include.add("use_gcs_staging")
            if (
                (self.select_statement)
                or (
                    self.read_method
                    and (
                        (hasattr(self.read_method, "value") and self.read_method.value == "select")
                        or (self.read_method == "select")
                    )
                )
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
            else exclude.add("use_gcs_staging")
        )
        (
            include.add("row_limit")
            if (

                    self.read_method
                    and (
                        (hasattr(self.read_method, "value") and self.read_method.value == "general")
                        or (self.read_method == "general")
                    )

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
            else exclude.add("row_limit")
        )
        (
            include.add("lookup_type")
            if (self.has_reference_output == "true" or self.has_reference_output)
            else exclude.add("lookup_type")
        )
        include.add("row_start") if (self.row_limit) else exclude.add("row_start")
        (
            include.add("byte_limit")
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
            else exclude.add("byte_limit")
        )
        (
            include.add("dataset_name")
            if (
                (not self.select_statement)
                and (not self.call_procedure_statement)
                and (
                    self.read_method
                    and (
                        (
                            hasattr(self.read_method, "value")
                            and self.read_method.value
                            and "general" in str(self.read_method.value)
                        )
                        or ("general" in str(self.read_method))
                    )
                )
            )
            or (self.use_gcs_staging)
            else exclude.add("dataset_name")
        )
        include.add("file_name_prefix") if self.use_gcs_staging else exclude.add("file_name_prefix")
        include.add("read_part_size") if self.use_gcs_staging else exclude.add("read_part_size")
        (
            include.add("table_name")
            if (not self.select_statement)
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
            if (not self.table_name)
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
        include.add("bucket") if self.use_gcs_staging else exclude.add("bucket")
        (
            include.add("enable_partitioned_reads")
            if (
                (self.select_statement)
                or (
                    self.read_method
                    and (
                        (hasattr(self.read_method, "value") and self.read_method.value == "select")
                        or (self.read_method == "select")
                    )
                )
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
            else exclude.add("enable_partitioned_reads")
        )
        (
            include.add("call_procedure_statement")
            if (not self.dataset_name)
            and (not self.table_name)
            and (not self.select_statement)
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
            include.add("database_name")
            if (
                (not self.select_statement)
                and (
                    self.read_method
                    and (
                        (hasattr(self.read_method, "value") and self.read_method.value == "general")
                        or (self.read_method == "general")
                    )
                )
            )
            or (self.use_gcs_staging)
            else exclude.add("database_name")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("bucket")
            if (
                (
                    ((self.update_statement and "TEMP_EXTERNAL_TABLE" in str(self.update_statement)))
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                                or (self.write_mode != "insert")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and ((hasattr(self.file_format, "value") and self.file_format.value) or (self.file_format))
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
            )
            else exclude.add("bucket")
        )
        (
            include.add("database_name")
            if (
                ((not self.update_statement))
                and (not self.static_statement)
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
            else exclude.add("database_name")
        )
        (
            include.add("file_name_prefix")
            if (
                (
                    ((self.update_statement and "TEMP_EXTERNAL_TABLE" in str(self.update_statement)))
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                                or (self.write_mode != "insert")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and ((hasattr(self.file_format, "value") and self.file_format.value) or (self.file_format))
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
            )
            else exclude.add("file_name_prefix")
        )
        (
            include.add("update_statement")
            if (
                ((not self.database_name))
                and (not self.dataset_name)
                and (not self.table_name)
                and (not self.call_procedure_statement)
                and (not self.static_statement)
                and (


                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_statement")
                                or (self.write_mode == "update_statement")
                            )


                )
            )
            else exclude.add("update_statement")
        )
        (
            include.add("dataset_name")
            if (
                ((not self.call_procedure_statement))
                and (not self.update_statement)
                and (not self.static_statement)
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
            else exclude.add("dataset_name")
        )
        (
            include.add("table_name")
            if (
                ((not self.call_procedure_statement))
                and (not self.update_statement)
                and (not self.static_statement)
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
            else exclude.add("table_name")
        )
        (
            include.add("key_column_names")
            if (
                (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                                or (self.write_mode != "insert")
                            )
                        )
                    )
                    and (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "insert_only")
                                or (self.write_mode != "insert_only")
                            )
                        )
                    )
                )
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
            else exclude.add("key_column_names")
        )
        (
            include.add("table_action")
            if (
                (
                    ((self.bucket))
                    or ((self.file_name_prefix))
                    or (
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
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value != "update_statement")
                                    or (self.write_mode != "update_statement")
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
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "delete")
                                or (self.write_mode != "delete")
                            )
                        )
                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "update")
                                or (self.write_mode != "update")
                            )

                    )
                )
            )
            else exclude.add("table_action")
        )
        (
            include.add("static_statement")
            if (
                ((not self.dataset_name))
                and (not self.table_name)
                and (not self.database_name)
                and (not self.call_procedure_statement)
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
            include.add("call_procedure_statement")
            if (
                ((not self.static_statement))
                and (not self.dataset_name)
                and (not self.table_name)
                and (not self.update_statement)
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
                ((not self.database_name))
                and (not self.dataset_name)
                and (not self.table_name)
                and (not self.call_procedure_statement)
                and (not self.static_statement)
                and (


                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_statement")
                                or (self.write_mode == "update_statement")
                            )


                )
            )
            else exclude.add("read_update_statement_from_file")
        )
        (
            include.add("write_part_size")
            if (
                ((self.update_statement and "TEMP_EXTERNAL_TABLE" in str(self.update_statement)))
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                            or (self.write_mode != "insert")
                        )

                )
                or (

                        self.file_format
                        and ((hasattr(self.file_format, "value") and self.file_format.value) or (self.file_format))

                )
            )
            else exclude.add("write_part_size")
        )
        (
            include.add("execute_procedure_for_each_row")
            if (
                ((not self.static_statement))
                and (not self.table_name)
                and (not self.update_statement)
                and (


                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "call_statement")
                                or (self.write_mode == "call_statement")
                            )


                )
            )
            else exclude.add("execute_procedure_for_each_row")
        )
        (
            include.add("bucket")
            if (

                    (
                        ((self.update_statement and "TEMP_EXTERNAL_TABLE" in str(self.update_statement)))
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                                    or (self.write_mode != "insert")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value)
                                    or (self.file_format)
                                )
                            )
                        )
                        or ((self.update_statement and "#" in str(self.update_statement)))
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

            )
            else exclude.add("bucket")
        )
        (
            include.add("call_procedure_statement")
            if (

                    (((not self.static_statement)) or ((self.static_statement and "#" in str(self.static_statement))))
                    and (((not self.dataset_name)) or (self.dataset_name and "#" in str(self.dataset_name)))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
                    and (
                        ((not self.update_statement)) or (self.update_statement and "#" in str(self.update_statement))
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

                    (((not self.database_name)) or ((self.database_name and "#" in str(self.database_name))))
                    and (((not self.dataset_name)) or (self.dataset_name and "#" in str(self.dataset_name)))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
                    )
                    and (
                        ((not self.static_statement)) or (self.static_statement and "#" in str(self.static_statement))
                    )
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
            include.add("database_name")
            if (

                    (((not self.update_statement)) or ((self.update_statement and "#" in str(self.update_statement))))
                    and (
                        ((not self.static_statement)) or (self.static_statement and "#" in str(self.static_statement))
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
            else exclude.add("database_name")
        )
        (
            include.add("file_name_prefix")
            if (

                    (
                        ((self.update_statement and "TEMP_EXTERNAL_TABLE" in str(self.update_statement)))
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                                    or (self.write_mode != "insert")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value)
                                    or (self.file_format)
                                )
                            )
                        )
                        or ((self.update_statement and "#" in str(self.update_statement)))
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

            )
            else exclude.add("file_name_prefix")
        )
        (
            include.add("write_part_size")
            if (
                ((self.update_statement and "TEMP_EXTERNAL_TABLE" in str(self.update_statement)))
                or (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                            or (self.write_mode != "insert")
                        )

                )
                or (

                        self.file_format
                        and ((hasattr(self.file_format, "value") and self.file_format.value) or (self.file_format))

                )
                or (self.update_statement and "#" in str(self.update_statement))
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
            else exclude.add("write_part_size")
        )
        (
            include.add("update_statement")
            if (

                    (((not self.database_name)) or ((self.database_name and "#" in str(self.database_name))))
                    and (((not self.dataset_name)) or (self.dataset_name and "#" in str(self.dataset_name)))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
                    )
                    and (
                        ((not self.static_statement)) or (self.static_statement and "#" in str(self.static_statement))
                    )
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
            include.add("dataset_name")
            if (

                    (
                        ((not self.call_procedure_statement))
                        or ((self.call_procedure_statement and "#" in str(self.call_procedure_statement)))
                    )
                    and (
                        ((not self.update_statement)) or (self.update_statement and "#" in str(self.update_statement))
                    )
                    and (
                        ((not self.static_statement)) or (self.static_statement and "#" in str(self.static_statement))
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
            else exclude.add("dataset_name")
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
            else exclude.add("execute_procedure_for_each_row")
        )
        (
            include.add("table_name")
            if (

                    (
                        ((not self.call_procedure_statement))
                        or ((self.call_procedure_statement and "#" in str(self.call_procedure_statement)))
                    )
                    and (
                        ((not self.update_statement)) or (self.update_statement and "#" in str(self.update_statement))
                    )
                    and (
                        ((not self.static_statement)) or (self.static_statement and "#" in str(self.static_statement))
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
            else exclude.add("table_name")
        )
        (
            include.add("key_column_names")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.write_mode
                                        and (
                                            (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                                            or (self.write_mode != "insert")
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
                                                and self.write_mode.value != "insert_only"
                                            )
                                            or (self.write_mode != "insert_only")
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
            else exclude.add("key_column_names")
        )
        (
            include.add("table_action")
            if (

                    (
                        ((self.bucket))
                        or ((self.file_name_prefix))
                        or (
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
                        or ((self.bucket and "#" in str(self.bucket)))
                        or ((self.file_name_prefix and "#" in str(self.file_name_prefix)))
                    )
                    and (

                            (
                                (
                                    (
                                        self.write_mode
                                        and (
                                            (hasattr(self.write_mode, "value") and self.write_mode.value != "delete")
                                            or (self.write_mode != "delete")
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
                                            (hasattr(self.write_mode, "value") and self.write_mode.value != "update")
                                            or (self.write_mode != "update")
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
            else exclude.add("table_action")
        )
        (
            include.add("static_statement")
            if (

                    (((not self.dataset_name)) or ((self.dataset_name and "#" in str(self.dataset_name))))
                    and (((not self.table_name)) or (self.table_name and "#" in str(self.table_name)))
                    and (((not self.database_name)) or (self.database_name and "#" in str(self.database_name)))
                    and (
                        ((not self.call_procedure_statement))
                        or (self.call_procedure_statement and "#" in str(self.call_procedure_statement))
                    )
                    and (
                        ((not self.update_statement)) or (self.update_statement and "#" in str(self.update_statement))
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
            include.add("key_column_names")
            if (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert" not in str(self.write_mode.value)
                    )
                    or ("insert" not in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "insert_only" not in str(self.write_mode.value)
                    )
                    or ("insert_only" not in str(self.write_mode))
                )
            )
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
            else exclude.add("key_column_names")
        )
        (
            include.add("static_statement")
            if (not self.dataset_name)
            and (not self.table_name)
            and (not self.database_name)
            and (not self.call_procedure_statement)
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
            include.add("write_part_size")
            if (self.update_statement and "TEMP_EXTERNAL_TABLE" in str(self.update_statement))
            or (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                    or (self.write_mode != "insert")
                )
            )
            or (
                self.file_format
                and ((hasattr(self.file_format, "value") and self.file_format.value) or (self.file_format))
            )
            else exclude.add("write_part_size")
        )
        (
            include.add("dataset_name")
            if (not self.call_procedure_statement)
            and (not self.update_statement)
            and (not self.static_statement)
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
            else exclude.add("dataset_name")
        )
        (
            include.add("file_name_prefix")
            if (
                (self.update_statement and "TEMP_EXTERNAL_TABLE" in str(self.update_statement))
                or (
                    self.write_mode
                    and (
                        (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                        or (self.write_mode != "insert")
                    )
                )
                or (
                    self.file_format
                    and ((hasattr(self.file_format, "value") and self.file_format.value) or (self.file_format))
                )
            )
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
            else exclude.add("file_name_prefix")
        )
        (
            include.add("table_action")
            if (not self.bucket) and (not self.file_name_prefix)
            else exclude.add("table_action")
        )
        (
            include.add("table_name")
            if (not self.call_procedure_statement)
            and (not self.update_statement)
            and (not self.static_statement)
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
            else exclude.add("table_name")
        )
        (
            include.add("bucket")
            if (
                (self.update_statement and "TEMP_EXTERNAL_TABLE" in str(self.update_statement))
                or (
                    self.write_mode
                    and (
                        (hasattr(self.write_mode, "value") and self.write_mode.value != "insert")
                        or (self.write_mode != "insert")
                    )
                )
                or (
                    self.file_format
                    and ((hasattr(self.file_format, "value") and self.file_format.value) or (self.file_format))
                )
            )
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
            else exclude.add("bucket")
        )
        (
            include.add("read_update_statement_from_file")
            if (not self.database_name)
            and (not self.dataset_name)
            and (not self.table_name)
            and (not self.call_procedure_statement)
            and (not self.static_statement)
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
            )
            else exclude.add("read_update_statement_from_file")
        )
        (
            include.add("update_statement")
            if (not self.database_name)
            and (not self.dataset_name)
            and (not self.table_name)
            and (not self.call_procedure_statement)
            and (not self.static_statement)
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
            )
            else exclude.add("update_statement")
        )
        (
            include.add("call_procedure_statement")
            if (not self.static_statement)
            and (not self.dataset_name)
            and (not self.table_name)
            and (not self.update_statement)
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
                (self.bucket)
                or (self.file_name_prefix)
                or (
                    self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "static_statement" not in str(self.write_mode.value)
                        )
                        or ("static_statement" not in str(self.write_mode))
                    )
                    or self.write_mode
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
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "delete" not in str(self.write_mode.value)
                    )
                    or ("delete" not in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update" not in str(self.write_mode.value)
                    )
                    or ("update" not in str(self.write_mode))
                )
            )
            else exclude.add("table_action")
        )
        (
            include.add("database_name")
            if (not self.update_statement)
            and (not self.static_statement)
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
            else exclude.add("database_name")
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
            "bucket",
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
            "database_name",
            "dataset_name",
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
            "enable_partitioned_reads",
            "enable_schemaless_design",
            "execution_mode",
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "file_name_prefix",
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
            "lookup_type",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "node_count",
            "node_number",
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
            "query_timeout",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_after_sql_node_statements_from_file",
            "read_after_sql_statements_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statements_from_file",
            "read_method",
            "read_part_size",
            "read_select_statement_from_file",
            "rejected_filters",
            "row_limit",
            "row_start",
            "runtime_column_propagation",
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
            "use_gcs_staging",
        }
        required = {
            "access_token",
            "authentication_method",
            "bucket",
            "client_id",
            "client_secret",
            "credentials",
            "credentials_file_path",
            "current_output_link_type",
            "dataset_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "output_acp_should_hide",
            "proxy_host",
            "proxy_port",
            "refresh_token",
            "security_token_service_audience",
            "select_statement",
            "service_account_email",
            "table_name",
            "token_field_name",
            "token_url",
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
            "big_query_temp_bucket_name",
            "bucket",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "call_procedure_statement",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "create_data_asset",
            "current_output_link_type",
            "data_asset_name",
            "database_name",
            "dataset_name",
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
            "fail_on_error_after_sql",
            "fail_on_error_after_sql_node",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "file_format",
            "file_name_prefix",
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
            "key_column_names",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "node_count",
            "node_number",
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
            "write_part_size",
        }
        required = {
            "access_token",
            "authentication_method",
            "client_id",
            "client_secret",
            "credentials",
            "credentials_file_path",
            "current_output_link_type",
            "data_asset_name",
            "dataset_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "output_acp_should_hide",
            "proxy_host",
            "proxy_port",
            "refresh_token",
            "security_token_service_audience",
            "service_account_email",
            "static_statement",
            "table_name",
            "token_field_name",
            "token_url",
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
