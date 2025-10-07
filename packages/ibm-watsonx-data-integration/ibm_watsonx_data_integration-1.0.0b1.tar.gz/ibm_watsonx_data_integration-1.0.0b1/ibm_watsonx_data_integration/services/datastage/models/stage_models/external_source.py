import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import EXTERNAL_SOURCE
from pydantic import Field
from typing import ClassVar


class external_source(BaseStage):

    op_name: ClassVar[str] = "PxExternalSource"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/PxExternalSource.svg"
    label: ClassVar[str] = "External Source"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    actual_field_length: int | None = Field(None, alias="actual_length")
    allow_all_zeros: EXTERNAL_SOURCE.AllowAllZeros | None = Field(
        EXTERNAL_SOURCE.AllowAllZeros.nofix_zero, alias="allow_all_zeros"
    )
    allow_per_column_mapping: EXTERNAL_SOURCE.AllowPerColumnMapping | None = Field(
        EXTERNAL_SOURCE.AllowPerColumnMapping.false, alias="allow_column_mapping"
    )
    allow_signed_import: EXTERNAL_SOURCE.AllowSignedImport | None = Field(
        EXTERNAL_SOURCE.AllowSignedImport.allow_signed_import, alias="allow_signed_import"
    )
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode_ronly: EXTERNAL_SOURCE.BufModeRonly | None = Field(
        EXTERNAL_SOURCE.BufModeRonly.default, alias="buf_mode_ronly"
    )
    buffer_free_run_percent: int | None = Field(50, alias="buf_free_run")
    buffering_mode: EXTERNAL_SOURCE.BufferingMode | None = Field(
        EXTERNAL_SOURCE.BufferingMode.default, alias="buf_mode"
    )
    byte_order: EXTERNAL_SOURCE.ByteOrder | None = Field(EXTERNAL_SOURCE.ByteOrder.native_endian, alias="byte_order")
    c_format: str | None = Field("", alias="c_format")
    character_set: EXTERNAL_SOURCE.CharacterSet | None = Field(EXTERNAL_SOURCE.CharacterSet.ascii, alias="charset")
    check_intact: EXTERNAL_SOURCE.CheckIntact | None = Field(
        EXTERNAL_SOURCE.CheckIntact.check_intact, alias="check_intact"
    )
    collecting: EXTERNAL_SOURCE.Collecting | None = Field(EXTERNAL_SOURCE.Collecting.auto, alias="coll_type")
    column_metadata_change_propagation: bool | None = Field(None, alias="auto_column_propagation")
    combinability_mode: EXTERNAL_SOURCE.CombinabilityMode | None = Field(
        EXTERNAL_SOURCE.CombinabilityMode.auto, alias="combinability"
    )
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_format: EXTERNAL_SOURCE.DataFormat | None = Field(EXTERNAL_SOURCE.DataFormat.text, alias="data_format")
    date_format: str | None = Field("", alias="date_format")
    date_options: EXTERNAL_SOURCE.DateOption | None = Field(EXTERNAL_SOURCE.DateOption.none, alias="dateOption")
    days_since: str | None = Field("", alias="days_since")
    db2_database_name: str | None = Field(None, alias="part_client_dbname")
    db2_instance_name: str | None = Field(None, alias="part_client_instance")
    db2_source_connection_required: str | None = Field("", alias="part_dbconnection")
    db2_table_name: str | None = Field(None, alias="part_table")
    decimal_options: EXTERNAL_SOURCE.DecimalOption | None = Field([], alias="decimalOption")
    decimal_packed: EXTERNAL_SOURCE.DecimalPacked | None = Field(
        EXTERNAL_SOURCE.DecimalPacked.packed, alias="decimal_packed"
    )
    decimal_packed_check: EXTERNAL_SOURCE.DecimalPackedCheck | None = Field(
        EXTERNAL_SOURCE.DecimalPackedCheck.check, alias="decimal_packed_check"
    )
    decimal_packed_sign_position: EXTERNAL_SOURCE.DecimalPackedSignPosition | None = Field(
        EXTERNAL_SOURCE.DecimalPackedSignPosition.trailing, alias="decimal_packed_sign_position"
    )
    decimal_packed_signed: EXTERNAL_SOURCE.DecimalPackedSigned | None = Field(
        EXTERNAL_SOURCE.DecimalPackedSigned.signed, alias="decimal_packed_signed"
    )
    decimal_sep_value: str | None = Field("", alias="decimal_sep_value")
    decimal_separator: EXTERNAL_SOURCE.DecimalSeparator | None = Field(
        EXTERNAL_SOURCE.DecimalSeparator.period, alias="decimal_separator"
    )
    delim_value: str | None = Field("", alias="delim_value")
    delimiter: EXTERNAL_SOURCE.Delimiter | None = Field(EXTERNAL_SOURCE.Delimiter.comma, alias="delim")
    delimiter_string: str | None = Field("", alias="delim_string")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    disk_write_increment_bytes: int | None = Field(1048576, alias="disk_write_inc")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execution_mode: EXTERNAL_SOURCE.ExecutionMode | None = Field(
        EXTERNAL_SOURCE.ExecutionMode.default_par, alias="execmode"
    )
    export_ebcdic_as_ascii: EXTERNAL_SOURCE.ExportEbcdicAsAscii | None = Field(
        EXTERNAL_SOURCE.ExportEbcdicAsAscii.export_ebcdic_as_ascii, alias="export_ebcdic_as_ascii"
    )
    field_defaults_options: EXTERNAL_SOURCE.FieldOption | None = Field(
        EXTERNAL_SOURCE.FieldOption.delimiter, alias="fieldOption"
    )
    field_max_width: int | None = Field(None, alias="max_width")
    field_width: int | None = Field(None, alias="width")
    fill_char: EXTERNAL_SOURCE.FillChar | None = Field(EXTERNAL_SOURCE.FillChar.null, alias="fill")
    fill_char_value: str | None = Field("", alias="fill_char_value")
    final_delim_value: str | None = Field("", alias="final_delim_value")
    final_delimiter: EXTERNAL_SOURCE.FinalDelimiter | None = Field(
        EXTERNAL_SOURCE.FinalDelimiter.end, alias="final_delim"
    )
    final_delimiter_string: str | None = Field("", alias="final_delim_string")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    general_options: EXTERNAL_SOURCE.GeneralOption | None = Field([], alias="generalOption")
    hide: bool | None = Field(False, alias="hide")
    import_ascii_as_ebcdic: EXTERNAL_SOURCE.ImportAsciiAsEbcdic | None = Field(
        EXTERNAL_SOURCE.ImportAsciiAsEbcdic.import_ascii_as_ebcdic, alias="import_ascii_as_ebcdic"
    )
    in_format: str | None = Field("", alias="in_format")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    intact: str | None = Field("", alias="intact")
    is_julian: EXTERNAL_SOURCE.IsJulian | None = Field(EXTERNAL_SOURCE.IsJulian.julian, alias="is_julian")
    is_midnight_seconds: EXTERNAL_SOURCE.IsMidnightSeconds | None = Field(
        EXTERNAL_SOURCE.IsMidnightSeconds.midnight_seconds, alias="is_midnight_seconds"
    )
    keep_file_partitions: EXTERNAL_SOURCE.KeepPartitions | None = Field(
        EXTERNAL_SOURCE.KeepPartitions.false, alias="keepPartitions"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    map_name: EXTERNAL_SOURCE.MapName | None = Field(EXTERNAL_SOURCE.MapName.UTF_8, alias="nls_map_name")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    maximum_memory_buffer_size_bytes: int | None = Field(3145728, alias="max_mem_buf_size")
    null_field_length: int | None = Field(None, alias="null_length")
    null_field_sep_value: str | None = Field("", alias="null_field_sep_value")
    null_field_value: str | None = Field("NULL", alias="null_field")
    null_field_value_separator: EXTERNAL_SOURCE.NullFieldValueSeparator | None = Field(
        EXTERNAL_SOURCE.NullFieldValueSeparator.comma, alias="null_field_sep"
    )
    numeric_options: EXTERNAL_SOURCE.NumericOption | None = Field([], alias="numericOption")
    out_format: str | None = Field("", alias="out_format")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    pad_char: EXTERNAL_SOURCE.PadChar | None = Field(EXTERNAL_SOURCE.PadChar.false_, alias="padchar")
    padchar_value: str | None = Field("", alias="padchar_value")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    partition_type: EXTERNAL_SOURCE.PartitionType | None = Field(
        EXTERNAL_SOURCE.PartitionType.auto, alias="part_type"
    )
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    precision: int | None = Field(None, alias="precision")
    prefix_bytes: EXTERNAL_SOURCE.PrefixBytes | None = Field(EXTERNAL_SOURCE.PrefixBytes.one, alias="prefix")
    preserve_partitioning: EXTERNAL_SOURCE.PreservePartitioning | None = Field(None, alias="preserve")
    print_field: EXTERNAL_SOURCE.PrintField | None = Field(
        EXTERNAL_SOURCE.PrintField.print_field, alias="print_field"
    )
    queue_upper_bound_size_bytes: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    quote: EXTERNAL_SOURCE.Quote | None = Field(EXTERNAL_SOURCE.Quote.double, alias="quote")
    quote_value: str | None = Field("", alias="quote_value")
    record_delim_value: str | None = Field("", alias="record_delim_value")
    record_delimiter: EXTERNAL_SOURCE.RecordDelimiter | None = Field(
        EXTERNAL_SOURCE.RecordDelimiter.newline, alias="record_delim"
    )
    record_delimiter_string: str | None = Field("", alias="record_delim_string")
    record_len_value: int | None = Field(0, alias="record_len_value")
    record_length: EXTERNAL_SOURCE.RecordLength | None = Field(
        EXTERNAL_SOURCE.RecordLength.fixed, alias="record_length"
    )
    record_level_options: EXTERNAL_SOURCE.RecLevelOption | None = Field([], alias="recLevelOption")
    record_prefix: EXTERNAL_SOURCE.RecordPrefix | None = Field(
        EXTERNAL_SOURCE.RecordPrefix.one, alias="record_prefix"
    )
    record_type: EXTERNAL_SOURCE.RecordType | None = Field(
        EXTERNAL_SOURCE.RecordType.type_implicit, alias="record_format"
    )
    reject_mode: EXTERNAL_SOURCE.RejectMode | None = Field(EXTERNAL_SOURCE.RejectMode.cont, alias="rejects")
    reject_reason_column: str | None = Field(None, alias="rejectReasonField")
    rounding: EXTERNAL_SOURCE.Rounding | None = Field(EXTERNAL_SOURCE.Rounding.trunc_zero, alias="round")
    row_number_column: str | None = Field(None, alias="recordNumberField")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    scale: int | None = Field(None, alias="scale")
    schema_file: str | None = Field(None, alias="schemafile")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    sorting_key: EXTERNAL_SOURCE.KeyColSelect | None = Field(
        EXTERNAL_SOURCE.KeyColSelect.default, alias="keyColSelect"
    )
    source_method: EXTERNAL_SOURCE.SourceMethod | None = Field(
        EXTERNAL_SOURCE.SourceMethod.program, alias="selection"
    )
    source_name_column: str | None = Field(None, alias="sourceNameField")
    source_program: list | None = Field([], alias="source")
    source_programs_file: list | None = Field([], alias="sourcelist")
    stable: bool | None = Field(None, alias="part_stable")
    stage_description: list | None = Field("", alias="stageDescription")
    string_options: EXTERNAL_SOURCE.StringOption | None = Field([], alias="stringOption")
    strip_bom: EXTERNAL_SOURCE.StripBom | None = Field(EXTERNAL_SOURCE.StripBom.false, alias="stripbom")
    time_format: str | None = Field("", alias="time_format")
    time_options: EXTERNAL_SOURCE.TimeOption | None = Field(EXTERNAL_SOURCE.TimeOption.none, alias="timeOption")
    timestamp_format: str | None = Field("", alias="timestamp_format")
    timestamp_options: EXTERNAL_SOURCE.TimestampOption | None = Field(
        EXTERNAL_SOURCE.TimestampOption.none, alias="timestampOption"
    )
    unique: bool | None = Field(None, alias="part_unique")
    vector_prefix: EXTERNAL_SOURCE.VectorPrefix | None = Field(
        EXTERNAL_SOURCE.VectorPrefix.one, alias="vector_prefix"
    )
    whether_check_intact: bool | None = Field(False, alias="check_intact_flag")
    whether_specify_null_field_value_separator: bool | None = Field(False, alias="null_field_sep_flag")

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("source_program") if (self.source_method == "program") else exclude.add("source_program")
        include.add("source_programs_file") if (self.source_method == "file") else exclude.add("source_programs_file")
        (
            include.add("preserve_partitioning")
            if (self.output_count and self.output_count > 0)
            else exclude.add("preserve_partitioning")
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

        include.add("schema_file") if (()) else exclude.add("schema_file")
        include.add("source_name_column") if (()) else exclude.add("source_name_column")
        include.add("row_number_column") if (()) else exclude.add("row_number_column")
        include.add("strip_bom") if (()) else exclude.add("strip_bom")
        include.add("reject_reason_column") if (()) else exclude.add("reject_reason_column")
        return include, exclude

    def get_input_ports_props(self) -> dict:
        include, exclude = self.validate()
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
        include, exclude = self.validate()
        props = {
            "additional_properties_set",
            "combinability_mode",
            "execution_mode",
            "keep_file_partitions",
            "preserve_partitioning",
            "reject_mode",
            "reject_reason_column",
            "row_number_column",
            "schema_file",
            "source_method",
            "source_name_column",
            "source_program",
            "source_programs_file",
            "strip_bom",
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

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "actual_field_length",
            "allow_all_zeros",
            "allow_per_column_mapping",
            "allow_signed_import",
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
            "combinability_mode",
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
            "fill_char",
            "fill_char_value",
            "final_delim_value",
            "final_delimiter",
            "final_delimiter_string",
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
            "null_field_length",
            "null_field_sep_value",
            "null_field_value",
            "null_field_value_separator",
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
            "source_method",
            "source_name_column",
            "source_program",
            "source_programs_file",
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
            "output_acp_should_hide",
            "source_method",
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
            "allow_all_zeros",
            "allow_per_column_mapping",
            "allow_signed_import",
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
            "combinability_mode",
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
            "fill_char",
            "fill_char_value",
            "final_delim_value",
            "final_delimiter",
            "final_delimiter_string",
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
            "null_field_length",
            "null_field_sep_value",
            "null_field_value",
            "null_field_value_separator",
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
            "source_method",
            "source_name_column",
            "source_program",
            "source_programs_file",
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
            "output_acp_should_hide",
            "source_method",
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
