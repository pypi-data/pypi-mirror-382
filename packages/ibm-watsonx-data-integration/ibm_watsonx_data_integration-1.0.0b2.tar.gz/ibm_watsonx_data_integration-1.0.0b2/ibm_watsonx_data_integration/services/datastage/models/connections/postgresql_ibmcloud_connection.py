from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class PostgresqlIbmcloudConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "048ed1bf-516c-46f0-ae90-fa3349d8bc1c"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    discover_data_assets: bool | None = Field(None, alias="auto_discovery")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    database: str = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    hostname_or_ip_address: str = Field(None, alias="host")
    login_timeout: int | None = Field(None, alias="login_timeout")
    password: str = Field(None, alias="password")
    port: int = Field(None, alias="port")
    proxy: bool | None = Field(False, alias="proxy")
    proxy_host: str = Field(None, alias="proxy_host")
    proxy_password: str | None = Field(None, alias="proxy_password")
    proxy_port: int = Field(None, alias="proxy_port")
    proxy_username: str | None = Field(None, alias="proxy_user")
    query_timeout: int | None = Field(300, alias="query_timeout")
    retry_limit: int | None = Field(2, alias="retry_limit")
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

        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        include.add("password") if (not self.defer_credentials) else exclude.add("password")
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
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
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        include.add("ssl_certificate_file") if (not self.ssl_certificate) else exclude.add("ssl_certificate_file")
        include.add("password") if not self.defer_credentials else exclude.add("password")
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        include.add("username") if not self.defer_credentials else exclude.add("username")
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
