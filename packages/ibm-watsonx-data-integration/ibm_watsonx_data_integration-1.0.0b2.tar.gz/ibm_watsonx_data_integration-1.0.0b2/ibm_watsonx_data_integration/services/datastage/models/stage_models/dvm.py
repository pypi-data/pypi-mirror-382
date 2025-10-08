import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.dvm_connection import DvmConn
from ibm_watsonx_data_integration.services.datastage.models.enums import DVM
from pydantic import Field
from typing import ClassVar


class dvm(BaseStage):

    op_name: ClassVar[str] = "dvm"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/dvm.svg"
    label: ClassVar[str] = "IBM Data Virtualization Manager for z/OS"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: DvmConn = DvmConn()
    batch_size: int | None = Field(2000, alias="batch_size")
    byte_limit: str | None = Field(None, alias="byte_limit")
    decimal_rounding_mode: DVM.DecimalRoundingMode | None = Field(
        DVM.DecimalRoundingMode.floor, alias="decimal_rounding_mode"
    )
    default_max_string_binary_precision: int | None = Field(20000, alias="default_max_string_binary_precision")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    execmode: DVM.Execmode | None = Field(DVM.Execmode.default_par, alias="execmode")
    generate_unicode_columns: bool | None = Field(False, alias="generate_unicode_columns")
    has_reject_output: bool | None = Field(False, alias="has_reject_output")
    input_count: int | None = Field(0, alias="input_count")
    key_column_names: str | None = Field(None, alias="key_column_names")
    output_count: int | None = Field(0, alias="output_count")
    preserve: DVM.Preserve | None = Field(DVM.Preserve.default_propagate, alias="preserve")
    push_filters: str | None = Field(None, alias="push_filters")
    pushed_filters: str | None = Field(None, alias="pushed_filters")
    rcp: bool | None = Field(True, alias="rcp")
    read_mode: DVM.ReadMode | None = Field(DVM.ReadMode.general, alias="read_mode")
    reject_condition_row_is_rejected: bool | None = Field(False, alias="reject_condition_row_is_rejected")
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_from_link: int | None = Field(None, alias="reject_from_link")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: DVM.RejectUses | None = Field(DVM.RejectUses.rows, alias="reject_uses")
    rejected_filters: str | None = Field(None, alias="rejected_filters")
    row_limit: int | None = Field(None, alias="row_limit")
    schema_name: str | None = Field(None, alias="schema_name")
    select_statement: str = Field(None, alias="select_statement")
    static_statement: str = Field(None, alias="static_statement")
    table_action: DVM.TableAction | None = Field(DVM.TableAction.append, alias="table_action")
    table_name: str = Field(None, alias="table_name")
    update_statement: str | None = Field(None, alias="update_statement")
    write_mode: DVM.WriteMode | None = Field(DVM.WriteMode.insert, alias="write_mode")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("preserve") if (self.output_count and self.output_count > 0) else exclude.add("preserve")
        (
            include.add("reject_uses")
            if (self.reject_from_link and self.reject_from_link > -1)
            else exclude.add("reject_uses")
        )
        (
            include.add("reject_number")
            if (self.reject_from_link and self.reject_from_link > -1)
            else exclude.add("reject_number")
        )
        (
            include.add("reject_data_element_errorcode")
            if (self.reject_from_link and self.reject_from_link > -1)
            else exclude.add("reject_data_element_errorcode")
        )
        (
            include.add("reject_data_element_errortext")
            if (self.reject_from_link and self.reject_from_link > -1)
            else exclude.add("reject_data_element_errortext")
        )
        include.add("reject_threshold") if (self.reject_uses == "percent") else exclude.add("reject_threshold")
        return include, exclude

    def validate_source(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("select_statement")
            if (
                ((not self.schema_name))
                and (not self.table_name)
                and (

                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "select")
                            or (self.read_mode == "select")
                        )

                )
            )
            else exclude.add("select_statement")
        )
        (
            include.add("schema_name")
            if (
                ((not self.select_statement))
                and (

                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "general")
                            or (self.read_mode == "general")
                        )

                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("table_name")
            if (
                ((not self.select_statement))
                and (

                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "general")
                            or (self.read_mode == "general")
                        )

                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("schema_name")
            if (not self.select_statement)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value == "general")
                    or (self.read_mode == "general")
                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("table_name")
            if (not self.select_statement)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value == "general")
                    or (self.read_mode == "general")
                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("select_statement")
            if (not self.schema_name)
            and (not self.table_name)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value == "select")
                    or (self.read_mode == "select")
                )
            )
            else exclude.add("select_statement")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("update_statement")
            if (
                ((not self.static_statement))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "update_statement")
                                or (self.write_mode == "update_statement")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (
                                    hasattr(self.write_mode, "value")
                                    and self.write_mode.value == "update_statement_table_action"
                                )
                                or (self.write_mode == "update_statement_table_action")
                            )

                    )
                )
            )
            else exclude.add("update_statement")
        )
        (
            include.add("schema_name")
            if (
                ((not self.static_statement))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
                            )
                        )
                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "update_statement")
                                or (self.write_mode != "update_statement")
                            )

                    )
                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("table_name")
            if (
                ((not self.static_statement))
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
                            )
                        )
                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "update_statement")
                                or (self.write_mode != "update_statement")
                            )

                    )
                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("key_column_names")
            if (
                (
                    (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )
                            )
                        )
                    )
                )
                and (((not self.update_statement)) and (not self.static_statement))
            )
            else exclude.add("key_column_names")
        )
        (
            include.add("table_action")
            if (
                (
                    (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "insert")
                                    or (self.write_mode == "insert")
                                )
                            )
                        )
                        or (
                            (
                                self.write_mode
                                and (
                                    (
                                        hasattr(self.write_mode, "value")
                                        and self.write_mode.value == "update_statement_table_action"
                                    )
                                    or (self.write_mode == "update_statement_table_action")
                                )
                            )
                        )
                    )
                )
                and (
                    ((not self.static_statement))
                    and (
                        (
                            (
                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                    or (self.write_mode != "static_statement")
                                )
                            )
                        )
                        and (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value != "update_statement")
                                    or (self.write_mode != "update_statement")
                                )

                        )
                    )
                )
            )
            else exclude.add("table_action")
        )
        (
            include.add("static_statement")
            if (
                ((not self.schema_name))
                and (not self.table_name)
                and (not self.update_statement)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "static_statement")
                            or (self.write_mode == "static_statement")
                        )

                )
            )
            else exclude.add("static_statement")
        )
        (
            include.add("batch_size")
            if (((not self.has_reject_output)) or (not self.has_reject_output))
            else exclude.add("batch_size")
        )
        (
            include.add("schema_name")
            if (not self.static_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "static_statement" not in str(self.write_mode.value)
                    )
                    or ("static_statement" not in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_statement" not in str(self.write_mode.value)
                    )
                    or ("update_statement" not in str(self.write_mode))
                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("key_column_names")
            if (

                    self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "insert" in str(self.write_mode.value)
                        )
                        or ("insert" in str(self.write_mode))
                    )
                    or self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update" in str(self.write_mode.value)
                        )
                        or ("update" in str(self.write_mode))
                    )

            )
            and ((not self.update_statement) and (not self.static_statement))
            else exclude.add("key_column_names")
        )
        (
            include.add("static_statement")
            if (not self.schema_name)
            and (not self.table_name)
            and (not self.update_statement)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "static_statement")
                    or (self.write_mode == "static_statement")
                )
            )
            else exclude.add("static_statement")
        )
        (
            include.add("table_name")
            if (not self.static_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "static_statement" not in str(self.write_mode.value)
                    )
                    or ("static_statement" not in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_statement" not in str(self.write_mode.value)
                    )
                    or ("update_statement" not in str(self.write_mode))
                )
            )
            else exclude.add("table_name")
        )
        (
            include.add("batch_size")
            if (not self.has_reject_output) or (self.has_reject_output != "true" or not self.has_reject_output)
            else exclude.add("batch_size")
        )
        (
            include.add("update_statement")
            if (not self.static_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_statement" in str(self.write_mode.value)
                    )
                    or ("update_statement" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "update_statement_table_action" in str(self.write_mode.value)
                    )
                    or ("update_statement_table_action" in str(self.write_mode))
                )
            )
            else exclude.add("update_statement")
        )
        (
            include.add("table_action")
            if (

                    self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "insert" in str(self.write_mode.value)
                        )
                        or ("insert" in str(self.write_mode))
                    )
                    and self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update_statement_table_action" in str(self.write_mode.value)
                        )
                        or ("update_statement_table_action" in str(self.write_mode))
                    )

            )
            and (
                (not self.static_statement)
                and (
                    self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "static_statement" not in str(self.write_mode.value)
                        )
                        or ("static_statement" not in str(self.write_mode))
                    )
                    and self.write_mode
                    and (
                        (
                            hasattr(self.write_mode, "value")
                            and self.write_mode.value
                            and "update_statement" not in str(self.write_mode.value)
                        )
                        or ("update_statement" not in str(self.write_mode))
                    )
                )
            )
            else exclude.add("table_action")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "byte_limit",
            "decimal_rounding_mode",
            "default_max_string_binary_precision",
            "ds_java_heap_size",
            "generate_unicode_columns",
            "key_column_names",
            "push_filters",
            "pushed_filters",
            "rcp",
            "read_mode",
            "rejected_filters",
            "row_limit",
            "schema_name",
            "select_statement",
            "table_name",
        }
        required = {"select_statement", "table_name"}
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
            "batch_size",
            "ds_java_heap_size",
            "has_reject_output",
            "key_column_names",
            "schema_name",
            "static_statement",
            "table_action",
            "table_name",
            "update_statement",
            "write_mode",
        }
        required = {"static_statement"}
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
        props = {"execmode", "input_count", "output_count", "preserve"}
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
                "maxRejectOutputs": 1,
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
        props = {
            "reject_condition_row_is_rejected",
            "reject_data_element_errorcode",
            "reject_data_element_errortext",
            "reject_from_link",
            "reject_number",
            "reject_threshold",
            "reject_uses",
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

    def get_allowed_as_source_props(self) -> bool:
        return True

    def get_allowed_as_target_props(self) -> bool:
        return True
