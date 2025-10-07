import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import WEB_SERVICE
from pydantic import Field
from typing import ClassVar


class web_service(BaseStage):

    op_name: ClassVar[str] = "WSTransformerPX"
    node_type: ClassVar[str] = "execution_node"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/WSTransformerPX.svg"
    label: ClassVar[str] = "Web Service"
    allow_column_mapping: bool | None = Field(False, alias="allow_column_mapping")
    authentication_password: str | None = Field("", alias="authentication_password")
    authentication_user_name: str | None = Field("", alias="authentication_user_name")
    auto_column_propagation: bool | None = Field(None, alias="auto_column_propagation")
    buf_free_run: int | None = Field(50, alias="buf_free_run")
    buf_free_run_ronly: int | None = Field(50, alias="buf_free_run_ronly")
    buf_mode: WEB_SERVICE.BufMode | None = Field(WEB_SERVICE.BufMode.default, alias="buf_mode")
    buf_mode_ronly: WEB_SERVICE.BufModeRonly | None = Field(WEB_SERVICE.BufModeRonly.default, alias="buf_mode_ronly")
    certificate_passwd: str | None = Field("", alias="certificate_passwd")
    coll_type: WEB_SERVICE.CollType | None = Field(WEB_SERVICE.CollType.auto, alias="coll_type")
    combinability: WEB_SERVICE.Combinability | None = Field(WEB_SERVICE.Combinability.auto, alias="combinability")
    current_output_link_type: str = Field("PRIMARY", alias="currentOutputLinkType")
    disk_write_inc: int | None = Field(1048576, alias="disk_write_inc")
    disk_write_inc_ronly: int | None = Field(1048576, alias="disk_write_inc_ronly")
    enable_flow_acp_control: bool = Field(True, alias="enableFlowAcpControl")
    enable_schemaless_design: bool = Field(False, alias="enableSchemalessDesign")
    error_handling: WEB_SERVICE.ErrorHandling | None = Field(WEB_SERVICE.ErrorHandling.fatal, alias="error_handling")
    execmode: WEB_SERVICE.Execmode | None = Field(WEB_SERVICE.Execmode.default_seq, alias="execmode")
    field_delimiter: str | None = Field(" ", alias="field_delimiter")
    flow_dirty: str | None = Field("false", alias="flow_dirty")
    has_reference_output: bool | None = Field(False, alias="hasReferenceOutput")
    hide: bool | None = Field(False, alias="hide")
    inherit_from_stage: int | None = Field(1, alias="inherit_from_stage")
    input_col: list | None = Field(None, alias="input_col")
    input_count: int | None = Field(0, alias="input_count")
    input_description: str | None = Field("0", alias="input_description")
    input_link_description: list | None = Field("", alias="inputLinkDescription")
    input_message_table_id: str | None = Field("", alias="input_message_table_id")
    input_name: str | None = Field("", alias="input_name")
    input_namespace_name: str | None = Field("", alias="input_namespace_name")
    input_namespace_value: str | None = Field("", alias="input_namespace_value")
    input_request: str | None = Field("", alias="input_request")
    inputcol_properties: list | None = Field([], alias="inputcolProperties")
    is_authentication_required: bool | None = Field(False, alias="is_authentication_required")
    is_automatic_trust: bool | None = Field(False, alias="is_automatic_trust")
    is_certificate_required: bool | None = Field(False, alias="is_certificate_required")
    is_input_header_xml_column: bool | None = Field(False, alias="is_input_header_xml_column")
    is_input_xml_column: bool | None = Field(False, alias="is_input_xml_column")
    is_log_reject_reason_disabled: bool | None = Field(False, alias="is_log_reject_reason_disabled")
    is_output_header_xml_column: bool | None = Field(False, alias="is_output_header_xml_column")
    is_output_xml_column: bool | None = Field(False, alias="is_output_xml_column")
    is_pass_through_disabled: bool | None = Field(False, alias="is_pass_through_disabled")
    is_proxy_required: bool | None = Field(False, alias="is_proxy_required")
    is_reject_column: bool | None = Field(False, alias="is_reject_column")
    is_reject_link: bool | None = Field(False, alias="is_reject_link")
    jvm_options: str | None = Field("", alias="jvm_options")
    key_col_select: WEB_SERVICE.KeyColSelect | None = Field(WEB_SERVICE.KeyColSelect.default, alias="keyColSelect")
    key_cols_coll: list | None = Field([], alias="keyColsColl")
    key_cols_coll_ordered: list | None = Field([], alias="keyColsCollOrdered")
    key_cols_coll_robin: list | None = Field([], alias="keyColsCollRobin")
    key_cols_none: list | None = Field([], alias="keyColsNone")
    key_cols_part: list | None = Field([], alias="keyColsPart")
    keystore_file: str | None = Field("", alias="keystore_file")
    link_minimised: int | None = Field(0, alias="LinkMinimised")
    log_response: WEB_SERVICE.LogResponse | None = Field(WEB_SERVICE.LogResponse.zero, alias="log_response")
    max_mem_buf_size: int | None = Field(3145728, alias="max_mem_buf_size")
    max_mem_buf_size_ronly: int | None = Field(3145728, alias="max_mem_buf_size_ronly")
    operation_timeout: int | None = Field(0, alias="operation_timeout")
    output_acp_should_hide: bool = Field(True, alias="outputAcpShouldHide")
    output_col: list | None = Field(None, alias="output_col")
    output_count: int | None = Field(0, alias="output_count")
    output_link_description: list | None = Field("", alias="outputLinkDescription")
    output_message_table_id: str | None = Field("", alias="output_message_table_id")
    output_namespace_name: str | None = Field("", alias="output_namespace_name")
    output_namespace_value: str | None = Field("", alias="output_namespace_value")
    output_reject_column: str | None = Field("", alias="output_reject_column")
    outputcol_properties: list | None = Field([], alias="outputcolProperties")
    part_client_dbname: str | None = Field(None, alias="part_client_dbname")
    part_client_instance: str | None = Field(None, alias="part_client_instance")
    part_coll: str | None = Field("part_type", alias="part_coll")
    part_dbconnection: str | None = Field("", alias="part_dbconnection")
    part_stable: bool | None = Field(None, alias="part_stable")
    part_stable_coll: bool | None = Field(False, alias="part_stable_coll")
    part_stable_ordered: bool | None = Field(False, alias="part_stable_ordered")
    part_stable_roundrobin_coll: bool | None = Field(False, alias="part_stable_roundrobin_coll")
    part_table: str | None = Field(None, alias="part_table")
    part_type: WEB_SERVICE.PartType | None = Field(WEB_SERVICE.PartType.auto, alias="part_type")
    part_unique: bool | None = Field(None, alias="part_unique")
    part_unique_coll: bool | None = Field(False, alias="part_unique_coll")
    part_unique_ordered: bool | None = Field(False, alias="part_unique_ordered")
    part_unique_roundrobin_coll: bool | None = Field(False, alias="part_unique_roundrobin_coll")
    perform_sort: bool | None = Field(False, alias="perform_sort")
    perform_sort_coll: bool | None = Field(False, alias="perform_sort_coll")
    perform_sort_modulus: bool | None = Field(False, alias="perform_sort_modulus")
    preserve: WEB_SERVICE.Preserve | None = Field(WEB_SERVICE.Preserve.default_clear, alias="preserve")
    proxy_host_name: str | None = Field("", alias="proxy_host_name")
    proxy_password: str | None = Field("", alias="proxy_password")
    proxy_port_number: str | None = Field("", alias="proxy_port_number")
    proxy_user_name: str | None = Field("", alias="proxy_user_name")
    queue_upper_size: int | None = Field(0, alias="queue_upper_size")
    queue_upper_size_ronly: int | None = Field(0, alias="queue_upper_size_ronly")
    reject_link_index: int | None = Field(-1, alias="rejectLinkIndex")
    reject_link_name: str | None = Field("", alias="rejectLinkName")
    request_mapping: str | None = Field("", alias="request_mapping")
    request_name: str | None = Field("", alias="requestName")
    response_name: str | None = Field("", alias="responseName")
    runtime_column_propagation: int | None = Field(1, alias="runtime_column_propagation")
    show_coll_type: int | None = Field(0, alias="showCollType")
    show_part_type: int | None = Field(1, alias="showPartType")
    show_sort_options: int | None = Field(0, alias="showSortOptions")
    sort_instructions: str | None = Field("", alias="sortInstructions")
    sort_instructions_text: str | None = Field("", alias="sortInstructionsText")
    ssl_certificate: str | None = Field("", alias="ssl_certificate")
    stage_description: list | None = Field("", alias="stageDescription")
    truststore_type: WEB_SERVICE.TruststoreType | None = Field(
        WEB_SERVICE.TruststoreType.JKS, alias="truststore_type"
    )
    user_classpath: str | None = Field("", alias="user_classpath")
    wsdl_document_uri: str | None = Field("", alias="wsdl_document_uri")
    wsdl_document_xml: str | None = Field("", alias="wsdl_document_xml")
    wsdl_input_message_namespace: str | None = Field("", alias="wsdl_input_message_namespace")
    wsdl_operation_name: str | None = Field("", alias="wsdl_operation_name")
    wsdl_operation_style: str | None = Field("", alias="wsdl_operation_style")
    wsdl_port_address: str | None = Field("", alias="wsdl_port_address")
    wsdl_port_name: str | None = Field("", alias="wsdl_port_name")
    wsdl_service_name: str | None = Field("", alias="wsdl_service_name")
    wsdl_soap_action: str | None = Field("", alias="wsdl_soap_action")
    xml_input_column: str | None = Field("", alias="xml_input_column")
    xml_input_header_column: str | None = Field("", alias="xml_input_header_column")
    xml_output_column: str | None = Field("", alias="xml_output_column")
    xml_output_header_column: str | None = Field("", alias="xml_output_header_column")

    def validate_parameters(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        include.add("preserve") if (self.output_count and self.output_count > 0) else exclude.add("preserve")
        (
            include.add("is_log_reject_reason_disabled")
            if (((self.input_count and self.input_count > 0)) and (self.output_count and self.output_count > 0))
            else exclude.add("is_log_reject_reason_disabled")
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
        return include, exclude

    def get_input_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "inherit_from_stage",
            "input_message_table_id",
            "is_input_header_xml_column",
            "is_input_xml_column",
            "link_minimised",
            "log_response",
            "part_coll",
            "runtime_column_propagation",
            "xml_input_column",
            "xml_input_header_column",
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
        props = {
            "input_description",
            "input_name",
            "input_request",
            "is_output_header_xml_column",
            "is_output_xml_column",
            "is_pass_through_disabled",
            "is_reject_column",
            "is_reject_link",
            "output_message_table_id",
            "output_reject_column",
            "request_mapping",
            "xml_output_column",
            "xml_output_header_column",
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
        return {"min": 0, "max": 2}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "allow_column_mapping",
            "authentication_password",
            "authentication_user_name",
            "auto_column_propagation",
            "buf_free_run",
            "buf_free_run_ronly",
            "buf_mode",
            "buf_mode_ronly",
            "certificate_passwd",
            "coll_type",
            "combinability",
            "current_output_link_type",
            "disk_write_inc",
            "disk_write_inc_ronly",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "error_handling",
            "execmode",
            "field_delimiter",
            "flow_dirty",
            "has_reference_output",
            "hide",
            "inherit_from_stage",
            "input_col",
            "input_count",
            "input_description",
            "input_link_description",
            "input_message_table_id",
            "input_name",
            "input_namespace_name",
            "input_namespace_value",
            "input_request",
            "inputcol_properties",
            "is_authentication_required",
            "is_automatic_trust",
            "is_certificate_required",
            "is_input_header_xml_column",
            "is_input_xml_column",
            "is_log_reject_reason_disabled",
            "is_output_header_xml_column",
            "is_output_xml_column",
            "is_pass_through_disabled",
            "is_proxy_required",
            "is_reject_column",
            "is_reject_link",
            "jvm_options",
            "key_col_select",
            "key_cols_coll",
            "key_cols_coll_ordered",
            "key_cols_coll_robin",
            "key_cols_none",
            "key_cols_part",
            "keystore_file",
            "link_minimised",
            "log_response",
            "max_mem_buf_size",
            "max_mem_buf_size_ronly",
            "operation_timeout",
            "output_acp_should_hide",
            "output_col",
            "output_count",
            "output_link_description",
            "output_message_table_id",
            "output_namespace_name",
            "output_namespace_value",
            "output_reject_column",
            "outputcol_properties",
            "part_client_dbname",
            "part_client_instance",
            "part_coll",
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
            "proxy_host_name",
            "proxy_password",
            "proxy_port_number",
            "proxy_user_name",
            "queue_upper_size",
            "queue_upper_size_ronly",
            "reject_link_index",
            "reject_link_name",
            "request_mapping",
            "request_name",
            "response_name",
            "runtime_column_propagation",
            "show_coll_type",
            "show_part_type",
            "show_sort_options",
            "sort_instructions",
            "sort_instructions_text",
            "ssl_certificate",
            "stage_description",
            "truststore_type",
            "user_classpath",
            "wsdl_document_uri",
            "wsdl_document_xml",
            "wsdl_input_message_namespace",
            "wsdl_operation_name",
            "wsdl_operation_style",
            "wsdl_port_address",
            "wsdl_port_name",
            "wsdl_service_name",
            "wsdl_soap_action",
            "xml_input_column",
            "xml_input_header_column",
            "xml_output_column",
            "xml_output_header_column",
        }
        required = {
            "current_output_link_type",
            "enable_flow_acp_control",
            "enable_schemaless_design",
            "output_acp_should_hide",
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
