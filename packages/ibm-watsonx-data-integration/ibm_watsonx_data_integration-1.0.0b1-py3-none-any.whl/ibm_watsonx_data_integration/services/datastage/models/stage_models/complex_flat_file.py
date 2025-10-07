import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import COMPLEX_FLAT_FILE
from pydantic import Field
from typing import ClassVar


class complex_flat_file(BaseStage):

    op_name: ClassVar[str] = "PxCFF"
    node_type: ClassVar[str] = "execution_node"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/PxCFF.svg"
    label: ClassVar[str] = "Complex Flat File"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    records: list | None = Field([], alias="records")
    output_columns: list | None = Field([], alias="output_columns")
    records_id: list | None = Field([], alias="records_id")
    allow_column_mapping: COMPLEX_FLAT_FILE.AllowColumnMapping | None = Field(
        COMPLEX_FLAT_FILE.AllowColumnMapping.false, alias="allow_column_mapping"
    )
    allowzeros: COMPLEX_FLAT_FILE.Allowzeros | None = Field(
        COMPLEX_FLAT_FILE.Allowzeros.nofix_zero, alias="allowzeros"
    )
    auto_column_propagation: bool | None = Field(None, alias="auto_column_propagation")
    buf_free_run: int | None = Field(50, alias="buf_free_run")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode: COMPLEX_FLAT_FILE.BufMode | None = Field(COMPLEX_FLAT_FILE.BufMode.default, alias="buf_mode")
    buf_mode_ronly: COMPLEX_FLAT_FILE.BufModeRonly | None = Field(
        COMPLEX_FLAT_FILE.BufModeRonly.default, alias="buf_mode_ronly"
    )
    byteorder: COMPLEX_FLAT_FILE.Byteorder | None = Field(
        COMPLEX_FLAT_FILE.Byteorder.native_endian, alias="byteorder"
    )
    chardefault: str | None = Field(None, alias="chardefault")
    charset: COMPLEX_FLAT_FILE.Charset | None = Field(COMPLEX_FLAT_FILE.Charset.ebcdic, alias="charset")
    coll_type: COMPLEX_FLAT_FILE.CollType | None = Field(COMPLEX_FLAT_FILE.CollType.auto, alias="coll_type")
    combinability: COMPLEX_FLAT_FILE.Combinability | None = Field(
        COMPLEX_FLAT_FILE.Combinability.auto, alias="combinability"
    )
    connect_to_zos: COMPLEX_FLAT_FILE.ConnectToZos | None = Field(
        COMPLEX_FLAT_FILE.ConnectToZos.custom, alias="connect_to_zos"
    )
    constraint: list | None = Field([], alias="predicate")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    data_asset_name: str = Field(None, alias="dataAssetName")
    dataformat: COMPLEX_FLAT_FILE.Dataformat | None = Field(COMPLEX_FLAT_FILE.Dataformat.binary, alias="dataformat")
    decdefault: str | None = Field(None, alias="decdefault")
    decrounding: COMPLEX_FLAT_FILE.Decrounding | None = Field(
        COMPLEX_FLAT_FILE.Decrounding.round_inf, alias="decrounding"
    )
    decsep: COMPLEX_FLAT_FILE.Decsep | None = Field(COMPLEX_FLAT_FILE.Decsep.default, alias="decsep")
    disk_write_inc: int | None = Field(1048576, alias="disk_write_inc")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execmode: COMPLEX_FLAT_FILE.Execmode | None = Field(None, alias="execmode")
    field_rejects: COMPLEX_FLAT_FILE.FieldRejects | None = Field(
        COMPLEX_FLAT_FILE.FieldRejects.keepField, alias="field_rejects"
    )
    filename: str = Field(None, alias="filename")
    filter: str | None = Field(None, alias="filter")
    first: int | None = Field(None, alias="first")
    floatrepresentation: COMPLEX_FLAT_FILE.Floatrepresentation | None = Field(
        COMPLEX_FLAT_FILE.Floatrepresentation.IEEE, alias="floatrepresentation"
    )
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    intdefault: str | None = Field(None, alias="intdefault")
    ismultipleformat: bool | None = Field(False, alias="ismultipleformat")
    keep_partitions: COMPLEX_FLAT_FILE.KeepPartitions | None = Field(
        COMPLEX_FLAT_FILE.KeepPartitions.false, alias="keepPartitions"
    )
    key_col_select: COMPLEX_FLAT_FILE.KeyColSelect | None = Field(
        COMPLEX_FLAT_FILE.KeyColSelect.default, alias="keyColSelect"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    max_mem_buf_size: int | None = Field(3145728, alias="max_mem_buf_size")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    missing_file: COMPLEX_FLAT_FILE.MissingFile | None = Field(
        COMPLEX_FLAT_FILE.MissingFile.custom, alias="missingFile"
    )
    multinode: COMPLEX_FLAT_FILE.Multinode | None = Field(COMPLEX_FLAT_FILE.Multinode.no, alias="multinode")
    nls_map_name: COMPLEX_FLAT_FILE.NlsMapName | None = Field(
        COMPLEX_FLAT_FILE.NlsMapName.UTF_8, alias="nls_map_name"
    )
    nocleanup: COMPLEX_FLAT_FILE.Nocleanup | None = Field(COMPLEX_FLAT_FILE.Nocleanup.false, alias="nocleanup")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    padchar: str | None = Field(None, alias="padchar")
    part_client_dbname: str | None = Field(None, alias="part_client_dbname")
    part_client_instance: str | None = Field(None, alias="part_client_instance")
    part_dbconnection: str | None = Field("", alias="part_dbconnection")
    part_stable: bool | None = Field(None, alias="part_stable")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_table: str | None = Field(None, alias="part_table")
    part_type: COMPLEX_FLAT_FILE.PartType | None = Field(COMPLEX_FLAT_FILE.PartType.auto, alias="part_type")
    part_unique: bool | None = Field(None, alias="part_unique")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve: COMPLEX_FLAT_FILE.Preserve | None = Field(COMPLEX_FLAT_FILE.Preserve.clear, alias="preserve")
    print_field: COMPLEX_FLAT_FILE.PrintField | None = Field(COMPLEX_FLAT_FILE.PrintField.false, alias="print_field")
    queue_upper_size: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    readers: int | None = Field(1, alias="readers")
    record_prefix: COMPLEX_FLAT_FILE.RecordPrefix | None = Field(
        COMPLEX_FLAT_FILE.RecordPrefix.custom, alias="record_prefix"
    )
    recorddelimiter: COMPLEX_FLAT_FILE.Recorddelimiter | None = Field(
        COMPLEX_FLAT_FILE.Recorddelimiter.custom, alias="recorddelimiter"
    )
    recordtype: COMPLEX_FLAT_FILE.Recordtype | None = Field(COMPLEX_FLAT_FILE.Recordtype.F, alias="recordtype")
    register_data_asset: bool | None = Field(False, alias="registerDataAsset")
    rejects: COMPLEX_FLAT_FILE.Rejects | None = Field(COMPLEX_FLAT_FILE.Rejects.cont, alias="rejects")
    report_progress: COMPLEX_FLAT_FILE.ReportProgress | None = Field(
        COMPLEX_FLAT_FILE.ReportProgress.yes, alias="reportProgress"
    )
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    selection: COMPLEX_FLAT_FILE.Selection | None = Field(COMPLEX_FLAT_FILE.Selection.singlefile, alias="selection")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    stage_description: list | None = Field("", alias="stageDescription")
    writeoption: COMPLEX_FLAT_FILE.Writeoption | None = Field(
        COMPLEX_FLAT_FILE.Writeoption.overwrite, alias="writeoption"
    )

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("print_field")
            if (
                (
                    ((self.input_count == 0))
                    and (
                        (
                            self.connect_to_zos
                            and (
                                (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                                or (self.connect_to_zos == " ")
                            )
                        )
                    )
                )
                or (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == "zosAsSource")
                            or (self.connect_to_zos == "zosAsSource")
                        )

                )
            )
            else exclude.add("print_field")
        )
        (
            include.add("decdefault")
            if (
                (
                    ((self.input_count == 0))
                    and (
                        (
                            self.connect_to_zos
                            and (
                                (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                                or (self.connect_to_zos == " ")
                            )
                        )
                    )
                )
                or (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == "zosAsSource")
                            or (self.connect_to_zos == "zosAsSource")
                        )

                )
            )
            else exclude.add("decdefault")
        )
        (
            include.add("intdefault")
            if (
                (
                    ((self.input_count == 0))
                    and (
                        (
                            self.connect_to_zos
                            and (
                                (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                                or (self.connect_to_zos == " ")
                            )
                        )
                    )
                )
                or (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == "zosAsSource")
                            or (self.connect_to_zos == "zosAsSource")
                        )

                )
            )
            else exclude.add("intdefault")
        )
        (
            include.add("chardefault")
            if (
                (
                    ((self.input_count == 0))
                    and (
                        (
                            self.connect_to_zos
                            and (
                                (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                                or (self.connect_to_zos == " ")
                            )
                        )
                    )
                )
                or (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == "zosAsSource")
                            or (self.connect_to_zos == "zosAsSource")
                        )

                )
            )
            else exclude.add("chardefault")
        )
        (
            include.add("report_progress")
            if (
                ((self.input_count == 0))
                and (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "source")
                            or (self.selection != "source")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "sourcelist")
                            or (self.selection != "sourcelist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destination")
                            or (self.selection != "destination")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destinationlist")
                            or (self.selection != "destinationlist")
                        )

                )
            )
            else exclude.add("report_progress")
        )
        (
            include.add("filter")
            if (
                (
                    (
                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )
                    )
                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "source")
                            or (self.selection != "source")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "sourcelist")
                            or (self.selection != "sourcelist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destination")
                            or (self.selection != "destination")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destinationlist")
                            or (self.selection != "destinationlist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "filepattern")
                            or (self.selection != "filepattern")
                        )

                )
            )
            else exclude.add("filter")
        )
        (
            include.add("constraint")
            if (
                (
                    (
                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )
                    )
                )
                or (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == "zosAsSource")
                            or (self.connect_to_zos == "zosAsSource")
                        )

                )
            )
            else exclude.add("constraint")
        )
        (
            include.add("first")
            if (
                ((self.input_count == 0))
                and (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "source")
                            or (self.selection != "source")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "sourcelist")
                            or (self.selection != "sourcelist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destination")
                            or (self.selection != "destination")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destinationlist")
                            or (self.selection != "destinationlist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "fileset")
                            or (self.selection != "fileset")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "filepattern")
                            or (self.selection != "filepattern")
                        )

                )
                and (

                        self.multinode
                        and (
                            (hasattr(self.multinode, "value") and self.multinode.value != "yes")
                            or (self.multinode != "yes")
                        )

                )
                and (((self.readers is None)) or (self.readers == 1))
            )
            else exclude.add("first")
        )
        (
            include.add("connect_to_zos")
            if (
                (
                    (
                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value != " ")
                            or (self.connect_to_zos != " ")
                        )
                    )
                )
                and (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )

                )
            )
            else exclude.add("connect_to_zos")
        )
        (
            include.add("field_rejects")
            if (

                    self.connect_to_zos
                    and (
                        (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value != " ")
                        or (self.connect_to_zos != " ")
                    )

            )
            else exclude.add("field_rejects")
        )
        (
            include.add("keep_partitions")
            if (
                ((self.input_count == 0))
                and (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )

                )
            )
            else exclude.add("keep_partitions")
        )
        (
            include.add("selection")
            if (

                    self.connect_to_zos
                    and (
                        (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                        or (self.connect_to_zos == " ")
                    )

            )
            else exclude.add("selection")
        )
        (
            include.add("rejects")
            if (

                    self.connect_to_zos
                    and (
                        (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                        or (self.connect_to_zos == " ")
                    )

            )
            else exclude.add("rejects")
        )
        (
            include.add("record_prefix")
            if (

                    self.connect_to_zos
                    and (
                        (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                        or (self.connect_to_zos == " ")
                    )

            )
            else exclude.add("record_prefix")
        )
        (
            include.add("recordtype")
            if (

                    self.connect_to_zos
                    and (
                        (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                        or (self.connect_to_zos == " ")
                    )

            )
            else exclude.add("recordtype")
        )
        (
            include.add("filename")
            if (

                    self.connect_to_zos
                    and (
                        (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                        or (self.connect_to_zos == " ")
                    )

            )
            else exclude.add("filename")
        )
        (
            include.add("missing_file")
            if (
                ((self.input_count == 0))
                and (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "source")
                            or (self.selection != "source")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "sourcelist")
                            or (self.selection != "sourcelist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destination")
                            or (self.selection != "destination")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destinationlist")
                            or (self.selection != "destinationlist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "fileset")
                            or (self.selection != "fileset")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "filepattern")
                            or (self.selection != "filepattern")
                        )

                )
            )
            else exclude.add("missing_file")
        )
        (
            include.add("multinode")
            if (
                ((self.input_count == 0))
                and (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "source")
                            or (self.selection != "source")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "sourcelist")
                            or (self.selection != "sourcelist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destination")
                            or (self.selection != "destination")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destinationlist")
                            or (self.selection != "destinationlist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "fileset")
                            or (self.selection != "fileset")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "filepattern")
                            or (self.selection != "filepattern")
                        )

                )
            )
            else exclude.add("multinode")
        )
        (
            include.add("padchar")
            if (
                (
                    ((self.input_count and self.input_count > 0))
                    and (
                        (
                            self.connect_to_zos
                            and (
                                (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                                or (self.connect_to_zos == " ")
                            )
                        )
                    )
                )
                or (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == "zosAsTarget")
                            or (self.connect_to_zos == "zosAsTarget")
                        )

                )
            )
            else exclude.add("padchar")
        )
        (
            include.add("readers")
            if (
                ((self.input_count == 0))
                and (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "source")
                            or (self.selection != "source")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "sourcelist")
                            or (self.selection != "sourcelist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destination")
                            or (self.selection != "destination")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "destinationlist")
                            or (self.selection != "destinationlist")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "fileset")
                            or (self.selection != "fileset")
                        )

                )
                and (

                        self.selection
                        and (
                            (hasattr(self.selection, "value") and self.selection.value != "filepattern")
                            or (self.selection != "filepattern")
                        )

                )
                and (

                        self.multinode
                        and (
                            (hasattr(self.multinode, "value") and self.multinode.value != "yes")
                            or (self.multinode != "yes")
                        )

                )
            )
            else exclude.add("readers")
        )
        (
            include.add("writeoption")
            if (
                ((self.input_count and self.input_count > 0))
                and (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )

                )
            )
            else exclude.add("writeoption")
        )
        (
            include.add("nocleanup")
            if (
                ((self.input_count and self.input_count > 0))
                and (

                        self.connect_to_zos
                        and (
                            (hasattr(self.connect_to_zos, "value") and self.connect_to_zos.value == " ")
                            or (self.connect_to_zos == " ")
                        )

                )
            )
            else exclude.add("nocleanup")
        )
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
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

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
        return {"min": 0, "max": 1}

    def get_output_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = {"constraint"}
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
        return {"min": 0, "max": -1}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "allowzeros",
            "byteorder",
            "chardefault",
            "charset",
            "combinability",
            "connect_to_zos",
            "data_asset_name",
            "dataformat",
            "decdefault",
            "decrounding",
            "decsep",
            "execmode",
            "field_rejects",
            "filename",
            "filter",
            "first",
            "floatrepresentation",
            "input_count",
            "intdefault",
            "ismultipleformat",
            "keep_partitions",
            "missing_file",
            "multinode",
            "nocleanup",
            "output_count",
            "padchar",
            "preserve",
            "print_field",
            "readers",
            "record_prefix",
            "recorddelimiter",
            "recordtype",
            "register_data_asset",
            "rejects",
            "report_progress",
            "selection",
            "writeoption",
        }
        required = {"data_asset_name", "filename", "recordtype", "selection"}
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
            "allow_column_mapping",
            "allowzeros",
            "auto_column_propagation",
            "buf_free_run",
            "buf_free_run_ronly",
            "buf_mode",
            "buf_mode_ronly",
            "byteorder",
            "chardefault",
            "charset",
            "coll_type",
            "combinability",
            "connect_to_zos",
            "constraint",
            "current_output_link_type",
            "dataformat",
            "decdefault",
            "decrounding",
            "decsep",
            "disk_write_inc",
            "disk_write_inc_ronly",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execmode",
            "field_rejects",
            "filename",
            "filter",
            "first",
            "floatrepresentation",
            "flow_dirty",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "intdefault",
            "ismultipleformat",
            "keep_partitions",
            "key_col_select",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "max_mem_buf_size",
            "max_mem_buf_size_ronly",
            "missing_file",
            "multinode",
            "nls_map_name",
            "nocleanup",
            "output_acp_should_hide",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "padchar",
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
            "preserve",
            "print_field",
            "queue_upper_size",
            "queue_upper_size_ronly",
            "readers",
            "record_prefix",
            "recorddelimiter",
            "recordtype",
            "rejects",
            "report_progress",
            "runtime_column_propagation",
            "selection",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "stage_description",
            "writeoption",
        }
        required = {
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "filename",
            "output_acp_should_hide",
            "recordtype",
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
