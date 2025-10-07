from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class ExasolConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "8136a39f-465f-43a3-a606-ce238fb19116"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    database: str | None = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    fingerprint: str | None = Field(None, alias="fingerprint")
    gateway_url: str | None = Field(None, alias="gateway_url")
    hostname_or_ip_address: str = Field(None, alias="host")
    jar_uris: str = Field(None, alias="jar_uris")
    password: str = Field(None, alias="password")
    port: int = Field(None, alias="port")
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
        include.add("password") if (not self.defer_credentials) else exclude.add("password")
        (
            include.add("satellite_connector_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_location_id))
            else exclude.add("satellite_connector_id")
        )
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
        (
            include.add("satellite_client_certificate")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_client_certificate")
        )
        (
            include.add("secure_gateway_service_url")
            if (self.hidden_dummy_property1)
            else exclude.add("secure_gateway_service_url")
        )
        include.add("sl_host_original") if (self.hidden_dummy_property1) else exclude.add("sl_host_original")
        (
            include.add("satellite_client_private_key")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_client_private_key")
        )
        (
            include.add("satellite_connector_id")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_connector_id")
        )
        include.add("sg_host_original") if (self.hidden_dummy_property1) else exclude.add("sg_host_original")
        (
            include.add("secure_gateway_as_http_proxy")
            if (self.hidden_dummy_property1)
            else exclude.add("secure_gateway_as_http_proxy")
        )
        include.add("secure_gateway_id") if (self.hidden_dummy_property1) else exclude.add("secure_gateway_id")
        (
            include.add("secure_gateway_security_token")
            if (self.hidden_dummy_property1)
            else exclude.add("secure_gateway_security_token")
        )
        include.add("satellite_service_url") if (self.hidden_dummy_property1) else exclude.add("satellite_service_url")
        (
            include.add("satellite_endpoint_display_name")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_endpoint_display_name")
        )
        (
            include.add("satellite_endpoint_host")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_endpoint_host")
        )
        (
            include.add("satellite_endpoint_port")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_endpoint_port")
        )
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")
        (
            include.add("satellite_as_http_proxy")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_as_http_proxy")
        )
        include.add("satellite_location_id") if (self.hidden_dummy_property1) else exclude.add("satellite_location_id")

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
        (
            include.add("satellite_connector_id")
            if (not self.secure_gateway_id) and (not self.satellite_location_id)
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        include.add("password") if not self.defer_credentials else exclude.add("password")
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
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
