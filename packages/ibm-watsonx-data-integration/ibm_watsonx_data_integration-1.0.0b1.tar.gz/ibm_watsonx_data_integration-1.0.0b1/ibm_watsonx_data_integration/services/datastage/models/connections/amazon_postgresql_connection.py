from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class AmazonPostgresqlConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "9493d830-882b-445e-96c7-8e4c635a1a5b"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    auto_discovery: bool | None = Field(None, alias="auto_discovery")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    database: str = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    host: str = Field(None, alias="host")
    login_timeout: int | None = Field(None, alias="login_timeout")
    password: str = Field(None, alias="password")
    port: int = Field(None, alias="port")
    proxy: bool | None = Field(False, alias="proxy")
    proxy_host: str = Field(None, alias="proxy_host")
    proxy_password: str | None = Field(None, alias="proxy_password")
    proxy_port: int = Field(None, alias="proxy_port")
    proxy_user: str | None = Field(None, alias="proxy_user")
    query_timeout: int | None = Field(300, alias="query_timeout")
    retry_limit: int | None = Field(2, alias="retry_limit")
    ssl: bool | None = Field(True, alias="ssl")
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
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        include.add("password") if (not self.defer_credentials) else exclude.add("password")
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        include.add("proxy_user") if (self.proxy) else exclude.add("proxy_user")
        include.add("ssl_certificate_hostname") if (self.ssl) else exclude.add("ssl_certificate_hostname")
        include.add("validate_ssl_certificate") if (self.ssl) else exclude.add("validate_ssl_certificate")
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
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
        include.add("proxy_user") if (self.proxy) else exclude.add("proxy_user")
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.ssl == "true" or self.ssl)
            else exclude.add("ssl_certificate_file")
        )
        include.add("password") if not self.defer_credentials else exclude.add("password")
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        include.add("username") if not self.defer_credentials else exclude.add("username")
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.ssl == "true" or self.ssl)
            else exclude.add("ssl_certificate")
        )
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
