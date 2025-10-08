import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import TWO_SOURCE_MATCH
from pydantic import Field
from typing import ClassVar


class two_source_match(BaseStage):

    op_name: ClassVar[str] = "ReferenceMatch"
    node_type: ClassVar[str] = "execution_node"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/ReferenceMatch.svg"
    label: ClassVar[str] = "Two-source Match"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    # match_asset_id: Optional[str] = Field(None, alias='match_asset_id')
    # match_specification: Optional[MatchSpecification] = None
    buf_free_run: int | None = Field(50, alias="buf_free_run")
    buf_free_run_ronly: str | None = Field("", alias="buf_free_run_ronly")
    buf_mode: TWO_SOURCE_MATCH.BufMode | None = Field(TWO_SOURCE_MATCH.BufMode.default, alias="buf_mode")
    buf_mode_ronly: str | None = Field("", alias="buf_mode_ronly")
    clro: str | None = Field(None, alias="clro")
    coll_type: TWO_SOURCE_MATCH.CollType | None = Field(TWO_SOURCE_MATCH.CollType.auto, alias="coll_type")
    combinability: TWO_SOURCE_MATCH.Combinability | None = Field(
        TWO_SOURCE_MATCH.Combinability.auto, alias="combinability"
    )
    cutoffs_properties: list | None = Field([], alias="cutoffsProperties")
    db2_instance_select: TWO_SOURCE_MATCH.Db2InstanceSelect | None = Field(
        TWO_SOURCE_MATCH.Db2InstanceSelect.use_db2InstanceEnv, alias="db2InstanceSelect"
    )
    db2_name_select: TWO_SOURCE_MATCH.Db2NameSelect | None = Field(
        TWO_SOURCE_MATCH.Db2NameSelect.use_db2NameEnv, alias="db2NameSelect"
    )
    disk_write_inc: int | None = Field(1048576, alias="disk_write_inc")
    disk_write_inc_ronly: str | None = Field("", alias="disk_write_inc_ronly")
    dupa: str | None = Field(None, alias="dupa")
    dupb: str | None = Field(None, alias="dupb")
    enable_override: bool | None = Field(False, alias="enableOverride")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execmode: TWO_SOURCE_MATCH.Execmode | None = Field(TWO_SOURCE_MATCH.Execmode.default_par, alias="execmode")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    freq_a: str = Field(None, alias="freqA")
    freq_b: str = Field(None, alias="freqB")
    group: str | None = Field(None, alias="group")
    hide: bool | None = Field(False, alias="hide")
    input_count: int = Field(1, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    inputlink_ordering_list: list | None = Field([], alias="InputlinkOrderingList")
    key_col_select: TWO_SOURCE_MATCH.KeyColSelect | None = Field(
        TWO_SOURCE_MATCH.KeyColSelect.Select_a_column, alias="keyColSelect"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    locale: str | None = Field(None, alias="locale")
    match_type: str | None = Field("Match", alias="matchType")
    mato: str | None = Field(None, alias="mato")
    max_mem_buf_size: int | None = Field(3145728, alias="max_mem_buf_size")
    max_mem_buf_size_ronly: str | None = Field("", alias="max_mem_buf_size_ronly")
    output_count: int = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    outputlink_ordering_list: list | None = Field([], alias="OutputlinkOrderingList")
    override: str | None = Field(None, alias="override")
    part_dbname: str | None = Field("eg: SAMPLE", alias="part_dbname")
    part_server: str | None = Field("eg: DB2INST", alias="part_server")
    part_stable: bool | None = Field(None, alias="part_stable")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_table: str | None = Field(None, alias="part_table")
    part_type: TWO_SOURCE_MATCH.PartType | None = Field(TWO_SOURCE_MATCH.PartType.auto, alias="part_type")
    part_unique: bool | None = Field(None, alias="part_unique")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    pgmtype: TWO_SOURCE_MATCH.Pgmtype | None = Field(TWO_SOURCE_MATCH.Pgmtype.many_to_one, alias="pgmtype")
    preserve: TWO_SOURCE_MATCH.Preserve | None = Field(TWO_SOURCE_MATCH.Preserve.default_propagate, alias="preserve")
    queue_upper_size: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: str | None = Field("", alias="queue_upper_size_ronly")
    resa: str | None = Field(None, alias="resa")
    resb: str | None = Field(None, alias="resb")
    reuse_rec_id: str | None = Field(None, alias="reuseRecId")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    schema_name_check: bool | None = Field(None, alias="schemaNameCheck")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field(
        "If sort keys are added, a sort will be performed.", alias="sortInstructions"
    )
    spec_cutoff: str | None = Field("", alias="specCutoff")
    specfile: str = Field(None, alias="specfile")
    stage_description: list | None = Field("", alias="stageDescription")
    stats: str | None = Field(None, alias="stats")
    trace_properties: list | None = Field([], alias="traceProperties")
    workdir: str = Field("", alias="workdir")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("pgmtype") if (self.specfile) else exclude.add("pgmtype")
        include.add("mato") if (self.specfile) else exclude.add("mato")
        include.add("clro") if (self.specfile) else exclude.add("clro")
        include.add("dupa") if (self.specfile) else exclude.add("dupa")
        include.add("dupb") if (self.specfile) else exclude.add("dupb")
        include.add("resa") if (self.specfile) else exclude.add("resa")
        include.add("resb") if (self.specfile) else exclude.add("resb")
        include.add("stats") if (self.specfile) else exclude.add("stats")
        include.add("enable_override") if (self.specfile) else exclude.add("enable_override")
        include.add("cutoffs_properties") if (self.specfile) else exclude.add("cutoffs_properties")

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
            include.add("max_mem_buf_size_ronly")
            if (self.hide != "true" or not self.hide)
            else exclude.add("max_mem_buf_size_ronly")
        )
        (
            include.add("buf_free_run_ronly")
            if (self.hide != "true" or not self.hide)
            else exclude.add("buf_free_run_ronly")
        )
        (
            include.add("queue_upper_size_ronly")
            if (self.hide != "true" or not self.hide)
            else exclude.add("queue_upper_size_ronly")
        )
        (
            include.add("disk_write_inc_ronly")
            if (self.hide != "true" or not self.hide)
            else exclude.add("disk_write_inc_ronly")
        )
        (
            include.add("part_stable")
            if (((self.show_part_type)) and (self.part_type != "auto") and (self.show_sort_options))
            else exclude.add("part_stable")
        )
        (
            include.add("part_unique")
            if (((self.show_part_type)) and (self.part_type != "auto") and (self.show_sort_options))
            else exclude.add("part_unique")
        )
        (
            include.add("key_cols_part")
            if (
                (
                    ((self.show_part_type))
                    and ((not self.show_coll_type))
                    and ((self.part_type != "auto"))
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
            include.add("db2_name_select")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("db2_name_select")
        )
        (
            include.add("part_dbname")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("part_dbname")
        )
        (
            include.add("db2_instance_select")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("db2_instance_select")
        )
        (
            include.add("part_server")
            if (((self.part_type == "db2part")) and (self.show_part_type))
            else exclude.add("part_server")
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
        return {"min": 4, "max": 4}

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
        return {"min": 1, "max": 7}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "buf_free_run",
            "buf_free_run_ronly",
            "buf_mode",
            "buf_mode_ronly",
            "clro",
            "coll_type",
            "combinability",
            "cutoffs_properties",
            "db2_instance_select",
            "db2_name_select",
            "disk_write_inc",
            "disk_write_inc_ronly",
            "dupa",
            "dupb",
            "enable_override",
            "enable_schemaless_design",
            "execmode",
            "flow_dirty",
            "freq_a",
            "freq_b",
            "group",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "inputlink_ordering_list",
            "key_col_select",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "locale",
            "match_type",
            "mato",
            "max_mem_buf_size",
            "max_mem_buf_size_ronly",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "outputlink_ordering_list",
            "override",
            "part_dbname",
            "part_server",
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
            "pgmtype",
            "preserve",
            "queue_upper_size",
            "queue_upper_size_ronly",
            "resa",
            "resb",
            "reuse_rec_id",
            "runtime_column_propagation",
            "schema_name_check",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "spec_cutoff",
            "specfile",
            "stage_description",
            "stats",
            "trace_properties",
            "workdir",
        }
        required = {
            "enable_schemaless_design",
            "freq_a",
            "freq_b",
            "input_count",
            "output_count",
            "pgmtype",
            "specfile",
            "workdir",
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
                "maxRejectOutputs": 0,
                "minRejectOutputs": 0,
                "maxReferenceInputs": 0,
                "minReferenceInputs": 0,
            }
        }
