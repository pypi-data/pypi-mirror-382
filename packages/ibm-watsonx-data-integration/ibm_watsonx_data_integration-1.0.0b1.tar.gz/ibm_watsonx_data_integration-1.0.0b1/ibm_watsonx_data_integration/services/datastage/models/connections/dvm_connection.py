from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class DvmConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "dvm"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    auto_discovery: bool | None = Field(None, alias="auto_discovery")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    host: str = Field(None, alias="host")
    password: str = Field(None, alias="password")
    port: int = Field(None, alias="port")
    query_timeout: int | None = Field(None, alias="query_timeout")
    sg_gateway_id: str | None = Field(None, alias="sg_gateway_id")
    sg_host_original: str | None = Field(None, alias="sg_host_original")
    sg_http_proxy: bool | None = Field(None, alias="sg_http_proxy")
    sg_security_token: str | None = Field(None, alias="sg_security_token")
    sg_service_url: str | None = Field(None, alias="sg_service_url")
    sl_client_cert: str | None = Field(None, alias="sl_client_cert")
    sl_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    sl_connector_id: str | None = Field(None, alias="sl_connector_id")
    sl_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    sl_endpoint_name: str | None = Field(None, alias="sl_endpoint_name")
    sl_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    sl_host_original: str | None = Field(None, alias="sl_host_original")
    sl_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    sl_location_id: str | None = Field(None, alias="sl_location_id")
    sl_service_url: str | None = Field(None, alias="sl_service_url")
    ssl: bool | None = Field(False, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    ssl_certificate_hostname: str | None = Field(None, alias="ssl_certificate_host")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    properties: str | None = Field(None, alias="properties")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("ssl_certificate")
            if ((((not self.ssl_certificate_file))) and (self.ssl))
            else exclude.add("ssl_certificate")
        )
        include.add("password") if (not self.defer_credentials) else exclude.add("password")
        (
            include.add("sl_connector_id")
            if (((not self.sg_gateway_id)) and (not self.sl_location_id))
            else exclude.add("sl_connector_id")
        )
        include.add("ssl_certificate_hostname") if (self.ssl) else exclude.add("ssl_certificate_hostname")
        include.add("validate_ssl_certificate") if (self.ssl) else exclude.add("validate_ssl_certificate")
        (
            include.add("sl_location_id")
            if (((not self.sg_gateway_id)) and (not self.sl_connector_id))
            else exclude.add("sl_location_id")
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
        include.add("properties") if (self.hidden_dummy_property1) else exclude.add("properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        (
            include.add("validate_ssl_certificate")
            if (self.ssl == "true" or self.ssl)
            else exclude.add("validate_ssl_certificate")
        )
        (
            include.add("ssl_certificate_hostname")
            if (self.ssl == "true" or self.ssl)
            else exclude.add("ssl_certificate_hostname")
        )
        (
            include.add("sl_connector_id")
            if (not self.sg_gateway_id) and (not self.sl_location_id)
            else exclude.add("sl_connector_id")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.ssl == "true" or self.ssl)
            else exclude.add("ssl_certificate_file")
        )
        include.add("password") if not self.defer_credentials else exclude.add("password")
        include.add("username") if not self.defer_credentials else exclude.add("username")
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.ssl == "true" or self.ssl)
            else exclude.add("ssl_certificate")
        )
        (
            include.add("sl_location_id")
            if (not self.sg_gateway_id) and (not self.sl_connector_id)
            else exclude.add("sl_location_id")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
