import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.apache_kafka_connection import ApacheKafkaConn
from ibm_watsonx_data_integration.services.datastage.models.enums import APACHE_KAFKA
from pydantic import Field
from typing import ClassVar


class apache_kafka(BaseStage):

    op_name: ClassVar[str] = "KafkaConnectorPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/KafkaConnectorPX.svg"
    label: ClassVar[str] = "Apache Kafka"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: ApacheKafkaConn = ApacheKafkaConn()
    advanced_kafka_config_options: str | None = Field(None, alias="advanced_kafka_config_options")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: APACHE_KAFKA.BufModeRonly | None = Field(
        APACHE_KAFKA.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: APACHE_KAFKA.BufferingMode | None = Field(APACHE_KAFKA.BufferingMode.default, alias="buf_mode")
    collecting: APACHE_KAFKA.Collecting | None = Field(APACHE_KAFKA.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: APACHE_KAFKA.CombinabilityMode | None = Field(
        APACHE_KAFKA.CombinabilityMode.auto, alias="combinability"
    )
    conn_registry_key_chain_pem: str | None = Field(None, alias="conn_registry_key_chain_pem")
    conn_registry_key_password: str = Field(None, alias="conn_registry_key_password")
    conn_registry_key_pem: str | None = Field(None, alias="conn_registry_key_pem")
    conn_registry_keystore_location: str | None = Field(None, alias="conn_registry_keystore_location")
    conn_registry_keystore_password: str = Field(None, alias="conn_registry_keystore_password")
    conn_registry_keytab: str | None = Field(None, alias="conn_registry_keytab")
    conn_registry_password: str = Field(None, alias="conn_registry_password")
    conn_registry_principal_name: str | None = Field(None, alias="conn_registry_principal_name")
    conn_registry_truststore_pem: str | None = Field(None, alias="conn_registry_truststore_pem")
    conn_registry_username: str | None = Field(None, alias="conn_registry_username")
    conn_schema_registry_authentication: APACHE_KAFKA.ConnSchemaRegistryAuthentication | None = Field(
        APACHE_KAFKA.ConnSchemaRegistryAuthentication.none, alias="conn_schema_registry_authentication"
    )
    conn_schema_registry_secure: APACHE_KAFKA.ConnSchemaRegistrySecure | None = Field(
        APACHE_KAFKA.ConnSchemaRegistrySecure.none, alias="conn_schema_registry_secure"
    )
    consumer_group: str | None = Field(None, alias="consumer_group_name")
    continuous_mode: bool | None = Field(False, alias="continuous_mode")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    ds_advanced_client_logging: bool | None = Field(False, alias="_advanced_client_logging")
    ds_advanced_kafka_config_options: bool | None = Field(False, alias="_advanced_kafka_config_options")
    ds_client_logging_level: APACHE_KAFKA.DSClientLoggingLevel | None = Field(
        APACHE_KAFKA.DSClientLoggingLevel.off, alias="_client_logging_level"
    )
    ds_consumer_group_name: str | None = Field(None, alias="_consumer_group_name")
    ds_isolation_level: APACHE_KAFKA.DSIsolationLevel | None = Field(
        APACHE_KAFKA.DSIsolationLevel.read_uncommitted, alias="_isolation_level"
    )
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    ds_kafka_config_options: str | None = Field(None, alias="_kafka_config_options")
    ds_key_serializer_type: APACHE_KAFKA.DSKeySerializerType | None = Field(
        APACHE_KAFKA.DSKeySerializerType.string, alias="_key_serializer_type"
    )
    ds_max_messages: int | None = Field(None, alias="_max_messages")
    ds_max_poll_records: int | None = Field(100, alias="_max_poll_records")
    ds_reset_policy: APACHE_KAFKA.DSResetPolicy | None = Field(
        APACHE_KAFKA.DSResetPolicy.latest, alias="_reset_policy"
    )
    ds_start_offset: str | None = Field(None, alias="_start_offset")
    ds_stop_message: str | None = Field(None, alias="_stop_message")
    ds_timeout: int | None = Field(None, alias="_timeout")
    ds_timeout_after_last_message: int | None = Field(30, alias="_timeout_after_last_message")
    ds_use_datastage: bool | None = Field(True, alias="_use_datastage")
    ds_value_serializer_type: APACHE_KAFKA.DSValueSerializerType | None = Field(
        APACHE_KAFKA.DSValueSerializerType.string, alias="_value_serializer_type"
    )
    ds_warn_and_error_log: APACHE_KAFKA.DSWarnAndErrorLog | None = Field(
        APACHE_KAFKA.DSWarnAndErrorLog.log_as_informational, alias="_warn_and_error_log"
    )
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    end_of_data: bool | None = Field(False, alias="end_of_data")
    end_of_wave: bool | None = Field(False, alias="end_of_wave")
    execution_mode: APACHE_KAFKA.ExecutionMode | None = Field(
        APACHE_KAFKA.ExecutionMode.default_par, alias="execmode"
    )
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    generate_unicode_type_columns: bool | None = Field(False, alias="generate_unicode_columns")
    heap_size: int | None = Field(256, alias="heap_size")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    isolation_level: APACHE_KAFKA.IsolationLevel | None = Field(
        APACHE_KAFKA.IsolationLevel.read_uncommitted, alias="isolation_level"
    )
    job_timeout_in_seconds: int | None = Field(30, alias="timeout")
    kafka_client_logging_level: APACHE_KAFKA.KafkaClientLoggingLevel | None = Field(
        APACHE_KAFKA.KafkaClientLoggingLevel.off, alias="kafka_client_logging_level"
    )
    kafka_config_options: str | None = Field(None, alias="kafka_config_options")
    kafka_start_offset: str | None = Field(None, alias="start_offset")
    kafka_warning_and_error_logs: APACHE_KAFKA.KafkaWarningAndErrorLogs | None = Field(
        APACHE_KAFKA.KafkaWarningAndErrorLogs.log_as_informational, alias="kafka_warning_and_error_logs"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    key_serializer: APACHE_KAFKA.KeySerializer | None = Field(
        APACHE_KAFKA.KeySerializer.string, alias="key_serializer_type"
    )
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    messages_read_within_single_request: int | None = Field(100, alias="max_poll_records")
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
    partition_type: APACHE_KAFKA.PartitionType | None = Field(APACHE_KAFKA.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: APACHE_KAFKA.PreservePartitioning | None = Field(
        APACHE_KAFKA.PreservePartitioning.default_propagate, alias="preserve"
    )
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    record_count: int | None = Field(0, alias="record_count")
    registry_trust_location: str | None = Field(None, alias="registry_trust_location")
    registry_trust_password: str | None = Field(None, alias="registry_trust_password")
    reset_policy: APACHE_KAFKA.ResetPolicy | None = Field(APACHE_KAFKA.ResetPolicy.earliest, alias="reset_policy")
    row_limit: int | None = Field(None, alias="row_limit")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    schema_registry_url: str | None = Field(None, alias="conn_schema_registry_url")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: APACHE_KAFKA.KeyColSelect | None = Field(APACHE_KAFKA.KeyColSelect.default, alias="keyColSelect")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    stop_message_pattern: str | None = Field(None, alias="stop_message")
    time_interval: int | None = Field(0, alias="time_interval")
    topic_name: str = Field(None, alias="topic_name")
    total_number_of_messages: int | None = Field(100, alias="max_messages")
    unique: bool | None = Field(None, alias="part_unique")
    value_serializer: APACHE_KAFKA.ValueSerializer | None = Field(
        APACHE_KAFKA.ValueSerializer.string, alias="value_serializer_type"
    )

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

        include.add("registry_trust_password") if (()) else exclude.add("registry_trust_password")
        (
            include.add("kafka_warning_and_error_logs")
            if (

                    (
                        (
                            self.kafka_client_logging_level
                            and (
                                (
                                    hasattr(self.kafka_client_logging_level, "value")
                                    and self.kafka_client_logging_level.value == "debug"
                                )
                                or (self.kafka_client_logging_level == "debug")
                            )
                        )
                    )
                    or (

                            self.kafka_client_logging_level
                            and (
                                (
                                    hasattr(self.kafka_client_logging_level, "value")
                                    and self.kafka_client_logging_level.value == "error"
                                )
                                or (self.kafka_client_logging_level == "error")
                            )

                    )
                    or (

                            self.kafka_client_logging_level
                            and (
                                (
                                    hasattr(self.kafka_client_logging_level, "value")
                                    and self.kafka_client_logging_level.value == "fatal"
                                )
                                or (self.kafka_client_logging_level == "fatal")
                            )

                    )
                    or (

                            self.kafka_client_logging_level
                            and (
                                (
                                    hasattr(self.kafka_client_logging_level, "value")
                                    and self.kafka_client_logging_level.value == "info"
                                )
                                or (self.kafka_client_logging_level == "info")
                            )

                    )
                    or (

                            self.kafka_client_logging_level
                            and (
                                (
                                    hasattr(self.kafka_client_logging_level, "value")
                                    and self.kafka_client_logging_level.value == "trace"
                                )
                                or (self.kafka_client_logging_level == "trace")
                            )

                    )
                    or (

                            self.kafka_client_logging_level
                            and (
                                (
                                    hasattr(self.kafka_client_logging_level, "value")
                                    and self.kafka_client_logging_level.value == "warn"
                                )
                                or (self.kafka_client_logging_level == "warn")
                            )

                    )

            )
            else exclude.add("kafka_warning_and_error_logs")
        )
        include.add("time_interval") if (self.record_count == "0.0") else exclude.add("time_interval")
        (
            include.add("job_timeout_in_seconds")
            if (not self.continuous_mode)
            else exclude.add("job_timeout_in_seconds")
        )
        include.add("end_of_data") if (self.end_of_wave) else exclude.add("end_of_data")
        include.add("registry_trust_location") if (()) else exclude.add("registry_trust_location")
        (
            include.add("stop_message_pattern")
            if (self.continuous_mode)
            else exclude.add("stop_message_pattern")
        )
        (
            include.add("ds_client_logging_level")
            if (self.ds_advanced_client_logging)
            else exclude.add("ds_client_logging_level")
        )
        (
            include.add("ds_warn_and_error_log")
            if (
                (((self.ds_advanced_client_logging)))
                and (
                    ((self.ds_client_logging_level == "debug"))
                    or (self.ds_client_logging_level == "error")
                    or (self.ds_client_logging_level == "fatal")
                    or (self.ds_client_logging_level == "info")
                    or (self.ds_client_logging_level == "trace")
                    or (self.ds_client_logging_level == "warn")
                )
            )
            else exclude.add("ds_warn_and_error_log")
        )
        (
            include.add("ds_kafka_config_options")
            if (self.ds_advanced_kafka_config_options)
            else exclude.add("ds_kafka_config_options")
        )
        (
            include.add("registry_trust_password")
            if (((((()) or (())))) and (self.ds_use_datastage))
            else exclude.add("registry_trust_password")
        )
        (
            include.add("ds_client_logging_level")
            if (

                    (
                        ((self.ds_advanced_client_logging))
                        or ((self.ds_advanced_client_logging and "#" in str(self.ds_advanced_client_logging)))
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("ds_client_logging_level")
        )
        (
            include.add("ds_warn_and_error_log")
            if (

                    (
                        (
                            (
                                ((self.ds_advanced_client_logging))
                                or ((self.ds_advanced_client_logging and "#" in str(self.ds_advanced_client_logging)))
                            )
                            and (
                                ((self.ds_client_logging_level == "debug"))
                                or ((self.ds_client_logging_level == "error"))
                                or ((self.ds_client_logging_level == "fatal"))
                                or ((self.ds_client_logging_level == "info"))
                                or ((self.ds_client_logging_level == "trace"))
                                or ((self.ds_client_logging_level == "warn"))
                                or ((self.ds_client_logging_level and "#" in str(self.ds_client_logging_level)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("ds_warn_and_error_log")
        )
        (
            include.add("kafka_warning_and_error_logs")
            if (

                    (
                        (
                            (
                                self.kafka_client_logging_level
                                and (
                                    (
                                        hasattr(self.kafka_client_logging_level, "value")
                                        and self.kafka_client_logging_level.value == "debug"
                                    )
                                    or (self.kafka_client_logging_level == "debug")
                                )
                            )
                        )
                        or (
                            (
                                self.kafka_client_logging_level
                                and (
                                    (
                                        hasattr(self.kafka_client_logging_level, "value")
                                        and self.kafka_client_logging_level.value == "error"
                                    )
                                    or (self.kafka_client_logging_level == "error")
                                )
                            )
                        )
                        or (
                            (
                                self.kafka_client_logging_level
                                and (
                                    (
                                        hasattr(self.kafka_client_logging_level, "value")
                                        and self.kafka_client_logging_level.value == "fatal"
                                    )
                                    or (self.kafka_client_logging_level == "fatal")
                                )
                            )
                        )
                        or (
                            (
                                self.kafka_client_logging_level
                                and (
                                    (
                                        hasattr(self.kafka_client_logging_level, "value")
                                        and self.kafka_client_logging_level.value == "info"
                                    )
                                    or (self.kafka_client_logging_level == "info")
                                )
                            )
                        )
                        or (
                            (
                                self.kafka_client_logging_level
                                and (
                                    (
                                        hasattr(self.kafka_client_logging_level, "value")
                                        and self.kafka_client_logging_level.value == "trace"
                                    )
                                    or (self.kafka_client_logging_level == "trace")
                                )
                            )
                        )
                        or (
                            (
                                self.kafka_client_logging_level
                                and (
                                    (
                                        hasattr(self.kafka_client_logging_level, "value")
                                        and self.kafka_client_logging_level.value == "warn"
                                    )
                                    or (self.kafka_client_logging_level == "warn")
                                )
                            )
                        )
                        or (
                            (
                                self.kafka_client_logging_level
                                and (
                                    (
                                        hasattr(self.kafka_client_logging_level, "value")
                                        and self.kafka_client_logging_level.value
                                        and "#" in str(self.kafka_client_logging_level.value)
                                    )
                                    or ("#" in str(self.kafka_client_logging_level))
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("kafka_warning_and_error_logs")
        )
        (
            include.add("time_interval")
            if (

                    (((self.record_count == 0)) or ((self.record_count and "#" in str(self.record_count))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("time_interval")
        )
        (
            include.add("job_timeout_in_seconds")
            if (

                    (((not self.continuous_mode)) or ((self.continuous_mode and "#" in str(self.continuous_mode))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("job_timeout_in_seconds")
        )
        (
            include.add("end_of_data")
            if (

                    (((self.end_of_wave)) or ((self.end_of_wave and "#" in str(self.end_of_wave))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("end_of_data")
        )
        (
            include.add("registry_trust_location")
            if (((((()) or (())))) and (self.ds_use_datastage))
            else exclude.add("registry_trust_location")
        )
        (
            include.add("ds_kafka_config_options")
            if (

                    (
                        ((self.ds_advanced_kafka_config_options))
                        or (
                            (
                                self.ds_advanced_kafka_config_options
                                and "#" in str(self.ds_advanced_kafka_config_options)
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("ds_kafka_config_options")
        )
        (
            include.add("stop_message_pattern")
            if (

                    (((self.continuous_mode)) or ((self.continuous_mode and "#" in str(self.continuous_mode))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("stop_message_pattern")
        )
        include.add("ds_java_heap_size") if (not self.ds_use_datastage) else exclude.add("ds_java_heap_size")
        (
            include.add("advanced_kafka_config_options")
            if (self.ds_use_datastage)
            else exclude.add("advanced_kafka_config_options")
        )
        include.add("end_of_wave") if (self.ds_use_datastage) else exclude.add("end_of_wave")
        (
            include.add("kafka_config_options")
            if (self.ds_use_datastage)
            else exclude.add("kafka_config_options")
        )
        include.add("ds_max_messages") if (not self.ds_use_datastage) else exclude.add("ds_max_messages")
        (
            include.add("messages_read_within_single_request")
            if (self.ds_use_datastage)
            else exclude.add("messages_read_within_single_request")
        )
        include.add("heap_size") if (self.ds_use_datastage) else exclude.add("heap_size")
        include.add("reset_policy") if (self.ds_use_datastage) else exclude.add("reset_policy")
        include.add("ds_timeout") if (not self.ds_use_datastage) else exclude.add("ds_timeout")
        (
            include.add("kafka_client_logging_level")
            if (self.ds_use_datastage)
            else exclude.add("kafka_client_logging_level")
        )
        include.add("continuous_mode") if (self.ds_use_datastage) else exclude.add("continuous_mode")
        include.add("ds_max_poll_records") if (not self.ds_use_datastage) else exclude.add("ds_max_poll_records")
        include.add("key_serializer") if (self.ds_use_datastage) else exclude.add("key_serializer")
        (
            include.add("ds_advanced_kafka_config_options")
            if (not self.ds_use_datastage)
            else exclude.add("ds_advanced_kafka_config_options")
        )
        (
            include.add("ds_value_serializer_type")
            if (not self.ds_use_datastage)
            else exclude.add("ds_value_serializer_type")
        )
        (
            include.add("ds_timeout_after_last_message")
            if (not self.ds_use_datastage)
            else exclude.add("ds_timeout_after_last_message")
        )
        include.add("record_count") if (self.ds_use_datastage) else exclude.add("record_count")
        include.add("ds_isolation_level") if (not self.ds_use_datastage) else exclude.add("ds_isolation_level")
        (
            include.add("ds_advanced_client_logging")
            if (not self.ds_use_datastage)
            else exclude.add("ds_advanced_client_logging")
        )
        include.add("consumer_group") if (self.ds_use_datastage) else exclude.add("consumer_group")
        (
            include.add("total_number_of_messages")
            if (self.ds_use_datastage)
            else exclude.add("total_number_of_messages")
        )
        include.add("ds_reset_policy") if (not self.ds_use_datastage) else exclude.add("ds_reset_policy")
        include.add("value_serializer") if (self.ds_use_datastage) else exclude.add("value_serializer")
        (
            include.add("generate_unicode_type_columns")
            if (not self.ds_use_datastage)
            else exclude.add("generate_unicode_type_columns")
        )
        include.add("isolation_level") if (self.ds_use_datastage) else exclude.add("isolation_level")
        include.add("ds_start_offset") if (not self.ds_use_datastage) else exclude.add("ds_start_offset")
        (
            include.add("ds_key_serializer_type")
            if (not self.ds_use_datastage)
            else exclude.add("ds_key_serializer_type")
        )
        (
            include.add("ds_consumer_group_name")
            if (not self.ds_use_datastage)
            else exclude.add("ds_consumer_group_name")
        )
        include.add("row_limit") if (not self.ds_use_datastage) else exclude.add("row_limit")
        include.add("ds_stop_message") if (not self.ds_use_datastage) else exclude.add("ds_stop_message")
        include.add("kafka_start_offset") if (self.ds_use_datastage) else exclude.add("kafka_start_offset")
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
        (
            include.add("conn_registry_key_pem")
            if (

                    (
                        ((self.conn_schema_registry_secure == "ssl"))
                        or ((self.conn_schema_registry_secure and "#" in str(self.conn_schema_registry_secure)))
                    )
                    and ((()) or (()))
                    and (not self.defer_credentials)
                    and (())

            )
            else exclude.add("conn_registry_key_pem")
        )
        (
            include.add("conn_schema_registry_authentication")
            if ((()) and (((()) or (())) or ((()) or (()))))
            else exclude.add("conn_schema_registry_authentication")
        )
        (
            include.add("conn_registry_keystore_location")
            if (

                    (())
                    and (
                        (
                            (
                                ((()) or (()))
                                and (
                                    ((self.conn_schema_registry_secure == "ssl"))
                                    or (
                                        (
                                            self.conn_schema_registry_secure
                                            and "#" in str(self.conn_schema_registry_secure)
                                        )
                                    )
                                )
                                and ((()) or (()))
                            )
                        )
                        or (

                                ((()) or (()))
                                and (
                                    ((self.conn_schema_registry_secure == "ssl"))
                                    or (

                                            self.conn_schema_registry_secure
                                            and "#" in str(self.conn_schema_registry_secure)

                                    )
                                )
                                and ((()) or (()))

                        )
                    )

            )
            else exclude.add("conn_registry_keystore_location")
        )
        (
            include.add("conn_registry_password")
            if (

                    (
                        ((self.conn_schema_registry_authentication == "user_credentials"))
                        or (
                            (
                                self.conn_schema_registry_authentication
                                and "#" in str(self.conn_schema_registry_authentication)
                            )
                        )
                    )
                    and ((()) or (()))
                    and (not self.defer_credentials)
                    and (())

            )
            else exclude.add("conn_registry_password")
        )
        (
            include.add("conn_registry_keytab")
            if (

                    (())
                    and (
                        (
                            (
                                (
                                    ((self.conn_schema_registry_secure == "kerberos"))
                                    or (
                                        (
                                            self.conn_schema_registry_secure
                                            and "#" in str(self.conn_schema_registry_secure)
                                        )
                                    )
                                )
                                and ((()) or (()))
                                and ((not self.defer_credentials))
                            )
                        )
                        or (

                                (
                                    ((self.conn_schema_registry_secure == "kerberos"))
                                    or (
                                        (
                                            self.conn_schema_registry_secure
                                            and "#" in str(self.conn_schema_registry_secure)
                                        )
                                    )
                                )
                                and ((()) or (()))
                                and ((()) or (()))
                                and (not self.defer_credentials)

                        )
                    )

            )
            else exclude.add("conn_registry_keytab")
        )
        (
            include.add("conn_registry_principal_name")
            if (

                    (
                        ((self.conn_schema_registry_secure == "kerberos"))
                        or ((self.conn_schema_registry_secure and "#" in str(self.conn_schema_registry_secure)))
                    )
                    and ((()) or (()))
                    and (not self.defer_credentials)
                    and (())

            )
            else exclude.add("conn_registry_principal_name")
        )
        (
            include.add("conn_registry_key_chain_pem")
            if (

                    (
                        ((self.conn_schema_registry_secure == "ssl"))
                        or ((self.conn_schema_registry_secure and "#" in str(self.conn_schema_registry_secure)))
                    )
                    and ((()) or (()))
                    and (not self.defer_credentials)
                    and (())

            )
            else exclude.add("conn_registry_key_chain_pem")
        )
        (
            include.add("conn_registry_keystore_password")
            if (

                    (())
                    and (
                        (
                            (
                                ((()) or (()))
                                and (
                                    ((self.conn_schema_registry_secure == "ssl"))
                                    or (
                                        (
                                            self.conn_schema_registry_secure
                                            and "#" in str(self.conn_schema_registry_secure)
                                        )
                                    )
                                )
                                and ((()) or (()))
                            )
                        )
                        or (

                                ((()) or (()))
                                and (
                                    ((self.conn_schema_registry_secure == "ssl"))
                                    or (

                                            self.conn_schema_registry_secure
                                            and "#" in str(self.conn_schema_registry_secure)

                                    )
                                )
                                and ((()) or (()))

                        )
                    )

            )
            else exclude.add("conn_registry_keystore_password")
        )
        include.add("schema_registry_url") if ((()) and ((()) or (()))) else exclude.add("schema_registry_url")
        (
            include.add("conn_registry_username")
            if (

                    (
                        ((self.conn_schema_registry_authentication == "user_credentials"))
                        or (
                            (
                                self.conn_schema_registry_authentication
                                and "#" in str(self.conn_schema_registry_authentication)
                            )
                        )
                    )
                    and ((()) or (()))
                    and (not self.defer_credentials)
                    and (())

            )
            else exclude.add("conn_registry_username")
        )
        (
            include.add("conn_registry_truststore_pem")
            if (

                    (
                        ((self.conn_schema_registry_secure == "kerberos"))
                        or ((self.conn_schema_registry_secure == "ssl"))
                        or ((self.conn_schema_registry_secure and "#" in str(self.conn_schema_registry_secure)))
                    )
                    and ((()) or (()))
                    and (not self.defer_credentials)
                    and (())

            )
            else exclude.add("conn_registry_truststore_pem")
        )
        (
            include.add("conn_schema_registry_secure")
            if ((()) and (((((()) or (())))) or ((()) or (()))))
            else exclude.add("conn_schema_registry_secure")
        )
        (
            include.add("conn_registry_key_password")
            if (

                    (
                        ((self.conn_schema_registry_secure == "ssl"))
                        or ((self.conn_schema_registry_secure and "#" in str(self.conn_schema_registry_secure)))
                    )
                    and ((()) or (()))
                    and (not self.defer_credentials)
                    and (())

            )
            else exclude.add("conn_registry_key_password")
        )
        include.add("schema_registry_url") if (()) else exclude.add("schema_registry_url")
        (
            include.add("conn_schema_registry_authentication")
            if (())
            else exclude.add("conn_schema_registry_authentication")
        )
        include.add("conn_registry_username") if (()) else exclude.add("conn_registry_username")
        include.add("conn_registry_password") if (()) else exclude.add("conn_registry_password")
        include.add("conn_schema_registry_secure") if (()) else exclude.add("conn_schema_registry_secure")
        include.add("conn_registry_principal_name") if (()) else exclude.add("conn_registry_principal_name")
        include.add("conn_registry_keytab") if (()) else exclude.add("conn_registry_keytab")
        include.add("conn_registry_truststore_pem") if (()) else exclude.add("conn_registry_truststore_pem")
        include.add("conn_registry_key_pem") if (()) else exclude.add("conn_registry_key_pem")
        include.add("conn_registry_key_chain_pem") if (()) else exclude.add("conn_registry_key_chain_pem")
        include.add("conn_registry_key_password") if (()) else exclude.add("conn_registry_key_password")
        include.add("conn_registry_keystore_location") if (()) else exclude.add("conn_registry_keystore_location")
        include.add("conn_registry_keystore_password") if (()) else exclude.add("conn_registry_keystore_password")
        include.add("defer_credentials") if (()) else exclude.add("defer_credentials")
        (
            include.add("end_of_data")
            if (self.end_of_wave and "true" in str(self.end_of_wave))
            else exclude.add("end_of_data")
        )
        (
            include.add("ds_client_logging_level")
            if (self.ds_advanced_client_logging and "true" in str(self.ds_advanced_client_logging))
            else exclude.add("ds_client_logging_level")
        )
        (
            include.add("ds_value_serializer_type")
            if (
                self.ds_key_serializer_type
                and "avro" in str(self.ds_key_serializer_type)
                and self.ds_key_serializer_type
                and "avro_to_json" in str(self.ds_key_serializer_type)
            )
            else exclude.add("ds_value_serializer_type")
        )
        (
            include.add("kafka_warning_and_error_logs")
            if (
                self.kafka_client_logging_level
                and (
                    (
                        hasattr(self.kafka_client_logging_level, "value")
                        and self.kafka_client_logging_level.value
                        and "debug" in str(self.kafka_client_logging_level.value)
                    )
                    or ("debug" in str(self.kafka_client_logging_level))
                )
                or self.kafka_client_logging_level
                and (
                    (
                        hasattr(self.kafka_client_logging_level, "value")
                        and self.kafka_client_logging_level.value
                        and "error" in str(self.kafka_client_logging_level.value)
                    )
                    or ("error" in str(self.kafka_client_logging_level))
                )
                or self.kafka_client_logging_level
                and (
                    (
                        hasattr(self.kafka_client_logging_level, "value")
                        and self.kafka_client_logging_level.value
                        and "fatal" in str(self.kafka_client_logging_level.value)
                    )
                    or ("fatal" in str(self.kafka_client_logging_level))
                )
                or self.kafka_client_logging_level
                and (
                    (
                        hasattr(self.kafka_client_logging_level, "value")
                        and self.kafka_client_logging_level.value
                        and "info" in str(self.kafka_client_logging_level.value)
                    )
                    or ("info" in str(self.kafka_client_logging_level))
                )
                or self.kafka_client_logging_level
                and (
                    (
                        hasattr(self.kafka_client_logging_level, "value")
                        and self.kafka_client_logging_level.value
                        and "trace" in str(self.kafka_client_logging_level.value)
                    )
                    or ("trace" in str(self.kafka_client_logging_level))
                )
                or self.kafka_client_logging_level
                and (
                    (
                        hasattr(self.kafka_client_logging_level, "value")
                        and self.kafka_client_logging_level.value
                        and "warn" in str(self.kafka_client_logging_level.value)
                    )
                    or ("warn" in str(self.kafka_client_logging_level))
                )
            )
            else exclude.add("kafka_warning_and_error_logs")
        )
        include.add("time_interval") if (self.record_count == "0") else exclude.add("time_interval")
        (
            include.add("value_serializer")
            if (
                self.key_serializer
                and (
                    (
                        hasattr(self.key_serializer, "value")
                        and self.key_serializer.value
                        and "avro" in str(self.key_serializer.value)
                    )
                    or ("avro" in str(self.key_serializer))
                )
                and self.key_serializer
                and (
                    (
                        hasattr(self.key_serializer, "value")
                        and self.key_serializer.value
                        and "avro_to_json" in str(self.key_serializer.value)
                    )
                    or ("avro_to_json" in str(self.key_serializer))
                )
            )
            else exclude.add("value_serializer")
        )
        (
            include.add("ds_warn_and_error_log")
            if (self.ds_advanced_client_logging and "true" in str(self.ds_advanced_client_logging))
            and (
                self.ds_client_logging_level
                and "debug" in str(self.ds_client_logging_level)
                and self.ds_client_logging_level
                and "error" in str(self.ds_client_logging_level)
                and self.ds_client_logging_level
                and "fatal" in str(self.ds_client_logging_level)
                and self.ds_client_logging_level
                and "info" in str(self.ds_client_logging_level)
                and self.ds_client_logging_level
                and "trace" in str(self.ds_client_logging_level)
                and self.ds_client_logging_level
                and "warn" in str(self.ds_client_logging_level)
            )
            else exclude.add("ds_warn_and_error_log")
        )
        (
            include.add("ds_kafka_config_options")
            if (self.ds_advanced_kafka_config_options and "true" in str(self.ds_advanced_kafka_config_options))
            else exclude.add("ds_kafka_config_options")
        )
        (
            include.add("stop_message_pattern")
            if (self.continuous_mode and "true" in str(self.continuous_mode))
            else exclude.add("stop_message_pattern")
        )
        (
            include.add("job_timeout_in_seconds")
            if (self.continuous_mode and "false" in str(self.continuous_mode))
            else exclude.add("job_timeout_in_seconds")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "advanced_kafka_config_options",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "conn_registry_key_chain_pem",
            "conn_registry_key_password",
            "conn_registry_key_pem",
            "conn_registry_keystore_location",
            "conn_registry_keystore_password",
            "conn_registry_keytab",
            "conn_registry_password",
            "conn_registry_principal_name",
            "conn_registry_truststore_pem",
            "conn_registry_username",
            "conn_schema_registry_authentication",
            "conn_schema_registry_secure",
            "consumer_group",
            "continuous_mode",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_advanced_client_logging",
            "ds_advanced_kafka_config_options",
            "ds_client_logging_level",
            "ds_consumer_group_name",
            "ds_isolation_level",
            "ds_java_heap_size",
            "ds_kafka_config_options",
            "ds_key_serializer_type",
            "ds_max_messages",
            "ds_max_poll_records",
            "ds_reset_policy",
            "ds_start_offset",
            "ds_stop_message",
            "ds_timeout",
            "ds_timeout_after_last_message",
            "ds_use_datastage",
            "ds_value_serializer_type",
            "ds_warn_and_error_log",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "end_of_data",
            "end_of_wave",
            "execution_mode",
            "flow_dirty",
            "generate_unicode_type_columns",
            "heap_size",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "isolation_level",
            "job_timeout_in_seconds",
            "kafka_client_logging_level",
            "kafka_config_options",
            "kafka_start_offset",
            "kafka_warning_and_error_logs",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_serializer",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "messages_read_within_single_request",
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
            "record_count",
            "registry_trust_location",
            "registry_trust_password",
            "reset_policy",
            "row_limit",
            "runtime_column_propagation",
            "schema_registry_url",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "stop_message_pattern",
            "time_interval",
            "topic_name",
            "total_number_of_messages",
            "unique",
            "value_serializer",
        }
        required = {
            "consumer_group",
            "current_output_link_type",
            "ds_consumer_group_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "kafka_server_host_name",
            "output_acp_should_hide",
            "topic_name",
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
            "advanced_kafka_config_options",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "conn_registry_key_chain_pem",
            "conn_registry_key_password",
            "conn_registry_key_pem",
            "conn_registry_keystore_location",
            "conn_registry_keystore_password",
            "conn_registry_keytab",
            "conn_registry_password",
            "conn_registry_principal_name",
            "conn_registry_truststore_pem",
            "conn_registry_username",
            "conn_schema_registry_authentication",
            "conn_schema_registry_secure",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_advanced_client_logging",
            "ds_advanced_kafka_config_options",
            "ds_client_logging_level",
            "ds_java_heap_size",
            "ds_kafka_config_options",
            "ds_key_serializer_type",
            "ds_use_datastage",
            "ds_value_serializer_type",
            "ds_warn_and_error_log",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execution_mode",
            "flow_dirty",
            "heap_size",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "kafka_client_logging_level",
            "kafka_config_options",
            "kafka_warning_and_error_logs",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_serializer",
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
            "registry_trust_location",
            "registry_trust_password",
            "runtime_column_propagation",
            "schema_registry_url",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "topic_name",
            "unique",
            "value_serializer",
        }
        required = {
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "kafka_server_host_name",
            "output_acp_should_hide",
            "topic_name",
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
                "active": 1,
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
