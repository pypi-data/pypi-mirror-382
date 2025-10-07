import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.ibm_mq_connection import IbmMqConn
from ibm_watsonx_data_integration.services.datastage.models.enums import IBM_MQ
from pydantic import Field
from typing import ClassVar


class ibm_mq(BaseStage):

    op_name: ClassVar[str] = "WebSphereMQConnectorPX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/alternateCanvasSVG/WebSphereMQConnectorPX_Alt.svg"
    label: ClassVar[str] = "IBM MQ"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: IbmMqConn = IbmMqConn()
    access_mode: IBM_MQ.AccessMode | None = Field(IBM_MQ.AccessMode.as_in_queue_definition, alias="access_mode")
    alternate_user_id: str | None = Field(None, alias="other_queue_settings.alternate_user_id")
    append_node_number: bool | None = Field(True, alias="work_queue.append_node_number")
    binding_mode: IBM_MQ.OtherQueueSettingsClusterQueueBindingMode | None = Field(
        IBM_MQ.OtherQueueSettingsClusterQueueBindingMode.as_in_queue_definition,
        alias="other_queue_settings.cluster_queue.binding_mode",
    )
    blocking_transaction_processing: bool | None = Field(False, alias="transaction.end_of_day")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: IBM_MQ.BufModeRonly | None = Field(IBM_MQ.BufModeRonly.default, alias="buf_mode_ronly")
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: IBM_MQ.BufferingMode | None = Field(IBM_MQ.BufferingMode.default, alias="buf_mode")
    cipher_spec: str | None = Field("ECDHE_RSA_AES_128_CBC_SHA256", alias="ssl_cipher_spec")
    cluster_queue: bool | None = Field(False, alias="other_queue_settings.cluster_queue")
    cluster_queue_manager_name: str | None = Field(
        None, alias="other_queue_settings.cluster_queue.queue_manager_name"
    )
    collecting: IBM_MQ.Collecting | None = Field(IBM_MQ.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: IBM_MQ.CombinabilityMode | None = Field(IBM_MQ.CombinabilityMode.auto, alias="combinability")
    content_filter: str | None = Field(None, alias="pub_sub.content_filter")
    context_mode: IBM_MQ.ContextMode | None = Field(IBM_MQ.ContextMode.none, alias="context_mode")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    custom_value: str | None = Field(None, alias="pub_sub.publish.publication_format.custom_value")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    deregistration: bool | None = Field(False, alias="pub_sub.deregistration")
    deregistration_correlation_id: str | None = Field(None, alias="pub_sub.deregistration.deregistration_correl_id")
    deregistration_topic: str | None = Field(None, alias="pub_sub.deregistration.deregistration_topic")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    dynamic_queue_name: str = Field("*", alias="other_queue_settings.dynamic_queue.name")
    dynamic_reply_queue: bool | None = Field(False, alias="pub_sub.pub_sub_dynamic_reply_to_queue")
    dynamic_reply_queue_close_options: IBM_MQ.OtherQueueSettingsDynamicQueueCloseOptions | None = Field(
        IBM_MQ.OtherQueueSettingsDynamicQueueCloseOptions.none, alias="other_queue_settings.dynamic_queue.close_options"
    )
    dynamic_reply_queue_name: str = Field("*", alias="pub_sub.pub_sub_dynamic_reply_to_queue.name")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_payload_reference: bool | None = Field(False, alias="message_options.pass_by_reference")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    end_of_data: bool | None = Field(True, alias="transaction.end_of_wave.end_of_data")
    end_of_data_message_type: int | None = Field(None, alias="end_of_data_message_type")
    end_of_wave: IBM_MQ.TransactionEndOfWave | None = Field(
        IBM_MQ.TransactionEndOfWave.none, alias="transaction.end_of_wave"
    )
    error_queue: bool | None = Field(False, alias="error_queue")
    error_queue_context_mode: IBM_MQ.ErrorQueueContextMode | None = Field(
        IBM_MQ.ErrorQueueContextMode.none, alias="error_queue.context_mode"
    )
    error_queue_name: str = Field(None, alias="error_queue.name")
    error_queue_queue_manager_name: str | None = Field("", alias="error_queue.queue_manager_name")
    execution_mode: IBM_MQ.ExecutionMode | None = Field(IBM_MQ.ExecutionMode.default_par, alias="execmode")
    extract_key: bool | None = Field(False, alias="message_options.extract_key")
    extract_key_length: int = Field(0, alias="message_options.extract_key.key_length")
    extract_key_offset: int = Field(0, alias="message_options.extract_key.key_offset")
    filter_acceptable_value_correlation_id: str | None = Field(None, alias="header_fields_filter.correl_id.value")
    filter_confirm_on_arrival: IBM_MQ.HeaderFieldsFilterReportValue | None = Field(
        None, alias="header_fields_filter.report.value"
    )
    filter_correlation_id_is_hex: bool | None = Field(False, alias="header_fields_filter.correl_id.hex")
    filter_group_id_is_hex: bool | None = Field(False, alias="header_fields_filter.group_id.hex")
    filter_group_id_use_wildcard: bool | None = Field(False, alias="header_fields_filter.group_id.use_wildcard")
    filter_match_all_report: bool | None = Field(False, alias="header_fields_filter.report.must_match_all")
    filter_message_flags_must_match_all: bool | None = Field(
        False, alias="header_fields_filter.msg_flags.must_match_all"
    )
    filter_message_id_is_hex: bool | None = Field(False, alias="header_fields_filter.msg_id.hex")
    filter_messages: bool | None = Field(False, alias="header_fields_filter")
    filter_source_acceptable_application_id_data: str | None = Field(
        None, alias="header_fields_filter.appl_identity_data"
    )
    filter_source_acceptable_backout_count: str | None = Field(None, alias="header_fields_filter.backout_count")
    filter_source_acceptable_coded_character_set_identifer: str | None = Field(
        None, alias="header_fields_filter.coded_char_set_id"
    )
    filter_source_acceptable_encoding_value: str | None = Field(None, alias="header_fields_filter.encoding")
    filter_source_acceptable_expiry_interval_value: str | None = Field(None, alias="header_fields_filter.expiry")
    filter_source_acceptable_feedback_custom_value: str | None = Field(
        None, alias="header_fields_filter.feedback.custom_value"
    )
    filter_source_acceptable_feedback_system_value: IBM_MQ.HeaderFieldsFilterFeedbackSystemValue | None = Field(
        None, alias="header_fields_filter.feedback.system_value"
    )
    filter_source_acceptable_format_custom_value: str | None = Field(
        None, alias="header_fields_filter.format.custom_value"
    )
    filter_source_acceptable_format_system_value: IBM_MQ.HeaderFieldsFilterFormatSystemValue | None = Field(
        None, alias="header_fields_filter.format.system_value"
    )
    filter_source_acceptable_group_id: str | None = Field(None, alias="header_fields_filter.group_id.value")
    filter_source_acceptable_message_flag_values: IBM_MQ.HeaderFieldsFilterMsgFlagsValue | None = Field(
        None, alias="header_fields_filter.msg_flags.value"
    )
    filter_source_acceptable_message_payload_size_value: str | None = Field(
        None, alias="header_fields_filter.msg_payload_size"
    )
    filter_source_acceptable_message_sequence_number_value: str | None = Field(
        None, alias="header_fields_filter.msg_seq_number"
    )
    filter_source_acceptable_message_type_custom_value: str | None = Field(
        None, alias="header_fields_filter.msg_type.custom_value"
    )
    filter_source_acceptable_message_type_system_value: IBM_MQ.HeaderFieldsFilterMsgTypeSystemValue | None = Field(
        None, alias="header_fields_filter.msg_type.system_value"
    )
    filter_source_acceptable_offset_value: str | None = Field(None, alias="header_fields_filter.offset")
    filter_source_acceptable_original_length_value: str | None = Field(
        None, alias="header_fields_filter.original_length"
    )
    filter_source_acceptable_persistence_value: IBM_MQ.HeaderFieldsFilterPersistence | None = Field(
        None, alias="header_fields_filter.persistence"
    )
    filter_source_acceptable_priority_value: str | None = Field(None, alias="header_fields_filter.priority")
    filter_source_acceptable_put_application_name_value: str | None = Field(
        None, alias="header_fields_filter.put_appl_name"
    )
    filter_source_acceptable_put_application_type_custom_value: str | None = Field(
        None, alias="header_fields_filter.put_appl_type.custom_value"
    )
    filter_source_acceptable_put_application_type_system_value: IBM_MQ.HeaderFieldsFilterPutApplTypeSystemValue | None = Field(None, alias="header_fields_filter.put_appl_type.system_value")
    filter_source_acceptable_put_date_value: str | None = Field(None, alias="header_fields_filter.put_date")
    filter_source_acceptable_put_time_value: str | None = Field(None, alias="header_fields_filter.put_time")
    filter_source_acceptable_reply_to_queue_manager_value: str | None = Field(
        None, alias="header_fields_filter.reply_to_q_mgr"
    )
    filter_source_acceptable_reply_to_queue_value: str | None = Field(None, alias="header_fields_filter.reply_to_q")
    filter_source_acceptable_user_id_value: str | None = Field(None, alias="header_fields_filter.user_identifier")
    filter_source_accptable_accounting_token_value: str | None = Field(
        None, alias="header_fields_filter.accounting_token.value"
    )
    filter_source_application_origin_data: str | None = Field(None, alias="header_fields_filter.appl_origin_data")
    filter_treat_accounting_token_as_hex: bool | None = Field(
        False, alias="header_fields_filter.accounting_token.hex"
    )
    filter_use_wildcard_accounting_token: bool | None = Field(
        False, alias="header_fields_filter.accounting_token.use_wildcard"
    )
    filter_use_wildcard_correlation_id: bool | None = Field(
        False, alias="header_fields_filter.correl_id.use_wildcard"
    )
    filter_use_wildcard_message_id: bool | None = Field(False, alias="header_fields_filter.msg_id.use_wildcard")
    filter_use_wildcard_message_id: str | None = Field(None, alias="header_fields_filter.msg_id.value")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    hex: bool | None = Field(True, alias="other_queue_settings.alternate_security_id.hex")
    hide: bool | None = Field(False, alias="hide")
    identity_options: IBM_MQ.PubSubRegistrationSubscriberIdentity | None = Field(
        None, alias="pub_sub.registration.subscriber_identity"
    )
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    key_column: list | None = Field([], alias="record_ordering.key_column")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_depth: int = Field(None, alias="work_queue.monitor_queue_depth.max_queue_depth")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    message_coded_character_set_id: int | None = Field(
        0, alias="message_options.message_conversion.coded_char_set_id"
    )
    message_content_descriptor: bool | None = Field(False, alias="pub_sub.publish.message_content_descriptor")
    message_controlled: bool | None = Field(False, alias="transaction.message_controlled")
    message_conversion_encoding: int | None = Field(-1, alias="message_options.message_conversion.encoding")
    message_options: bool | None = Field(False, alias="message_options")
    message_order_and_assembly: IBM_MQ.MessageOptionsMessageOrderAndAssembly | None = Field(
        IBM_MQ.MessageOptionsMessageOrderAndAssembly.individual_ordered,
        alias="message_options.message_order_and_assembly",
    )
    message_publication_options: IBM_MQ.PubSubPublishPublication | None = Field(
        None, alias="pub_sub.publish.publication"
    )
    message_quantity: int | None = Field(-1, alias="message_quantity")
    message_read_mode: IBM_MQ.MessageReadMode | None = Field(
        IBM_MQ.MessageReadMode.delete_under_transaction, alias="message_read_mode"
    )
    message_service_domain: IBM_MQ.PubSubPublishMessageContentDescriptorMessageServiceDomain = Field(
        IBM_MQ.PubSubPublishMessageContentDescriptorMessageServiceDomain.mrm,
        alias="pub_sub.publish.message_content_descriptor.message_service_domain",
    )
    message_set: str | None = Field("", alias="pub_sub.publish.message_content_descriptor.message_set")
    message_type: str | None = Field("", alias="pub_sub.publish.message_content_descriptor.message_type")
    message_write_mode: IBM_MQ.MessageWriteMode | None = Field(
        IBM_MQ.MessageWriteMode.create_under_transaction, alias="message_write_mode"
    )
    minimum_depth: int = Field(None, alias="work_queue.monitor_queue_depth.min_queue_depth")
    monitor_queue_depth: bool | None = Field(False, alias="work_queue.monitor_queue_depth")
    name: str = Field(None, alias="work_queue.name")
    open_as_dynamic_queue: bool | None = Field(False, alias="other_queue_settings.dynamic_queue")
    other_queue_settings: bool | None = Field(False, alias="other_queue_settings")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(1, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field(None, alias="outputcolProperties")
    pad_message_payload: bool | None = Field(False, alias="message_options.message_padding")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    partition_type: IBM_MQ.PartitionType | None = Field(IBM_MQ.PartitionType.auto, alias="part_type")
    peform_message_conversion: bool | None = Field(False, alias="message_options.message_conversion")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    period: int | None = Field(-1, alias="refresh.period")
    persistence_options: IBM_MQ.PubSubRegistrationSubscriberPersistence | None = Field(
        IBM_MQ.PubSubRegistrationSubscriberPersistence.persistent_as_publish,
        alias="pub_sub.registration.subscriber_persistence",
    )
    physical_format: str | None = Field("", alias="pub_sub.publish.message_content_descriptor.mrm_physical_format")
    preserve_partitioning: IBM_MQ.PreservePartitioning | None = Field(
        IBM_MQ.PreservePartitioning.default_propagate, alias="preserve"
    )
    process_end_of_data_message: bool | None = Field(
        True, alias="end_of_data_message_type.process_end_of_data_message"
    )
    publication_message_topic: str | None = Field(None, alias="pub_sub.publish.publish_topic")
    publish_subscribe: bool | None = Field(False, alias="pub_sub")
    publisher_general_deregistration_options: IBM_MQ.PubSubDeregistrationPublisher | None = Field(
        None, alias="pub_sub.deregistration.publisher"
    )
    publisher_general_registration_options: IBM_MQ.PubSubRegistrationPublisher | None = Field(
        None, alias="pub_sub.registration.publisher"
    )
    queue_name: str | None = Field("", alias="queue_name")
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    record_count: int | None = Field(0, alias="transaction.record_count")
    record_ordering: IBM_MQ.RecordOrdering | None = Field(IBM_MQ.RecordOrdering.zero, alias="record_ordering")
    refresh: bool | None = Field(False, alias="refresh")
    registration: bool | None = Field(False, alias="pub_sub.registration")
    registration_correlation_id: str | None = Field(None, alias="pub_sub.registration.registration_correl_id")
    registration_options: IBM_MQ.PubSubPublishRegistration | None = Field(None, alias="pub_sub.publish.registration")
    registration_topics: str = Field(None, alias="pub_sub.registration.registration_topic")
    reject_condition_row_not_updated: bool | None = Field(False, alias="reject_condition_row_not_updated")
    reject_condition_sql_error: bool | None = Field(False, alias="reject_condition_sql_error")
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_from_link: int | None = Field(None, alias="reject_from_link")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: IBM_MQ.RejectUses | None = Field(IBM_MQ.RejectUses.rows, alias="reject_uses")
    remote_transmission_queue_name: str | None = Field(None, alias="other_queue_settings.transmission_queue_name")
    remove_mqrfh2_header: bool | None = Field(False, alias="message_options.remove_mqrfh2header")
    reply_queue: str | None = Field(None, alias="pub_sub.pub_sub_reply_to_queue")
    row_buffer_count: int | None = Field(1, alias="message_options.row_buffer_count")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    seperate_message_into_segments: bool | None = Field(False, alias="message_options.create_segmented_message")
    service_type: IBM_MQ.PubSubServiceType | None = Field(
        IBM_MQ.PubSubServiceType.mqrfh, alias="pub_sub.service_type"
    )
    set_header_fields: bool | None = Field(False, alias="header_fields_setter")
    set_message_id_to_column_value: bool | None = Field(False, alias="message_options.set_message_id_column_value")
    setter_acceptable_value_correlation_id: str | None = Field(None, alias="header_fields_setter.correl_id.value")
    setter_correlation_id_is_hex: bool | None = Field(False, alias="header_fields_setter.correl_id.hex")
    setter_destination_header_version: IBM_MQ.HeaderFieldsSetterVersion | None = Field(
        IBM_MQ.HeaderFieldsSetterVersion.two, alias="header_fields_setter.version"
    )
    setter_destination_message_flags: IBM_MQ.HeaderFieldsSetterMsgFlags | None = Field(
        None, alias="header_fields_setter.msg_flags"
    )
    setter_destination_report_value: IBM_MQ.HeaderFieldsSetterReport | None = Field(
        None, alias="header_fields_setter.report"
    )
    setter_group_id_is_hex: bool | None = Field(False, alias="header_fields_setter.group_id.hex")
    setter_message_id_is_hex: bool | None = Field(False, alias="header_fields_setter.msg_id.hex")
    setter_source_acceptable_application_id_data: str | None = Field(
        None, alias="header_fields_setter.appl_identity_data"
    )
    setter_source_acceptable_coded_character_set_identifer: int | None = Field(
        0, alias="header_fields_setter.coded_char_set_id"
    )
    setter_source_acceptable_encoding_value: int | None = Field(-1, alias="header_fields_setter.encoding")
    setter_source_acceptable_expiry_interval_value: int | None = Field(-1, alias="header_fields_setter.expiry")
    setter_source_acceptable_feedback_custom_value: int | None = Field(
        None, alias="header_fields_setter.feedback.custom_value"
    )
    setter_source_acceptable_feedback_system_value: IBM_MQ.HeaderFieldsSetterFeedbackSystemValue | None = Field(
        IBM_MQ.HeaderFieldsSetterFeedbackSystemValue.none, alias="header_fields_setter.feedback.system_value"
    )
    setter_source_acceptable_format_custom_value: str | None = Field(
        None, alias="header_fields_setter.format.custom_value"
    )
    setter_source_acceptable_format_system_value: IBM_MQ.HeaderFieldsSetterFormatSystemValue | None = Field(
        IBM_MQ.HeaderFieldsSetterFormatSystemValue.mqstr, alias="header_fields_setter.format.system_value"
    )
    setter_source_acceptable_group_id: str | None = Field(None, alias="header_fields_setter.group_id.value")
    setter_source_acceptable_message_sequence_number_value: int | None = Field(
        1, alias="header_fields_setter.msg_seq_number"
    )
    setter_source_acceptable_message_type_custom_value: int | None = Field(
        None, alias="header_fields_setter.msg_type.custom_value"
    )
    setter_source_acceptable_message_type_system_value: IBM_MQ.HeaderFieldsSetterMsgTypeSystemValue | None = Field(
        IBM_MQ.HeaderFieldsSetterMsgTypeSystemValue.datagram, alias="header_fields_setter.msg_type.system_value"
    )
    setter_source_acceptable_offset_value: int | None = Field(0, alias="header_fields_setter.offset")
    setter_source_acceptable_persistence_value: IBM_MQ.HeaderFieldsSetterPersistence | None = Field(
        IBM_MQ.HeaderFieldsSetterPersistence.as_in_queue_definition, alias="header_fields_setter.persistence"
    )
    setter_source_acceptable_priority_value: int | None = Field(-1, alias="header_fields_setter.priority")
    setter_source_acceptable_put_application_name_value: str | None = Field(
        None, alias="header_fields_setter.put_appl_name"
    )
    setter_source_acceptable_put_application_type_custom_value: int | None = Field(
        None, alias="header_fields_setter.put_appl_type.custom_value"
    )
    setter_source_acceptable_put_application_type_system_value: IBM_MQ.HeaderFieldsSetterPutApplTypeSystemValue | None = Field(
        IBM_MQ.HeaderFieldsSetterPutApplTypeSystemValue.nocontext,
        alias="header_fields_setter.put_appl_type.system_value",
    )
    setter_source_acceptable_put_date_value: str | None = Field(None, alias="header_fields_setter.put_date")
    setter_source_acceptable_put_time_value: str | None = Field(None, alias="header_fields_setter.put_time")
    setter_source_acceptable_reply_to_queue_manager_value: str | None = Field(
        None, alias="header_fields_setter.reply_to_q_mgr"
    )
    setter_source_acceptable_reply_to_queue_value: str | None = Field(None, alias="header_fields_setter.reply_to_q")
    setter_source_acceptable_user_id_value: str | None = Field(None, alias="header_fields_setter.user_identifier")
    setter_source_accptable_accounting_token_value: str | None = Field(
        None, alias="header_fields_setter.accounting_token.value"
    )
    setter_source_application_origin_data: str | None = Field(None, alias="header_fields_setter.appl_origin_data")
    setter_treat_accounting_token_as_hex: bool | None = Field(
        False, alias="header_fields_setter.accounting_token.hex"
    )
    setter_use_wildcard_message_id: str | None = Field(None, alias="header_fields_setter.msg_id.value")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    size_of_message_segments: int = Field(1024, alias="message_options.create_segmented_message.segment_size")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: IBM_MQ.KeyColSelect | None = Field(IBM_MQ.KeyColSelect.default, alias="keyColSelect")
    sql_select_statement: str | None = Field(None, alias="sql.select_statement")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    start_value: int | None = Field(1, alias="pub_sub.publish.msg_seq_number.start_value")
    stream_name: str | None = Field("SYSTEM.BROKER.DEFAULT.STREAM", alias="pub_sub.stream_name")
    subscriber_general_deregistration_options: IBM_MQ.PubSubDeregistrationSubscriber | None = Field(
        None, alias="pub_sub.deregistration.subscriber"
    )
    subscriber_general_registration_options: IBM_MQ.PubSubRegistrationSubscriberGeneral | None = Field(
        None, alias="pub_sub.registration.subscriber_general"
    )
    subscription_identity: str | None = Field(None, alias="pub_sub.sub_identity")
    subscription_name: str | None = Field(None, alias="pub_sub.sub_name")
    subscription_point: str | None = Field(None, alias="pub_sub.sub_point")
    system_value: IBM_MQ.PubSubPublishPublicationFormatSystemValue | None = Field(
        IBM_MQ.PubSubPublishPublicationFormatSystemValue.mqstr, alias="pub_sub.publish.publication_format.system_value"
    )
    time_interval: int | None = Field(0, alias="transaction.time_interval")
    timeout: int | None = Field(-1, alias="transaction.end_of_day.timeout")
    timestamp: bool | None = Field(False, alias="pub_sub.publish.timestamp")
    transaction_end_of_day_method_name: str = Field("", alias="transaction.end_of_day.method_name")
    transaction_end_of_day_module_name: str = Field("", alias="transaction.end_of_day.module_name")
    transaction_message_controlled_method_name: str = Field("", alias="transaction.message_controlled.method_name")
    transaction_message_controlled_module_name: str = Field("", alias="transaction.message_controlled.module_name")
    transmission_queue: str | None = Field(None, alias="error_queue.tranmission_queue_name")
    treat_eol_as_row_terminator: bool | None = Field(False, alias="message_options.treat_eol_as_row_terminator")
    truncate_message: bool | None = Field(True, alias="message_options.message_truncation")
    unique: bool | None = Field(None, alias="part_unique")
    update_message_sequence_number: bool | None = Field(False, alias="pub_sub.publish.msg_seq_number")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    value: str | None = Field(None, alias="other_queue_settings.alternate_security_id.value")
    wait_time: int | None = Field(-1, alias="wait_time")
    work_queue_context_mode: IBM_MQ.WorkQueueContextMode | None = Field(
        IBM_MQ.WorkQueueContextMode.set_all, alias="work_queue.context_mode"
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
            include.add("blocking_transaction_processing")
            if (


                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value == "move_to_work_queue"
                            )
                            or (self.message_read_mode == "move_to_work_queue")
                        )


            )
            else exclude.add("blocking_transaction_processing")
        )
        (
            include.add("error_queue")
            if (


                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value == "delete_under_transaction"
                            )
                            or (self.message_read_mode == "delete_under_transaction")
                        )


            )
            else exclude.add("error_queue")
        )
        (
            include.add("filter_acceptable_value_correlation_id")
            if (self.filter_messages)
            else exclude.add("filter_acceptable_value_correlation_id")
        )
        include.add("value") if (self.other_queue_settings) else exclude.add("value")
        (
            include.add("registration_topics")
            if (((self.publish_subscribe)) and (self.registration))
            else exclude.add("registration_topics")
        )
        (
            include.add("transaction_end_of_day_module_name")
            if (self.blocking_transaction_processing)
            else exclude.add("transaction_end_of_day_module_name")
        )
        (
            include.add("registration_correlation_id")
            if (((self.publish_subscribe)) and (self.registration))
            else exclude.add("registration_correlation_id")
        )
        (
            include.add("filter_source_acceptable_priority_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_priority_value")
        )
        (
            include.add("maximum_depth")
            if (
                (
                    (
                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value == "move_to_work_queue"
                            )
                            or (self.message_read_mode == "move_to_work_queue")
                        )
                    )
                )
                and (self.monitor_queue_depth)
            )
            else exclude.add("maximum_depth")
        )
        include.add("timeout") if (self.blocking_transaction_processing) else exclude.add("timeout")
        include.add("transmission_queue") if (self.error_queue) else exclude.add("transmission_queue")
        (
            include.add("minimum_depth")
            if (
                (
                    (
                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value == "move_to_work_queue"
                            )
                            or (self.message_read_mode == "move_to_work_queue")
                        )
                    )
                )
                and (self.monitor_queue_depth)
            )
            else exclude.add("minimum_depth")
        )
        include.add("extract_key") if (self.message_options) else exclude.add("extract_key")
        (
            include.add("monitor_queue_depth")
            if (


                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value == "move_to_work_queue"
                            )
                            or (self.message_read_mode == "move_to_work_queue")
                        )


            )
            else exclude.add("monitor_queue_depth")
        )
        include.add("hex") if (self.other_queue_settings) else exclude.add("hex")
        (
            include.add("filter_source_acceptable_message_payload_size_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_message_payload_size_value")
        )
        (
            include.add("filter_correlation_id_is_hex")
            if (self.filter_messages)
            else exclude.add("filter_correlation_id_is_hex")
        )
        (
            include.add("message_coded_character_set_id")
            if (((self.message_options)) and (self.peform_message_conversion))
            else exclude.add("message_coded_character_set_id")
        )
        (
            include.add("stream_name")
            if (((self.publish_subscribe)) and (self.service_type == "mqrfh"))
            else exclude.add("stream_name")
        )
        (
            include.add("content_filter")
            if (((self.publish_subscribe)) and (self.service_type == "mqrfh2"))
            else exclude.add("content_filter")
        )
        (
            include.add("append_node_number")
            if (


                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value == "move_to_work_queue"
                            )
                            or (self.message_read_mode == "move_to_work_queue")
                        )


            )
            else exclude.add("append_node_number")
        )
        (
            include.add("transaction_message_controlled_module_name")
            if (self.message_controlled)
            else exclude.add("transaction_message_controlled_module_name")
        )
        (
            include.add("filter_source_acceptable_offset_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_offset_value")
        )
        (
            include.add("filter_source_acceptable_coded_character_set_identifer")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_coded_character_set_identifer")
        )
        (
            include.add("work_queue_context_mode")
            if (


                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value == "move_to_work_queue"
                            )
                            or (self.message_read_mode == "move_to_work_queue")
                        )


            )
            else exclude.add("work_queue_context_mode")
        )
        (
            include.add("dynamic_reply_queue_name")
            if (((self.publish_subscribe)) and (self.dynamic_reply_queue))
            else exclude.add("dynamic_reply_queue_name")
        )
        (
            include.add("subscriber_general_registration_options")
            if (((self.publish_subscribe)) and (self.registration))
            else exclude.add("subscriber_general_registration_options")
        )
        (
            include.add("filter_source_acceptable_reply_to_queue_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_reply_to_queue_value")
        )
        (
            include.add("remove_mqrfh2_header")
            if (self.message_options)
            else exclude.add("remove_mqrfh2_header")
        )
        (
            include.add("filter_source_acceptable_application_id_data")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_application_id_data")
        )
        include.add("service_type") if (self.publish_subscribe) else exclude.add("service_type")
        (
            include.add("filter_group_id_use_wildcard")
            if (((self.filter_messages)) and (not self.filter_group_id_is_hex))
            else exclude.add("filter_group_id_use_wildcard")
        )
        (
            include.add("filter_source_acceptable_feedback_custom_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_feedback_custom_value")
        )
        include.add("pad_message_payload") if (self.message_options) else exclude.add("pad_message_payload")
        (
            include.add("filter_source_acceptable_encoding_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_encoding_value")
        )
        (
            include.add("filter_treat_accounting_token_as_hex")
            if (self.filter_messages)
            else exclude.add("filter_treat_accounting_token_as_hex")
        )
        (
            include.add("subscription_point")
            if (((self.publish_subscribe)) and (self.service_type == "mqrfh2"))
            else exclude.add("subscription_point")
        )
        (
            include.add("filter_source_acceptable_user_id_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_user_id_value")
        )
        (
            include.add("filter_use_wildcard_message_id")
            if (((self.filter_messages)) and (not self.filter_message_id_is_hex))
            else exclude.add("filter_use_wildcard_message_id")
        )
        (
            include.add("treat_eol_as_row_terminator")
            if (self.message_options)
            else exclude.add("treat_eol_as_row_terminator")
        )
        (
            include.add("filter_match_all_report")
            if (self.filter_messages)
            else exclude.add("filter_match_all_report")
        )
        include.add("period") if (self.refresh) else exclude.add("period")
        (
            include.add("dynamic_reply_queue")
            if (((self.publish_subscribe)) and (self.service_type == "mqrfh"))
            else exclude.add("dynamic_reply_queue")
        )
        (
            include.add("extract_key_length")
            if (((self.message_options)) and (self.extract_key))
            else exclude.add("extract_key_length")
        )
        (
            include.add("identity_options")
            if (((self.publish_subscribe)) and (self.registration))
            else exclude.add("identity_options")
        )
        (
            include.add("filter_source_application_origin_data")
            if (self.filter_messages)
            else exclude.add("filter_source_application_origin_data")
        )
        (
            include.add("name")
            if (


                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value == "move_to_work_queue"
                            )
                            or (self.message_read_mode == "move_to_work_queue")
                        )


            )
            else exclude.add("name")
        )
        (
            include.add("subscription_identity")
            if (self.publish_subscribe)
            else exclude.add("subscription_identity")
        )
        (
            include.add("reply_queue")
            if (((self.publish_subscribe)) and (self.service_type == "mqrfh"))
            else exclude.add("reply_queue")
        )
        (
            include.add("extract_key_offset")
            if (((self.message_options)) and (self.extract_key))
            else exclude.add("extract_key_offset")
        )
        (
            include.add("filter_use_wildcard_accounting_token")
            if (((self.filter_messages)) and (not self.filter_treat_accounting_token_as_hex))
            else exclude.add("filter_use_wildcard_accounting_token")
        )
        (
            include.add("filter_source_acceptable_put_application_type_custom_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_put_application_type_custom_value")
        )
        (
            include.add("transaction_end_of_day_method_name")
            if (self.blocking_transaction_processing)
            else exclude.add("transaction_end_of_day_method_name")
        )
        (
            include.add("deregistration_topic")
            if (((self.publish_subscribe)) and (self.deregistration))
            else exclude.add("deregistration_topic")
        )
        (
            include.add("filter_source_acceptable_reply_to_queue_manager_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_reply_to_queue_manager_value")
        )
        (
            include.add("filter_source_acceptable_group_id")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_group_id")
        )
        (
            include.add("alternate_user_id")
            if (self.other_queue_settings)
            else exclude.add("alternate_user_id")
        )
        (
            include.add("filter_source_acceptable_feedback_system_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_feedback_system_value")
        )
        (
            include.add("error_queue_context_mode")
            if (self.error_queue)
            else exclude.add("error_queue_context_mode")
        )
        (
            include.add("filter_source_acceptable_expiry_interval_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_expiry_interval_value")
        )
        (
            include.add("filter_message_id_is_hex")
            if (self.filter_messages)
            else exclude.add("filter_message_id_is_hex")
        )
        (
            include.add("filter_group_id_is_hex")
            if (self.filter_messages)
            else exclude.add("filter_group_id_is_hex")
        )
        (
            include.add("end_of_data")
            if (((self.end_of_wave == "after")) or (self.end_of_wave == "before"))
            else exclude.add("end_of_data")
        )
        (
            include.add("filter_source_acceptable_backout_count")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_backout_count")
        )
        (
            include.add("filter_source_acceptable_message_type_system_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_message_type_system_value")
        )
        (
            include.add("error_queue_queue_manager_name")
            if (self.error_queue)
            else exclude.add("error_queue_queue_manager_name")
        )
        (
            include.add("filter_source_acceptable_format_custom_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_format_custom_value")
        )
        (
            include.add("filter_source_acceptable_put_date_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_put_date_value")
        )
        (
            include.add("filter_confirm_on_arrival")
            if (self.filter_messages)
            else exclude.add("filter_confirm_on_arrival")
        )
        (
            include.add("transaction_message_controlled_method_name")
            if (self.message_controlled)
            else exclude.add("transaction_message_controlled_method_name")
        )
        (
            include.add("message_conversion_encoding")
            if (((self.message_options)) and (self.peform_message_conversion))
            else exclude.add("message_conversion_encoding")
        )
        (
            include.add("filter_use_wildcard_message_id")
            if (self.filter_messages)
            else exclude.add("filter_use_wildcard_message_id")
        )
        (
            include.add("filter_source_acceptable_put_application_name_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_put_application_name_value")
        )
        (
            include.add("filter_source_accptable_accounting_token_value")
            if (self.filter_messages)
            else exclude.add("filter_source_accptable_accounting_token_value")
        )
        (
            include.add("filter_source_acceptable_put_application_type_system_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_put_application_type_system_value")
        )
        (
            include.add("persistence_options")
            if (((self.publish_subscribe)) and (self.registration))
            else exclude.add("persistence_options")
        )
        (
            include.add("subscriber_general_deregistration_options")
            if (((self.publish_subscribe)) and (self.deregistration))
            else exclude.add("subscriber_general_deregistration_options")
        )
        (
            include.add("deregistration_correlation_id")
            if (((self.publish_subscribe)) and (self.deregistration))
            else exclude.add("deregistration_correlation_id")
        )
        (
            include.add("filter_source_acceptable_format_system_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_format_system_value")
        )
        (
            include.add("filter_source_acceptable_message_sequence_number_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_message_sequence_number_value")
        )
        (
            include.add("deregistration")
            if (((self.publish_subscribe)) and (self.service_type == "mqrfh"))
            else exclude.add("deregistration")
        )
        (
            include.add("filter_source_acceptable_original_length_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_original_length_value")
        )
        (
            include.add("filter_use_wildcard_correlation_id")
            if (((self.filter_messages)) and (not self.filter_correlation_id_is_hex))
            else exclude.add("filter_use_wildcard_correlation_id")
        )
        include.add("error_queue_name") if (self.error_queue) else exclude.add("error_queue_name")
        (
            include.add("filter_source_acceptable_message_flag_values")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_message_flag_values")
        )
        (
            include.add("registration")
            if (((self.publish_subscribe)) and (self.service_type == "mqrfh"))
            else exclude.add("registration")
        )
        (
            include.add("filter_source_acceptable_message_type_custom_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_message_type_custom_value")
        )
        (
            include.add("filter_message_flags_must_match_all")
            if (self.filter_messages)
            else exclude.add("filter_message_flags_must_match_all")
        )
        include.add("truncate_message") if (self.message_options) else exclude.add("truncate_message")
        include.add("subscription_name") if (self.publish_subscribe) else exclude.add("subscription_name")
        (
            include.add("filter_source_acceptable_put_time_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_put_time_value")
        )
        (
            include.add("filter_source_acceptable_persistence_value")
            if (self.filter_messages)
            else exclude.add("filter_source_acceptable_persistence_value")
        )
        (
            include.add("peform_message_conversion")
            if (self.message_options)
            else exclude.add("peform_message_conversion")
        )
        (
            include.add("message_order_and_assembly")
            if (self.message_options)
            else exclude.add("message_order_and_assembly")
        )
        (
            include.add("enable_payload_reference")
            if (
                ((self.message_options))
                and (
                    ((self.message_order_and_assembly == "assemble_logical_messages"))
                    or (self.message_order_and_assembly == "individual_ordered")
                    or (self.message_order_and_assembly == "individual_unordered")
                )
            )
            else exclude.add("enable_payload_reference")
        )
        (
            include.add("blocking_transaction_processing")
            if (
                (
                    (
                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value == "move_to_work_queue"
                            )
                            or (self.message_read_mode == "move_to_work_queue")
                        )
                    )
                )
                or (

                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value
                                and "#" in str(self.message_read_mode.value)
                            )
                            or ("#" in str(self.message_read_mode))
                        )

                )
            )
            else exclude.add("blocking_transaction_processing")
        )
        (
            include.add("error_queue")
            if (
                (
                    (
                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value == "delete_under_transaction"
                            )
                            or (self.message_read_mode == "delete_under_transaction")
                        )
                    )
                )
                or (

                        self.message_read_mode
                        and (
                            (
                                hasattr(self.message_read_mode, "value")
                                and self.message_read_mode.value
                                and "#" in str(self.message_read_mode.value)
                            )
                            or ("#" in str(self.message_read_mode))
                        )

                )
            )
            else exclude.add("error_queue")
        )
        (
            include.add("filter_acceptable_value_correlation_id")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_acceptable_value_correlation_id")
        )
        (
            include.add("value")
            if (


                        ((self.other_queue_settings))
                        or (self.other_queue_settings and "#" in str(self.other_queue_settings))


            )
            else exclude.add("value")
        )
        (
            include.add("registration_topics")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.registration)) or (self.registration and "#" in str(self.registration)))

            )
            else exclude.add("registration_topics")
        )
        (
            include.add("transaction_end_of_day_module_name")
            if (


                        ((self.blocking_transaction_processing))
                        or (self.blocking_transaction_processing and "#" in str(self.blocking_transaction_processing))


            )
            else exclude.add("transaction_end_of_day_module_name")
        )
        (
            include.add("registration_correlation_id")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.registration)) or (self.registration and "#" in str(self.registration)))

            )
            else exclude.add("registration_correlation_id")
        )
        (
            include.add("filter_source_acceptable_priority_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_priority_value")
        )
        (
            include.add("maximum_depth")
            if (

                    (
                        (
                            (
                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value == "move_to_work_queue"
                                    )
                                    or (self.message_read_mode == "move_to_work_queue")
                                )
                            )
                        )
                        or (
                            (
                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value
                                        and "#" in str(self.message_read_mode.value)
                                    )
                                    or ("#" in str(self.message_read_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.monitor_queue_depth))
                        or (self.monitor_queue_depth and "#" in str(self.monitor_queue_depth))
                    )

            )
            else exclude.add("maximum_depth")
        )
        (
            include.add("timeout")
            if (


                        ((self.blocking_transaction_processing))
                        or (self.blocking_transaction_processing and "#" in str(self.blocking_transaction_processing))


            )
            else exclude.add("timeout")
        )
        (
            include.add("transmission_queue")
            if (((self.error_queue)) or (self.error_queue and "#" in str(self.error_queue)))
            else exclude.add("transmission_queue")
        )
        (
            include.add("minimum_depth")
            if (

                    (
                        (
                            (
                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value == "move_to_work_queue"
                                    )
                                    or (self.message_read_mode == "move_to_work_queue")
                                )
                            )
                        )
                        or (
                            (
                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value
                                        and "#" in str(self.message_read_mode.value)
                                    )
                                    or ("#" in str(self.message_read_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.monitor_queue_depth))
                        or (self.monitor_queue_depth and "#" in str(self.monitor_queue_depth))
                    )

            )
            else exclude.add("minimum_depth")
        )
        (
            include.add("extract_key")
            if (((self.message_options)) or (self.message_options and "#" in str(self.message_options)))
            else exclude.add("extract_key")
        )
        (
            include.add("monitor_queue_depth")
            if (


                        (
                            (
                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value == "move_to_work_queue"
                                    )
                                    or (self.message_read_mode == "move_to_work_queue")
                                )
                            )
                        )
                        or (

                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value
                                        and "#" in str(self.message_read_mode.value)
                                    )
                                    or ("#" in str(self.message_read_mode))
                                )

                        )


            )
            else exclude.add("monitor_queue_depth")
        )
        (
            include.add("hex")
            if (


                        ((self.other_queue_settings))
                        or (self.other_queue_settings and "#" in str(self.other_queue_settings))


            )
            else exclude.add("hex")
        )
        (
            include.add("filter_source_acceptable_message_payload_size_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_message_payload_size_value")
        )
        (
            include.add("filter_correlation_id_is_hex")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_correlation_id_is_hex")
        )
        (
            include.add("message_coded_character_set_id")
            if (

                    (((self.message_options)) or ((self.message_options and "#" in str(self.message_options))))
                    and (
                        ((self.peform_message_conversion))
                        or (self.peform_message_conversion and "#" in str(self.peform_message_conversion))
                    )

            )
            else exclude.add("message_coded_character_set_id")
        )
        (
            include.add("stream_name")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.service_type == "mqrfh")) or (self.service_type and "#" in str(self.service_type)))

            )
            else exclude.add("stream_name")
        )
        (
            include.add("content_filter")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.service_type == "mqrfh2")) or (self.service_type and "#" in str(self.service_type)))

            )
            else exclude.add("content_filter")
        )
        (
            include.add("append_node_number")
            if (


                        (
                            (
                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value == "move_to_work_queue"
                                    )
                                    or (self.message_read_mode == "move_to_work_queue")
                                )
                            )
                        )
                        or (

                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value
                                        and "#" in str(self.message_read_mode.value)
                                    )
                                    or ("#" in str(self.message_read_mode))
                                )

                        )


            )
            else exclude.add("append_node_number")
        )
        (
            include.add("transaction_message_controlled_module_name")
            if (


                        ((self.message_controlled))
                        or (self.message_controlled and "#" in str(self.message_controlled))


            )
            else exclude.add("transaction_message_controlled_module_name")
        )
        (
            include.add("filter_source_acceptable_offset_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_offset_value")
        )
        (
            include.add("filter_source_acceptable_coded_character_set_identifer")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_coded_character_set_identifer")
        )
        (
            include.add("work_queue_context_mode")
            if (


                        (
                            (
                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value == "move_to_work_queue"
                                    )
                                    or (self.message_read_mode == "move_to_work_queue")
                                )
                            )
                        )
                        or (

                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value
                                        and "#" in str(self.message_read_mode.value)
                                    )
                                    or ("#" in str(self.message_read_mode))
                                )

                        )


            )
            else exclude.add("work_queue_context_mode")
        )
        (
            include.add("dynamic_reply_queue_name")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (
                        ((self.dynamic_reply_queue))
                        or (self.dynamic_reply_queue and "#" in str(self.dynamic_reply_queue))
                    )

            )
            else exclude.add("dynamic_reply_queue_name")
        )
        (
            include.add("subscriber_general_registration_options")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.registration)) or (self.registration and "#" in str(self.registration)))

            )
            else exclude.add("subscriber_general_registration_options")
        )
        (
            include.add("filter_source_acceptable_reply_to_queue_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_reply_to_queue_value")
        )
        (
            include.add("remove_mqrfh2_header")
            if (((self.message_options)) or (self.message_options and "#" in str(self.message_options)))
            else exclude.add("remove_mqrfh2_header")
        )
        (
            include.add("filter_source_acceptable_application_id_data")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_application_id_data")
        )
        (
            include.add("service_type")
            if (


                        ((self.publish_subscribe))
                        or (self.publish_subscribe and "#" in str(self.publish_subscribe))


            )
            else exclude.add("service_type")
        )
        (
            include.add("filter_group_id_use_wildcard")
            if (

                    (((self.filter_messages)) or ((self.filter_messages and "#" in str(self.filter_messages))))
                    and (
                        ((not self.filter_group_id_is_hex))
                        or (self.filter_group_id_is_hex and "#" in str(self.filter_group_id_is_hex))
                    )

            )
            else exclude.add("filter_group_id_use_wildcard")
        )
        (
            include.add("filter_source_acceptable_feedback_custom_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_feedback_custom_value")
        )
        (
            include.add("pad_message_payload")
            if (((self.message_options)) or (self.message_options and "#" in str(self.message_options)))
            else exclude.add("pad_message_payload")
        )
        (
            include.add("filter_source_acceptable_encoding_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_encoding_value")
        )
        (
            include.add("filter_treat_accounting_token_as_hex")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_treat_accounting_token_as_hex")
        )
        (
            include.add("subscription_point")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.service_type == "mqrfh2")) or (self.service_type and "#" in str(self.service_type)))

            )
            else exclude.add("subscription_point")
        )
        (
            include.add("filter_source_acceptable_user_id_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_user_id_value")
        )
        (
            include.add("filter_use_wildcard_message_id")
            if (

                    (((self.filter_messages)) or ((self.filter_messages and "#" in str(self.filter_messages))))
                    and (
                        ((not self.filter_message_id_is_hex))
                        or (self.filter_message_id_is_hex and "#" in str(self.filter_message_id_is_hex))
                    )

            )
            else exclude.add("filter_use_wildcard_message_id")
        )
        (
            include.add("treat_eol_as_row_terminator")
            if (((self.message_options)) or (self.message_options and "#" in str(self.message_options)))
            else exclude.add("treat_eol_as_row_terminator")
        )
        (
            include.add("filter_match_all_report")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_match_all_report")
        )
        (
            include.add("period")
            if (((self.refresh)) or (self.refresh and "#" in str(self.refresh)))
            else exclude.add("period")
        )
        (
            include.add("dynamic_reply_queue")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.service_type == "mqrfh")) or (self.service_type and "#" in str(self.service_type)))

            )
            else exclude.add("dynamic_reply_queue")
        )
        (
            include.add("extract_key_length")
            if (

                    (((self.message_options)) or ((self.message_options and "#" in str(self.message_options))))
                    and (((self.extract_key)) or (self.extract_key and "#" in str(self.extract_key)))

            )
            else exclude.add("extract_key_length")
        )
        (
            include.add("identity_options")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.registration)) or (self.registration and "#" in str(self.registration)))

            )
            else exclude.add("identity_options")
        )
        (
            include.add("filter_source_application_origin_data")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_application_origin_data")
        )
        (
            include.add("name")
            if (


                        (
                            (
                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value == "move_to_work_queue"
                                    )
                                    or (self.message_read_mode == "move_to_work_queue")
                                )
                            )
                        )
                        or (

                                self.message_read_mode
                                and (
                                    (
                                        hasattr(self.message_read_mode, "value")
                                        and self.message_read_mode.value
                                        and "#" in str(self.message_read_mode.value)
                                    )
                                    or ("#" in str(self.message_read_mode))
                                )

                        )


            )
            else exclude.add("name")
        )
        (
            include.add("subscription_identity")
            if (


                        ((self.publish_subscribe))
                        or (self.publish_subscribe and "#" in str(self.publish_subscribe))


            )
            else exclude.add("subscription_identity")
        )
        (
            include.add("reply_queue")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.service_type == "mqrfh")) or (self.service_type and "#" in str(self.service_type)))

            )
            else exclude.add("reply_queue")
        )
        (
            include.add("extract_key_offset")
            if (

                    (((self.message_options)) or ((self.message_options and "#" in str(self.message_options))))
                    and (((self.extract_key)) or (self.extract_key and "#" in str(self.extract_key)))

            )
            else exclude.add("extract_key_offset")
        )
        (
            include.add("filter_use_wildcard_accounting_token")
            if (

                    (((self.filter_messages)) or ((self.filter_messages and "#" in str(self.filter_messages))))
                    and (
                        ((not self.filter_treat_accounting_token_as_hex))
                        or (

                                self.filter_treat_accounting_token_as_hex
                                and "#" in str(self.filter_treat_accounting_token_as_hex)

                        )
                    )

            )
            else exclude.add("filter_use_wildcard_accounting_token")
        )
        (
            include.add("filter_source_acceptable_put_application_type_custom_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_put_application_type_custom_value")
        )
        (
            include.add("transaction_end_of_day_method_name")
            if (


                        ((self.blocking_transaction_processing))
                        or (self.blocking_transaction_processing and "#" in str(self.blocking_transaction_processing))


            )
            else exclude.add("transaction_end_of_day_method_name")
        )
        (
            include.add("deregistration_topic")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.deregistration)) or (self.deregistration and "#" in str(self.deregistration)))

            )
            else exclude.add("deregistration_topic")
        )
        (
            include.add("filter_source_acceptable_reply_to_queue_manager_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_reply_to_queue_manager_value")
        )
        (
            include.add("filter_source_acceptable_group_id")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_group_id")
        )
        (
            include.add("alternate_user_id")
            if (


                        ((self.other_queue_settings))
                        or (self.other_queue_settings and "#" in str(self.other_queue_settings))


            )
            else exclude.add("alternate_user_id")
        )
        (
            include.add("filter_source_acceptable_feedback_system_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_feedback_system_value")
        )
        (
            include.add("error_queue_context_mode")
            if (((self.error_queue)) or (self.error_queue and "#" in str(self.error_queue)))
            else exclude.add("error_queue_context_mode")
        )
        (
            include.add("filter_source_acceptable_expiry_interval_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_expiry_interval_value")
        )
        (
            include.add("filter_message_id_is_hex")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_message_id_is_hex")
        )
        (
            include.add("filter_group_id_is_hex")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_group_id_is_hex")
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
            include.add("filter_source_acceptable_backout_count")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_backout_count")
        )
        (
            include.add("filter_source_acceptable_message_type_system_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_message_type_system_value")
        )
        (
            include.add("error_queue_queue_manager_name")
            if (((self.error_queue)) or (self.error_queue and "#" in str(self.error_queue)))
            else exclude.add("error_queue_queue_manager_name")
        )
        (
            include.add("filter_source_acceptable_format_custom_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_format_custom_value")
        )
        (
            include.add("filter_source_acceptable_put_date_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_put_date_value")
        )
        (
            include.add("filter_confirm_on_arrival")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_confirm_on_arrival")
        )
        (
            include.add("transaction_message_controlled_method_name")
            if (


                        ((self.message_controlled))
                        or (self.message_controlled and "#" in str(self.message_controlled))


            )
            else exclude.add("transaction_message_controlled_method_name")
        )
        (
            include.add("message_conversion_encoding")
            if (

                    (((self.message_options)) or ((self.message_options and "#" in str(self.message_options))))
                    and (
                        ((self.peform_message_conversion))
                        or (self.peform_message_conversion and "#" in str(self.peform_message_conversion))
                    )

            )
            else exclude.add("message_conversion_encoding")
        )
        (
            include.add("filter_use_wildcard_message_id")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_use_wildcard_message_id")
        )
        (
            include.add("filter_source_acceptable_put_application_name_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_put_application_name_value")
        )
        (
            include.add("filter_source_accptable_accounting_token_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_accptable_accounting_token_value")
        )
        (
            include.add("filter_source_acceptable_put_application_type_system_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_put_application_type_system_value")
        )
        (
            include.add("persistence_options")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.registration)) or (self.registration and "#" in str(self.registration)))

            )
            else exclude.add("persistence_options")
        )
        (
            include.add("subscriber_general_deregistration_options")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.deregistration)) or (self.deregistration and "#" in str(self.deregistration)))

            )
            else exclude.add("subscriber_general_deregistration_options")
        )
        (
            include.add("deregistration_correlation_id")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.deregistration)) or (self.deregistration and "#" in str(self.deregistration)))

            )
            else exclude.add("deregistration_correlation_id")
        )
        (
            include.add("filter_source_acceptable_format_system_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_format_system_value")
        )
        (
            include.add("filter_source_acceptable_message_sequence_number_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_message_sequence_number_value")
        )
        (
            include.add("deregistration")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.service_type == "mqrfh")) or (self.service_type and "#" in str(self.service_type)))

            )
            else exclude.add("deregistration")
        )
        (
            include.add("filter_source_acceptable_original_length_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_original_length_value")
        )
        (
            include.add("filter_use_wildcard_correlation_id")
            if (

                    (((self.filter_messages)) or ((self.filter_messages and "#" in str(self.filter_messages))))
                    and (
                        ((not self.filter_correlation_id_is_hex))
                        or (self.filter_correlation_id_is_hex and "#" in str(self.filter_correlation_id_is_hex))
                    )

            )
            else exclude.add("filter_use_wildcard_correlation_id")
        )
        (
            include.add("error_queue_name")
            if (((self.error_queue)) or (self.error_queue and "#" in str(self.error_queue)))
            else exclude.add("error_queue_name")
        )
        (
            include.add("filter_source_acceptable_message_flag_values")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_message_flag_values")
        )
        (
            include.add("registration")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.service_type == "mqrfh")) or (self.service_type and "#" in str(self.service_type)))

            )
            else exclude.add("registration")
        )
        (
            include.add("filter_source_acceptable_message_type_custom_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_message_type_custom_value")
        )
        (
            include.add("filter_message_flags_must_match_all")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_message_flags_must_match_all")
        )
        (
            include.add("truncate_message")
            if (((self.message_options)) or (self.message_options and "#" in str(self.message_options)))
            else exclude.add("truncate_message")
        )
        (
            include.add("subscription_name")
            if (


                        ((self.publish_subscribe))
                        or (self.publish_subscribe and "#" in str(self.publish_subscribe))


            )
            else exclude.add("subscription_name")
        )
        (
            include.add("filter_source_acceptable_put_time_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_put_time_value")
        )
        (
            include.add("filter_source_acceptable_persistence_value")
            if (((self.filter_messages)) or (self.filter_messages and "#" in str(self.filter_messages)))
            else exclude.add("filter_source_acceptable_persistence_value")
        )
        (
            include.add("peform_message_conversion")
            if (((self.message_options)) or (self.message_options and "#" in str(self.message_options)))
            else exclude.add("peform_message_conversion")
        )
        (
            include.add("message_order_and_assembly")
            if (((self.message_options)) or (self.message_options and "#" in str(self.message_options)))
            else exclude.add("message_order_and_assembly")
        )
        (
            include.add("enable_payload_reference")
            if (

                    (((self.message_options)) or ((self.message_options and "#" in str(self.message_options))))
                    and (
                        ((self.message_order_and_assembly == "assemble_logical_messages"))
                        or (self.message_order_and_assembly == "individual_ordered")
                        or (self.message_order_and_assembly == "individual_unordered")
                        or (self.message_order_and_assembly and "#" in str(self.message_order_and_assembly))
                    )

            )
            else exclude.add("enable_payload_reference")
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
        include.add("cipher_spec") if (((()) or (())) and (())) else exclude.add("cipher_spec")
        include.add("use_cas_lite_service") if (((()) or (())) and (())) else exclude.add("use_cas_lite_service")
        include.add("use_cas_lite_service") if (()) else exclude.add("use_cas_lite_service")
        include.add("cipher_spec") if (()) else exclude.add("cipher_spec")
        include.add("defer_credentials") if (()) else exclude.add("defer_credentials")
        include.add("period") if (self.refresh == "true" or self.refresh) else exclude.add("period")
        (
            include.add("filter_use_wildcard_message_id")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_use_wildcard_message_id")
        )
        (
            include.add("subscription_identity")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            else exclude.add("subscription_identity")
        )
        (
            include.add("filter_correlation_id_is_hex")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_correlation_id_is_hex")
        )
        (
            include.add("enable_payload_reference")
            if (self.message_options == "true" or self.message_options)
            and (
                self.message_order_and_assembly
                and "assemble_logical_messages" in str(self.message_order_and_assembly)
                and self.message_order_and_assembly
                and "individual_ordered" in str(self.message_order_and_assembly)
                and self.message_order_and_assembly
                and "individual_unordered" in str(self.message_order_and_assembly)
            )
            else exclude.add("enable_payload_reference")
        )
        (
            include.add("filter_source_acceptable_group_id")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_group_id")
        )
        (
            include.add("filter_source_acceptable_reply_to_queue_manager_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_reply_to_queue_manager_value")
        )
        (
            include.add("timeout")
            if (self.blocking_transaction_processing == "true" or self.blocking_transaction_processing)
            else exclude.add("timeout")
        )
        (
            include.add("work_queue_context_mode")
            if (
                self.message_read_mode
                and (
                    (hasattr(self.message_read_mode, "value") and self.message_read_mode.value == "move_to_work_queue")
                    or (self.message_read_mode == "move_to_work_queue")
                )
            )
            else exclude.add("work_queue_context_mode")
        )
        (
            include.add("filter_source_application_origin_data")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_application_origin_data")
        )
        (
            include.add("filter_source_acceptable_offset_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_offset_value")
        )
        (
            include.add("content_filter")
            if (self.publish_subscribe == "true" or self.publish_subscribe) and (self.service_type == "mqrfh2")
            else exclude.add("content_filter")
        )
        (
            include.add("transaction_end_of_day_method_name")
            if (self.blocking_transaction_processing == "true" or self.blocking_transaction_processing)
            else exclude.add("transaction_end_of_day_method_name")
        )
        (
            include.add("filter_source_acceptable_format_system_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_format_system_value")
        )
        (
            include.add("value")
            if (self.other_queue_settings == "true" or self.other_queue_settings)
            else exclude.add("value")
        )
        (
            include.add("remove_mqrfh2_header")
            if (self.message_options == "true" or self.message_options)
            else exclude.add("remove_mqrfh2_header")
        )
        (
            include.add("filter_source_acceptable_persistence_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_persistence_value")
        )
        (
            include.add("filter_match_all_report")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_match_all_report")
        )
        (
            include.add("filter_source_acceptable_message_flag_values")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_message_flag_values")
        )
        (
            include.add("extract_key")
            if (self.message_options == "true" or self.message_options)
            else exclude.add("extract_key")
        )
        (
            include.add("filter_source_acceptable_reply_to_queue_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_reply_to_queue_value")
        )
        (
            include.add("error_queue")
            if (
                self.message_read_mode
                and (
                    (
                        hasattr(self.message_read_mode, "value")
                        and self.message_read_mode.value == "delete_under_transaction"
                    )
                    or (self.message_read_mode == "delete_under_transaction")
                )
            )
            else exclude.add("error_queue")
        )
        (
            include.add("filter_source_acceptable_put_date_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_put_date_value")
        )
        (
            include.add("filter_use_wildcard_accounting_token")
            if (self.filter_messages == "true" or self.filter_messages)
            and (
                self.filter_treat_accounting_token_as_hex == "false"
                or not self.filter_treat_accounting_token_as_hex
            )
            else exclude.add("filter_use_wildcard_accounting_token")
        )
        (
            include.add("filter_source_acceptable_encoding_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_encoding_value")
        )
        (
            include.add("filter_source_acceptable_put_application_type_system_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_put_application_type_system_value")
        )
        (
            include.add("filter_source_acceptable_user_id_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_user_id_value")
        )
        (
            include.add("append_node_number")
            if (
                self.message_read_mode
                and (
                    (hasattr(self.message_read_mode, "value") and self.message_read_mode.value == "move_to_work_queue")
                    or (self.message_read_mode == "move_to_work_queue")
                )
            )
            else exclude.add("append_node_number")
        )
        (
            include.add("stream_name")
            if (self.publish_subscribe == "true" or self.publish_subscribe) and (self.service_type == "mqrfh")
            else exclude.add("stream_name")
        )
        (
            include.add("registration_correlation_id")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.registration == "true" or self.registration)
            else exclude.add("registration_correlation_id")
        )
        (
            include.add("subscription_point")
            if (self.publish_subscribe == "true" or self.publish_subscribe) and (self.service_type == "mqrfh2")
            else exclude.add("subscription_point")
        )
        (
            include.add("name")
            if (
                self.message_read_mode
                and (
                    (hasattr(self.message_read_mode, "value") and self.message_read_mode.value == "move_to_work_queue")
                    or (self.message_read_mode == "move_to_work_queue")
                )
            )
            else exclude.add("name")
        )
        (
            include.add("service_type")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            else exclude.add("service_type")
        )
        (
            include.add("filter_source_acceptable_message_type_custom_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_message_type_custom_value")
        )
        (
            include.add("alternate_user_id")
            if (self.other_queue_settings == "true" or self.other_queue_settings)
            else exclude.add("alternate_user_id")
        )
        (
            include.add("filter_source_acceptable_feedback_custom_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_feedback_custom_value")
        )
        (
            include.add("registration")
            if (self.publish_subscribe == "true" or self.publish_subscribe) and (self.service_type == "mqrfh")
            else exclude.add("registration")
        )
        (
            include.add("subscriber_general_deregistration_options")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.deregistration == "true" or self.deregistration)
            else exclude.add("subscriber_general_deregistration_options")
        )
        (
            include.add("persistence_options")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.registration == "true" or self.registration)
            else exclude.add("persistence_options")
        )
        (
            include.add("filter_source_acceptable_original_length_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_original_length_value")
        )
        (
            include.add("error_queue_queue_manager_name")
            if (self.error_queue == "true" or self.error_queue)
            else exclude.add("error_queue_queue_manager_name")
        )
        (
            include.add("minimum_depth")
            if (
                self.message_read_mode
                and (
                    (hasattr(self.message_read_mode, "value") and self.message_read_mode.value == "move_to_work_queue")
                    or (self.message_read_mode == "move_to_work_queue")
                )
            )
            and (self.monitor_queue_depth == "true" or self.monitor_queue_depth)
            else exclude.add("minimum_depth")
        )
        (
            include.add("maximum_depth")
            if (
                self.message_read_mode
                and (
                    (hasattr(self.message_read_mode, "value") and self.message_read_mode.value == "move_to_work_queue")
                    or (self.message_read_mode == "move_to_work_queue")
                )
            )
            and (self.monitor_queue_depth == "true" or self.monitor_queue_depth)
            else exclude.add("maximum_depth")
        )
        (
            include.add("transaction_message_controlled_module_name")
            if (self.message_controlled == "true" or self.message_controlled)
            else exclude.add("transaction_message_controlled_module_name")
        )
        (
            include.add("message_order_and_assembly")
            if (self.message_options == "true" or self.message_options)
            else exclude.add("message_order_and_assembly")
        )
        (
            include.add("dynamic_reply_queue")
            if (self.publish_subscribe == "true" or self.publish_subscribe) and (self.service_type == "mqrfh")
            else exclude.add("dynamic_reply_queue")
        )
        (
            include.add("filter_source_acceptable_put_time_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_put_time_value")
        )
        (
            include.add("transaction_message_controlled_method_name")
            if (self.message_controlled == "true" or self.message_controlled)
            else exclude.add("transaction_message_controlled_method_name")
        )
        (
            include.add("hex")
            if (self.other_queue_settings == "true" or self.other_queue_settings)
            else exclude.add("hex")
        )
        (
            include.add("truncate_message")
            if (self.message_options == "true" or self.message_options)
            else exclude.add("truncate_message")
        )
        (
            include.add("subscriber_general_registration_options")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.registration == "true" or self.registration)
            else exclude.add("subscriber_general_registration_options")
        )
        (
            include.add("filter_message_id_is_hex")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_message_id_is_hex")
        )
        (
            include.add("filter_source_acceptable_format_custom_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_format_custom_value")
        )
        (
            include.add("deregistration")
            if (self.publish_subscribe == "true" or self.publish_subscribe) and (self.service_type == "mqrfh")
            else exclude.add("deregistration")
        )
        (
            include.add("deregistration_correlation_id")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.deregistration == "true" or self.deregistration)
            else exclude.add("deregistration_correlation_id")
        )
        (
            include.add("transaction_end_of_day_module_name")
            if (self.blocking_transaction_processing == "true" or self.blocking_transaction_processing)
            else exclude.add("transaction_end_of_day_module_name")
        )
        (
            include.add("filter_source_acceptable_message_sequence_number_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_message_sequence_number_value")
        )
        (
            include.add("dynamic_reply_queue_name")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.dynamic_reply_queue == "true" or self.dynamic_reply_queue)
            else exclude.add("dynamic_reply_queue_name")
        )
        (
            include.add("extract_key_offset")
            if (self.message_options == "true" or self.message_options)
            and (self.extract_key == "true" or self.extract_key)
            else exclude.add("extract_key_offset")
        )
        (
            include.add("peform_message_conversion")
            if (self.message_options == "true" or self.message_options)
            else exclude.add("peform_message_conversion")
        )
        (
            include.add("filter_source_acceptable_coded_character_set_identifer")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_coded_character_set_identifer")
        )
        (
            include.add("subscription_name")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            else exclude.add("subscription_name")
        )
        (
            include.add("filter_source_acceptable_priority_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_priority_value")
        )
        (
            include.add("registration_topics")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.registration == "true" or self.registration)
            else exclude.add("registration_topics")
        )
        (
            include.add("error_queue_name")
            if (self.error_queue == "true" or self.error_queue)
            else exclude.add("error_queue_name")
        )
        (
            include.add("filter_acceptable_value_correlation_id")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_acceptable_value_correlation_id")
        )
        (
            include.add("transmission_queue")
            if (self.error_queue == "true" or self.error_queue)
            else exclude.add("transmission_queue")
        )
        (
            include.add("reply_queue")
            if (self.publish_subscribe == "true" or self.publish_subscribe) and (self.service_type == "mqrfh")
            else exclude.add("reply_queue")
        )
        (
            include.add("filter_source_acceptable_feedback_system_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_feedback_system_value")
        )
        (
            include.add("filter_source_accptable_accounting_token_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_accptable_accounting_token_value")
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
            include.add("filter_source_acceptable_put_application_name_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_put_application_name_value")
        )
        (
            include.add("filter_source_acceptable_application_id_data")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_application_id_data")
        )
        (
            include.add("filter_group_id_is_hex")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_group_id_is_hex")
        )
        (
            include.add("message_conversion_encoding")
            if (self.message_options == "true" or self.message_options)
            and (self.peform_message_conversion == "true" or self.peform_message_conversion)
            else exclude.add("message_conversion_encoding")
        )
        (
            include.add("deregistration_topic")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.deregistration == "true" or self.deregistration)
            else exclude.add("deregistration_topic")
        )
        (
            include.add("filter_treat_accounting_token_as_hex")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_treat_accounting_token_as_hex")
        )
        (
            include.add("filter_use_wildcard_correlation_id")
            if (self.filter_messages == "true" or self.filter_messages)
            and (self.filter_correlation_id_is_hex == "false" or not self.filter_correlation_id_is_hex)
            else exclude.add("filter_use_wildcard_correlation_id")
        )
        (
            include.add("filter_source_acceptable_message_type_system_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_message_type_system_value")
        )
        (
            include.add("filter_source_acceptable_expiry_interval_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_expiry_interval_value")
        )
        (
            include.add("filter_source_acceptable_put_application_type_custom_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_put_application_type_custom_value")
        )
        (
            include.add("filter_message_flags_must_match_all")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_message_flags_must_match_all")
        )
        (
            include.add("treat_eol_as_row_terminator")
            if (self.message_options == "true" or self.message_options)
            else exclude.add("treat_eol_as_row_terminator")
        )
        (
            include.add("filter_group_id_use_wildcard")
            if (self.filter_messages == "true" or self.filter_messages)
            and (self.filter_group_id_is_hex == "false" or not self.filter_group_id_is_hex)
            else exclude.add("filter_group_id_use_wildcard")
        )
        (
            include.add("message_coded_character_set_id")
            if (self.message_options == "true" or self.message_options)
            and (self.peform_message_conversion == "true" or self.peform_message_conversion)
            else exclude.add("message_coded_character_set_id")
        )
        (
            include.add("error_queue_context_mode")
            if (self.error_queue == "true" or self.error_queue)
            else exclude.add("error_queue_context_mode")
        )
        (
            include.add("filter_source_acceptable_backout_count")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_backout_count")
        )
        (
            include.add("filter_use_wildcard_message_id")
            if (self.filter_messages == "true" or self.filter_messages)
            and (self.filter_message_id_is_hex == "false" or not self.filter_message_id_is_hex)
            else exclude.add("filter_use_wildcard_message_id")
        )
        (
            include.add("filter_source_acceptable_message_payload_size_value")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_source_acceptable_message_payload_size_value")
        )
        (
            include.add("identity_options")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.registration == "true" or self.registration)
            else exclude.add("identity_options")
        )
        (
            include.add("monitor_queue_depth")
            if (
                self.message_read_mode
                and (
                    (hasattr(self.message_read_mode, "value") and self.message_read_mode.value == "move_to_work_queue")
                    or (self.message_read_mode == "move_to_work_queue")
                )
            )
            else exclude.add("monitor_queue_depth")
        )
        (
            include.add("blocking_transaction_processing")
            if (
                self.message_read_mode
                and (
                    (hasattr(self.message_read_mode, "value") and self.message_read_mode.value == "move_to_work_queue")
                    or (self.message_read_mode == "move_to_work_queue")
                )
            )
            else exclude.add("blocking_transaction_processing")
        )
        (
            include.add("extract_key_length")
            if (self.message_options == "true" or self.message_options)
            and (self.extract_key == "true" or self.extract_key)
            else exclude.add("extract_key_length")
        )
        (
            include.add("pad_message_payload")
            if (self.message_options == "true" or self.message_options)
            else exclude.add("pad_message_payload")
        )
        (
            include.add("filter_confirm_on_arrival")
            if (self.filter_messages == "true" or self.filter_messages)
            else exclude.add("filter_confirm_on_arrival")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("publisher_general_deregistration_options")
            if (((self.publish_subscribe)) and (self.deregistration))
            else exclude.add("publisher_general_deregistration_options")
        )
        (
            include.add("setter_destination_message_flags")
            if (((self.set_header_fields)) and (self.setter_destination_header_version == "2"))
            else exclude.add("setter_destination_message_flags")
        )
        (
            include.add("setter_source_acceptable_format_custom_value")
            if (self.set_header_fields)
            else exclude.add("setter_source_acceptable_format_custom_value")
        )
        include.add("timestamp") if (self.publish_subscribe) else exclude.add("timestamp")
        (
            include.add("setter_acceptable_value_correlation_id")
            if (self.set_header_fields)
            else exclude.add("setter_acceptable_value_correlation_id")
        )
        (
            include.add("setter_source_acceptable_feedback_custom_value")
            if (self.set_header_fields)
            else exclude.add("setter_source_acceptable_feedback_custom_value")
        )
        (
            include.add("setter_source_acceptable_message_type_custom_value")
            if (self.set_header_fields)
            else exclude.add("setter_source_acceptable_message_type_custom_value")
        )
        (
            include.add("setter_source_acceptable_priority_value")
            if (self.set_header_fields)
            else exclude.add("setter_source_acceptable_priority_value")
        )
        (
            include.add("setter_use_wildcard_message_id")
            if (self.set_header_fields)
            else exclude.add("setter_use_wildcard_message_id")
        )
        (
            include.add("setter_treat_accounting_token_as_hex")
            if (
                (
                    (
                        (
                            self.context_mode
                            and (
                                (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                or (self.context_mode == "set_all")
                            )
                        )
                    )
                    or (
                        (
                            self.context_mode
                            and (
                                (hasattr(self.context_mode, "value") and self.context_mode.value == "set_identity")
                                or (self.context_mode == "set_identity")
                            )
                        )
                    )
                )
                and (self.set_header_fields)
            )
            else exclude.add("setter_treat_accounting_token_as_hex")
        )
        (
            include.add("message_type")
            if (
                ((self.publish_subscribe))
                and (self.message_content_descriptor)
                and (((self.message_service_domain == "idoc")) or (self.message_service_domain == "mrm"))
            )
            else exclude.add("message_type")
        )
        (
            include.add("open_as_dynamic_queue")
            if (self.other_queue_settings)
            else exclude.add("open_as_dynamic_queue")
        )
        (
            include.add("publication_message_topic")
            if (self.publish_subscribe)
            else exclude.add("publication_message_topic")
        )
        (
            include.add("setter_source_acceptable_application_id_data")
            if (
                (
                    (
                        (
                            self.context_mode
                            and (
                                (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                or (self.context_mode == "set_all")
                            )
                        )
                    )
                    or (
                        (
                            self.context_mode
                            and (
                                (hasattr(self.context_mode, "value") and self.context_mode.value == "set_identity")
                                or (self.context_mode == "set_identity")
                            )
                        )
                    )
                )
                and (self.set_header_fields)
            )
            else exclude.add("setter_source_acceptable_application_id_data")
        )
        (
            include.add("dynamic_reply_queue_close_options")
            if (((self.other_queue_settings)) and (self.open_as_dynamic_queue))
            else exclude.add("dynamic_reply_queue_close_options")
        )
        (
            include.add("setter_group_id_is_hex")
            if (((self.set_header_fields)) and (self.setter_destination_header_version == "2"))
            else exclude.add("setter_group_id_is_hex")
        )
        include.add("cluster_queue") if (self.other_queue_settings) else exclude.add("cluster_queue")
        (
            include.add("message_service_domain")
            if (((self.publish_subscribe)) and (self.message_content_descriptor))
            else exclude.add("message_service_domain")
        )
        (
            include.add("remote_transmission_queue_name")
            if (self.other_queue_settings)
            else exclude.add("remote_transmission_queue_name")
        )
        (
            include.add("setter_source_acceptable_format_system_value")
            if (((self.set_header_fields)) and (not self.setter_source_acceptable_format_custom_value))
            else exclude.add("setter_source_acceptable_format_system_value")
        )
        (
            include.add("publisher_general_registration_options")
            if (((self.publish_subscribe)) and (self.registration))
            else exclude.add("publisher_general_registration_options")
        )
        include.add("custom_value") if (self.publish_subscribe) else exclude.add("custom_value")
        (
            include.add("dynamic_queue_name")
            if (((self.other_queue_settings)) and (self.open_as_dynamic_queue))
            else exclude.add("dynamic_queue_name")
        )
        (
            include.add("setter_source_acceptable_message_sequence_number_value")
            if (((self.set_header_fields)) and (self.setter_destination_header_version == "2"))
            else exclude.add("setter_source_acceptable_message_sequence_number_value")
        )
        (
            include.add("seperate_message_into_segments")
            if (self.message_options)
            else exclude.add("seperate_message_into_segments")
        )
        (
            include.add("setter_source_acceptable_feedback_system_value")
            if (((self.set_header_fields)) and (not self.setter_source_acceptable_feedback_custom_value))
            else exclude.add("setter_source_acceptable_feedback_system_value")
        )
        (
            include.add("setter_source_acceptable_user_id_value")
            if (
                (
                    (
                        (
                            self.context_mode
                            and (
                                (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                or (self.context_mode == "set_all")
                            )
                        )
                    )
                    or (
                        (
                            self.context_mode
                            and (
                                (hasattr(self.context_mode, "value") and self.context_mode.value == "set_identity")
                                or (self.context_mode == "set_identity")
                            )
                        )
                    )
                )
                and (self.set_header_fields)
            )
            else exclude.add("setter_source_acceptable_user_id_value")
        )
        (
            include.add("message_set")
            if (
                ((self.publish_subscribe))
                and (self.message_content_descriptor)
                and (((self.message_service_domain == "idoc")) or (self.message_service_domain == "mrm"))
            )
            else exclude.add("message_set")
        )
        (
            include.add("start_value")
            if (((self.publish_subscribe)) and (self.update_message_sequence_number))
            else exclude.add("start_value")
        )
        (
            include.add("system_value")
            if (((self.publish_subscribe)) and (not self.custom_value))
            else exclude.add("system_value")
        )
        (
            include.add("binding_mode")
            if (((self.other_queue_settings)) and (self.cluster_queue))
            else exclude.add("binding_mode")
        )
        (
            include.add("setter_source_acceptable_group_id")
            if (((self.set_header_fields)) and (self.setter_destination_header_version == "2"))
            else exclude.add("setter_source_acceptable_group_id")
        )
        (
            include.add("setter_source_acceptable_put_date_value")
            if (
                (
                    (
                        self.context_mode
                        and (
                            (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                            or (self.context_mode == "set_all")
                        )
                    )
                )
                and (self.set_header_fields)
            )
            else exclude.add("setter_source_acceptable_put_date_value")
        )
        (
            include.add("setter_source_application_origin_data")
            if (
                (
                    (
                        self.context_mode
                        and (
                            (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                            or (self.context_mode == "set_all")
                        )
                    )
                )
                and (self.set_header_fields)
            )
            else exclude.add("setter_source_application_origin_data")
        )
        (
            include.add("setter_source_acceptable_encoding_value")
            if (self.set_header_fields)
            else exclude.add("setter_source_acceptable_encoding_value")
        )
        (
            include.add("registration_options")
            if (self.publish_subscribe)
            else exclude.add("registration_options")
        )
        (
            include.add("size_of_message_segments")
            if (((self.message_options)) and (self.seperate_message_into_segments))
            else exclude.add("size_of_message_segments")
        )
        (
            include.add("setter_source_acceptable_offset_value")
            if (((self.set_header_fields)) and (self.setter_destination_header_version == "2"))
            else exclude.add("setter_source_acceptable_offset_value")
        )
        (
            include.add("setter_source_acceptable_put_application_name_value")
            if (
                (
                    (
                        self.context_mode
                        and (
                            (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                            or (self.context_mode == "set_all")
                        )
                    )
                )
                and (self.set_header_fields)
            )
            else exclude.add("setter_source_acceptable_put_application_name_value")
        )
        (
            include.add("setter_source_acceptable_persistence_value")
            if (self.set_header_fields)
            else exclude.add("setter_source_acceptable_persistence_value")
        )
        (
            include.add("setter_source_acceptable_reply_to_queue_manager_value")
            if (self.set_header_fields)
            else exclude.add("setter_source_acceptable_reply_to_queue_manager_value")
        )
        (
            include.add("setter_source_acceptable_put_application_type_system_value")
            if (
                (
                    (
                        self.context_mode
                        and (
                            (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                            or (self.context_mode == "set_all")
                        )
                    )
                )
                and (self.set_header_fields)
                and (not self.setter_source_acceptable_put_application_type_custom_value)
            )
            else exclude.add("setter_source_acceptable_put_application_type_system_value")
        )
        (
            include.add("setter_destination_header_version")
            if (self.set_header_fields)
            else exclude.add("setter_destination_header_version")
        )
        (
            include.add("setter_source_acceptable_put_time_value")
            if (
                (
                    (
                        self.context_mode
                        and (
                            (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                            or (self.context_mode == "set_all")
                        )
                    )
                )
                and (self.set_header_fields)
            )
            else exclude.add("setter_source_acceptable_put_time_value")
        )
        (
            include.add("setter_destination_report_value")
            if (self.set_header_fields)
            else exclude.add("setter_destination_report_value")
        )
        (
            include.add("setter_source_acceptable_expiry_interval_value")
            if (self.set_header_fields)
            else exclude.add("setter_source_acceptable_expiry_interval_value")
        )
        (
            include.add("physical_format")
            if (
                ((self.publish_subscribe))
                and (self.message_content_descriptor)
                and (((self.message_service_domain == "idoc")) or (self.message_service_domain == "mrm"))
            )
            else exclude.add("physical_format")
        )
        (
            include.add("update_message_sequence_number")
            if (self.publish_subscribe)
            else exclude.add("update_message_sequence_number")
        )
        include.add("row_buffer_count") if (self.message_options) else exclude.add("row_buffer_count")
        (
            include.add("message_content_descriptor")
            if (((self.publish_subscribe)) and (self.service_type == "mqrfh2"))
            else exclude.add("message_content_descriptor")
        )
        (
            include.add("setter_source_acceptable_message_type_system_value")
            if (((self.set_header_fields)) and (not self.setter_source_acceptable_message_type_custom_value))
            else exclude.add("setter_source_acceptable_message_type_system_value")
        )
        (
            include.add("setter_source_acceptable_coded_character_set_identifer")
            if (self.set_header_fields)
            else exclude.add("setter_source_acceptable_coded_character_set_identifer")
        )
        (
            include.add("setter_message_id_is_hex")
            if (self.set_header_fields)
            else exclude.add("setter_message_id_is_hex")
        )
        (
            include.add("setter_correlation_id_is_hex")
            if (self.set_header_fields)
            else exclude.add("setter_correlation_id_is_hex")
        )
        (
            include.add("set_message_id_to_column_value")
            if (self.message_options)
            else exclude.add("set_message_id_to_column_value")
        )
        (
            include.add("message_publication_options")
            if (self.publish_subscribe)
            else exclude.add("message_publication_options")
        )
        (
            include.add("cluster_queue_manager_name")
            if (((self.other_queue_settings)) and (self.cluster_queue))
            else exclude.add("cluster_queue_manager_name")
        )
        (
            include.add("setter_source_acceptable_put_application_type_custom_value")
            if (
                (
                    (
                        self.context_mode
                        and (
                            (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                            or (self.context_mode == "set_all")
                        )
                    )
                )
                and (self.set_header_fields)
            )
            else exclude.add("setter_source_acceptable_put_application_type_custom_value")
        )
        (
            include.add("setter_source_accptable_accounting_token_value")
            if (
                (
                    (
                        (
                            self.context_mode
                            and (
                                (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                or (self.context_mode == "set_all")
                            )
                        )
                    )
                    or (
                        (
                            self.context_mode
                            and (
                                (hasattr(self.context_mode, "value") and self.context_mode.value == "set_identity")
                                or (self.context_mode == "set_identity")
                            )
                        )
                    )
                )
                and (self.set_header_fields)
            )
            else exclude.add("setter_source_accptable_accounting_token_value")
        )
        (
            include.add("setter_source_acceptable_reply_to_queue_value")
            if (self.set_header_fields)
            else exclude.add("setter_source_acceptable_reply_to_queue_value")
        )
        (
            include.add("publisher_general_deregistration_options")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.deregistration)) or (self.deregistration and "#" in str(self.deregistration)))

            )
            else exclude.add("publisher_general_deregistration_options")
        )
        (
            include.add("setter_destination_message_flags")
            if (

                    (
                        ((self.set_header_fields))
                        or ((self.set_header_fields and "#" in str(self.set_header_fields)))
                    )
                    and (
                        ((self.setter_destination_header_version == "2"))
                        or (

                                self.setter_destination_header_version
                                and "#" in str(self.setter_destination_header_version)

                        )
                    )

            )
            else exclude.add("setter_destination_message_flags")
        )
        (
            include.add("setter_source_acceptable_format_custom_value")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_source_acceptable_format_custom_value")
        )
        (
            include.add("timestamp")
            if (


                        ((self.publish_subscribe))
                        or (self.publish_subscribe and "#" in str(self.publish_subscribe))


            )
            else exclude.add("timestamp")
        )
        (
            include.add("setter_acceptable_value_correlation_id")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_acceptable_value_correlation_id")
        )
        (
            include.add("setter_source_acceptable_feedback_custom_value")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_source_acceptable_feedback_custom_value")
        )
        (
            include.add("setter_source_acceptable_message_type_custom_value")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_source_acceptable_message_type_custom_value")
        )
        (
            include.add("setter_source_acceptable_priority_value")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_source_acceptable_priority_value")
        )
        (
            include.add("setter_use_wildcard_message_id")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_use_wildcard_message_id")
        )
        (
            include.add("setter_treat_accounting_token_as_hex")
            if (

                    (
                        (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                    or (self.context_mode == "set_all")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_identity")
                                    or (self.context_mode == "set_identity")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (
                                        hasattr(self.context_mode, "value")
                                        and self.context_mode.value
                                        and "#" in str(self.context_mode.value)
                                    )
                                    or ("#" in str(self.context_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))
                    )

            )
            else exclude.add("setter_treat_accounting_token_as_hex")
        )
        (
            include.add("message_type")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (
                        ((self.message_content_descriptor))
                        or (self.message_content_descriptor and "#" in str(self.message_content_descriptor))
                    )
                    and (
                        ((self.message_service_domain == "idoc"))
                        or (self.message_service_domain == "mrm")
                        or (self.message_service_domain and "#" in str(self.message_service_domain))
                    )

            )
            else exclude.add("message_type")
        )
        (
            include.add("open_as_dynamic_queue")
            if (


                        ((self.other_queue_settings))
                        or (self.other_queue_settings and "#" in str(self.other_queue_settings))


            )
            else exclude.add("open_as_dynamic_queue")
        )
        (
            include.add("publication_message_topic")
            if (


                        ((self.publish_subscribe))
                        or (self.publish_subscribe and "#" in str(self.publish_subscribe))


            )
            else exclude.add("publication_message_topic")
        )
        (
            include.add("setter_source_acceptable_application_id_data")
            if (

                    (
                        (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                    or (self.context_mode == "set_all")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_identity")
                                    or (self.context_mode == "set_identity")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (
                                        hasattr(self.context_mode, "value")
                                        and self.context_mode.value
                                        and "#" in str(self.context_mode.value)
                                    )
                                    or ("#" in str(self.context_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))
                    )

            )
            else exclude.add("setter_source_acceptable_application_id_data")
        )
        (
            include.add("dynamic_reply_queue_close_options")
            if (

                    (
                        ((self.other_queue_settings))
                        or ((self.other_queue_settings and "#" in str(self.other_queue_settings)))
                    )
                    and (
                        ((self.open_as_dynamic_queue))
                        or (self.open_as_dynamic_queue and "#" in str(self.open_as_dynamic_queue))
                    )

            )
            else exclude.add("dynamic_reply_queue_close_options")
        )
        (
            include.add("setter_group_id_is_hex")
            if (

                    (
                        ((self.set_header_fields))
                        or ((self.set_header_fields and "#" in str(self.set_header_fields)))
                    )
                    and (
                        ((self.setter_destination_header_version == "2"))
                        or (

                                self.setter_destination_header_version
                                and "#" in str(self.setter_destination_header_version)

                        )
                    )

            )
            else exclude.add("setter_group_id_is_hex")
        )
        (
            include.add("cluster_queue")
            if (


                        ((self.other_queue_settings))
                        or (self.other_queue_settings and "#" in str(self.other_queue_settings))


            )
            else exclude.add("cluster_queue")
        )
        (
            include.add("message_service_domain")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (
                        ((self.message_content_descriptor))
                        or (self.message_content_descriptor and "#" in str(self.message_content_descriptor))
                    )

            )
            else exclude.add("message_service_domain")
        )
        (
            include.add("remote_transmission_queue_name")
            if (


                        ((self.other_queue_settings))
                        or (self.other_queue_settings and "#" in str(self.other_queue_settings))


            )
            else exclude.add("remote_transmission_queue_name")
        )
        (
            include.add("setter_source_acceptable_format_system_value")
            if (

                    (
                        ((self.set_header_fields))
                        or ((self.set_header_fields and "#" in str(self.set_header_fields)))
                    )
                    and (
                        ((not self.setter_source_acceptable_format_custom_value))
                        or (

                                self.setter_source_acceptable_format_custom_value
                                and "#" in str(self.setter_source_acceptable_format_custom_value)

                        )
                    )

            )
            else exclude.add("setter_source_acceptable_format_system_value")
        )
        (
            include.add("publisher_general_registration_options")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.registration)) or (self.registration and "#" in str(self.registration)))

            )
            else exclude.add("publisher_general_registration_options")
        )
        (
            include.add("custom_value")
            if (


                        ((self.publish_subscribe))
                        or (self.publish_subscribe and "#" in str(self.publish_subscribe))


            )
            else exclude.add("custom_value")
        )
        (
            include.add("dynamic_queue_name")
            if (

                    (
                        ((self.other_queue_settings))
                        or ((self.other_queue_settings and "#" in str(self.other_queue_settings)))
                    )
                    and (
                        ((self.open_as_dynamic_queue))
                        or (self.open_as_dynamic_queue and "#" in str(self.open_as_dynamic_queue))
                    )

            )
            else exclude.add("dynamic_queue_name")
        )
        (
            include.add("setter_source_acceptable_message_sequence_number_value")
            if (

                    (
                        ((self.set_header_fields))
                        or ((self.set_header_fields and "#" in str(self.set_header_fields)))
                    )
                    and (
                        ((self.setter_destination_header_version == "2"))
                        or (

                                self.setter_destination_header_version
                                and "#" in str(self.setter_destination_header_version)

                        )
                    )

            )
            else exclude.add("setter_source_acceptable_message_sequence_number_value")
        )
        (
            include.add("seperate_message_into_segments")
            if (((self.message_options)) or (self.message_options and "#" in str(self.message_options)))
            else exclude.add("seperate_message_into_segments")
        )
        (
            include.add("setter_source_acceptable_feedback_system_value")
            if (

                    (
                        ((self.set_header_fields))
                        or ((self.set_header_fields and "#" in str(self.set_header_fields)))
                    )
                    and (
                        ((not self.setter_source_acceptable_feedback_custom_value))
                        or (

                                self.setter_source_acceptable_feedback_custom_value
                                and "#" in str(self.setter_source_acceptable_feedback_custom_value)

                        )
                    )

            )
            else exclude.add("setter_source_acceptable_feedback_system_value")
        )
        (
            include.add("setter_source_acceptable_user_id_value")
            if (

                    (
                        (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                    or (self.context_mode == "set_all")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_identity")
                                    or (self.context_mode == "set_identity")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (
                                        hasattr(self.context_mode, "value")
                                        and self.context_mode.value
                                        and "#" in str(self.context_mode.value)
                                    )
                                    or ("#" in str(self.context_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))
                    )

            )
            else exclude.add("setter_source_acceptable_user_id_value")
        )
        (
            include.add("message_set")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (
                        ((self.message_content_descriptor))
                        or (self.message_content_descriptor and "#" in str(self.message_content_descriptor))
                    )
                    and (
                        ((self.message_service_domain == "idoc"))
                        or (self.message_service_domain == "mrm")
                        or (self.message_service_domain and "#" in str(self.message_service_domain))
                    )

            )
            else exclude.add("message_set")
        )
        (
            include.add("start_value")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (
                        ((self.update_message_sequence_number))
                        or (self.update_message_sequence_number and "#" in str(self.update_message_sequence_number))
                    )

            )
            else exclude.add("start_value")
        )
        (
            include.add("system_value")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((not self.custom_value)) or (self.custom_value and "#" in str(self.custom_value)))

            )
            else exclude.add("system_value")
        )
        (
            include.add("binding_mode")
            if (

                    (
                        ((self.other_queue_settings))
                        or ((self.other_queue_settings and "#" in str(self.other_queue_settings)))
                    )
                    and (((self.cluster_queue)) or (self.cluster_queue and "#" in str(self.cluster_queue)))

            )
            else exclude.add("binding_mode")
        )
        (
            include.add("setter_source_acceptable_group_id")
            if (

                    (
                        ((self.set_header_fields))
                        or ((self.set_header_fields and "#" in str(self.set_header_fields)))
                    )
                    and (
                        ((self.setter_destination_header_version == "2"))
                        or (

                                self.setter_destination_header_version
                                and "#" in str(self.setter_destination_header_version)

                        )
                    )

            )
            else exclude.add("setter_source_acceptable_group_id")
        )
        (
            include.add("setter_source_acceptable_put_date_value")
            if (

                    (
                        (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                    or (self.context_mode == "set_all")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (
                                        hasattr(self.context_mode, "value")
                                        and self.context_mode.value
                                        and "#" in str(self.context_mode.value)
                                    )
                                    or ("#" in str(self.context_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))
                    )

            )
            else exclude.add("setter_source_acceptable_put_date_value")
        )
        (
            include.add("setter_source_application_origin_data")
            if (

                    (
                        (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                    or (self.context_mode == "set_all")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (
                                        hasattr(self.context_mode, "value")
                                        and self.context_mode.value
                                        and "#" in str(self.context_mode.value)
                                    )
                                    or ("#" in str(self.context_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))
                    )

            )
            else exclude.add("setter_source_application_origin_data")
        )
        (
            include.add("setter_source_acceptable_encoding_value")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_source_acceptable_encoding_value")
        )
        (
            include.add("registration_options")
            if (


                        ((self.publish_subscribe))
                        or (self.publish_subscribe and "#" in str(self.publish_subscribe))


            )
            else exclude.add("registration_options")
        )
        (
            include.add("size_of_message_segments")
            if (

                    (((self.message_options)) or ((self.message_options and "#" in str(self.message_options))))
                    and (
                        ((self.seperate_message_into_segments))
                        or (self.seperate_message_into_segments and "#" in str(self.seperate_message_into_segments))
                    )

            )
            else exclude.add("size_of_message_segments")
        )
        (
            include.add("setter_source_acceptable_offset_value")
            if (

                    (
                        ((self.set_header_fields))
                        or ((self.set_header_fields and "#" in str(self.set_header_fields)))
                    )
                    and (
                        ((self.setter_destination_header_version == "2"))
                        or (

                                self.setter_destination_header_version
                                and "#" in str(self.setter_destination_header_version)

                        )
                    )

            )
            else exclude.add("setter_source_acceptable_offset_value")
        )
        (
            include.add("setter_source_acceptable_put_application_name_value")
            if (

                    (
                        (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                    or (self.context_mode == "set_all")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (
                                        hasattr(self.context_mode, "value")
                                        and self.context_mode.value
                                        and "#" in str(self.context_mode.value)
                                    )
                                    or ("#" in str(self.context_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))
                    )

            )
            else exclude.add("setter_source_acceptable_put_application_name_value")
        )
        (
            include.add("setter_source_acceptable_persistence_value")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_source_acceptable_persistence_value")
        )
        (
            include.add("setter_source_acceptable_reply_to_queue_manager_value")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_source_acceptable_reply_to_queue_manager_value")
        )
        (
            include.add("setter_source_acceptable_put_application_type_system_value")
            if (

                    (
                        (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                    or (self.context_mode == "set_all")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (
                                        hasattr(self.context_mode, "value")
                                        and self.context_mode.value
                                        and "#" in str(self.context_mode.value)
                                    )
                                    or ("#" in str(self.context_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))
                    )
                    and (
                        ((not self.setter_source_acceptable_put_application_type_custom_value))
                        or (

                                self.setter_source_acceptable_put_application_type_custom_value
                                and "#" in str(self.setter_source_acceptable_put_application_type_custom_value)

                        )
                    )

            )
            else exclude.add("setter_source_acceptable_put_application_type_system_value")
        )
        (
            include.add("setter_destination_header_version")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_destination_header_version")
        )
        (
            include.add("setter_source_acceptable_put_time_value")
            if (

                    (
                        (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                    or (self.context_mode == "set_all")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (
                                        hasattr(self.context_mode, "value")
                                        and self.context_mode.value
                                        and "#" in str(self.context_mode.value)
                                    )
                                    or ("#" in str(self.context_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))
                    )

            )
            else exclude.add("setter_source_acceptable_put_time_value")
        )
        (
            include.add("setter_destination_report_value")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_destination_report_value")
        )
        (
            include.add("setter_source_acceptable_expiry_interval_value")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_source_acceptable_expiry_interval_value")
        )
        (
            include.add("physical_format")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (
                        ((self.message_content_descriptor))
                        or (self.message_content_descriptor and "#" in str(self.message_content_descriptor))
                    )
                    and (
                        ((self.message_service_domain == "idoc"))
                        or (self.message_service_domain == "mrm")
                        or (self.message_service_domain and "#" in str(self.message_service_domain))
                    )

            )
            else exclude.add("physical_format")
        )
        (
            include.add("update_message_sequence_number")
            if (


                        ((self.publish_subscribe))
                        or (self.publish_subscribe and "#" in str(self.publish_subscribe))


            )
            else exclude.add("update_message_sequence_number")
        )
        (
            include.add("row_buffer_count")
            if (((self.message_options)) or (self.message_options and "#" in str(self.message_options)))
            else exclude.add("row_buffer_count")
        )
        (
            include.add("message_content_descriptor")
            if (

                    (
                        ((self.publish_subscribe))
                        or ((self.publish_subscribe and "#" in str(self.publish_subscribe)))
                    )
                    and (((self.service_type == "mqrfh2")) or (self.service_type and "#" in str(self.service_type)))

            )
            else exclude.add("message_content_descriptor")
        )
        (
            include.add("setter_source_acceptable_message_type_system_value")
            if (

                    (
                        ((self.set_header_fields))
                        or ((self.set_header_fields and "#" in str(self.set_header_fields)))
                    )
                    and (
                        ((not self.setter_source_acceptable_message_type_custom_value))
                        or (

                                self.setter_source_acceptable_message_type_custom_value
                                and "#" in str(self.setter_source_acceptable_message_type_custom_value)

                        )
                    )

            )
            else exclude.add("setter_source_acceptable_message_type_system_value")
        )
        (
            include.add("setter_source_acceptable_coded_character_set_identifer")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_source_acceptable_coded_character_set_identifer")
        )
        (
            include.add("setter_message_id_is_hex")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_message_id_is_hex")
        )
        (
            include.add("setter_correlation_id_is_hex")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_correlation_id_is_hex")
        )
        (
            include.add("set_message_id_to_column_value")
            if (((self.message_options)) or (self.message_options and "#" in str(self.message_options)))
            else exclude.add("set_message_id_to_column_value")
        )
        (
            include.add("message_publication_options")
            if (


                        ((self.publish_subscribe))
                        or (self.publish_subscribe and "#" in str(self.publish_subscribe))


            )
            else exclude.add("message_publication_options")
        )
        (
            include.add("cluster_queue_manager_name")
            if (

                    (
                        ((self.other_queue_settings))
                        or ((self.other_queue_settings and "#" in str(self.other_queue_settings)))
                    )
                    and (((self.cluster_queue)) or (self.cluster_queue and "#" in str(self.cluster_queue)))

            )
            else exclude.add("cluster_queue_manager_name")
        )
        (
            include.add("setter_source_acceptable_put_application_type_custom_value")
            if (

                    (
                        (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                    or (self.context_mode == "set_all")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (
                                        hasattr(self.context_mode, "value")
                                        and self.context_mode.value
                                        and "#" in str(self.context_mode.value)
                                    )
                                    or ("#" in str(self.context_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))
                    )

            )
            else exclude.add("setter_source_acceptable_put_application_type_custom_value")
        )
        (
            include.add("setter_source_accptable_accounting_token_value")
            if (

                    (
                        (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                                    or (self.context_mode == "set_all")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_identity")
                                    or (self.context_mode == "set_identity")
                                )
                            )
                        )
                        or (
                            (
                                self.context_mode
                                and (
                                    (
                                        hasattr(self.context_mode, "value")
                                        and self.context_mode.value
                                        and "#" in str(self.context_mode.value)
                                    )
                                    or ("#" in str(self.context_mode))
                                )
                            )
                        )
                    )
                    and (
                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))
                    )

            )
            else exclude.add("setter_source_accptable_accounting_token_value")
        )
        (
            include.add("setter_source_acceptable_reply_to_queue_value")
            if (


                        ((self.set_header_fields))
                        or (self.set_header_fields and "#" in str(self.set_header_fields))


            )
            else exclude.add("setter_source_acceptable_reply_to_queue_value")
        )
        (
            include.add("setter_treat_accounting_token_as_hex")
            if (
                self.context_mode
                and (
                    (
                        hasattr(self.context_mode, "value")
                        and self.context_mode.value
                        and "set_all" in str(self.context_mode.value)
                    )
                    or ("set_all" in str(self.context_mode))
                )
                and self.context_mode
                and (
                    (
                        hasattr(self.context_mode, "value")
                        and self.context_mode.value
                        and "set_identity" in str(self.context_mode.value)
                    )
                    or ("set_identity" in str(self.context_mode))
                )
            )
            and (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_treat_accounting_token_as_hex")
        )
        (
            include.add("setter_acceptable_value_correlation_id")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_acceptable_value_correlation_id")
        )
        (
            include.add("setter_source_acceptable_encoding_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_encoding_value")
        )
        (
            include.add("setter_source_acceptable_group_id")
            if (self.set_header_fields == "true" or self.set_header_fields)
            and (self.setter_destination_header_version == "2")
            else exclude.add("setter_source_acceptable_group_id")
        )
        (
            include.add("update_message_sequence_number")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            else exclude.add("update_message_sequence_number")
        )
        (
            include.add("setter_destination_message_flags")
            if (self.set_header_fields == "true" or self.set_header_fields)
            and (self.setter_destination_header_version == "2")
            else exclude.add("setter_destination_message_flags")
        )
        (
            include.add("dynamic_queue_name")
            if (self.other_queue_settings == "true" or self.other_queue_settings)
            and (self.open_as_dynamic_queue == "true" or self.open_as_dynamic_queue)
            else exclude.add("dynamic_queue_name")
        )
        (
            include.add("setter_message_id_is_hex")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_message_id_is_hex")
        )
        (
            include.add("setter_source_acceptable_reply_to_queue_manager_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_reply_to_queue_manager_value")
        )
        (
            include.add("custom_value")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            else exclude.add("custom_value")
        )
        (
            include.add("binding_mode")
            if (self.other_queue_settings == "true" or self.other_queue_settings)
            and (self.cluster_queue == "true" or self.cluster_queue)
            else exclude.add("binding_mode")
        )
        (
            include.add("setter_source_acceptable_message_type_custom_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_message_type_custom_value")
        )
        (
            include.add("setter_source_acceptable_persistence_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_persistence_value")
        )
        (
            include.add("timestamp")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            else exclude.add("timestamp")
        )
        (
            include.add("message_publication_options")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            else exclude.add("message_publication_options")
        )
        (
            include.add("dynamic_reply_queue_close_options")
            if (self.other_queue_settings == "true" or self.other_queue_settings)
            and (self.open_as_dynamic_queue == "true" or self.open_as_dynamic_queue)
            else exclude.add("dynamic_reply_queue_close_options")
        )
        (
            include.add("setter_source_acceptable_put_application_name_value")
            if (
                self.context_mode
                and (
                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                    or (self.context_mode == "set_all")
                )
            )
            and (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_put_application_name_value")
        )
        (
            include.add("setter_source_acceptable_format_custom_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_format_custom_value")
        )
        (
            include.add("message_service_domain")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.message_content_descriptor == "true" or self.message_content_descriptor)
            else exclude.add("message_service_domain")
        )
        (
            include.add("open_as_dynamic_queue")
            if (self.other_queue_settings == "true" or self.other_queue_settings)
            else exclude.add("open_as_dynamic_queue")
        )
        (
            include.add("publication_message_topic")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            else exclude.add("publication_message_topic")
        )
        (
            include.add("setter_source_acceptable_put_application_type_custom_value")
            if (
                self.context_mode
                and (
                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                    or (self.context_mode == "set_all")
                )
            )
            and (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_put_application_type_custom_value")
        )
        (
            include.add("setter_source_acceptable_reply_to_queue_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_reply_to_queue_value")
        )
        (
            include.add("row_buffer_count")
            if (self.message_options == "true" or self.message_options)
            else exclude.add("row_buffer_count")
        )
        (
            include.add("remote_transmission_queue_name")
            if (self.other_queue_settings == "true" or self.other_queue_settings)
            else exclude.add("remote_transmission_queue_name")
        )
        (
            include.add("setter_source_acceptable_expiry_interval_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_expiry_interval_value")
        )
        (
            include.add("start_value")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.update_message_sequence_number == "true" or self.update_message_sequence_number)
            else exclude.add("start_value")
        )
        (
            include.add("setter_source_acceptable_feedback_custom_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_feedback_custom_value")
        )
        (
            include.add("seperate_message_into_segments")
            if (self.message_options == "true" or self.message_options)
            else exclude.add("seperate_message_into_segments")
        )
        (
            include.add("cluster_queue")
            if (self.other_queue_settings == "true" or self.other_queue_settings)
            else exclude.add("cluster_queue")
        )
        (
            include.add("setter_destination_report_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_destination_report_value")
        )
        (
            include.add("setter_source_acceptable_user_id_value")
            if (
                self.context_mode
                and (
                    (
                        hasattr(self.context_mode, "value")
                        and self.context_mode.value
                        and "set_all" in str(self.context_mode.value)
                    )
                    or ("set_all" in str(self.context_mode))
                )
                and self.context_mode
                and (
                    (
                        hasattr(self.context_mode, "value")
                        and self.context_mode.value
                        and "set_identity" in str(self.context_mode.value)
                    )
                    or ("set_identity" in str(self.context_mode))
                )
            )
            and (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_user_id_value")
        )
        (
            include.add("setter_source_acceptable_application_id_data")
            if (
                self.context_mode
                and (
                    (
                        hasattr(self.context_mode, "value")
                        and self.context_mode.value
                        and "set_all" in str(self.context_mode.value)
                    )
                    or ("set_all" in str(self.context_mode))
                )
                and self.context_mode
                and (
                    (
                        hasattr(self.context_mode, "value")
                        and self.context_mode.value
                        and "set_identity" in str(self.context_mode.value)
                    )
                    or ("set_identity" in str(self.context_mode))
                )
            )
            and (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_application_id_data")
        )
        (
            include.add("setter_source_application_origin_data")
            if (
                self.context_mode
                and (
                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                    or (self.context_mode == "set_all")
                )
            )
            and (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_application_origin_data")
        )
        (
            include.add("setter_group_id_is_hex")
            if (self.set_header_fields == "true" or self.set_header_fields)
            and (self.setter_destination_header_version == "2")
            else exclude.add("setter_group_id_is_hex")
        )
        (
            include.add("setter_source_acceptable_put_date_value")
            if (
                self.context_mode
                and (
                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                    or (self.context_mode == "set_all")
                )
            )
            and (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_put_date_value")
        )
        (
            include.add("message_type")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.message_content_descriptor == "true" or self.message_content_descriptor)
            and (
                self.message_service_domain
                and "idoc" in str(self.message_service_domain)
                and self.message_service_domain
                and "mrm" in str(self.message_service_domain)
            )
            else exclude.add("message_type")
        )
        (
            include.add("setter_destination_header_version")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_destination_header_version")
        )
        (
            include.add("message_content_descriptor")
            if (self.publish_subscribe == "true" or self.publish_subscribe) and (self.service_type == "mqrfh2")
            else exclude.add("message_content_descriptor")
        )
        (
            include.add("setter_use_wildcard_message_id")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_use_wildcard_message_id")
        )
        (
            include.add("setter_source_acceptable_priority_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_priority_value")
        )
        (
            include.add("setter_source_acceptable_offset_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            and (self.setter_destination_header_version == "2")
            else exclude.add("setter_source_acceptable_offset_value")
        )
        (
            include.add("setter_source_acceptable_message_sequence_number_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            and (self.setter_destination_header_version == "2")
            else exclude.add("setter_source_acceptable_message_sequence_number_value")
        )
        (
            include.add("size_of_message_segments")
            if (self.message_options == "true" or self.message_options)
            and (self.seperate_message_into_segments == "true" or self.seperate_message_into_segments)
            else exclude.add("size_of_message_segments")
        )
        (
            include.add("system_value")
            if (self.publish_subscribe == "true" or self.publish_subscribe) and (not self.custom_value)
            else exclude.add("system_value")
        )
        (
            include.add("setter_source_acceptable_message_type_system_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            and (not self.setter_source_acceptable_message_type_custom_value)
            else exclude.add("setter_source_acceptable_message_type_system_value")
        )
        (
            include.add("set_message_id_to_column_value")
            if (self.message_options == "true" or self.message_options)
            else exclude.add("set_message_id_to_column_value")
        )
        (
            include.add("publisher_general_registration_options")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.registration == "true" or self.registration)
            else exclude.add("publisher_general_registration_options")
        )
        (
            include.add("setter_source_acceptable_feedback_system_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            and (not self.setter_source_acceptable_feedback_custom_value)
            else exclude.add("setter_source_acceptable_feedback_system_value")
        )
        (
            include.add("setter_source_acceptable_put_time_value")
            if (
                self.context_mode
                and (
                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                    or (self.context_mode == "set_all")
                )
            )
            and (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_put_time_value")
        )
        (
            include.add("setter_source_accptable_accounting_token_value")
            if (
                self.context_mode
                and (
                    (
                        hasattr(self.context_mode, "value")
                        and self.context_mode.value
                        and "set_all" in str(self.context_mode.value)
                    )
                    or ("set_all" in str(self.context_mode))
                )
                and self.context_mode
                and (
                    (
                        hasattr(self.context_mode, "value")
                        and self.context_mode.value
                        and "set_identity" in str(self.context_mode.value)
                    )
                    or ("set_identity" in str(self.context_mode))
                )
            )
            and (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_accptable_accounting_token_value")
        )
        (
            include.add("setter_source_acceptable_coded_character_set_identifer")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_source_acceptable_coded_character_set_identifer")
        )
        (
            include.add("registration_options")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            else exclude.add("registration_options")
        )
        (
            include.add("setter_correlation_id_is_hex")
            if (self.set_header_fields == "true" or self.set_header_fields)
            else exclude.add("setter_correlation_id_is_hex")
        )
        (
            include.add("message_set")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.message_content_descriptor == "true" or self.message_content_descriptor)
            and (
                self.message_service_domain
                and "idoc" in str(self.message_service_domain)
                and self.message_service_domain
                and "mrm" in str(self.message_service_domain)
            )
            else exclude.add("message_set")
        )
        (
            include.add("cluster_queue_manager_name")
            if (self.other_queue_settings == "true" or self.other_queue_settings)
            and (self.cluster_queue == "true" or self.cluster_queue)
            else exclude.add("cluster_queue_manager_name")
        )
        (
            include.add("setter_source_acceptable_format_system_value")
            if (self.set_header_fields == "true" or self.set_header_fields)
            and (not self.setter_source_acceptable_format_custom_value)
            else exclude.add("setter_source_acceptable_format_system_value")
        )
        (
            include.add("publisher_general_deregistration_options")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.deregistration == "true" or self.deregistration)
            else exclude.add("publisher_general_deregistration_options")
        )
        (
            include.add("physical_format")
            if (self.publish_subscribe == "true" or self.publish_subscribe)
            and (self.message_content_descriptor == "true" or self.message_content_descriptor)
            and (
                self.message_service_domain
                and "idoc" in str(self.message_service_domain)
                and self.message_service_domain
                and "mrm" in str(self.message_service_domain)
            )
            else exclude.add("physical_format")
        )
        (
            include.add("setter_source_acceptable_put_application_type_system_value")
            if (
                self.context_mode
                and (
                    (hasattr(self.context_mode, "value") and self.context_mode.value == "set_all")
                    or (self.context_mode == "set_all")
                )
            )
            and (self.set_header_fields == "true" or self.set_header_fields)
            and (not self.setter_source_acceptable_put_application_type_custom_value)
            else exclude.add("setter_source_acceptable_put_application_type_system_value")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "access_mode",
            "alternate_user_id",
            "append_node_number",
            "blocking_transaction_processing",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "cipher_spec",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "content_filter",
            "current_output_link_type",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "deregistration",
            "deregistration_correlation_id",
            "deregistration_topic",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "dynamic_reply_queue",
            "dynamic_reply_queue_name",
            "enable_flow_acp_control",
            "enable_payload_reference",
            "enable_schemaless_design",
            "end_of_data",
            "end_of_data_message_type",
            "end_of_wave",
            "error_queue",
            "error_queue_context_mode",
            "error_queue_name",
            "error_queue_queue_manager_name",
            "execution_mode",
            "extract_key",
            "extract_key_length",
            "extract_key_offset",
            "filter_acceptable_value_correlation_id",
            "filter_confirm_on_arrival",
            "filter_correlation_id_is_hex",
            "filter_group_id_is_hex",
            "filter_group_id_use_wildcard",
            "filter_match_all_report",
            "filter_message_flags_must_match_all",
            "filter_message_id_is_hex",
            "filter_messages",
            "filter_source_acceptable_application_id_data",
            "filter_source_acceptable_backout_count",
            "filter_source_acceptable_coded_character_set_identifer",
            "filter_source_acceptable_encoding_value",
            "filter_source_acceptable_expiry_interval_value",
            "filter_source_acceptable_feedback_custom_value",
            "filter_source_acceptable_feedback_system_value",
            "filter_source_acceptable_format_custom_value",
            "filter_source_acceptable_format_system_value",
            "filter_source_acceptable_group_id",
            "filter_source_acceptable_message_flag_values",
            "filter_source_acceptable_message_payload_size_value",
            "filter_source_acceptable_message_sequence_number_value",
            "filter_source_acceptable_message_type_custom_value",
            "filter_source_acceptable_message_type_system_value",
            "filter_source_acceptable_offset_value",
            "filter_source_acceptable_original_length_value",
            "filter_source_acceptable_persistence_value",
            "filter_source_acceptable_priority_value",
            "filter_source_acceptable_put_application_name_value",
            "filter_source_acceptable_put_application_type_custom_value",
            "filter_source_acceptable_put_application_type_system_value",
            "filter_source_acceptable_put_date_value",
            "filter_source_acceptable_put_time_value",
            "filter_source_acceptable_reply_to_queue_manager_value",
            "filter_source_acceptable_reply_to_queue_value",
            "filter_source_acceptable_user_id_value",
            "filter_source_accptable_accounting_token_value",
            "filter_source_application_origin_data",
            "filter_treat_accounting_token_as_hex",
            "filter_use_wildcard_accounting_token",
            "filter_use_wildcard_correlation_id",
            "filter_use_wildcard_message_id",
            "flow_dirty",
            "hex",
            "hide",
            "identity_options",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_column",
            "max_mem_buf_size_ronly",
            "maximum_depth",
            "maximum_memory_buffer_size_bytes",
            "message_coded_character_set_id",
            "message_controlled",
            "message_conversion_encoding",
            "message_options",
            "message_order_and_assembly",
            "message_quantity",
            "message_read_mode",
            "minimum_depth",
            "monitor_queue_depth",
            "name",
            "other_queue_settings",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "pad_message_payload",
            "part_stable_coll",
            "part_stable_ordered",
            "part_stable_roundrobin_coll",
            "part_unique_coll",
            "part_unique_ordered",
            "part_unique_roundrobin_coll",
            "partition_type",
            "peform_message_conversion",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "period",
            "persistence_options",
            "preserve_partitioning",
            "process_end_of_data_message",
            "publish_subscribe",
            "queue_name",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "record_count",
            "record_ordering",
            "refresh",
            "registration",
            "registration_correlation_id",
            "registration_topics",
            "remove_mqrfh2_header",
            "reply_queue",
            "runtime_column_propagation",
            "service_type",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "sql_select_statement",
            "stable",
            "stage_description",
            "stream_name",
            "subscriber_general_deregistration_options",
            "subscriber_general_registration_options",
            "subscription_identity",
            "subscription_name",
            "subscription_point",
            "time_interval",
            "timeout",
            "transaction_end_of_day_method_name",
            "transaction_end_of_day_module_name",
            "transaction_message_controlled_method_name",
            "transaction_message_controlled_module_name",
            "transmission_queue",
            "treat_eol_as_row_terminator",
            "truncate_message",
            "unique",
            "value",
            "wait_time",
            "work_queue_context_mode",
        }
        required = {
            "current_output_link_type",
            "dynamic_reply_queue_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "error_queue_name",
            "extract_key_length",
            "extract_key_offset",
            "maximum_depth",
            "minimum_depth",
            "name",
            "output_acp_should_hide",
            "registration_topics",
            "transaction_end_of_day_method_name",
            "transaction_end_of_day_module_name",
            "transaction_message_controlled_method_name",
            "transaction_message_controlled_module_name",
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
            "alternate_user_id",
            "binding_mode",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "cipher_spec",
            "cluster_queue",
            "cluster_queue_manager_name",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "context_mode",
            "current_output_link_type",
            "custom_value",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "deregistration",
            "deregistration_correlation_id",
            "deregistration_topic",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "dynamic_queue_name",
            "dynamic_reply_queue",
            "dynamic_reply_queue_close_options",
            "dynamic_reply_queue_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "error_queue",
            "error_queue_context_mode",
            "error_queue_name",
            "error_queue_queue_manager_name",
            "execution_mode",
            "flow_dirty",
            "hex",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "key_column",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "message_content_descriptor",
            "message_options",
            "message_publication_options",
            "message_service_domain",
            "message_set",
            "message_type",
            "message_write_mode",
            "open_as_dynamic_queue",
            "other_queue_settings",
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
            "physical_format",
            "preserve_partitioning",
            "publication_message_topic",
            "publish_subscribe",
            "publisher_general_deregistration_options",
            "publisher_general_registration_options",
            "queue_name",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "record_count",
            "record_ordering",
            "registration",
            "registration_correlation_id",
            "registration_options",
            "registration_topics",
            "remote_transmission_queue_name",
            "reply_queue",
            "row_buffer_count",
            "runtime_column_propagation",
            "seperate_message_into_segments",
            "service_type",
            "set_header_fields",
            "set_message_id_to_column_value",
            "setter_acceptable_value_correlation_id",
            "setter_correlation_id_is_hex",
            "setter_destination_header_version",
            "setter_destination_message_flags",
            "setter_destination_report_value",
            "setter_group_id_is_hex",
            "setter_message_id_is_hex",
            "setter_source_acceptable_application_id_data",
            "setter_source_acceptable_coded_character_set_identifer",
            "setter_source_acceptable_encoding_value",
            "setter_source_acceptable_expiry_interval_value",
            "setter_source_acceptable_feedback_custom_value",
            "setter_source_acceptable_feedback_system_value",
            "setter_source_acceptable_format_custom_value",
            "setter_source_acceptable_format_system_value",
            "setter_source_acceptable_group_id",
            "setter_source_acceptable_message_sequence_number_value",
            "setter_source_acceptable_message_type_custom_value",
            "setter_source_acceptable_message_type_system_value",
            "setter_source_acceptable_offset_value",
            "setter_source_acceptable_persistence_value",
            "setter_source_acceptable_priority_value",
            "setter_source_acceptable_put_application_name_value",
            "setter_source_acceptable_put_application_type_custom_value",
            "setter_source_acceptable_put_application_type_system_value",
            "setter_source_acceptable_put_date_value",
            "setter_source_acceptable_put_time_value",
            "setter_source_acceptable_reply_to_queue_manager_value",
            "setter_source_acceptable_reply_to_queue_value",
            "setter_source_acceptable_user_id_value",
            "setter_source_accptable_accounting_token_value",
            "setter_source_application_origin_data",
            "setter_treat_accounting_token_as_hex",
            "setter_use_wildcard_message_id",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "size_of_message_segments",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "sql_select_statement",
            "stable",
            "stage_description",
            "start_value",
            "system_value",
            "timestamp",
            "transmission_queue",
            "unique",
            "update_message_sequence_number",
            "value",
        }
        required = {
            "current_output_link_type",
            "dynamic_queue_name",
            "dynamic_reply_queue_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "error_queue_name",
            "message_service_domain",
            "output_acp_should_hide",
            "registration_topics",
            "size_of_message_segments",
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
        props = {"execution_mode", "input_count", "output_count", "preserve_partitioning", "record_ordering"}
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
