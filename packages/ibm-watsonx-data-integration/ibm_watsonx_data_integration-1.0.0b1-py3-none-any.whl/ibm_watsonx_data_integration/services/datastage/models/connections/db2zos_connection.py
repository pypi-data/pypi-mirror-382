from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class Db2zosConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "c8d3eab2-25f6-4a90-8e10-0b4226693c45"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    application_name: str | None = Field(None, alias="application_name")
    avoid_timestamp_conversion: bool | None = Field(None, alias="avoid_timestamp_conversion")
    client_accounting_information: str | None = Field(None, alias="client_accounting_information")
    client_hostname: str | None = Field(None, alias="client_hostname")
    client_user: str | None = Field(None, alias="client_user")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    collection_id: str | None = Field(None, alias="collection")
    command_timeout: int | None = Field(600, alias="command_timeout")
    location: str = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    gateway_url: str | None = Field(None, alias="gateway_url")
    hostname_or_ip_address: str = Field(None, alias="host")
    jdbc_driver_files: str | None = Field(None, alias="jar_uris")
    max_transport_objects: int | None = Field(None, alias="max_transport_objects")
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
        include.add("gateway_url") if (self.hidden_dummy_property1) else exclude.add("gateway_url")
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        include.add("jdbc_driver_files") if (self.hidden_dummy_property1) else exclude.add("jdbc_driver_files")
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

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
