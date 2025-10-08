import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.planning_analytics_connection import (
    PlanningAnalyticsConn,
)
from ibm_watsonx_data_integration.services.datastage.models.enums import PLANNING_ANALYTICS
from pydantic import Field
from typing import ClassVar


class planning_analytics(BaseStage):

    op_name: ClassVar[str] = "tm1odata"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/tm1odata.svg"
    label: ClassVar[str] = "IBM Planning Analytics"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: PlanningAnalyticsConn = PlanningAnalyticsConn()
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: PLANNING_ANALYTICS.BufModeRonly | None = Field(
        PLANNING_ANALYTICS.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: PLANNING_ANALYTICS.BufferingMode | None = Field(
        PLANNING_ANALYTICS.BufferingMode.default, alias="buf_mode"
    )
    byte_limit: str | None = Field(None, alias="byte_limit")
    collecting: PLANNING_ANALYTICS.Collecting | None = Field(PLANNING_ANALYTICS.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: PLANNING_ANALYTICS.CombinabilityMode | None = Field(
        PLANNING_ANALYTICS.CombinabilityMode.auto, alias="combinability"
    )
    connection_mode: PLANNING_ANALYTICS.ConnectionMode | None = Field(
        PLANNING_ANALYTICS.ConnectionMode.cube_name, alias="connection_mode"
    )
    create_data_asset: bool | None = Field(False, alias="registerDataAsset")
    creation_order: bool | None = Field(False, alias="use_creation_order")
    cube_name: str = Field(None, alias="cube_name")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    custom_dimension_mapping_information: str | None = Field(None, alias="custom_mapping_info")
    custom_mapping: bool | None = Field(None, alias="use_custom_mapping")
    data_asset_name: str = Field(None, alias="dataAssetName")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execution_mode: PLANNING_ANALYTICS.ExecutionMode | None = Field(
        PLANNING_ANALYTICS.ExecutionMode.default_seq, alias="execmode"
    )
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    mdx_statement: str | None = Field(None, alias="mdx_statement")
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
    partition_type: PLANNING_ANALYTICS.PartitionType | None = Field(
        PLANNING_ANALYTICS.PartitionType.auto, alias="part_type"
    )
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: PLANNING_ANALYTICS.PreservePartitioning | None = Field(
        PLANNING_ANALYTICS.PreservePartitioning.default_propagate, alias="preserve"
    )
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sl_client_cert: str | None = Field(None, alias="sl_client_cert")
    sl_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    sl_connector_id: str | None = Field(None, alias="sl_connector_id")
    sl_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    sl_endpoint_name: str | None = Field(None, alias="sl_endpoint_name")
    sl_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    sl_host_original: str | None = Field(None, alias="sl_host_original")
    sl_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    sl_location_id: str | None = Field(None, alias="sl_location_id")
    sl_service_url: str | None = Field(None, alias="sl_service_url")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: PLANNING_ANALYTICS.KeyColSelect | None = Field(
        PLANNING_ANALYTICS.KeyColSelect.default, alias="keyColSelect"
    )
    ssl_certificate_hostname: str | None = Field(None, alias="ssl_certificate_host")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    unique: bool | None = Field(None, alias="part_unique")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    view: str = Field(None, alias="view_name")
    view_group: str = Field(None, alias="view_group")
    write_to_consolidation: bool | None = Field(None, alias="write_to_consolidation")

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
            include.add("view_group")
            if (
                ((not self.mdx_statement))
                and (


                            self.connection_mode
                            and (
                                (hasattr(self.connection_mode, "value") and self.connection_mode.value == "cube_name")
                                or (self.connection_mode == "cube_name")
                            )


                )
            )
            else exclude.add("view_group")
        )
        (
            include.add("mdx_statement")
            if (
                ((not self.cube_name))
                and (not self.view)
                and (not self.view_group)
                and (


                            self.connection_mode
                            and (
                                (
                                    hasattr(self.connection_mode, "value")
                                    and self.connection_mode.value == "mdx_statement"
                                )
                                or (self.connection_mode == "mdx_statement")
                            )


                )
            )
            else exclude.add("mdx_statement")
        )
        (
            include.add("view")
            if (
                ((not self.mdx_statement))
                and (


                            self.connection_mode
                            and (
                                (hasattr(self.connection_mode, "value") and self.connection_mode.value == "cube_name")
                                or (self.connection_mode == "cube_name")
                            )


                )
            )
            else exclude.add("view")
        )
        (
            include.add("cube_name")
            if (
                ((not self.mdx_statement))
                and (


                            self.connection_mode
                            and (
                                (hasattr(self.connection_mode, "value") and self.connection_mode.value == "cube_name")
                                or (self.connection_mode == "cube_name")
                            )


                )
            )
            else exclude.add("cube_name")
        )
        (
            include.add("view_group")
            if (

                    (((not self.mdx_statement)) or ((self.mdx_statement and "#" in str(self.mdx_statement))))
                    and (
                        (
                            (
                                self.connection_mode
                                and (
                                    (
                                        hasattr(self.connection_mode, "value")
                                        and self.connection_mode.value == "cube_name"
                                    )
                                    or (self.connection_mode == "cube_name")
                                )
                            )
                        )
                        or (

                                self.connection_mode
                                and (
                                    (
                                        hasattr(self.connection_mode, "value")
                                        and self.connection_mode.value
                                        and "#" in str(self.connection_mode.value)
                                    )
                                    or ("#" in str(self.connection_mode))
                                )

                        )
                    )

            )
            else exclude.add("view_group")
        )
        (
            include.add("mdx_statement")
            if (

                    (((not self.cube_name)) or ((self.cube_name and "#" in str(self.cube_name))))
                    and (((not self.view)) or (self.view and "#" in str(self.view)))
                    and (((not self.view_group)) or (self.view_group and "#" in str(self.view_group)))
                    and (
                        (
                            (
                                self.connection_mode
                                and (
                                    (
                                        hasattr(self.connection_mode, "value")
                                        and self.connection_mode.value == "mdx_statement"
                                    )
                                    or (self.connection_mode == "mdx_statement")
                                )
                            )
                        )
                        or (

                                self.connection_mode
                                and (
                                    (
                                        hasattr(self.connection_mode, "value")
                                        and self.connection_mode.value
                                        and "#" in str(self.connection_mode.value)
                                    )
                                    or ("#" in str(self.connection_mode))
                                )

                        )
                    )

            )
            else exclude.add("mdx_statement")
        )
        (
            include.add("view")
            if (

                    (((not self.mdx_statement)) or ((self.mdx_statement and "#" in str(self.mdx_statement))))
                    and (
                        (
                            (
                                self.connection_mode
                                and (
                                    (
                                        hasattr(self.connection_mode, "value")
                                        and self.connection_mode.value == "cube_name"
                                    )
                                    or (self.connection_mode == "cube_name")
                                )
                            )
                        )
                        or (

                                self.connection_mode
                                and (
                                    (
                                        hasattr(self.connection_mode, "value")
                                        and self.connection_mode.value
                                        and "#" in str(self.connection_mode.value)
                                    )
                                    or ("#" in str(self.connection_mode))
                                )

                        )
                    )

            )
            else exclude.add("view")
        )
        (
            include.add("cube_name")
            if (

                    (((not self.mdx_statement)) or ((self.mdx_statement and "#" in str(self.mdx_statement))))
                    and (
                        (
                            (
                                self.connection_mode
                                and (
                                    (
                                        hasattr(self.connection_mode, "value")
                                        and self.connection_mode.value == "cube_name"
                                    )
                                    or (self.connection_mode == "cube_name")
                                )
                            )
                        )
                        or (

                                self.connection_mode
                                and (
                                    (
                                        hasattr(self.connection_mode, "value")
                                        and self.connection_mode.value
                                        and "#" in str(self.connection_mode.value)
                                    )
                                    or ("#" in str(self.connection_mode))
                                )

                        )
                    )

            )
            else exclude.add("cube_name")
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
            include.add("cube_name")
            if (not self.mdx_statement)
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "cube_name" in str(self.connection_mode.value)
                    )
                    or ("cube_name" in str(self.connection_mode))
                )
            )
            else exclude.add("cube_name")
        )
        (
            include.add("view")
            if (not self.mdx_statement)
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "cube_name" in str(self.connection_mode.value)
                    )
                    or ("cube_name" in str(self.connection_mode))
                )
            )
            else exclude.add("view")
        )
        (
            include.add("view_group")
            if (not self.mdx_statement)
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "cube_name" in str(self.connection_mode.value)
                    )
                    or ("cube_name" in str(self.connection_mode))
                )
            )
            else exclude.add("view_group")
        )
        (
            include.add("mdx_statement")
            if (not self.cube_name)
            and (not self.view)
            and (not self.view_group)
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "mdx_statement" in str(self.connection_mode.value)
                    )
                    or ("mdx_statement" in str(self.connection_mode))
                )
            )
            else exclude.add("mdx_statement")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("data_asset_name") if (self.create_data_asset) else exclude.add("data_asset_name")
        include.add("create_data_asset") if (()) else exclude.add("create_data_asset")
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "byte_limit",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "connection_mode",
            "creation_order",
            "cube_name",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execution_mode",
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
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "mdx_statement",
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
            "row_limit",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "unique",
            "view",
            "view_group",
        }
        required = {
            "access_token",
            "authentication_type",
            "cube_name",
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "namespace",
            "output_acp_should_hide",
            "password",
            "tm1_server_api_root_url",
            "username",
            "view",
            "view_group",
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
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "connection_mode",
            "create_data_asset",
            "cube_name",
            "current_output_link_type",
            "custom_dimension_mapping_information",
            "custom_mapping",
            "data_asset_name",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execution_mode",
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
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "mdx_statement",
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
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "unique",
            "view",
            "view_group",
            "write_to_consolidation",
        }
        required = {
            "access_token",
            "authentication_type",
            "cube_name",
            "current_output_link_type",
            "data_asset_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "mdx_statement",
            "namespace",
            "output_acp_should_hide",
            "password",
            "tm1_server_api_root_url",
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
