import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.connections.amazon_postgresql_connection import (
    AmazonPostgresqlConn,
)
from ibm_watsonx_data_integration.services.datastage.models.enums import AMAZON_POSTGRESQL
from pydantic import Field
from typing import ClassVar


class amazon_postgresql(BaseStage):

    op_name: ClassVar[str] = "postgresql-amazon"
    node_type: ClassVar[str] = "binding"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/postgresql-amazon.svg"
    label: ClassVar[str] = "Amazon RDS for PostgreSQL"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    connection: AmazonPostgresqlConn = AmazonPostgresqlConn()
    add_proccode_column: bool | None = Field(False, alias="add_proccode_column")
    batch_size: int | None = Field(2000, alias="batch_size")
    before_after_after_node_fail_on_error: bool | None = Field(True, alias="before_after.after_node.fail_on_error")
    byte_limit: str | None = Field(None, alias="byte_limit")
    call_each_row: bool | None = Field(True, alias="call_each_row")
    call_statement: str | None = Field(None, alias="call_statement")
    create_statement: str | None = Field(None, alias="create_statement")
    default_max_string_binary_precision: int | None = Field(20000, alias="default_max_string_binary_precision")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    ds_java_heap_size: int | None = Field(256, alias="_java._heap_size")
    enable_after_sql: str | None = Field("", alias="before_after.after")
    enable_after_sql_node: str | None = Field("", alias="before_after.after_node")
    enable_before_sql: str | None = Field("", alias="before_after.before")
    enable_before_sql_node: str | None = Field("", alias="before_after.before_node")
    execmode: AMAZON_POSTGRESQL.Execmode | None = Field(AMAZON_POSTGRESQL.Execmode.default_par, alias="execmode")
    existing_table_action: AMAZON_POSTGRESQL.ExistingTableAction | None = Field(
        AMAZON_POSTGRESQL.ExistingTableAction.append, alias="existing_table_action"
    )
    fail_on_error_after_sql: bool | None = Field(True, alias="before_after.after.fail_on_error")
    fail_on_error_before_sql: bool | None = Field(True, alias="before_after.before.fail_on_error")
    fail_on_error_before_sql_node: bool | None = Field(True, alias="before_after.before_node.fail_on_error")
    forward_row_data: bool | None = Field(False, alias="forward_row_data")
    generate_unicode_columns: bool | None = Field(False, alias="generate_unicode_columns")
    has_ref_output: bool | None = Field(False, alias="has_ref_output")
    has_reject_output: bool | None = Field(False, alias="has_reject_output")
    input_count: int | None = Field(0, alias="input_count")
    key_column_names: str | None = Field(None, alias="key_column_names")
    login_timeout: int | None = Field(None, alias="login_timeout")
    lookup_type: AMAZON_POSTGRESQL.LookupType | None = Field(AMAZON_POSTGRESQL.LookupType.empty, alias="lookup_type")
    output_count: int | None = Field(0, alias="output_count")
    preserve: AMAZON_POSTGRESQL.Preserve | None = Field(
        AMAZON_POSTGRESQL.Preserve.default_propagate, alias="preserve"
    )
    procedure_name: str | None = Field(None, alias="procedure_name")
    push_filters: str | None = Field(None, alias="push_filters")
    pushed_filters: str | None = Field(None, alias="pushed_filters")
    rcp: bool | None = Field(True, alias="rcp")
    read_after_sql_node_statements_from_file: bool | None = Field(
        False, alias="before_after.after_node.read_from_file_after_sql_node"
    )
    read_after_sql_statements_from_file: bool | None = Field(
        False, alias="before_after.after.read_from_file_after_sql"
    )
    read_before_sql_node_statement_from_file: bool | None = Field(
        False, alias="before_after.before_node.read_from_file_before_sql_node"
    )
    read_before_sql_statements_from_file: bool | None = Field(
        False, alias="before_after.before.read_from_file_before_sql"
    )
    read_mode: AMAZON_POSTGRESQL.ReadMode | None = Field(AMAZON_POSTGRESQL.ReadMode.general, alias="read_mode")
    reject_condition_row_is_rejected: bool | None = Field(False, alias="reject_condition_row_is_rejected")
    reject_data_element_errorcode: bool | None = Field(False, alias="reject_data_element_errorcode")
    reject_data_element_errortext: bool | None = Field(False, alias="reject_data_element_errortext")
    reject_from_link: int | None = Field(None, alias="reject_from_link")
    reject_number: int | None = Field(None, alias="reject_number")
    reject_threshold: int | None = Field(None, alias="reject_threshold")
    reject_uses: AMAZON_POSTGRESQL.RejectUses | None = Field(AMAZON_POSTGRESQL.RejectUses.rows, alias="reject_uses")
    rejected_filters: str | None = Field(None, alias="rejected_filters")
    row_limit: int | None = Field(None, alias="row_limit")
    sampling_percentage: str | None = Field(None, alias="sampling_percentage")
    sampling_seed: int | None = Field(None, alias="sampling_seed")
    sampling_type: AMAZON_POSTGRESQL.SamplingType | None = Field(
        AMAZON_POSTGRESQL.SamplingType.none, alias="sampling_type"
    )
    schema_name: str | None = Field(None, alias="schema_name")
    select_statement: str = Field(None, alias="select_statement")
    select_statement_read_from_file_select: bool | None = Field(
        False, alias="select_statement.read_from_file_select"
    )
    static_statement: str = Field(None, alias="static_statement")
    table_action: AMAZON_POSTGRESQL.TableAction | None = Field(
        AMAZON_POSTGRESQL.TableAction.append, alias="table_action"
    )
    table_name: str = Field(None, alias="table_name")
    transform: str | None = Field("false", alias="transform")
    update_statement: str | None = Field(None, alias="update_statement")
    update_statement_read_from_file_update: bool | None = Field(
        False, alias="update_statement.read_from_file_update"
    )
    user_defined_function: bool | None = Field(None, alias="user_defined_function")
    write_mode: AMAZON_POSTGRESQL.WriteMode | None = Field(AMAZON_POSTGRESQL.WriteMode.insert, alias="write_mode")

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
            include.add("call_statement")
            if (
                ((not self.table_name))
                and (not self.select_statement)
                and (not self.procedure_name)
                and (

                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "call_statement")
                            or (self.read_mode == "call_statement")
                        )

                )
            )
            else exclude.add("call_statement")
        )
        (
            include.add("row_limit")
            if (

                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value != "call")
                                or (self.read_mode != "call")
                            )
                        )
                    )
                    and (

                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value != "call_statement")
                                or (self.read_mode != "call_statement")
                            )

                    )

            )
            else exclude.add("row_limit")
        )
        (
            include.add("select_statement")
            if (
                ((not self.schema_name))
                and (not self.table_name)
                and (not self.procedure_name)
                and (not self.call_statement)
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
                and (not self.call_statement)
                and (
                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "call")
                                or (self.read_mode == "call")
                            )
                        )
                    )
                    or (

                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "general")
                                or (self.read_mode == "general")
                            )

                    )
                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("table_name")
            if (
                ((not self.select_statement))
                and (not self.procedure_name)
                and (not self.call_statement)
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
            include.add("user_defined_function")
            if (

                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "call")
                                or (self.read_mode == "call")
                            )
                        )
                    )
                    or (

                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "call_statement")
                                or (self.read_mode == "call_statement")
                            )

                    )

            )
            else exclude.add("user_defined_function")
        )
        (
            include.add("add_proccode_column")
            if (
                ((not self.select_statement))
                and (not self.table_name)
                and (
                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "call")
                                or (self.read_mode == "call")
                            )
                        )
                    )
                    or (

                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "call_statement")
                                or (self.read_mode == "call_statement")
                            )

                    )
                )
            )
            else exclude.add("add_proccode_column")
        )
        (
            include.add("procedure_name")
            if (
                ((not self.call_statement))
                and (not self.select_statement)
                and (not self.table_name)
                and (

                        self.read_mode
                        and (
                            (hasattr(self.read_mode, "value") and self.read_mode.value == "call")
                            or (self.read_mode == "call")
                        )

                )
            )
            else exclude.add("procedure_name")
        )
        (
            include.add("select_statement_read_from_file_select")
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
            else exclude.add("select_statement_read_from_file_select")
        )
        (
            include.add("forward_row_data")
            if (
                ((not self.select_statement))
                and (not self.table_name)
                and (
                    (
                        (
                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "call")
                                or (self.read_mode == "call")
                            )
                        )
                    )
                    or (

                            self.read_mode
                            and (
                                (hasattr(self.read_mode, "value") and self.read_mode.value == "call_statement")
                                or (self.read_mode == "call_statement")
                            )

                    )
                )
            )
            else exclude.add("forward_row_data")
        )
        (
            include.add("schema_name")
            if (not self.select_statement)
            and (not self.call_statement)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "call" in str(self.read_mode.value))
                    or ("call" in str(self.read_mode))
                )
                and self.read_mode
                and (
                    (
                        hasattr(self.read_mode, "value")
                        and self.read_mode.value
                        and "general" in str(self.read_mode.value)
                    )
                    or ("general" in str(self.read_mode))
                )
            )
            else exclude.add("schema_name")
        )
        (
            include.add("procedure_name")
            if (not self.call_statement)
            and (not self.select_statement)
            and (not self.table_name)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value == "call") or (self.read_mode == "call")
                )
            )
            else exclude.add("procedure_name")
        )
        (
            include.add("select_statement_read_from_file_select")
            if (not self.schema_name)
            and (not self.table_name)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value == "select")
                    or (self.read_mode == "select")
                )
            )
            else exclude.add("select_statement_read_from_file_select")
        )
        (
            include.add("table_name")
            if (not self.select_statement)
            and (not self.procedure_name)
            and (not self.call_statement)
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
            and (not self.procedure_name)
            and (not self.call_statement)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value == "select")
                    or (self.read_mode == "select")
                )
            )
            else exclude.add("select_statement")
        )
        (
            include.add("add_proccode_column")
            if (not self.select_statement)
            and (not self.table_name)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "call" in str(self.read_mode.value))
                    or ("call" in str(self.read_mode))
                )
                and self.read_mode
                and (
                    (
                        hasattr(self.read_mode, "value")
                        and self.read_mode.value
                        and "call_statement" in str(self.read_mode.value)
                    )
                    or ("call_statement" in str(self.read_mode))
                )
            )
            else exclude.add("add_proccode_column")
        )
        (
            include.add("forward_row_data")
            if (not self.select_statement)
            and (not self.table_name)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "call" in str(self.read_mode.value))
                    or ("call" in str(self.read_mode))
                )
                and self.read_mode
                and (
                    (
                        hasattr(self.read_mode, "value")
                        and self.read_mode.value
                        and "call_statement" in str(self.read_mode.value)
                    )
                    or ("call_statement" in str(self.read_mode))
                )
            )
            else exclude.add("forward_row_data")
        )
        (
            include.add("row_limit")
            if (
                self.read_mode
                and (
                    (
                        hasattr(self.read_mode, "value")
                        and self.read_mode.value
                        and "call" not in str(self.read_mode.value)
                    )
                    or ("call" not in str(self.read_mode))
                )
                and self.read_mode
                and (
                    (
                        hasattr(self.read_mode, "value")
                        and self.read_mode.value
                        and "call_statement" not in str(self.read_mode.value)
                    )
                    or ("call_statement" not in str(self.read_mode))
                )
            )
            else exclude.add("row_limit")
        )
        (
            include.add("call_statement")
            if (not self.table_name)
            and (not self.select_statement)
            and (not self.procedure_name)
            and (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value == "call_statement")
                    or (self.read_mode == "call_statement")
                )
            )
            else exclude.add("call_statement")
        )
        (
            include.add("user_defined_function")
            if (
                self.read_mode
                and (
                    (hasattr(self.read_mode, "value") and self.read_mode.value and "call" in str(self.read_mode.value))
                    or ("call" in str(self.read_mode))
                )
                and self.read_mode
                and (
                    (
                        hasattr(self.read_mode, "value")
                        and self.read_mode.value
                        and "call_statement" in str(self.read_mode.value)
                    )
                    or ("call_statement" in str(self.read_mode))
                )
            )
            else exclude.add("user_defined_function")
        )
        return include, exclude

    def validate_target(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("create_statement")
            if (
                ((not self.static_statement))
                and (not self.procedure_name)
                and (not self.call_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "call")
                                or (self.write_mode != "call")
                            )
                        )
                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "call_statement")
                                or (self.write_mode != "call_statement")
                            )

                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
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
            else exclude.add("create_statement")
        )
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
                and (not self.call_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "call_statement")
                                or (self.write_mode != "call_statement")
                            )
                        )
                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
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
                and (not self.call_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "call")
                                or (self.write_mode != "call")
                            )
                        )
                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "call_statement")
                                or (self.write_mode != "call_statement")
                            )

                    )
                    and (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value != "static_statement")
                                or (self.write_mode != "static_statement")
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
                (((not self.update_statement)) and ((not self.static_statement)))
                and (
                    (
                        (
                            (
                                self.existing_table_action
                                and (
                                    (
                                        hasattr(self.existing_table_action, "value")
                                        and self.existing_table_action.value == "append"
                                    )
                                    or (self.existing_table_action == "append")
                                )
                            )
                        )
                        or (
                            (
                                self.existing_table_action
                                and (
                                    (
                                        hasattr(self.existing_table_action, "value")
                                        and self.existing_table_action.value == "merge"
                                    )
                                    or (self.existing_table_action == "merge")
                                )
                            )
                        )
                        or (
                            (
                                self.existing_table_action
                                and (
                                    (
                                        hasattr(self.existing_table_action, "value")
                                        and self.existing_table_action.value == "update"
                                    )
                                    or (self.existing_table_action == "update")
                                )
                            )
                        )
                    )
                    or (
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

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "merge")
                                    or (self.write_mode == "merge")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )

                        )
                    )
                )
                and (
                    (
                        (
                            (
                                self.existing_table_action
                                and (
                                    (
                                        hasattr(self.existing_table_action, "value")
                                        and self.existing_table_action.value == "append"
                                    )
                                    or (self.existing_table_action == "append")
                                )
                            )
                        )
                        or (
                            (
                                self.existing_table_action
                                and (
                                    (
                                        hasattr(self.existing_table_action, "value")
                                        and self.existing_table_action.value == "merge"
                                    )
                                    or (self.existing_table_action == "merge")
                                )
                            )
                        )
                        or (
                            (
                                self.existing_table_action
                                and (
                                    (
                                        hasattr(self.existing_table_action, "value")
                                        and self.existing_table_action.value == "update"
                                    )
                                    or (self.existing_table_action == "update")
                                )
                            )
                        )
                    )
                    or (
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

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "merge")
                                    or (self.write_mode == "merge")
                                )

                        )
                        or (

                                self.write_mode
                                and (
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "update")
                                    or (self.write_mode == "update")
                                )

                        )
                    )
                )
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
                                    (hasattr(self.write_mode, "value") and self.write_mode.value == "merge")
                                    or (self.write_mode == "merge")
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
                and (not self.procedure_name)
                and (not self.call_statement)
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
            include.add("call_statement")
            if (
                ((not self.static_statement))
                and (not self.schema_name)
                and (not self.table_name)
                and (not self.update_statement)
                and (not self.procedure_name)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "call_statement")
                            or (self.write_mode == "call_statement")
                        )

                )
            )
            else exclude.add("call_statement")
        )
        (
            include.add("update_statement_read_from_file_update")
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
            else exclude.add("update_statement_read_from_file_update")
        )
        (
            include.add("procedure_name")
            if (
                ((not self.static_statement))
                and (not self.table_name)
                and (not self.update_statement)
                and (not self.call_statement)
                and (

                        self.write_mode
                        and (
                            (hasattr(self.write_mode, "value") and self.write_mode.value == "call")
                            or (self.write_mode == "call")
                        )

                )
            )
            else exclude.add("procedure_name")
        )
        (
            include.add("batch_size")
            if (((not self.has_reject_output)) or (not self.has_reject_output))
            else exclude.add("batch_size")
        )
        (
            include.add("call_each_row")
            if (
                ((not self.static_statement))
                and (not self.table_name)
                and (not self.update_statement)
                and (
                    (
                        (
                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "call")
                                or (self.write_mode == "call")
                            )
                        )
                    )
                    or (

                            self.write_mode
                            and (
                                (hasattr(self.write_mode, "value") and self.write_mode.value == "call_statement")
                                or (self.write_mode == "call_statement")
                            )

                    )
                )
            )
            else exclude.add("call_each_row")
        )
        (
            include.add("schema_name")
            if (not self.static_statement)
            and (not self.call_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call_statement" not in str(self.write_mode.value)
                    )
                    or ("call_statement" not in str(self.write_mode))
                )
                and self.write_mode
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
            include.add("procedure_name")
            if (not self.static_statement)
            and (not self.table_name)
            and (not self.update_statement)
            and (not self.call_statement)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "call")
                    or (self.write_mode == "call")
                )
            )
            else exclude.add("procedure_name")
        )
        (
            include.add("key_column_names")
            if ((not self.update_statement) and (not self.static_statement))
            and (
                (
                    self.existing_table_action
                    and (
                        (
                            hasattr(self.existing_table_action, "value")
                            and self.existing_table_action.value
                            and "append" in str(self.existing_table_action.value)
                        )
                        or ("append" in str(self.existing_table_action))
                    )
                    or self.existing_table_action
                    and (
                        (
                            hasattr(self.existing_table_action, "value")
                            and self.existing_table_action.value
                            and "merge" in str(self.existing_table_action.value)
                        )
                        or ("merge" in str(self.existing_table_action))
                    )
                    or self.existing_table_action
                    and (
                        (
                            hasattr(self.existing_table_action, "value")
                            and self.existing_table_action.value
                            and "update" in str(self.existing_table_action.value)
                        )
                        or ("update" in str(self.existing_table_action))
                    )
                )
                or (
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
                            and "merge" in str(self.write_mode.value)
                        )
                        or ("merge" in str(self.write_mode))
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
            )
            and (
                (
                    self.existing_table_action
                    and (
                        (
                            hasattr(self.existing_table_action, "value")
                            and self.existing_table_action.value
                            and "append" in str(self.existing_table_action.value)
                        )
                        or ("append" in str(self.existing_table_action))
                    )
                    or self.existing_table_action
                    and (
                        (
                            hasattr(self.existing_table_action, "value")
                            and self.existing_table_action.value
                            and "merge" in str(self.existing_table_action.value)
                        )
                        or ("merge" in str(self.existing_table_action))
                    )
                    or self.existing_table_action
                    and (
                        (
                            hasattr(self.existing_table_action, "value")
                            and self.existing_table_action.value
                            and "update" in str(self.existing_table_action.value)
                        )
                        or ("update" in str(self.existing_table_action))
                    )
                )
                or (
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
                            and "merge" in str(self.write_mode.value)
                        )
                        or ("merge" in str(self.write_mode))
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
            )
            else exclude.add("key_column_names")
        )
        (
            include.add("create_statement")
            if (not self.static_statement)
            and (not self.procedure_name)
            and (not self.call_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call" not in str(self.write_mode.value)
                    )
                    or ("call" not in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call_statement" not in str(self.write_mode.value)
                    )
                    or ("call_statement" not in str(self.write_mode))
                )
                and self.write_mode
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
            else exclude.add("create_statement")
        )
        (
            include.add("static_statement")
            if (not self.schema_name)
            and (not self.table_name)
            and (not self.update_statement)
            and (not self.procedure_name)
            and (not self.call_statement)
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
            and (not self.call_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call" not in str(self.write_mode.value)
                    )
                    or ("call" not in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call_statement" not in str(self.write_mode.value)
                    )
                    or ("call_statement" not in str(self.write_mode))
                )
                and self.write_mode
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
            include.add("update_statement_read_from_file_update")
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
            else exclude.add("update_statement_read_from_file_update")
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
            include.add("call_statement")
            if (not self.static_statement)
            and (not self.schema_name)
            and (not self.table_name)
            and (not self.update_statement)
            and (not self.procedure_name)
            and (
                self.write_mode
                and (
                    (hasattr(self.write_mode, "value") and self.write_mode.value == "call_statement")
                    or (self.write_mode == "call_statement")
                )
            )
            else exclude.add("call_statement")
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
                            and "merge" in str(self.write_mode.value)
                        )
                        or ("merge" in str(self.write_mode))
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
        (
            include.add("call_each_row")
            if (not self.static_statement)
            and (not self.table_name)
            and (not self.update_statement)
            and (
                self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call" in str(self.write_mode.value)
                    )
                    or ("call" in str(self.write_mode))
                )
                and self.write_mode
                and (
                    (
                        hasattr(self.write_mode, "value")
                        and self.write_mode.value
                        and "call_statement" in str(self.write_mode.value)
                    )
                    or ("call_statement" in str(self.write_mode))
                )
            )
            else exclude.add("call_each_row")
        )
        return include, exclude

    def get_source_props(self) -> dict:
        include, exclude = self.validate_source()
        props = {
            "add_proccode_column",
            "before_after_after_node_fail_on_error",
            "byte_limit",
            "call_statement",
            "default_max_string_binary_precision",
            "ds_java_heap_size",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_sql",
            "enable_before_sql_node",
            "fail_on_error_after_sql",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "forward_row_data",
            "generate_unicode_columns",
            "has_ref_output",
            "key_column_names",
            "lookup_type",
            "procedure_name",
            "push_filters",
            "pushed_filters",
            "rcp",
            "read_after_sql_node_statements_from_file",
            "read_after_sql_statements_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statements_from_file",
            "read_mode",
            "rejected_filters",
            "row_limit",
            "sampling_percentage",
            "sampling_seed",
            "sampling_type",
            "schema_name",
            "select_statement",
            "select_statement_read_from_file_select",
            "table_name",
            "transform",
            "user_defined_function",
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
            "before_after_after_node_fail_on_error",
            "call_each_row",
            "call_statement",
            "create_statement",
            "ds_java_heap_size",
            "enable_after_sql",
            "enable_after_sql_node",
            "enable_before_sql",
            "enable_before_sql_node",
            "existing_table_action",
            "fail_on_error_after_sql",
            "fail_on_error_before_sql",
            "fail_on_error_before_sql_node",
            "has_reject_output",
            "key_column_names",
            "procedure_name",
            "read_after_sql_node_statements_from_file",
            "read_after_sql_statements_from_file",
            "read_before_sql_node_statement_from_file",
            "read_before_sql_statements_from_file",
            "schema_name",
            "static_statement",
            "table_action",
            "table_name",
            "update_statement",
            "update_statement_read_from_file_update",
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
