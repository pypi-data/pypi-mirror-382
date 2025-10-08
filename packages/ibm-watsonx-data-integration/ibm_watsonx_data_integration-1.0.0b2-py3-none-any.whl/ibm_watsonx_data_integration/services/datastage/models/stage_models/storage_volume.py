import re
import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.storage_volume_connection import (
    StorageVolumeConn,
)
from ibm_watsonx_data_integration.services.datastage.models.enums import STORAGE_VOLUME
from pydantic import Field
from typing import ClassVar


class storage_volume(BaseStage):

    op_name: ClassVar[str] = "volumes"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/volumes.svg"
    label: ClassVar[str] = "Storage volume"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: StorageVolumeConn = StorageVolumeConn()
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: STORAGE_VOLUME.BufModeRonly | None = Field(
        STORAGE_VOLUME.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: STORAGE_VOLUME.BufferingMode | None = Field(
        STORAGE_VOLUME.BufferingMode.default, alias="buf_mode"
    )
    byte_limit: str | None = Field(None, alias="byte_limit")
    cell_range: str | None = Field(None, alias="range")
    codec_avro: STORAGE_VOLUME.CodecAvro | None = Field(None, alias="codec_avro")
    codec_csv: STORAGE_VOLUME.CodecCsv | None = Field(None, alias="codec_csv")
    codec_delimited: STORAGE_VOLUME.CodecDelimited | None = Field(None, alias="codec_delimited")
    codec_orc: STORAGE_VOLUME.CodecOrc | None = Field(None, alias="codec_orc")
    codec_parquet: STORAGE_VOLUME.CodecParquet | None = Field(None, alias="codec_parquet")
    collecting: STORAGE_VOLUME.Collecting | None = Field(STORAGE_VOLUME.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: STORAGE_VOLUME.CombinabilityMode | None = Field(
        STORAGE_VOLUME.CombinabilityMode.auto, alias="combinability"
    )
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
    decimal_rounding_mode: STORAGE_VOLUME.DecimalRoundingMode | None = Field(
        STORAGE_VOLUME.DecimalRoundingMode.floor, alias="decimal_rounding_mode"
    )
    decimal_separator: str | None = Field(None, alias="decimal_format_decimal_separator")
    default_maximum_length_for_columns: int | None = Field(20000, alias="default_max_string_binary_precision")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    display_value_labels: bool | None = Field(None, alias="display_value_labels")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    encoding: str | None = Field("utf-8", alias="encoding")
    encryption_key: str | None = Field(None, alias="encryption_key")
    escape_character: STORAGE_VOLUME.EscapeCharacter | None = Field(
        STORAGE_VOLUME.EscapeCharacter.none, alias="escape_character"
    )
    escape_character_value: str = Field(None, alias="escape_character_value")
    exclude_missing_values: bool | None = Field(None, alias="exclude_missing_values")
    execution_mode: STORAGE_VOLUME.ExecutionMode | None = Field(
        STORAGE_VOLUME.ExecutionMode.default_par, alias="execmode"
    )
    field_delimiter: STORAGE_VOLUME.FieldDelimiter | None = Field(
        STORAGE_VOLUME.FieldDelimiter.comma, alias="field_delimiter"
    )
    field_delimiter_value: str = Field(None, alias="field_delimiter_value")
    fields_xml_path: str | None = Field(None, alias="xml_path_fields")
    file_format: STORAGE_VOLUME.FileFormat | None = Field(STORAGE_VOLUME.FileFormat.csv, alias="file_format")
    file_name: str = Field(None, alias="file_name")
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
    invalid_data_handling: STORAGE_VOLUME.InvalidDataHandling | None = Field(
        STORAGE_VOLUME.InvalidDataHandling.fail, alias="invalid_data_handling"
    )
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
    partition_type: STORAGE_VOLUME.PartitionType | None = Field(STORAGE_VOLUME.PartitionType.auto, alias="part_type")
    partitioned: bool | None = Field(False, alias="partitioned")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve_partitioning: STORAGE_VOLUME.PreservePartitioning | None = Field(
        STORAGE_VOLUME.PreservePartitioning.default_propagate, alias="preserve"
    )
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    quote_character: STORAGE_VOLUME.QuoteCharacter | None = Field(
        STORAGE_VOLUME.QuoteCharacter.none, alias="quote_character"
    )
    quote_numeric_values: bool | None = Field(True, alias="quote_numerics")
    read_mode: STORAGE_VOLUME.ReadMode | None = Field(STORAGE_VOLUME.ReadMode.read_single, alias="read_mode")
    row_delimiter: STORAGE_VOLUME.RowDelimiter | None = Field(
        STORAGE_VOLUME.RowDelimiter.new_line, alias="row_delimiter"
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
    sorting_key: STORAGE_VOLUME.KeyColSelect | None = Field(
        STORAGE_VOLUME.KeyColSelect.default, alias="keyColSelect"
    )
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    store_shared_strings_in_the_temporary_file: bool | None = Field(None, alias="use_sst_temp_file")
    time_format: str | None = Field(None, alias="time_format")
    timestamp_format: str | None = Field(None, alias="timestamp_format")
    timezone_format: str | None = Field(None, alias="time_zone_format")
    trust_all_ssl_cert: bool | None = Field(False, alias="trust_all_ssl_cert")
    type_mapping: str | None = Field(None, alias="type_mapping")
    unique: bool | None = Field(None, alias="part_unique")
    use_4_digit_years_in_date_formats: bool | None = Field(None, alias="use_4_digit_year")
    use_field_formats: bool | None = Field(None, alias="use_field_formats")
    use_variable_formats: bool | None = Field(None, alias="use_variable_formats")
    worksheet_name: str | None = Field(None, alias="sheet_name")
    write_mode: STORAGE_VOLUME.WriteMode | None = Field(STORAGE_VOLUME.WriteMode.write, alias="write_mode")
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
            include.add("file_format")
            if (

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

                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "read_multiple_wildcard")
                                or (self.read_mode == "read_multiple_wildcard")
                            )

                    )
                    or (

                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "read_single")
                                or (self.read_mode == "read_single")
                            )

                    )

            )
            else exclude.add("file_format")
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
                    and (((not self.output_as_json)) or (self.output_as_json and "#" in str(self.output_as_json)))

            )
            else exclude.add("decimal_separator")
        )
        (
            include.add("infer_timestamp_as_date")
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
                or (

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
            else exclude.add("infer_timestamp_as_date")
        )
        (
            include.add("xml_path")
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
                or (

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
            else exclude.add("xml_path")
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
                or (

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
            else exclude.add("first_line")
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
                or (

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
            else exclude.add("null_value")
        )
        (
            include.add("cell_range")
            if (
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
            else exclude.add("cell_range")
        )
        (
            include.add("output_as_json")
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
                            (
                                hasattr(self.file_format, "value")
                                and self.file_format.value
                                and "#" in str(self.file_format.value)
                            )
                            or ("#" in str(self.file_format))
                        )

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
                or (

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
            else exclude.add("first_line_is_header")
        )
        (
            include.add("use_4_digit_years_in_date_formats")
            if (
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
            else exclude.add("use_4_digit_years_in_date_formats")
        )
        (
            include.add("json_infer_record_count")
            if (
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
            else exclude.add("json_infer_record_count")
        )
        (
            include.add("store_shared_strings_in_the_temporary_file")
            if (
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
                or (

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
                or (

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
                or (

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
            else exclude.add("escape_character")
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
                or (

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
            else exclude.add("invalid_data_handling")
        )
        (
            include.add("display_value_labels")
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
                    and (
                        ((not self.exclude_missing_values))
                        or (self.exclude_missing_values and "#" in str(self.exclude_missing_values))
                    )

            )
            else exclude.add("display_value_labels")
        )
        (
            include.add("file_format")
            if (
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

                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "read_multiple_wildcard")
                            or (self.read_mode == "read_multiple_wildcard")
                        )

                )
                or (

                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "read_single")
                            or (self.read_mode == "read_single")
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
            else exclude.add("file_format")
        )
        (
            include.add("escape_character_value")
            if (
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
            else exclude.add("escape_character_value")
        )
        (
            include.add("field_delimiter_value")
            if (
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
            else exclude.add("field_delimiter_value")
        )
        (
            include.add("row_delimiter")
            if (
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
            else exclude.add("row_delimiter")
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
                    and (((not self.output_as_json)) or (self.output_as_json and "#" in str(self.output_as_json)))

            )
            else exclude.add("time_format")
        )
        (
            include.add("fields_xml_path")
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
                    and (((self.xml_path)) or (self.xml_path and "#" in str(self.xml_path)))

            )
            else exclude.add("fields_xml_path")
        )
        (
            include.add("use_field_formats")
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
                or (

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
            else exclude.add("use_field_formats")
        )
        (
            include.add("schema_of_xml")
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
                    and (((self.infer_schema)) or (self.infer_schema and "#" in str(self.infer_schema)))

            )
            else exclude.add("schema_of_xml")
        )
        (
            include.add("json_path")
            if (
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
            else exclude.add("json_path")
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
                or (

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
            else exclude.add("encoding")
        )
        (
            include.add("field_delimiter")
            if (
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
            else exclude.add("field_delimiter")
        )
        (
            include.add("row_delimiter_value")
            if (
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
            else exclude.add("row_delimiter_value")
        )
        (
            include.add("use_variable_formats")
            if (

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
                    and (((not self.infer_schema)) or (self.infer_schema and "#" in str(self.infer_schema)))

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
                    and (((not self.output_as_json)) or (self.output_as_json and "#" in str(self.output_as_json)))

            )
            else exclude.add("timestamp_format")
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
                or (

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
            else exclude.add("decimal_rounding_mode")
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
                    and (((not self.output_as_json)) or (self.output_as_json and "#" in str(self.output_as_json)))

            )
            else exclude.add("decimal_format")
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
                    and (((self.infer_schema)) or (self.infer_schema and "#" in str(self.infer_schema)))

            )
            else exclude.add("infer_record_count")
        )
        (
            include.add("labels_as_names")
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
                or (

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
            else exclude.add("labels_as_names")
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
                    and (((not self.output_as_json)) or (self.output_as_json and "#" in str(self.output_as_json)))

            )
            else exclude.add("decimal_grouping_separator")
        )
        (
            include.add("exclude_missing_values")
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
                    and (
                        ((not self.display_value_labels))
                        or (self.display_value_labels and "#" in str(self.display_value_labels))
                    )

            )
            else exclude.add("exclude_missing_values")
        )
        (
            include.add("encryption_key")
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
                or (

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
            else exclude.add("encryption_key")
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
                    and (((not self.output_as_json)) or (self.output_as_json and "#" in str(self.output_as_json)))

            )
            else exclude.add("date_format")
        )
        (
            include.add("worksheet_name")
            if (
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
            else exclude.add("worksheet_name")
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
                    and (((self.infer_schema)) or (self.infer_schema and "#" in str(self.infer_schema)))

            )
            else exclude.add("type_mapping")
        )

        include.add("infer_as_varchar") if (()) else exclude.add("infer_as_varchar")
        include.add("infer_schema") if (()) else exclude.add("infer_schema")
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
            else exclude.add("file_format")
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
            else exclude.add("quote_character")
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
            include.add("codec_parquet")
            if (
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
                    and (re.match(r".*\.parquet$", self.file_name))
                )
            )
            else exclude.add("codec_parquet")
        )
        (
            include.add("codec_avro")
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
                    (
                        (
                            self.file_format
                            and (
                                (hasattr(self.file_format, "value") and not self.file_format.value)
                                or (not self.file_format)
                            )
                        )
                    )
                    and (re.match(r".*\.avro$", self.file_name))
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
            include.add("codec_delimited")
            if (


                        self.file_format
                        and (
                            (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                            or (self.file_format == "delimited")
                        )


            )
            else exclude.add("codec_delimited")
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
            include.add("file_format")
            if (


                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "write")
                            or (self.write_mode == "write")
                        )


            )
            else exclude.add("file_format")
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
            include.add("codec_orc")
            if (
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
                    and (re.match(r".*\.orc$", self.file_name))
                )
            )
            else exclude.add("codec_orc")
        )
        (
            include.add("names_as_labels")
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
                    and (re.match(r".*\.sav$", self.file_name))
                )
            )
            else exclude.add("names_as_labels")
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
                    and (re.match(r".*\.sav$", self.file_name))
                )
            )
            else exclude.add("encryption_key")
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
                or (

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
            else exclude.add("decimal_separator")
        )
        (
            include.add("codec_parquet")
            if (
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
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and not self.file_format.value)
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
                            or (self.file_name and "#" in str(self.file_name))
                        )

                )
                or (

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
            else exclude.add("codec_parquet")
        )
        (
            include.add("codec_avro")
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

                        (
                            (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and not self.file_format.value)
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
                            or (self.file_name and "#" in str(self.file_name))
                        )

                )
                or (

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
            else exclude.add("codec_avro")
        )
        (
            include.add("quote_character")
            if (
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
            else exclude.add("quote_character")
        )
        (
            include.add("codec_delimited")
            if (
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
            else exclude.add("codec_delimited")
        )
        (
            include.add("codec_csv")
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
                            (
                                hasattr(self.file_format, "value")
                                and self.file_format.value
                                and "#" in str(self.file_format.value)
                            )
                            or ("#" in str(self.file_format))
                        )

                )
            )
            else exclude.add("codec_csv")
        )
        (
            include.add("escape_character")
            if (
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
            else exclude.add("escape_character")
        )
        (
            include.add("file_format")
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
            else exclude.add("file_format")
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
                or (

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
            else exclude.add("time_format")
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
                or (

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
            else exclude.add("quote_numeric_values")
        )
        (
            include.add("include_types")
            if (

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
                        or (

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
            else exclude.add("include_types")
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
                            (
                                hasattr(self.file_format, "value")
                                and self.file_format.value
                                and "#" in str(self.file_format.value)
                            )
                            or ("#" in str(self.file_format))
                        )

                )
            )
            else exclude.add("encoding")
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
                or (

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
            else exclude.add("timestamp_format")
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
                or (

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
            else exclude.add("decimal_format")
        )
        (
            include.add("codec_orc")
            if (
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
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and not self.file_format.value)
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
                            or (self.file_name and "#" in str(self.file_name))
                        )

                )
                or (

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
            else exclude.add("codec_orc")
        )
        (
            include.add("names_as_labels")
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
                or (

                        (
                            (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and not self.file_format.value)
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
                            or (self.file_name and "#" in str(self.file_name))
                        )

                )
                or (

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
            else exclude.add("names_as_labels")
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
                or (

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
            else exclude.add("decimal_grouping_separator")
        )
        (
            include.add("encryption_key")
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
                or (

                        (
                            (
                                (
                                    self.file_format
                                    and (
                                        (hasattr(self.file_format, "value") and not self.file_format.value)
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
                            or (self.file_name and "#" in str(self.file_name))
                        )

                )
                or (

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
            else exclude.add("encryption_key")
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
                or (

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
            else exclude.add("date_format")
        )
        include.add("data_asset_name") if (self.create_data_asset) else exclude.add("data_asset_name")
        include.add("create_data_asset") if (()) else exclude.add("create_data_asset")
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
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                    or (self.file_format == "sav")
                )
            )
            or (
                (
                    self.file_format
                    and ((hasattr(self.file_format, "value") and not self.file_format.value) or (not self.file_format))
                )
                and (re.match(r".*\.sav$", self.file_name))
            )
            else exclude.add("encryption_key")
        )
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
            include.add("names_as_labels")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "sav")
                    or (self.file_format == "sav")
                )
            )
            or (
                (
                    self.file_format
                    and ((hasattr(self.file_format, "value") and not self.file_format.value) or (not self.file_format))
                )
                and (re.match(r".*\.sav$", self.file_name))
            )
            else exclude.add("names_as_labels")
        )
        (
            include.add("codec_orc")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "orc")
                    or (self.file_format == "orc")
                )
            )
            or (
                (
                    self.file_format
                    and ((hasattr(self.file_format, "value") and not self.file_format.value) or (not self.file_format))
                )
                and (re.match(r".*\.orc$", self.file_name))
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
            else exclude.add("file_format")
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
            include.add("codec_parquet")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "parquet")
                    or (self.file_format == "parquet")
                )
            )
            or (
                (
                    self.file_format
                    and ((hasattr(self.file_format, "value") and not self.file_format.value) or (not self.file_format))
                )
                and (re.match(r".*\.parquet$", self.file_name))
            )
            else exclude.add("codec_parquet")
        )
        (
            include.add("codec_avro")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "avro")
                    or (self.file_format == "avro")
                )
            )
            or (
                (
                    self.file_format
                    and ((hasattr(self.file_format, "value") and not self.file_format.value) or (not self.file_format))
                )
                and (re.match(r".*\.avro$", self.file_name))
            )
            else exclude.add("codec_avro")
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
            include.add("codec_delimited")
            if (
                self.file_format
                and (
                    (hasattr(self.file_format, "value") and self.file_format.value == "delimited")
                    or (self.file_format == "delimited")
                )
            )
            else exclude.add("codec_delimited")
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
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "encoding",
            "encryption_key",
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
            "quote_character",
            "read_mode",
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
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "escape_character_value",
            "field_delimiter_value",
            "file_name",
            "output_acp_should_hide",
            "row_delimiter_value",
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
            "codec_avro",
            "codec_csv",
            "codec_delimited",
            "codec_orc",
            "codec_parquet",
            "collecting",
            "column_metadata_change_propagation",
            "combinability_mode",
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
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "encoding",
            "encryption_key",
            "escape_character",
            "escape_character_value",
            "execution_mode",
            "field_delimiter",
            "field_delimiter_value",
            "file_format",
            "file_name",
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
            "time_format",
            "timestamp_format",
            "timezone_format",
            "unique",
            "worksheet_name",
            "write_mode",
        }
        required = {
            "current_output_link_type",
            "data_asset_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "escape_character_value",
            "field_delimiter_value",
            "file_name",
            "output_acp_should_hide",
            "row_delimiter_value",
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
