from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import ORACLE_DATASTAGE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class ConnectionType(Enum):
    ldap = "ldap"
    seps = "seps"
    tcp = "tcp"
    tcps = "tcps"


class OracleDatastageConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "dd22f798-8c9b-41fa-841e-d66cbdf50722"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    cas_lite_service_authorization_header: str | None = Field(None, alias="cas_lite_auth_header")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    connection_string: str = Field(None, alias="connection_string")
    connection_type: ORACLE_DATASTAGE_CONNECTION.ConnectionType | None = Field(
        ORACLE_DATASTAGE_CONNECTION.ConnectionType.tcp, alias="connection_type"
    )
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    gateway_url: str | None = Field(None, alias="gateway_url")
    alternate_servers: str | None = Field(None, alias="oracle_alternate_servers")
    hostname: str = Field(None, alias="oracle_db_host")
    port: str = Field(None, alias="oracle_db_port")
    servicename: str = Field(None, alias="oracle_service_name")
    password: str | None = Field(None, alias="password")
    rac_server_name: str | None = Field(None, alias="rac_name")
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
    use_connection_string: bool | None = Field(False, alias="use_connection_string")
    username: str | None = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    oracle_client_version: str | None = Field(None, alias="version")
    xa_database_name: str | None = Field(None, alias="xao_db_name")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("alternate_servers")
            if (
                ((not self.use_connection_string))
                and (
                    (
                        (
                            (
                                self.connection_type
                                and (
                                    (hasattr(self.connection_type, "value") and self.connection_type.value == "tcp")
                                    or (self.connection_type == "tcp")
                                )
                            )
                        )
                        or (
                            (
                                self.connection_type
                                and (
                                    (hasattr(self.connection_type, "value") and self.connection_type.value == "tcps")
                                    or (self.connection_type == "tcps")
                                )
                            )
                        )
                    )
                    or (
                        self.connection_type
                        and (
                            (hasattr(self.connection_type, "value") and not self.connection_type.value)
                            or (not self.connection_type)
                        )
                    )
                )
            )
            else exclude.add("alternate_servers")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    ((self.use_connection_string))
                    or (
                        ((not self.use_connection_string))
                        and (
                            (
                                (
                                    (
                                        self.connection_type
                                        and (
                                            (
                                                hasattr(self.connection_type, "value")
                                                and self.connection_type.value == "ldap"
                                            )
                                            or (self.connection_type == "ldap")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.connection_type
                                        and (
                                            (
                                                hasattr(self.connection_type, "value")
                                                and self.connection_type.value == "tcp"
                                            )
                                            or (self.connection_type == "tcp")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.connection_type
                                        and (
                                            (
                                                hasattr(self.connection_type, "value")
                                                and self.connection_type.value == "tcps"
                                            )
                                            or (self.connection_type == "tcps")
                                        )
                                    )
                                )
                            )
                            or (
                                self.connection_type
                                and (
                                    (hasattr(self.connection_type, "value") and not self.connection_type.value)
                                    or (not self.connection_type)
                                )
                            )
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        include.add("connection_type") if (not self.use_connection_string) else exclude.add("connection_type")
        include.add("servicename") if (not self.use_connection_string) else exclude.add("servicename")
        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("port")
            if (
                ((not self.use_connection_string))
                and (
                    (
                        (
                            (
                                self.connection_type
                                and (
                                    (hasattr(self.connection_type, "value") and self.connection_type.value == "tcp")
                                    or (self.connection_type == "tcp")
                                )
                            )
                        )
                        or (
                            (
                                self.connection_type
                                and (
                                    (hasattr(self.connection_type, "value") and self.connection_type.value == "tcps")
                                    or (self.connection_type == "tcps")
                                )
                            )
                        )
                    )
                    or (
                        self.connection_type
                        and (
                            (hasattr(self.connection_type, "value") and not self.connection_type.value)
                            or (not self.connection_type)
                        )
                    )
                )
            )
            else exclude.add("port")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        (
            include.add("hostname")
            if (
                ((not self.use_connection_string))
                and (
                    (
                        (
                            (
                                self.connection_type
                                and (
                                    (hasattr(self.connection_type, "value") and self.connection_type.value == "tcp")
                                    or (self.connection_type == "tcp")
                                )
                            )
                        )
                        or (
                            (
                                self.connection_type
                                and (
                                    (hasattr(self.connection_type, "value") and self.connection_type.value == "tcps")
                                    or (self.connection_type == "tcps")
                                )
                            )
                        )
                    )
                    or (
                        self.connection_type
                        and (
                            (hasattr(self.connection_type, "value") and not self.connection_type.value)
                            or (not self.connection_type)
                        )
                    )
                )
            )
            else exclude.add("hostname")
        )
        include.add("connection_string") if (self.use_connection_string) else exclude.add("connection_string")
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    ((self.use_connection_string))
                    or (
                        ((not self.use_connection_string))
                        and (
                            (
                                (
                                    (
                                        self.connection_type
                                        and (
                                            (
                                                hasattr(self.connection_type, "value")
                                                and self.connection_type.value == "ldap"
                                            )
                                            or (self.connection_type == "ldap")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.connection_type
                                        and (
                                            (
                                                hasattr(self.connection_type, "value")
                                                and self.connection_type.value == "tcp"
                                            )
                                            or (self.connection_type == "tcp")
                                        )
                                    )
                                )
                                or (
                                    (
                                        self.connection_type
                                        and (
                                            (
                                                hasattr(self.connection_type, "value")
                                                and self.connection_type.value == "tcps"
                                            )
                                            or (self.connection_type == "tcps")
                                        )
                                    )
                                )
                            )
                            or (
                                self.connection_type
                                and (
                                    (hasattr(self.connection_type, "value") and not self.connection_type.value)
                                    or (not self.connection_type)
                                )
                            )
                        )
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
        include.add("alternate_servers") if (self.hidden_dummy_property1) else exclude.add("alternate_servers")
        include.add("connection_type") if (self.hidden_dummy_property1) else exclude.add("connection_type")
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")

        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("hostname")
            if (self.use_connection_string == "false" or not self.use_connection_string)
            and (
                (
                    self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value
                            and "tcp" in str(self.connection_type.value)
                        )
                        or ("tcp" in str(self.connection_type))
                    )
                    or self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value
                            and "tcps" in str(self.connection_type.value)
                        )
                        or ("tcps" in str(self.connection_type))
                    )
                )
                or (
                    self.connection_type
                    and (
                        (hasattr(self.connection_type, "value") and not self.connection_type.value)
                        or (not self.connection_type)
                    )
                )
            )
            else exclude.add("hostname")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service == "true" or self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        (
            include.add("alternate_servers")
            if (self.use_connection_string == "false" or not self.use_connection_string)
            and (
                (
                    self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value
                            and "tcp" in str(self.connection_type.value)
                        )
                        or ("tcp" in str(self.connection_type))
                    )
                    or self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value
                            and "tcps" in str(self.connection_type.value)
                        )
                        or ("tcps" in str(self.connection_type))
                    )
                )
                or (
                    self.connection_type
                    and (
                        (hasattr(self.connection_type, "value") and not self.connection_type.value)
                        or (not self.connection_type)
                    )
                )
            )
            else exclude.add("alternate_servers")
        )
        (
            include.add("servicename")
            if (self.use_connection_string == "false" or not self.use_connection_string)
            else exclude.add("servicename")
        )
        (
            include.add("connection_string")
            if (self.use_connection_string == "true" or self.use_connection_string)
            else exclude.add("connection_string")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                (self.use_connection_string == "true" or self.use_connection_string)
                or (
                    (self.use_connection_string == "false" or not self.use_connection_string)
                    and (
                        (
                            self.connection_type
                            and (
                                (
                                    hasattr(self.connection_type, "value")
                                    and self.connection_type.value
                                    and "ldap" in str(self.connection_type.value)
                                )
                                or ("ldap" in str(self.connection_type))
                            )
                            or self.connection_type
                            and (
                                (
                                    hasattr(self.connection_type, "value")
                                    and self.connection_type.value
                                    and "tcp" in str(self.connection_type.value)
                                )
                                or ("tcp" in str(self.connection_type))
                            )
                            or self.connection_type
                            and (
                                (
                                    hasattr(self.connection_type, "value")
                                    and self.connection_type.value
                                    and "tcps" in str(self.connection_type.value)
                                )
                                or ("tcps" in str(self.connection_type))
                            )
                        )
                        or (
                            self.connection_type
                            and (
                                (hasattr(self.connection_type, "value") and not self.connection_type.value)
                                or (not self.connection_type)
                            )
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("connection_type")
            if (self.use_connection_string == "false" or not self.use_connection_string)
            else exclude.add("connection_type")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                (self.use_connection_string == "true" or self.use_connection_string)
                or (
                    (self.use_connection_string == "false" or not self.use_connection_string)
                    and (
                        (
                            self.connection_type
                            and (
                                (
                                    hasattr(self.connection_type, "value")
                                    and self.connection_type.value
                                    and "ldap" in str(self.connection_type.value)
                                )
                                or ("ldap" in str(self.connection_type))
                            )
                            or self.connection_type
                            and (
                                (
                                    hasattr(self.connection_type, "value")
                                    and self.connection_type.value
                                    and "tcp" in str(self.connection_type.value)
                                )
                                or ("tcp" in str(self.connection_type))
                            )
                            or self.connection_type
                            and (
                                (
                                    hasattr(self.connection_type, "value")
                                    and self.connection_type.value
                                    and "tcps" in str(self.connection_type.value)
                                )
                                or ("tcps" in str(self.connection_type))
                            )
                        )
                        or (
                            self.connection_type
                            and (
                                (hasattr(self.connection_type, "value") and not self.connection_type.value)
                                or (not self.connection_type)
                            )
                        )
                    )
                )
            )
            else exclude.add("username")
        )
        (
            include.add("port")
            if (self.use_connection_string == "false" or not self.use_connection_string)
            and (
                (
                    self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value
                            and "tcp" in str(self.connection_type.value)
                        )
                        or ("tcp" in str(self.connection_type))
                    )
                    or self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value
                            and "tcps" in str(self.connection_type.value)
                        )
                        or ("tcps" in str(self.connection_type))
                    )
                )
                or (
                    self.connection_type
                    and (
                        (hasattr(self.connection_type, "value") and not self.connection_type.value)
                        or (not self.connection_type)
                    )
                )
            )
            else exclude.add("port")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
