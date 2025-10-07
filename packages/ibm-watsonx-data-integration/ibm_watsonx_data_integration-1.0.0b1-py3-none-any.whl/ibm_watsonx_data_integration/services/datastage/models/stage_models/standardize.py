import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import STANDARDIZE
from pydantic import Field
from typing import ClassVar


class standardize(BaseStage):

    op_name: ClassVar[str] = "Standardize"
    node_type: ClassVar[str] = "execution_node"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/Standardize.svg"
    label: ClassVar[str] = "Standardize"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    buf_free_run: int | None = Field(50, alias="buf_free_run")
    buf_free_run_ronly: str | None = Field("", alias="buf_free_run_ronly")
    buf_mode: STANDARDIZE.BufMode | None = Field(STANDARDIZE.BufMode.default, alias="buf_mode")
    buf_mode_ronly: str | None = Field("", alias="buf_mode_ronly")
    case: STANDARDIZE.Case | None = Field(STANDARDIZE.Case.UPPERALL, alias="case")
    coll_type: STANDARDIZE.CollType | None = Field(STANDARDIZE.CollType.auto, alias="coll_type")
    combinability: STANDARDIZE.Combinability | None = Field(STANDARDIZE.Combinability.auto, alias="combinability")
    db2_instance_select: STANDARDIZE.Db2InstanceSelect | None = Field(
        STANDARDIZE.Db2InstanceSelect.use_db2InstanceEnv, alias="db2InstanceSelect"
    )
    db2_name_select: STANDARDIZE.Db2NameSelect | None = Field(
        STANDARDIZE.Db2NameSelect.use_db2NameEnv, alias="db2NameSelect"
    )
    disk_write_inc: int | None = Field(1048576, alias="disk_write_inc")
    disk_write_inc_ronly: str | None = Field("", alias="disk_write_inc_ronly")
    execmode: STANDARDIZE.Execmode | None = Field(STANDARDIZE.Execmode.default_par, alias="execmode")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    key_col_select: STANDARDIZE.KeyColSelect | None = Field(
        STANDARDIZE.KeyColSelect.Select_a_column, alias="keyColSelect"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    locale: str | None = Field(None, alias="locale")
    max_mem_buf_size: int | None = Field(3145728, alias="max_mem_buf_size")
    max_mem_buf_size_ronly: str | None = Field("", alias="max_mem_buf_size_ronly")
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    part_dbname: str | None = Field("eg: SAMPLE", alias="part_dbname")
    part_server: str | None = Field("eg: DB2INST", alias="part_server")
    part_stable: bool | None = Field(None, alias="part_stable")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_table: str | None = Field(None, alias="part_table")
    part_type: STANDARDIZE.PartType | None = Field(STANDARDIZE.PartType.auto, alias="part_type")
    part_unique: bool | None = Field(None, alias="part_unique")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve: STANDARDIZE.Preserve | None = Field(STANDARDIZE.Preserve.default_propagate, alias="preserve")
    queue_upper_size: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: str | None = Field("", alias="queue_upper_size_ronly")
    reporting_output: bool | None = Field(False, alias="reportingOutput")
    ruleset: str | None = Field("", alias="ruleset")
    ruleset_properties: list | None = Field([], alias="rulesetProperties")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    schema_name_check: bool | None = Field(None, alias="schemaNameCheck")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field(
        "If sort keys are added, a sort will be performed.", alias="sortInstructions"
    )
    stage_description: list | None = Field("", alias="stageDescription")
    stagecol_properties: list | None = Field([], alias="stagecolProperties")
    trace_properties: list | None = Field([], alias="traceProperties")
    workdir: str | None = Field("", alias="workdir")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("max_mem_buf_size") if (self.buf_mode != "nobuffer") else exclude.add("max_mem_buf_size")
        include.add("buf_free_run") if (self.buf_mode != "nobuffer") else exclude.add("buf_free_run")
        include.add("queue_upper_size") if (self.buf_mode != "nobuffer") else exclude.add("queue_upper_size")
        include.add("disk_write_inc") if (self.buf_mode != "nobuffer") else exclude.add("disk_write_inc")

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
                (((self.show_part_type)) and ((self.part_type != "auto")) and ((self.part_type != "modulus")))
                or (
                    ((self.show_part_type))
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
            if (((self.part_type == "hash")) or (self.part_type == "range"))
            else exclude.add("perform_sort")
        )
        include.add("perform_sort_modulus") if (self.part_type == "modulus") else exclude.add("perform_sort_modulus")
        (
            include.add("key_col_select")
            if (((self.part_type == "modulus")) and (not self.perform_sort_modulus))
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
            if (((self.coll_type == "ordered")) or (self.coll_type == "roundrobin_coll"))
            else exclude.add("perform_sort_coll")
        )
        (
            include.add("key_cols_coll")
            if (
                ((self.show_coll_type))
                and (((self.coll_type == "sortmerge")) or (self.perform_sort_coll))
            )
            else exclude.add("key_cols_coll")
        )
        (
            include.add("key_cols_none")
            if (((not self.show_part_type)) and (not self.show_coll_type))
            else exclude.add("key_cols_none")
        )
        (
            include.add("part_stable_coll")
            if (
                ((self.coll_type == "sortmerge"))
                or (self.perform_sort_coll)
                or (((not self.show_part_type)) and (not self.show_coll_type))
            )
            else exclude.add("part_stable_coll")
        )
        (
            include.add("part_unique_coll")
            if (
                ((self.coll_type == "sortmerge"))
                or (self.perform_sort_coll)
                or (((not self.show_part_type)) and (not self.show_coll_type))
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
        return {"min": 1, "max": 1}

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
        return {"min": 1, "max": 1}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "buf_free_run",
            "buf_free_run_ronly",
            "buf_mode",
            "buf_mode_ronly",
            "case",
            "coll_type",
            "combinability",
            "db2_instance_select",
            "db2_name_select",
            "disk_write_inc",
            "disk_write_inc_ronly",
            "execmode",
            "flow_dirty",
            "hide",
            "input_count",
            "input_link_description",
            "inputcol_properties",
            "key_col_select",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "locale",
            "max_mem_buf_size",
            "max_mem_buf_size_ronly",
            "output_count",
            "output_link_description",
            "outputcol_properties",
            "part_dbname",
            "part_server",
            "part_stable",
            "part_stable_coll",
            "part_table",
            "part_type",
            "part_unique",
            "part_unique_coll",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "preserve",
            "queue_upper_size",
            "queue_upper_size_ronly",
            "reporting_output",
            "ruleset",
            "ruleset_properties",
            "runtime_column_propagation",
            "schema_name_check",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "stage_description",
            "stagecol_properties",
            "trace_properties",
            "workdir",
        }
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
                "maxRejectOutputs": 0,
                "minRejectOutputs": 0,
                "maxReferenceInputs": 0,
                "minReferenceInputs": 0,
            }
        }
