import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import EXTERNAL_TARGET
from pydantic import Field
from typing import ClassVar


class external_target(BaseStage):

    op_name: ClassVar[str] = "PxExternalTarget"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/PxExternalTarget.svg"
    label: ClassVar[str] = "External Target"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    actual_length: int | None = Field(None, alias="actual_length")
    allow_all_zeros: EXTERNAL_TARGET.AllowAllZeros | None = Field(
        EXTERNAL_TARGET.AllowAllZeros.nofix_zero, alias="allow_all_zeros"
    )
    allow_column_mapping: EXTERNAL_TARGET.AllowColumnMapping | None = Field(
        EXTERNAL_TARGET.AllowColumnMapping.false, alias="allow_column_mapping"
    )
    allow_signed_import: EXTERNAL_TARGET.AllowSignedImport | None = Field(
        EXTERNAL_TARGET.AllowSignedImport.allow_signed_import, alias="allow_signed_import"
    )
    auto_column_propagation: bool | None = Field(None, alias="auto_column_propagation")
    buf_free_run: int | None = Field(50, alias="buf_free_run")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode: EXTERNAL_TARGET.BufMode | None = Field(EXTERNAL_TARGET.BufMode.default, alias="buf_mode")
    buf_mode_ronly: EXTERNAL_TARGET.BufModeRonly | None = Field(
        EXTERNAL_TARGET.BufModeRonly.default, alias="buf_mode_ronly"
    )
    byte_order: EXTERNAL_TARGET.ByteOrder | None = Field(EXTERNAL_TARGET.ByteOrder.native_endian, alias="byte_order")
    c_format: str | None = Field("", alias="c_format")
    charset: EXTERNAL_TARGET.Charset | None = Field(EXTERNAL_TARGET.Charset.ascii, alias="charset")
    check_intact: EXTERNAL_TARGET.CheckIntact | None = Field(
        EXTERNAL_TARGET.CheckIntact.check_intact, alias="check_intact"
    )
    check_intact_flag: bool | None = Field(False, alias="check_intact_flag")
    coll_type: EXTERNAL_TARGET.CollType | None = Field(EXTERNAL_TARGET.CollType.auto, alias="coll_type")
    combinability: EXTERNAL_TARGET.Combinability | None = Field(
        EXTERNAL_TARGET.Combinability.auto, alias="combinability"
    )
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_format: EXTERNAL_TARGET.DataFormat | None = Field(EXTERNAL_TARGET.DataFormat.text, alias="data_format")
    date_format: str | None = Field("", alias="date_format")
    date_option: EXTERNAL_TARGET.DateOption | None = Field(EXTERNAL_TARGET.DateOption.none, alias="dateOption")
    days_since: str | None = Field("", alias="days_since")
    decimal_options: EXTERNAL_TARGET.DecimalOption | None = Field([], alias="decimalOption")
    decimal_packed: EXTERNAL_TARGET.DecimalPacked | None = Field(
        EXTERNAL_TARGET.DecimalPacked.packed, alias="decimal_packed"
    )
    decimal_packed_check: EXTERNAL_TARGET.DecimalPackedCheck | None = Field(
        EXTERNAL_TARGET.DecimalPackedCheck.check, alias="decimal_packed_check"
    )
    decimal_packed_sign_position: EXTERNAL_TARGET.DecimalPackedSignPosition | None = Field(
        EXTERNAL_TARGET.DecimalPackedSignPosition.trailing, alias="decimal_packed_sign_position"
    )
    decimal_packed_signed: EXTERNAL_TARGET.DecimalPackedSigned | None = Field(
        EXTERNAL_TARGET.DecimalPackedSigned.signed, alias="decimal_packed_signed"
    )
    decimal_sep_value: str | None = Field("", alias="decimal_sep_value")
    decimal_separator: EXTERNAL_TARGET.DecimalSeparator | None = Field(
        EXTERNAL_TARGET.DecimalSeparator.period, alias="decimal_separator"
    )
    delim: EXTERNAL_TARGET.Delim | None = Field(EXTERNAL_TARGET.Delim.comma, alias="delim")
    delim_string: str | None = Field("", alias="delim_string")
    delim_value: str | None = Field("", alias="delim_value")
    destination: list | None = Field([], alias="destination")
    destinationlist: list | None = Field([], alias="destinationlist")
    disk_write_inc: int | None = Field(1048576, alias="disk_write_inc")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execmode: EXTERNAL_TARGET.Execmode | None = Field(EXTERNAL_TARGET.Execmode.default_par, alias="execmode")
    export_ebcdic_as_ascii: EXTERNAL_TARGET.ExportEbcdicAsAscii | None = Field(
        EXTERNAL_TARGET.ExportEbcdicAsAscii.export_ebcdic_as_ascii, alias="export_ebcdic_as_ascii"
    )
    field_option: EXTERNAL_TARGET.FieldOption | None = Field(
        EXTERNAL_TARGET.FieldOption.delimiter, alias="fieldOption"
    )
    fill: EXTERNAL_TARGET.Fill | None = Field(EXTERNAL_TARGET.Fill.null, alias="fill")
    fill_char_value: str | None = Field("", alias="fill_char_value")
    final_delim: EXTERNAL_TARGET.FinalDelim | None = Field(EXTERNAL_TARGET.FinalDelim.end, alias="final_delim")
    final_delim_string: str | None = Field("", alias="final_delim_string")
    final_delim_value: str | None = Field("", alias="final_delim_value")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    general_option: EXTERNAL_TARGET.GeneralOption | None = Field([], alias="generalOption")
    hide: bool | None = Field(False, alias="hide")
    import_ascii_as_ebcdic: EXTERNAL_TARGET.ImportAsciiAsEbcdic | None = Field(
        EXTERNAL_TARGET.ImportAsciiAsEbcdic.import_ascii_as_ebcdic, alias="import_ascii_as_ebcdic"
    )
    in_format: str | None = Field("", alias="in_format")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    intact: str | None = Field("", alias="intact")
    is_julian: EXTERNAL_TARGET.IsJulian | None = Field(EXTERNAL_TARGET.IsJulian.julian, alias="is_julian")
    is_midnight_seconds: EXTERNAL_TARGET.IsMidnightSeconds | None = Field(
        EXTERNAL_TARGET.IsMidnightSeconds.midnight_seconds, alias="is_midnight_seconds"
    )
    key_col_select: EXTERNAL_TARGET.KeyColSelect | None = Field(
        EXTERNAL_TARGET.KeyColSelect.default, alias="keyColSelect"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    max_mem_buf_size: int | None = Field(3145728, alias="max_mem_buf_size")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    max_width: int | None = Field(None, alias="max_width")
    nls_map_name: EXTERNAL_TARGET.NlsMapName | None = Field(EXTERNAL_TARGET.NlsMapName.UTF_8, alias="nls_map_name")
    null_field: str | None = Field("NULL", alias="null_field")
    null_field_sep: EXTERNAL_TARGET.NullFieldSep | None = Field(
        EXTERNAL_TARGET.NullFieldSep.comma, alias="null_field_sep"
    )
    null_field_sep_flag: bool | None = Field(False, alias="null_field_sep_flag")
    null_field_sep_value: str | None = Field("", alias="null_field_sep_value")
    null_length: int | None = Field(None, alias="null_length")
    numeric_option: EXTERNAL_TARGET.NumericOption | None = Field([], alias="numericOption")
    out_format: str | None = Field("", alias="out_format")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    padchar: EXTERNAL_TARGET.Padchar | None = Field(EXTERNAL_TARGET.Padchar.false_, alias="padchar")
    padchar_value: str | None = Field("", alias="padchar_value")
    part_client_dbname: str | None = Field(None, alias="part_client_dbname")
    part_client_instance: str | None = Field(None, alias="part_client_instance")
    part_dbconnection: str | None = Field("", alias="part_dbconnection")
    part_stable: bool | None = Field(None, alias="part_stable")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_table: str | None = Field(None, alias="part_table")
    part_type: EXTERNAL_TARGET.PartType | None = Field(EXTERNAL_TARGET.PartType.auto, alias="part_type")
    part_unique: bool | None = Field(None, alias="part_unique")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    precision: int | None = Field(None, alias="precision")
    prefix: EXTERNAL_TARGET.Prefix | None = Field(EXTERNAL_TARGET.Prefix.one, alias="prefix")
    preserve: EXTERNAL_TARGET.Preserve | None = Field(EXTERNAL_TARGET.Preserve.default_propagate, alias="preserve")
    print_field: EXTERNAL_TARGET.PrintField | None = Field(
        EXTERNAL_TARGET.PrintField.print_field, alias="print_field"
    )
    queue_upper_size: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    quote: EXTERNAL_TARGET.Quote | None = Field(EXTERNAL_TARGET.Quote.double, alias="quote")
    quote_value: str | None = Field("", alias="quote_value")
    rec_level_option: EXTERNAL_TARGET.RecLevelOption | None = Field([], alias="recLevelOption")
    record_delim: EXTERNAL_TARGET.RecordDelim | None = Field(
        EXTERNAL_TARGET.RecordDelim.newline, alias="record_delim"
    )
    record_delim_string: str | None = Field("", alias="record_delim_string")
    record_delim_value: str | None = Field("", alias="record_delim_value")
    record_format: EXTERNAL_TARGET.RecordFormat | None = Field(
        EXTERNAL_TARGET.RecordFormat.type_implicit, alias="record_format"
    )
    record_len_value: int | None = Field(0, alias="record_len_value")
    record_length: EXTERNAL_TARGET.RecordLength | None = Field(
        EXTERNAL_TARGET.RecordLength.fixed, alias="record_length"
    )
    record_prefix: EXTERNAL_TARGET.RecordPrefix | None = Field(
        EXTERNAL_TARGET.RecordPrefix.one, alias="record_prefix"
    )
    rejects: EXTERNAL_TARGET.Rejects | None = Field(EXTERNAL_TARGET.Rejects.cont, alias="rejects")
    round: EXTERNAL_TARGET.Round | None = Field(EXTERNAL_TARGET.Round.trunc_zero, alias="round")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    scale: int | None = Field(None, alias="scale")
    schemafile: str | None = Field(None, alias="schemafile")
    selection: EXTERNAL_TARGET.Selection | None = Field(EXTERNAL_TARGET.Selection.program, alias="selection")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    stage_description: list | None = Field("", alias="stageDescription")
    string_option: EXTERNAL_TARGET.StringOption | None = Field([], alias="stringOption")
    time_format: str | None = Field("", alias="time_format")
    time_option: EXTERNAL_TARGET.TimeOption | None = Field(EXTERNAL_TARGET.TimeOption.none, alias="timeOption")
    timestamp_format: str | None = Field("", alias="timestamp_format")
    timestamp_option: EXTERNAL_TARGET.TimestampOption | None = Field(
        EXTERNAL_TARGET.TimestampOption.none, alias="timestampOption"
    )
    vector_prefix: EXTERNAL_TARGET.VectorPrefix | None = Field(
        EXTERNAL_TARGET.VectorPrefix.one, alias="vector_prefix"
    )
    width: int | None = Field(None, alias="width")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("schemafile") if (()) else exclude.add("schemafile")
        include.add("rejects") if (()) else exclude.add("rejects")

        include.add("destination") if (self.selection == "program") else exclude.add("destination")
        include.add("destinationlist") if (self.selection == "file") else exclude.add("destinationlist")
        include.add("preserve") if (self.output_count and self.output_count > 0) else exclude.add("preserve")
        include.add("max_mem_buf_size") if (self.buf_mode != "nobuffer") else exclude.add("max_mem_buf_size")
        include.add("buf_free_run") if (self.buf_mode != "nobuffer") else exclude.add("buf_free_run")
        include.add("queue_upper_size") if (self.buf_mode != "nobuffer") else exclude.add("queue_upper_size")
        include.add("disk_write_inc") if (self.buf_mode != "nobuffer") else exclude.add("disk_write_inc")
        (
            include.add("runtime_column_propagation")
            if (not self.enable_schemaless_design)
            else exclude.add("runtime_column_propagation")
        )
        (
            include.add("auto_column_propagation")
            if (not self.output_acp_should_hide)
            else exclude.add("auto_column_propagation")
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
            include.add("part_stable")
            if (
                ((self.show_part_type))
                and (self.part_type != "auto")
                and (self.part_type != "db2connector")
                and (self.show_sort_options)
            )
            else exclude.add("part_stable")
        )
        (
            include.add("part_unique")
            if (
                ((self.show_part_type))
                and (self.part_type != "auto")
                and (self.part_type != "db2connector")
                and (self.show_sort_options)
            )
            else exclude.add("part_unique")
        )
        (
            include.add("key_cols_part")
            if (
                (
                    ((self.show_part_type))
                    and ((not self.show_coll_type))
                    and ((self.part_type != "auto"))
                    and ((self.part_type != "db2connector"))
                    and ((self.part_type != "modulus"))
                )
                or (
                    ((self.show_part_type))
                    and (not self.show_coll_type)
                    and (self.part_type == "modulus")
                    and (self.perform_sort_modulus)
                )
            )
            else exclude.add("key_cols_part")
        )
        (
            include.add("part_dbconnection")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("part_dbconnection")
        )
        (
            include.add("part_client_dbname")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("part_client_dbname")
        )
        (
            include.add("part_client_instance")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("part_client_instance")
        )
        (
            include.add("part_table")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("part_table")
        )
        (
            include.add("perform_sort")
            if (((self.show_part_type)) and (((self.part_type == "hash")) or (self.part_type == "range")))
            else exclude.add("perform_sort")
        )
        (
            include.add("perform_sort_modulus")
            if (((self.show_part_type)) and (self.part_type == "modulus"))
            else exclude.add("perform_sort_modulus")
        )
        (
            include.add("key_col_select")
            if (
                ((self.show_part_type))
                and (self.part_type == "modulus")
                and (not self.perform_sort_modulus)
            )
            else exclude.add("key_col_select")
        )
        (
            include.add("sort_instructions")
            if (
                ((self.show_part_type))
                and (
                    ((self.part_type == "db2part"))
                    or (self.part_type == "entire")
                    or (self.part_type == "random")
                    or (self.part_type == "roundrobin")
                    or (self.part_type == "same")
                )
            )
            else exclude.add("sort_instructions")
        )
        (
            include.add("sort_instructions_text")
            if (
                ((self.show_part_type))
                and (
                    ((self.part_type == "db2part"))
                    or (self.part_type == "entire")
                    or (self.part_type == "random")
                    or (self.part_type == "roundrobin")
                    or (self.part_type == "same")
                )
            )
            else exclude.add("sort_instructions_text")
        )
        include.add("coll_type") if (self.show_coll_type) else exclude.add("coll_type")
        include.add("part_type") if (self.show_part_type) else exclude.add("part_type")
        (
            include.add("perform_sort_coll")
            if (
                (
                    ((self.show_coll_type))
                    and (
                        ((self.coll_type == "ordered"))
                        or ((self.coll_type == "roundrobin_coll"))
                        or ((self.coll_type == "sortmerge"))
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
                and (self.coll_type != "auto")
                and (((self.coll_type == "sortmerge")) or (self.perform_sort_coll))
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
                        and ((self.coll_type != "auto"))
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
                        and ((self.coll_type != "auto"))
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
            include.add("final_delim")
            if (self.rec_level_option and "final_delimiter" in str(self.rec_level_option))
            else exclude.add("final_delim")
        )
        (
            include.add("final_delim_value")
            if (
                ((self.rec_level_option and "final_delimiter" in str(self.rec_level_option)))
                and (self.final_delim == " ")
            )
            else exclude.add("final_delim_value")
        )
        (
            include.add("fill")
            if (self.rec_level_option and "fill" in str(self.rec_level_option))
            else exclude.add("fill")
        )
        (
            include.add("fill_char_value")
            if (((self.rec_level_option and "fill" in str(self.rec_level_option))) and (self.fill == -1))
            else exclude.add("fill_char_value")
        )
        (
            include.add("final_delim_string")
            if (self.rec_level_option and "final_delim_string" in str(self.rec_level_option))
            else exclude.add("final_delim_string")
        )
        (
            include.add("intact")
            if (self.rec_level_option and "intact" in str(self.rec_level_option))
            else exclude.add("intact")
        )
        (
            include.add("check_intact_flag")
            if (self.rec_level_option and "intact" in str(self.rec_level_option))
            else exclude.add("check_intact_flag")
        )
        (
            include.add("check_intact")
            if (
                ((self.check_intact_flag))
                and (self.rec_level_option and "intact" in str(self.rec_level_option))
            )
            else exclude.add("check_intact")
        )
        (
            include.add("record_delim")
            if (self.rec_level_option and "record_delimiter" in str(self.rec_level_option))
            else exclude.add("record_delim")
        )
        (
            include.add("record_delim_value")
            if (
                ((self.rec_level_option and "record_delimiter" in str(self.rec_level_option)))
                and (self.record_delim == " ")
            )
            else exclude.add("record_delim_value")
        )
        (
            include.add("record_delim_string")
            if (self.rec_level_option and "record_delim_string" in str(self.rec_level_option))
            else exclude.add("record_delim_string")
        )
        (
            include.add("record_length")
            if (self.rec_level_option and "record_length" in str(self.rec_level_option))
            else exclude.add("record_length")
        )
        (
            include.add("record_len_value")
            if (
                ((self.rec_level_option and "record_length" in str(self.rec_level_option)))
                and (self.record_length == " ")
            )
            else exclude.add("record_len_value")
        )
        (
            include.add("record_prefix")
            if (self.rec_level_option and "record_prefix" in str(self.rec_level_option))
            else exclude.add("record_prefix")
        )
        (
            include.add("record_format")
            if (self.rec_level_option and "record_format" in str(self.rec_level_option))
            else exclude.add("record_format")
        )
        (
            include.add("delim")
            if (self.field_option and "delimiter" in str(self.field_option))
            else exclude.add("delim")
        )
        (
            include.add("delim_value")
            if (((self.field_option and "delimiter" in str(self.field_option))) and (self.delim == " "))
            else exclude.add("delim_value")
        )
        include.add("quote") if (self.field_option and "quote" in str(self.field_option)) else exclude.add("quote")
        (
            include.add("quote_value")
            if (((self.field_option and "quote" in str(self.field_option))) and (self.quote == " "))
            else exclude.add("quote_value")
        )
        (
            include.add("actual_length")
            if (self.field_option and "actual_length" in str(self.field_option))
            else exclude.add("actual_length")
        )
        (
            include.add("delim_string")
            if (self.field_option and "delim_string" in str(self.field_option))
            else exclude.add("delim_string")
        )
        (
            include.add("null_length")
            if (self.field_option and "null_length" in str(self.field_option))
            else exclude.add("null_length")
        )
        (
            include.add("null_field")
            if (self.field_option and "null_field" in str(self.field_option))
            else exclude.add("null_field")
        )
        (
            include.add("null_field_sep_flag")
            if (self.field_option and "null_field" in str(self.field_option))
            else exclude.add("null_field_sep_flag")
        )
        (
            include.add("null_field_sep")
            if (
                ((self.null_field_sep_flag))
                and (self.field_option and "null_field" in str(self.field_option))
            )
            else exclude.add("null_field_sep")
        )
        (
            include.add("null_field_sep_value")
            if (
                ((self.field_option and "null_field" in str(self.field_option)))
                and (self.null_field_sep_flag)
                and (self.null_field_sep == " ")
            )
            else exclude.add("null_field_sep_value")
        )
        (
            include.add("prefix")
            if (self.field_option and "prefix_bytes" in str(self.field_option))
            else exclude.add("prefix")
        )
        (
            include.add("print_field")
            if (self.field_option and "print_field" in str(self.field_option))
            else exclude.add("print_field")
        )
        (
            include.add("vector_prefix")
            if (self.field_option and "vector_prefix" in str(self.field_option))
            else exclude.add("vector_prefix")
        )
        (
            include.add("byte_order")
            if (self.general_option and "byte_order" in str(self.general_option))
            else exclude.add("byte_order")
        )
        (
            include.add("charset")
            if (self.general_option and "charset" in str(self.general_option))
            else exclude.add("charset")
        )
        (
            include.add("data_format")
            if (self.general_option and "data_format" in str(self.general_option))
            else exclude.add("data_format")
        )
        (
            include.add("max_width")
            if (self.general_option and "max_width" in str(self.general_option))
            else exclude.add("max_width")
        )
        (
            include.add("width")
            if (self.general_option and "field_width" in str(self.general_option))
            else exclude.add("width")
        )
        (
            include.add("padchar")
            if (self.general_option and "padchar" in str(self.general_option))
            else exclude.add("padchar")
        )
        (
            include.add("padchar_value")
            if (((self.general_option and "padchar" in str(self.general_option))) and (self.padchar == " "))
            else exclude.add("padchar_value")
        )
        (
            include.add("export_ebcdic_as_ascii")
            if (self.string_option and "export_ebcdic_as_ascii" in str(self.string_option))
            else exclude.add("export_ebcdic_as_ascii")
        )
        (
            include.add("import_ascii_as_ebcdic")
            if (self.string_option and "import_ascii_as_ebcdic" in str(self.string_option))
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
            include.add("round")
            if (self.decimal_options and "round" in str(self.decimal_options))
            else exclude.add("round")
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
            if (self.numeric_option and "c_format" in str(self.numeric_option))
            else exclude.add("c_format")
        )
        (
            include.add("in_format")
            if (self.numeric_option and "in_format" in str(self.numeric_option))
            else exclude.add("in_format")
        )
        (
            include.add("out_format")
            if (self.numeric_option and "out_format" in str(self.numeric_option))
            else exclude.add("out_format")
        )
        include.add("days_since") if (self.date_option == "days_since") else exclude.add("days_since")
        include.add("date_format") if (self.date_option == "date_format") else exclude.add("date_format")
        include.add("is_julian") if (self.date_option == "is_julian") else exclude.add("is_julian")
        include.add("time_format") if (self.time_option == "time_format") else exclude.add("time_format")
        (
            include.add("is_midnight_seconds")
            if (self.time_option == "is_midnight_seconds")
            else exclude.add("is_midnight_seconds")
        )
        (
            include.add("timestamp_format")
            if (self.timestamp_option == "timestamp_format")
            else exclude.add("timestamp_format")
        )
        return include, exclude

    def get_input_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "additional_properties_set",
            "destination",
            "destinationlist",
            "rejects",
            "runtime_column_propagation",
            "schemafile",
            "selection",
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

    def get_input_cardinality(self) -> dict:
        return {"min": 0, "max": 1}

    def get_output_ports_props(self) -> dict:
        include, exclude = self.validate()
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
        return {"min": 0, "max": 0}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "actual_length",
            "additional_properties_set_option",
            "allow_all_zeros",
            "allow_column_mapping",
            "allow_signed_import",
            "auto_column_propagation",
            "buf_free_run",
            "buf_free_run_ronly",
            "buf_mode",
            "buf_mode_ronly",
            "byte_order",
            "c_format",
            "charset",
            "check_intact",
            "check_intact_flag",
            "coll_type",
            "combinability",
            "current_output_link_type",
            "data_format",
            "date_format",
            "date_option",
            "days_since",
            "decimal_options",
            "decimal_packed",
            "decimal_packed_check",
            "decimal_packed_sign_position",
            "decimal_packed_signed",
            "decimal_sep_value",
            "decimal_separator",
            "delim",
            "delim_string",
            "delim_value",
            "destination",
            "destinationlist",
            "disk_write_inc",
            "disk_write_inc_ronly",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execmode",
            "export_ebcdic_as_ascii",
            "field_option",
            "fill",
            "fill_char_value",
            "final_delim",
            "final_delim_string",
            "final_delim_value",
            "flow_dirty",
            "general_option",
            "hide",
            "import_ascii_as_ebcdic",
            "in_format",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "intact",
            "is_julian",
            "is_midnight_seconds",
            "key_col_select",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "max_mem_buf_size",
            "max_mem_buf_size_ronly",
            "max_width",
            "nls_map_name",
            "null_field",
            "null_field_sep",
            "null_field_sep_flag",
            "null_field_sep_value",
            "null_length",
            "numeric_option",
            "out_format",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "padchar",
            "padchar_value",
            "part_client_dbname",
            "part_client_instance",
            "part_dbconnection",
            "part_stable",
            "part_stable_coll",
            "part_stable_ordered",
            "part_stable_roundrobin_coll",
            "part_table",
            "part_type",
            "part_unique",
            "part_unique_coll",
            "part_unique_ordered",
            "part_unique_roundrobin_coll",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "precision",
            "prefix",
            "preserve",
            "print_field",
            "queue_upper_size",
            "queue_upper_size_ronly",
            "quote",
            "quote_value",
            "rec_level_option",
            "record_delim",
            "record_delim_string",
            "record_delim_value",
            "record_format",
            "record_len_value",
            "record_length",
            "record_prefix",
            "rejects",
            "round",
            "runtime_column_propagation",
            "scale",
            "schemafile",
            "selection",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "stage_description",
            "string_option",
            "time_format",
            "time_option",
            "timestamp_format",
            "timestamp_option",
            "vector_prefix",
            "width",
        }
        required = {
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "output_acp_should_hide",
            "selection",
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
