from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import ODBC_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthenticationMethod(Enum):
    oauth2 = "oauth2"
    serviceaccount = "serviceaccount"


class DsnType(Enum):
    Cassandra = "Cassandra"
    Hive = "Hive"
    Googlebigquery = "Googlebigquery"
    GreenPlum = "GreenPlum"
    DB2 = "DB2"
    DB2zOS = "DB2zOS"
    DB2AS400 = "DB2AS400"
    Informix = "Informix"
    Netezza = "Netezza"
    Impala = "Impala"
    MicrosoftSQLServer = "MicrosoftSQLServer"
    MongoDB = "MongoDB"
    MySQL = "MySQL"
    Oracle = "Oracle"
    PostgreSQL = "PostgreSQL"
    SybaseASE = "SybaseASE"
    SybaseIQ = "SybaseIQ"
    Teradata = "Teradata"
    Text = "Text"
    use_dsn_name = "use_dsn_name"


class LogOnMech(Enum):
    ldap = "ldap"
    td2 = "td2"


class ServiceAccountKeyInputMethod(Enum):
    keycontent = "keycontent"
    keyfile = "keyfile"


class OdbcConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "0ca92c3d-0e46-3b42-a573-77958d53c9be"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    access_token: str = Field(None, alias="access_token")
    additional_properties: str | None = Field(None, alias="additional_props")
    authentication_method: ODBC_CONNECTION.AuthenticationMethod = Field(
        ODBC_CONNECTION.AuthenticationMethod.oauth2, alias="authentication_method"
    )
    cas_lite_service_authorization_header: str | None = Field(None, alias="cas_lite_auth_header")
    client_id: str = Field(None, alias="client_id")
    client_secret: str = Field(None, alias="client_secret")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_nodes: str = Field(None, alias="cluster_nodes")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    database: str = Field(None, alias="database")
    dataset: str = Field(None, alias="dataset_name")
    default_port: int | None = Field(2638, alias="default_port")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    data_source_name: str = Field(None, alias="dsn_name")
    data_source_type: ODBC_CONNECTION.DsnType = Field(ODBC_CONNECTION.DsnType.DB2, alias="dsn_type")
    delimiter: str | None = Field(",", alias="host_port_separator")
    hostname_or_ip_address: str = Field(None, alias="hostname")
    keyspace: str | None = Field(None, alias="keyspace")
    log_on_mech: ODBC_CONNECTION.LogOnMech = Field(ODBC_CONNECTION.LogOnMech.td2, alias="log_on_mech")
    network_address: str = Field(None, alias="network_address")
    password: str | None = Field(None, alias="password")
    port: int = Field(None, alias="port")
    project: str = Field(None, alias="project_name")
    refresh_token: str = Field(None, alias="refresh_token")
    service_account_email: str = Field(None, alias="service_account_email")
    service_account_key_content: str = Field(None, alias="service_account_key_content")
    input_method_for_service_account_key: ODBC_CONNECTION.ServiceAccountKeyInputMethod = Field(
        ODBC_CONNECTION.ServiceAccountKeyInputMethod.keycontent, alias="service_account_key_input_method"
    )
    service_account_private_key_file_path: str | None = Field(None, alias="service_account_private_key")
    service_name: str = Field(None, alias="service_name")
    satellite_client_certificate: str | None = Field(None, alias="sl_client_cert")
    satellite_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    satellite_connector_id: str | None = Field(None, alias="sl_connector_id")
    satellite_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    satellite_endpoint_display_name: str | None = Field(None, alias="sl_endpoint_name")
    satellite_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    original_hostname_of_the_resource: str | None = Field(None, alias="sl_host_original")
    satellite_as_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    satellite_location_id: str | None = Field(None, alias="sl_location_id")
    satellite_service_url: str | None = Field(None, alias="sl_service_url")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    username: str | None = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("log_on_mech")
            if (
                self.data_source_type
                and (
                    (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Teradata")
                    or (self.data_source_type == "Teradata")
                )
            )
            else exclude.add("log_on_mech")
        )
        (
            include.add("default_port")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseASE")
                            or (self.data_source_type == "SybaseASE")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseIQ")
                        or (self.data_source_type == "SybaseIQ")
                    )
                )
            )
            else exclude.add("default_port")
        )
        (
            include.add("project")
            if (
                self.data_source_type
                and (
                    (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Googlebigquery")
                    or (self.data_source_type == "Googlebigquery")
                )
            )
            else exclude.add("project")
        )
        (
            include.add("data_source_name")
            if (
                self.data_source_type
                and (
                    (hasattr(self.data_source_type, "value") and self.data_source_type.value == "use_dsn_name")
                    or (self.data_source_type == "use_dsn_name")
                )
            )
            else exclude.add("data_source_name")
        )
        (
            include.add("client_id")
            if (
                (
                    (
                        (
                            self.data_source_type
                            and (
                                (
                                    hasattr(self.data_source_type, "value")
                                    and self.data_source_type.value == "Googlebigquery"
                                )
                                or (self.data_source_type == "Googlebigquery")
                            )
                        )
                    )
                )
                and (
                    self.authentication_method
                    and (
                        (hasattr(self.authentication_method, "value") and self.authentication_method.value == "oauth2")
                        or (self.authentication_method == "oauth2")
                    )
                )
            )
            else exclude.add("client_id")
        )
        (
            include.add("authentication_method")
            if (
                self.data_source_type
                and (
                    (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Googlebigquery")
                    or (self.data_source_type == "Googlebigquery")
                )
            )
            else exclude.add("authentication_method")
        )
        (
            include.add("password")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Cassandra")
                            or (self.data_source_type == "Cassandra")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2")
                        or (self.data_source_type == "DB2")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2AS400")
                        or (self.data_source_type == "DB2AS400")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2zOS")
                        or (self.data_source_type == "DB2zOS")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "GreenPlum")
                        or (self.data_source_type == "GreenPlum")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Hive")
                        or (self.data_source_type == "Hive")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Impala")
                        or (self.data_source_type == "Impala")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Informix")
                        or (self.data_source_type == "Informix")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (
                            hasattr(self.data_source_type, "value")
                            and self.data_source_type.value == "MicrosoftSQLServer"
                        )
                        or (self.data_source_type == "MicrosoftSQLServer")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MongoDB")
                        or (self.data_source_type == "MongoDB")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MySQL")
                        or (self.data_source_type == "MySQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Netezza")
                        or (self.data_source_type == "Netezza")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Oracle")
                        or (self.data_source_type == "Oracle")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "PostgreSQL")
                        or (self.data_source_type == "PostgreSQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseASE")
                        or (self.data_source_type == "SybaseASE")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseIQ")
                        or (self.data_source_type == "SybaseIQ")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Teradata")
                        or (self.data_source_type == "Teradata")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "use_dsn_name")
                        or (self.data_source_type == "use_dsn_name")
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("hostname_or_ip_address")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Cassandra")
                            or (self.data_source_type == "Cassandra")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2")
                        or (self.data_source_type == "DB2")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2AS400")
                        or (self.data_source_type == "DB2AS400")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2zOS")
                        or (self.data_source_type == "DB2zOS")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "GreenPlum")
                        or (self.data_source_type == "GreenPlum")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Hive")
                        or (self.data_source_type == "Hive")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Impala")
                        or (self.data_source_type == "Impala")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Informix")
                        or (self.data_source_type == "Informix")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (
                            hasattr(self.data_source_type, "value")
                            and self.data_source_type.value == "MicrosoftSQLServer"
                        )
                        or (self.data_source_type == "MicrosoftSQLServer")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MongoDB")
                        or (self.data_source_type == "MongoDB")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MySQL")
                        or (self.data_source_type == "MySQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Netezza")
                        or (self.data_source_type == "Netezza")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Oracle")
                        or (self.data_source_type == "Oracle")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "PostgreSQL")
                        or (self.data_source_type == "PostgreSQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Teradata")
                        or (self.data_source_type == "Teradata")
                    )
                )
            )
            else exclude.add("hostname_or_ip_address")
        )
        (
            include.add("database")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2")
                            or (self.data_source_type == "DB2")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2AS400")
                        or (self.data_source_type == "DB2AS400")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2zOS")
                        or (self.data_source_type == "DB2zOS")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "GreenPlum")
                        or (self.data_source_type == "GreenPlum")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Hive")
                        or (self.data_source_type == "Hive")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Impala")
                        or (self.data_source_type == "Impala")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Informix")
                        or (self.data_source_type == "Informix")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (
                            hasattr(self.data_source_type, "value")
                            and self.data_source_type.value == "MicrosoftSQLServer"
                        )
                        or (self.data_source_type == "MicrosoftSQLServer")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MongoDB")
                        or (self.data_source_type == "MongoDB")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MySQL")
                        or (self.data_source_type == "MySQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Netezza")
                        or (self.data_source_type == "Netezza")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "PostgreSQL")
                        or (self.data_source_type == "PostgreSQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseASE")
                        or (self.data_source_type == "SybaseASE")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseIQ")
                        or (self.data_source_type == "SybaseIQ")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Teradata")
                        or (self.data_source_type == "Teradata")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Text")
                        or (self.data_source_type == "Text")
                    )
                )
            )
            else exclude.add("database")
        )
        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("client_secret")
            if (
                (
                    (
                        (
                            self.data_source_type
                            and (
                                (
                                    hasattr(self.data_source_type, "value")
                                    and self.data_source_type.value == "Googlebigquery"
                                )
                                or (self.data_source_type == "Googlebigquery")
                            )
                        )
                    )
                )
                and (
                    self.authentication_method
                    and (
                        (hasattr(self.authentication_method, "value") and self.authentication_method.value == "oauth2")
                        or (self.authentication_method == "oauth2")
                    )
                )
            )
            else exclude.add("client_secret")
        )
        (
            include.add("service_name")
            if (
                self.data_source_type
                and (
                    (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Oracle")
                    or (self.data_source_type == "Oracle")
                )
            )
            else exclude.add("service_name")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        (
            include.add("dataset")
            if (
                self.data_source_type
                and (
                    (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Googlebigquery")
                    or (self.data_source_type == "Googlebigquery")
                )
            )
            else exclude.add("dataset")
        )
        (
            include.add("service_account_private_key_file_path")
            if (
                (
                    (
                        (
                            self.data_source_type
                            and (
                                (
                                    hasattr(self.data_source_type, "value")
                                    and self.data_source_type.value == "Googlebigquery"
                                )
                                or (self.data_source_type == "Googlebigquery")
                            )
                        )
                    )
                )
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "serviceaccount"
                        )
                        or (self.authentication_method == "serviceaccount")
                    )
                )
                and (
                    self.input_method_for_service_account_key
                    and (
                        (
                            hasattr(self.input_method_for_service_account_key, "value")
                            and self.input_method_for_service_account_key.value == "keyfile"
                        )
                        or (self.input_method_for_service_account_key == "keyfile")
                    )
                )
            )
            else exclude.add("service_account_private_key_file_path")
        )
        (
            include.add("service_account_key_content")
            if (
                (
                    (
                        (
                            self.data_source_type
                            and (
                                (
                                    hasattr(self.data_source_type, "value")
                                    and self.data_source_type.value == "Googlebigquery"
                                )
                                or (self.data_source_type == "Googlebigquery")
                            )
                        )
                    )
                )
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "serviceaccount"
                        )
                        or (self.authentication_method == "serviceaccount")
                    )
                )
                and (
                    self.input_method_for_service_account_key
                    and (
                        (
                            hasattr(self.input_method_for_service_account_key, "value")
                            and self.input_method_for_service_account_key.value == "keycontent"
                        )
                        or (self.input_method_for_service_account_key == "keycontent")
                    )
                )
            )
            else exclude.add("service_account_key_content")
        )
        (
            include.add("input_method_for_service_account_key")
            if (
                (
                    (
                        (
                            self.data_source_type
                            and (
                                (
                                    hasattr(self.data_source_type, "value")
                                    and self.data_source_type.value == "Googlebigquery"
                                )
                                or (self.data_source_type == "Googlebigquery")
                            )
                        )
                    )
                )
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "serviceaccount"
                        )
                        or (self.authentication_method == "serviceaccount")
                    )
                )
            )
            else exclude.add("input_method_for_service_account_key")
        )
        (
            include.add("access_token")
            if (
                (
                    (
                        (
                            self.data_source_type
                            and (
                                (
                                    hasattr(self.data_source_type, "value")
                                    and self.data_source_type.value == "Googlebigquery"
                                )
                                or (self.data_source_type == "Googlebigquery")
                            )
                        )
                    )
                )
                and (
                    self.authentication_method
                    and (
                        (hasattr(self.authentication_method, "value") and self.authentication_method.value == "oauth2")
                        or (self.authentication_method == "oauth2")
                    )
                )
            )
            else exclude.add("access_token")
        )
        (
            include.add("refresh_token")
            if (
                (
                    (
                        (
                            self.data_source_type
                            and (
                                (
                                    hasattr(self.data_source_type, "value")
                                    and self.data_source_type.value == "Googlebigquery"
                                )
                                or (self.data_source_type == "Googlebigquery")
                            )
                        )
                    )
                )
                and (
                    self.authentication_method
                    and (
                        (hasattr(self.authentication_method, "value") and self.authentication_method.value == "oauth2")
                        or (self.authentication_method == "oauth2")
                    )
                )
            )
            else exclude.add("refresh_token")
        )
        (
            include.add("keyspace")
            if (
                self.data_source_type
                and (
                    (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Cassandra")
                    or (self.data_source_type == "Cassandra")
                )
            )
            else exclude.add("keyspace")
        )
        (
            include.add("cluster_nodes")
            if (
                self.data_source_type
                and (
                    (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Cassandra")
                    or (self.data_source_type == "Cassandra")
                )
            )
            else exclude.add("cluster_nodes")
        )
        (
            include.add("delimiter")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseASE")
                            or (self.data_source_type == "SybaseASE")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseIQ")
                        or (self.data_source_type == "SybaseIQ")
                    )
                )
            )
            else exclude.add("delimiter")
        )
        (
            include.add("port")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Cassandra")
                            or (self.data_source_type == "Cassandra")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2")
                        or (self.data_source_type == "DB2")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2AS400")
                        or (self.data_source_type == "DB2AS400")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2zOS")
                        or (self.data_source_type == "DB2zOS")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "GreenPlum")
                        or (self.data_source_type == "GreenPlum")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Hive")
                        or (self.data_source_type == "Hive")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Impala")
                        or (self.data_source_type == "Impala")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Informix")
                        or (self.data_source_type == "Informix")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (
                            hasattr(self.data_source_type, "value")
                            and self.data_source_type.value == "MicrosoftSQLServer"
                        )
                        or (self.data_source_type == "MicrosoftSQLServer")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MongoDB")
                        or (self.data_source_type == "MongoDB")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MySQL")
                        or (self.data_source_type == "MySQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Netezza")
                        or (self.data_source_type == "Netezza")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Oracle")
                        or (self.data_source_type == "Oracle")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "PostgreSQL")
                        or (self.data_source_type == "PostgreSQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Teradata")
                        or (self.data_source_type == "Teradata")
                    )
                )
            )
            else exclude.add("port")
        )
        (
            include.add("network_address")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseASE")
                            or (self.data_source_type == "SybaseASE")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseIQ")
                        or (self.data_source_type == "SybaseIQ")
                    )
                )
            )
            else exclude.add("network_address")
        )
        (
            include.add("service_account_email")
            if (
                (
                    (
                        (
                            self.data_source_type
                            and (
                                (
                                    hasattr(self.data_source_type, "value")
                                    and self.data_source_type.value == "Googlebigquery"
                                )
                                or (self.data_source_type == "Googlebigquery")
                            )
                        )
                    )
                )
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "serviceaccount"
                        )
                        or (self.authentication_method == "serviceaccount")
                    )
                )
            )
            else exclude.add("service_account_email")
        )
        (
            include.add("username")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Cassandra")
                            or (self.data_source_type == "Cassandra")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2")
                        or (self.data_source_type == "DB2")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2AS400")
                        or (self.data_source_type == "DB2AS400")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2zOS")
                        or (self.data_source_type == "DB2zOS")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "GreenPlum")
                        or (self.data_source_type == "GreenPlum")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Hive")
                        or (self.data_source_type == "Hive")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Impala")
                        or (self.data_source_type == "Impala")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Informix")
                        or (self.data_source_type == "Informix")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (
                            hasattr(self.data_source_type, "value")
                            and self.data_source_type.value == "MicrosoftSQLServer"
                        )
                        or (self.data_source_type == "MicrosoftSQLServer")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MongoDB")
                        or (self.data_source_type == "MongoDB")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MySQL")
                        or (self.data_source_type == "MySQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Netezza")
                        or (self.data_source_type == "Netezza")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Oracle")
                        or (self.data_source_type == "Oracle")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "PostgreSQL")
                        or (self.data_source_type == "PostgreSQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseASE")
                        or (self.data_source_type == "SybaseASE")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseIQ")
                        or (self.data_source_type == "SybaseIQ")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Teradata")
                        or (self.data_source_type == "Teradata")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "use_dsn_name")
                        or (self.data_source_type == "use_dsn_name")
                    )
                )
            )
            else exclude.add("username")
        )
        (
            include.add("database")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2")
                            or (self.data_source_type == "DB2")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2AS400")
                        or (self.data_source_type == "DB2AS400")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2zOS")
                        or (self.data_source_type == "DB2zOS")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "GreenPlum")
                        or (self.data_source_type == "GreenPlum")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Hive")
                        or (self.data_source_type == "Hive")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Impala")
                        or (self.data_source_type == "Impala")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Informix")
                        or (self.data_source_type == "Informix")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (
                            hasattr(self.data_source_type, "value")
                            and self.data_source_type.value == "MicrosoftSQLServer"
                        )
                        or (self.data_source_type == "MicrosoftSQLServer")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MongoDB")
                        or (self.data_source_type == "MongoDB")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MySQL")
                        or (self.data_source_type == "MySQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Netezza")
                        or (self.data_source_type == "Netezza")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "PostgreSQL")
                        or (self.data_source_type == "PostgreSQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseASE")
                        or (self.data_source_type == "SybaseASE")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseIQ")
                        or (self.data_source_type == "SybaseIQ")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Text")
                        or (self.data_source_type == "Text")
                    )
                )
            )
            else exclude.add("database")
        )
        (
            include.add("password")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Cassandra")
                            or (self.data_source_type == "Cassandra")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2")
                        or (self.data_source_type == "DB2")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2AS400")
                        or (self.data_source_type == "DB2AS400")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2zOS")
                        or (self.data_source_type == "DB2zOS")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "GreenPlum")
                        or (self.data_source_type == "GreenPlum")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Hive")
                        or (self.data_source_type == "Hive")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Impala")
                        or (self.data_source_type == "Impala")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Informix")
                        or (self.data_source_type == "Informix")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (
                            hasattr(self.data_source_type, "value")
                            and self.data_source_type.value == "MicrosoftSQLServer"
                        )
                        or (self.data_source_type == "MicrosoftSQLServer")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MongoDB")
                        or (self.data_source_type == "MongoDB")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MySQL")
                        or (self.data_source_type == "MySQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Netezza")
                        or (self.data_source_type == "Netezza")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Oracle")
                        or (self.data_source_type == "Oracle")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "PostgreSQL")
                        or (self.data_source_type == "PostgreSQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseASE")
                        or (self.data_source_type == "SybaseASE")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseIQ")
                        or (self.data_source_type == "SybaseIQ")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "use_dsn_name")
                        or (self.data_source_type == "use_dsn_name")
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("hostname_or_ip_address")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Cassandra")
                            or (self.data_source_type == "Cassandra")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2")
                        or (self.data_source_type == "DB2")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2AS400")
                        or (self.data_source_type == "DB2AS400")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2zOS")
                        or (self.data_source_type == "DB2zOS")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "GreenPlum")
                        or (self.data_source_type == "GreenPlum")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Hive")
                        or (self.data_source_type == "Hive")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Impala")
                        or (self.data_source_type == "Impala")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Informix")
                        or (self.data_source_type == "Informix")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (
                            hasattr(self.data_source_type, "value")
                            and self.data_source_type.value == "MicrosoftSQLServer"
                        )
                        or (self.data_source_type == "MicrosoftSQLServer")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MongoDB")
                        or (self.data_source_type == "MongoDB")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MySQL")
                        or (self.data_source_type == "MySQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Netezza")
                        or (self.data_source_type == "Netezza")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Oracle")
                        or (self.data_source_type == "Oracle")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "PostgreSQL")
                        or (self.data_source_type == "PostgreSQL")
                    )
                )
            )
            else exclude.add("hostname_or_ip_address")
        )
        (
            include.add("port")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Cassandra")
                            or (self.data_source_type == "Cassandra")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2")
                        or (self.data_source_type == "DB2")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2AS400")
                        or (self.data_source_type == "DB2AS400")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2zOS")
                        or (self.data_source_type == "DB2zOS")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "GreenPlum")
                        or (self.data_source_type == "GreenPlum")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Hive")
                        or (self.data_source_type == "Hive")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Impala")
                        or (self.data_source_type == "Impala")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Informix")
                        or (self.data_source_type == "Informix")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (
                            hasattr(self.data_source_type, "value")
                            and self.data_source_type.value == "MicrosoftSQLServer"
                        )
                        or (self.data_source_type == "MicrosoftSQLServer")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MongoDB")
                        or (self.data_source_type == "MongoDB")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MySQL")
                        or (self.data_source_type == "MySQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Netezza")
                        or (self.data_source_type == "Netezza")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Oracle")
                        or (self.data_source_type == "Oracle")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "PostgreSQL")
                        or (self.data_source_type == "PostgreSQL")
                    )
                )
            )
            else exclude.add("port")
        )
        (
            include.add("username")
            if (
                (
                    (
                        self.data_source_type
                        and (
                            (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Cassandra")
                            or (self.data_source_type == "Cassandra")
                        )
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2")
                        or (self.data_source_type == "DB2")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2AS400")
                        or (self.data_source_type == "DB2AS400")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "DB2zOS")
                        or (self.data_source_type == "DB2zOS")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "GreenPlum")
                        or (self.data_source_type == "GreenPlum")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Hive")
                        or (self.data_source_type == "Hive")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Impala")
                        or (self.data_source_type == "Impala")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Informix")
                        or (self.data_source_type == "Informix")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (
                            hasattr(self.data_source_type, "value")
                            and self.data_source_type.value == "MicrosoftSQLServer"
                        )
                        or (self.data_source_type == "MicrosoftSQLServer")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MongoDB")
                        or (self.data_source_type == "MongoDB")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "MySQL")
                        or (self.data_source_type == "MySQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Netezza")
                        or (self.data_source_type == "Netezza")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "Oracle")
                        or (self.data_source_type == "Oracle")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "PostgreSQL")
                        or (self.data_source_type == "PostgreSQL")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseASE")
                        or (self.data_source_type == "SybaseASE")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "SybaseIQ")
                        or (self.data_source_type == "SybaseIQ")
                    )
                )
                or (
                    self.data_source_type
                    and (
                        (hasattr(self.data_source_type, "value") and self.data_source_type.value == "use_dsn_name")
                        or (self.data_source_type == "use_dsn_name")
                    )
                )
            )
            else exclude.add("username")
        )
        (
            include.add("hidden_dummy_property2")
            if (self.hidden_dummy_property1)
            else exclude.add("hidden_dummy_property2")
        )
        (
            include.add("hidden_dummy_property1")
            if (self.hidden_dummy_property2)
            else exclude.add("hidden_dummy_property1")
        )
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        (
            include.add("service_account_private_key_file_path")
            if (self.hidden_dummy_property1)
            else exclude.add("service_account_private_key_file_path")
        )

        (
            include.add("keyspace")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Cassandra" in str(self.data_source_type.value)
                    )
                    or ("Cassandra" in str(self.data_source_type))
                )
            )
            else exclude.add("keyspace")
        )
        (
            include.add("authentication_method")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            else exclude.add("authentication_method")
        )
        (
            include.add("service_account_key_content")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "serviceaccount" in str(self.authentication_method.value)
                    )
                    or ("serviceaccount" in str(self.authentication_method))
                )
            )
            and (
                self.input_method_for_service_account_key
                and (
                    (
                        hasattr(self.input_method_for_service_account_key, "value")
                        and self.input_method_for_service_account_key.value
                        and "keycontent" in str(self.input_method_for_service_account_key.value)
                    )
                    or ("keycontent" in str(self.input_method_for_service_account_key))
                )
            )
            else exclude.add("service_account_key_content")
        )
        (
            include.add("network_address")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseASE" in str(self.data_source_type.value)
                    )
                    or ("SybaseASE" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseIQ" in str(self.data_source_type.value)
                    )
                    or ("SybaseIQ" in str(self.data_source_type))
                )
            )
            else exclude.add("network_address")
        )
        (
            include.add("service_account_email")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "serviceaccount" in str(self.authentication_method.value)
                    )
                    or ("serviceaccount" in str(self.authentication_method))
                )
            )
            else exclude.add("service_account_email")
        )
        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service == "true" or self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        (
            include.add("delimiter")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseASE" in str(self.data_source_type.value)
                    )
                    or ("SybaseASE" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseIQ" in str(self.data_source_type.value)
                    )
                    or ("SybaseIQ" in str(self.data_source_type))
                )
            )
            else exclude.add("delimiter")
        )
        (
            include.add("service_account_private_key_file_path")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "serviceaccount" in str(self.authentication_method.value)
                    )
                    or ("serviceaccount" in str(self.authentication_method))
                )
            )
            and (
                self.input_method_for_service_account_key
                and (
                    (
                        hasattr(self.input_method_for_service_account_key, "value")
                        and self.input_method_for_service_account_key.value
                        and "keyfile" in str(self.input_method_for_service_account_key.value)
                    )
                    or ("keyfile" in str(self.input_method_for_service_account_key))
                )
            )
            else exclude.add("service_account_private_key_file_path")
        )
        (
            include.add("input_method_for_service_account_key")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "serviceaccount" in str(self.authentication_method.value)
                    )
                    or ("serviceaccount" in str(self.authentication_method))
                )
            )
            else exclude.add("input_method_for_service_account_key")
        )
        (
            include.add("database")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2" in str(self.data_source_type.value)
                    )
                    or ("DB2" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2AS400" in str(self.data_source_type.value)
                    )
                    or ("DB2AS400" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2zOS" in str(self.data_source_type.value)
                    )
                    or ("DB2zOS" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "GreenPlum" in str(self.data_source_type.value)
                    )
                    or ("GreenPlum" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Hive" in str(self.data_source_type.value)
                    )
                    or ("Hive" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Impala" in str(self.data_source_type.value)
                    )
                    or ("Impala" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Informix" in str(self.data_source_type.value)
                    )
                    or ("Informix" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MicrosoftSQLServer" in str(self.data_source_type.value)
                    )
                    or ("MicrosoftSQLServer" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MongoDB" in str(self.data_source_type.value)
                    )
                    or ("MongoDB" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MySQL" in str(self.data_source_type.value)
                    )
                    or ("MySQL" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Netezza" in str(self.data_source_type.value)
                    )
                    or ("Netezza" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "PostgreSQL" in str(self.data_source_type.value)
                    )
                    or ("PostgreSQL" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseASE" in str(self.data_source_type.value)
                    )
                    or ("SybaseASE" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseIQ" in str(self.data_source_type.value)
                    )
                    or ("SybaseIQ" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Teradata" in str(self.data_source_type.value)
                    )
                    or ("Teradata" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Text" in str(self.data_source_type.value)
                    )
                    or ("Text" in str(self.data_source_type))
                )
            )
            else exclude.add("database")
        )
        (
            include.add("cluster_nodes")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Cassandra" in str(self.data_source_type.value)
                    )
                    or ("Cassandra" in str(self.data_source_type))
                )
            )
            else exclude.add("cluster_nodes")
        )
        (
            include.add("hostname_or_ip_address")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Cassandra" in str(self.data_source_type.value)
                    )
                    or ("Cassandra" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2" in str(self.data_source_type.value)
                    )
                    or ("DB2" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2AS400" in str(self.data_source_type.value)
                    )
                    or ("DB2AS400" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2zOS" in str(self.data_source_type.value)
                    )
                    or ("DB2zOS" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "GreenPlum" in str(self.data_source_type.value)
                    )
                    or ("GreenPlum" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Hive" in str(self.data_source_type.value)
                    )
                    or ("Hive" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Impala" in str(self.data_source_type.value)
                    )
                    or ("Impala" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Informix" in str(self.data_source_type.value)
                    )
                    or ("Informix" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MicrosoftSQLServer" in str(self.data_source_type.value)
                    )
                    or ("MicrosoftSQLServer" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MongoDB" in str(self.data_source_type.value)
                    )
                    or ("MongoDB" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MySQL" in str(self.data_source_type.value)
                    )
                    or ("MySQL" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Netezza" in str(self.data_source_type.value)
                    )
                    or ("Netezza" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Oracle" in str(self.data_source_type.value)
                    )
                    or ("Oracle" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "PostgreSQL" in str(self.data_source_type.value)
                    )
                    or ("PostgreSQL" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Teradata" in str(self.data_source_type.value)
                    )
                    or ("Teradata" in str(self.data_source_type))
                )
            )
            else exclude.add("hostname_or_ip_address")
        )
        (
            include.add("client_id")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "oauth2" in str(self.authentication_method.value)
                    )
                    or ("oauth2" in str(self.authentication_method))
                )
            )
            else exclude.add("client_id")
        )
        (
            include.add("default_port")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseASE" in str(self.data_source_type.value)
                    )
                    or ("SybaseASE" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseIQ" in str(self.data_source_type.value)
                    )
                    or ("SybaseIQ" in str(self.data_source_type))
                )
            )
            else exclude.add("default_port")
        )
        (
            include.add("password")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Cassandra" in str(self.data_source_type.value)
                    )
                    or ("Cassandra" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2" in str(self.data_source_type.value)
                    )
                    or ("DB2" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2AS400" in str(self.data_source_type.value)
                    )
                    or ("DB2AS400" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2zOS" in str(self.data_source_type.value)
                    )
                    or ("DB2zOS" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "GreenPlum" in str(self.data_source_type.value)
                    )
                    or ("GreenPlum" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Hive" in str(self.data_source_type.value)
                    )
                    or ("Hive" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Impala" in str(self.data_source_type.value)
                    )
                    or ("Impala" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Informix" in str(self.data_source_type.value)
                    )
                    or ("Informix" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MicrosoftSQLServer" in str(self.data_source_type.value)
                    )
                    or ("MicrosoftSQLServer" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MongoDB" in str(self.data_source_type.value)
                    )
                    or ("MongoDB" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MySQL" in str(self.data_source_type.value)
                    )
                    or ("MySQL" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Netezza" in str(self.data_source_type.value)
                    )
                    or ("Netezza" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Oracle" in str(self.data_source_type.value)
                    )
                    or ("Oracle" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "PostgreSQL" in str(self.data_source_type.value)
                    )
                    or ("PostgreSQL" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseASE" in str(self.data_source_type.value)
                    )
                    or ("SybaseASE" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseIQ" in str(self.data_source_type.value)
                    )
                    or ("SybaseIQ" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Teradata" in str(self.data_source_type.value)
                    )
                    or ("Teradata" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "use_dsn_name" in str(self.data_source_type.value)
                    )
                    or ("use_dsn_name" in str(self.data_source_type))
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Cassandra" in str(self.data_source_type.value)
                    )
                    or ("Cassandra" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2" in str(self.data_source_type.value)
                    )
                    or ("DB2" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2AS400" in str(self.data_source_type.value)
                    )
                    or ("DB2AS400" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2zOS" in str(self.data_source_type.value)
                    )
                    or ("DB2zOS" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "GreenPlum" in str(self.data_source_type.value)
                    )
                    or ("GreenPlum" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Hive" in str(self.data_source_type.value)
                    )
                    or ("Hive" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Impala" in str(self.data_source_type.value)
                    )
                    or ("Impala" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Informix" in str(self.data_source_type.value)
                    )
                    or ("Informix" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MicrosoftSQLServer" in str(self.data_source_type.value)
                    )
                    or ("MicrosoftSQLServer" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MongoDB" in str(self.data_source_type.value)
                    )
                    or ("MongoDB" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MySQL" in str(self.data_source_type.value)
                    )
                    or ("MySQL" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Netezza" in str(self.data_source_type.value)
                    )
                    or ("Netezza" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Oracle" in str(self.data_source_type.value)
                    )
                    or ("Oracle" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "PostgreSQL" in str(self.data_source_type.value)
                    )
                    or ("PostgreSQL" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseASE" in str(self.data_source_type.value)
                    )
                    or ("SybaseASE" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "SybaseIQ" in str(self.data_source_type.value)
                    )
                    or ("SybaseIQ" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Teradata" in str(self.data_source_type.value)
                    )
                    or ("Teradata" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "use_dsn_name" in str(self.data_source_type.value)
                    )
                    or ("use_dsn_name" in str(self.data_source_type))
                )
            )
            else exclude.add("username")
        )
        (
            include.add("client_secret")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "oauth2" in str(self.authentication_method.value)
                    )
                    or ("oauth2" in str(self.authentication_method))
                )
            )
            else exclude.add("client_secret")
        )
        (
            include.add("project")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            else exclude.add("project")
        )
        (
            include.add("log_on_mech")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Teradata" in str(self.data_source_type.value)
                    )
                    or ("Teradata" in str(self.data_source_type))
                )
            )
            else exclude.add("log_on_mech")
        )
        (
            include.add("service_name")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Oracle" in str(self.data_source_type.value)
                    )
                    or ("Oracle" in str(self.data_source_type))
                )
            )
            else exclude.add("service_name")
        )
        (
            include.add("refresh_token")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "oauth2" in str(self.authentication_method.value)
                    )
                    or ("oauth2" in str(self.authentication_method))
                )
            )
            else exclude.add("refresh_token")
        )
        (
            include.add("access_token")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "oauth2" in str(self.authentication_method.value)
                    )
                    or ("oauth2" in str(self.authentication_method))
                )
            )
            else exclude.add("access_token")
        )
        (
            include.add("dataset")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Googlebigquery" in str(self.data_source_type.value)
                    )
                    or ("Googlebigquery" in str(self.data_source_type))
                )
            )
            else exclude.add("dataset")
        )
        (
            include.add("port")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Cassandra" in str(self.data_source_type.value)
                    )
                    or ("Cassandra" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2" in str(self.data_source_type.value)
                    )
                    or ("DB2" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2AS400" in str(self.data_source_type.value)
                    )
                    or ("DB2AS400" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "DB2zOS" in str(self.data_source_type.value)
                    )
                    or ("DB2zOS" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "GreenPlum" in str(self.data_source_type.value)
                    )
                    or ("GreenPlum" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Hive" in str(self.data_source_type.value)
                    )
                    or ("Hive" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Impala" in str(self.data_source_type.value)
                    )
                    or ("Impala" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Informix" in str(self.data_source_type.value)
                    )
                    or ("Informix" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MicrosoftSQLServer" in str(self.data_source_type.value)
                    )
                    or ("MicrosoftSQLServer" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MongoDB" in str(self.data_source_type.value)
                    )
                    or ("MongoDB" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "MySQL" in str(self.data_source_type.value)
                    )
                    or ("MySQL" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Netezza" in str(self.data_source_type.value)
                    )
                    or ("Netezza" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Oracle" in str(self.data_source_type.value)
                    )
                    or ("Oracle" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "PostgreSQL" in str(self.data_source_type.value)
                    )
                    or ("PostgreSQL" in str(self.data_source_type))
                )
                and self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "Teradata" in str(self.data_source_type.value)
                    )
                    or ("Teradata" in str(self.data_source_type))
                )
            )
            else exclude.add("port")
        )
        (
            include.add("data_source_name")
            if (
                self.data_source_type
                and (
                    (
                        hasattr(self.data_source_type, "value")
                        and self.data_source_type.value
                        and "use_dsn_name" in str(self.data_source_type.value)
                    )
                    or ("use_dsn_name" in str(self.data_source_type))
                )
            )
            else exclude.add("data_source_name")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
