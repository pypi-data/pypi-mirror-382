import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import SURROGATE_KEY_GENERATOR
from pydantic import Field
from typing import ClassVar


class surrogate_key_generator(BaseStage):

    op_name: ClassVar[str] = "PxSurrogateKeyGeneratorN"
    node_type: ClassVar[str] = "execution_node"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/PxSurrogateKeyGeneratorN.svg"
    label: ClassVar[str] = "Surrogate Key Generator"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    account_name: str = Field(None, alias="account_name")
    admin: SURROGATE_KEY_GENERATOR.Admin | None = Field(SURROGATE_KEY_GENERATOR.Admin.create, alias="admin")
    advanced_hostname: str = Field(None, alias="advanced.hostname")
    advanced_port: int = Field(50000, alias="advanced.port")
    as_sequencer: SURROGATE_KEY_GENERATOR.AsSequencer | None = Field(
        SURROGATE_KEY_GENERATOR.AsSequencer.false, alias="asSequencer"
    )
    auto_column_propagation: bool | None = Field(None, alias="auto_column_propagation")
    block_size: int | None = Field(2, alias="block_size")
    block_size_properties: dict | None = Field(None, alias="blockSizeProperties")
    buf_free_run: int | None = Field(50, alias="buf_free_run")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode: SURROGATE_KEY_GENERATOR.BufMode | None = Field(
        SURROGATE_KEY_GENERATOR.BufMode.default, alias="buf_mode"
    )
    buf_mode_ronly: SURROGATE_KEY_GENERATOR.BufModeRonly | None = Field(
        SURROGATE_KEY_GENERATOR.BufModeRonly.default, alias="buf_mode_ronly"
    )
    client_dbname: str | None = Field(None, alias="client_dbname")
    client_instance: str | None = Field(None, alias="client_instance")
    coll_type: SURROGATE_KEY_GENERATOR.CollType | None = Field(
        SURROGATE_KEY_GENERATOR.CollType.auto, alias="coll_type"
    )
    combinability: SURROGATE_KEY_GENERATOR.Combinability | None = Field(
        SURROGATE_KEY_GENERATOR.Combinability.auto, alias="combinability"
    )
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    database: str = Field(None, alias="database")
    db2_cat: bool | None = Field(None, alias="db2Cat")
    dbblocktype: SURROGATE_KEY_GENERATOR.Dbblocktype | None = Field(
        SURROGATE_KEY_GENERATOR.Dbblocktype.adaptivesize, alias="dbblocktype"
    )
    dbtype: SURROGATE_KEY_GENERATOR.Dbtype | None = Field(SURROGATE_KEY_GENERATOR.Dbtype.db2, alias="dbtype")
    dbtype_properties: dict | None = Field(None, alias="dbtypeProperties")
    disk_write_inc: int | None = Field(1048576, alias="disk_write_inc")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    dsn_type: SURROGATE_KEY_GENERATOR.DsnType = Field(SURROGATE_KEY_GENERATOR.DsnType.DB2, alias="dsn_type")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    execmode: SURROGATE_KEY_GENERATOR.Execmode | None = Field(
        SURROGATE_KEY_GENERATOR.Execmode.default_par, alias="execmode"
    )
    fileblocktype: SURROGATE_KEY_GENERATOR.Fileblocktype | None = Field(
        SURROGATE_KEY_GENERATOR.Fileblocktype.adaptivesize, alias="fileblocktype"
    )
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    hide: bool | None = Field(False, alias="hide")
    hostname: str = Field(None, alias="hostname")
    input_count: int | None = Field(0, alias="input_count")
    input_key: str = Field(None, alias="input_key")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    key_col_select: SURROGATE_KEY_GENERATOR.KeyColSelect | None = Field(
        SURROGATE_KEY_GENERATOR.KeyColSelect.default, alias="keyColSelect"
    )
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    keysourcetype: SURROGATE_KEY_GENERATOR.Keysourcetype = Field(
        SURROGATE_KEY_GENERATOR.Keysourcetype.file, alias="keysourcetype"
    )
    max_mem_buf_size: int | None = Field(3145728, alias="max_mem_buf_size")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    oracle_db_host: str = Field(None, alias="oracle_db_host")
    oracle_db_port: str = Field(None, alias="oracle_db_port")
    oracle_service_name: str = Field(None, alias="oracle_service_name")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_count: int | None = Field(0, alias="output_count")
    output_key: str = Field(None, alias="output_key")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    part_client_dbname: str | None = Field(None, alias="part_client_dbname")
    part_client_instance: str | None = Field(None, alias="part_client_instance")
    part_dbconnection: str | None = Field("", alias="part_dbconnection")
    part_stable: bool | None = Field(None, alias="part_stable")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_table: str | None = Field(None, alias="part_table")
    part_type: SURROGATE_KEY_GENERATOR.PartType | None = Field(
        SURROGATE_KEY_GENERATOR.PartType.auto, alias="part_type"
    )
    part_unique: bool | None = Field(None, alias="part_unique")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    password: str = Field(None, alias="password")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    port: str = Field(None, alias="port")
    preserve: SURROGATE_KEY_GENERATOR.Preserve | None = Field(
        SURROGATE_KEY_GENERATOR.Preserve.default_propagate, alias="preserve"
    )
    queue_upper_size: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    records: int | None = Field(10, alias="records")
    role: str = Field(None, alias="role")
    runtime_column_propagation: bool | None = Field(None, alias="runtime_column_propagation")
    schema_: str = Field(None, alias="schema")
    service_name: str = Field(None, alias="service_name")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sk_id: str = Field(None, alias="sk_id")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    source_conn: str | None = Field("", alias="sourceConn")
    source_name_check: bool | None = Field(None, alias="sourceNameCheck")
    stage_description: list | None = Field("", alias="stageDescription")
    start_value: int | None = Field(1, alias="start_value")
    start_value_plus: int | None = Field(1, alias="start_value +")
    update_action: SURROGATE_KEY_GENERATOR.UpdateAction | None = Field(
        SURROGATE_KEY_GENERATOR.UpdateAction.admin_update, alias="update_action"
    )
    username: str = Field(None, alias="username")
    viewonly: SURROGATE_KEY_GENERATOR.Viewonly | None = Field(SURROGATE_KEY_GENERATOR.Viewonly.no, alias="viewonly")
    warehouse: str = Field(None, alias="warehouse")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        (
            include.add("dbtype_properties")
            if (

                    self.keysourcetype
                    and (
                        (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                        or (self.keysourcetype == "dbsequence")
                    )

            )
            else exclude.add("dbtype_properties")
        )
        (
            include.add("db2_cat")
            if (
                (
                    (
                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )
                    )
                )
                and (self.dbtype == "db2")
            )
            else exclude.add("db2_cat")
        )
        (
            include.add("advanced_hostname")
            if (
                (
                    (
                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )
                    )
                )
                and (self.source_conn == "<Flow connection>")
                and (self.dbtype == "db2")
            )
            else exclude.add("advanced_hostname")
        )
        (
            include.add("advanced_port")
            if (
                (
                    (
                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )
                    )
                )
                and (self.source_conn == "<Flow connection>")
                and (self.dbtype == "db2")
            )
            else exclude.add("advanced_port")
        )
        (
            include.add("username")
            if (
                (
                    (
                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )
                    )
                )
                and (self.source_conn == "<Flow connection>")
                and (self.dbtype == "db2")
            )
            else exclude.add("username")
        )
        (
            include.add("password")
            if (
                (
                    (
                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )
                    )
                )
                and (self.source_conn == "<Flow connection>")
                and (self.dbtype == "db2")
            )
            else exclude.add("password")
        )

        (
            include.add("oracle_db_host")
            if (
                (
                    (
                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )
                    )
                )
                and (self.source_conn == "<Flow connection>")
                and (self.dbtype == "oracle")
            )
            else exclude.add("oracle_db_host")
        )
        (
            include.add("as_sequencer")
            if (
                ((self.output_count != 0))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "dbsequence")
                            or (self.keysourcetype != "dbsequence")
                        )

                )
                and (())
            )
            else exclude.add("as_sequencer")
        )
        include.add("preserve") if (self.output_count and self.output_count > 0) else exclude.add("preserve")
        (
            include.add("dbtype")
            if (

                    self.keysourcetype
                    and (
                        (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                        or (self.keysourcetype == "dbsequence")
                    )

            )
            else exclude.add("dbtype")
        )
        (
            include.add("source_conn")
            if (

                    self.keysourcetype
                    and (
                        (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                        or (self.keysourcetype == "dbsequence")
                    )

            )
            else exclude.add("source_conn")
        )
        (
            include.add("client_instance")
            if (

                    self.keysourcetype
                    and (
                        (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                        or (self.keysourcetype == "dbsequence")
                    )

            )
            else exclude.add("client_instance")
        )
        (
            include.add("client_dbname")
            if (

                    self.keysourcetype
                    and (
                        (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                        or (self.keysourcetype == "dbsequence")
                    )

            )
            else exclude.add("client_dbname")
        )
        (
            include.add("source_conn")
            if (

                    self.keysourcetype
                    and (
                        (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                        or (self.keysourcetype != "file")
                    )

            )
            else exclude.add("source_conn")
        )
        (
            include.add("admin")
            if (
                ((self.output_count == 0))
                and (self.input_count == 0)
                and (

                        self.viewonly
                        and (
                            (hasattr(self.viewonly, "value") and self.viewonly.value != "admin viewonly")
                            or (self.viewonly != "admin viewonly")
                        )

                )
            )
            else exclude.add("admin")
        )
        (
            include.add("viewonly")
            if (
                ((self.output_count == 0))
                and (self.input_count == 0)
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "dbsequence")
                            or (self.keysourcetype != "dbsequence")
                        )

                )
            )
            else exclude.add("viewonly")
        )
        (
            include.add("update_action")
            if (
                ((self.input_count != 0))
                and (self.output_count == 0)
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "dbsequence")
                            or (self.keysourcetype != "dbsequence")
                        )

                )
            )
            else exclude.add("update_action")
        )
        (
            include.add("input_key")
            if (
                ((self.input_count != 0))
                and (self.output_count == 0)
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "dbsequence")
                            or (self.keysourcetype != "dbsequence")
                        )

                )
            )
            else exclude.add("input_key")
        )
        include.add("output_key") if (self.output_count != 0) else exclude.add("output_key")
        (
            include.add("start_value")
            if (
                ((self.output_count != 0))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "file")
                            or (self.keysourcetype == "file")
                        )

                )
                and (())
            )
            else exclude.add("start_value")
        )
        (
            include.add("fileblocktype")
            if (((self.input_count == 0)) and (self.output_count != 0) and (()))
            else exclude.add("fileblocktype")
        )
        (
            include.add("start_value_plus")
            if (
                ((self.input_count == 0))
                and (self.output_count == 0)
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )

                )
                and (())
            )
            else exclude.add("start_value_plus")
        )
        (
            include.add("dbblocktype")
            if (
                ((self.input_count == 0))
                and (self.output_count == 0)
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )

                )
                and (())
                and (

                        self.admin
                        and (
                            (hasattr(self.admin, "value") and self.admin.value == "create") or (self.admin == "create")
                        )

                )
            )
            else exclude.add("dbblocktype")
        )
        (
            include.add("records")
            if (((self.input_count == 0)) and (self.output_count != 0) and (()))
            else exclude.add("records")
        )
        (
            include.add("fileblocktype")
            if (
                ((self.output_count != 0))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "file")
                            or (self.keysourcetype == "file")
                        )

                )
                and (())
            )
            else exclude.add("fileblocktype")
        )
        (
            include.add("block_size")
            if (
                (
                    ((self.output_count != 0))
                    and (
                        (
                            self.viewonly
                            and (
                                (hasattr(self.viewonly, "value") and self.viewonly.value == " ")
                                or (self.viewonly == " ")
                            )
                        )
                    )
                    and (
                        (
                            self.admin
                            and (
                                (hasattr(self.admin, "value") and self.admin.value == "create")
                                or (self.admin == "create")
                            )
                        )
                    )
                    and ((self.fileblocktype == "usersize"))
                    and (())
                )
                or (
                    ((self.output_count == 0))
                    and (self.input_count == 0)
                    and (

                            self.viewonly
                            and (
                                (hasattr(self.viewonly, "value") and self.viewonly.value == " ")
                                or (self.viewonly == " ")
                            )

                    )
                    and (

                            self.admin
                            and (
                                (hasattr(self.admin, "value") and self.admin.value == "create")
                                or (self.admin == "create")
                            )

                    )
                    and (self.dbblocktype == "usersize")
                    and (())
                )
            )
            else exclude.add("block_size")
        )
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
            include.add("client_instance")
            if (
                ((self.dbtype == "db2"))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )

                )
            )
            else exclude.add("client_instance")
        )
        (
            include.add("client_dbname")
            if (
                ((self.dbtype == "db2"))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )

                )
            )
            else exclude.add("client_dbname")
        )
        (
            include.add("dsn_type")
            if (
                ((self.dbtype == "odbc"))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )

                )
            )
            else exclude.add("dsn_type")
        )
        (
            include.add("password")
            if (
                ((self.source_conn == "<Flow connection>"))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )

                )
            )
            else exclude.add("password")
        )
        (
            include.add("advanced_hostname")
            if (
                ((self.dbtype == "db2"))
                and (self.source_conn == "<Flow connection>")
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )

                )
            )
            else exclude.add("advanced_hostname")
        )
        (
            include.add("username")
            if (
                ((self.source_conn == "<Flow connection>"))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )

                )
            )
            else exclude.add("username")
        )
        (
            include.add("advanced_port")
            if (
                ((self.dbtype == "db2"))
                and (self.source_conn == "<Flow connection>")
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )

                )
            )
            else exclude.add("advanced_port")
        )
        (
            include.add("oracle_service_name")
            if (
                ((self.dbtype == "oracle"))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )

                )
                and (self.source_conn == "<Flow connection>")
            )
            else exclude.add("oracle_service_name")
        )
        (
            include.add("oracle_db_port")
            if (
                ((self.dbtype == "oracle"))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )

                )
                and (self.source_conn == "<Flow connection>")
            )
            else exclude.add("oracle_db_port")
        )
        (
            include.add("username")
            if (
                (
                    (
                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )
                    )
                )
                and (self.source_conn == "<Flow connection>")
            )
            else exclude.add("username")
        )
        (
            include.add("password")
            if (
                (
                    (
                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )
                    )
                )
                and (self.source_conn == "<Flow connection>")
            )
            else exclude.add("password")
        )
        (
            include.add("oracle_db_host")
            if (
                ((self.dbtype == "oracle"))
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value == "dbsequence")
                            or (self.keysourcetype == "dbsequence")
                        )

                )
                and (self.source_conn == "<Flow connection>")
            )
            else exclude.add("oracle_db_host")
        )
        (
            include.add("username")
            if (
                ((self.dbtype == "odbc"))
                and (self.dbtype != "db2")
                and (self.dbtype != "oracle")
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )

                )
            )
            else exclude.add("username")
        )
        (
            include.add("password")
            if (
                ((self.dbtype == "odbc"))
                and (self.dbtype != "db2")
                and (self.dbtype != "oracle")
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )

                )
            )
            else exclude.add("password")
        )
        (
            include.add("hostname")
            if (
                ((self.dbtype == "odbc"))
                and (((self.dsn_type == "Oracle")) or (self.dsn_type == "DB2"))
                and (self.dbtype != "db2")
            )
            else exclude.add("hostname")
        )
        (
            include.add("port")
            if (
                ((self.dbtype == "odbc"))
                and (((self.dsn_type == "Oracle")) or (self.dsn_type == "DB2"))
                and (self.dbtype != "db2")
            )
            else exclude.add("port")
        )
        (
            include.add("account_name")
            if (((self.dbtype == "odbc")) and (self.dsn_type == "Snowflake"))
            else exclude.add("account_name")
        )
        (
            include.add("warehouse")
            if (((self.dbtype == "odbc")) and (self.dsn_type == "Snowflake"))
            else exclude.add("warehouse")
        )
        include.add("role") if (((self.dbtype == "odbc")) and (self.dsn_type == "Snowflake")) else exclude.add("role")
        (
            include.add("schema_")
            if (((self.dbtype == "odbc")) and (self.dsn_type == "Snowflake"))
            else exclude.add("schema_")
        )
        (
            include.add("service_name")
            if (
                ((self.dbtype == "odbc"))
                and (self.dsn_type == "Oracle")
                and (

                        self.keysourcetype
                        and (
                            (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                            or (self.keysourcetype != "file")
                        )

                )
            )
            else exclude.add("service_name")
        )
        (
            include.add("database")
            if (
                (
                    (
                        (
                            self.keysourcetype
                            and (
                                (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                                or (self.keysourcetype != "file")
                            )
                        )
                    )
                    and ((self.source_conn == "<Flow connection>"))
                    and ((self.dbtype == "db2"))
                )
                or (
                    ((self.dbtype == "odbc"))
                    and (((self.dsn_type == "DB2")) or (self.dsn_type == "Snowflake"))
                    and (

                            self.keysourcetype
                            and (
                                (hasattr(self.keysourcetype, "value") and self.keysourcetype.value != "file")
                                or (self.keysourcetype != "file")
                            )

                    )
                )
            )
            else exclude.add("database")
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
        return {"min": 0, "max": 1}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "account_name",
            "additional_properties_set_option",
            "additional_properties_set_options",
            "additional_props",
            "admin",
            "advanced_hostname",
            "advanced_port",
            "as_sequencer",
            "auto_column_propagation",
            "block_size",
            "block_size_properties",
            "buf_free_run",
            "buf_free_run_ronly",
            "buf_mode",
            "buf_mode_ronly",
            "client_dbname",
            "client_instance",
            "coll_type",
            "combinability",
            "current_output_link_type",
            "database",
            "db2_cat",
            "dbblocktype",
            "dbtype",
            "dbtype_properties",
            "disk_write_inc",
            "disk_write_inc_ronly",
            "dsn_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "execmode",
            "fileblocktype",
            "flow_dirty",
            "hide",
            "hostname",
            "input_count",
            "input_key",
            "input_link_description",
            "inputcol_properties",
            "key_col_select",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "keysourcetype",
            "max_mem_buf_size",
            "max_mem_buf_size_ronly",
            "oracle_db_host",
            "oracle_db_port",
            "oracle_service_name",
            "output_acp_should_hide",
            "output_count",
            "output_key",
            "output_link_description",
            "outputcol_properties",
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
            "password",
            "perform_sort",
            "perform_sort_coll",
            "perform_sort_modulus",
            "port",
            "preserve",
            "queue_upper_size",
            "queue_upper_size_ronly",
            "records",
            "role",
            "runtime_column_propagation",
            "schema_",
            "service_name",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sk_id",
            "sort_instructions",
            "sort_instructions_text",
            "source_conn",
            "source_name_check",
            "stage_description",
            "start_value",
            "start_value_plus",
            "update_action",
            "username",
            "viewonly",
            "warehouse",
        }
        required = {
            "account_name",
            "advanced_hostname",
            "advanced_port",
            "current_output_link_type",
            "database",
            "dsn_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "hostname",
            "input_key",
            "keysourcetype",
            "oracle_db_host",
            "oracle_db_port",
            "oracle_service_name",
            "output_acp_should_hide",
            "output_key",
            "password",
            "port",
            "role",
            "schema_",
            "service_name",
            "sk_id",
            "username",
            "warehouse",
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
