from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import SQLSERVER_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class NtlmVersion(Enum):
    default = "default"
    v2 = "v2"


class SqlserverConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "48695e79-6279-474a-b539-342625d3dfc2"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    discover_data_assets: bool | None = Field(None, alias="auto_discovery")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    database: str | None = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    domain: str | None = Field(None, alias="domain")
    hostname_or_ip_address: str = Field(None, alias="host")
    instance_name: str = Field(None, alias="instance_name")
    ntlm_version: SQLSERVER_CONNECTION.NtlmVersion | None = Field(None, alias="ntlm_version")
    password: str = Field(None, alias="password")
    port: int = Field(None, alias="port")
    proxy: bool | None = Field(False, alias="proxy")
    proxy_host: str = Field(None, alias="proxy_host")
    proxy_password: str | None = Field(None, alias="proxy_password")
    proxy_port: int = Field(None, alias="proxy_port")
    proxy_username: str | None = Field(None, alias="proxy_user")
    query_timeout: int | None = Field(None, alias="query_timeout")
    secure_gateway_id: str | None = Field(None, alias="sg_gateway_id")
    sg_host_original: str | None = Field(None, alias="sg_host_original")
    secure_gateway_as_http_proxy: bool | None = Field(None, alias="sg_http_proxy")
    secure_gateway_security_token: str | None = Field(None, alias="sg_security_token")
    secure_gateway_service_url: str | None = Field(None, alias="sg_service_url")
    satellite_client_certificate: str | None = Field(None, alias="sl_client_cert")
    satellite_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    satellite_connector_id: str | None = Field(None, alias="sl_connector_id")
    satellite_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    satellite_endpoint_display_name: str | None = Field(None, alias="sl_endpoint_name")
    satellite_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    sl_host_original: str | None = Field(None, alias="sl_host_original")
    satellite_as_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    satellite_location_id: str | None = Field(None, alias="sl_location_id")
    satellite_service_url: str | None = Field(None, alias="sl_service_url")
    port_is_ssl_enabled: bool | None = Field(False, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    ssl_certificate_hostname: str | None = Field(None, alias="ssl_certificate_host")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    use_active_directory: bool | None = Field(None, alias="use_active_directory")
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
        include.add("instance_name") if (not self.port) else exclude.add("instance_name")
        (
            include.add("satellite_connector_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_location_id))
            else exclude.add("satellite_connector_id")
        )
        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
        (
            include.add("ssl_certificate_hostname")
            if (self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_hostname")
        )
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        include.add("password") if (not self.defer_credentials) else exclude.add("password")
        include.add("port") if (not self.instance_name) else exclude.add("port")
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        include.add("domain") if (self.use_active_directory) else exclude.add("domain")
        include.add("ntlm_version") if (self.use_active_directory) else exclude.add("ntlm_version")
        (
            include.add("validate_ssl_certificate")
            if (self.port_is_ssl_enabled)
            else exclude.add("validate_ssl_certificate")
        )
        (
            include.add("satellite_location_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_connector_id))
            else exclude.add("satellite_location_id")
        )
        include.add("username") if (not self.defer_credentials) else exclude.add("username")
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
            include.add("satellite_connector_id")
            if (not self.secure_gateway_id) and (not self.satellite_location_id)
            else exclude.add("satellite_connector_id")
        )
        include.add("ntlm_version") if (self.use_active_directory) else exclude.add("ntlm_version")
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        include.add("password") if not self.defer_credentials else exclude.add("password")
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        include.add("username") if not self.defer_credentials else exclude.add("username")
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate")
        )
        (
            include.add("satellite_location_id")
            if (not self.secure_gateway_id) and (not self.satellite_connector_id)
            else exclude.add("satellite_location_id")
        )
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
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        include.add("domain") if (self.use_active_directory) else exclude.add("domain")
        include.add("instance_name") if (not self.port) else exclude.add("instance_name")
        include.add("port") if (not self.instance_name) else exclude.add("port")
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
