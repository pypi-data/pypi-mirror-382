import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.sapbulkextract_connection import (
    SapbulkextractConn,
)
from ibm_watsonx_data_integration.services.datastage.models.enums import SAPBULKEXTRACT
from pydantic import Field
from typing import ClassVar


class sapbulkextract(BaseStage):

    op_name: ClassVar[str] = "sapbulkextract"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/sapbulkextract.svg"
    label: ClassVar[str] = "SAP Bulk Extract"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: SapbulkextractConn = SapbulkextractConn()
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: SAPBULKEXTRACT.BufModeRonly | None = Field(
        SAPBULKEXTRACT.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: SAPBULKEXTRACT.BufferingMode | None = Field(
        SAPBULKEXTRACT.BufferingMode.default, alias="buf_mode"
    )
    collecting: SAPBULKEXTRACT.Collecting | None = Field(SAPBULKEXTRACT.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: SAPBULKEXTRACT.CombinabilityMode | None = Field(
        SAPBULKEXTRACT.CombinabilityMode.auto, alias="combinability"
    )
    condition_clauses: str | None = Field(None, alias="condition_clause")
    connection_count: int | None = Field(1, alias="connection_count")
    create_rfc_destination: bool | None = Field(True, alias="create_rfc_destination")
    create_rfc_destination_name: bool | None = Field(True, alias="create_rfc_destination_name")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execution_mode: SAPBULKEXTRACT.ExecutionMode | None = Field(
        SAPBULKEXTRACT.ExecutionMode.default_par, alias="execmode"
    )
    extract_data_in_foreground: bool | None = Field(False, alias="extract_in_foreground")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    gateway_host: str | None = Field(None, alias="gateway_host")
    generate_sql_query: bool | None = Field(False, alias="generate_sql_query")
    generate_unicode_type_columns: bool | None = Field(False, alias="generate_unicode_columns")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    job: str | None = Field(None, alias="job")
    job_timeout_in_seconds: int | None = Field(600, alias="timeout")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    metadata_table: str | None = Field(None, alias="metadata_table")
    node_count: int | None = Field(1, alias="node_count")
    node_number: int | None = Field(0, alias="node_number")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    package_name: str | None = Field(None, alias="package_name")
    packet_size: int | None = Field(50000, alias="packet_size")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    partition_type: SAPBULKEXTRACT.PartitionType | None = Field(SAPBULKEXTRACT.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: SAPBULKEXTRACT.PreservePartitioning | None = Field(
        SAPBULKEXTRACT.PreservePartitioning.default_propagate, alias="preserve"
    )
    program_id: str | None = Field(None, alias="program_id")
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    rfc_destination_name: str | None = Field(None, alias="rfc_destination")
    row_limit: str | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: SAPBULKEXTRACT.KeyColSelect | None = Field(
        SAPBULKEXTRACT.KeyColSelect.default, alias="keyColSelect"
    )
    sql_query: str | None = Field(None, alias="sql_query")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    system_number_gateway_service: str | None = Field(None, alias="gateway_service")
    table_name: str | None = Field(None, alias="table_name")
    unique: bool | None = Field(None, alias="part_unique")
    use_secured_port: bool | None = Field(False, alias="use_secured_port")

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

        include.add("condition_clauses") if (self.generate_sql_query) else exclude.add("condition_clauses")
        (
            include.add("program_id")
            if (((not self.create_rfc_destination_name)) or (not self.create_rfc_destination))
            else exclude.add("program_id")
        )
        include.add("sql_query") if (not self.generate_sql_query) else exclude.add("sql_query")
        (
            include.add("create_rfc_destination_name")
            if (self.create_rfc_destination)
            else exclude.add("create_rfc_destination_name")
        )
        include.add("table_name") if (self.generate_sql_query) else exclude.add("table_name")
        (
            include.add("rfc_destination_name")
            if (((not self.create_rfc_destination_name)) or (not self.create_rfc_destination))
            else exclude.add("rfc_destination_name")
        )
        (
            include.add("condition_clauses")
            if (
                ((self.generate_sql_query))
                or (self.generate_sql_query and "#" in str(self.generate_sql_query))
            )
            else exclude.add("condition_clauses")
        )
        (
            include.add("program_id")
            if (
                ((not self.create_rfc_destination_name))
                or (not self.create_rfc_destination)
                or (self.create_rfc_destination_name and "#" in str(self.create_rfc_destination_name))
                or (self.create_rfc_destination and "#" in str(self.create_rfc_destination))
            )
            else exclude.add("program_id")
        )
        (
            include.add("sql_query")
            if (
                ((not self.generate_sql_query))
                or (self.generate_sql_query and "#" in str(self.generate_sql_query))
            )
            else exclude.add("sql_query")
        )
        (
            include.add("create_rfc_destination_name")
            if (
                ((self.create_rfc_destination))
                or (self.create_rfc_destination and "#" in str(self.create_rfc_destination))
            )
            else exclude.add("create_rfc_destination_name")
        )
        (
            include.add("table_name")
            if (
                ((self.generate_sql_query))
                or (self.generate_sql_query and "#" in str(self.generate_sql_query))
            )
            else exclude.add("table_name")
        )
        (
            include.add("rfc_destination_name")
            if (
                ((not self.create_rfc_destination_name))
                or (not self.create_rfc_destination)
                or (self.create_rfc_destination_name and "#" in str(self.create_rfc_destination_name))
                or (self.create_rfc_destination and "#" in str(self.create_rfc_destination))
            )
            else exclude.add("rfc_destination_name")
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
        include.add("defer_credentials") if (()) else exclude.add("defer_credentials")
        (
            include.add("create_rfc_destination_name")
            if (self.create_rfc_destination == "true" or self.create_rfc_destination)
            else exclude.add("create_rfc_destination_name")
        )
        (
            include.add("rfc_destination_name")
            if (self.create_rfc_destination_name == "false" or not self.create_rfc_destination_name)
            or (self.create_rfc_destination == "false" or not self.create_rfc_destination)
            else exclude.add("rfc_destination_name")
        )
        (
            include.add("table_name")
            if (self.generate_sql_query == "true" or self.generate_sql_query)
            else exclude.add("table_name")
        )
        (
            include.add("program_id")
            if (self.create_rfc_destination_name == "false" or not self.create_rfc_destination_name)
            or (self.create_rfc_destination == "false" or not self.create_rfc_destination)
            else exclude.add("program_id")
        )
        (
            include.add("condition_clauses")
            if (self.generate_sql_query == "true" or self.generate_sql_query)
            else exclude.add("condition_clauses")
        )
        (
            include.add("sql_query")
            if (self.generate_sql_query == "false" or not self.generate_sql_query)
            else exclude.add("sql_query")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "condition_clauses",
            "connection_count",
            "create_rfc_destination",
            "create_rfc_destination_name",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_java_heap_size",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execution_mode",
            "extract_data_in_foreground",
            "flow_dirty",
            "gateway_host",
            "generate_sql_query",
            "generate_unicode_type_columns",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "job",
            "job_timeout_in_seconds",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "metadata_table",
            "node_count",
            "node_number",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "package_name",
            "packet_size",
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
            "program_id",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "rfc_destination_name",
            "row_limit",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "sql_query",
            "stable",
            "stage_description",
            "system_number_gateway_service",
            "table_name",
            "unique",
            "use_secured_port",
        }
        required = {
            "application_server",
            "client_number",
            "connection_type",
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "group",
            "language",
            "message_server",
            "output_acp_should_hide",
            "sap_application_system_number",
            "snc_name",
            "snc_partner_name",
            "system_id",
            "system_number",
            "username",
            "x_509_certificate",
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
        return {"min": 0, "max": 0}

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

    def get_target_props(self) -> dict:
        include, exclude = self.validate_target()
        props = {}
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
