from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import AMAZONRDS_ORACLE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class ConnectionMode(Enum):
    sid = "sid"
    service_name = "service_name"


class FailoverMode(Enum):
    connect = "connect"
    extended = "extended"
    select = "select"


class MetadataDiscovery(Enum):
    no_remarks = "no_remarks"
    no_remarks_or_synonyms = "no_remarks_or_synonyms"
    no_synonyms = "no_synonyms"
    remarks_and_synonyms = "remarks_and_synonyms"


class NumberType(Enum):
    double = "double"
    varchar = "varchar"


class AmazonrdsOracleConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "8b8fcd6d-8f95-49c7-8195-c72c95c9a84b"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    alternate_servers: str | None = Field(None, alias="alternate_servers")
    discover_data_assets: bool | None = Field(None, alias="auto_discovery")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    conn_impersonate_user: str | None = Field(None, alias="conn_impersonate_user")
    conn_impersonate_user_password: str | None = Field(None, alias="conn_impersonate_user_password")
    connection_mode: AMAZONRDS_ORACLE_CONNECTION.ConnectionMode | None = Field(None, alias="connection_mode")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    failover_mode: AMAZONRDS_ORACLE_CONNECTION.FailoverMode | None = Field(None, alias="failover_mode")
    hostname_or_ip_address: str = Field(None, alias="host")
    load_balancing: bool | None = Field(None, alias="load_balancing")
    metadata_discovery: AMAZONRDS_ORACLE_CONNECTION.MetadataDiscovery | None = Field(
        AMAZONRDS_ORACLE_CONNECTION.MetadataDiscovery.no_remarks, alias="metadata_discovery"
    )
    number_type: AMAZONRDS_ORACLE_CONNECTION.NumberType | None = Field(None, alias="number_type")
    password: str = Field(None, alias="password")
    port: int = Field(None, alias="port")
    proxy: bool | None = Field(False, alias="proxy")
    proxy_host: str = Field(None, alias="proxy_host")
    proxy_password: str | None = Field(None, alias="proxy_password")
    proxy_port: int = Field(None, alias="proxy_port")
    proxy_username: str | None = Field(None, alias="proxy_user")
    retry_limit: int | None = Field(2, alias="retry_limit")
    service_name: str = Field(None, alias="service_name")
    database_sid: str = Field(None, alias="sid")
    port_is_ssl_enabled: bool | None = Field(False, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    ssl_certificate_hostname: str | None = Field(None, alias="ssl_certificate_host")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    additional_properties: str | None = Field(None, alias="properties")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("ssl_certificate")
            if ((((not self.ssl_certificate_file))) and (self.port_is_ssl_enabled))
            else exclude.add("ssl_certificate")
        )
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        include.add("password") if (not self.defer_credentials) else exclude.add("password")
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        (
            include.add("service_name")
            if (
                ((not self.database_sid))
                and (
                    self.connection_mode
                    and (
                        (hasattr(self.connection_mode, "value") and self.connection_mode.value == "service_name")
                        or (self.connection_mode == "service_name")
                    )
                )
            )
            else exclude.add("service_name")
        )
        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
        (
            include.add("ssl_certificate_hostname")
            if (self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_hostname")
        )
        (
            include.add("validate_ssl_certificate")
            if (self.port_is_ssl_enabled)
            else exclude.add("validate_ssl_certificate")
        )
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        include.add("username") if (not self.defer_credentials) else exclude.add("username")
        (
            include.add("database_sid")
            if (
                ((not self.service_name))
                and (
                    self.connection_mode
                    and (
                        (hasattr(self.connection_mode, "value") and self.connection_mode.value == "sid")
                        or (self.connection_mode == "sid")
                    )
                )
            )
            else exclude.add("database_sid")
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
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        (
            include.add("validate_ssl_certificate")
            if (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("validate_ssl_certificate")
        )
        (
            include.add("ssl_certificate_hostname")
            if (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_hostname")
        )
        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
        (
            include.add("database_sid")
            if (not self.service_name)
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "sid" in str(self.connection_mode.value)
                    )
                    or ("sid" in str(self.connection_mode))
                )
            )
            else exclude.add("database_sid")
        )
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        (
            include.add("service_name")
            if (not self.database_sid)
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "service_name" in str(self.connection_mode.value)
                    )
                    or ("service_name" in str(self.connection_mode))
                )
            )
            else exclude.add("service_name")
        )
        include.add("password") if not self.defer_credentials else exclude.add("password")
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        include.add("username") if not self.defer_credentials else exclude.add("username")
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate")
        )
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
