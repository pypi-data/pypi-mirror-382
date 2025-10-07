import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.salesforceapi_connection import (
    SalesforceapiConn,
)
from ibm_watsonx_data_integration.services.datastage.models.enums import SALESFORCEAPI
from pydantic import Field
from typing import ClassVar


class salesforceapi(BaseStage):

    op_name: ClassVar[str] = "SALESFORCEJCConnectorPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/SALESFORCEJCConnectorPX.svg"
    label: ClassVar[str] = "Salesforce API for DataStage"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: SalesforceapiConn = SalesforceapiConn()
    access_method: SALESFORCEAPI.AccessMethod | None = Field(
        SALESFORCEAPI.AccessMethod.real_time_mode, alias="access_method"
    )
    batch_size: int | None = Field(200, alias="batch_size")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: SALESFORCEAPI.BufModeRonly | None = Field(
        SALESFORCEAPI.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: SALESFORCEAPI.BufferingMode | None = Field(SALESFORCEAPI.BufferingMode.default, alias="buf_mode")
    business_object: str = Field(None, alias="salesforce_object_name")
    collecting: SALESFORCEAPI.Collecting | None = Field(SALESFORCEAPI.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: SALESFORCEAPI.CombinabilityMode | None = Field(
        SALESFORCEAPI.CombinabilityMode.auto, alias="combinability"
    )
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    delta_end_time: str = Field("CurrentTime", alias="end_time")
    delta_extract_id: str = Field("", alias="delta_extract_id")
    delta_start_time: str = Field("LastExtractTime", alias="start_time")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    empty_recycle_bin: bool | None = Field(False, alias="hard_delete_property")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_load_or_extract_large_object_via_flat_file: bool | None = Field(False, alias="enable_flat_file")
    enable_pk_chunking: bool | None = Field(True, alias="pk_chunking")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execution_mode: SALESFORCEAPI.ExecutionMode | None = Field(
        SALESFORCEAPI.ExecutionMode.default_par, alias="execmode"
    )
    flat_file_column_name: str = Field(None, alias="flat_file_column_name")
    flat_file_content_name: str = Field(None, alias="flat_file_content_name")
    flat_file_folder_location: str = Field(None, alias="flat_file_folder_location")
    flat_file_overwrite: bool | None = Field(True, alias="flat_file_overwrite")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    has_reference_output: bool | None = Field(False, alias="has_ref_output")
    hidden_job_id: str | None = Field("0", alias="hidden_job_id")
    hidden_total_record_count: str | None = Field("0", alias="hidden_total_record_count")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    is_reject_output: bool | None = Field(False, alias="is_reject_output")
    job_id: str = Field(None, alias="job_id")
    job_id_file_name: str = Field(None, alias="file_path_job_id")
    job_id_in_file: bool | None = Field(False, alias="sf_job_id_in_file")
    keep_temporary_files: bool | None = Field(False, alias="keep_temp_file")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    lookup_type: SALESFORCEAPI.LookupType | None = Field(SALESFORCEAPI.LookupType.empty, alias="lookup_type")
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
    partition_type: SALESFORCEAPI.PartitionType | None = Field(SALESFORCEAPI.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: SALESFORCEAPI.PreservePartitioning | None = Field(
        SALESFORCEAPI.PreservePartitioning.default_propagate, alias="preserve"
    )
    program_generated_reference_soql_query: str | None = Field("", alias="reference_soql")
    public_datasource_field_map: str | None = Field(None, alias="public_data_source_field_map")
    public_datasource_locator: str | None = Field(None, alias="public_data_source_locator")
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    read_operation: SALESFORCEAPI.ReadOperation | None = Field(SALESFORCEAPI.ReadOperation.query, alias="read_mode")
    reject_condition_write_error_row_rejected: bool | None = Field(
        False, alias="reject_condition_write_error_row_rejected"
    )
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: SALESFORCEAPI.RejectUses | None = Field(SALESFORCEAPI.RejectUses.rows, alias="reject_uses")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    salesforce_concurrency_mode: SALESFORCEAPI.SalesforceConcurrencyMode | None = Field(
        SALESFORCEAPI.SalesforceConcurrencyMode.parallel, alias="backend_load_method"
    )
    serialize_modified_properties: bool | None = Field(True, alias="serialize_modified_properties")
    sf_v2_job_id_in_file: bool | None = Field(False, alias="sf_v2_job_id_in_file")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sleep: int | None = Field(60, alias="sleep")
    soql_query_to_salesforce: str = Field("", alias="soql_string")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: SALESFORCEAPI.KeyColSelect | None = Field(SALESFORCEAPI.KeyColSelect.default, alias="keyColSelect")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    table_name: str | None = Field(None, alias="table_name")
    tenacity: int | None = Field(1800, alias="tenacity")
    unique: bool | None = Field(None, alias="part_unique")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    v2_file_path_job_id: str = Field(None, alias="v2_file_path_job_id")
    v2_hard_delete_property: bool | None = Field(False, alias="v2_hard_delete_property")
    v2_hidden_job_id: str | None = Field("0", alias="v2_hidden_job_id")
    v2_hidden_total_record_count: str | None = Field("0", alias="v2_hidden_total_record_count")
    v2_keep_temp_file: bool | None = Field(False, alias="v2_keep_temp_file")
    write_operation: SALESFORCEAPI.WriteOperation | None = Field(
        SALESFORCEAPI.WriteOperation.upsert, alias="write_mode"
    )

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("preserve_partitioning")
            if (self.output_count and self.output_count > 0)
            else exclude.add("preserve_partitioning")
        )
        (
            include.add("reject_condition_write_error_row_rejected")
            if (self.is_reject_output)
            else exclude.add("reject_condition_write_error_row_rejected")
        )
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
        include.add("reject_uses") if (self.is_reject_output) else exclude.add("reject_uses")
        include.add("reject_number") if (self.is_reject_output) else exclude.add("reject_number")
        include.add("reject_threshold") if (self.is_reject_output) else exclude.add("reject_threshold")
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
            include.add("v2_file_path_job_id")
            if (
                (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                            or (self.access_method == "bulk_mode_v2")
                        )

                )
                and (self.sf_v2_job_id_in_file)
            )
            else exclude.add("v2_file_path_job_id")
        )
        (
            include.add("access_method")
            if (
                (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
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
            else exclude.add("access_method")
        )
        (
            include.add("sf_v2_job_id_in_file")
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
                )
                and (
                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )
                            )
                        )
                    )
                    and (

                            self.access_method
                            and (
                                (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                                or (self.access_method == "bulk_mode_v2")
                            )

                    )
                )
            )
            else exclude.add("sf_v2_job_id_in_file")
        )
        (
            include.add("enable_load_or_extract_large_object_via_flat_file")
            if (
                (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
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
            else exclude.add("enable_load_or_extract_large_object_via_flat_file")
        )
        (
            include.add("v2_hidden_total_record_count")
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
                )
                and (
                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )
                            )
                        )
                    )
                    and (

                            self.access_method
                            and (
                                (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                                or (self.access_method == "bulk_mode_v2")
                            )

                    )
                )
            )
            else exclude.add("v2_hidden_total_record_count")
        )
        (
            include.add("v2_hidden_job_id")
            if (
                (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                            or (self.access_method == "bulk_mode_v2")
                        )

                )
            )
            else exclude.add("v2_hidden_job_id")
        )
        (
            include.add("sleep")
            if (
                (
                    (
                        self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value == "get_the_bulk_load_status"
                            )
                            or (self.read_operation == "get_the_bulk_load_status")
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
            else exclude.add("sleep")
        )
        (
            include.add("flat_file_content_name")
            if (
                (((self.enable_load_or_extract_large_object_via_flat_file)))
                and (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
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
            else exclude.add("flat_file_content_name")
        )
        (
            include.add("soql_query_to_salesforce")
            if (
                ((not self.table_name))
                and (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
                            )

                    )
                )
            )
            else exclude.add("soql_query_to_salesforce")
        )
        (
            include.add("tenacity")
            if (
                (
                    (
                        self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value == "get_the_bulk_load_status"
                            )
                            or (self.read_operation == "get_the_bulk_load_status")
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
            else exclude.add("tenacity")
        )
        (
            include.add("business_object")
            if (

                    (
                        (
                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_deleted_delta"
                                )
                                or (self.read_operation == "get_deleted_delta")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_updated_delta"
                                )
                                or (self.read_operation == "get_updated_delta")
                            )

                    )

            )
            else exclude.add("business_object")
        )
        (
            include.add("batch_size")
            if (

                    (
                        (
                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_deleted_delta"
                                )
                                or (self.read_operation == "get_deleted_delta")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_updated_delta"
                                )
                                or (self.read_operation == "get_updated_delta")
                            )

                    )
                    or (

                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )

                    )
                    or (

                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
                            )

                    )

            )
            else exclude.add("batch_size")
        )
        (
            include.add("flat_file_column_name")
            if (
                (((self.enable_load_or_extract_large_object_via_flat_file)))
                and (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
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
            else exclude.add("flat_file_column_name")
        )
        (
            include.add("hidden_job_id")
            if (
                (
                    (
                        (
                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_the_bulk_load_status"
                                )
                                or (self.read_operation == "get_the_bulk_load_status")
                            )
                        )
                    )
                )
                or (
                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )
                            )
                        )
                    )
                    and (

                            self.access_method
                            and (
                                (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                or (self.access_method == "bulk_mode")
                            )

                    )
                )
            )
            else exclude.add("hidden_job_id")
        )
        (
            include.add("delta_end_time")
            if (

                    (
                        (
                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_deleted_delta"
                                )
                                or (self.read_operation == "get_deleted_delta")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_updated_delta"
                                )
                                or (self.read_operation == "get_updated_delta")
                            )

                    )

            )
            else exclude.add("delta_end_time")
        )
        (
            include.add("program_generated_reference_soql_query")
            if (

                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
                            )

                    )

            )
            else exclude.add("program_generated_reference_soql_query")
        )
        (
            include.add("flat_file_folder_location")
            if (
                (((self.enable_load_or_extract_large_object_via_flat_file)))
                and (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
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
            else exclude.add("flat_file_folder_location")
        )
        (
            include.add("enable_pk_chunking")
            if (
                (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                            or (self.access_method == "bulk_mode")
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
            else exclude.add("enable_pk_chunking")
        )
        (
            include.add("delta_start_time")
            if (

                    (
                        (
                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_deleted_delta"
                                )
                                or (self.read_operation == "get_deleted_delta")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_updated_delta"
                                )
                                or (self.read_operation == "get_updated_delta")
                            )

                    )

            )
            else exclude.add("delta_start_time")
        )
        (
            include.add("job_id_file_name")
            if (
                (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                            or (self.access_method == "bulk_mode")
                        )

                )
                and (self.job_id_in_file)
            )
            else exclude.add("job_id_file_name")
        )
        (
            include.add("delta_extract_id")
            if (

                    (
                        (
                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_deleted_delta"
                                )
                                or (self.read_operation == "get_deleted_delta")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_updated_delta"
                                )
                                or (self.read_operation == "get_updated_delta")
                            )

                    )

            )
            else exclude.add("delta_extract_id")
        )
        (
            include.add("job_id_in_file")
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
                )
                and (
                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value == "get_the_bulk_load_status"
                                    )
                                    or (self.read_operation == "get_the_bulk_load_status")
                                )
                            )
                        )
                    )
                    or (
                        (
                            (
                                (
                                    self.read_operation
                                    and (
                                        (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                        or (self.read_operation == "query")
                                    )
                                )
                            )
                            or (
                                (
                                    self.read_operation
                                    and (
                                        (
                                            hasattr(self.read_operation, "value")
                                            and self.read_operation.value == "query_all"
                                        )
                                        or (self.read_operation == "query_all")
                                    )
                                )
                            )
                        )
                        and (

                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                    or (self.access_method == "bulk_mode")
                                )

                        )
                    )
                )
            )
            else exclude.add("job_id_in_file")
        )
        (
            include.add("job_id")
            if (
                (
                    (
                        (
                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_the_bulk_load_status"
                                )
                                or (self.read_operation == "get_the_bulk_load_status")
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
            else exclude.add("job_id")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("hidden_total_record_count")
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
                )
                and (
                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value == "get_the_bulk_load_status"
                                    )
                                    or (self.read_operation == "get_the_bulk_load_status")
                                )
                            )
                        )
                    )
                    or (
                        (
                            (
                                (
                                    self.read_operation
                                    and (
                                        (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                        or (self.read_operation == "query")
                                    )
                                )
                            )
                            or (
                                (
                                    self.read_operation
                                    and (
                                        (
                                            hasattr(self.read_operation, "value")
                                            and self.read_operation.value == "query_all"
                                        )
                                        or (self.read_operation == "query_all")
                                    )
                                )
                            )
                        )
                        and (

                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                    or (self.access_method == "bulk_mode")
                                )

                        )
                    )
                )
            )
            else exclude.add("hidden_total_record_count")
        )
        (
            include.add("flat_file_overwrite")
            if (
                (((self.enable_load_or_extract_large_object_via_flat_file)))
                and (
                    (
                        (
                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                or (self.read_operation == "query")
                            )
                        )
                    )
                    or (

                            self.read_operation
                            and (
                                (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                or (self.read_operation == "query_all")
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
            else exclude.add("flat_file_overwrite")
        )
        (
            include.add("access_method")
            if (

                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
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
            else exclude.add("access_method")
        )
        (
            include.add("batch_size")
            if (
                (
                    (
                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "get_deleted_delta")
                            or (self.read_operation == "get_deleted_delta")
                        )
                    )
                )
                or (

                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "get_updated_delta")
                            or (self.read_operation == "get_updated_delta")
                        )

                )
                or (

                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                            or (self.read_operation == "query")
                        )

                )
                or (

                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                            or (self.read_operation == "query_all")
                        )

                )
                or (

                        self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value
                                and "#" in str(self.read_operation.value)
                            )
                            or ("#" in str(self.read_operation))
                        )

                )
            )
            else exclude.add("batch_size")
        )
        (
            include.add("flat_file_column_name")
            if (

                    (
                        ((self.enable_load_or_extract_large_object_via_flat_file))
                        or (
                            (
                                self.enable_load_or_extract_large_object_via_flat_file
                                and "#" in str(self.enable_load_or_extract_large_object_via_flat_file)
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (

                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )

                        )
                        or (

                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
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
            else exclude.add("flat_file_column_name")
        )
        (
            include.add("hidden_job_id")
            if (
                (
                    (
                        (
                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value == "get_the_bulk_load_status"
                                )
                                or (self.read_operation == "get_the_bulk_load_status")
                            )
                        )
                    )
                    or (
                        (
                            self.read_operation
                            and (
                                (
                                    hasattr(self.read_operation, "value")
                                    and self.read_operation.value
                                    and "#" in str(self.read_operation.value)
                                )
                                or ("#" in str(self.read_operation))
                            )
                        )
                    )
                )
                or (

                        (
                            (
                                (
                                    self.read_operation
                                    and (
                                        (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                        or (self.read_operation == "query")
                                    )
                                )
                            )
                            or (
                                (
                                    self.read_operation
                                    and (
                                        (
                                            hasattr(self.read_operation, "value")
                                            and self.read_operation.value == "query_all"
                                        )
                                        or (self.read_operation == "query_all")
                                    )
                                )
                            )
                            or (
                                (
                                    self.read_operation
                                    and (
                                        (
                                            hasattr(self.read_operation, "value")
                                            and self.read_operation.value
                                            and "#" in str(self.read_operation.value)
                                        )
                                        or ("#" in str(self.read_operation))
                                    )
                                )
                            )
                        )
                        and (
                            (
                                (
                                    self.access_method
                                    and (
                                        (
                                            hasattr(self.access_method, "value")
                                            and self.access_method.value == "bulk_mode"
                                        )
                                        or (self.access_method == "bulk_mode")
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
            )
            else exclude.add("hidden_job_id")
        )
        (
            include.add("delta_end_time")
            if (
                (
                    (
                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "get_deleted_delta")
                            or (self.read_operation == "get_deleted_delta")
                        )
                    )
                )
                or (

                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "get_updated_delta")
                            or (self.read_operation == "get_updated_delta")
                        )

                )
                or (

                        self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value
                                and "#" in str(self.read_operation.value)
                            )
                            or ("#" in str(self.read_operation))
                        )

                )
            )
            else exclude.add("delta_end_time")
        )
        (
            include.add("enable_load_or_extract_large_object_via_flat_file")
            if (

                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
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
            else exclude.add("enable_load_or_extract_large_object_via_flat_file")
        )
        (
            include.add("program_generated_reference_soql_query")
            if (
                (
                    (
                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                            or (self.read_operation == "query")
                        )
                    )
                )
                or (

                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                            or (self.read_operation == "query_all")
                        )

                )
                or (

                        self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value
                                and "#" in str(self.read_operation.value)
                            )
                            or ("#" in str(self.read_operation))
                        )

                )
            )
            else exclude.add("program_generated_reference_soql_query")
        )
        (
            include.add("flat_file_folder_location")
            if (

                    (
                        ((self.enable_load_or_extract_large_object_via_flat_file))
                        or (
                            (
                                self.enable_load_or_extract_large_object_via_flat_file
                                and "#" in str(self.enable_load_or_extract_large_object_via_flat_file)
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (

                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )

                        )
                        or (

                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
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
            else exclude.add("flat_file_folder_location")
        )
        (
            include.add("sleep")
            if (

                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value == "get_the_bulk_load_status"
                                    )
                                    or (self.read_operation == "get_the_bulk_load_status")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
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
            else exclude.add("sleep")
        )
        (
            include.add("enable_pk_chunking")
            if (

                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                    or (self.access_method == "bulk_mode")
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
            else exclude.add("enable_pk_chunking")
        )
        (
            include.add("flat_file_content_name")
            if (

                    (
                        ((self.enable_load_or_extract_large_object_via_flat_file))
                        or (
                            (
                                self.enable_load_or_extract_large_object_via_flat_file
                                and "#" in str(self.enable_load_or_extract_large_object_via_flat_file)
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (

                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )

                        )
                        or (

                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
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
            else exclude.add("flat_file_content_name")
        )
        (
            include.add("delta_start_time")
            if (
                (
                    (
                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "get_deleted_delta")
                            or (self.read_operation == "get_deleted_delta")
                        )
                    )
                )
                or (

                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "get_updated_delta")
                            or (self.read_operation == "get_updated_delta")
                        )

                )
                or (

                        self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value
                                and "#" in str(self.read_operation.value)
                            )
                            or ("#" in str(self.read_operation))
                        )

                )
            )
            else exclude.add("delta_start_time")
        )
        (
            include.add("job_id_file_name")
            if (

                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                    or (self.access_method == "bulk_mode")
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
                    and (((self.job_id_in_file)) or (self.job_id_in_file and "#" in str(self.job_id_in_file)))

            )
            else exclude.add("job_id_file_name")
        )
        (
            include.add("soql_query_to_salesforce")
            if (

                    (((not self.table_name)) or ((self.table_name and "#" in str(self.table_name))))
                    and (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (

                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )

                        )
                        or (

                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
                                )

                        )
                    )

            )
            else exclude.add("soql_query_to_salesforce")
        )
        (
            include.add("delta_extract_id")
            if (
                (
                    (
                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "get_deleted_delta")
                            or (self.read_operation == "get_deleted_delta")
                        )
                    )
                )
                or (

                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "get_updated_delta")
                            or (self.read_operation == "get_updated_delta")
                        )

                )
                or (

                        self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value
                                and "#" in str(self.read_operation.value)
                            )
                            or ("#" in str(self.read_operation))
                        )

                )
            )
            else exclude.add("delta_extract_id")
        )
        (
            include.add("job_id")
            if (

                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value == "get_the_bulk_load_status"
                                    )
                                    or (self.read_operation == "get_the_bulk_load_status")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
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
            else exclude.add("job_id")
        )
        (
            include.add("job_id_in_file")
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
                    and (
                        (
                            (
                                (
                                    self.read_operation
                                    and (
                                        (
                                            hasattr(self.read_operation, "value")
                                            and self.read_operation.value == "get_the_bulk_load_status"
                                        )
                                        or (self.read_operation == "get_the_bulk_load_status")
                                    )
                                )
                            )
                            or (
                                (
                                    self.read_operation
                                    and (
                                        (
                                            hasattr(self.read_operation, "value")
                                            and self.read_operation.value
                                            and "#" in str(self.read_operation.value)
                                        )
                                        or ("#" in str(self.read_operation))
                                    )
                                )
                            )
                        )
                        or (

                                (
                                    (
                                        (
                                            self.read_operation
                                            and (
                                                (
                                                    hasattr(self.read_operation, "value")
                                                    and self.read_operation.value == "query"
                                                )
                                                or (self.read_operation == "query")
                                            )
                                        )
                                    )
                                    or (
                                        (
                                            self.read_operation
                                            and (
                                                (
                                                    hasattr(self.read_operation, "value")
                                                    and self.read_operation.value == "query_all"
                                                )
                                                or (self.read_operation == "query_all")
                                            )
                                        )
                                    )
                                    or (
                                        (
                                            self.read_operation
                                            and (
                                                (
                                                    hasattr(self.read_operation, "value")
                                                    and self.read_operation.value
                                                    and "#" in str(self.read_operation.value)
                                                )
                                                or ("#" in str(self.read_operation))
                                            )
                                        )
                                    )
                                )
                                and (
                                    (
                                        (
                                            self.access_method
                                            and (
                                                (
                                                    hasattr(self.access_method, "value")
                                                    and self.access_method.value == "bulk_mode"
                                                )
                                                or (self.access_method == "bulk_mode")
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
                    )

            )
            else exclude.add("job_id_in_file")
        )
        (
            include.add("tenacity")
            if (

                    (
                        (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value == "get_the_bulk_load_status"
                                    )
                                    or (self.read_operation == "get_the_bulk_load_status")
                                )
                            )
                        )
                        or (
                            (
                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
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
            else exclude.add("tenacity")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("business_object")
            if (
                (
                    (
                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "get_deleted_delta")
                            or (self.read_operation == "get_deleted_delta")
                        )
                    )
                )
                or (

                        self.read_operation
                        and (
                            (hasattr(self.read_operation, "value") and self.read_operation.value == "get_updated_delta")
                            or (self.read_operation == "get_updated_delta")
                        )

                )
                or (

                        self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value
                                and "#" in str(self.read_operation.value)
                            )
                            or ("#" in str(self.read_operation))
                        )

                )
            )
            else exclude.add("business_object")
        )
        (
            include.add("hidden_total_record_count")
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
                    and (
                        (
                            (
                                (
                                    self.read_operation
                                    and (
                                        (
                                            hasattr(self.read_operation, "value")
                                            and self.read_operation.value == "get_the_bulk_load_status"
                                        )
                                        or (self.read_operation == "get_the_bulk_load_status")
                                    )
                                )
                            )
                            or (
                                (
                                    self.read_operation
                                    and (
                                        (
                                            hasattr(self.read_operation, "value")
                                            and self.read_operation.value
                                            and "#" in str(self.read_operation.value)
                                        )
                                        or ("#" in str(self.read_operation))
                                    )
                                )
                            )
                        )
                        or (

                                (
                                    (
                                        (
                                            self.read_operation
                                            and (
                                                (
                                                    hasattr(self.read_operation, "value")
                                                    and self.read_operation.value == "query"
                                                )
                                                or (self.read_operation == "query")
                                            )
                                        )
                                    )
                                    or (
                                        (
                                            self.read_operation
                                            and (
                                                (
                                                    hasattr(self.read_operation, "value")
                                                    and self.read_operation.value == "query_all"
                                                )
                                                or (self.read_operation == "query_all")
                                            )
                                        )
                                    )
                                    or (
                                        (
                                            self.read_operation
                                            and (
                                                (
                                                    hasattr(self.read_operation, "value")
                                                    and self.read_operation.value
                                                    and "#" in str(self.read_operation.value)
                                                )
                                                or ("#" in str(self.read_operation))
                                            )
                                        )
                                    )
                                )
                                and (
                                    (
                                        (
                                            self.access_method
                                            and (
                                                (
                                                    hasattr(self.access_method, "value")
                                                    and self.access_method.value == "bulk_mode"
                                                )
                                                or (self.access_method == "bulk_mode")
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
                    )

            )
            else exclude.add("hidden_total_record_count")
        )
        (
            include.add("flat_file_overwrite")
            if (

                    (
                        ((self.enable_load_or_extract_large_object_via_flat_file))
                        or (
                            (
                                self.enable_load_or_extract_large_object_via_flat_file
                                and "#" in str(self.enable_load_or_extract_large_object_via_flat_file)
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query")
                                    or (self.read_operation == "query")
                                )
                            )
                        )
                        or (

                                self.read_operation
                                and (
                                    (hasattr(self.read_operation, "value") and self.read_operation.value == "query_all")
                                    or (self.read_operation == "query_all")
                                )

                        )
                        or (

                                self.read_operation
                                and (
                                    (
                                        hasattr(self.read_operation, "value")
                                        and self.read_operation.value
                                        and "#" in str(self.read_operation.value)
                                    )
                                    or ("#" in str(self.read_operation))
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
            else exclude.add("flat_file_overwrite")
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
            include.add("v2_file_path_job_id")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                    or (self.access_method == "bulk_mode_v2")
                )
            )
            and (self.sf_v2_job_id_in_file == "true" or self.sf_v2_job_id_in_file)
            else exclude.add("v2_file_path_job_id")
        )
        (
            include.add("flat_file_content_name")
            if (
                self.enable_load_or_extract_large_object_via_flat_file
                and "true" in str(self.enable_load_or_extract_large_object_via_flat_file)
            )
            and (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
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
            else exclude.add("flat_file_content_name")
        )
        (
            include.add("access_method")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
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
            else exclude.add("access_method")
        )
        (
            include.add("job_id_file_name")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                    or (self.access_method == "bulk_mode")
                )
            )
            and (self.job_id_in_file == "true" or self.job_id_in_file)
            else exclude.add("job_id_file_name")
        )
        (
            include.add("enable_pk_chunking")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                    or (self.access_method == "bulk_mode")
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
            else exclude.add("enable_pk_chunking")
        )
        (
            include.add("delta_start_time")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_deleted_delta" in str(self.read_operation.value)
                    )
                    or ("get_deleted_delta" in str(self.read_operation))
                )
                or self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_updated_delta" in str(self.read_operation.value)
                    )
                    or ("get_updated_delta" in str(self.read_operation))
                )
            )
            else exclude.add("delta_start_time")
        )
        (
            include.add("delta_end_time")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_deleted_delta" in str(self.read_operation.value)
                    )
                    or ("get_deleted_delta" in str(self.read_operation))
                )
                or self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_updated_delta" in str(self.read_operation.value)
                    )
                    or ("get_updated_delta" in str(self.read_operation))
                )
            )
            else exclude.add("delta_end_time")
        )
        (
            include.add("enable_load_or_extract_large_object_via_flat_file")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
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
            else exclude.add("enable_load_or_extract_large_object_via_flat_file")
        )
        (
            include.add("job_id")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_the_bulk_load_status" in str(self.read_operation.value)
                    )
                    or ("get_the_bulk_load_status" in str(self.read_operation))
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
            else exclude.add("job_id")
        )
        (
            include.add("sleep")
            if (
                self.read_operation
                and (
                    (hasattr(self.read_operation, "value") and self.read_operation.value == "get_the_bulk_load_status")
                    or (self.read_operation == "get_the_bulk_load_status")
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
            else exclude.add("sleep")
        )
        (
            include.add("v2_hidden_total_record_count")
            if (
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
            and (
                (
                    self.read_operation
                    and (
                        (
                            hasattr(self.read_operation, "value")
                            and self.read_operation.value
                            and "query" in str(self.read_operation.value)
                        )
                        or ("query" in str(self.read_operation))
                    )
                    and self.read_operation
                    and (
                        (
                            hasattr(self.read_operation, "value")
                            and self.read_operation.value
                            and "query_all" in str(self.read_operation.value)
                        )
                        or ("query_all" in str(self.read_operation))
                    )
                )
                and (
                    self.access_method
                    and (
                        (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                        or (self.access_method == "bulk_mode_v2")
                    )
                )
            )
            else exclude.add("v2_hidden_total_record_count")
        )
        (
            include.add("flat_file_overwrite")
            if (
                self.enable_load_or_extract_large_object_via_flat_file
                and "true" in str(self.enable_load_or_extract_large_object_via_flat_file)
            )
            and (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
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
            else exclude.add("flat_file_overwrite")
        )
        (
            include.add("v2_hidden_job_id")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                    or (self.access_method == "bulk_mode_v2")
                )
            )
            else exclude.add("v2_hidden_job_id")
        )
        (
            include.add("sf_v2_job_id_in_file")
            if (
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
            and (
                (
                    self.read_operation
                    and (
                        (
                            hasattr(self.read_operation, "value")
                            and self.read_operation.value
                            and "query" in str(self.read_operation.value)
                        )
                        or ("query" in str(self.read_operation))
                    )
                    and self.read_operation
                    and (
                        (
                            hasattr(self.read_operation, "value")
                            and self.read_operation.value
                            and "query_all" in str(self.read_operation.value)
                        )
                        or ("query_all" in str(self.read_operation))
                    )
                )
                and (
                    self.access_method
                    and (
                        (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                        or (self.access_method == "bulk_mode_v2")
                    )
                )
            )
            else exclude.add("sf_v2_job_id_in_file")
        )
        (
            include.add("tenacity")
            if (
                self.read_operation
                and (
                    (hasattr(self.read_operation, "value") and self.read_operation.value == "get_the_bulk_load_status")
                    or (self.read_operation == "get_the_bulk_load_status")
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
            else exclude.add("tenacity")
        )
        (
            include.add("business_object")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_deleted_delta" in str(self.read_operation.value)
                    )
                    or ("get_deleted_delta" in str(self.read_operation))
                )
                or self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_updated_delta" in str(self.read_operation.value)
                    )
                    or ("get_updated_delta" in str(self.read_operation))
                )
            )
            else exclude.add("business_object")
        )
        (
            include.add("job_id_in_file")
            if (
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
            and (
                (
                    self.read_operation
                    and (
                        (
                            hasattr(self.read_operation, "value")
                            and self.read_operation.value
                            and "get_the_bulk_load_status" in str(self.read_operation.value)
                        )
                        or ("get_the_bulk_load_status" in str(self.read_operation))
                    )
                )
                or (
                    (
                        self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value
                                and "query" in str(self.read_operation.value)
                            )
                            or ("query" in str(self.read_operation))
                        )
                        and self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value
                                and "query_all" in str(self.read_operation.value)
                            )
                            or ("query_all" in str(self.read_operation))
                        )
                    )
                    and (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                            or (self.access_method == "bulk_mode")
                        )
                    )
                )
            )
            else exclude.add("job_id_in_file")
        )
        (
            include.add("lookup_type")
            if (self.has_reference_output == "true" or self.has_reference_output)
            else exclude.add("lookup_type")
        )
        (
            include.add("soql_query_to_salesforce")
            if (not self.table_name)
            and (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
                )
            )
            else exclude.add("soql_query_to_salesforce")
        )
        (
            include.add("flat_file_folder_location")
            if (
                self.enable_load_or_extract_large_object_via_flat_file
                and "true" in str(self.enable_load_or_extract_large_object_via_flat_file)
            )
            and (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
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
            else exclude.add("flat_file_folder_location")
        )
        (
            include.add("delta_extract_id")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_deleted_delta" in str(self.read_operation.value)
                    )
                    or ("get_deleted_delta" in str(self.read_operation))
                )
                or self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_updated_delta" in str(self.read_operation.value)
                    )
                    or ("get_updated_delta" in str(self.read_operation))
                )
            )
            else exclude.add("delta_extract_id")
        )
        (
            include.add("batch_size")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_deleted_delta" in str(self.read_operation.value)
                    )
                    or ("get_deleted_delta" in str(self.read_operation))
                )
                or self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_updated_delta" in str(self.read_operation.value)
                    )
                    or ("get_updated_delta" in str(self.read_operation))
                )
                or self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                or self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
                )
            )
            else exclude.add("batch_size")
        )
        (
            include.add("hidden_total_record_count")
            if (
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
            and (
                (
                    self.read_operation
                    and (
                        (
                            hasattr(self.read_operation, "value")
                            and self.read_operation.value
                            and "get_the_bulk_load_status" in str(self.read_operation.value)
                        )
                        or ("get_the_bulk_load_status" in str(self.read_operation))
                    )
                )
                or (
                    (
                        self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value
                                and "query" in str(self.read_operation.value)
                            )
                            or ("query" in str(self.read_operation))
                        )
                        and self.read_operation
                        and (
                            (
                                hasattr(self.read_operation, "value")
                                and self.read_operation.value
                                and "query_all" in str(self.read_operation.value)
                            )
                            or ("query_all" in str(self.read_operation))
                        )
                    )
                    and (
                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                            or (self.access_method == "bulk_mode")
                        )
                    )
                )
            )
            else exclude.add("hidden_total_record_count")
        )
        (
            include.add("flat_file_column_name")
            if (
                self.enable_load_or_extract_large_object_via_flat_file
                and "true" in str(self.enable_load_or_extract_large_object_via_flat_file)
            )
            and (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                and self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
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
            else exclude.add("flat_file_column_name")
        )
        (
            include.add("hidden_job_id")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "get_the_bulk_load_status" in str(self.read_operation.value)
                    )
                    or ("get_the_bulk_load_status" in str(self.read_operation))
                )
            )
            or (
                (
                    self.read_operation
                    and (
                        (
                            hasattr(self.read_operation, "value")
                            and self.read_operation.value
                            and "query" in str(self.read_operation.value)
                        )
                        or ("query" in str(self.read_operation))
                    )
                    and self.read_operation
                    and (
                        (
                            hasattr(self.read_operation, "value")
                            and self.read_operation.value
                            and "query_all" in str(self.read_operation.value)
                        )
                        or ("query_all" in str(self.read_operation))
                    )
                )
                and (
                    self.access_method
                    and (
                        (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                        or (self.access_method == "bulk_mode")
                    )
                )
            )
            else exclude.add("hidden_job_id")
        )
        (
            include.add("program_generated_reference_soql_query")
            if (
                self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query" in str(self.read_operation.value)
                    )
                    or ("query" in str(self.read_operation))
                )
                or self.read_operation
                and (
                    (
                        hasattr(self.read_operation, "value")
                        and self.read_operation.value
                        and "query_all" in str(self.read_operation.value)
                    )
                    or ("query_all" in str(self.read_operation))
                )
            )
            else exclude.add("program_generated_reference_soql_query")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("v2_file_path_job_id")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                            or (self.access_method == "bulk_mode_v2")
                        )

                )
                and (self.sf_v2_job_id_in_file)
            )
            else exclude.add("v2_file_path_job_id")
        )
        (
            include.add("salesforce_concurrency_mode")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                            or (self.access_method == "bulk_mode")
                        )

                )
            )
            else exclude.add("salesforce_concurrency_mode")
        )
        (
            include.add("access_method")
            if (

                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (

                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )

                    )
                    or (

                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )

                    )
                    or (

                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )

                    )

            )
            else exclude.add("access_method")
        )
        (
            include.add("batch_size")
            if (

                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (

                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )

                    )
                    or (

                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )

                    )
                    or (

                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )

                    )

            )
            else exclude.add("batch_size")
        )
        (
            include.add("flat_file_column_name")
            if (
                ((self.enable_load_or_extract_large_object_via_flat_file))
                and (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (

                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )

                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "real_time_mode")
                            or (self.access_method == "real_time_mode")
                        )

                )
            )
            else exclude.add("flat_file_column_name")
        )
        (
            include.add("sf_v2_job_id_in_file")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                            or (self.access_method == "bulk_mode_v2")
                        )

                )
            )
            else exclude.add("sf_v2_job_id_in_file")
        )
        (
            include.add("v2_hard_delete_property")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                            or (self.access_method == "bulk_mode_v2")
                        )

                )
            )
            else exclude.add("v2_hard_delete_property")
        )
        (
            include.add("hidden_job_id")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                            or (self.access_method == "bulk_mode")
                        )

                )
            )
            else exclude.add("hidden_job_id")
        )
        (
            include.add("enable_load_or_extract_large_object_via_flat_file")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "real_time_mode")
                            or (self.access_method == "real_time_mode")
                        )

                )
            )
            else exclude.add("enable_load_or_extract_large_object_via_flat_file")
        )
        (
            include.add("v2_hidden_job_id")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                            or (self.access_method == "bulk_mode_v2")
                        )

                )
            )
            else exclude.add("v2_hidden_job_id")
        )
        (
            include.add("job_id_file_name")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                            or (self.access_method == "bulk_mode")
                        )

                )
                and (self.job_id_in_file)
            )
            else exclude.add("job_id_file_name")
        )
        (
            include.add("empty_recycle_bin")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                            or (self.access_method == "bulk_mode")
                        )

                )
            )
            else exclude.add("empty_recycle_bin")
        )
        (
            include.add("job_id_in_file")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                            or (self.access_method == "bulk_mode")
                        )

                )
            )
            else exclude.add("job_id_in_file")
        )
        (
            include.add("business_object")
            if (

                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (

                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )

                    )
                    or (

                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )

                    )
                    or (

                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )

                    )

            )
            else exclude.add("business_object")
        )
        (
            include.add("v2_keep_temp_file")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                            or (self.access_method == "bulk_mode_v2")
                        )

                )
            )
            else exclude.add("v2_keep_temp_file")
        )
        (
            include.add("keep_temporary_files")
            if (
                (
                    (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                or (self.write_operation == "create")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                or (self.write_operation == "delete")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                or (self.write_operation == "update")
                            )
                        )
                    )
                    or (
                        (
                            self.write_operation
                            and (
                                (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                or (self.write_operation == "upsert")
                            )
                        )
                    )
                )
                and (

                        self.access_method
                        and (
                            (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                            or (self.access_method == "bulk_mode")
                        )

                )
            )
            else exclude.add("keep_temporary_files")
        )
        (
            include.add("salesforce_concurrency_mode")
            if (

                    (
                        (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                    or (self.write_operation == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                    or (self.write_operation == "delete")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                    or (self.write_operation == "update")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                    or (self.write_operation == "upsert")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (
                                        hasattr(self.write_operation, "value")
                                        and self.write_operation.value
                                        and "#" in str(self.write_operation.value)
                                    )
                                    or ("#" in str(self.write_operation))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                    or (self.access_method == "bulk_mode")
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
            else exclude.add("salesforce_concurrency_mode")
        )
        (
            include.add("job_id_file_name")
            if (

                    (
                        (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                    or (self.write_operation == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                    or (self.write_operation == "delete")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                    or (self.write_operation == "update")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                    or (self.write_operation == "upsert")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (
                                        hasattr(self.write_operation, "value")
                                        and self.write_operation.value
                                        and "#" in str(self.write_operation.value)
                                    )
                                    or ("#" in str(self.write_operation))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                    or (self.access_method == "bulk_mode")
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
                    and (((self.job_id_in_file)) or (self.job_id_in_file and "#" in str(self.job_id_in_file)))

            )
            else exclude.add("job_id_file_name")
        )
        (
            include.add("access_method")
            if (
                (
                    (
                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                            or (self.write_operation == "create")
                        )
                    )
                )
                or (

                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                            or (self.write_operation == "delete")
                        )

                )
                or (

                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                            or (self.write_operation == "update")
                        )

                )
                or (

                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                            or (self.write_operation == "upsert")
                        )

                )
                or (

                        self.write_operation
                        and (
                            (
                                hasattr(self.write_operation, "value")
                                and self.write_operation.value
                                and "#" in str(self.write_operation.value)
                            )
                            or ("#" in str(self.write_operation))
                        )

                )
            )
            else exclude.add("access_method")
        )
        (
            include.add("batch_size")
            if (
                (
                    (
                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                            or (self.write_operation == "create")
                        )
                    )
                )
                or (

                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                            or (self.write_operation == "delete")
                        )

                )
                or (

                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                            or (self.write_operation == "update")
                        )

                )
                or (

                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                            or (self.write_operation == "upsert")
                        )

                )
                or (

                        self.write_operation
                        and (
                            (
                                hasattr(self.write_operation, "value")
                                and self.write_operation.value
                                and "#" in str(self.write_operation.value)
                            )
                            or ("#" in str(self.write_operation))
                        )

                )
            )
            else exclude.add("batch_size")
        )
        (
            include.add("empty_recycle_bin")
            if (

                    (
                        (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                    or (self.write_operation == "delete")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (
                                        hasattr(self.write_operation, "value")
                                        and self.write_operation.value
                                        and "#" in str(self.write_operation.value)
                                    )
                                    or ("#" in str(self.write_operation))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                    or (self.access_method == "bulk_mode")
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
            else exclude.add("empty_recycle_bin")
        )
        (
            include.add("flat_file_column_name")
            if (

                    (
                        ((self.enable_load_or_extract_large_object_via_flat_file))
                        or (
                            (
                                self.enable_load_or_extract_large_object_via_flat_file
                                and "#" in str(self.enable_load_or_extract_large_object_via_flat_file)
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                    or (self.write_operation == "create")
                                )
                            )
                        )
                        or (

                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                    or (self.write_operation == "update")
                                )

                        )
                        or (

                                self.write_operation
                                and (
                                    (
                                        hasattr(self.write_operation, "value")
                                        and self.write_operation.value
                                        and "#" in str(self.write_operation.value)
                                    )
                                    or ("#" in str(self.write_operation))
                                )

                        )
                    )
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value == "real_time_mode"
                                    )
                                    or (self.access_method == "real_time_mode")
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
            else exclude.add("flat_file_column_name")
        )
        (
            include.add("job_id_in_file")
            if (

                    (
                        (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                    or (self.write_operation == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                    or (self.write_operation == "delete")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                    or (self.write_operation == "update")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                    or (self.write_operation == "upsert")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (
                                        hasattr(self.write_operation, "value")
                                        and self.write_operation.value
                                        and "#" in str(self.write_operation.value)
                                    )
                                    or ("#" in str(self.write_operation))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                    or (self.access_method == "bulk_mode")
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
            else exclude.add("job_id_in_file")
        )
        (
            include.add("hidden_job_id")
            if (

                    (
                        (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                    or (self.write_operation == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                    or (self.write_operation == "delete")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                    or (self.write_operation == "update")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                    or (self.write_operation == "upsert")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (
                                        hasattr(self.write_operation, "value")
                                        and self.write_operation.value
                                        and "#" in str(self.write_operation.value)
                                    )
                                    or ("#" in str(self.write_operation))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                    or (self.access_method == "bulk_mode")
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
            else exclude.add("hidden_job_id")
        )
        (
            include.add("business_object")
            if (
                (
                    (
                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                            or (self.write_operation == "create")
                        )
                    )
                )
                or (

                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                            or (self.write_operation == "delete")
                        )

                )
                or (

                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                            or (self.write_operation == "update")
                        )

                )
                or (

                        self.write_operation
                        and (
                            (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                            or (self.write_operation == "upsert")
                        )

                )
                or (

                        self.write_operation
                        and (
                            (
                                hasattr(self.write_operation, "value")
                                and self.write_operation.value
                                and "#" in str(self.write_operation.value)
                            )
                            or ("#" in str(self.write_operation))
                        )

                )
            )
            else exclude.add("business_object")
        )
        (
            include.add("enable_load_or_extract_large_object_via_flat_file")
            if (

                    (
                        (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                    or (self.write_operation == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                    or (self.write_operation == "update")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (
                                        hasattr(self.write_operation, "value")
                                        and self.write_operation.value
                                        and "#" in str(self.write_operation.value)
                                    )
                                    or ("#" in str(self.write_operation))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (
                                        hasattr(self.access_method, "value")
                                        and self.access_method.value == "real_time_mode"
                                    )
                                    or (self.access_method == "real_time_mode")
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
            else exclude.add("enable_load_or_extract_large_object_via_flat_file")
        )
        (
            include.add("keep_temporary_files")
            if (

                    (
                        (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "create")
                                    or (self.write_operation == "create")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "delete")
                                    or (self.write_operation == "delete")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "update")
                                    or (self.write_operation == "update")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (hasattr(self.write_operation, "value") and self.write_operation.value == "upsert")
                                    or (self.write_operation == "upsert")
                                )
                            )
                        )
                        or (
                            (
                                self.write_operation
                                and (
                                    (
                                        hasattr(self.write_operation, "value")
                                        and self.write_operation.value
                                        and "#" in str(self.write_operation.value)
                                    )
                                    or ("#" in str(self.write_operation))
                                )
                            )
                        )
                    )
                    and (
                        (
                            (
                                self.access_method
                                and (
                                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                                    or (self.access_method == "bulk_mode")
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
            else exclude.add("keep_temporary_files")
        )
        (
            include.add("salesforce_concurrency_mode")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                    or (self.access_method == "bulk_mode")
                )
            )
            else exclude.add("salesforce_concurrency_mode")
        )
        (
            include.add("v2_file_path_job_id")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                    or (self.access_method == "bulk_mode_v2")
                )
            )
            and (self.sf_v2_job_id_in_file == "true" or self.sf_v2_job_id_in_file)
            else exclude.add("v2_file_path_job_id")
        )
        (
            include.add("v2_keep_temp_file")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                    or (self.access_method == "bulk_mode_v2")
                )
            )
            else exclude.add("v2_keep_temp_file")
        )
        (
            include.add("business_object")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                or self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                or self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                or self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            else exclude.add("business_object")
        )
        (
            include.add("access_method")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                or self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                or self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                or self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            else exclude.add("access_method")
        )
        (
            include.add("job_id_in_file")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                    or (self.access_method == "bulk_mode")
                )
            )
            else exclude.add("job_id_in_file")
        )
        (
            include.add("job_id_file_name")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                    or (self.access_method == "bulk_mode")
                )
            )
            and (self.job_id_in_file == "true" or self.job_id_in_file)
            else exclude.add("job_id_file_name")
        )
        (
            include.add("v2_hard_delete_property")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                    or (self.access_method == "bulk_mode_v2")
                )
            )
            else exclude.add("v2_hard_delete_property")
        )
        (
            include.add("enable_load_or_extract_large_object_via_flat_file")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "real_time_mode")
                    or (self.access_method == "real_time_mode")
                )
            )
            else exclude.add("enable_load_or_extract_large_object_via_flat_file")
        )
        (
            include.add("batch_size")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                or self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                or self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                or self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            else exclude.add("batch_size")
        )
        (
            include.add("flat_file_column_name")
            if (
                self.enable_load_or_extract_large_object_via_flat_file == "true"
                or self.enable_load_or_extract_large_object_via_flat_file
            )
            and (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "real_time_mode")
                    or (self.access_method == "real_time_mode")
                )
            )
            else exclude.add("flat_file_column_name")
        )
        (
            include.add("v2_hidden_job_id")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                    or (self.access_method == "bulk_mode_v2")
                )
            )
            else exclude.add("v2_hidden_job_id")
        )
        (
            include.add("hidden_job_id")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                    or (self.access_method == "bulk_mode")
                )
            )
            else exclude.add("hidden_job_id")
        )
        (
            include.add("empty_recycle_bin")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                    or (self.access_method == "bulk_mode")
                )
            )
            else exclude.add("empty_recycle_bin")
        )
        (
            include.add("keep_temporary_files")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode")
                    or (self.access_method == "bulk_mode")
                )
            )
            else exclude.add("keep_temporary_files")
        )
        (
            include.add("sf_v2_job_id_in_file")
            if (
                self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "create" in str(self.write_operation.value)
                    )
                    or ("create" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "delete" in str(self.write_operation.value)
                    )
                    or ("delete" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "update" in str(self.write_operation.value)
                    )
                    or ("update" in str(self.write_operation))
                )
                and self.write_operation
                and (
                    (
                        hasattr(self.write_operation, "value")
                        and self.write_operation.value
                        and "upsert" in str(self.write_operation.value)
                    )
                    or ("upsert" in str(self.write_operation))
                )
            )
            and (
                self.access_method
                and (
                    (hasattr(self.access_method, "value") and self.access_method.value == "bulk_mode_v2")
                    or (self.access_method == "bulk_mode_v2")
                )
            )
            else exclude.add("sf_v2_job_id_in_file")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "access_method",
            "batch_size",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "business_object",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "delta_end_time",
            "delta_extract_id",
            "delta_start_time",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_java_heap_size",
            "enable_flow_acp_control",
            "enable_load_or_extract_large_object_via_flat_file",
            "enable_pk_chunking",
            "enable_schemaless_design",
            "execution_mode",
            "flat_file_column_name",
            "flat_file_content_name",
            "flat_file_folder_location",
            "flat_file_overwrite",
            "flow_dirty",
            "has_reference_output",
            "hidden_job_id",
            "hidden_total_record_count",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "job_id",
            "job_id_file_name",
            "job_id_in_file",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
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
            "program_generated_reference_soql_query",
            "public_datasource_field_map",
            "public_datasource_locator",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "read_operation",
            "runtime_column_propagation",
            "serialize_modified_properties",
            "sf_v2_job_id_in_file",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sleep",
            "soql_query_to_salesforce",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "table_name",
            "tenacity",
            "unique",
            "v2_file_path_job_id",
            "v2_hidden_job_id",
            "v2_hidden_total_record_count",
        }
        required = {
            "business_object",
            "current_output_link_type",
            "delta_end_time",
            "delta_extract_id",
            "delta_start_time",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "flat_file_column_name",
            "flat_file_content_name",
            "flat_file_folder_location",
            "job_id",
            "job_id_file_name",
            "output_acp_should_hide",
            "password",
            "proxy_server_hostname_or_ip_address",
            "proxy_server_port",
            "soql_query_to_salesforce",
            "url",
            "username",
            "v2_file_path_job_id",
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
            "batch_size",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "business_object",
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
            "ds_java_heap_size",
            "empty_recycle_bin",
            "enable_flow_acp_control",
            "enable_load_or_extract_large_object_via_flat_file",
            "enable_schemaless_design",
            "execution_mode",
            "flat_file_column_name",
            "flow_dirty",
            "hidden_job_id",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "job_id_file_name",
            "job_id_in_file",
            "keep_temporary_files",
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
            "public_datasource_field_map",
            "public_datasource_locator",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "runtime_column_propagation",
            "salesforce_concurrency_mode",
            "serialize_modified_properties",
            "sf_v2_job_id_in_file",
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
            "v2_file_path_job_id",
            "v2_hard_delete_property",
            "v2_hidden_job_id",
            "v2_keep_temp_file",
            "write_operation",
        }
        required = {
            "business_object",
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "flat_file_column_name",
            "job_id_file_name",
            "output_acp_should_hide",
            "password",
            "proxy_server_hostname_or_ip_address",
            "proxy_server_port",
            "url",
            "username",
            "v2_file_path_job_id",
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
        props = {
            "is_reject_output",
            "reject_condition_write_error_row_rejected",
            "reject_data_element_errorcode",
            "reject_data_element_errortext",
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
