import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import SEQUENTIALFILE
from pydantic import Field
from typing import ClassVar


class sequentialfile(BaseStage):

    op_name: ClassVar[str] = "PxSequentialFile"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/PxSequentialFile.svg"
    label: ClassVar[str] = "Sequential file"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    actual_field_length: int | None = Field(None, alias="actual_length")
    allow_all_zeros: SEQUENTIALFILE.AllowAllZeros | None = Field(
        SEQUENTIALFILE.AllowAllZeros.nofix_zero, alias="allow_all_zeros"
    )
    allow_per_column_mapping: SEQUENTIALFILE.AllowPerColumnMapping | None = Field(
        SEQUENTIALFILE.AllowPerColumnMapping.false, alias="allow_column_mapping"
    )
    allow_signed_import: SEQUENTIALFILE.AllowSignedImport | None = Field(
        SEQUENTIALFILE.AllowSignedImport.allow_signed_import, alias="allow_signed_import"
    )
    bucket: str | None = Field(None, alias="bucket")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: SEQUENTIALFILE.BufModeRonly | None = Field(
        SEQUENTIALFILE.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: SEQUENTIALFILE.BufferingMode | None = Field(
        SEQUENTIALFILE.BufferingMode.default, alias="buf_mode"
    )
    byte_order: SEQUENTIALFILE.ByteOrder | None = Field(SEQUENTIALFILE.ByteOrder.native_endian, alias="byte_order")
    c_format: str | None = Field("", alias="c_format")
    case_sensitive: SEQUENTIALFILE.CiCs | None = Field(SEQUENTIALFILE.CiCs.cs, alias="ci-cs")
    character_set: SEQUENTIALFILE.CharacterSet | None = Field(SEQUENTIALFILE.CharacterSet.ascii, alias="charset")
    check_intact: SEQUENTIALFILE.CheckIntact | None = Field(
        SEQUENTIALFILE.CheckIntact.check_intact, alias="check_intact"
    )
    cleanup_on_failure: SEQUENTIALFILE.CleanupOnFailure | None = Field(
        SEQUENTIALFILE.CleanupOnFailure.false, alias="nocleanup"
    )
    collate: SEQUENTIALFILE.Collate | None = Field(SEQUENTIALFILE.Collate.OFF, alias="collation_sequence")
    collecting: SEQUENTIALFILE.Collecting | None = Field(SEQUENTIALFILE.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    column_name_check: bool | None = Field(None, alias="columnNameCheck")
    combinability_mode: SEQUENTIALFILE.CombinabilityMode | None = Field(
        SEQUENTIALFILE.CombinabilityMode.auto, alias="combinability"
    )
    compression_codec: SEQUENTIALFILE.CompressionCodec | None = Field(
        SEQUENTIALFILE.CompressionCodec.snappy, alias="codec_parquet"
    )
    connection: str | None = Field("", alias="file_connector")
    create_data_asset: bool | None = Field(False, alias="registerDataAsset")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_asset_name: str = Field(None, alias="dataAssetName")
    data_format: SEQUENTIALFILE.DataFormat | None = Field(SEQUENTIALFILE.DataFormat.text, alias="data_format")
    date_format: str | None = Field("", alias="date_format")
    date_options: SEQUENTIALFILE.DateOption | None = Field(SEQUENTIALFILE.DateOption.none, alias="dateOption")
    days_since: str | None = Field("", alias="days_since")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    decimal_options: SEQUENTIALFILE.DecimalOption | None = Field([], alias="decimalOption")
    decimal_packed: SEQUENTIALFILE.DecimalPacked | None = Field(
        SEQUENTIALFILE.DecimalPacked.packed, alias="decimal_packed"
    )
    decimal_packed_check: SEQUENTIALFILE.DecimalPackedCheck | None = Field(
        SEQUENTIALFILE.DecimalPackedCheck.check, alias="decimal_packed_check"
    )
    decimal_packed_sign_position: SEQUENTIALFILE.DecimalPackedSignPosition | None = Field(
        SEQUENTIALFILE.DecimalPackedSignPosition.trailing, alias="decimal_packed_sign_position"
    )
    decimal_packed_signed: SEQUENTIALFILE.DecimalPackedSigned | None = Field(
        SEQUENTIALFILE.DecimalPackedSigned.signed, alias="decimal_packed_signed"
    )
    decimal_sep_value: str | None = Field("", alias="decimal_sep_value")
    decimal_separator: SEQUENTIALFILE.DecimalSeparator | None = Field(
        SEQUENTIALFILE.DecimalSeparator.period, alias="decimal_separator"
    )
    delim_value: str | None = Field("", alias="delim_value")
    delimiter: SEQUENTIALFILE.Delimiter | None = Field(SEQUENTIALFILE.Delimiter.comma, alias="delim")
    delimiter_string: str | None = Field("", alias="delim_string")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    exclude_partition_string: SEQUENTIALFILE.ExcludePart | None = Field(
        SEQUENTIALFILE.ExcludePart.false, alias="excludePart"
    )
    execution_mode: SEQUENTIALFILE.ExecutionMode | None = Field(
        SEQUENTIALFILE.ExecutionMode.default_seq, alias="execmode"
    )
    export_ebcdic_as_ascii: SEQUENTIALFILE.ExportEbcdicAsAscii | None = Field(
        SEQUENTIALFILE.ExportEbcdicAsAscii.export_ebcdic_as_ascii, alias="export_ebcdic_as_ascii"
    )
    field_defaults_options: SEQUENTIALFILE.FieldOption | None = Field(
        SEQUENTIALFILE.FieldOption.delimiter, alias="fieldOption"
    )
    field_max_width: int | None = Field(None, alias="max_width")
    field_width: int | None = Field(None, alias="width")
    file: list = Field([], alias="file")
    file_format: SEQUENTIALFILE.FileFormat | None = Field(SEQUENTIALFILE.FileFormat.sequential, alias="file_format")
    file_location: SEQUENTIALFILE.FileLocation | None = Field(
        SEQUENTIALFILE.FileLocation.file_system, alias="file_location"
    )
    file_name_column: str | None = Field(None, alias="sourceNameField")
    file_pattern: list | None = Field([], alias="filepattern")
    file_plus: list = Field([], alias="file +")
    file_update_mode: SEQUENTIALFILE.AppendOverwrite | None = Field(
        SEQUENTIALFILE.AppendOverwrite.overwrite, alias="append-overwrite"
    )
    fill_char: SEQUENTIALFILE.FillChar | None = Field(SEQUENTIALFILE.FillChar.null, alias="fill")
    fill_char_value: str | None = Field("", alias="fill_char_value")
    filter: str | None = Field(None, alias="filter")
    final_delim_value: str | None = Field("", alias="final_delim_value")
    final_delimiter: SEQUENTIALFILE.FinalDelimiter | None = Field(
        SEQUENTIALFILE.FinalDelimiter.end, alias="final_delim"
    )
    final_delimiter_string: str | None = Field("", alias="final_delim_string")
    first_line_is_column_names: SEQUENTIALFILE.FirstLineColumnNames | None = Field(
        SEQUENTIALFILE.FirstLineColumnNames.false, alias="firstLineColumnNames"
    )
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    force_sequential: SEQUENTIALFILE.ForceSequential | None = Field(
        SEQUENTIALFILE.ForceSequential.false, alias="sequential"
    )
    general_options: SEQUENTIALFILE.GeneralOption | None = Field([], alias="generalOption")
    hide: bool | None = Field(False, alias="hide")
    import_ascii_as_ebcdic: SEQUENTIALFILE.ImportAsciiAsEbcdic | None = Field(
        SEQUENTIALFILE.ImportAsciiAsEbcdic.import_ascii_as_ebcdic, alias="import_ascii_as_ebcdic"
    )
    in_format: str | None = Field("", alias="in_format")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    intact: str | None = Field("", alias="intact")
    is_julian: SEQUENTIALFILE.IsJulian | None = Field(SEQUENTIALFILE.IsJulian.julian, alias="is_julian")
    is_midnight_seconds: SEQUENTIALFILE.IsMidnightSeconds | None = Field(
        SEQUENTIALFILE.IsMidnightSeconds.midnight_seconds, alias="is_midnight_seconds"
    )
    keep_file_partitions: SEQUENTIALFILE.KeepPartitions | None = Field(
        SEQUENTIALFILE.KeepPartitions.false, alias="keepPartitions"
    )
    key: str | None = Field(None, alias="key")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    map_name: SEQUENTIALFILE.MapName | None = Field(SEQUENTIALFILE.MapName.UTF_8, alias="nls_map_name")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_file_size: str = Field(None, alias="maxFileSize")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    missing_file_mode: SEQUENTIALFILE.MissingFile | None = Field(
        SEQUENTIALFILE.MissingFile.custom, alias="missingFile"
    )
    null_field_length: int | None = Field(None, alias="null_length")
    null_field_sep_value: str | None = Field("", alias="null_field_sep_value")
    null_field_value: str | None = Field("NULL", alias="null_field")
    null_field_value_separator: SEQUENTIALFILE.NullFieldValueSeparator | None = Field(
        SEQUENTIALFILE.NullFieldValueSeparator.comma, alias="null_field_sep"
    )
    nulls_position: SEQUENTIALFILE.NullsPosition | None = Field(SEQUENTIALFILE.NullsPosition.first, alias="nulls")
    number_of_readers_per_node: int | None = Field(1, alias="readers")
    numeric_options: SEQUENTIALFILE.NumericOption | None = Field([], alias="numericOption")
    out_format: str | None = Field("", alias="out_format")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    pad_char: SEQUENTIALFILE.PadChar | None = Field(SEQUENTIALFILE.PadChar.false_, alias="padchar")
    padchar_value: str | None = Field("", alias="padchar_value")
    page_size: int | None = Field(1048576, alias="page_size")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    partition_type: SEQUENTIALFILE.PartitionType | None = Field(SEQUENTIALFILE.PartitionType.auto, alias="part_type")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    precision: int | None = Field(None, alias="precision")
    prefix_bytes: SEQUENTIALFILE.PrefixBytes | None = Field(SEQUENTIALFILE.PrefixBytes.one, alias="prefix")
    preserve_partitioning: SEQUENTIALFILE.PreservePartitioning | None = Field(
        SEQUENTIALFILE.PreservePartitioning.default_clear, alias="preserve"
    )
    print_field: SEQUENTIALFILE.PrintField | None = Field(SEQUENTIALFILE.PrintField.print_field, alias="print_field")
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    quote: SEQUENTIALFILE.Quote | None = Field(SEQUENTIALFILE.Quote.double, alias="quote")
    quote_value: str | None = Field("", alias="quote_value")
    read_batch_size: int | None = Field(10000, alias="read_batch_size")
    read_entire_file_as_one_column: bool | None = Field(False, alias="read_file_as_one_column")
    read_first_rows: int | None = Field(None, alias="first")
    read_from_multiple_nodes: SEQUENTIALFILE.ReadFromMultipleNodes | None = Field(
        SEQUENTIALFILE.ReadFromMultipleNodes.no, alias="multinode"
    )
    read_method: SEQUENTIALFILE.ReadMethod | None = Field(SEQUENTIALFILE.ReadMethod.file, alias="selection")
    record_delim_value: str | None = Field("", alias="record_delim_value")
    record_delimiter: SEQUENTIALFILE.RecordDelimiter | None = Field(
        SEQUENTIALFILE.RecordDelimiter.newline, alias="record_delim"
    )
    record_delimiter_string: str | None = Field("", alias="record_delim_string")
    record_len_value: int | None = Field(0, alias="record_len_value")
    record_length: SEQUENTIALFILE.RecordLength | None = Field(
        SEQUENTIALFILE.RecordLength.fixed, alias="record_length"
    )
    record_level_options: SEQUENTIALFILE.RecLevelOption | None = Field([], alias="recLevelOption")
    record_prefix: SEQUENTIALFILE.RecordPrefix | None = Field(SEQUENTIALFILE.RecordPrefix.one, alias="record_prefix")
    record_type: SEQUENTIALFILE.RecordType | None = Field(
        SEQUENTIALFILE.RecordType.type_implicit, alias="record_format"
    )
    reject_mode: SEQUENTIALFILE.RejectMode | None = Field(SEQUENTIALFILE.RejectMode.cont, alias="rejects")
    reject_reason_column: str | None = Field(None, alias="rejectReasonField")
    report_progress: SEQUENTIALFILE.ReportProgress | None = Field(
        SEQUENTIALFILE.ReportProgress.yes, alias="reportProgress"
    )
    rich_file: list | None = Field([], alias="rich_file")
    rich_file_plus: list | None = Field([], alias="rich_file +")
    richfile: list = Field([], alias="richfile")
    richfile_plus: list = Field([], alias="richfile +")
    root_file_string: str | None = Field(None, alias="filepath")
    rounding: SEQUENTIALFILE.Rounding | None = Field(SEQUENTIALFILE.Rounding.trunc_zero, alias="round")
    row_group_size: int | None = Field(1000000, alias="block_size")
    row_number_column: str | None = Field(None, alias="recordNumberField")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    scale: int | None = Field(None, alias="scale")
    schema_file: str | None = Field(None, alias="schemafile")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_as_ebcdic: SEQUENTIALFILE.SortAsEbcdic | None = Field(SEQUENTIALFILE.SortAsEbcdic.false, alias="ebcdic")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sort_order: SEQUENTIALFILE.AscDesc | None = Field(SEQUENTIALFILE.AscDesc.asc, alias="asc-desc")
    sorting_key: SEQUENTIALFILE.KeyColSelect | None = Field(
        SEQUENTIALFILE.KeyColSelect.default, alias="keyColSelect"
    )
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    string_options: SEQUENTIALFILE.StringOption | None = Field([], alias="stringOption")
    strip_bom: SEQUENTIALFILE.StripBom | None = Field(SEQUENTIALFILE.StripBom.false, alias="stripbom")
    time_format: str | None = Field("", alias="time_format")
    time_options: SEQUENTIALFILE.TimeOption | None = Field(SEQUENTIALFILE.TimeOption.none, alias="timeOption")
    timestamp_format: str | None = Field("", alias="timestamp_format")
    timestamp_options: SEQUENTIALFILE.TimestampOption | None = Field(
        SEQUENTIALFILE.TimestampOption.none, alias="timestampOption"
    )
    unique: bool | None = Field(None, alias="part_unique")
    use_value_in_filename: SEQUENTIALFILE.UseValueInFilename | None = Field(
        SEQUENTIALFILE.UseValueInFilename.false, alias="include"
    )
    vector_prefix: SEQUENTIALFILE.VectorPrefix | None = Field(SEQUENTIALFILE.VectorPrefix.one, alias="vector_prefix")
    whether_check_intact: bool | None = Field(False, alias="check_intact_flag")
    whether_specify_null_field_value_separator: bool | None = Field(False, alias="null_field_sep_flag")
    write_method: SEQUENTIALFILE.WriteMethod | None = Field(SEQUENTIALFILE.WriteMethod.specific, alias="writemethod")

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("root_file_string") if (()) else exclude.add("root_file_string")
        include.add("force_sequential") if (()) else exclude.add("force_sequential")
        include.add("exclude_partition_string") if (()) else exclude.add("exclude_partition_string")
        include.add("key") if (()) else exclude.add("key")
        include.add("use_value_in_filename") if (()) else exclude.add("use_value_in_filename")
        include.add("case_sensitive") if (()) else exclude.add("case_sensitive")
        include.add("nulls_position") if (()) else exclude.add("nulls_position")
        include.add("sort_as_ebcdic") if (()) else exclude.add("sort_as_ebcdic")
        include.add("schema_file") if (()) else exclude.add("schema_file")
        include.add("filter") if (()) else exclude.add("filter")
        include.add("maximum_file_size") if (()) else exclude.add("maximum_file_size")

        include.add("row_group_size") if (self.file_format == "parquet") else exclude.add("row_group_size")
        include.add("page_size") if (self.file_format == "parquet") else exclude.add("page_size")
        include.add("compression_codec") if (self.file_format == "parquet") else exclude.add("compression_codec")
        include.add("file_plus") if (self.read_method == "file") else exclude.add("file_plus")
        include.add("missing_file_mode") if (self.read_method == "file") else exclude.add("missing_file_mode")
        include.add("collate") if (((self.write_method == "filepattern")) and (self.key)) else exclude.add("collate")
        include.add("bucket") if (self.file_location != "file_system") else exclude.add("bucket")
        include.add("connection") if (self.file_location != "file_system") else exclude.add("connection")
        include.add("richfile") if (self.file_location != "file_system") else exclude.add("richfile")
        (
            include.add("file")
            if (((self.write_method == " ")) and (self.file_location == "file_system"))
            else exclude.add("file")
        )
        (
            include.add("first_line_is_column_names")
            if (
                (((self.input_count and self.input_count > 0)) and (()))
                or (((self.input_count and self.input_count > 0)) and (()) and (not self.filter))
            )
            else exclude.add("first_line_is_column_names")
        )
        include.add("file_pattern") if (self.read_method == "pattern") else exclude.add("file_pattern")
        include.add("key") if (()) else exclude.add("key")
        include.add("sort_order") if (()) else exclude.add("sort_order")
        (
            include.add("preserve_partitioning")
            if (self.output_count and self.output_count > 0)
            else exclude.add("preserve_partitioning")
        )
        include.add("data_asset_name") if (self.create_data_asset) else exclude.add("data_asset_name")
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
                    ((self.show_part_type))
                    and ((not self.show_coll_type))
                    and ((self.partition_type != "auto"))
                    and ((self.partition_type != "db2connector"))
                    and ((self.partition_type != "modulus"))
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
                    ((self.show_coll_type))
                    and (
                        ((self.collecting == "ordered"))
                        or ((self.collecting == "roundrobin_coll"))
                        or ((self.collecting == "sortmerge"))
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
                        ((not self.show_part_type))
                        and ((self.show_coll_type))
                        and ((self.collecting != "auto"))
                        and ((self.show_sort_options))
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
                        ((not self.show_part_type))
                        and ((self.show_coll_type))
                        and ((self.collecting != "auto"))
                        and ((self.show_sort_options))
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
            include.add("final_delimiter")
            if (self.record_level_options and "final_delimiter" in str(self.record_level_options))
            else exclude.add("final_delimiter")
        )
        (
            include.add("final_delim_value")
            if (
                ((self.record_level_options and "final_delimiter" in str(self.record_level_options)))
                and (self.final_delimiter == " ")
            )
            else exclude.add("final_delim_value")
        )
        (
            include.add("fill_char")
            if (self.record_level_options and "fill" in str(self.record_level_options))
            else exclude.add("fill_char")
        )
        (
            include.add("fill_char_value")
            if (((self.record_level_options and "fill" in str(self.record_level_options))) and (self.fill_char == -1))
            else exclude.add("fill_char_value")
        )
        (
            include.add("final_delimiter_string")
            if (self.record_level_options and "final_delim_string" in str(self.record_level_options))
            else exclude.add("final_delimiter_string")
        )
        (
            include.add("intact")
            if (self.record_level_options and "intact" in str(self.record_level_options))
            else exclude.add("intact")
        )
        (
            include.add("whether_check_intact")
            if (self.record_level_options and "intact" in str(self.record_level_options))
            else exclude.add("whether_check_intact")
        )
        (
            include.add("check_intact")
            if (
                ((self.whether_check_intact))
                and (self.record_level_options and "intact" in str(self.record_level_options))
            )
            else exclude.add("check_intact")
        )
        (
            include.add("record_delimiter")
            if (self.record_level_options and "record_delimiter" in str(self.record_level_options))
            else exclude.add("record_delimiter")
        )
        (
            include.add("record_delim_value")
            if (
                ((self.record_level_options and "record_delimiter" in str(self.record_level_options)))
                and (self.record_delimiter == " ")
            )
            else exclude.add("record_delim_value")
        )
        (
            include.add("record_delimiter_string")
            if (self.record_level_options and "record_delim_string" in str(self.record_level_options))
            else exclude.add("record_delimiter_string")
        )
        (
            include.add("record_length")
            if (self.record_level_options and "record_length" in str(self.record_level_options))
            else exclude.add("record_length")
        )
        (
            include.add("record_len_value")
            if (
                ((self.record_level_options and "record_length" in str(self.record_level_options)))
                and (self.record_length == " ")
            )
            else exclude.add("record_len_value")
        )
        (
            include.add("record_prefix")
            if (self.record_level_options and "record_prefix" in str(self.record_level_options))
            else exclude.add("record_prefix")
        )
        (
            include.add("record_type")
            if (self.record_level_options and "record_format" in str(self.record_level_options))
            else exclude.add("record_type")
        )
        (
            include.add("delimiter")
            if (self.field_defaults_options and "delimiter" in str(self.field_defaults_options))
            else exclude.add("delimiter")
        )
        (
            include.add("delim_value")
            if (
                ((self.field_defaults_options and "delimiter" in str(self.field_defaults_options)))
                and (self.delimiter == " ")
            )
            else exclude.add("delim_value")
        )
        (
            include.add("quote")
            if (self.field_defaults_options and "quote" in str(self.field_defaults_options))
            else exclude.add("quote")
        )
        (
            include.add("quote_value")
            if (
                ((self.field_defaults_options and "quote" in str(self.field_defaults_options)))
                and (self.quote == " ")
            )
            else exclude.add("quote_value")
        )
        (
            include.add("actual_field_length")
            if (self.field_defaults_options and "actual_length" in str(self.field_defaults_options))
            else exclude.add("actual_field_length")
        )
        (
            include.add("delimiter_string")
            if (self.field_defaults_options and "delim_string" in str(self.field_defaults_options))
            else exclude.add("delimiter_string")
        )
        (
            include.add("null_field_length")
            if (self.field_defaults_options and "null_length" in str(self.field_defaults_options))
            else exclude.add("null_field_length")
        )
        (
            include.add("null_field_value")
            if (self.field_defaults_options and "null_field" in str(self.field_defaults_options))
            else exclude.add("null_field_value")
        )
        (
            include.add("whether_specify_null_field_value_separator")
            if (self.field_defaults_options and "null_field" in str(self.field_defaults_options))
            else exclude.add("whether_specify_null_field_value_separator")
        )
        (
            include.add("null_field_value_separator")
            if (
                ((self.whether_specify_null_field_value_separator))
                and (self.field_defaults_options and "null_field" in str(self.field_defaults_options))
            )
            else exclude.add("null_field_value_separator")
        )
        (
            include.add("null_field_sep_value")
            if (
                ((self.field_defaults_options and "null_field" in str(self.field_defaults_options)))
                and (self.whether_specify_null_field_value_separator)
                and (self.null_field_value_separator == " ")
            )
            else exclude.add("null_field_sep_value")
        )
        (
            include.add("prefix_bytes")
            if (self.field_defaults_options and "prefix_bytes" in str(self.field_defaults_options))
            else exclude.add("prefix_bytes")
        )
        (
            include.add("print_field")
            if (self.field_defaults_options and "print_field" in str(self.field_defaults_options))
            else exclude.add("print_field")
        )
        (
            include.add("vector_prefix")
            if (self.field_defaults_options and "vector_prefix" in str(self.field_defaults_options))
            else exclude.add("vector_prefix")
        )
        (
            include.add("byte_order")
            if (self.general_options and "byte_order" in str(self.general_options))
            else exclude.add("byte_order")
        )
        (
            include.add("character_set")
            if (self.general_options and "charset" in str(self.general_options))
            else exclude.add("character_set")
        )
        (
            include.add("data_format")
            if (self.general_options and "data_format" in str(self.general_options))
            else exclude.add("data_format")
        )
        (
            include.add("field_max_width")
            if (self.general_options and "max_width" in str(self.general_options))
            else exclude.add("field_max_width")
        )
        (
            include.add("field_width")
            if (self.general_options and "field_width" in str(self.general_options))
            else exclude.add("field_width")
        )
        (
            include.add("pad_char")
            if (self.general_options and "padchar" in str(self.general_options))
            else exclude.add("pad_char")
        )
        (
            include.add("padchar_value")
            if (((self.general_options and "padchar" in str(self.general_options))) and (self.pad_char == " "))
            else exclude.add("padchar_value")
        )
        (
            include.add("export_ebcdic_as_ascii")
            if (self.string_options and "export_ebcdic_as_ascii" in str(self.string_options))
            else exclude.add("export_ebcdic_as_ascii")
        )
        (
            include.add("import_ascii_as_ebcdic")
            if (self.string_options and "import_ascii_as_ebcdic" in str(self.string_options))
            else exclude.add("import_ascii_as_ebcdic")
        )
        (
            include.add("allow_all_zeros")
            if (self.decimal_options and "allow_all_zeros" in str(self.decimal_options))
            else exclude.add("allow_all_zeros")
        )
        (
            include.add("decimal_separator")
            if (self.decimal_options and "decimal_separator" in str(self.decimal_options))
            else exclude.add("decimal_separator")
        )
        (
            include.add("decimal_sep_value")
            if (
                ((self.decimal_options and "decimal_separator" in str(self.decimal_options)))
                and (self.decimal_separator == " ")
            )
            else exclude.add("decimal_sep_value")
        )
        (
            include.add("decimal_packed")
            if (self.decimal_options and "decimal_packed" in str(self.decimal_options))
            else exclude.add("decimal_packed")
        )
        (
            include.add("precision")
            if (self.decimal_options and "precision" in str(self.decimal_options))
            else exclude.add("precision")
        )
        (
            include.add("rounding")
            if (self.decimal_options and "round" in str(self.decimal_options))
            else exclude.add("rounding")
        )
        (
            include.add("scale")
            if (self.decimal_options and "scale" in str(self.decimal_options))
            else exclude.add("scale")
        )
        (
            include.add("decimal_packed_check")
            if (
                ((self.decimal_options and "decimal_packed" in str(self.decimal_options)))
                and (self.decimal_packed == "packed")
            )
            else exclude.add("decimal_packed_check")
        )
        (
            include.add("decimal_packed_sign_position")
            if (
                ((self.decimal_options and "decimal_packed" in str(self.decimal_options)))
                and (self.decimal_packed != "packed")
            )
            else exclude.add("decimal_packed_sign_position")
        )
        (
            include.add("decimal_packed_signed")
            if (
                ((self.decimal_options and "decimal_packed" in str(self.decimal_options)))
                and (((self.decimal_packed == "packed")) or (self.decimal_packed == "zoned"))
            )
            else exclude.add("decimal_packed_signed")
        )
        (
            include.add("allow_signed_import")
            if (
                ((self.decimal_options and "decimal_packed" in str(self.decimal_options)))
                and (self.decimal_packed == "packed")
                and (self.decimal_packed_signed == "unsigned")
            )
            else exclude.add("allow_signed_import")
        )
        (
            include.add("c_format")
            if (self.numeric_options and "c_format" in str(self.numeric_options))
            else exclude.add("c_format")
        )
        (
            include.add("in_format")
            if (self.numeric_options and "in_format" in str(self.numeric_options))
            else exclude.add("in_format")
        )
        (
            include.add("out_format")
            if (self.numeric_options and "out_format" in str(self.numeric_options))
            else exclude.add("out_format")
        )
        include.add("days_since") if (self.date_options == "days_since") else exclude.add("days_since")
        include.add("date_format") if (self.date_options == "date_format") else exclude.add("date_format")
        include.add("is_julian") if (self.date_options == "is_julian") else exclude.add("is_julian")
        include.add("time_format") if (self.time_options == "time_format") else exclude.add("time_format")
        (
            include.add("is_midnight_seconds")
            if (self.time_options == "is_midnight_seconds")
            else exclude.add("is_midnight_seconds")
        )
        (
            include.add("timestamp_format")
            if (self.timestamp_options == "timestamp_format")
            else exclude.add("timestamp_format")
        )
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("number_of_readers_per_node") if (()) else exclude.add("number_of_readers_per_node")
        include.add("read_from_multiple_nodes") if (()) else exclude.add("read_from_multiple_nodes")
        include.add("file_name_column") if (()) else exclude.add("file_name_column")
        include.add("row_number_column") if (()) else exclude.add("row_number_column")
        include.add("read_first_rows") if (()) else exclude.add("read_first_rows")
        include.add("strip_bom") if (()) else exclude.add("strip_bom")
        include.add("reject_reason_column") if (()) else exclude.add("reject_reason_column")
        include.add("bucket") if (self.file_location != "file_system") else exclude.add("bucket")
        include.add("connection") if (self.file_location != "file_system") else exclude.add("connection")
        include.add("richfile_plus") if (self.file_location != "file_system") else exclude.add("richfile_plus")
        include.add("read_batch_size") if (self.file_format == "parquet") else exclude.add("read_batch_size")
        (
            include.add("file_plus")
            if (((self.read_method == "file")) and (self.file_location == "file_system"))
            else exclude.add("file_plus")
        )
        include.add("missing_file_mode") if (self.read_method == "file") else exclude.add("missing_file_mode")
        include.add("report_progress") if ((()) or ((()) and (not self.filter))) else exclude.add("report_progress")
        (
            include.add("collate")
            if (((self.write_method == "filepattern")) and (self.key is not None))
            else exclude.add("collate")
        )
        include.add("file") if (self.write_method == " ") else exclude.add("file")
        (
            include.add("first_line_is_column_names")
            if (
                (
                    ((self.input_count == 0))
                    and ((self.output_count and self.output_count > 0))
                    and (())
                    and (())
                    and (())
                )
                or (
                    ((self.input_count == 0))
                    and (self.output_count and self.output_count > 0)
                    and (())
                    and (())
                    and (self.read_from_multiple_nodes != "yes")
                    and (())
                )
                or (
                    ((self.input_count == 0))
                    and (self.output_count and self.output_count > 0)
                    and (())
                    and (not self.filter)
                    and (())
                    and (())
                )
                or (
                    ((self.input_count == 0))
                    and (self.output_count and self.output_count > 0)
                    and (())
                    and (not self.filter)
                    and (())
                    and (self.read_from_multiple_nodes != "yes")
                    and (())
                )
            )
            else exclude.add("first_line_is_column_names")
        )
        (
            include.add("final_delimiter")
            if (
                ((self.record_level_options and "final_delimiter" in str(self.record_level_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("final_delimiter")
        )
        (
            include.add("final_delim_value")
            if (
                ((self.record_level_options and "final_delimiter" in str(self.record_level_options)))
                and (self.final_delimiter == " ")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("final_delim_value")
        )
        (
            include.add("fill_char")
            if (
                ((self.record_level_options and "fill" in str(self.record_level_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("fill_char")
        )
        (
            include.add("fill_char_value")
            if (
                ((self.record_level_options and "fill" in str(self.record_level_options)))
                and (self.fill_char == -1)
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("fill_char_value")
        )
        (
            include.add("final_delimiter_string")
            if (
                ((self.record_level_options and "final_delim_string" in str(self.record_level_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("final_delimiter_string")
        )
        (
            include.add("intact")
            if (
                ((self.record_level_options and "intact" in str(self.record_level_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("intact")
        )
        (
            include.add("whether_check_intact")
            if (
                ((self.record_level_options and "intact" in str(self.record_level_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("whether_check_intact")
        )
        (
            include.add("check_intact")
            if (
                ((self.whether_check_intact))
                and (self.record_level_options and "intact" in str(self.record_level_options))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("check_intact")
        )
        (
            include.add("record_delimiter")
            if (
                ((self.record_level_options and "record_delimiter" in str(self.record_level_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("record_delimiter")
        )
        (
            include.add("record_delim_value")
            if (
                ((self.record_level_options and "record_delimiter" in str(self.record_level_options)))
                and (self.record_delimiter == " ")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("record_delim_value")
        )
        (
            include.add("record_delimiter_string")
            if (
                ((self.record_level_options and "record_delim_string" in str(self.record_level_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("record_delimiter_string")
        )
        (
            include.add("record_length")
            if (
                ((self.record_level_options and "record_length" in str(self.record_level_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("record_length")
        )
        (
            include.add("record_len_value")
            if (
                ((self.record_level_options and "record_length" in str(self.record_level_options)))
                and (self.record_length == " ")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("record_len_value")
        )
        (
            include.add("record_type")
            if (
                ((self.record_level_options and "record_format" in str(self.record_level_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("record_type")
        )
        (
            include.add("delimiter")
            if (
                ((self.field_defaults_options and "delimiter" in str(self.field_defaults_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("delimiter")
        )
        (
            include.add("delim_value")
            if (
                ((self.field_defaults_options and "delimiter" in str(self.field_defaults_options)))
                and (self.delimiter == " ")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("delim_value")
        )
        (
            include.add("quote")
            if (
                ((self.field_defaults_options and "quote" in str(self.field_defaults_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("quote")
        )
        (
            include.add("quote_value")
            if (
                ((self.field_defaults_options and "quote" in str(self.field_defaults_options)))
                and (self.quote == " ")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("quote_value")
        )
        (
            include.add("actual_field_length")
            if (
                ((self.field_defaults_options and "actual_length" in str(self.field_defaults_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("actual_field_length")
        )
        (
            include.add("delimiter_string")
            if (
                ((self.field_defaults_options and "delim_string" in str(self.field_defaults_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("delimiter_string")
        )
        (
            include.add("null_field_length")
            if (
                ((self.field_defaults_options and "null_length" in str(self.field_defaults_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("null_field_length")
        )
        (
            include.add("null_field_value")
            if (
                ((self.field_defaults_options and "null_field" in str(self.field_defaults_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("null_field_value")
        )
        (
            include.add("whether_specify_null_field_value_separator")
            if (
                ((self.field_defaults_options and "null_field" in str(self.field_defaults_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("whether_specify_null_field_value_separator")
        )
        (
            include.add("null_field_value_separator")
            if (
                ((self.whether_specify_null_field_value_separator))
                and (self.field_defaults_options and "null_field" in str(self.field_defaults_options))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("null_field_value_separator")
        )
        (
            include.add("null_field_sep_value")
            if (
                ((self.field_defaults_options and "null_field" in str(self.field_defaults_options)))
                and (self.whether_specify_null_field_value_separator)
                and (self.null_field_value_separator == " ")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("null_field_sep_value")
        )
        (
            include.add("prefix_bytes")
            if (
                ((self.field_defaults_options and "prefix_bytes" in str(self.field_defaults_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("prefix_bytes")
        )
        (
            include.add("print_field")
            if (
                ((self.field_defaults_options and "print_field" in str(self.field_defaults_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("print_field")
        )
        (
            include.add("vector_prefix")
            if (
                ((self.field_defaults_options and "vector_prefix" in str(self.field_defaults_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("vector_prefix")
        )
        (
            include.add("byte_order")
            if (
                ((self.general_options and "byte_order" in str(self.general_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("byte_order")
        )
        (
            include.add("character_set")
            if (
                ((self.general_options and "charset" in str(self.general_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("character_set")
        )
        (
            include.add("data_format")
            if (
                ((self.general_options and "data_format" in str(self.general_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("data_format")
        )
        (
            include.add("field_max_width")
            if (
                ((self.general_options and "max_width" in str(self.general_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("field_max_width")
        )
        (
            include.add("field_width")
            if (
                ((self.general_options and "field_width" in str(self.general_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("field_width")
        )
        (
            include.add("pad_char")
            if (
                ((self.general_options and "padchar" in str(self.general_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("pad_char")
        )
        (
            include.add("padchar_value")
            if (
                ((self.general_options and "padchar" in str(self.general_options)))
                and (self.pad_char == " ")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("padchar_value")
        )
        (
            include.add("export_ebcdic_as_ascii")
            if (
                ((self.string_options and "export_ebcdic_as_ascii" in str(self.string_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("export_ebcdic_as_ascii")
        )
        (
            include.add("import_ascii_as_ebcdic")
            if (
                ((self.string_options and "import_ascii_as_ebcdic" in str(self.string_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("import_ascii_as_ebcdic")
        )
        (
            include.add("allow_all_zeros")
            if (
                ((self.decimal_options and "allow_all_zeros" in str(self.decimal_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("allow_all_zeros")
        )
        (
            include.add("decimal_separator")
            if (
                ((self.decimal_options and "decimal_separator" in str(self.decimal_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("decimal_separator")
        )
        (
            include.add("decimal_sep_value")
            if (
                ((self.decimal_options and "decimal_separator" in str(self.decimal_options)))
                and (self.decimal_separator == " ")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("decimal_sep_value")
        )
        (
            include.add("decimal_packed")
            if (
                ((self.decimal_options and "decimal_packed" in str(self.decimal_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("decimal_packed")
        )
        (
            include.add("precision")
            if (
                ((self.decimal_options and "precision" in str(self.decimal_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("precision")
        )
        (
            include.add("rounding")
            if (
                ((self.decimal_options and "round" in str(self.decimal_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("rounding")
        )
        (
            include.add("scale")
            if (
                ((self.decimal_options and "scale" in str(self.decimal_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("scale")
        )
        (
            include.add("decimal_packed_check")
            if (
                ((self.decimal_options and "decimal_packed" in str(self.decimal_options)))
                and (self.decimal_packed == "packed")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("decimal_packed_check")
        )
        (
            include.add("decimal_packed_sign_position")
            if (
                ((self.decimal_options and "decimal_packed" in str(self.decimal_options)))
                and (self.decimal_packed != "packed")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("decimal_packed_sign_position")
        )
        (
            include.add("decimal_packed_signed")
            if (
                ((self.decimal_options and "decimal_packed" in str(self.decimal_options)))
                and (((self.decimal_packed == "packed")) or (self.decimal_packed == "zoned"))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("decimal_packed_signed")
        )
        (
            include.add("allow_signed_import")
            if (
                ((self.decimal_options and "decimal_packed" in str(self.decimal_options)))
                and (self.decimal_packed == "packed")
                and (self.decimal_packed_signed == "unsigned")
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("allow_signed_import")
        )
        (
            include.add("c_format")
            if (
                ((self.numeric_options and "c_format" in str(self.numeric_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("c_format")
        )
        (
            include.add("in_format")
            if (
                ((self.numeric_options and "in_format" in str(self.numeric_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("in_format")
        )
        (
            include.add("out_format")
            if (
                ((self.numeric_options and "out_format" in str(self.numeric_options)))
                and (not self.read_entire_file_as_one_column)
            )
            else exclude.add("out_format")
        )
        (
            include.add("days_since")
            if (((self.date_options == "days_since")) and (not self.read_entire_file_as_one_column))
            else exclude.add("days_since")
        )
        (
            include.add("date_format")
            if (((self.date_options == "date_format")) and (not self.read_entire_file_as_one_column))
            else exclude.add("date_format")
        )
        (
            include.add("is_julian")
            if (((self.date_options == "is_julian")) and (not self.read_entire_file_as_one_column))
            else exclude.add("is_julian")
        )
        (
            include.add("time_format")
            if (((self.time_options == "time_format")) and (not self.read_entire_file_as_one_column))
            else exclude.add("time_format")
        )
        (
            include.add("is_midnight_seconds")
            if (((self.time_options == "is_midnight_seconds")) and (not self.read_entire_file_as_one_column))
            else exclude.add("is_midnight_seconds")
        )
        (
            include.add("timestamp_format")
            if (((self.timestamp_options == "timestamp_format")) and (not self.read_entire_file_as_one_column))
            else exclude.add("timestamp_format")
        )
        (
            include.add("record_level_options")
            if (not self.read_entire_file_as_one_column)
            else exclude.add("record_level_options")
        )
        (
            include.add("field_defaults_options")
            if (not self.read_entire_file_as_one_column)
            else exclude.add("field_defaults_options")
        )
        (
            include.add("general_options")
            if (not self.read_entire_file_as_one_column)
            else exclude.add("general_options")
        )
        (
            include.add("string_options")
            if (not self.read_entire_file_as_one_column)
            else exclude.add("string_options")
        )
        (
            include.add("decimal_options")
            if (not self.read_entire_file_as_one_column)
            else exclude.add("decimal_options")
        )
        (
            include.add("numeric_options")
            if (not self.read_entire_file_as_one_column)
            else exclude.add("numeric_options")
        )
        include.add("date_options") if (not self.read_entire_file_as_one_column) else exclude.add("date_options")
        include.add("time_options") if (not self.read_entire_file_as_one_column) else exclude.add("time_options")
        (
            include.add("timestamp_options")
            if (not self.read_entire_file_as_one_column)
            else exclude.add("timestamp_options")
        )
        return include, exclude

    def get_input_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "additional_properties",
            "case_sensitive",
            "cleanup_on_failure",
            "create_data_asset",
            "data_asset_name",
            "exclude_partition_string",
            "file",
            "file_update_mode",
            "filter",
            "first_line_is_column_names",
            "force_sequential",
            "key",
            "maximum_file_size",
            "nulls_position",
            "reject_mode",
            "rich_file",
            "root_file_string",
            "runtime_column_propagation",
            "schema_file",
            "sort_as_ebcdic",
            "sort_order",
            "target_additional_properties",
            "use_value_in_filename",
            "write_method",
        }
        required = {"data_asset_name", "file"}
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
        include, exclude = self.validate()
        props = {
            "file_name_column",
            "file_pattern",
            "file_plus",
            "filter",
            "first_line_is_column_names",
            "keep_file_partitions",
            "missing_file_mode",
            "number_of_readers_per_node",
            "output_additional_properties",
            "read_first_rows",
            "read_from_multiple_nodes",
            "read_method",
            "reject_mode",
            "reject_reason_column",
            "report_progress",
            "rich_file_plus",
            "row_number_column",
            "schema_file",
            "strip_bom",
        }
        required = {"file_plus"}
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

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "actual_field_length",
            "allow_all_zeros",
            "allow_per_column_mapping",
            "allow_signed_import",
            "bucket",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "byte_order",
            "c_format",
            "character_set",
            "check_intact",
            "collecting",
            "column_metadata_change_propagation",
            "column_name_check",
            "combinability_mode",
            "connection",
            "current_output_link_type",
            "data_format",
            "date_format",
            "date_options",
            "days_since",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "decimal_options",
            "decimal_packed",
            "decimal_packed_check",
            "decimal_packed_sign_position",
            "decimal_packed_signed",
            "decimal_sep_value",
            "decimal_separator",
            "delim_value",
            "delimiter",
            "delimiter_string",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execution_mode",
            "export_ebcdic_as_ascii",
            "field_defaults_options",
            "field_max_width",
            "field_width",
            "file_format",
            "file_location",
            "file_name_column",
            "file_pattern",
            "file_plus",
            "fill_char",
            "fill_char_value",
            "filter",
            "final_delim_value",
            "final_delimiter",
            "final_delimiter_string",
            "first_line_is_column_names",
            "flow_dirty",
            "general_options",
            "hide",
            "import_ascii_as_ebcdic",
            "in_format",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "intact",
            "is_julian",
            "is_midnight_seconds",
            "keep_file_partitions",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "map_name",
            "max_mem_buf_size_ronly",
            "maximum_memory_buffer_size_bytes",
            "missing_file_mode",
            "null_field_length",
            "null_field_sep_value",
            "null_field_value",
            "null_field_value_separator",
            "number_of_readers_per_node",
            "numeric_options",
            "out_format",
            "output_acp_should_hide",
            "output_additional_properties",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "pad_char",
            "padchar_value",
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
            "precision",
            "prefix_bytes",
            "preserve_partitioning",
            "print_field",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "quote",
            "quote_value",
            "read_batch_size",
            "read_entire_file_as_one_column",
            "read_first_rows",
            "read_from_multiple_nodes",
            "read_method",
            "record_delim_value",
            "record_delimiter",
            "record_delimiter_string",
            "record_len_value",
            "record_length",
            "record_level_options",
            "record_prefix",
            "record_type",
            "reject_mode",
            "reject_reason_column",
            "report_progress",
            "richfile_plus",
            "rounding",
            "row_number_column",
            "runtime_column_propagation",
            "scale",
            "schema_file",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "sorting_key",
            "stable",
            "stage_description",
            "string_options",
            "strip_bom",
            "time_format",
            "time_options",
            "timestamp_format",
            "timestamp_options",
            "unique",
            "vector_prefix",
            "whether_check_intact",
            "whether_specify_null_field_value_separator",
        }
        required = {
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "file_plus",
            "output_acp_should_hide",
            "read_method",
            "richfile_plus",
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

    def get_app_data_props(self) -> dict:
        return {
            "datastage": {
                "maxRejectOutputs": 1,
                "minRejectOutputs": 0,
                "maxReferenceInputs": 0,
                "minReferenceInputs": 0,
            }
        }

    def get_target_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "actual_field_length",
            "additional_properties",
            "allow_all_zeros",
            "allow_per_column_mapping",
            "allow_signed_import",
            "bucket",
            "buf_free_run_ronly",
            "buf_mode_ronly",
            "buffer_free_run_percent",
            "buffering_mode",
            "byte_order",
            "c_format",
            "case_sensitive",
            "character_set",
            "check_intact",
            "cleanup_on_failure",
            "collate",
            "collecting",
            "column_metadata_change_propagation",
            "column_name_check",
            "combinability_mode",
            "compression_codec",
            "connection",
            "create_data_asset",
            "current_output_link_type",
            "data_asset_name",
            "data_format",
            "date_format",
            "date_options",
            "days_since",
            "db2_database_name",
            "db2_instance_name",
            "db2_source_connection_required",
            "db2_table_name",
            "decimal_options",
            "decimal_packed",
            "decimal_packed_check",
            "decimal_packed_sign_position",
            "decimal_packed_signed",
            "decimal_sep_value",
            "decimal_separator",
            "delim_value",
            "delimiter",
            "delimiter_string",
            "disk_write_inc_ronly",
            "disk_write_increment_bytes",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "exclude_partition_string",
            "execution_mode",
            "export_ebcdic_as_ascii",
            "field_defaults_options",
            "field_max_width",
            "field_width",
            "file",
            "file_format",
            "file_location",
            "file_name_column",
            "file_pattern",
            "file_plus",
            "file_update_mode",
            "fill_char",
            "fill_char_value",
            "filter",
            "final_delim_value",
            "final_delimiter",
            "final_delimiter_string",
            "first_line_is_column_names",
            "flow_dirty",
            "force_sequential",
            "general_options",
            "hide",
            "import_ascii_as_ebcdic",
            "in_format",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "intact",
            "is_julian",
            "is_midnight_seconds",
            "keep_file_partitions",
            "key",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "map_name",
            "max_mem_buf_size_ronly",
            "maximum_file_size",
            "maximum_memory_buffer_size_bytes",
            "missing_file_mode",
            "null_field_length",
            "null_field_sep_value",
            "null_field_value",
            "null_field_value_separator",
            "nulls_position",
            "number_of_readers_per_node",
            "numeric_options",
            "out_format",
            "output_acp_should_hide",
            "output_additional_properties",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "pad_char",
            "padchar_value",
            "page_size",
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
            "precision",
            "prefix_bytes",
            "preserve_partitioning",
            "print_field",
            "queue_upper_bound_size_bytes",
            "queue_upper_size_ronly",
            "quote",
            "quote_value",
            "read_batch_size",
            "read_entire_file_as_one_column",
            "read_first_rows",
            "read_from_multiple_nodes",
            "read_method",
            "record_delim_value",
            "record_delimiter",
            "record_delimiter_string",
            "record_len_value",
            "record_length",
            "record_level_options",
            "record_prefix",
            "record_type",
            "reject_mode",
            "reject_reason_column",
            "report_progress",
            "richfile",
            "richfile_plus",
            "root_file_string",
            "rounding",
            "row_group_size",
            "row_number_column",
            "runtime_column_propagation",
            "scale",
            "schema_file",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_as_ebcdic",
            "sort_instructions",
            "sort_instructions_text",
            "sort_order",
            "sorting_key",
            "stable",
            "stage_description",
            "string_options",
            "strip_bom",
            "target_additional_properties",
            "time_format",
            "time_options",
            "timestamp_format",
            "timestamp_options",
            "unique",
            "use_value_in_filename",
            "vector_prefix",
            "whether_check_intact",
            "whether_specify_null_field_value_separator",
            "write_method",
        }
        required = {
            "current_output_link_type",
            "data_asset_name",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "file",
            "file_plus",
            "output_acp_should_hide",
            "read_method",
            "richfile",
            "richfile_plus",
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
