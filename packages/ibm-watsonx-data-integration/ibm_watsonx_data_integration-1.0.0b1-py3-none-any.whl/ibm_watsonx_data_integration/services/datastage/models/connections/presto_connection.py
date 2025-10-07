from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class PrestoConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "11849f0a-54cc-448d-bb8c-d79206636e3d"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    discover_data_assets: bool | None = Field(None, alias="auto_discovery")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    hostname_or_ip_address: str = Field(None, alias="host")
    password: str | None = Field(None, alias="password")
    port: int = Field(None, alias="port")
    port_is_ssl_enabled: bool | None = Field(False, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    use_source_to_source_ssl_certificate: bool | None = Field(False, alias="use_s2s_ssl_certificate")
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
            include.add("use_source_to_source_ssl_certificate")
            if (((self.port_is_ssl_enabled)) and (self.ssl_certificate))
            else exclude.add("use_source_to_source_ssl_certificate")
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
            include.add("use_source_to_source_ssl_certificate")
            if (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled) and (self.ssl_certificate)
            else exclude.add("use_source_to_source_ssl_certificate")
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
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
