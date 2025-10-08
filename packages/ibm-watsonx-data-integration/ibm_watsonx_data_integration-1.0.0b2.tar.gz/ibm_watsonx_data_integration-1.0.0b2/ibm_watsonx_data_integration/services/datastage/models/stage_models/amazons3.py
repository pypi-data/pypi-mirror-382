import re
import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.amazons3_connection import Amazons3Conn
from ibm_watsonx_data_integration.services.datastage.models.enums import AMAZONS3
from pydantic import Field
from typing import ClassVar


class amazons3(BaseStage):

    op_name: ClassVar[str] = "AmazonS3PX"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/AmazonS3PX.svg"
    label: ClassVar[str] = "Amazon S3"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: Amazons3Conn = Amazons3Conn()
    append_unique_identifier: bool | None = Field(False, alias="append_uid")
    bucket: str | None = Field(None, alias="bucket")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: AMAZONS3.BufModeRonly | None = Field(AMAZONS3.BufModeRonly.default, alias="buf_mode_ronly")
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: AMAZONS3.BufferingMode | None = Field(AMAZONS3.BufferingMode.default, alias="buf_mode")
    byte_limit: str | None = Field(None, alias="byte_limit")
    cell_range: str | None = Field(None, alias="range")
    codec_avro: AMAZONS3.CodecAvro | None = Field(None, alias="codec_avro")
    codec_csv: AMAZONS3.CodecCsv | None = Field(None, alias="codec_csv")
    codec_delimited: AMAZONS3.CodecDelimited | None = Field(None, alias="codec_delimited")
    codec_orc: AMAZONS3.CodecOrc | None = Field(None, alias="codec_orc")
    codec_parquet: AMAZONS3.CodecParquet | None = Field(None, alias="codec_parquet")
    collecting: AMAZONS3.Collecting | None = Field(AMAZONS3.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: AMAZONS3.CombinabilityMode | None = Field(
        AMAZONS3.CombinabilityMode.auto, alias="combinability"
    )
    create_bucket: bool | None = Field(False, alias="create_bucket")
    create_data_asset: bool | None = Field(False, alias="registerDataAsset")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_asset_name: str = Field(None, alias="dataAssetName")
    date_format: str | None = Field(None, alias="date_format")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    decimal_format: str | None = Field(None, alias="decimal_format")
    decimal_grouping_separator: str | None = Field(None, alias="decimal_format_grouping_separator")
    decimal_rounding_mode: AMAZONS3.DecimalRoundingMode | None = Field(
        AMAZONS3.DecimalRoundingMode.floor, alias="decimal_rounding_mode"
    )
    decimal_separator: str | None = Field(None, alias="decimal_format_decimal_separator")
    default_maximum_length_for_columns: int | None = Field(20000, alias="default_max_string_binary_precision")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    delete_bucket: bool | None = Field(False, alias="delete_bucket")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    display_value_labels: bool | None = Field(None, alias="display_value_labels")
    ds_codec_avro: AMAZONS3.DSCodecAvro | None = Field(None, alias="_codec_avro")
    ds_create_bucket_append_u_u_i_d: bool | None = Field(False, alias="_create_bucket._append_u_u_i_d")
    ds_exclude_files: str | None = Field(None, alias="_exclude_files")
    ds_file_attributes: bool | None = Field(None, alias="_file_attributes")
    ds_file_attributes_content_type: str | None = Field(None, alias="_file_attributes._content_type")
    ds_file_attributes_encryption: AMAZONS3.DSFileAttributesEncryption | None = Field(
        AMAZONS3.DSFileAttributesEncryption.none, alias="_file_attributes._encryption"
    )
    ds_file_attributes_life_cycle_rule: bool | None = Field(False, alias="_file_attributes._life_cycle_rule")
    ds_file_attributes_life_cycle_rule_expiration: bool | None = Field(
        False, alias="_file_attributes._life_cycle_rule._expiration"
    )
    ds_file_attributes_life_cycle_rule_expiration_expiration_date: str = Field(
        None, alias="_file_attributes._life_cycle_rule._expiration._expiration_date"
    )
    ds_file_attributes_life_cycle_rule_expiration_expiration_duration: int = Field(
        None, alias="_file_attributes._life_cycle_rule._expiration._expiration_duration"
    )
    ds_file_attributes_life_cycle_rule_l_c_rule_format: AMAZONS3.DSFileAttributesLifeCycleRuleLCRuleFormat | None = (
        Field(
            AMAZONS3.DSFileAttributesLifeCycleRuleLCRuleFormat.days_from_creation,
            alias="_file_attributes._life_cycle_rule._l_c_rule_format",
        )
    )
    ds_file_attributes_life_cycle_rule_l_c_rule_scope: AMAZONS3.DSFileAttributesLifeCycleRuleLCRuleScope | None = (
        Field(
            AMAZONS3.DSFileAttributesLifeCycleRuleLCRuleScope.file,
            alias="_file_attributes._life_cycle_rule._l_c_rule_scope",
        )
    )
    ds_file_attributes_life_cycle_rule_transition: bool | None = Field(
        False, alias="_file_attributes._life_cycle_rule._transition"
    )
    ds_file_attributes_life_cycle_rule_transition_transition_date: str = Field(
        None, alias="_file_attributes._life_cycle_rule._transition._transition_date"
    )
    ds_file_attributes_life_cycle_rule_transition_transition_duration: int = Field(
        None, alias="_file_attributes._life_cycle_rule._transition._transition_duration"
    )
    ds_file_attributes_storage_class: AMAZONS3.DSFileAttributesStorageClass | None = Field(
        AMAZONS3.DSFileAttributesStorageClass.standard_class, alias="_file_attributes._storage_class"
    )
    ds_file_attributes_user_metadata: str | None = Field(None, alias="_file_attributes._user_metadata")
    ds_file_exists: AMAZONS3.DSFileExists | None = Field(AMAZONS3.DSFileExists.overwrite, alias="_file_exists")
    ds_file_format: AMAZONS3.DSFileFormat | None = Field(AMAZONS3.DSFileFormat.delimited, alias="_file_format")
    ds_file_format_avro_source: bool | None = Field(None, alias="_file_format._avro_source")
    ds_file_format_avro_source_output_j_s_o_n: bool | None = Field(
        False, alias="_file_format._avro_source._output_j_s_o_n"
    )
    ds_file_format_avrotarget: bool | None = Field(None, alias="_file_format._avrotarget")
    ds_file_format_avrotarget_avro_array_keys: str | None = Field(
        None, alias="_file_format._avrotarget._avro_array_keys"
    )
    ds_file_format_avrotarget_avro_schema: str | None = Field(None, alias="_file_format._avrotarget._avro_schema")
    ds_file_format_avrotarget_input_j_s_o_n: bool | None = Field(
        False, alias="_file_format._avrotarget._input_j_s_o_n"
    )
    ds_file_format_avrotarget_use_schema: bool | None = Field(False, alias="_file_format._avrotarget._use_schema")
    ds_file_format_delimited_syntax: bool | None = Field(None, alias="_file_format._delimited_syntax")
    ds_file_format_delimited_syntax_data_format: AMAZONS3.DSFileFormatDelimitedSyntaxDataFormat | None = Field(
        AMAZONS3.DSFileFormatDelimitedSyntaxDataFormat.test, alias="_file_format._delimited_syntax._data_format"
    )
    ds_file_format_delimited_syntax_encoding_output_b_o_m: bool | None = Field(
        False, alias="_file_format._delimited_syntax._encoding._output_b_o_m"
    )
    ds_file_format_delimited_syntax_escape: str | None = Field(None, alias="_file_format._delimited_syntax._escape")
    ds_file_format_delimited_syntax_field_delimiter: str | None = Field(
        ",", alias="_file_format._delimited_syntax._field_delimiter"
    )
    ds_file_format_delimited_syntax_record_def: AMAZONS3.DSFileFormatDelimitedSyntaxRecordDef | None = Field(
        AMAZONS3.DSFileFormatDelimitedSyntaxRecordDef.none, alias="_file_format._delimited_syntax._record_def"
    )
    ds_file_format_delimited_syntax_record_def_record_def_source: str | None = Field(
        None, alias="_file_format._delimited_syntax._record_def._record_def_source"
    )
    ds_file_format_delimited_syntax_row_delimiter: str | None = Field(
        "<NL>", alias="_file_format._delimited_syntax._row_delimiter"
    )
    ds_file_format_delimited_syntax_trace_file: str | None = Field(
        None, alias="_file_format._delimited_syntax._trace_file"
    )
    ds_file_format_o_r_c_source: bool | None = Field(None, alias="_file_format._o_r_c_source")
    ds_file_format_o_r_c_source_temp_staging_area: str | None = Field(
        None, alias="_file_format._o_r_c_source._temp_staging_area"
    )
    ds_file_format_o_r_c_target: bool | None = Field(None, alias="_file_format._o_r_c_target")
    ds_file_format_o_r_c_target_orc_buffer_size: int | None = Field(
        10000, alias="_file_format._o_r_c_target._orc_buffer_size"
    )
    ds_file_format_o_r_c_target_orc_compress: AMAZONS3.DSFileFormatORCTargetOrcCompress | None = Field(
        AMAZONS3.DSFileFormatORCTargetOrcCompress.gzip, alias="_file_format._o_r_c_target._orc_compress"
    )
    ds_file_format_o_r_c_target_orc_stripe_size: int | None = Field(
        100000, alias="_file_format._o_r_c_target._orc_stripe_size"
    )
    ds_file_format_o_r_c_target_temp_staging_area: str | None = Field(
        None, alias="_file_format._o_r_c_target._temp_staging_area"
    )
    ds_file_format_parquet_source: bool | None = Field(None, alias="_file_format._parquet_source")
    ds_file_format_parquet_source_temp_staging_area: str | None = Field(
        None, alias="_file_format._parquet_source._temp_staging_area"
    )
    ds_file_format_parquet_target: bool | None = Field(None, alias="_file_format._parquet_target")
    ds_file_format_parquet_target_parquet_block_size: int | None = Field(
        10000000, alias="_file_format._parquet_target._parquet_block_size"
    )
    ds_file_format_parquet_target_parquet_compress: AMAZONS3.DSFileFormatParquetTargetParquetCompress | None = Field(
        AMAZONS3.DSFileFormatParquetTargetParquetCompress.snappy, alias="_file_format._parquet_target._parquet_compress"
    )
    ds_file_format_parquet_target_parquet_page_size: int | None = Field(
        10000, alias="_file_format._parquet_target._parquet_page_size"
    )
    ds_file_format_parquet_target_temp_staging_area: str | None = Field(
        None, alias="_file_format._parquet_target._temp_staging_area"
    )
    ds_filename_column: str | None = Field(None, alias="_filename_column")
    ds_first_line_header: bool | None = Field(False, alias="_first_line_header")
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    ds_log_interval: int | None = Field(None, alias="_log_interval")
    ds_read_mode: AMAZONS3.DSReadMode | None = Field(AMAZONS3.DSReadMode.single_file, alias="_read_mode")
    ds_recurse: bool | None = Field(True, alias="_recurse")
    ds_reject_mode: AMAZONS3.DSRejectMode | None = Field(AMAZONS3.DSRejectMode.cont, alias="_reject_mode")
    ds_thread_count: int | None = Field(5, alias="_thread_count")
    ds_use_datastage: bool | None = Field(True, alias="_use_datastage")
    ds_write_mode: AMAZONS3.DSWriteMode | None = Field(AMAZONS3.DSWriteMode.write, alias="_write_mode")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    encoding: str | None = Field("utf-8", alias="encoding")
    encryption_key: str | None = Field(None, alias="encryption_key")
    endpoint_folder: str | None = Field(None, alias="table_folder_name")
    escape_character: AMAZONS3.EscapeCharacter | None = Field(
        AMAZONS3.EscapeCharacter.none, alias="escape_character"
    )
    escape_character_value: str = Field(None, alias="escape_character_value")
    exclude_missing_values: bool | None = Field(None, alias="exclude_missing_values")
    execution_mode: AMAZONS3.ExecutionMode | None = Field(AMAZONS3.ExecutionMode.default_par, alias="execmode")
    field_delimiter: AMAZONS3.FieldDelimiter | None = Field(AMAZONS3.FieldDelimiter.comma, alias="field_delimiter")
    field_delimiter_value: str = Field(None, alias="field_delimiter_value")
    fields_xml_path: str | None = Field(None, alias="xml_path_fields")
    file_format: AMAZONS3.FileFormat | None = Field(AMAZONS3.FileFormat.csv, alias="file_format")
    file_name: str | None = Field(None, alias="file_name")
    file_size_threshold: int | None = Field(1, alias="file_size_threshold")
    first_line: int | None = Field(0, alias="first_line")
    first_line_is_header: bool | None = Field(False, alias="first_line_header")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    generate_unicode_type_columns: bool | None = Field(False, alias="generate_unicode_columns")
    hide: bool | None = Field(False, alias="hide")
    include_types: bool | None = Field(False, alias="include_types")
    infer_as_varchar: bool | None = Field(None, alias="infer_as_varchar")
    infer_null_as_empty_string: bool | None = Field(False, alias="infer_null_as_empty_string")
    infer_record_count: int | None = Field(1000, alias="infer_record_count")
    infer_schema: bool | None = Field(None, alias="infer_schema")
    infer_timestamp_as_date: bool | None = Field(True, alias="infer_timestamp_as_date")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    invalid_data_handling: AMAZONS3.InvalidDataHandling | None = Field(
        AMAZONS3.InvalidDataHandling.fail, alias="invalid_data_handling"
    )
    is_reject_link: bool | None = Field(False, alias="is_reject")
    json_infer_record_count: int | None = Field(None, alias="json_infer_record_count")
    json_path: str | None = Field(None, alias="json_path")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    labels_as_names: bool | None = Field(None, alias="labels_as_names")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    names_as_labels: bool | None = Field(None, alias="names_as_labels")
    null_value: str | None = Field(None, alias="null_value")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_avro_as_json: bool | None = Field(None, alias="output_avro_as_json")
    output_count: int | None = Field(1, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    partition_name_prefix: str | None = Field("part", alias="partition_name_prefix")
    partition_type: AMAZONS3.PartitionType | None = Field(AMAZONS3.PartitionType.auto, alias="part_type")
    partitioned: bool | None = Field(False, alias="partitioned")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: AMAZONS3.PreservePartitioning | None = Field(
        AMAZONS3.PreservePartitioning.default_propagate, alias="preserve"
    )
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    quote_character: AMAZONS3.QuoteCharacter | None = Field(AMAZONS3.QuoteCharacter.none, alias="quote_character")
    quote_numeric_values: bool | None = Field(True, alias="quote_numerics")
    read_a_file_to_a_row: bool | None = Field(False, alias="read_file_to_row")
    read_mode: AMAZONS3.ReadMode | None = Field(AMAZONS3.ReadMode.read_single, alias="read_mode")
    read_part_size: int | None = Field(None, alias="read_part_size")
    row_delimiter: AMAZONS3.RowDelimiter | None = Field(AMAZONS3.RowDelimiter.new_line, alias="row_delimiter")
    row_delimiter_value: str = Field(None, alias="row_delimiter_value")
    row_limit: int | None = Field(None, alias="row_limit")
    row_start: int | None = Field(None, alias="row_start")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    schema_of_xml: str | None = Field(None, alias="xml_schema")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: AMAZONS3.KeyColSelect | None = Field(AMAZONS3.KeyColSelect.default, alias="keyColSelect")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    store_shared_strings_in_the_temporary_file: bool | None = Field(None, alias="use_sst_temp_file")
    table_action: AMAZONS3.TableAction | None = Field(AMAZONS3.TableAction.append, alias="table_action")
    table_data_file_compression_codec: AMAZONS3.TableDataFileCompressionCodec | None = Field(
        None, alias="table_data_file_compression_codec"
    )
    table_data_file_format: AMAZONS3.TableDataFileFormat | None = Field(
        AMAZONS3.TableDataFileFormat.avro, alias="table_data_file_format"
    )
    table_format: AMAZONS3.TableFormat | None = Field(None, alias="table_format")
    table_name: str | None = Field(None, alias="table_name")
    table_namespace: str | None = Field(None, alias="table_namespace")
    the_cache_expiration: str | None = Field(None, alias="table_partition_cache_expiration")
    the_cache_size: int | None = Field(None, alias="table_partition_cache_size")
    the_data_path: str | None = Field(None, alias="table_data_path")
    the_partition_columns: str | None = Field(None, alias="table_partition_columns")
    the_partition_paths: str | None = Field(None, alias="table_partition_path")
    time_format: str | None = Field(None, alias="time_format")
    timestamp_format: str | None = Field(None, alias="timestamp_format")
    timezone_format: str | None = Field(None, alias="time_zone_format")
    type_mapping: str | None = Field(None, alias="type_mapping")
    unique: bool | None = Field(None, alias="part_unique")
    use_4_digit_years_in_date_formats: bool | None = Field(None, alias="use_4_digit_year")
    use_field_formats: bool | None = Field(None, alias="use_field_formats")
    use_variable_formats: bool | None = Field(None, alias="use_variable_formats")
    worksheet_name: str | None = Field(None, alias="sheet_name")
    write_mode: AMAZONS3.WriteMode | None = Field(AMAZONS3.WriteMode.write, alias="write_mode")
    write_part_size: int | None = Field(None, alias="write_part_size")
    xml_path: str | None = Field(None, alias="xml_path")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("preserve_partitioning")
            if (self.output_count and self.output_count > 0)
            else exclude.add("preserve_partitioning")
        )
        include.add("is_reject_link") if (self.ds_use_datastage) else exclude.add("is_reject_link")
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("ds_file_format_parquet_source")
            if (self.ds_file_format == "6")
            else exclude.add("ds_file_format_parquet_source")
        )
        (
            include.add("null_value")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                    )
                )
                or (
                    ((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2")
                )
            )
            else exclude.add("null_value")
        )
        (
            include.add("ds_recurse")
            if (((self.ds_read_mode == "1")) or (self.ds_read_mode == "3"))
            else exclude.add("ds_recurse")
        )
        (
            include.add("quote_character")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                    )
                )
                or (self.ds_file_format == "0")
            )
            else exclude.add("quote_character")
        )
        (
            include.add("ds_file_format_delimited_syntax_row_delimiter")
            if (self.ds_file_format == "0")
            else exclude.add("ds_file_format_delimited_syntax_row_delimiter")
        )
        (
            include.add("time_format")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                    or (self.file_format == "parquet")
                                )
                            )
                        )
                    )
                    and ((not self.output_avro_as_json))
                )
                or (
                    ((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2")
                )
            )
            else exclude.add("time_format")
        )
        (
            include.add("ds_file_format_delimited_syntax_field_delimiter")
            if (self.ds_file_format == "0")
            else exclude.add("ds_file_format_delimited_syntax_field_delimiter")
        )
        (
            include.add("encoding")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "shp")
                                    or (self.file_format == "shp")
                                )
                            )
                        )
                    )
                )
                or (((self.ds_file_format == "0")) or (self.ds_file_format == "1"))
            )
            else exclude.add("encoding")
        )
        (
            include.add("bucket")
            if (
                (((self.ds_read_mode == "0")) or ((self.ds_read_mode == "1")) or ((self.ds_read_mode == "3")))
                or (not self.ds_read_mode)
            )
            else exclude.add("bucket")
        )
        (
            include.add("timestamp_format")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                    or (self.file_format == "parquet")
                                )
                            )
                        )
                    )
                    and ((not self.output_avro_as_json))
                )
                or (
                    ((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2")
                )
            )
            else exclude.add("timestamp_format")
        )
        (
            include.add("ds_file_format_avro_source_output_j_s_o_n")
            if (self.ds_file_format == "4")
            else exclude.add("ds_file_format_avro_source_output_j_s_o_n")
        )
        (
            include.add("ds_file_format_delimited_syntax_record_def")
            if (((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2"))
            else exclude.add("ds_file_format_delimited_syntax_record_def")
        )
        (
            include.add("table_format")
            if (


                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "read_single")
                            or (self.read_mode == "read_single")
                        )


            )
            else exclude.add("table_format")
        )
        (
            include.add("ds_file_format_parquet_source_temp_staging_area")
            if (self.ds_file_format == "6")
            else exclude.add("ds_file_format_parquet_source_temp_staging_area")
        )
        (
            include.add("ds_file_format_delimited_syntax_data_format")
            if (self.ds_file_format == "0")
            else exclude.add("ds_file_format_delimited_syntax_data_format")
        )
        (
            include.add("ds_file_format_delimited_syntax_trace_file")
            if (((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2"))
            else exclude.add("ds_file_format_delimited_syntax_trace_file")
        )
        (
            include.add("ds_reject_mode")
            if (((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2"))
            else exclude.add("ds_reject_mode")
        )
        (
            include.add("ds_file_format_delimited_syntax")
            if (((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2"))
            else exclude.add("ds_file_format_delimited_syntax")
        )
        (
            include.add("ds_file_format_o_r_c_source_temp_staging_area")
            if (self.ds_file_format == "7")
            else exclude.add("ds_file_format_o_r_c_source_temp_staging_area")
        )
        (
            include.add("quote_numeric_values")
            if (self.ds_file_format_delimited_syntax_data_format == "1")
            else exclude.add("quote_numeric_values")
        )
        (
            include.add("file_name")
            if (
                (
                    (
                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )
                            )
                        )
                    )
                )
                or (
                    (
                        (((self.ds_read_mode == "0")) or ((self.ds_read_mode == "1")) or ((self.ds_read_mode == "3")))
                        or ((not self.ds_read_mode))
                    )
                    and (
                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and not self.table_format.value)
                                    or (not self.table_format)
                                )
                            )
                        )
                        or (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value == "file")
                                    or (self.table_format == "file")
                                )

                        )
                    )
                )
            )
            else exclude.add("file_name")
        )
        (
            include.add("ds_file_format")
            if (((self.ds_read_mode == "0")) or (self.ds_read_mode == "1"))
            else exclude.add("ds_file_format")
        )
        (
            include.add("ds_file_format_delimited_syntax_escape")
            if (self.ds_file_format == "0")
            else exclude.add("ds_file_format_delimited_syntax_escape")
        )
        (
            include.add("ds_filename_column")
            if (((self.ds_read_mode == "0")) or (self.ds_read_mode == "1"))
            else exclude.add("ds_filename_column")
        )
        (
            include.add("ds_file_format_avro_source")
            if (self.ds_file_format == "4")
            else exclude.add("ds_file_format_avro_source")
        )
        (
            include.add("ds_first_line_header")
            if (

                    ((self.ds_file_format_delimited_syntax_record_def == "0"))
                    or (self.ds_file_format_delimited_syntax_record_def == "2")
                    or (self.ds_file_format_delimited_syntax_record_def == "3")
                    or (self.ds_file_format_delimited_syntax_record_def == "4")

            )
            else exclude.add("ds_first_line_header")
        )
        (
            include.add("decimal_format")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                    or (self.file_format == "parquet")
                                )
                            )
                        )
                    )
                    and ((not self.output_avro_as_json))
                )
                or (
                    ((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2")
                )
            )
            else exclude.add("decimal_format")
        )
        (
            include.add("row_limit")
            if (
                ((not self.ds_read_mode))
                or (
                    ((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2")
                )
            )
            else exclude.add("row_limit")
        )
        (
            include.add("ds_file_format_delimited_syntax_record_def_record_def_source")
            if (

                    ((self.ds_file_format_delimited_syntax_record_def == "2"))
                    or (self.ds_file_format_delimited_syntax_record_def == "3")
                    or (self.ds_file_format_delimited_syntax_record_def == "4")

            )
            else exclude.add("ds_file_format_delimited_syntax_record_def_record_def_source")
        )
        (
            include.add("date_format")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                    or (self.file_format == "parquet")
                                )
                            )
                        )
                    )
                    and ((not self.output_avro_as_json))
                )
                or (
                    ((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2")
                )
            )
            else exclude.add("date_format")
        )
        include.add("ds_exclude_files") if (self.ds_read_mode == "1") else exclude.add("ds_exclude_files")
        (
            include.add("decimal_separator")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                or (self.file_format == "avro")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                or (self.file_format == "parquet")
                            )
                        )
                    )
                )
                and (not self.output_avro_as_json)
            )
            else exclude.add("decimal_separator")
        )
        (
            include.add("xml_path")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "xml")
                            or (self.file_format == "xml")
                        )


            )
            else exclude.add("xml_path")
        )
        (
            include.add("table_namespace")
            if (
                (
                    (
                        (
                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                                or (self.table_format == "iceberg")
                            )
                        )
                    )
                )
                and (self.endpoint_folder)
            )
            else exclude.add("table_namespace")
        )
        (
            include.add("output_avro_as_json")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                            or (self.file_format == "avro")
                        )


            )
            else exclude.add("output_avro_as_json")
        )
        (
            include.add("first_line_is_header")
            if (

                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )

                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                or (self.file_format == "excel")
                            )

                    )

            )
            else exclude.add("first_line_is_header")
        )
        include.add("table_name") if (self.endpoint_folder) else exclude.add("table_name")
        (
            include.add("store_shared_strings_in_the_temporary_file")
            if (



                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                or (self.file_format == "excel")
                            )



            )
            else exclude.add("store_shared_strings_in_the_temporary_file")
        )
        (
            include.add("infer_null_as_empty_string")
            if (

                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )

                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                or (self.file_format == "excel")
                            )

                    )

            )
            else exclude.add("infer_null_as_empty_string")
        )
        (
            include.add("escape_character")
            if (

                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )

                    )

            )
            else exclude.add("escape_character")
        )
        (
            include.add("display_value_labels")
            if (
                (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                            or (self.file_format == "sav")
                        )
                    )
                )
                and (not self.exclude_missing_values)
            )
            else exclude.add("display_value_labels")
        )
        (
            include.add("invalid_data_handling")
            if (

                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )

                    )

            )
            else exclude.add("invalid_data_handling")
        )
        (
            include.add("escape_character_value")
            if (



                            self.escape_character
                            and (
                                (hasattr(self.escape_character, "value") and self.escape_character.value == "<?>")
                                or (self.escape_character == "<?>")
                            )



            )
            else exclude.add("escape_character_value")
        )
        (
            include.add("fields_xml_path")
            if (
                (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "xml")
                            or (self.file_format == "xml")
                        )
                    )
                )
                and (self.xml_path)
            )
            else exclude.add("fields_xml_path")
        )
        (
            include.add("schema_of_xml")
            if (
                (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "xml")
                            or (self.file_format == "xml")
                        )
                    )
                )
                and (self.infer_schema)
            )
            else exclude.add("schema_of_xml")
        )
        (
            include.add("field_delimiter")
            if (



                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )



            )
            else exclude.add("field_delimiter")
        )
        (
            include.add("use_variable_formats")
            if (
                (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "sas")
                            or (self.file_format == "sas")
                        )
                    )
                )
                and (not self.infer_schema)
            )
            else exclude.add("use_variable_formats")
        )
        (
            include.add("infer_record_count")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                or (self.file_format == "excel")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "json")
                                or (self.file_format == "json")
                            )
                        )
                    )
                )
                and (self.infer_schema)
            )
            else exclude.add("infer_record_count")
        )
        (
            include.add("decimal_grouping_separator")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                or (self.file_format == "avro")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                or (self.file_format == "parquet")
                            )
                        )
                    )
                )
                and (not self.output_avro_as_json)
            )
            else exclude.add("decimal_grouping_separator")
        )
        (
            include.add("exclude_missing_values")
            if (
                (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                            or (self.file_format == "sav")
                        )
                    )
                )
                and (not self.display_value_labels)
            )
            else exclude.add("exclude_missing_values")
        )
        (
            include.add("encryption_key")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                            or (self.file_format == "sav")
                        )


            )
            else exclude.add("encryption_key")
        )
        (
            include.add("worksheet_name")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                            or (self.file_format == "excel")
                        )


            )
            else exclude.add("worksheet_name")
        )
        (
            include.add("infer_timestamp_as_date")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                            or (self.file_format == "sav")
                        )


            )
            else exclude.add("infer_timestamp_as_date")
        )
        (
            include.add("first_line")
            if (

                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )

                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                or (self.file_format == "excel")
                            )

                    )

            )
            else exclude.add("first_line")
        )
        (
            include.add("endpoint_folder")
            if (

                    (
                        (
                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value == "deltalake")
                                or (self.table_format == "deltalake")
                            )
                        )
                    )
                    or (

                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                                or (self.table_format == "iceberg")
                            )

                    )

            )
            else exclude.add("endpoint_folder")
        )
        (
            include.add("cell_range")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                            or (self.file_format == "excel")
                        )


            )
            else exclude.add("cell_range")
        )
        (
            include.add("use_4_digit_years_in_date_formats")
            if (



                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                or (self.file_format == "excel")
                            )



            )
            else exclude.add("use_4_digit_years_in_date_formats")
        )
        (
            include.add("json_infer_record_count")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "json")
                            or (self.file_format == "json")
                        )


            )
            else exclude.add("json_infer_record_count")
        )
        (
            include.add("read_a_file_to_a_row")
            if (


                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "read_raw_multiple_wildcard")
                            or (self.read_mode == "read_raw_multiple_wildcard")
                        )


            )
            else exclude.add("read_a_file_to_a_row")
        )
        (
            include.add("file_format")
            if (
                (
                    (
                        (
                            (
                                self.read_mode
                                and (
                                    (hasattr(self.read_mode, "value") and self.read_mode.value == "read_multiple_regex")
                                    or (self.read_mode == "read_multiple_regex")
                                )
                            )
                        )
                        or (
                            (
                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value == "read_multiple_wildcard"
                                    )
                                    or (self.read_mode == "read_multiple_wildcard")
                                )
                            )
                        )
                        or (
                            (
                                self.read_mode
                                and (
                                    (hasattr(self.read_mode, "value") and self.read_mode.value == "read_single")
                                    or (self.read_mode == "read_single")
                                )
                            )
                        )
                    )
                )
                and (

                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )

                        )

                )
            )
            else exclude.add("file_format")
        )
        (
            include.add("field_delimiter_value")
            if (



                            self.field_delimiter
                            and (
                                (hasattr(self.field_delimiter, "value") and self.field_delimiter.value == "<?>")
                                or (self.field_delimiter == "<?>")
                            )



            )
            else exclude.add("field_delimiter_value")
        )
        (
            include.add("row_delimiter")
            if (



                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )



            )
            else exclude.add("row_delimiter")
        )
        (
            include.add("use_field_formats")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                            or (self.file_format == "sav")
                        )


            )
            else exclude.add("use_field_formats")
        )
        (
            include.add("json_path")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "json")
                            or (self.file_format == "json")
                        )


            )
            else exclude.add("json_path")
        )
        (
            include.add("row_delimiter_value")
            if (



                            self.row_delimiter
                            and (
                                (hasattr(self.row_delimiter, "value") and self.row_delimiter.value == "<?>")
                                or (self.row_delimiter == "<?>")
                            )



            )
            else exclude.add("row_delimiter_value")
        )
        (
            include.add("decimal_rounding_mode")
            if (

                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )

                    )

            )
            else exclude.add("decimal_rounding_mode")
        )
        (
            include.add("labels_as_names")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                            or (self.file_format == "sav")
                        )


            )
            else exclude.add("labels_as_names")
        )
        (
            include.add("type_mapping")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                    )
                    or ((self.infer_schema))
                )
                and (self.infer_schema)
            )
            else exclude.add("type_mapping")
        )
        (
            include.add("decimal_separator")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                            or (self.file_format == "avro")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                            or (self.file_format == "csv")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value == "delimited"
                                            )
                                            or (self.file_format == "delimited")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                            or (self.file_format == "parquet")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                ((not self.output_avro_as_json))
                                or ((self.output_avro_as_json and "#" in str(self.output_avro_as_json)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("decimal_separator")
        )
        (
            include.add("xml_path")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "xml")
                                    or (self.file_format == "xml")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("xml_path")
        )
        (
            include.add("table_namespace")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value == "iceberg"
                                            )
                                            or (self.table_format == "iceberg")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value
                                                and "#" in str(self.table_format.value)
                                            )
                                            or ("#" in str(self.table_format))
                                        )
                                    )
                                )
                            )
                            and (
                                ((self.endpoint_folder))
                                or ((self.endpoint_folder and "#" in str(self.endpoint_folder)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("table_namespace")
        )
        (
            include.add("ds_file_format_parquet_source")
            if (

                    (((((self.ds_file_format == "6")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_parquet_source")
        )
        (
            include.add("null_value")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (
                                    hasattr(self.file_format, "value")
                                    and self.file_format.value
                                    and "#" in str(self.file_format.value)
                                )
                                or ("#" in str(self.file_format))
                            )
                        )
                    )
                )
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format == "2")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
            )
            else exclude.add("null_value")
        )
        (
            include.add("output_avro_as_json")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("output_avro_as_json")
        )
        (
            include.add("first_line_is_header")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                    or (self.file_format == "excel")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("first_line_is_header")
        )
        (
            include.add("table_name")
            if (

                    (((self.endpoint_folder)) or ((self.endpoint_folder and "#" in str(self.endpoint_folder))))
                    and (not self.ds_use_datastage)

            )
            else exclude.add("table_name")
        )
        (
            include.add("store_shared_strings_in_the_temporary_file")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                    or (self.file_format == "excel")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("store_shared_strings_in_the_temporary_file")
        )
        (
            include.add("ds_recurse")
            if (

                    (
                        (
                            (
                                ((self.ds_read_mode == "1"))
                                or ((self.ds_read_mode == "3"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_recurse")
        )
        (
            include.add("quote_character")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (
                                    hasattr(self.file_format, "value")
                                    and self.file_format.value
                                    and "#" in str(self.file_format.value)
                                )
                                or ("#" in str(self.file_format))
                            )
                        )
                    )
                )
                or (((self.ds_file_format == "0")) or (self.ds_file_format and "#" in str(self.ds_file_format)))
            )
            else exclude.add("quote_character")
        )
        (
            include.add("infer_null_as_empty_string")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                    or (self.file_format == "excel")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("infer_null_as_empty_string")
        )
        (
            include.add("escape_character")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("escape_character")
        )
        (
            include.add("display_value_labels")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                                            or (self.file_format == "sav")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                ((not self.exclude_missing_values))
                                or ((self.exclude_missing_values and "#" in str(self.exclude_missing_values)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("display_value_labels")
        )
        (
            include.add("invalid_data_handling")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("invalid_data_handling")
        )
        (
            include.add("ds_file_format_delimited_syntax_row_delimiter")
            if (

                    (((((self.ds_file_format == "0")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_delimited_syntax_row_delimiter")
        )
        (
            include.add("escape_character_value")
            if (

                    (
                        (
                            (
                                self.escape_character
                                and (
                                    (hasattr(self.escape_character, "value") and self.escape_character.value == "<?>")
                                    or (self.escape_character == "<?>")
                                )
                            )
                        )
                        or (
                            (
                                self.escape_character
                                and (
                                    (
                                        hasattr(self.escape_character, "value")
                                        and self.escape_character.value
                                        and "#" in str(self.escape_character.value)
                                    )
                                    or ("#" in str(self.escape_character))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("escape_character_value")
        )
        (
            include.add("time_format")
            if (
                (
                    (
                        (
                            (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                        or (self.file_format == "avro")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                        or (self.file_format == "csv")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                        or (self.file_format == "delimited")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                        or (self.file_format == "parquet")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (
                                            hasattr(self.file_format, "value")
                                            and self.file_format.value
                                            and "#" in str(self.file_format.value)
                                        )
                                        or ("#" in str(self.file_format))
                                    )
                                )
                            )
                        )
                        and (
                            ((not self.output_avro_as_json))
                            or ((self.output_avro_as_json and "#" in str(self.output_avro_as_json)))
                        )
                    )
                )
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format == "2")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
            )
            else exclude.add("time_format")
        )
        (
            include.add("fields_xml_path")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "xml")
                                            or (self.file_format == "xml")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (((self.xml_path)) or ((self.xml_path and "#" in str(self.xml_path))))
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("fields_xml_path")
        )
        (
            include.add("schema_of_xml")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "xml")
                                            or (self.file_format == "xml")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                ((self.infer_schema)) or ((self.infer_schema and "#" in str(self.infer_schema)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("schema_of_xml")
        )
        (
            include.add("ds_file_format_delimited_syntax_field_delimiter")
            if (

                    (((((self.ds_file_format == "0")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_delimited_syntax_field_delimiter")
        )
        (
            include.add("encoding")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "shp")
                                or (self.file_format == "shp")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (
                                    hasattr(self.file_format, "value")
                                    and self.file_format.value
                                    and "#" in str(self.file_format.value)
                                )
                                or ("#" in str(self.file_format))
                            )
                        )
                    )
                )
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
            )
            else exclude.add("encoding")
        )
        (
            include.add("field_delimiter")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("field_delimiter")
        )
        (
            include.add("use_variable_formats")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "sas")
                                            or (self.file_format == "sas")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                ((not self.infer_schema)) or ((self.infer_schema and "#" in str(self.infer_schema)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("use_variable_formats")
        )
        (
            include.add("bucket")
            if (
                (
                    ((self.ds_read_mode == "0"))
                    or ((self.ds_read_mode == "1"))
                    or ((self.ds_read_mode == "3"))
                    or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                )
                or (not self.ds_read_mode)
                or (self.ds_read_mode and "#" in str(self.ds_read_mode))
            )
            else exclude.add("bucket")
        )
        (
            include.add("timestamp_format")
            if (
                (
                    (
                        (
                            (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                        or (self.file_format == "avro")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                        or (self.file_format == "csv")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                        or (self.file_format == "delimited")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                        or (self.file_format == "parquet")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (
                                            hasattr(self.file_format, "value")
                                            and self.file_format.value
                                            and "#" in str(self.file_format.value)
                                        )
                                        or ("#" in str(self.file_format))
                                    )
                                )
                            )
                        )
                        and (
                            ((not self.output_avro_as_json))
                            or ((self.output_avro_as_json and "#" in str(self.output_avro_as_json)))
                        )
                    )
                )
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format == "2")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
            )
            else exclude.add("timestamp_format")
        )
        (
            include.add("ds_file_format_avro_source_output_j_s_o_n")
            if (

                    (((((self.ds_file_format == "4")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_avro_source_output_j_s_o_n")
        )
        (
            include.add("ds_file_format_delimited_syntax_record_def")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "0"))
                                or ((self.ds_file_format == "1"))
                                or ((self.ds_file_format == "2"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_delimited_syntax_record_def")
        )
        (
            include.add("infer_record_count")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                            or (self.file_format == "csv")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value == "delimited"
                                            )
                                            or (self.file_format == "delimited")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                            or (self.file_format == "excel")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "json")
                                            or (self.file_format == "json")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                ((self.infer_schema)) or ((self.infer_schema and "#" in str(self.infer_schema)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("infer_record_count")
        )
        (
            include.add("decimal_grouping_separator")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                            or (self.file_format == "avro")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                            or (self.file_format == "csv")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value == "delimited"
                                            )
                                            or (self.file_format == "delimited")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                            or (self.file_format == "parquet")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                ((not self.output_avro_as_json))
                                or ((self.output_avro_as_json and "#" in str(self.output_avro_as_json)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("decimal_grouping_separator")
        )
        (
            include.add("exclude_missing_values")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                                            or (self.file_format == "sav")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                ((not self.display_value_labels))
                                or ((self.display_value_labels and "#" in str(self.display_value_labels)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("exclude_missing_values")
        )
        (
            include.add("encryption_key")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                                    or (self.file_format == "sav")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("encryption_key")
        )
        (
            include.add("worksheet_name")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                    or (self.file_format == "excel")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("worksheet_name")
        )
        (
            include.add("table_format")
            if (
                (
                    (
                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "read_single")
                            or (self.read_mode == "read_single")
                        )
                    )
                )
                or (

                        self.read_mode
                        and (
                            (
                                hasattr(self.read_mode, "value")
                                and self.read_mode.value
                                and "#" in str(self.read_mode.value)
                            )
                            or ("#" in str(self.read_mode))
                        )

                )
            )
            else exclude.add("table_format")
        )
        (
            include.add("infer_timestamp_as_date")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                                    or (self.file_format == "sav")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("infer_timestamp_as_date")
        )
        (
            include.add("ds_file_format_parquet_source_temp_staging_area")
            if (

                    (((((self.ds_file_format == "6")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_parquet_source_temp_staging_area")
        )
        (
            include.add("ds_file_format_delimited_syntax_data_format")
            if (

                    (((((self.ds_file_format == "0")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_delimited_syntax_data_format")
        )
        (
            include.add("first_line")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                    or (self.file_format == "excel")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("first_line")
        )
        (
            include.add("ds_file_format_delimited_syntax_trace_file")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "0"))
                                or ((self.ds_file_format == "1"))
                                or ((self.ds_file_format == "2"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_delimited_syntax_trace_file")
        )
        (
            include.add("endpoint_folder")
            if (

                    (
                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value == "deltalake")
                                    or (self.table_format == "deltalake")
                                )
                            )
                        )
                        or (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                                    or (self.table_format == "iceberg")
                                )
                            )
                        )
                        or (
                            (
                                self.table_format
                                and (
                                    (
                                        hasattr(self.table_format, "value")
                                        and self.table_format.value
                                        and "#" in str(self.table_format.value)
                                    )
                                    or ("#" in str(self.table_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("endpoint_folder")
        )
        (
            include.add("cell_range")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                    or (self.file_format == "excel")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("cell_range")
        )
        (
            include.add("use_4_digit_years_in_date_formats")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                    or (self.file_format == "excel")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("use_4_digit_years_in_date_formats")
        )
        (
            include.add("json_infer_record_count")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "json")
                                    or (self.file_format == "json")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("json_infer_record_count")
        )
        (
            include.add("ds_reject_mode")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "0"))
                                or ((self.ds_file_format == "1"))
                                or ((self.ds_file_format == "2"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_reject_mode")
        )
        (
            include.add("read_a_file_to_a_row")
            if (

                    (
                        (
                            (
                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value == "read_raw_multiple_wildcard"
                                    )
                                    or (self.read_mode == "read_raw_multiple_wildcard")
                                )
                            )
                        )
                        or (
                            (
                                self.read_mode
                                and (
                                    (
                                        hasattr(self.read_mode, "value")
                                        and self.read_mode.value
                                        and "#" in str(self.read_mode.value)
                                    )
                                    or ("#" in str(self.read_mode))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("read_a_file_to_a_row")
        )
        (
            include.add("ds_file_format_delimited_syntax")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "0"))
                                or ((self.ds_file_format == "1"))
                                or ((self.ds_file_format == "2"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_delimited_syntax")
        )
        (
            include.add("file_format")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.read_mode
                                        and (
                                            (
                                                hasattr(self.read_mode, "value")
                                                and self.read_mode.value == "read_multiple_regex"
                                            )
                                            or (self.read_mode == "read_multiple_regex")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_mode
                                        and (
                                            (
                                                hasattr(self.read_mode, "value")
                                                and self.read_mode.value == "read_multiple_wildcard"
                                            )
                                            or (self.read_mode == "read_multiple_wildcard")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_mode
                                        and (
                                            (hasattr(self.read_mode, "value") and self.read_mode.value == "read_single")
                                            or (self.read_mode == "read_single")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.read_mode
                                        and (
                                            (
                                                hasattr(self.read_mode, "value")
                                                and self.read_mode.value
                                                and "#" in str(self.read_mode.value)
                                            )
                                            or ("#" in str(self.read_mode))
                                        )
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "deltalake"
                                                    )
                                                    or (self.table_format != "deltalake")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
                                                )
                                            )
                                        )
                                    )
                                    and (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "iceberg"
                                                    )
                                                    or (self.table_format != "iceberg")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
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
            else exclude.add("file_format")
        )
        (
            include.add("ds_file_format_o_r_c_source_temp_staging_area")
            if (

                    (((((self.ds_file_format == "7")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_o_r_c_source_temp_staging_area")
        )
        (
            include.add("field_delimiter_value")
            if (

                    (
                        (
                            (
                                self.field_delimiter
                                and (
                                    (hasattr(self.field_delimiter, "value") and self.field_delimiter.value == "<?>")
                                    or (self.field_delimiter == "<?>")
                                )
                            )
                        )
                        or (
                            (
                                self.field_delimiter
                                and (
                                    (
                                        hasattr(self.field_delimiter, "value")
                                        and self.field_delimiter.value
                                        and "#" in str(self.field_delimiter.value)
                                    )
                                    or ("#" in str(self.field_delimiter))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("field_delimiter_value")
        )
        (
            include.add("row_delimiter")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("row_delimiter")
        )
        (
            include.add("quote_numeric_values")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format_delimited_syntax_data_format == "1"))
                                or (
                                    (
                                        self.ds_file_format_delimited_syntax_data_format
                                        and "#" in str(self.ds_file_format_delimited_syntax_data_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("quote_numeric_values")
        )
        (
            include.add("use_field_formats")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                                    or (self.file_format == "sav")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("use_field_formats")
        )
        (
            include.add("file_name")
            if (
                (
                    (
                        (
                            (
                                (
                                    self.table_format
                                    and (
                                        (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                        or (self.table_format != "deltalake")
                                    )
                                )
                            )
                            or (
                                (
                                    self.table_format
                                    and (
                                        (
                                            hasattr(self.table_format, "value")
                                            and self.table_format.value
                                            and "#" in str(self.table_format.value)
                                        )
                                        or ("#" in str(self.table_format))
                                    )
                                )
                            )
                        )
                        and (
                            (
                                (
                                    self.table_format
                                    and (
                                        (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                        or (self.table_format != "iceberg")
                                    )
                                )
                            )
                            or (
                                (
                                    self.table_format
                                    and (
                                        (
                                            hasattr(self.table_format, "value")
                                            and self.table_format.value
                                            and "#" in str(self.table_format.value)
                                        )
                                        or ("#" in str(self.table_format))
                                    )
                                )
                            )
                        )
                    )
                )
                or (

                        (
                            (
                                ((self.ds_read_mode == "0"))
                                or ((self.ds_read_mode == "1"))
                                or ((self.ds_read_mode == "3"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                            or ((not self.ds_read_mode))
                            or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                        )
                        and (
                            (
                                (
                                    self.table_format
                                    and (
                                        (hasattr(self.table_format, "value") and not self.table_format.value)
                                        or (not self.table_format)
                                    )
                                )
                            )
                            or (

                                    self.table_format
                                    and (
                                        (hasattr(self.table_format, "value") and self.table_format.value == "file")
                                        or (self.table_format == "file")
                                    )

                            )
                            or (

                                    self.table_format
                                    and (
                                        (
                                            hasattr(self.table_format, "value")
                                            and self.table_format.value
                                            and "#" in str(self.table_format.value)
                                        )
                                        or ("#" in str(self.table_format))
                                    )

                            )
                        )

                )
            )
            else exclude.add("file_name")
        )
        (
            include.add("json_path")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "json")
                                    or (self.file_format == "json")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("json_path")
        )
        (
            include.add("ds_file_format")
            if (

                    (
                        ((self.ds_read_mode == "0"))
                        or ((self.ds_read_mode == "1"))
                        or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format")
        )
        (
            include.add("ds_file_format_delimited_syntax_escape")
            if (

                    (((((self.ds_file_format == "0")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_delimited_syntax_escape")
        )
        (
            include.add("ds_filename_column")
            if (

                    (
                        (
                            (
                                ((self.ds_read_mode == "0"))
                                or ((self.ds_read_mode == "1"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_filename_column")
        )
        (
            include.add("row_delimiter_value")
            if (

                    (
                        (
                            (
                                self.row_delimiter
                                and (
                                    (hasattr(self.row_delimiter, "value") and self.row_delimiter.value == "<?>")
                                    or (self.row_delimiter == "<?>")
                                )
                            )
                        )
                        or (
                            (
                                self.row_delimiter
                                and (
                                    (
                                        hasattr(self.row_delimiter, "value")
                                        and self.row_delimiter.value
                                        and "#" in str(self.row_delimiter.value)
                                    )
                                    or ("#" in str(self.row_delimiter))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("row_delimiter_value")
        )
        (
            include.add("ds_file_format_avro_source")
            if (

                    (((((self.ds_file_format == "4")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_avro_source")
        )
        (
            include.add("ds_first_line_header")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format_delimited_syntax_record_def == "0"))
                                or ((self.ds_file_format_delimited_syntax_record_def == "2"))
                                or ((self.ds_file_format_delimited_syntax_record_def == "3"))
                                or ((self.ds_file_format_delimited_syntax_record_def == "4"))
                                or (
                                    (
                                        self.ds_file_format_delimited_syntax_record_def
                                        and "#" in str(self.ds_file_format_delimited_syntax_record_def)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_first_line_header")
        )
        (
            include.add("decimal_format")
            if (
                (
                    (
                        (
                            (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                        or (self.file_format == "avro")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                        or (self.file_format == "csv")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                        or (self.file_format == "delimited")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                        or (self.file_format == "parquet")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (
                                            hasattr(self.file_format, "value")
                                            and self.file_format.value
                                            and "#" in str(self.file_format.value)
                                        )
                                        or ("#" in str(self.file_format))
                                    )
                                )
                            )
                        )
                        and (
                            ((not self.output_avro_as_json))
                            or ((self.output_avro_as_json and "#" in str(self.output_avro_as_json)))
                        )
                    )
                )
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format == "2")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
            )
            else exclude.add("decimal_format")
        )
        (
            include.add("decimal_rounding_mode")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("decimal_rounding_mode")
        )
        (
            include.add("labels_as_names")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                                    or (self.file_format == "sav")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("labels_as_names")
        )
        (
            include.add("row_limit")
            if (
                ((not self.ds_read_mode))
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format == "2")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
                or (self.ds_read_mode and "#" in str(self.ds_read_mode))
            )
            else exclude.add("row_limit")
        )
        (
            include.add("ds_file_format_delimited_syntax_record_def_record_def_source")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format_delimited_syntax_record_def == "2"))
                                or ((self.ds_file_format_delimited_syntax_record_def == "3"))
                                or ((self.ds_file_format_delimited_syntax_record_def == "4"))
                                or (
                                    (
                                        self.ds_file_format_delimited_syntax_record_def
                                        and "#" in str(self.ds_file_format_delimited_syntax_record_def)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_delimited_syntax_record_def_record_def_source")
        )
        (
            include.add("date_format")
            if (
                (
                    (
                        (
                            (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                        or (self.file_format == "avro")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                        or (self.file_format == "csv")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                        or (self.file_format == "delimited")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                        or (self.file_format == "parquet")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (
                                            hasattr(self.file_format, "value")
                                            and self.file_format.value
                                            and "#" in str(self.file_format.value)
                                        )
                                        or ("#" in str(self.file_format))
                                    )
                                )
                            )
                        )
                        and (
                            ((not self.output_avro_as_json))
                            or ((self.output_avro_as_json and "#" in str(self.output_avro_as_json)))
                        )
                    )
                )
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format == "2")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
            )
            else exclude.add("date_format")
        )
        (
            include.add("ds_exclude_files")
            if (

                    (((((self.ds_read_mode == "1")) or ((self.ds_read_mode and "#" in str(self.ds_read_mode))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_exclude_files")
        )
        (
            include.add("type_mapping")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        (
                                            self.file_format
                                            and (
                                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                                or (self.file_format == "csv")
                                            )
                                        )
                                    )
                                    or (
                                        (
                                            self.file_format
                                            and (
                                                (
                                                    hasattr(self.file_format, "value")
                                                    and self.file_format.value == "delimited"
                                                )
                                                or (self.file_format == "delimited")
                                            )
                                        )
                                    )
                                    or (
                                        (
                                            self.file_format
                                            and (
                                                (
                                                    hasattr(self.file_format, "value")
                                                    and self.file_format.value
                                                    and "#" in str(self.file_format.value)
                                                )
                                                or ("#" in str(self.file_format))
                                            )
                                        )
                                    )
                                )
                                or ((self.infer_schema))
                                or ((self.infer_schema and "#" in str(self.infer_schema)))
                            )
                            and (
                                ((self.infer_schema)) or ((self.infer_schema and "#" in str(self.infer_schema)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("type_mapping")
        )

        include.add("infer_as_varchar") if (()) else exclude.add("infer_as_varchar")
        include.add("infer_schema") if (()) else exclude.add("infer_schema")
        (
            include.add("partition_name_prefix")
            if (not self.ds_use_datastage)
            else exclude.add("partition_name_prefix")
        )
        include.add("read_mode") if (not self.ds_use_datastage) else exclude.add("read_mode")
        include.add("ds_read_mode") if (self.ds_use_datastage) else exclude.add("ds_read_mode")
        include.add("byte_limit") if (not self.ds_use_datastage) else exclude.add("byte_limit")
        (
            include.add("default_maximum_length_for_columns")
            if (not self.ds_use_datastage)
            else exclude.add("default_maximum_length_for_columns")
        )
        (
            include.add("generate_unicode_type_columns")
            if (not self.ds_use_datastage)
            else exclude.add("generate_unicode_type_columns")
        )
        (
            include.add("ds_file_format_o_r_c_source")
            if (self.ds_use_datastage)
            else exclude.add("ds_file_format_o_r_c_source")
        )
        include.add("read_part_size") if (not self.ds_use_datastage) else exclude.add("read_part_size")
        include.add("row_start") if (not self.ds_use_datastage) else exclude.add("row_start")
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
            include.add("is_reject_link")
            if (

                    ((self.ds_use_datastage))
                    and (((self.ds_reject_mode == "2")) or (self.ds_reject_mode and "#" in str(self.ds_reject_mode)))

            )
            else exclude.add("is_reject_link")
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
            include.add("ds_file_format_delimited_syntax")
            if (
                self.ds_file_format
                and "0" in str(self.ds_file_format)
                and self.ds_file_format
                and "1" in str(self.ds_file_format)
                and self.ds_file_format
                and "2" in str(self.ds_file_format)
            )
            else exclude.add("ds_file_format_delimited_syntax")
        )
        (
            include.add("ds_file_format_delimited_syntax_row_delimiter")
            if (self.ds_file_format and "0" in str(self.ds_file_format))
            else exclude.add("ds_file_format_delimited_syntax_row_delimiter")
        )
        (
            include.add("ds_filename_column")
            if (
                self.ds_read_mode
                and "0" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "1" in str(self.ds_read_mode)
            )
            else exclude.add("ds_filename_column")
        )
        (
            include.add("time_format")
            if (
                (
                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "avro" in str(self.file_format.value)
                        )
                        or ("avro" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "parquet" in str(self.file_format.value)
                        )
                        or ("parquet" in str(self.file_format))
                    )
                )
                and (not self.output_avro_as_json)
            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "2" in str(self.ds_file_format)

            )
            else exclude.add("time_format")
        )
        (
            include.add("endpoint_folder")
            if (
                self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "deltalake" in str(self.table_format.value)
                    )
                    or ("deltalake" in str(self.table_format))
                )
                or self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "iceberg" in str(self.table_format.value)
                    )
                    or ("iceberg" in str(self.table_format))
                )
            )
            else exclude.add("endpoint_folder")
        )
        (
            include.add("first_line_is_header")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "excel" in str(self.file_format.value)
                    )
                    or ("excel" in str(self.file_format))
                )
            )
            else exclude.add("first_line_is_header")
        )
        (
            include.add("json_path")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "json")
                    or (self.file_format == "json")
                )
            )
            else exclude.add("json_path")
        )
        (
            include.add("first_line")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "excel" in str(self.file_format.value)
                    )
                    or ("excel" in str(self.file_format))
                )
            )
            else exclude.add("first_line")
        )
        (
            include.add("ds_file_format_delimited_syntax_field_delimiter")
            if (self.ds_file_format and "0" in str(self.ds_file_format))
            else exclude.add("ds_file_format_delimited_syntax_field_delimiter")
        )
        (
            include.add("ds_file_format_delimited_syntax_record_def")
            if (
                self.ds_file_format
                and "0" in str(self.ds_file_format)
                and self.ds_file_format
                and "1" in str(self.ds_file_format)
                and self.ds_file_format
                and "2" in str(self.ds_file_format)
            )
            else exclude.add("ds_file_format_delimited_syntax_record_def")
        )
        (
            include.add("file_name")
            if (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            or (
                (
                    (
                        self.ds_read_mode
                        and "0" in str(self.ds_read_mode)
                        or self.ds_read_mode
                        and "1" in str(self.ds_read_mode)
                        or self.ds_read_mode
                        and "3" in str(self.ds_read_mode)
                    )
                    or (not self.ds_read_mode)
                )
                and (
                    (
                        self.table_format
                        and (
                            (hasattr(self.table_format, "value") and not self.table_format.value)
                            or (not self.table_format)
                        )
                    )
                    or (
                        self.table_format
                        and (
                            (hasattr(self.table_format, "value") and self.table_format.value == "file")
                            or (self.table_format == "file")
                        )
                    )
                )
            )
            else exclude.add("file_name")
        )
        (
            include.add("row_delimiter_value")
            if (
                self.row_delimiter
                and (
                    (
                        hasattr(self.row_delimiter, "value")
                        and self.row_delimiter.value
                        and "<?>" in str(self.row_delimiter.value)
                    )
                    or ("<?>" in str(self.row_delimiter))
                )
            )
            else exclude.add("row_delimiter_value")
        )
        (
            include.add("escape_character_value")
            if (
                self.escape_character
                and (
                    (
                        hasattr(self.escape_character, "value")
                        and self.escape_character.value
                        and "<?>" in str(self.escape_character.value)
                    )
                    or ("<?>" in str(self.escape_character))
                )
            )
            else exclude.add("escape_character_value")
        )
        (
            include.add("ds_file_format")
            if (
                self.ds_read_mode
                and "0" in str(self.ds_read_mode)
                or self.ds_read_mode
                and "1" in str(self.ds_read_mode)
            )
            else exclude.add("ds_file_format")
        )
        (
            include.add("date_format")
            if (
                (
                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "avro" in str(self.file_format.value)
                        )
                        or ("avro" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "parquet" in str(self.file_format.value)
                        )
                        or ("parquet" in str(self.file_format))
                    )
                )
                and (not self.output_avro_as_json)
            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "2" in str(self.ds_file_format)

            )
            else exclude.add("date_format")
        )
        (
            include.add("xml_path")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "xml")
                    or (self.file_format == "xml")
                )
            )
            else exclude.add("xml_path")
        )
        (
            include.add("fields_xml_path")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "xml")
                    or (self.file_format == "xml")
                )
            )
            and (self.xml_path)
            else exclude.add("fields_xml_path")
        )
        (
            include.add("labels_as_names")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                    or (self.file_format == "sav")
                )
            )
            else exclude.add("labels_as_names")
        )
        (
            include.add("null_value")
            if (

                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )

            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "2" in str(self.ds_file_format)

            )
            else exclude.add("null_value")
        )
        (
            include.add("timestamp_format")
            if (
                (
                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "avro" in str(self.file_format.value)
                        )
                        or ("avro" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "parquet" in str(self.file_format.value)
                        )
                        or ("parquet" in str(self.file_format))
                    )
                )
                and (not self.output_avro_as_json)
            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "2" in str(self.ds_file_format)

            )
            else exclude.add("timestamp_format")
        )
        (
            include.add("worksheet_name")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                    or (self.file_format == "excel")
                )
            )
            else exclude.add("worksheet_name")
        )
        (
            include.add("infer_record_count")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "excel" in str(self.file_format.value)
                    )
                    or ("excel" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "json" in str(self.file_format.value)
                    )
                    or ("json" in str(self.file_format))
                )
            )
            and (self.infer_schema == "true" or self.infer_schema)
            else exclude.add("infer_record_count")
        )
        (
            include.add("ds_reject_mode")
            if (
                self.ds_file_format
                and "0" in str(self.ds_file_format)
                and self.ds_file_format
                and "1" in str(self.ds_file_format)
                and self.ds_file_format
                and "2" in str(self.ds_file_format)
            )
            else exclude.add("ds_reject_mode")
        )
        (
            include.add("encoding")
            if (

                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "shp" in str(self.file_format.value)
                        )
                        or ("shp" in str(self.file_format))
                    )

            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)

            )
            else exclude.add("encoding")
        )
        (
            include.add("row_limit")
            if (not self.ds_read_mode)
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "2" in str(self.ds_file_format)

            )
            else exclude.add("row_limit")
        )
        (
            include.add("infer_as_varchar")
            if (
                (
                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                )
                or (self.infer_schema == "true" or self.infer_schema)
                or (self.type_mapping == "false" or not self.type_mapping)
            )
            and (self.infer_schema == "true" or self.infer_schema)
            else exclude.add("infer_as_varchar")
        )
        (
            include.add("ds_file_format_delimited_syntax_trace_file")
            if (
                self.ds_file_format
                and "0" in str(self.ds_file_format)
                and self.ds_file_format
                and "1" in str(self.ds_file_format)
                and self.ds_file_format
                and "2" in str(self.ds_file_format)
            )
            else exclude.add("ds_file_format_delimited_syntax_trace_file")
        )
        (
            include.add("invalid_data_handling")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
            )
            else exclude.add("invalid_data_handling")
        )
        (
            include.add("ds_file_format_avro_source_output_j_s_o_n")
            if (self.ds_file_format and "4" in str(self.ds_file_format))
            else exclude.add("ds_file_format_avro_source_output_j_s_o_n")
        )
        (
            include.add("infer_timestamp_as_date")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                    or (self.file_format == "sav")
                )
            )
            else exclude.add("infer_timestamp_as_date")
        )
        (
            include.add("schema_of_xml")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "xml")
                    or (self.file_format == "xml")
                )
            )
            and (self.infer_schema == "true" or self.infer_schema)
            else exclude.add("schema_of_xml")
        )
        (
            include.add("cell_range")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                    or (self.file_format == "excel")
                )
            )
            else exclude.add("cell_range")
        )
        include.add("table_name") if (self.endpoint_folder) else exclude.add("table_name")
        (
            include.add("ds_first_line_header")
            if (
                self.ds_file_format_delimited_syntax_record_def
                and "0" in str(self.ds_file_format_delimited_syntax_record_def)
                and self.ds_file_format_delimited_syntax_record_def
                and "2" in str(self.ds_file_format_delimited_syntax_record_def)
                and self.ds_file_format_delimited_syntax_record_def
                and "3" in str(self.ds_file_format_delimited_syntax_record_def)
                and self.ds_file_format_delimited_syntax_record_def
                and "4" in str(self.ds_file_format_delimited_syntax_record_def)
            )
            else exclude.add("ds_first_line_header")
        )
        (
            include.add("use_field_formats")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                    or (self.file_format == "sav")
                )
            )
            else exclude.add("use_field_formats")
        )
        (
            include.add("field_delimiter")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
            )
            else exclude.add("field_delimiter")
        )
        (
            include.add("decimal_rounding_mode")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
            )
            else exclude.add("decimal_rounding_mode")
        )
        (
            include.add("field_delimiter_value")
            if (
                self.field_delimiter
                and (
                    (
                        hasattr(self.field_delimiter, "value")
                        and self.field_delimiter.value
                        and "<?>" in str(self.field_delimiter.value)
                    )
                    or ("<?>" in str(self.field_delimiter))
                )
            )
            else exclude.add("field_delimiter_value")
        )
        (
            include.add("row_delimiter")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
            )
            else exclude.add("row_delimiter")
        )
        (
            include.add("quote_character")
            if (

                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )

            )
            or (self.ds_file_format and "0" in str(self.ds_file_format))
            else exclude.add("quote_character")
        )
        (
            include.add("ds_file_format_parquet_source")
            if (self.ds_file_format and "6" in str(self.ds_file_format))
            else exclude.add("ds_file_format_parquet_source")
        )
        (
            include.add("type_mapping")
            if (
                (
                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                )
                or (self.infer_schema == "true" or self.infer_schema)
            )
            and (self.infer_schema == "true" or self.infer_schema)
            else exclude.add("type_mapping")
        )
        (
            include.add("ds_file_format_o_r_c_source_temp_staging_area")
            if (self.ds_file_format and "7" in str(self.ds_file_format))
            else exclude.add("ds_file_format_o_r_c_source_temp_staging_area")
        )
        (
            include.add("decimal_format")
            if (
                (
                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "avro" in str(self.file_format.value)
                        )
                        or ("avro" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "parquet" in str(self.file_format.value)
                        )
                        or ("parquet" in str(self.file_format))
                    )
                )
                and (not self.output_avro_as_json)
            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "2" in str(self.ds_file_format)

            )
            else exclude.add("decimal_format")
        )
        (
            include.add("decimal_grouping_separator")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "avro" in str(self.file_format.value)
                    )
                    or ("avro" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "parquet" in str(self.file_format.value)
                    )
                    or ("parquet" in str(self.file_format))
                )
            )
            and (not self.output_avro_as_json)
            else exclude.add("decimal_grouping_separator")
        )
        (
            include.add("store_shared_strings_in_the_temporary_file")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "excel" in str(self.file_format.value)
                    )
                    or ("excel" in str(self.file_format))
                )
            )
            else exclude.add("store_shared_strings_in_the_temporary_file")
        )
        (
            include.add("escape_character")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
            )
            else exclude.add("escape_character")
        )
        (
            include.add("decimal_separator")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "avro" in str(self.file_format.value)
                    )
                    or ("avro" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "parquet" in str(self.file_format.value)
                    )
                    or ("parquet" in str(self.file_format))
                )
            )
            and (not self.output_avro_as_json)
            else exclude.add("decimal_separator")
        )
        (
            include.add("ds_file_format_delimited_syntax_data_format")
            if (self.ds_file_format and "0" in str(self.ds_file_format))
            else exclude.add("ds_file_format_delimited_syntax_data_format")
        )
        (
            include.add("encryption_key")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                    or (self.file_format == "sav")
                )
            )
            else exclude.add("encryption_key")
        )
        (
            include.add("quote_numeric_values")
            if (
                self.ds_file_format_delimited_syntax_data_format
                and "1" in str(self.ds_file_format_delimited_syntax_data_format)
            )
            else exclude.add("quote_numeric_values")
        )
        (
            include.add("ds_file_format_delimited_syntax_escape")
            if (self.ds_file_format and "0" in str(self.ds_file_format))
            else exclude.add("ds_file_format_delimited_syntax_escape")
        )
        (
            include.add("ds_file_format_parquet_source_temp_staging_area")
            if (self.ds_file_format and "6" in str(self.ds_file_format))
            else exclude.add("ds_file_format_parquet_source_temp_staging_area")
        )
        (
            include.add("read_a_file_to_a_row")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value == "read_raw_multiple_wildcard")
                    or (self.read_mode == "read_raw_multiple_wildcard")
                )
            )
            else exclude.add("read_a_file_to_a_row")
        )
        (
            include.add("ds_recurse")
            if (
                self.ds_read_mode
                and "1" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "3" in str(self.ds_read_mode)
            )
            else exclude.add("ds_recurse")
        )
        (
            include.add("file_format")
            if (

                    self.read_mode
                    and (
                        (
                            hasattr(self.read_mode, "value")
                            and self.read_mode.value
                            and "read_multiple_regex" in str(self.read_mode.value)
                        )
                        or ("read_multiple_regex" in str(self.read_mode))
                    )
                    or self.read_mode
                    and (
                        (
                            hasattr(self.read_mode, "value")
                            and self.read_mode.value
                            and "read_multiple_wildcard" in str(self.read_mode.value)
                        )
                        or ("read_multiple_wildcard" in str(self.read_mode))
                    )
                    or self.read_mode
                    and (
                        (
                            hasattr(self.read_mode, "value")
                            and self.read_mode.value
                            and "read_single" in str(self.read_mode.value)
                        )
                        or ("read_single" in str(self.read_mode))
                    )

            )
            and (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            else exclude.add("file_format")
        )
        (
            include.add("table_format")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value == "read_single")
                    or (self.read_mode == "read_single")
                )
            )
            else exclude.add("table_format")
        )
        (
            include.add("exclude_missing_values")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                    or (self.file_format == "sav")
                )
            )
            and (self.display_value_labels != "true" or not self.display_value_labels)
            else exclude.add("exclude_missing_values")
        )
        (
            include.add("json_infer_record_count")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "json")
                    or (self.file_format == "json")
                )
            )
            else exclude.add("json_infer_record_count")
        )
        (
            include.add("output_avro_as_json")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                    or (self.file_format == "avro")
                )
            )
            else exclude.add("output_avro_as_json")
        )
        (
            include.add("use_variable_formats")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "sas")
                    or (self.file_format == "sas")
                )
            )
            and (self.infer_schema != "true" or not self.infer_schema)
            else exclude.add("use_variable_formats")
        )
        (
            include.add("display_value_labels")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                    or (self.file_format == "sav")
                )
            )
            and (self.exclude_missing_values != "true" or not self.exclude_missing_values)
            else exclude.add("display_value_labels")
        )
        (
            include.add("ds_exclude_files")
            if (self.ds_read_mode and "1" in str(self.ds_read_mode))
            else exclude.add("ds_exclude_files")
        )
        (
            include.add("ds_file_format_delimited_syntax_record_def_record_def_source")
            if (
                self.ds_file_format_delimited_syntax_record_def
                and "2" in str(self.ds_file_format_delimited_syntax_record_def)
                and self.ds_file_format_delimited_syntax_record_def
                and "3" in str(self.ds_file_format_delimited_syntax_record_def)
                and self.ds_file_format_delimited_syntax_record_def
                and "4" in str(self.ds_file_format_delimited_syntax_record_def)
            )
            else exclude.add("ds_file_format_delimited_syntax_record_def_record_def_source")
        )
        (
            include.add("table_namespace")
            if (
                self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "iceberg" in str(self.table_format.value)
                    )
                    or ("iceberg" in str(self.table_format))
                )
            )
            and (self.endpoint_folder)
            else exclude.add("table_namespace")
        )
        (
            include.add("ds_file_format_avro_source")
            if (self.ds_file_format and "4" in str(self.ds_file_format))
            else exclude.add("ds_file_format_avro_source")
        )
        (
            include.add("bucket")
            if (
                self.ds_read_mode
                and "0" in str(self.ds_read_mode)
                or self.ds_read_mode
                and "1" in str(self.ds_read_mode)
                or self.ds_read_mode
                and "3" in str(self.ds_read_mode)
            )
            or (not self.ds_read_mode)
            else exclude.add("bucket")
        )
        (
            include.add("use_4_digit_years_in_date_formats")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "excel" in str(self.file_format.value)
                    )
                    or ("excel" in str(self.file_format))
                )
            )
            else exclude.add("use_4_digit_years_in_date_formats")
        )
        (
            include.add("infer_null_as_empty_string")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "excel" in str(self.file_format.value)
                    )
                    or ("excel" in str(self.file_format))
                )
            )
            else exclude.add("infer_null_as_empty_string")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("ds_file_format_parquet_target")
            if (self.ds_file_format == "6")
            else exclude.add("ds_file_format_parquet_target")
        )
        (
            include.add("file_size_threshold")
            if (((self.append_unique_identifier)) or (not self.ds_write_mode))
            else exclude.add("file_size_threshold")
        )
        (
            include.add("ds_file_format_parquet_target_parquet_compress")
            if (self.ds_file_format == "6")
            else exclude.add("ds_file_format_parquet_target_parquet_compress")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_expiration_expiration_date")
            if (
                ((self.ds_file_attributes_life_cycle_rule_expiration))
                and (self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "1")
            )
            else exclude.add("ds_file_attributes_life_cycle_rule_expiration_expiration_date")
        )
        include.add("ds_log_interval") if (self.ds_write_mode == "0") else exclude.add("ds_log_interval")
        (
            include.add("quote_character")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                    )
                )
                or (self.ds_file_format == "0")
            )
            else exclude.add("quote_character")
        )
        (
            include.add("ds_file_format_o_r_c_target_temp_staging_area")
            if (self.ds_file_format == "7")
            else exclude.add("ds_file_format_o_r_c_target_temp_staging_area")
        )
        (
            include.add("ds_file_attributes_content_type")
            if (self.ds_write_mode == "0")
            else exclude.add("ds_file_attributes_content_type")
        )
        (
            include.add("ds_file_format_avrotarget_avro_schema")
            if (self.ds_file_format_avrotarget_use_schema)
            else exclude.add("ds_file_format_avrotarget_avro_schema")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_expiration_expiration_duration")
            if (
                ((self.ds_file_attributes_life_cycle_rule_expiration))
                and (self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "0")
            )
            else exclude.add("ds_file_attributes_life_cycle_rule_expiration_expiration_duration")
        )
        (
            include.add("delete_bucket")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                            or (self.write_mode == "delete")
                        )


            )
            else exclude.add("delete_bucket")
        )
        (
            include.add("time_format")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                    or (self.file_format == "parquet")
                                )
                            )
                        )
                    )
                )
                or (
                    ((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2")
                )
            )
            else exclude.add("time_format")
        )
        (
            include.add("append_unique_identifier")
            if ((((self.ds_write_mode == "0"))) or (not self.ds_write_mode))
            else exclude.add("append_unique_identifier")
        )
        (
            include.add("encoding")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                    )
                )
                or (((self.ds_file_format == "0")) or (self.ds_file_format == "1"))
            )
            else exclude.add("encoding")
        )
        (
            include.add("timestamp_format")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                    or (self.file_format == "parquet")
                                )
                            )
                        )
                    )
                )
                or (
                    ((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2")
                )
            )
            else exclude.add("timestamp_format")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_l_c_rule_scope")
            if (self.ds_file_attributes_life_cycle_rule)
            else exclude.add("ds_file_attributes_life_cycle_rule_l_c_rule_scope")
        )
        (
            include.add("ds_file_exists")
            if ((((self.ds_write_mode == "0"))) and (not self.append_unique_identifier))
            else exclude.add("ds_file_exists")
        )
        (
            include.add("ds_file_format_o_r_c_target_orc_stripe_size")
            if (self.ds_file_format == "7")
            else exclude.add("ds_file_format_o_r_c_target_orc_stripe_size")
        )
        (
            include.add("ds_file_format_o_r_c_target_orc_compress")
            if (self.ds_file_format == "7")
            else exclude.add("ds_file_format_o_r_c_target_orc_compress")
        )
        (
            include.add("worksheet_name")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                or (self.file_format == "excel")
                            )
                        )
                    )
                )
                and (

                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )

                        )

                )
            )
            else exclude.add("worksheet_name")
        )
        (
            include.add("ds_file_format_o_r_c_target_orc_buffer_size")
            if (self.ds_file_format == "7")
            else exclude.add("ds_file_format_o_r_c_target_orc_buffer_size")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_l_c_rule_format")
            if (self.ds_file_attributes_life_cycle_rule)
            else exclude.add("ds_file_attributes_life_cycle_rule_l_c_rule_format")
        )
        (
            include.add("table_format")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                            or (self.write_mode == "write")
                        )


            )
            else exclude.add("table_format")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_transition_transition_duration")
            if (
                ((self.ds_file_attributes_life_cycle_rule_transition))
                and (self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "0")
            )
            else exclude.add("ds_file_attributes_life_cycle_rule_transition_transition_duration")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_transition_transition_date")
            if (
                ((self.ds_file_attributes_life_cycle_rule_transition))
                and (self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "1")
            )
            else exclude.add("ds_file_attributes_life_cycle_rule_transition_transition_date")
        )
        include.add("ds_thread_count") if (self.ds_write_mode == "0") else exclude.add("ds_thread_count")
        (
            include.add("ds_file_attributes_life_cycle_rule_transition")
            if (self.ds_file_attributes_life_cycle_rule)
            else exclude.add("ds_file_attributes_life_cycle_rule_transition")
        )
        include.add("ds_codec_avro") if (self.ds_file_format == "4") else exclude.add("ds_codec_avro")
        (
            include.add("ds_file_format_avrotarget")
            if (self.ds_file_format == "4")
            else exclude.add("ds_file_format_avrotarget")
        )
        include.add("ds_file_attributes") if (self.ds_write_mode == "0") else exclude.add("ds_file_attributes")
        (
            include.add("ds_file_attributes_life_cycle_rule_expiration")
            if (self.ds_file_attributes_life_cycle_rule)
            else exclude.add("ds_file_attributes_life_cycle_rule_expiration")
        )
        (
            include.add("ds_file_attributes_user_metadata")
            if (self.ds_write_mode == "0")
            else exclude.add("ds_file_attributes_user_metadata")
        )
        (
            include.add("ds_file_attributes_storage_class")
            if (self.ds_write_mode == "0")
            else exclude.add("ds_file_attributes_storage_class")
        )
        (
            include.add("ds_file_format_parquet_target_parquet_page_size")
            if (self.ds_file_format == "6")
            else exclude.add("ds_file_format_parquet_target_parquet_page_size")
        )
        (
            include.add("ds_file_format_delimited_syntax_encoding_output_b_o_m")
            if (((self.ds_file_format == "0")) or (self.ds_file_format == "1"))
            else exclude.add("ds_file_format_delimited_syntax_encoding_output_b_o_m")
        )
        (
            include.add("ds_file_format_avrotarget_avro_array_keys")
            if (self.ds_file_format_avrotarget_use_schema)
            else exclude.add("ds_file_format_avrotarget_avro_array_keys")
        )
        (
            include.add("ds_create_bucket_append_u_u_i_d")
            if (self.create_bucket)
            else exclude.add("ds_create_bucket_append_u_u_i_d")
        )
        (
            include.add("ds_file_format_parquet_target_parquet_block_size")
            if (self.ds_file_format == "6")
            else exclude.add("ds_file_format_parquet_target_parquet_block_size")
        )
        (
            include.add("quote_numeric_values")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                    )
                )
                or (self.ds_file_format_delimited_syntax_data_format == "1")
            )
            else exclude.add("quote_numeric_values")
        )
        (
            include.add("file_name")
            if (
                (
                    (
                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )
                            )
                        )
                    )
                )
                or (
                    ((((self.ds_write_mode == "0"))) or ((not self.ds_write_mode)))
                    and (
                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and not self.table_format.value)
                                    or (not self.table_format)
                                )
                            )
                        )
                        or (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value == "file")
                                    or (self.table_format == "file")
                                )

                        )
                    )
                )
            )
            else exclude.add("file_name")
        )
        (
            include.add("ds_file_format_avrotarget_input_j_s_o_n")
            if (self.ds_file_format_avrotarget_use_schema)
            else exclude.add("ds_file_format_avrotarget_input_j_s_o_n")
        )
        (
            include.add("ds_file_attributes_encryption")
            if (self.ds_write_mode == "0")
            else exclude.add("ds_file_attributes_encryption")
        )
        (
            include.add("ds_file_format_avrotarget_use_schema")
            if (self.ds_file_format == "4")
            else exclude.add("ds_file_format_avrotarget_use_schema")
        )
        (
            include.add("include_types")
            if (
                (
                    ((self.first_line_is_header))
                    and (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                    or (self.file_format == "excel")
                                )
                            )
                        )
                    )
                )
                or (self.ds_first_line_header)
            )
            else exclude.add("include_types")
        )
        include.add("ds_file_format") if (self.ds_write_mode == "0") else exclude.add("ds_file_format")
        (
            include.add("ds_file_format_parquet_target_temp_staging_area")
            if (self.ds_file_format == "6")
            else exclude.add("ds_file_format_parquet_target_temp_staging_area")
        )
        (
            include.add("ds_first_line_header")
            if (((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2"))
            else exclude.add("ds_first_line_header")
        )
        (
            include.add("decimal_format")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                    or (self.file_format == "parquet")
                                )
                            )
                        )
                    )
                )
                or (
                    ((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2")
                )
            )
            else exclude.add("decimal_format")
        )
        (
            include.add("create_bucket")
            if (
                (
                    (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                                    or (self.write_mode == "write")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "write_raw")
                                    or (self.write_mode == "write_raw")
                                )
                            )
                        )
                    )
                )
                or (self.ds_write_mode == "0")
            )
            else exclude.add("create_bucket")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule")
            if (self.ds_write_mode == "0")
            else exclude.add("ds_file_attributes_life_cycle_rule")
        )
        (
            include.add("date_format")
            if (
                (
                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                    or (self.file_format == "parquet")
                                )
                            )
                        )
                    )
                )
                or (
                    ((self.ds_file_format == "0")) or (self.ds_file_format == "1") or (self.ds_file_format == "2")
                )
            )
            else exclude.add("date_format")
        )
        (
            include.add("decimal_separator")
            if (

                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                or (self.file_format == "avro")
                            )
                        )
                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )

                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )

                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                or (self.file_format == "parquet")
                            )

                    )

            )
            else exclude.add("decimal_separator")
        )
        (
            include.add("partition_name_prefix")
            if (

                    (
                        (
                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                or (self.table_format != "deltalake")
                            )
                        )
                    )
                    and (

                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                or (self.table_format != "iceberg")
                            )

                    )

            )
            else exclude.add("partition_name_prefix")
        )
        (
            include.add("codec_parquet")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                or (self.file_format == "parquet")
                            )
                        )
                    )
                    or (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and not self.file_format.value)
                                    or (not self.file_format)
                                )
                            )
                        )
                        and ((re.match(r".*\.parquet$", self.file_name)))
                    )
                )
                and (

                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )

                        )

                )
            )
            else exclude.add("codec_parquet")
        )
        (
            include.add("the_data_path")
            if (



                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                                or (self.table_format == "iceberg")
                            )



            )
            else exclude.add("the_data_path")
        )
        (
            include.add("codec_avro")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                or (self.file_format == "avro")
                            )
                        )
                    )
                    or (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and not self.file_format.value)
                                    or (not self.file_format)
                                )
                            )
                        )
                        and ((re.match(r".*\.avro$", self.file_name)))
                    )
                )
                and (

                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )

                        )

                )
            )
            else exclude.add("codec_avro")
        )
        (
            include.add("escape_character")
            if (



                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )



            )
            else exclude.add("escape_character")
        )
        (
            include.add("codec_delimited")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                )
                and (

                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )

                        )

                )
            )
            else exclude.add("codec_delimited")
        )
        (
            include.add("table_data_file_compression_codec")
            if (
                (
                    (
                        (
                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value == "deltalake")
                                or (self.table_format == "deltalake")
                            )
                        )
                    )
                    or (
                        (
                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                                or (self.table_format == "iceberg")
                            )
                        )
                    )
                )
                and (

                        self.table_data_file_format
                        and (
                            (hasattr(self.table_data_file_format, "value") and self.table_data_file_format.value)
                            or (self.table_data_file_format)
                        )

                )
                and (self.endpoint_folder)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                            or (self.write_mode == "write")
                        )

                )
            )
            else exclude.add("table_data_file_compression_codec")
        )
        (
            include.add("codec_orc")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "orc")
                                or (self.file_format == "orc")
                            )
                        )
                    )
                    or (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and not self.file_format.value)
                                    or (not self.file_format)
                                )
                            )
                        )
                        and ((re.match(r".*\.orc$", self.file_name)))
                    )
                )
                and (

                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )

                        )

                )
            )
            else exclude.add("codec_orc")
        )
        (
            include.add("decimal_grouping_separator")
            if (

                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                or (self.file_format == "avro")
                            )
                        )
                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )

                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )

                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                or (self.file_format == "parquet")
                            )

                    )

            )
            else exclude.add("decimal_grouping_separator")
        )
        (
            include.add("encryption_key")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                                or (self.file_format == "sav")
                            )
                        )
                    )
                    or (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and not self.file_format.value)
                                    or (not self.file_format)
                                )
                            )
                        )
                        and ((re.match(r".*\.sav$", self.file_name)))
                    )
                )
                and (

                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )

                        )

                )
            )
            else exclude.add("encryption_key")
        )
        (
            include.add("table_data_file_format")
            if (
                (
                    (
                        (
                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value == "deltalake")
                                or (self.table_format == "deltalake")
                            )
                        )
                    )
                    or (
                        (
                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                                or (self.table_format == "iceberg")
                            )
                        )
                    )
                )
                and (self.endpoint_folder)
            )
            else exclude.add("table_data_file_format")
        )
        include.add("the_partition_columns") if (self.endpoint_folder) else exclude.add("the_partition_columns")
        (
            include.add("partitioned")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                            or (self.write_mode == "write")
                        )
                    )
                )
                and (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (

                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )

                    )
                )
            )
            else exclude.add("partitioned")
        )
        (
            include.add("codec_csv")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                            or (self.file_format == "csv")
                        )


            )
            else exclude.add("codec_csv")
        )
        (
            include.add("file_format")
            if (
                (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                                or (self.write_mode == "write")
                            )
                        )
                    )
                )
                and (

                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )

                        )

                )
            )
            else exclude.add("file_format")
        )
        (
            include.add("table_action")
            if (

                    (
                        (
                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value == "deltalake")
                                or (self.table_format == "deltalake")
                            )
                        )
                    )
                    or (

                            self.table_format
                            and (
                                (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                                or (self.table_format == "iceberg")
                            )

                    )

            )
            else exclude.add("table_action")
        )
        (
            include.add("names_as_labels")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                                or (self.file_format == "sav")
                            )
                        )
                    )
                    or (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and not self.file_format.value)
                                    or (not self.file_format)
                                )
                            )
                        )
                        and ((re.match(r".*\.sav$", self.file_name)))
                    )
                )
                and (

                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                    or (self.table_format != "deltalake")
                                )
                            )
                        )
                        and (

                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                    or (self.table_format != "iceberg")
                                )

                        )

                )
            )
            else exclude.add("names_as_labels")
        )
        (
            include.add("decimal_separator")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                    or (self.file_format == "parquet")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("decimal_separator")
        )
        (
            include.add("partition_name_prefix")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value != "deltalake"
                                            )
                                            or (self.table_format != "deltalake")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value
                                                and "#" in str(self.table_format.value)
                                            )
                                            or ("#" in str(self.table_format))
                                        )
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value != "iceberg"
                                            )
                                            or (self.table_format != "iceberg")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value
                                                and "#" in str(self.table_format.value)
                                            )
                                            or ("#" in str(self.table_format))
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("partition_name_prefix")
        )
        (
            include.add("codec_parquet")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                            or (self.file_format == "parquet")
                                        )
                                    )
                                )
                                or (
                                    (
                                        (
                                            (
                                                (
                                                    self.file_format
                                                    and (
                                                        (
                                                            hasattr(self.file_format, "value")
                                                            and not self.file_format.value
                                                        )
                                                        or (not self.file_format)
                                                    )
                                                )
                                            )
                                            or (
                                                (
                                                    self.file_format
                                                    and (
                                                        (
                                                            hasattr(self.file_format, "value")
                                                            and self.file_format.value
                                                            and "#" in str(self.file_format.value)
                                                        )
                                                        or ("#" in str(self.file_format))
                                                    )
                                                )
                                            )
                                        )
                                        and (
                                            ((re.match(r".*\.parquet$", self.file_name)))
                                            or ((self.file_name and "#" in str(self.file_name)))
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "deltalake"
                                                    )
                                                    or (self.table_format != "deltalake")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
                                                )
                                            )
                                        )
                                    )
                                    and (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "iceberg"
                                                    )
                                                    or (self.table_format != "iceberg")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
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
            else exclude.add("codec_parquet")
        )
        (
            include.add("the_data_path")
            if (

                    (
                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                                    or (self.table_format == "iceberg")
                                )
                            )
                        )
                        or (
                            (
                                self.table_format
                                and (
                                    (
                                        hasattr(self.table_format, "value")
                                        and self.table_format.value
                                        and "#" in str(self.table_format.value)
                                    )
                                    or ("#" in str(self.table_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("the_data_path")
        )
        (
            include.add("ds_file_format_parquet_target")
            if (

                    (((((self.ds_file_format == "6")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_parquet_target")
        )
        (
            include.add("codec_avro")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                            or (self.file_format == "avro")
                                        )
                                    )
                                )
                                or (
                                    (
                                        (
                                            (
                                                (
                                                    self.file_format
                                                    and (
                                                        (
                                                            hasattr(self.file_format, "value")
                                                            and not self.file_format.value
                                                        )
                                                        or (not self.file_format)
                                                    )
                                                )
                                            )
                                            or (
                                                (
                                                    self.file_format
                                                    and (
                                                        (
                                                            hasattr(self.file_format, "value")
                                                            and self.file_format.value
                                                            and "#" in str(self.file_format.value)
                                                        )
                                                        or ("#" in str(self.file_format))
                                                    )
                                                )
                                            )
                                        )
                                        and (
                                            ((re.match(r".*\.avro$", self.file_name)))
                                            or ((self.file_name and "#" in str(self.file_name)))
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "deltalake"
                                                    )
                                                    or (self.table_format != "deltalake")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
                                                )
                                            )
                                        )
                                    )
                                    and (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "iceberg"
                                                    )
                                                    or (self.table_format != "iceberg")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
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
            else exclude.add("codec_avro")
        )
        (
            include.add("file_size_threshold")
            if (
                ((self.append_unique_identifier))
                or (not self.ds_write_mode)
                or (self.append_unique_identifier and "#" in str(self.append_unique_identifier))
                or (self.ds_write_mode and "#" in str(self.ds_write_mode))
            )
            else exclude.add("file_size_threshold")
        )
        (
            include.add("ds_file_format_parquet_target_parquet_compress")
            if (

                    (((((self.ds_file_format == "6")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_parquet_target_parquet_compress")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_expiration_expiration_date")
            if (

                    (
                        (
                            (
                                ((self.ds_file_attributes_life_cycle_rule_expiration))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule_expiration
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule_expiration)
                                    )
                                )
                            )
                            and (
                                ((self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "1"))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule_l_c_rule_format
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule_l_c_rule_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_life_cycle_rule_expiration_expiration_date")
        )
        (
            include.add("ds_log_interval")
            if (

                    (((((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_log_interval")
        )
        (
            include.add("quote_character")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (
                                    hasattr(self.file_format, "value")
                                    and self.file_format.value
                                    and "#" in str(self.file_format.value)
                                )
                                or ("#" in str(self.file_format))
                            )
                        )
                    )
                )
                or (((self.ds_file_format == "0")) or (self.ds_file_format and "#" in str(self.ds_file_format)))
            )
            else exclude.add("quote_character")
        )
        (
            include.add("ds_file_format_o_r_c_target_temp_staging_area")
            if (

                    (((((self.ds_file_format == "7")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_o_r_c_target_temp_staging_area")
        )
        (
            include.add("escape_character")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("escape_character")
        )
        (
            include.add("codec_delimited")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value == "delimited"
                                            )
                                            or (self.file_format == "delimited")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "deltalake"
                                                    )
                                                    or (self.table_format != "deltalake")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
                                                )
                                            )
                                        )
                                    )
                                    and (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "iceberg"
                                                    )
                                                    or (self.table_format != "iceberg")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
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
            else exclude.add("codec_delimited")
        )
        (
            include.add("ds_file_attributes_content_type")
            if (

                    (((((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_content_type")
        )
        (
            include.add("ds_file_format_avrotarget_avro_schema")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format_avrotarget_use_schema))
                                or (
                                    (
                                        self.ds_file_format_avrotarget_use_schema
                                        and "#" in str(self.ds_file_format_avrotarget_use_schema)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_avrotarget_avro_schema")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_expiration_expiration_duration")
            if (

                    (
                        (
                            (
                                ((self.ds_file_attributes_life_cycle_rule_expiration))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule_expiration
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule_expiration)
                                    )
                                )
                            )
                            and (
                                ((self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "0"))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule_l_c_rule_format
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule_l_c_rule_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_life_cycle_rule_expiration_expiration_duration")
        )
        (
            include.add("delete_bucket")
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
                            (
                                hasattr(self.write_mode, "value")
                                and self.write_mode.value
                                and "#" in str(self.write_mode.value)
                            )
                            or ("#" in str(self.write_mode))
                        )

                )
            )
            else exclude.add("delete_bucket")
        )
        (
            include.add("time_format")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                or (self.file_format == "avro")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                or (self.file_format == "parquet")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (
                                    hasattr(self.file_format, "value")
                                    and self.file_format.value
                                    and "#" in str(self.file_format.value)
                                )
                                or ("#" in str(self.file_format))
                            )
                        )
                    )
                )
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format == "2")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
            )
            else exclude.add("time_format")
        )
        (
            include.add("append_unique_identifier")
            if (
                (((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                or (not self.ds_write_mode)
                or (self.ds_write_mode and "#" in str(self.ds_write_mode))
            )
            else exclude.add("append_unique_identifier")
        )
        (
            include.add("encoding")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (
                                    hasattr(self.file_format, "value")
                                    and self.file_format.value
                                    and "#" in str(self.file_format.value)
                                )
                                or ("#" in str(self.file_format))
                            )
                        )
                    )
                )
                or (
                    ((self.ds_file_format == "0"))
                    or (self.ds_file_format == "1")
                    or (self.ds_file_format and "#" in str(self.ds_file_format))
                )
            )
            else exclude.add("encoding")
        )
        (
            include.add("table_data_file_compression_codec")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value == "deltalake"
                                            )
                                            or (self.table_format == "deltalake")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value == "iceberg"
                                            )
                                            or (self.table_format == "iceberg")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value
                                                and "#" in str(self.table_format.value)
                                            )
                                            or ("#" in str(self.table_format))
                                        )
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        self.table_data_file_format
                                        and (
                                            (
                                                hasattr(self.table_data_file_format, "value")
                                                and self.table_data_file_format.value
                                            )
                                            or (self.table_data_file_format)
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.table_data_file_format
                                        and (
                                            (
                                                hasattr(self.table_data_file_format, "value")
                                                and self.table_data_file_format.value
                                                and "#" in str(self.table_data_file_format.value)
                                            )
                                            or ("#" in str(self.table_data_file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                ((self.endpoint_folder))
                                or ((self.endpoint_folder and "#" in str(self.endpoint_folder)))
                            )
                            and (
                                (
                                    (
                                        self.write_mode
                                        and (
                                            (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                                            or (self.write_mode == "write")
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
            else exclude.add("table_data_file_compression_codec")
        )
        (
            include.add("timestamp_format")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                or (self.file_format == "avro")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                or (self.file_format == "parquet")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (
                                    hasattr(self.file_format, "value")
                                    and self.file_format.value
                                    and "#" in str(self.file_format.value)
                                )
                                or ("#" in str(self.file_format))
                            )
                        )
                    )
                )
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format == "2")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
            )
            else exclude.add("timestamp_format")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_l_c_rule_scope")
            if (

                    (
                        (
                            (
                                ((self.ds_file_attributes_life_cycle_rule))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_life_cycle_rule_l_c_rule_scope")
        )
        (
            include.add("ds_file_exists")
            if (

                    (
                        (
                            (((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                            and (
                                ((not self.append_unique_identifier))
                                or ((self.append_unique_identifier and "#" in str(self.append_unique_identifier)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_exists")
        )
        (
            include.add("codec_orc")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "orc")
                                            or (self.file_format == "orc")
                                        )
                                    )
                                )
                                or (
                                    (
                                        (
                                            (
                                                (
                                                    self.file_format
                                                    and (
                                                        (
                                                            hasattr(self.file_format, "value")
                                                            and not self.file_format.value
                                                        )
                                                        or (not self.file_format)
                                                    )
                                                )
                                            )
                                            or (
                                                (
                                                    self.file_format
                                                    and (
                                                        (
                                                            hasattr(self.file_format, "value")
                                                            and self.file_format.value
                                                            and "#" in str(self.file_format.value)
                                                        )
                                                        or ("#" in str(self.file_format))
                                                    )
                                                )
                                            )
                                        )
                                        and (
                                            ((re.match(r".*\.orc$", self.file_name)))
                                            or ((self.file_name and "#" in str(self.file_name)))
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "deltalake"
                                                    )
                                                    or (self.table_format != "deltalake")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
                                                )
                                            )
                                        )
                                    )
                                    and (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "iceberg"
                                                    )
                                                    or (self.table_format != "iceberg")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
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
            else exclude.add("codec_orc")
        )
        (
            include.add("ds_file_format_o_r_c_target_orc_stripe_size")
            if (

                    (((((self.ds_file_format == "7")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_o_r_c_target_orc_stripe_size")
        )
        (
            include.add("decimal_grouping_separator")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                    or (self.file_format == "avro")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                    or (self.file_format == "delimited")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                    or (self.file_format == "parquet")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("decimal_grouping_separator")
        )
        (
            include.add("encryption_key")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                                            or (self.file_format == "sav")
                                        )
                                    )
                                )
                                or (
                                    (
                                        (
                                            (
                                                (
                                                    self.file_format
                                                    and (
                                                        (
                                                            hasattr(self.file_format, "value")
                                                            and not self.file_format.value
                                                        )
                                                        or (not self.file_format)
                                                    )
                                                )
                                            )
                                            or (
                                                (
                                                    self.file_format
                                                    and (
                                                        (
                                                            hasattr(self.file_format, "value")
                                                            and self.file_format.value
                                                            and "#" in str(self.file_format.value)
                                                        )
                                                        or ("#" in str(self.file_format))
                                                    )
                                                )
                                            )
                                        )
                                        and (
                                            ((re.match(r".*\.sav$", self.file_name)))
                                            or ((self.file_name and "#" in str(self.file_name)))
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "deltalake"
                                                    )
                                                    or (self.table_format != "deltalake")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
                                                )
                                            )
                                        )
                                    )
                                    and (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "iceberg"
                                                    )
                                                    or (self.table_format != "iceberg")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
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
            else exclude.add("encryption_key")
        )
        (
            include.add("table_data_file_format")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value == "deltalake"
                                            )
                                            or (self.table_format == "deltalake")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value == "iceberg"
                                            )
                                            or (self.table_format == "iceberg")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value
                                                and "#" in str(self.table_format.value)
                                            )
                                            or ("#" in str(self.table_format))
                                        )
                                    )
                                )
                            )
                            and (
                                ((self.endpoint_folder))
                                or ((self.endpoint_folder and "#" in str(self.endpoint_folder)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("table_data_file_format")
        )
        (
            include.add("ds_file_format_o_r_c_target_orc_compress")
            if (

                    (((((self.ds_file_format == "7")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_o_r_c_target_orc_compress")
        )
        (
            include.add("worksheet_name")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                    or (self.file_format == "excel")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (

                            (
                                (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value != "deltalake"
                                            )
                                            or (self.table_format != "deltalake")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value
                                                and "#" in str(self.table_format.value)
                                            )
                                            or ("#" in str(self.table_format))
                                        )
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value != "iceberg"
                                            )
                                            or (self.table_format != "iceberg")
                                        )
                                    )
                                )
                                or (

                                        self.table_format
                                        and (
                                            (
                                                hasattr(self.table_format, "value")
                                                and self.table_format.value
                                                and "#" in str(self.table_format.value)
                                            )
                                            or ("#" in str(self.table_format))
                                        )

                                )
                            )

                    )

            )
            else exclude.add("worksheet_name")
        )
        (
            include.add("ds_file_format_o_r_c_target_orc_buffer_size")
            if (

                    (((((self.ds_file_format == "7")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_o_r_c_target_orc_buffer_size")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_l_c_rule_format")
            if (

                    (
                        (
                            (
                                ((self.ds_file_attributes_life_cycle_rule))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_life_cycle_rule_l_c_rule_format")
        )
        (
            include.add("table_format")
            if (
                (
                    (
                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                            or (self.write_mode == "write")
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
            else exclude.add("table_format")
        )
        (
            include.add("the_partition_columns")
            if (

                    (((self.endpoint_folder)) or ((self.endpoint_folder and "#" in str(self.endpoint_folder))))
                    and (not self.ds_use_datastage)

            )
            else exclude.add("the_partition_columns")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_transition_transition_duration")
            if (

                    (
                        (
                            (
                                ((self.ds_file_attributes_life_cycle_rule_transition))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule_transition
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule_transition)
                                    )
                                )
                            )
                            and (
                                ((self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "0"))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule_l_c_rule_format
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule_l_c_rule_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_life_cycle_rule_transition_transition_duration")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_transition_transition_date")
            if (

                    (
                        (
                            (
                                ((self.ds_file_attributes_life_cycle_rule_transition))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule_transition
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule_transition)
                                    )
                                )
                            )
                            and (
                                ((self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "1"))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule_l_c_rule_format
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule_l_c_rule_format)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_life_cycle_rule_transition_transition_date")
        )
        (
            include.add("ds_thread_count")
            if (

                    (((((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_thread_count")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_transition")
            if (

                    (
                        (
                            (
                                ((self.ds_file_attributes_life_cycle_rule))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_life_cycle_rule_transition")
        )
        (
            include.add("partitioned")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.write_mode
                                        and (
                                            (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                                            or (self.write_mode == "write")
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
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                            or (self.file_format == "csv")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value == "delimited"
                                            )
                                            or (self.file_format == "delimited")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("partitioned")
        )
        (
            include.add("ds_codec_avro")
            if (

                    (((self.ds_file_format == "4")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_codec_avro")
        )
        (
            include.add("ds_file_format_avrotarget")
            if (

                    (((((self.ds_file_format == "4")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_avrotarget")
        )
        (
            include.add("ds_file_attributes")
            if (

                    (((((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_expiration")
            if (

                    (
                        (
                            (
                                ((self.ds_file_attributes_life_cycle_rule))
                                or (
                                    (
                                        self.ds_file_attributes_life_cycle_rule
                                        and "#" in str(self.ds_file_attributes_life_cycle_rule)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_life_cycle_rule_expiration")
        )
        (
            include.add("ds_file_attributes_user_metadata")
            if (

                    (((((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_user_metadata")
        )
        (
            include.add("ds_file_attributes_storage_class")
            if (

                    (((((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_storage_class")
        )
        (
            include.add("codec_csv")
            if (

                    (
                        (
                            (
                                self.file_format
                                and (
                                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                    or (self.file_format == "csv")
                                )
                            )
                        )
                        or (
                            (
                                self.file_format
                                and (
                                    (
                                        hasattr(self.file_format, "value")
                                        and self.file_format.value
                                        and "#" in str(self.file_format.value)
                                    )
                                    or ("#" in str(self.file_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("codec_csv")
        )
        (
            include.add("ds_file_format_parquet_target_parquet_page_size")
            if (

                    (((((self.ds_file_format == "6")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_parquet_target_parquet_page_size")
        )
        (
            include.add("ds_file_format_delimited_syntax_encoding_output_b_o_m")
            if (

                    (
                        ((self.ds_file_format == "0"))
                        or ((self.ds_file_format == "1"))
                        or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_delimited_syntax_encoding_output_b_o_m")
        )
        (
            include.add("file_format")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.write_mode
                                        and (
                                            (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                                            or (self.write_mode == "write")
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
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "deltalake"
                                                    )
                                                    or (self.table_format != "deltalake")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
                                                )
                                            )
                                        )
                                    )
                                    and (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "iceberg"
                                                    )
                                                    or (self.table_format != "iceberg")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
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
            else exclude.add("file_format")
        )
        (
            include.add("table_action")
            if (

                    (
                        (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value == "deltalake")
                                    or (self.table_format == "deltalake")
                                )
                            )
                        )
                        or (
                            (
                                self.table_format
                                and (
                                    (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                                    or (self.table_format == "iceberg")
                                )
                            )
                        )
                        or (
                            (
                                self.table_format
                                and (
                                    (
                                        hasattr(self.table_format, "value")
                                        and self.table_format.value
                                        and "#" in str(self.table_format.value)
                                    )
                                    or ("#" in str(self.table_format))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("table_action")
        )
        (
            include.add("ds_file_format_avrotarget_avro_array_keys")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format_avrotarget_use_schema))
                                or (
                                    (
                                        self.ds_file_format_avrotarget_use_schema
                                        and "#" in str(self.ds_file_format_avrotarget_use_schema)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_avrotarget_avro_array_keys")
        )
        (
            include.add("ds_create_bucket_append_u_u_i_d")
            if (

                    (((((self.create_bucket)) or ((self.create_bucket and "#" in str(self.create_bucket))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_create_bucket_append_u_u_i_d")
        )
        (
            include.add("ds_file_format_parquet_target_parquet_block_size")
            if (

                    (((((self.ds_file_format == "6")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_parquet_target_parquet_block_size")
        )
        (
            include.add("quote_numeric_values")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (
                                    hasattr(self.file_format, "value")
                                    and self.file_format.value
                                    and "#" in str(self.file_format.value)
                                )
                                or ("#" in str(self.file_format))
                            )
                        )
                    )
                )
                or (


                            ((self.ds_file_format_delimited_syntax_data_format == "1"))
                            or (

                                    self.ds_file_format_delimited_syntax_data_format
                                    and "#" in str(self.ds_file_format_delimited_syntax_data_format)

                            )


                )
            )
            else exclude.add("quote_numeric_values")
        )
        (
            include.add("file_name")
            if (
                (
                    (
                        (
                            (
                                (
                                    self.table_format
                                    and (
                                        (hasattr(self.table_format, "value") and self.table_format.value != "deltalake")
                                        or (self.table_format != "deltalake")
                                    )
                                )
                            )
                            or (
                                (
                                    self.table_format
                                    and (
                                        (
                                            hasattr(self.table_format, "value")
                                            and self.table_format.value
                                            and "#" in str(self.table_format.value)
                                        )
                                        or ("#" in str(self.table_format))
                                    )
                                )
                            )
                        )
                        and (
                            (
                                (
                                    self.table_format
                                    and (
                                        (hasattr(self.table_format, "value") and self.table_format.value != "iceberg")
                                        or (self.table_format != "iceberg")
                                    )
                                )
                            )
                            or (
                                (
                                    self.table_format
                                    and (
                                        (
                                            hasattr(self.table_format, "value")
                                            and self.table_format.value
                                            and "#" in str(self.table_format.value)
                                        )
                                        or ("#" in str(self.table_format))
                                    )
                                )
                            )
                        )
                    )
                )
                or (

                        (
                            (((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                            or ((not self.ds_write_mode))
                            or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                        )
                        and (
                            (
                                (
                                    self.table_format
                                    and (
                                        (hasattr(self.table_format, "value") and not self.table_format.value)
                                        or (not self.table_format)
                                    )
                                )
                            )
                            or (

                                    self.table_format
                                    and (
                                        (hasattr(self.table_format, "value") and self.table_format.value == "file")
                                        or (self.table_format == "file")
                                    )

                            )
                            or (

                                    self.table_format
                                    and (
                                        (
                                            hasattr(self.table_format, "value")
                                            and self.table_format.value
                                            and "#" in str(self.table_format.value)
                                        )
                                        or ("#" in str(self.table_format))
                                    )

                            )
                        )

                )
            )
            else exclude.add("file_name")
        )
        (
            include.add("ds_file_format_avrotarget_input_j_s_o_n")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format_avrotarget_use_schema))
                                or (
                                    (
                                        self.ds_file_format_avrotarget_use_schema
                                        and "#" in str(self.ds_file_format_avrotarget_use_schema)
                                    )
                                )
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_avrotarget_input_j_s_o_n")
        )
        (
            include.add("ds_file_attributes_encryption")
            if (

                    (((((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_encryption")
        )
        (
            include.add("ds_file_format_avrotarget_use_schema")
            if (

                    (((((self.ds_file_format == "4")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_avrotarget_use_schema")
        )
        (
            include.add("include_types")
            if (
                (
                    (
                        (
                            ((self.first_line_is_header))
                            or ((self.first_line_is_header and "#" in str(self.first_line_is_header)))
                        )
                        and (
                            (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                        or (self.file_format == "csv")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                        or (self.file_format == "delimited")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                                        or (self.file_format == "excel")
                                    )
                                )
                            )
                            or (
                                (
                                    self.file_format
                                    and (
                                        (
                                            hasattr(self.file_format, "value")
                                            and self.file_format.value
                                            and "#" in str(self.file_format.value)
                                        )
                                        or ("#" in str(self.file_format))
                                    )
                                )
                            )
                        )
                    )
                )
                or (


                            ((self.ds_first_line_header))
                            or (self.ds_first_line_header and "#" in str(self.ds_first_line_header))


                )
            )
            else exclude.add("include_types")
        )
        (
            include.add("ds_file_format")
            if (

                    (((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format")
        )
        (
            include.add("ds_file_format_parquet_target_temp_staging_area")
            if (

                    (((((self.ds_file_format == "6")) or ((self.ds_file_format and "#" in str(self.ds_file_format))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format_parquet_target_temp_staging_area")
        )
        (
            include.add("ds_first_line_header")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "0"))
                                or ((self.ds_file_format == "1"))
                                or ((self.ds_file_format == "2"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_first_line_header")
        )
        (
            include.add("decimal_format")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                or (self.file_format == "avro")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                or (self.file_format == "parquet")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (
                                    hasattr(self.file_format, "value")
                                    and self.file_format.value
                                    and "#" in str(self.file_format.value)
                                )
                                or ("#" in str(self.file_format))
                            )
                        )
                    )
                )
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format == "2")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
            )
            else exclude.add("decimal_format")
        )
        (
            include.add("create_bucket")
            if (
                (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                                or (self.write_mode == "write")
                            )
                        )
                    )
                    or (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "write_raw")
                                or (self.write_mode == "write_raw")
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
                or (((self.ds_write_mode == "0")) or (self.ds_write_mode and "#" in str(self.ds_write_mode)))
            )
            else exclude.add("create_bucket")
        )
        (
            include.add("names_as_labels")
            if (

                    (
                        (
                            (
                                (
                                    (
                                        self.file_format
                                        and (
                                            (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                                            or (self.file_format == "sav")
                                        )
                                    )
                                )
                                or (
                                    (
                                        (
                                            (
                                                (
                                                    self.file_format
                                                    and (
                                                        (
                                                            hasattr(self.file_format, "value")
                                                            and not self.file_format.value
                                                        )
                                                        or (not self.file_format)
                                                    )
                                                )
                                            )
                                            or (
                                                (
                                                    self.file_format
                                                    and (
                                                        (
                                                            hasattr(self.file_format, "value")
                                                            and self.file_format.value
                                                            and "#" in str(self.file_format.value)
                                                        )
                                                        or ("#" in str(self.file_format))
                                                    )
                                                )
                                            )
                                        )
                                        and (
                                            ((re.match(r".*\.sav$", self.file_name)))
                                            or ((self.file_name and "#" in str(self.file_name)))
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.file_format
                                        and (
                                            (
                                                hasattr(self.file_format, "value")
                                                and self.file_format.value
                                                and "#" in str(self.file_format.value)
                                            )
                                            or ("#" in str(self.file_format))
                                        )
                                    )
                                )
                            )
                            and (
                                (
                                    (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "deltalake"
                                                    )
                                                    or (self.table_format != "deltalake")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
                                                )
                                            )
                                        )
                                    )
                                    and (
                                        (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value != "iceberg"
                                                    )
                                                    or (self.table_format != "iceberg")
                                                )
                                            )
                                        )
                                        or (
                                            (
                                                self.table_format
                                                and (
                                                    (
                                                        hasattr(self.table_format, "value")
                                                        and self.table_format.value
                                                        and "#" in str(self.table_format.value)
                                                    )
                                                    or ("#" in str(self.table_format))
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
            else exclude.add("names_as_labels")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule")
            if (

                    (((((self.ds_write_mode == "0")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_attributes_life_cycle_rule")
        )
        (
            include.add("date_format")
            if (
                (
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                                or (self.file_format == "avro")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                                or (self.file_format == "csv")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                                or (self.file_format == "parquet")
                            )
                        )
                    )
                    or (
                        (
                            self.file_format
                            and (
                                (
                                    hasattr(self.file_format, "value")
                                    and self.file_format.value
                                    and "#" in str(self.file_format.value)
                                )
                                or ("#" in str(self.file_format))
                            )
                        )
                    )
                )
                or (


                            ((self.ds_file_format == "0"))
                            or (self.ds_file_format == "1")
                            or (self.ds_file_format == "2")
                            or (self.ds_file_format and "#" in str(self.ds_file_format))


                )
            )
            else exclude.add("date_format")
        )
        include.add("write_mode") if (not self.ds_use_datastage) else exclude.add("write_mode")
        (
            include.add("ds_file_format_o_r_c_target")
            if (self.ds_use_datastage)
            else exclude.add("ds_file_format_o_r_c_target")
        )
        include.add("write_part_size") if (not self.ds_use_datastage) else exclude.add("write_part_size")
        include.add("ds_write_mode") if (self.ds_use_datastage) else exclude.add("ds_write_mode")
        include.add("the_partition_paths") if (not self.ds_use_datastage) else exclude.add("the_partition_paths")
        (
            include.add("the_cache_expiration")
            if (not self.ds_use_datastage)
            else exclude.add("the_cache_expiration")
        )
        include.add("the_cache_size") if (not self.ds_use_datastage) else exclude.add("the_cache_size")
        (
            include.add("is_reject_link")
            if (((self.ds_use_datastage)) and (self.ds_reject_mode == "2"))
            else exclude.add("is_reject_link")
        )
        include.add("data_asset_name") if (self.create_data_asset) else exclude.add("data_asset_name")
        include.add("create_data_asset") if (()) else exclude.add("create_data_asset")
        (
            include.add("table_data_file_format")
            if (
                self.table_format
                and (
                    (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                    or (self.table_format == "iceberg")
                )
            )
            else exclude.add("table_data_file_format")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_transition_transition_date")
            if (
                self.ds_file_attributes_life_cycle_rule_transition == "true"
                or self.ds_file_attributes_life_cycle_rule_transition
            )
            and (self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "1")
            else exclude.add("ds_file_attributes_life_cycle_rule_transition_transition_date")
        )
        (
            include.add("time_format")
            if (

                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "avro" in str(self.file_format.value)
                        )
                        or ("avro" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "parquet" in str(self.file_format.value)
                        )
                        or ("parquet" in str(self.file_format))
                    )

            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "2" in str(self.ds_file_format)

            )
            else exclude.add("time_format")
        )
        (
            include.add("include_types")
            if (
                (self.first_line_is_header == "yes")
                and (
                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                    and self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "excel" in str(self.file_format.value)
                        )
                        or ("excel" in str(self.file_format))
                    )
                )
            )
            or (self.ds_first_line_header == "true" or self.ds_first_line_header)
            else exclude.add("include_types")
        )
        (
            include.add("ds_file_format_o_r_c_target_orc_compress")
            if (self.ds_file_format and "7" in str(self.ds_file_format))
            else exclude.add("ds_file_format_o_r_c_target_orc_compress")
        )
        (
            include.add("ds_file_format_avrotarget_avro_array_keys")
            if (
                self.ds_file_format_avrotarget_use_schema == "true" or self.ds_file_format_avrotarget_use_schema
            )
            else exclude.add("ds_file_format_avrotarget_avro_array_keys")
        )
        (
            include.add("ds_file_format_parquet_target_temp_staging_area")
            if (self.ds_file_format and "6" in str(self.ds_file_format))
            else exclude.add("ds_file_format_parquet_target_temp_staging_area")
        )
        (
            include.add("file_name")
            if (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            or (
                ((self.ds_write_mode and "0" in str(self.ds_write_mode)) or (not self.ds_write_mode))
                and (
                    (
                        self.table_format
                        and (
                            (hasattr(self.table_format, "value") and not self.table_format.value)
                            or (not self.table_format)
                        )
                    )
                    or (
                        self.table_format
                        and (
                            (hasattr(self.table_format, "value") and self.table_format.value == "file")
                            or (self.table_format == "file")
                        )
                    )
                )
            )
            else exclude.add("file_name")
        )
        (
            include.add("names_as_labels")
            if (
                (
                    self.file_format
                    and (
                        (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                        or (self.file_format == "sav")
                    )
                )
                or (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and not self.file_format.value)
                            or (not self.file_format)
                        )
                    )
                    and (re.match(r".*\.sav$", self.file_name))
                )
            )
            and (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            else exclude.add("names_as_labels")
        )
        (
            include.add("ds_file_format")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode))
            else exclude.add("ds_file_format")
        )
        (
            include.add("partitioned")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                    or (self.write_mode == "write")
                )
            )
            and (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                and self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
            )
            else exclude.add("partitioned")
        )
        (
            include.add("date_format")
            if (

                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "avro" in str(self.file_format.value)
                        )
                        or ("avro" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "parquet" in str(self.file_format.value)
                        )
                        or ("parquet" in str(self.file_format))
                    )

            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "2" in str(self.ds_file_format)

            )
            else exclude.add("date_format")
        )
        (
            include.add("table_data_file_format")
            if (
                self.table_format
                and (
                    (hasattr(self.table_format, "value") and self.table_format.value == "deltalake")
                    or (self.table_format == "deltalake")
                )
            )
            else exclude.add("table_data_file_format")
        )
        (
            include.add("ds_file_attributes_storage_class")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode))
            else exclude.add("ds_file_attributes_storage_class")
        )
        (
            include.add("timestamp_format")
            if (

                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "avro" in str(self.file_format.value)
                        )
                        or ("avro" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "parquet" in str(self.file_format.value)
                        )
                        or ("parquet" in str(self.file_format))
                    )

            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "2" in str(self.ds_file_format)

            )
            else exclude.add("timestamp_format")
        )
        (
            include.add("ds_file_format_parquet_target_parquet_compress")
            if (self.ds_file_format and "6" in str(self.ds_file_format))
            else exclude.add("ds_file_format_parquet_target_parquet_compress")
        )
        (
            include.add("worksheet_name")
            if (

                    self.file_format
                    and (
                        (hasattr(self.file_format, "value") and self.file_format.value == "excel")
                        or (self.file_format == "excel")
                    )

            )
            and (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            else exclude.add("worksheet_name")
        )
        (
            include.add("file_size_threshold")
            if (self.append_unique_identifier == "true" or self.append_unique_identifier)
            or (not self.ds_write_mode)
            else exclude.add("file_size_threshold")
        )
        (
            include.add("encoding")
            if (

                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )

            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    or self.ds_file_format
                    and "1" in str(self.ds_file_format)

            )
            else exclude.add("encoding")
        )
        (
            include.add("table_data_file_compression_codec")
            if (
                self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "deltalake" in str(self.table_format.value)
                    )
                    or ("deltalake" in str(self.table_format))
                )
                and self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "iceberg" in str(self.table_format.value)
                    )
                    or ("iceberg" in str(self.table_format))
                )
            )
            and (
                self.table_data_file_format
                and (
                    (hasattr(self.table_data_file_format, "value") and self.table_data_file_format.value)
                    or (self.table_data_file_format)
                )
            )
            and (self.endpoint_folder)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                    or (self.write_mode == "write")
                )
            )
            else exclude.add("table_data_file_compression_codec")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_transition")
            if (self.ds_file_attributes_life_cycle_rule == "true" or self.ds_file_attributes_life_cycle_rule)
            else exclude.add("ds_file_attributes_life_cycle_rule_transition")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_transition_transition_duration")
            if (
                self.ds_file_attributes_life_cycle_rule_transition == "true"
                or self.ds_file_attributes_life_cycle_rule_transition
            )
            and (self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "0")
            else exclude.add("ds_file_attributes_life_cycle_rule_transition_transition_duration")
        )
        (
            include.add("ds_file_format_parquet_target_parquet_page_size")
            if (self.ds_file_format and "6" in str(self.ds_file_format))
            else exclude.add("ds_file_format_parquet_target_parquet_page_size")
        )
        (
            include.add("partition_name_prefix")
            if (
                self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "deltalake" not in str(self.table_format.value)
                    )
                    or ("deltalake" not in str(self.table_format))
                )
                or self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "iceberg" not in str(self.table_format.value)
                    )
                    or ("iceberg" not in str(self.table_format))
                )
            )
            else exclude.add("partition_name_prefix")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_l_c_rule_scope")
            if (self.ds_file_attributes_life_cycle_rule == "true" or self.ds_file_attributes_life_cycle_rule)
            else exclude.add("ds_file_attributes_life_cycle_rule_l_c_rule_scope")
        )
        (
            include.add("codec_csv")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "csv")
                    or (self.file_format == "csv")
                )
            )
            else exclude.add("codec_csv")
        )
        (
            include.add("ds_file_format_avrotarget_input_j_s_o_n")
            if (
                self.ds_file_format_avrotarget_use_schema == "true" or self.ds_file_format_avrotarget_use_schema
            )
            else exclude.add("ds_file_format_avrotarget_input_j_s_o_n")
        )
        (
            include.add("ds_first_line_header")
            if (
                self.ds_file_format
                and "0" in str(self.ds_file_format)
                and self.ds_file_format
                and "1" in str(self.ds_file_format)
                and self.ds_file_format
                and "2" in str(self.ds_file_format)
            )
            else exclude.add("ds_first_line_header")
        )
        (
            include.add("ds_file_format_parquet_target")
            if (self.ds_file_format and "6" in str(self.ds_file_format))
            else exclude.add("ds_file_format_parquet_target")
        )
        (
            include.add("ds_file_attributes")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode))
            else exclude.add("ds_file_attributes")
        )
        (
            include.add("codec_delimited")
            if (

                    self.file_format
                    and (
                        (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                        or (self.file_format == "delimited")
                    )

            )
            and (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            else exclude.add("codec_delimited")
        )
        (
            include.add("ds_log_interval")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode))
            else exclude.add("ds_log_interval")
        )
        (
            include.add("quote_character")
            if (

                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )

            )
            or (self.ds_file_format and "0" in str(self.ds_file_format))
            else exclude.add("quote_character")
        )
        (
            include.add("decimal_format")
            if (

                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "avro" in str(self.file_format.value)
                        )
                        or ("avro" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "parquet" in str(self.file_format.value)
                        )
                        or ("parquet" in str(self.file_format))
                    )

            )
            or (

                    self.ds_file_format
                    and "0" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "1" in str(self.ds_file_format)
                    and self.ds_file_format
                    and "2" in str(self.ds_file_format)

            )
            else exclude.add("decimal_format")
        )
        (
            include.add("decimal_grouping_separator")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "avro" in str(self.file_format.value)
                    )
                    or ("avro" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "parquet" in str(self.file_format.value)
                    )
                    or ("parquet" in str(self.file_format))
                )
            )
            else exclude.add("decimal_grouping_separator")
        )
        (
            include.add("delete_bucket")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                    or (self.write_mode == "delete")
                )
            )
            else exclude.add("delete_bucket")
        )
        (
            include.add("escape_character")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
            )
            else exclude.add("escape_character")
        )
        (
            include.add("table_data_file_compression_codec")
            if (
                self.table_data_file_format
                and (
                    (hasattr(self.table_data_file_format, "value") and self.table_data_file_format.value == "parquet")
                    or (self.table_data_file_format == "parquet")
                )
            )
            else exclude.add("table_data_file_compression_codec")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_l_c_rule_format")
            if (self.ds_file_attributes_life_cycle_rule == "true" or self.ds_file_attributes_life_cycle_rule)
            else exclude.add("ds_file_attributes_life_cycle_rule_l_c_rule_format")
        )
        (
            include.add("decimal_separator")
            if (
                self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "avro" in str(self.file_format.value)
                    )
                    or ("avro" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "csv" in str(self.file_format.value)
                    )
                    or ("csv" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "delimited" in str(self.file_format.value)
                    )
                    or ("delimited" in str(self.file_format))
                )
                or self.file_format
                and (
                    (
                        hasattr(self.file_format, "value")
                        and self.file_format.value
                        and "parquet" in str(self.file_format.value)
                    )
                    or ("parquet" in str(self.file_format))
                )
            )
            else exclude.add("decimal_separator")
        )
        (
            include.add("encryption_key")
            if (
                (
                    self.file_format
                    and (
                        (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                        or (self.file_format == "sav")
                    )
                )
                or (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and not self.file_format.value)
                            or (not self.file_format)
                        )
                    )
                    and (re.match(r".*\.sav$", self.file_name))
                )
            )
            and (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            else exclude.add("encryption_key")
        )
        (
            include.add("table_data_file_compression_codec")
            if (
                self.table_data_file_format
                and (
                    (hasattr(self.table_data_file_format, "value") and self.table_data_file_format.value == "avro")
                    or (self.table_data_file_format == "avro")
                )
            )
            else exclude.add("table_data_file_compression_codec")
        )
        (
            include.add("the_data_path")
            if (
                self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "iceberg" in str(self.table_format.value)
                    )
                    or ("iceberg" in str(self.table_format))
                )
            )
            else exclude.add("the_data_path")
        )
        (
            include.add("ds_file_format_o_r_c_target_orc_stripe_size")
            if (self.ds_file_format and "7" in str(self.ds_file_format))
            else exclude.add("ds_file_format_o_r_c_target_orc_stripe_size")
        )
        include.add("the_partition_columns") if (self.endpoint_folder) else exclude.add("the_partition_columns")
        (
            include.add("quote_numeric_values")
            if (

                    self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "csv" in str(self.file_format.value)
                        )
                        or ("csv" in str(self.file_format))
                    )
                    or self.file_format
                    and (
                        (
                            hasattr(self.file_format, "value")
                            and self.file_format.value
                            and "delimited" in str(self.file_format.value)
                        )
                        or ("delimited" in str(self.file_format))
                    )

            )
            or (

                    self.ds_file_format_delimited_syntax_data_format
                    and "1" in str(self.ds_file_format_delimited_syntax_data_format)

            )
            else exclude.add("quote_numeric_values")
        )
        (
            include.add("ds_file_attributes_content_type")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode))
            else exclude.add("ds_file_attributes_content_type")
        )
        (
            include.add("ds_file_format_delimited_syntax_encoding_output_b_o_m")
            if (
                self.ds_file_format
                and "0" in str(self.ds_file_format)
                or self.ds_file_format
                and "1" in str(self.ds_file_format)
            )
            else exclude.add("ds_file_format_delimited_syntax_encoding_output_b_o_m")
        )
        (
            include.add("codec_orc")
            if (
                (
                    self.file_format
                    and (
                        (hasattr(self.file_format, "value") and self.file_format.value == "orc")
                        or (self.file_format == "orc")
                    )
                )
                or (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and not self.file_format.value)
                            or (not self.file_format)
                        )
                    )
                    and (re.match(r".*\.orc$", self.file_name))
                )
            )
            and (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            else exclude.add("codec_orc")
        )
        (
            include.add("ds_file_attributes_user_metadata")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode))
            else exclude.add("ds_file_attributes_user_metadata")
        )
        (
            include.add("ds_thread_count")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode))
            else exclude.add("ds_thread_count")
        )
        (
            include.add("file_format")
            if (

                    self.write_mode
                    and (
                        (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                        or (self.write_mode == "write")
                    )

            )
            and (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            else exclude.add("file_format")
        )
        (
            include.add("ds_file_exists")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode))
            and (self.append_unique_identifier == "false" or not self.append_unique_identifier)
            else exclude.add("ds_file_exists")
        )
        (
            include.add("ds_file_attributes_encryption")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode))
            else exclude.add("ds_file_attributes_encryption")
        )
        include.add("ds_codec_avro") if (self.ds_file_format == "4") else exclude.add("ds_codec_avro")
        (
            include.add("table_format")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                    or (self.write_mode == "write")
                )
            )
            else exclude.add("table_format")
        )
        (
            include.add("table_action")
            if (
                self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "deltalake" in str(self.table_format.value)
                    )
                    or ("deltalake" in str(self.table_format))
                )
                or self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "iceberg" in str(self.table_format.value)
                    )
                    or ("iceberg" in str(self.table_format))
                )
            )
            else exclude.add("table_action")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_expiration_expiration_date")
            if (
                self.ds_file_attributes_life_cycle_rule_expiration == "true"
                or self.ds_file_attributes_life_cycle_rule_expiration
            )
            and (self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "1")
            else exclude.add("ds_file_attributes_life_cycle_rule_expiration_expiration_date")
        )
        (
            include.add("ds_file_format_avrotarget_use_schema")
            if (self.ds_file_format and "4" in str(self.ds_file_format))
            else exclude.add("ds_file_format_avrotarget_use_schema")
        )
        (
            include.add("codec_parquet")
            if (
                (
                    self.file_format
                    and (
                        (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                        or (self.file_format == "parquet")
                    )
                )
                or (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and not self.file_format.value)
                            or (not self.file_format)
                        )
                    )
                    and (re.match(r".*\.parquet$", self.file_name))
                )
            )
            and (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            else exclude.add("codec_parquet")
        )
        (
            include.add("append_unique_identifier")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode)) or (not self.ds_write_mode)
            else exclude.add("append_unique_identifier")
        )
        (
            include.add("table_data_file_format")
            if (
                self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "deltalake" in str(self.table_format.value)
                    )
                    or ("deltalake" in str(self.table_format))
                )
                and self.table_format
                and (
                    (
                        hasattr(self.table_format, "value")
                        and self.table_format.value
                        and "iceberg" in str(self.table_format.value)
                    )
                    or ("iceberg" in str(self.table_format))
                )
            )
            and (self.endpoint_folder)
            else exclude.add("table_data_file_format")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule")
            if (self.ds_write_mode and "0" in str(self.ds_write_mode))
            else exclude.add("ds_file_attributes_life_cycle_rule")
        )
        (
            include.add("codec_avro")
            if (
                (
                    self.file_format
                    and (
                        (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                        or (self.file_format == "avro")
                    )
                )
                or (
                    (
                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and not self.file_format.value)
                            or (not self.file_format)
                        )
                    )
                    and (re.match(r".*\.avro$", self.file_name))
                )
            )
            and (

                    self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "deltalake" not in str(self.table_format.value)
                        )
                        or ("deltalake" not in str(self.table_format))
                    )
                    or self.table_format
                    and (
                        (
                            hasattr(self.table_format, "value")
                            and self.table_format.value
                            and "iceberg" not in str(self.table_format.value)
                        )
                        or ("iceberg" not in str(self.table_format))
                    )

            )
            else exclude.add("codec_avro")
        )
        (
            include.add("ds_file_format_o_r_c_target_temp_staging_area")
            if (self.ds_file_format and "7" in str(self.ds_file_format))
            else exclude.add("ds_file_format_o_r_c_target_temp_staging_area")
        )
        (
            include.add("ds_file_format_avrotarget_avro_schema")
            if (
                self.ds_file_format_avrotarget_use_schema == "true" or self.ds_file_format_avrotarget_use_schema
            )
            else exclude.add("ds_file_format_avrotarget_avro_schema")
        )
        (
            include.add("ds_create_bucket_append_u_u_i_d")
            if (self.create_bucket == "true" or self.create_bucket)
            else exclude.add("ds_create_bucket_append_u_u_i_d")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_expiration")
            if (self.ds_file_attributes_life_cycle_rule == "true" or self.ds_file_attributes_life_cycle_rule)
            else exclude.add("ds_file_attributes_life_cycle_rule_expiration")
        )
        (
            include.add("ds_file_format_avrotarget")
            if (self.ds_file_format and "4" in str(self.ds_file_format))
            else exclude.add("ds_file_format_avrotarget")
        )
        (
            include.add("ds_file_attributes_life_cycle_rule_expiration_expiration_duration")
            if (
                self.ds_file_attributes_life_cycle_rule_expiration == "true"
                or self.ds_file_attributes_life_cycle_rule_expiration
            )
            and (self.ds_file_attributes_life_cycle_rule_l_c_rule_format == "0")
            else exclude.add("ds_file_attributes_life_cycle_rule_expiration_expiration_duration")
        )
        (
            include.add("create_bucket")
            if (

                    self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "write" in str(self.write_mode.value)
                        )
                        or ("write" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "write_raw" in str(self.write_mode.value)
                        )
                        or ("write_raw" in str(self.write_mode))
                    )

            )
            or (self.ds_write_mode and "0" in str(self.ds_write_mode))
            else exclude.add("create_bucket")
        )
        (
            include.add("table_data_file_compression_codec")
            if (
                self.table_data_file_format
                and (
                    (hasattr(self.table_data_file_format, "value") and self.table_data_file_format.value == "orc")
                    or (self.table_data_file_format == "orc")
                )
            )
            else exclude.add("table_data_file_compression_codec")
        )
        (
            include.add("ds_file_format_parquet_target_parquet_block_size")
            if (self.ds_file_format and "6" in str(self.ds_file_format))
            else exclude.add("ds_file_format_parquet_target_parquet_block_size")
        )
        (
            include.add("ds_file_format_o_r_c_target_orc_buffer_size")
            if (self.ds_file_format and "7" in str(self.ds_file_format))
            else exclude.add("ds_file_format_o_r_c_target_orc_buffer_size")
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
            "cell_range",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "current_output_link_type",
            "date_format",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "decimal_format",
            "decimal_grouping_separator",
            "decimal_rounding_mode",
            "decimal_separator",
            "default_maximum_length_for_columns",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "display_value_labels",
            "ds_exclude_files",
            "ds_file_format",
            "ds_file_format_avro_source",
            "ds_file_format_avro_source_output_j_s_o_n",
            "ds_file_format_delimited_syntax",
            "ds_file_format_delimited_syntax_data_format",
            "ds_file_format_delimited_syntax_escape",
            "ds_file_format_delimited_syntax_field_delimiter",
            "ds_file_format_delimited_syntax_record_def",
            "ds_file_format_delimited_syntax_record_def_record_def_source",
            "ds_file_format_delimited_syntax_row_delimiter",
            "ds_file_format_delimited_syntax_trace_file",
            "ds_file_format_o_r_c_source",
            "ds_file_format_o_r_c_source_temp_staging_area",
            "ds_file_format_parquet_source",
            "ds_file_format_parquet_source_temp_staging_area",
            "ds_filename_column",
            "ds_first_line_header",
            "ds_java_heap_size",
            "ds_read_mode",
            "ds_recurse",
            "ds_reject_mode",
            "ds_use_datastage",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "encoding",
            "encryption_key",
            "endpoint_folder",
            "escape_character",
            "escape_character_value",
            "exclude_missing_values",
            "execution_mode",
            "field_delimiter",
            "field_delimiter_value",
            "fields_xml_path",
            "file_format",
            "file_name",
            "first_line",
            "first_line_is_header",
            "flow_dirty",
            "generate_unicode_type_columns",
            "hide",
            "infer_as_varchar",
            "infer_null_as_empty_string",
            "infer_record_count",
            "infer_schema",
            "infer_timestamp_as_date",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "invalid_data_handling",
            "is_reject_link",
            "json_infer_record_count",
            "json_path",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "labels_as_names",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "null_value",
            "output_acp_should_hide",
            "output_avro_as_json",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "part_stable_coll",
            "part_stable_ordered",
            "part_stable_roundrobin_coll",
            "part_unique_coll",
            "part_unique_ordered",
            "part_unique_roundrobin_coll",
            "partition_name_prefix",
            "partition_type",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "preserve_partitioning",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "quote_character",
            "quote_numeric_values",
            "read_a_file_to_a_row",
            "read_mode",
            "read_part_size",
            "row_delimiter",
            "row_delimiter_value",
            "row_limit",
            "row_start",
            "runtime_column_propagation",
            "schema_of_xml",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "store_shared_strings_in_the_temporary_file",
            "table_format",
            "table_name",
            "table_namespace",
            "time_format",
            "timestamp_format",
            "timezone_format",
            "type_mapping",
            "unique",
            "use_4_digit_years_in_date_formats",
            "use_field_formats",
            "use_variable_formats",
            "worksheet_name",
            "xml_path",
        }
        required = {
            "access_key",
            "authentication_method",
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "escape_character_value",
            "field_delimiter_value",
            "output_acp_should_hide",
            "proxy_host",
            "proxy_port",
            "role_arn",
            "role_session_name",
            "row_delimiter_value",
            "secret_key",
            "session_token",
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
            "append_unique_identifier",
            "bucket",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "codec_avro",
            "codec_csv",
            "codec_delimited",
            "codec_orc",
            "codec_parquet",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "create_bucket",
            "create_data_asset",
            "current_output_link_type",
            "data_asset_name",
            "date_format",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "decimal_format",
            "decimal_grouping_separator",
            "decimal_separator",
            "delete_bucket",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_codec_avro",
            "ds_create_bucket_append_u_u_i_d",
            "ds_file_attributes",
            "ds_file_attributes_content_type",
            "ds_file_attributes_encryption",
            "ds_file_attributes_life_cycle_rule",
            "ds_file_attributes_life_cycle_rule_expiration",
            "ds_file_attributes_life_cycle_rule_expiration_expiration_date",
            "ds_file_attributes_life_cycle_rule_expiration_expiration_duration",
            "ds_file_attributes_life_cycle_rule_l_c_rule_format",
            "ds_file_attributes_life_cycle_rule_l_c_rule_scope",
            "ds_file_attributes_life_cycle_rule_transition",
            "ds_file_attributes_life_cycle_rule_transition_transition_date",
            "ds_file_attributes_life_cycle_rule_transition_transition_duration",
            "ds_file_attributes_storage_class",
            "ds_file_attributes_user_metadata",
            "ds_file_exists",
            "ds_file_format",
            "ds_file_format_avrotarget",
            "ds_file_format_avrotarget_avro_array_keys",
            "ds_file_format_avrotarget_avro_schema",
            "ds_file_format_avrotarget_input_j_s_o_n",
            "ds_file_format_avrotarget_use_schema",
            "ds_file_format_delimited_syntax",
            "ds_file_format_delimited_syntax_data_format",
            "ds_file_format_delimited_syntax_encoding_output_b_o_m",
            "ds_file_format_delimited_syntax_escape",
            "ds_file_format_delimited_syntax_field_delimiter",
            "ds_file_format_delimited_syntax_row_delimiter",
            "ds_file_format_o_r_c_target",
            "ds_file_format_o_r_c_target_orc_buffer_size",
            "ds_file_format_o_r_c_target_orc_compress",
            "ds_file_format_o_r_c_target_orc_stripe_size",
            "ds_file_format_o_r_c_target_temp_staging_area",
            "ds_file_format_parquet_target",
            "ds_file_format_parquet_target_parquet_block_size",
            "ds_file_format_parquet_target_parquet_compress",
            "ds_file_format_parquet_target_parquet_page_size",
            "ds_file_format_parquet_target_temp_staging_area",
            "ds_first_line_header",
            "ds_java_heap_size",
            "ds_log_interval",
            "ds_thread_count",
            "ds_use_datastage",
            "ds_write_mode",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "encoding",
            "encryption_key",
            "endpoint_folder",
            "escape_character",
            "escape_character_value",
            "execution_mode",
            "field_delimiter",
            "field_delimiter_value",
            "file_format",
            "file_name",
            "file_size_threshold",
            "first_line_is_header",
            "flow_dirty",
            "hide",
            "include_types",
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
            "names_as_labels",
            "null_value",
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
            "partition_name_prefix",
            "partition_type",
            "partitioned",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "preserve_partitioning",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "quote_character",
            "quote_numeric_values",
            "row_delimiter",
            "row_delimiter_value",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "table_action",
            "table_data_file_compression_codec",
            "table_data_file_format",
            "table_format",
            "table_name",
            "table_namespace",
            "the_cache_expiration",
            "the_cache_size",
            "the_data_path",
            "the_partition_columns",
            "the_partition_paths",
            "time_format",
            "timestamp_format",
            "timezone_format",
            "unique",
            "worksheet_name",
            "write_mode",
            "write_part_size",
        }
        required = {
            "access_key",
            "authentication_method",
            "current_output_link_type",
            "data_asset_name",
            "ds_file_attributes_life_cycle_rule_expiration_expiration_date",
            "ds_file_attributes_life_cycle_rule_expiration_expiration_duration",
            "ds_file_attributes_life_cycle_rule_transition_transition_date",
            "ds_file_attributes_life_cycle_rule_transition_transition_duration",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "escape_character_value",
            "field_delimiter_value",
            "output_acp_should_hide",
            "proxy_host",
            "proxy_port",
            "role_arn",
            "role_session_name",
            "row_delimiter_value",
            "secret_key",
            "session_token",
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
                "SupportsRef": False,
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
        props = {"is_reject_link"}
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
        return {"min": 0, "max": 2}

    def get_allowed_as_source_props(self) -> bool:
        return True

    def get_allowed_as_target_props(self) -> bool:
        return True
