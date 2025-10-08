import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import ADDRESS_VERIFICATION
from pydantic import Field
from typing import ClassVar


class address_verification(BaseStage):

    op_name: ClassVar[str] = "AddressVerification2"
    node_type: ClassVar[str] = "execution_node"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/AddressVerification2.svg"
    label: ClassVar[str] = "Address Verification"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    add_server_options: str | None = Field("", alias="addServerOptions")
    address_count: str = Field("1", alias="addressCount")
    address_line_properties: list | None = Field([], alias="addressLineProperties")
    address_line_separator: ADDRESS_VERIFICATION.AddressLineSeparator | None = Field(
        ADDRESS_VERIFICATION.AddressLineSeparator.PIPE, alias="addressLineSeparator"
    )
    buf_free_run: int | None = Field(50, alias="buf_free_run")
    buf_free_run_ronly: str | None = Field("", alias="buf_free_run_ronly")
    buf_mode: ADDRESS_VERIFICATION.BufMode | None = Field(ADDRESS_VERIFICATION.BufMode.default, alias="buf_mode")
    buf_mode_ronly: str | None = Field("", alias="buf_mode_ronly")
    coll_type: ADDRESS_VERIFICATION.CollType | None = Field(ADDRESS_VERIFICATION.CollType.auto, alias="coll_type")
    combinability: ADDRESS_VERIFICATION.Combinability | None = Field(
        ADDRESS_VERIFICATION.Combinability.auto, alias="combinability"
    )
    company_name: str = Field("", alias="companyName")
    db2_instance_select: ADDRESS_VERIFICATION.Db2InstanceSelect | None = Field(
        ADDRESS_VERIFICATION.Db2InstanceSelect.use_db2InstanceEnv, alias="db2InstanceSelect"
    )
    db2_name_select: ADDRESS_VERIFICATION.Db2NameSelect | None = Field(
        ADDRESS_VERIFICATION.Db2NameSelect.use_db2NameEnv, alias="db2NameSelect"
    )
    db_path: str = Field("/opt/ibm/data/avi/LQTDB/", alias="dbPath")
    default_country: str | None = Field("", alias="defaultCountry")
    disk_write_inc: int | None = Field(1048576, alias="disk_write_inc")
    disk_write_inc_ronly: str | None = Field("", alias="disk_write_inc_ronly")
    enable_field_match_score: ADDRESS_VERIFICATION.EnableFieldMatchScore | None = Field(
        ADDRESS_VERIFICATION.EnableFieldMatchScore.No, alias="enableFieldMatchScore"
    )
    enable_field_status: ADDRESS_VERIFICATION.EnableFieldStatus | None = Field(
        ADDRESS_VERIFICATION.EnableFieldStatus.No, alias="enableFieldStatus"
    )
    enhanced_g_b: ADDRESS_VERIFICATION.EnhancedGB | None = Field(
        ADDRESS_VERIFICATION.EnhancedGB.No, alias="enhancedGB"
    )
    enhanced_u_s: ADDRESS_VERIFICATION.EnhancedUS | None = Field(
        ADDRESS_VERIFICATION.EnhancedUS.No, alias="enhancedUS"
    )
    error: ADDRESS_VERIFICATION.Error | None = Field(ADDRESS_VERIFICATION.Error.No, alias="error")
    execmode: ADDRESS_VERIFICATION.Execmode | None = Field(
        ADDRESS_VERIFICATION.Execmode.default_par, alias="execmode"
    )
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    geo_coding: ADDRESS_VERIFICATION.GeoCoding | None = Field(ADDRESS_VERIFICATION.GeoCoding.No, alias="geoCoding")
    hide: bool | None = Field(False, alias="hide")
    input_count: int | None = Field(0, alias="input_count")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    key_col_select: ADDRESS_VERIFICATION.KeyColSelect | None = Field(
        ADDRESS_VERIFICATION.KeyColSelect.Select_a_column, alias="keyColSelect"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    less_used_fields: ADDRESS_VERIFICATION.LessUsedFields | None = Field(
        ADDRESS_VERIFICATION.LessUsedFields.No, alias="lessUsedFields"
    )
    list_i_d: str = Field("", alias="listID")
    max_mem_buf_size: int | None = Field(3145728, alias="max_mem_buf_size")
    max_mem_buf_size_ronly: str | None = Field("", alias="max_mem_buf_size_ronly")
    max_results: int | None = Field(3, alias="maxResults")
    minimum_verification_level: ADDRESS_VERIFICATION.MinimumVerificationLevel | None = Field(
        ADDRESS_VERIFICATION.MinimumVerificationLevel.none, alias="minimumVerificationLevel"
    )
    op_callbacks: str | None = Field("qsavlibCalls", alias="opCallbacks")
    output_casing: ADDRESS_VERIFICATION.OutputCasing | None = Field(
        ADDRESS_VERIFICATION.OutputCasing.Title, alias="outputCasing"
    )
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    output_script: ADDRESS_VERIFICATION.OutputScript | None = Field(
        ADDRESS_VERIFICATION.OutputScript.AsProcessed, alias="outputScript"
    )
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    outputlink_ordering_list: list | None = Field([], alias="OutputlinkOrderingList")
    parse_properties: list | None = Field([], alias="parseProperties")
    part_dbname: str | None = Field("eg: SAMPLE", alias="part_dbname")
    part_server: str | None = Field("eg: DB2INST", alias="part_server")
    part_stable: bool | None = Field(None, alias="part_stable")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_table: str | None = Field(None, alias="part_table")
    part_type: ADDRESS_VERIFICATION.PartType | None = Field(ADDRESS_VERIFICATION.PartType.auto, alias="part_type")
    part_unique: bool | None = Field(None, alias="part_unique")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve: ADDRESS_VERIFICATION.Preserve | None = Field(
        ADDRESS_VERIFICATION.Preserve.default_propagate, alias="preserve"
    )
    processing_type: ADDRESS_VERIFICATION.ProcessingType = Field(
        ADDRESS_VERIFICATION.ProcessingType.Parse, alias="processingType"
    )
    queue_upper_size: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: str | None = Field("", alias="queue_upper_size_ronly")
    report_filefor_validation: str = Field("", alias="reportFileforValidation")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field(
        "If sort keys are added, a sort will be performed.", alias="sortInstructions"
    )
    stage_description: list | None = Field("", alias="stageDescription")
    use_city_abbreviations: ADDRESS_VERIFICATION.UseCityAbbreviations | None = Field(
        ADDRESS_VERIFICATION.UseCityAbbreviations.No, alias="useCityAbbreviations"
    )
    use_symbolic_transliteration: ADDRESS_VERIFICATION.UseSymbolicTransliteration | None = Field(
        ADDRESS_VERIFICATION.UseSymbolicTransliteration.true, alias="useSymbolicTransliteration"
    )
    validation_properties: list | None = Field([], alias="validationProperties")
    validation_type: ADDRESS_VERIFICATION.ValidationType | None = Field(
        ADDRESS_VERIFICATION.ValidationType.CorrectionOnly, alias="validationType"
    )

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("validation_type") if (self.processing_type == "Validation") else exclude.add("validation_type")
        include.add("geo_coding") if (self.processing_type == "Validation") else exclude.add("geo_coding")
        include.add("enhanced_u_s") if (self.processing_type == "Validation") else exclude.add("enhanced_u_s")
        (
            include.add("report_filefor_validation")
            if (self.processing_type == "Validation")
            else exclude.add("report_filefor_validation")
        )
        include.add("company_name") if (self.processing_type == "Validation") else exclude.add("company_name")
        include.add("list_i_d") if (self.processing_type == "Validation") else exclude.add("list_i_d")
        (
            include.add("enable_field_status")
            if (self.processing_type == "Validation")
            else exclude.add("enable_field_status")
        )
        (
            include.add("enable_field_match_score")
            if (self.processing_type == "Validation")
            else exclude.add("enable_field_match_score")
        )
        include.add("max_results") if (self.processing_type == "Validation") else exclude.add("max_results")
        (
            include.add("minimum_verification_level")
            if (self.processing_type == "Validation")
            else exclude.add("minimum_verification_level")
        )
        (
            include.add("enhanced_g_b")
            if (((self.processing_type == "Validation")) and (self.validation_type != "USPSCertification"))
            else exclude.add("enhanced_g_b")
        )
        (
            include.add("use_city_abbreviations")
            if (self.validation_type == "USPSCertification")
            else exclude.add("use_city_abbreviations")
        )

        (
            include.add("db_path")
            if (((self.processing_type == "Parse")) or (self.processing_type == "Validation"))
            else exclude.add("db_path")
        )
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
        return {"min": 1, "max": 2}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "add_server_options",
            "address_count",
            "address_line_properties",
            "address_line_separator",
            "buf_free_run",
            "buf_free_run_ronly",
            "buf_mode",
            "buf_mode_ronly",
            "coll_type",
            "combinability",
            "company_name",
            "db2_instance_select",
            "db2_name_select",
            "db_path",
            "default_country",
            "disk_write_inc",
            "disk_write_inc_ronly",
            "enable_field_match_score",
            "enable_field_status",
            "enhanced_g_b",
            "enhanced_u_s",
            "error",
            "execmode",
            "flow_dirty",
            "geo_coding",
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
            "less_used_fields",
            "list_i_d",
            "max_mem_buf_size",
            "max_mem_buf_size_ronly",
            "max_results",
            "minimum_verification_level",
            "op_callbacks",
            "op_name",
            "output_casing",
            "output_count",
            "output_link_description",
            "output_script",
            "outputcol_properties",
            "outputlink_ordering_list",
            "parse_properties",
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
            "preserve",
            "processing_type",
            "queue_upper_size",
            "queue_upper_size_ronly",
            "report_filefor_validation",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "stage_description",
            "use_city_abbreviations",
            "use_symbolic_transliteration",
            "validation_properties",
            "validation_type",
        }
        required = {
            "address_count",
            "company_name",
            "db_path",
            "list_i_d",
            "processing_type",
            "report_filefor_validation",
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
