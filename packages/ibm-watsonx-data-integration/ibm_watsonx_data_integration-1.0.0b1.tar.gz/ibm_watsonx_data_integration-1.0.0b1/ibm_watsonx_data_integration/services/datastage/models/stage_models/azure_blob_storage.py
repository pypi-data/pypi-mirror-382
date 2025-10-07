import re
import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.azure_blob_storage_connection import (
    AzureBlobStorageConn,
)
from ibm_watsonx_data_integration.services.datastage.models.enums import AZURE_BLOB_STORAGE
from pydantic import Field
from typing import ClassVar


class azure_blob_storage(BaseStage):

    op_name: ClassVar[str] = "azureblobstorage"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/azureblobstorage.svg"
    label: ClassVar[str] = "Microsoft Azure Blob Storage"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: AzureBlobStorageConn = AzureBlobStorageConn()
    append_unique_identifier: bool | None = Field(False, alias="wave_handling.append_uid")
    blob_type: AZURE_BLOB_STORAGE.BlobType = Field(AZURE_BLOB_STORAGE.BlobType.block, alias="blob_type")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: AZURE_BLOB_STORAGE.BufModeRonly | None = Field(
        AZURE_BLOB_STORAGE.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: AZURE_BLOB_STORAGE.BufferingMode | None = Field(
        AZURE_BLOB_STORAGE.BufferingMode.default, alias="buf_mode"
    )
    byte_limit: str | None = Field(None, alias="byte_limit")
    cas_api_key: str = Field(None, alias="cas_api_key")
    cas_endpoint: str = Field(None, alias="cas_endpoint")
    cas_instance_id: str = Field(None, alias="cas_instance_id")
    catalog_name: str | None = Field(None, alias="catalog_name")
    cell_range: str | None = Field(None, alias="range")
    codec_avro: AZURE_BLOB_STORAGE.CodecAvro | None = Field(None, alias="codec_avro")
    codec_csv: AZURE_BLOB_STORAGE.CodecCsv | None = Field(None, alias="codec_csv")
    codec_delimited: AZURE_BLOB_STORAGE.CodecDelimited | None = Field(None, alias="codec_delimited")
    codec_orc: AZURE_BLOB_STORAGE.CodecOrc | None = Field(None, alias="codec_orc")
    codec_parquet: AZURE_BLOB_STORAGE.CodecParquet | None = Field(None, alias="codec_parquet")
    collecting: AZURE_BLOB_STORAGE.Collecting | None = Field(AZURE_BLOB_STORAGE.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: AZURE_BLOB_STORAGE.CombinabilityMode | None = Field(
        AZURE_BLOB_STORAGE.CombinabilityMode.auto, alias="combinability"
    )
    container_for_temporary_files: str | None = Field(None, alias="parallel_write.temp_container")
    container_source: str | None = Field(None, alias="container_source")
    create_container: bool | None = Field(False, alias="create_container")
    create_data_asset: bool | None = Field(False, alias="registerDataAsset")
    create_temporary_container: bool | None = Field(False, alias="parallel_write.create_temp_container")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_asset_name: str = Field(None, alias="dataAssetName")
    date_format: str | None = Field(None, alias="date_format")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    decimal_format: str | None = Field(None, alias="decimal_format")
    decimal_grouping_separator: str | None = Field(None, alias="decimal_format_grouping_separator")
    decimal_rounding_mode: AZURE_BLOB_STORAGE.DecimalRoundingMode | None = Field(
        AZURE_BLOB_STORAGE.DecimalRoundingMode.floor, alias="decimal_rounding_mode"
    )
    decimal_separator: str | None = Field(None, alias="decimal_format_decimal_separator")
    default_maximum_length_for_columns: int | None = Field(20000, alias="default_max_string_binary_precision")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    definition_source: str | None = Field(None, alias="delimited_syntax.record_def.record_def_source")
    delete_container: bool | None = Field(False, alias="delete_container")
    delimited_syntax_encoding: str | None = Field(None, alias="delimited_syntax.encoding")
    delimited_syntax_escape: str | None = Field(None, alias="delimited_syntax.escape")
    delimited_syntax_field_delimiter: str | None = Field(",", alias="delimited_syntax.field_delimiter")
    delimited_syntax_field_formats_date_format: str | None = Field(
        None, alias="delimited_syntax.field_formats.date_format"
    )
    delimited_syntax_field_formats_decimal_format: str | None = Field(
        None, alias="delimited_syntax.field_formats.decimal_format"
    )
    delimited_syntax_field_formats_time_format: str | None = Field(
        None, alias="delimited_syntax.field_formats.time_format"
    )
    delimited_syntax_field_formats_timestamp_format: str | None = Field(
        None, alias="delimited_syntax.field_formats.timestamp_format"
    )
    delimited_syntax_null_value: str | None = Field(None, alias="delimited_syntax.null_value")
    delimited_syntax_row_delimiter: str | None = Field("<NL>", alias="delimited_syntax.row_delimiter")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    display_value_labels: bool | None = Field(None, alias="display_value_labels")
    ds_container: str | None = Field(None, alias="_container")
    ds_create_container: bool | None = Field(False, alias="_create_container")
    ds_file_format: AZURE_BLOB_STORAGE.DSFileFormat | None = Field(
        AZURE_BLOB_STORAGE.DSFileFormat.delimited, alias="_file_format"
    )
    ds_file_name: str = Field(None, alias="_file_name")
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    ds_read_mode: AZURE_BLOB_STORAGE.DSReadMode = Field(
        AZURE_BLOB_STORAGE.DSReadMode.read_single_file, alias="_read_mode"
    )
    ds_use_datastage: bool | None = Field(True, alias="_use_datastage")
    ds_write_mode: AZURE_BLOB_STORAGE.DSWriteMode = Field(AZURE_BLOB_STORAGE.DSWriteMode.write, alias="_write_mode")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_parallel_write: bool | None = Field(False, alias="parallel_write")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    encoding: str | None = Field("utf-8", alias="encoding")
    encryption_key: str | None = Field(None, alias="encryption_key")
    endpoint_folder: str | None = Field(None, alias="table_folder_name")
    escape_character: AZURE_BLOB_STORAGE.EscapeCharacter | None = Field(
        AZURE_BLOB_STORAGE.EscapeCharacter.none, alias="escape_character"
    )
    escape_character_value: str = Field(None, alias="escape_character_value")
    exclude_missing_values: bool | None = Field(None, alias="exclude_missing_values")
    execution_mode: AZURE_BLOB_STORAGE.ExecutionMode | None = Field(
        AZURE_BLOB_STORAGE.ExecutionMode.default_par, alias="execmode"
    )
    field_delimiter: AZURE_BLOB_STORAGE.FieldDelimiter | None = Field(
        AZURE_BLOB_STORAGE.FieldDelimiter.comma, alias="field_delimiter"
    )
    field_delimiter_value: str = Field(None, alias="field_delimiter_value")
    fields_xml_path: str | None = Field(None, alias="xml_path_fields")
    file_exists: AZURE_BLOB_STORAGE.FileExists | None = Field(
        AZURE_BLOB_STORAGE.FileExists.overwrite_file, alias="file_exists"
    )
    file_format: AZURE_BLOB_STORAGE.FileFormat | None = Field(AZURE_BLOB_STORAGE.FileFormat.csv, alias="file_format")
    file_name: str = Field(None, alias="file_name")
    file_name_column: str | None = Field(None, alias="filename_column")
    file_name_source: str = Field(None, alias="file_name_source")
    file_size_threshold: int | None = Field(1, alias="wave_handling.file_size_threshold")
    first_line: int | None = Field(0, alias="first_line")
    first_line_is_header: bool | None = Field(False, alias="first_line_header")
    first_row_is_header: bool | None = Field(False, alias="delimited_syntax.header")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    generate_unicode_type_columns: bool | None = Field(False, alias="generate_unicode_columns")
    has_reference_output: bool | None = Field(False, alias="has_ref_output")
    hide: bool | None = Field(False, alias="hide")
    include_byte_order_mark_for_unicode_encoding: bool | None = Field(
        False, alias="delimited_syntax.encoding.output_bom"
    )
    include_child_folders: bool | None = Field(True, alias="recurse")
    include_data_types: bool | None = Field(False, alias="delimited_syntax.header.include_types")
    include_types: bool | None = Field(False, alias="include_types")
    infer_as_varchar: bool | None = Field(None, alias="infer_as_varchar")
    infer_null_as_empty_string: bool | None = Field(False, alias="infer_null_as_empty_string")
    infer_record_count: int | None = Field(1000, alias="infer_record_count")
    infer_schema: bool | None = Field(None, alias="infer_schema")
    infer_timestamp_as_date: bool | None = Field(True, alias="infer_timestamp_as_date")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    invalid_data_handling: AZURE_BLOB_STORAGE.InvalidDataHandling | None = Field(
        AZURE_BLOB_STORAGE.InvalidDataHandling.fail, alias="invalid_data_handling"
    )
    json_infer_record_count: int | None = Field(None, alias="json_infer_record_count")
    json_path: str | None = Field(None, alias="json_path")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    labels_as_names: bool | None = Field(None, alias="labels_as_names")
    lookup_type: AZURE_BLOB_STORAGE.LookupType | None = Field(
        AZURE_BLOB_STORAGE.LookupType.empty, alias="lookup_type"
    )
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    mds_rest_endpoint: str | None = Field(None, alias="mds_rest_endpoint")
    names_as_labels: bool | None = Field(None, alias="names_as_labels")
    null_value: str | None = Field(None, alias="null_value")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_as_json: bool | None = Field(None, alias="output_avro_as_json")
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
    partition_type: AZURE_BLOB_STORAGE.PartitionType | None = Field(
        AZURE_BLOB_STORAGE.PartitionType.auto, alias="part_type"
    )
    partitioned: bool | None = Field(False, alias="partitioned")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: AZURE_BLOB_STORAGE.PreservePartitioning | None = Field(
        AZURE_BLOB_STORAGE.PreservePartitioning.default_propagate, alias="preserve"
    )
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    quotation_mark: AZURE_BLOB_STORAGE.DelimitedSyntaxQuotes | None = Field(
        AZURE_BLOB_STORAGE.DelimitedSyntaxQuotes.none, alias="delimited_syntax.quotes"
    )
    quote_character: AZURE_BLOB_STORAGE.QuoteCharacter | None = Field(
        AZURE_BLOB_STORAGE.QuoteCharacter.none, alias="quote_character"
    )
    quote_numeric_values: bool | None = Field(True, alias="quote_numerics")
    read_mode: AZURE_BLOB_STORAGE.ReadMode | None = Field(AZURE_BLOB_STORAGE.ReadMode.read_single, alias="read_mode")
    read_part_size: int | None = Field(None, alias="read_part_size")
    record_definition: AZURE_BLOB_STORAGE.DelimitedSyntaxRecordDef | None = Field(
        AZURE_BLOB_STORAGE.DelimitedSyntaxRecordDef.none, alias="delimited_syntax.record_def"
    )
    record_limit: int | None = Field(None, alias="delimited_syntax.record_limit")
    reject_mode: AZURE_BLOB_STORAGE.RejectMode | None = Field(
        AZURE_BLOB_STORAGE.RejectMode.cont, alias="reject_mode"
    )
    row_delimiter: AZURE_BLOB_STORAGE.RowDelimiter | None = Field(
        AZURE_BLOB_STORAGE.RowDelimiter.new_line, alias="row_delimiter"
    )
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
    sorting_key: AZURE_BLOB_STORAGE.KeyColSelect | None = Field(
        AZURE_BLOB_STORAGE.KeyColSelect.default, alias="keyColSelect"
    )
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    store_shared_strings_in_the_temporary_file: bool | None = Field(None, alias="use_sst_temp_file")
    table_action: AZURE_BLOB_STORAGE.TableAction | None = Field(
        AZURE_BLOB_STORAGE.TableAction.append, alias="table_action"
    )
    table_data_file_compression_codec: AZURE_BLOB_STORAGE.TableDataFileCompressionCodec | None = Field(
        None, alias="table_data_file_compression_codec"
    )
    table_data_file_format: AZURE_BLOB_STORAGE.TableDataFileFormat | None = Field(
        AZURE_BLOB_STORAGE.TableDataFileFormat.avro, alias="table_data_file_format"
    )
    table_format: AZURE_BLOB_STORAGE.TableFormat | None = Field(None, alias="table_format")
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
    use_watsonx_credential_provider: bool | None = Field(None, alias="use_watsonx_credential_provider")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    worksheet_name: str | None = Field(None, alias="sheet_name")
    write_mode: AZURE_BLOB_STORAGE.WriteMode | None = Field(AZURE_BLOB_STORAGE.WriteMode.write, alias="write_mode")
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
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("delimited_syntax_field_formats_date_format")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("delimited_syntax_field_formats_date_format")
        )
        (
            include.add("file_name_column")
            if (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            else exclude.add("file_name_column")
        )
        (
            include.add("delimited_syntax_field_formats_timestamp_format")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("delimited_syntax_field_formats_timestamp_format")
        )
        (
            include.add("reject_mode")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("reject_mode")
        )
        (
            include.add("record_definition")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("record_definition")
        )
        (
            include.add("delimited_syntax_encoding")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("delimited_syntax_encoding")
        )
        (
            include.add("delimited_syntax_escape")
            if (
                ((self.ds_file_format == "delimited"))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("delimited_syntax_escape")
        )
        (
            include.add("container_source")
            if (

                    ((self.ds_read_mode == "list_files"))
                    or (self.ds_read_mode == "read_multiple_files")
                    or (self.ds_read_mode == "read_single_file")

            )
            else exclude.add("container_source")
        )
        (
            include.add("include_child_folders")
            if (((self.ds_read_mode == "list_files")) or (self.ds_read_mode == "read_multiple_files"))
            else exclude.add("include_child_folders")
        )
        include.add("lookup_type") if (self.has_reference_output) else exclude.add("lookup_type")
        (
            include.add("quotation_mark")
            if (
                ((self.ds_file_format == "delimited"))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("quotation_mark")
        )
        (
            include.add("definition_source")
            if (
                (
                    ((self.record_definition == "delimited_string"))
                    or ((self.record_definition == "delimited_string_in_a_file"))
                    or ((self.record_definition == "schema_file"))
                )
                and (((self.ds_file_format == "comma-separated_value_csv")) or (self.ds_file_format == "delimited"))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("definition_source")
        )
        (
            include.add("delimited_syntax_field_formats_time_format")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("delimited_syntax_field_formats_time_format")
        )
        (
            include.add("first_row_is_header")
            if (
                (
                    ((self.record_definition == "delimited_string"))
                    or ((self.record_definition == "delimited_string_in_a_file"))
                    or ((self.record_definition == "none"))
                    or ((self.record_definition == "schema_file"))
                )
                and (((self.ds_file_format == "comma-separated_value_csv")) or (self.ds_file_format == "delimited"))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("first_row_is_header")
        )
        (
            include.add("delimited_syntax_field_formats_decimal_format")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("delimited_syntax_field_formats_decimal_format")
        )
        (
            include.add("file_name_source")
            if (

                    ((self.ds_read_mode == "list_files"))
                    or (self.ds_read_mode == "read_multiple_files")
                    or (self.ds_read_mode == "read_single_file")

            )
            else exclude.add("file_name_source")
        )
        (
            include.add("delimited_syntax_null_value")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("delimited_syntax_null_value")
        )
        (
            include.add("record_limit")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("record_limit")
        )
        (
            include.add("ds_file_format")
            if (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            else exclude.add("ds_file_format")
        )
        (
            include.add("delimited_syntax_row_delimiter")
            if (
                ((self.ds_file_format == "delimited"))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("delimited_syntax_row_delimiter")
        )
        (
            include.add("delimited_syntax_field_delimiter")
            if (
                ((self.ds_file_format == "delimited"))
                and (((self.ds_read_mode == "read_multiple_files")) or (self.ds_read_mode == "read_single_file"))
            )
            else exclude.add("delimited_syntax_field_delimiter")
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
                )
                and (not self.output_as_json)
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
            include.add("null_value")
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
            else exclude.add("null_value")
        )
        (
            include.add("output_as_json")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                            or (self.file_format == "avro")
                        )


            )
            else exclude.add("output_as_json")
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
            include.add("quote_character")
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
            else exclude.add("quote_character")
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
                )
                and (not self.output_as_json)
            )
            else exclude.add("time_format")
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
            include.add("encoding")
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
                                (hasattr(self.file_format, "value") and self.file_format.value == "shp")
                                or (self.file_format == "shp")
                            )

                    )

            )
            else exclude.add("encoding")
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
                )
                and (not self.output_as_json)
            )
            else exclude.add("timestamp_format")
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
                and (not self.output_as_json)
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
            include.add("file_name")
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
            else exclude.add("file_name")
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
                )
                and (not self.output_as_json)
            )
            else exclude.add("decimal_format")
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
                )
                and (not self.output_as_json)
            )
            else exclude.add("date_format")
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
                                ((not self.output_as_json))
                                or ((self.output_as_json and "#" in str(self.output_as_json)))
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
            include.add("delimited_syntax_field_formats_date_format")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_field_formats_date_format")
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("null_value")
        )
        (
            include.add("output_as_json")
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
            else exclude.add("output_as_json")
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
            include.add("file_name_column")
            if (

                    (
                        ((self.ds_read_mode == "read_multiple_files"))
                        or ((self.ds_read_mode == "read_single_file"))
                        or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("file_name_column")
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
            include.add("delimited_syntax_field_formats_timestamp_format")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_field_formats_timestamp_format")
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
                    and (not self.ds_use_datastage)

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
                                ((not self.output_as_json))
                                or ((self.output_as_json and "#" in str(self.output_as_json)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

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
            include.add("reject_mode")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("reject_mode")
        )
        (
            include.add("record_definition")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("record_definition")
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
            include.add("delimited_syntax_encoding")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_encoding")
        )
        (
            include.add("delimited_syntax_escape")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_escape")
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
                    and (not self.ds_use_datastage)

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
            include.add("container_source")
            if (

                    (
                        (
                            (
                                ((self.ds_read_mode == "list_files"))
                                or ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("container_source")
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
                                ((not self.output_as_json))
                                or ((self.output_as_json and "#" in str(self.output_as_json)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("timestamp_format")
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
            include.add("include_child_folders")
            if (

                    (
                        (
                            (
                                ((self.ds_read_mode == "list_files"))
                                or ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("include_child_folders")
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
                                ((not self.output_as_json))
                                or ((self.output_as_json and "#" in str(self.output_as_json)))
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
            include.add("lookup_type")
            if (((((self.has_reference_output)))) and (self.ds_use_datastage))
            else exclude.add("lookup_type")
        )
        (
            include.add("quotation_mark")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("quotation_mark")
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
                    and (not self.ds_use_datastage)

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
            include.add("definition_source")
            if (

                    (
                        (
                            (
                                ((self.record_definition == "delimited_string"))
                                or ((self.record_definition == "delimited_string_in_a_file"))
                                or ((self.record_definition == "schema_file"))
                                or ((self.record_definition and "#" in str(self.record_definition)))
                            )
                            and (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("definition_source")
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
            include.add("delimited_syntax_field_formats_time_format")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_field_formats_time_format")
        )
        (
            include.add("first_row_is_header")
            if (

                    (
                        (
                            (
                                ((self.record_definition == "delimited_string"))
                                or ((self.record_definition == "delimited_string_in_a_file"))
                                or ((self.record_definition == "none"))
                                or ((self.record_definition == "schema_file"))
                                or ((self.record_definition and "#" in str(self.record_definition)))
                            )
                            and (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("first_row_is_header")
        )
        (
            include.add("delimited_syntax_field_formats_decimal_format")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_field_formats_decimal_format")
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
            include.add("file_name_source")
            if (

                    (
                        ((self.ds_read_mode == "list_files"))
                        or ((self.ds_read_mode == "read_multiple_files"))
                        or ((self.ds_read_mode == "read_single_file"))
                        or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("file_name_source")
        )
        (
            include.add("delimited_syntax_null_value")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_null_value")
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
            include.add("record_limit")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("record_limit")
        )
        (
            include.add("ds_file_format")
            if (

                    (
                        ((self.ds_read_mode == "read_multiple_files"))
                        or ((self.ds_read_mode == "read_single_file"))
                        or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format")
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
                                ((not self.output_as_json))
                                or ((self.output_as_json and "#" in str(self.output_as_json)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

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
                                ((not self.output_as_json))
                                or ((self.output_as_json and "#" in str(self.output_as_json)))
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("date_format")
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
        (
            include.add("delimited_syntax_row_delimiter")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_row_delimiter")
        )
        (
            include.add("delimited_syntax_field_delimiter")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_read_mode == "read_multiple_files"))
                                or ((self.ds_read_mode == "read_single_file"))
                                or ((self.ds_read_mode and "#" in str(self.ds_read_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_field_delimiter")
        )

        include.add("infer_as_varchar") if (()) else exclude.add("infer_as_varchar")
        include.add("infer_schema") if (()) else exclude.add("infer_schema")
        (
            include.add("partition_name_prefix")
            if (not self.ds_use_datastage)
            else exclude.add("partition_name_prefix")
        )
        (
            include.add("has_reference_output")
            if (self.ds_use_datastage)
            else exclude.add("has_reference_output")
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
        include.add("read_part_size") if (not self.ds_use_datastage) else exclude.add("read_part_size")
        include.add("row_start") if (not self.ds_use_datastage) else exclude.add("row_start")
        include.add("row_limit") if (not self.ds_use_datastage) else exclude.add("row_limit")
        include.add("timezone_format") if (not self.ds_use_datastage) else exclude.add("timezone_format")
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
            include.add("quotation_mark")
            if (self.ds_file_format == "delimited")
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("quotation_mark")
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
            and (not self.output_as_json)
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
                and "read_multiple_files" in str(self.ds_read_mode)
                or self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("ds_file_format")
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
            and (not self.output_as_json)
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
            else exclude.add("null_value")
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
            and (not self.output_as_json)
            else exclude.add("timestamp_format")
        )
        (
            include.add("delimited_syntax_field_delimiter")
            if (self.ds_file_format == "delimited")
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("delimited_syntax_field_delimiter")
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
            include.add("reject_mode")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("reject_mode")
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
            else exclude.add("encoding")
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
            include.add("lookup_type")
            if (self.has_reference_output == "true" or self.has_reference_output)
            else exclude.add("lookup_type")
        )
        (
            include.add("delimited_syntax_row_delimiter")
            if (self.ds_file_format == "delimited")
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("delimited_syntax_row_delimiter")
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
            include.add("file_name_source")
            if (
                self.ds_read_mode
                and "list_files" in str(self.ds_read_mode)
                or self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                or self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("file_name_source")
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
            include.add("container_source")
            if (
                self.ds_read_mode
                and "list_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("container_source")
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
            include.add("delimited_syntax_encoding")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("delimited_syntax_encoding")
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
            include.add("first_row_is_header")
            if (
                self.record_definition
                and "delimited_string" in str(self.record_definition)
                and self.record_definition
                and "delimited_string_in_a_file" in str(self.record_definition)
                and self.record_definition
                and "none" in str(self.record_definition)
                and self.record_definition
                and "schema_file" in str(self.record_definition)
            )
            and (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("first_row_is_header")
        )
        (
            include.add("file_name_column")
            if (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                or self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("file_name_column")
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
            else exclude.add("quote_character")
        )
        (
            include.add("delimited_syntax_field_formats_time_format")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("delimited_syntax_field_formats_time_format")
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
            and (not self.output_as_json)
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
            and (not self.output_as_json)
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
            and (not self.output_as_json)
            else exclude.add("decimal_separator")
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
            include.add("delimited_syntax_field_formats_timestamp_format")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("delimited_syntax_field_formats_timestamp_format")
        )
        (
            include.add("definition_source")
            if (
                self.record_definition
                and "delimited_string" in str(self.record_definition)
                and self.record_definition
                and "delimited_string_in_a_file" in str(self.record_definition)
                and self.record_definition
                and "schema_file" in str(self.record_definition)
            )
            and (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("definition_source")
        )
        (
            include.add("include_child_folders")
            if (
                self.ds_read_mode
                and "list_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
            )
            else exclude.add("include_child_folders")
        )
        (
            include.add("record_definition")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("record_definition")
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
            include.add("output_as_json")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                    or (self.file_format == "avro")
                )
            )
            else exclude.add("output_as_json")
        )
        (
            include.add("delimited_syntax_escape")
            if (self.ds_file_format == "delimited")
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("delimited_syntax_escape")
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
            include.add("delimited_syntax_field_formats_decimal_format")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("delimited_syntax_field_formats_decimal_format")
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
            include.add("delimited_syntax_field_formats_date_format")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("delimited_syntax_field_formats_date_format")
        )
        (
            include.add("record_limit")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("record_limit")
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
            include.add("delimited_syntax_null_value")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (
                self.ds_read_mode
                and "read_multiple_files" in str(self.ds_read_mode)
                and self.ds_read_mode
                and "read_single_file" in str(self.ds_read_mode)
            )
            else exclude.add("delimited_syntax_null_value")
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
            include.add("enable_parallel_write")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (self.ds_write_mode == "write")
            )
            else exclude.add("enable_parallel_write")
        )
        (
            include.add("delimited_syntax_field_formats_date_format")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (self.ds_write_mode == "write")
            )
            else exclude.add("delimited_syntax_field_formats_date_format")
        )
        (
            include.add("delimited_syntax_field_formats_timestamp_format")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (self.ds_write_mode == "write")
            )
            else exclude.add("delimited_syntax_field_formats_timestamp_format")
        )
        (
            include.add("ds_create_container")
            if (self.ds_write_mode == "write")
            else exclude.add("ds_create_container")
        )
        (
            include.add("container_for_temporary_files")
            if (((self.enable_parallel_write)) and (self.ds_write_mode == "write"))
            else exclude.add("container_for_temporary_files")
        )
        (
            include.add("file_size_threshold")
            if (((self.append_unique_identifier)) and (self.ds_write_mode == "write"))
            else exclude.add("file_size_threshold")
        )
        include.add("ds_file_name") if (self.ds_write_mode == "write") else exclude.add("ds_file_name")
        (
            include.add("delimited_syntax_encoding")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (self.ds_write_mode == "write")
            )
            else exclude.add("delimited_syntax_encoding")
        )
        (
            include.add("delimited_syntax_escape")
            if (((self.ds_file_format == "delimited")) and (self.ds_write_mode == "write"))
            else exclude.add("delimited_syntax_escape")
        )
        (
            include.add("quotation_mark")
            if (((self.ds_file_format == "delimited")) and (self.ds_write_mode == "write"))
            else exclude.add("quotation_mark")
        )
        (
            include.add("delimited_syntax_field_formats_time_format")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (self.ds_write_mode == "write")
            )
            else exclude.add("delimited_syntax_field_formats_time_format")
        )
        (
            include.add("first_row_is_header")
            if (
                ((self.ds_write_mode == "write"))
                and (((self.ds_file_format == "comma-separated_value_csv")) or (self.ds_file_format == "delimited"))
            )
            else exclude.add("first_row_is_header")
        )
        (
            include.add("delimited_syntax_field_formats_decimal_format")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (self.ds_write_mode == "write")
            )
            else exclude.add("delimited_syntax_field_formats_decimal_format")
        )
        (
            include.add("delimited_syntax_null_value")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (self.ds_write_mode == "write")
            )
            else exclude.add("delimited_syntax_null_value")
        )
        (
            include.add("include_byte_order_mark_for_unicode_encoding")
            if (
                (((self.ds_file_format == "comma-separated_value_csv")) or ((self.ds_file_format == "delimited")))
                and (self.ds_write_mode == "write")
            )
            else exclude.add("include_byte_order_mark_for_unicode_encoding")
        )
        (
            include.add("append_unique_identifier")
            if (self.ds_write_mode == "write")
            else exclude.add("append_unique_identifier")
        )
        (
            include.add("include_data_types")
            if (
                ((self.first_row_is_header))
                and (((self.ds_file_format == "comma-separated_value_csv")) or (self.ds_file_format == "delimited"))
                and (self.ds_write_mode == "write")
            )
            else exclude.add("include_data_types")
        )
        include.add("ds_file_format") if (self.ds_write_mode == "write") else exclude.add("ds_file_format")
        (
            include.add("create_temporary_container")
            if (((self.enable_parallel_write)) and (self.ds_write_mode == "write"))
            else exclude.add("create_temporary_container")
        )
        (
            include.add("file_exists")
            if (((not self.append_unique_identifier)) and (self.ds_write_mode == "write"))
            else exclude.add("file_exists")
        )
        (
            include.add("delimited_syntax_row_delimiter")
            if (((self.ds_file_format == "delimited")) and (self.ds_write_mode == "write"))
            else exclude.add("delimited_syntax_row_delimiter")
        )
        (
            include.add("delimited_syntax_field_delimiter")
            if (((self.ds_file_format == "delimited")) and (self.ds_write_mode == "write"))
            else exclude.add("delimited_syntax_field_delimiter")
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
            include.add("quote_character")
            if (



                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                                or (self.file_format == "delimited")
                            )



            )
            else exclude.add("quote_character")
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
            include.add("time_format")
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
            else exclude.add("time_format")
        )
        (
            include.add("delete_container")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                            or (self.write_mode == "delete")
                        )


            )
            else exclude.add("delete_container")
        )
        (
            include.add("encoding")
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
            else exclude.add("encoding")
        )
        (
            include.add("blob_type")
            if (
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
            else exclude.add("blob_type")
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
            include.add("timestamp_format")
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
            else exclude.add("timestamp_format")
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
            include.add("create_container")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value != "delete")
                            or (self.write_mode != "delete")
                        )


            )
            else exclude.add("create_container")
        )
        include.add("the_partition_columns") if (self.endpoint_folder) else exclude.add("the_partition_columns")
        (
            include.add("write_part_size")
            if (
                (
                    (
                        self.blob_type
                        and (
                            (hasattr(self.blob_type, "value") and self.blob_type.value == "block")
                            or (self.blob_type == "block")
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
            else exclude.add("write_part_size")
        )
        (
            include.add("partitioned")
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
                or (
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
            include.add("quote_numeric_values")
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
            else exclude.add("quote_numeric_values")
        )
        (
            include.add("include_types")
            if (
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
            )
            else exclude.add("include_types")
        )
        (
            include.add("decimal_format")
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
            else exclude.add("decimal_format")
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
            include.add("date_format")
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
            else exclude.add("date_format")
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
            include.add("enable_parallel_write")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("enable_parallel_write")
        )
        (
            include.add("delimited_syntax_field_formats_date_format")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_field_formats_date_format")
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
            include.add("delimited_syntax_field_formats_timestamp_format")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_field_formats_timestamp_format")
        )
        (
            include.add("ds_create_container")
            if (

                    (((((self.ds_write_mode == "write")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_create_container")
        )
        (
            include.add("container_for_temporary_files")
            if (

                    (
                        (
                            (
                                ((self.enable_parallel_write))
                                or ((self.enable_parallel_write and "#" in str(self.enable_parallel_write)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("container_for_temporary_files")
        )
        (
            include.add("file_size_threshold")
            if (

                    (
                        (
                            (
                                ((self.append_unique_identifier))
                                or ((self.append_unique_identifier and "#" in str(self.append_unique_identifier)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("file_size_threshold")
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("quote_character")
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("time_format")
        )
        (
            include.add("delete_container")
            if (

                    (
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("delete_container")
        )
        (
            include.add("ds_file_name")
            if (

                    (((self.ds_write_mode == "write")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_name")
        )
        (
            include.add("delimited_syntax_encoding")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_encoding")
        )
        (
            include.add("delimited_syntax_escape")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_escape")
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("encoding")
        )
        (
            include.add("blob_type")
            if (

                    (
                        (
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
                                        self.table_format
                                        and (
                                            (hasattr(self.table_format, "value") and not self.table_format.value)
                                            or (not self.table_format)
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.table_format
                                        and (
                                            (hasattr(self.table_format, "value") and self.table_format.value == "file")
                                            or (self.table_format == "file")
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
            else exclude.add("blob_type")
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("timestamp_format")
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
            include.add("quotation_mark")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("quotation_mark")
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
            include.add("worksheet_name")
            if (

                    (
                        (
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
            else exclude.add("worksheet_name")
        )
        (
            include.add("table_format")
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("table_format")
        )
        (
            include.add("create_container")
            if (

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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("create_container")
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
            include.add("write_part_size")
            if (

                    (
                        (
                            (
                                self.blob_type
                                and (
                                    (hasattr(self.blob_type, "value") and self.blob_type.value == "block")
                                    or (self.blob_type == "block")
                                )
                            )
                        )
                        or (
                            (
                                self.blob_type
                                and (
                                    (
                                        hasattr(self.blob_type, "value")
                                        and self.blob_type.value
                                        and "#" in str(self.blob_type.value)
                                    )
                                    or ("#" in str(self.blob_type))
                                )
                            )
                        )
                    )
                    and (not self.ds_use_datastage)

            )
            else exclude.add("write_part_size")
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
            include.add("delimited_syntax_field_formats_time_format")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_field_formats_time_format")
        )
        (
            include.add("first_row_is_header")
            if (

                    (
                        (
                            (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                            and (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("first_row_is_header")
        )
        (
            include.add("delimited_syntax_field_formats_decimal_format")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_field_formats_decimal_format")
        )
        (
            include.add("delimited_syntax_null_value")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_null_value")
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
            include.add("include_byte_order_mark_for_unicode_encoding")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("include_byte_order_mark_for_unicode_encoding")
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
            include.add("append_unique_identifier")
            if (

                    (((self.ds_write_mode == "write")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("append_unique_identifier")
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("quote_numeric_values")
        )
        (
            include.add("include_data_types")
            if (

                    (
                        (
                            (
                                ((self.first_row_is_header))
                                or ((self.first_row_is_header and "#" in str(self.first_row_is_header)))
                            )
                            and (
                                ((self.ds_file_format == "comma-separated_value_csv"))
                                or ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("include_data_types")
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
            else exclude.add("include_types")
        )
        (
            include.add("ds_file_format")
            if (

                    (((self.ds_write_mode == "write")) or ((self.ds_write_mode and "#" in str(self.ds_write_mode))))
                    and (self.ds_use_datastage)

            )
            else exclude.add("ds_file_format")
        )
        (
            include.add("create_temporary_container")
            if (

                    (
                        (
                            (
                                ((self.enable_parallel_write))
                                or ((self.enable_parallel_write and "#" in str(self.enable_parallel_write)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("create_temporary_container")
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("decimal_format")
        )
        (
            include.add("file_exists")
            if (

                    (
                        (
                            (
                                ((not self.append_unique_identifier))
                                or ((self.append_unique_identifier and "#" in str(self.append_unique_identifier)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("file_exists")
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
                    and (not self.ds_use_datastage)

            )
            else exclude.add("date_format")
        )
        (
            include.add("delimited_syntax_row_delimiter")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_row_delimiter")
        )
        (
            include.add("delimited_syntax_field_delimiter")
            if (

                    (
                        (
                            (
                                ((self.ds_file_format == "delimited"))
                                or ((self.ds_file_format and "#" in str(self.ds_file_format)))
                            )
                            and (
                                ((self.ds_write_mode == "write"))
                                or ((self.ds_write_mode and "#" in str(self.ds_write_mode)))
                            )
                        )
                    )
                    and (self.ds_use_datastage)

            )
            else exclude.add("delimited_syntax_field_delimiter")
        )
        include.add("write_mode") if (not self.ds_use_datastage) else exclude.add("write_mode")
        include.add("ds_container") if (self.ds_use_datastage) else exclude.add("ds_container")
        include.add("ds_write_mode") if (self.ds_use_datastage) else exclude.add("ds_write_mode")
        include.add("the_partition_paths") if (not self.ds_use_datastage) else exclude.add("the_partition_paths")
        (
            include.add("the_cache_expiration")
            if (not self.ds_use_datastage)
            else exclude.add("the_cache_expiration")
        )
        include.add("the_cache_size") if (not self.ds_use_datastage) else exclude.add("the_cache_size")
        include.add("data_asset_name") if (self.create_data_asset) else exclude.add("data_asset_name")
        include.add("create_data_asset") if (()) else exclude.add("create_data_asset")
        (
            include.add("delete_container")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "delete")
                    or (self.write_mode == "delete")
                )
            )
            else exclude.add("delete_container")
        )
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
            include.add("quotation_mark")
            if (self.ds_file_format == "delimited") and (self.ds_write_mode == "write")
            else exclude.add("quotation_mark")
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
            else exclude.add("time_format")
        )
        (
            include.add("include_types")
            if (self.first_line_is_header == "yes")
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
            else exclude.add("include_types")
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
            include.add("file_size_threshold")
            if (self.append_unique_identifier == "true" or self.append_unique_identifier)
            and (self.ds_write_mode == "write")
            else exclude.add("file_size_threshold")
        )
        include.add("ds_file_format") if (self.ds_write_mode == "write") else exclude.add("ds_file_format")
        (
            include.add("partitioned")
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
            or (
                (
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
            )
            else exclude.add("partitioned")
        )
        (
            include.add("file_exists")
            if (self.append_unique_identifier == "false" or not self.append_unique_identifier)
            and (self.ds_write_mode == "write")
            else exclude.add("file_exists")
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
            else exclude.add("timestamp_format")
        )
        (
            include.add("delimited_syntax_field_delimiter")
            if (self.ds_file_format == "delimited") and (self.ds_write_mode == "write")
            else exclude.add("delimited_syntax_field_delimiter")
        )
        (
            include.add("append_unique_identifier")
            if (self.ds_write_mode == "write")
            else exclude.add("append_unique_identifier")
        )
        (
            include.add("include_byte_order_mark_for_unicode_encoding")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (self.ds_write_mode == "write")
            else exclude.add("include_byte_order_mark_for_unicode_encoding")
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
            include.add("delimited_syntax_row_delimiter")
            if (self.ds_file_format == "delimited") and (self.ds_write_mode == "write")
            else exclude.add("delimited_syntax_row_delimiter")
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
            include.add("create_container")
            if (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value != "delete")
                    or (self.write_mode != "delete")
                )
            )
            else exclude.add("create_container")
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
            include.add("delimited_syntax_encoding")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (self.ds_write_mode == "write")
            else exclude.add("delimited_syntax_encoding")
        )
        (
            include.add("first_row_is_header")
            if (self.ds_write_mode == "write")
            and (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            else exclude.add("first_row_is_header")
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
            else exclude.add("quote_character")
        )
        (
            include.add("delimited_syntax_field_formats_time_format")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (self.ds_write_mode == "write")
            else exclude.add("delimited_syntax_field_formats_time_format")
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
            include.add("container_for_temporary_files")
            if (self.enable_parallel_write == "true" or self.enable_parallel_write)
            and (self.ds_write_mode == "write")
            else exclude.add("container_for_temporary_files")
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
            include.add("delimited_syntax_field_formats_timestamp_format")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (self.ds_write_mode == "write")
            else exclude.add("delimited_syntax_field_formats_timestamp_format")
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
            else exclude.add("quote_numeric_values")
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
            include.add("ds_create_container")
            if (self.ds_write_mode and "write" in str(self.ds_write_mode))
            else exclude.add("ds_create_container")
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
            include.add("blob_type")
            if (

                    self.write_mode
                    and (
                        (hasattr(self.write_mode, "value") and self.write_mode.value != "delete")
                        or (self.write_mode != "delete")
                    )

            )
            and (
                (
                    self.table_format
                    and (
                        (hasattr(self.table_format, "value") and not self.table_format.value) or (not self.table_format)
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
            else exclude.add("blob_type")
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
            include.add("enable_parallel_write")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (self.ds_write_mode == "write")
            else exclude.add("enable_parallel_write")
        )
        (
            include.add("delimited_syntax_escape")
            if (self.ds_file_format == "delimited") and (self.ds_write_mode == "write")
            else exclude.add("delimited_syntax_escape")
        )
        (
            include.add("include_data_types")
            if (self.first_row_is_header == "true" or self.first_row_is_header)
            and (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (self.ds_write_mode == "write")
            else exclude.add("include_data_types")
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
            include.add("delimited_syntax_field_formats_decimal_format")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (self.ds_write_mode == "write")
            else exclude.add("delimited_syntax_field_formats_decimal_format")
        )
        (
            include.add("create_temporary_container")
            if (self.enable_parallel_write == "true" or self.enable_parallel_write)
            and (self.ds_write_mode == "write")
            else exclude.add("create_temporary_container")
        )
        (
            include.add("delimited_syntax_field_formats_date_format")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (self.ds_write_mode == "write")
            else exclude.add("delimited_syntax_field_formats_date_format")
        )
        (
            include.add("ds_file_name")
            if (self.ds_write_mode and "write" in str(self.ds_write_mode))
            else exclude.add("ds_file_name")
        )
        (
            include.add("write_part_size")
            if (
                self.blob_type
                and (
                    (hasattr(self.blob_type, "value") and self.blob_type.value == "block")
                    or (self.blob_type == "block")
                )
            )
            or (
                self.table_format
                and (
                    (hasattr(self.table_format, "value") and self.table_format.value == "iceberg")
                    or (self.table_format == "iceberg")
                )
            )
            else exclude.add("write_part_size")
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
            include.add("delimited_syntax_null_value")
            if (
                self.ds_file_format
                and "comma-separated_value_csv" in str(self.ds_file_format)
                and self.ds_file_format
                and "delimited" in str(self.ds_file_format)
            )
            and (self.ds_write_mode == "write")
            else exclude.add("delimited_syntax_null_value")
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
            "cell_range",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
            "container_source",
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
            "definition_source",
            "delimited_syntax_encoding",
            "delimited_syntax_escape",
            "delimited_syntax_field_delimiter",
            "delimited_syntax_field_formats_date_format",
            "delimited_syntax_field_formats_decimal_format",
            "delimited_syntax_field_formats_time_format",
            "delimited_syntax_field_formats_timestamp_format",
            "delimited_syntax_null_value",
            "delimited_syntax_row_delimiter",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "display_value_labels",
            "ds_file_format",
            "ds_java_heap_size",
            "ds_read_mode",
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
            "file_name_column",
            "file_name_source",
            "first_line",
            "first_line_is_header",
            "first_row_is_header",
            "flow_dirty",
            "generate_unicode_type_columns",
            "has_reference_output",
            "hide",
            "include_child_folders",
            "infer_as_varchar",
            "infer_null_as_empty_string",
            "infer_record_count",
            "infer_schema",
            "infer_timestamp_as_date",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "invalid_data_handling",
            "json_infer_record_count",
            "json_path",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "labels_as_names",
            "lookup_type",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "null_value",
            "output_acp_should_hide",
            "output_as_json",
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
            "quotation_mark",
            "quote_character",
            "read_mode",
            "read_part_size",
            "record_definition",
            "record_limit",
            "reject_mode",
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
            "authentication_method",
            "client_id",
            "client_secret",
            "connection_string",
            "current_output_link_type",
            "ds_read_mode",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "escape_character_value",
            "field_delimiter_value",
            "file_name",
            "file_name_source",
            "output_acp_should_hide",
            "password",
            "row_delimiter_value",
            "storage_account_url",
            "tenant_id",
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
            "append_unique_identifier",
            "blob_type",
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
            "container_for_temporary_files",
            "create_container",
            "create_data_asset",
            "create_temporary_container",
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
            "delete_container",
            "delimited_syntax_encoding",
            "delimited_syntax_escape",
            "delimited_syntax_field_delimiter",
            "delimited_syntax_field_formats_date_format",
            "delimited_syntax_field_formats_decimal_format",
            "delimited_syntax_field_formats_time_format",
            "delimited_syntax_field_formats_timestamp_format",
            "delimited_syntax_null_value",
            "delimited_syntax_row_delimiter",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "ds_container",
            "ds_create_container",
            "ds_file_format",
            "ds_file_name",
            "ds_java_heap_size",
            "ds_use_datastage",
            "ds_write_mode",
            "enable_flow_acp_control",
            "enable_parallel_write",
            "enable_schemaless_design",
            "encoding",
            "encryption_key",
            "endpoint_folder",
            "escape_character",
            "escape_character_value",
            "execution_mode",
            "field_delimiter",
            "field_delimiter_value",
            "file_exists",
            "file_format",
            "file_name",
            "file_size_threshold",
            "first_line_is_header",
            "first_row_is_header",
            "flow_dirty",
            "hide",
            "include_byte_order_mark_for_unicode_encoding",
            "include_data_types",
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
            "quotation_mark",
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
            "authentication_method",
            "blob_type",
            "client_id",
            "client_secret",
            "connection_string",
            "current_output_link_type",
            "data_asset_name",
            "ds_file_name",
            "ds_write_mode",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "escape_character_value",
            "field_delimiter_value",
            "file_name",
            "output_acp_should_hide",
            "password",
            "row_delimiter_value",
            "storage_account_url",
            "tenant_id",
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
        return {"min": 0, "max": 2}

    def get_allowed_as_source_props(self) -> bool:
        return True

    def get_allowed_as_target_props(self) -> bool:
        return True
