from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class Db2cloudConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "506039fb-802f-4ef2-a2bf-c1682e9c8aa2"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    access_token: str = Field(None, alias="access_token")
    discover_data_assets: bool | None = Field(None, alias="auto_discovery")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    command_timeout: int | None = Field(600, alias="command_timeout")
    database: str = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    hostname_or_ip_address: str = Field(None, alias="host")
    use_my_platform_login_credentials: bool | None = Field(False, alias="inherit_access_token")
    max_transport_objects: int | None = Field(None, alias="max_transport_objects")
    password: str = Field(None, alias="password")
    port: int | None = Field(50001, alias="port")
    port_is_ssl_enabled: bool | None = Field(True, alias="ssl")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    additional_properties: str | None = Field(None, alias="properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("access_token")
            if (((not self.defer_credentials)) and (not self.username))
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (not self.access_token)
                and (not self.use_my_platform_login_credentials)
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (not self.access_token)
                and (not self.use_my_platform_login_credentials)
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
        include.add("access_token") if (self.hidden_dummy_property1) else exclude.add("access_token")
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        (
            include.add("use_my_platform_login_credentials")
            if (self.hidden_dummy_property1)
            else exclude.add("use_my_platform_login_credentials")
        )
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")

        (
            include.add("access_token")
            if (not self.defer_credentials) and (not self.username)
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (not self.access_token)
            and (self.use_my_platform_login_credentials != "yes")
            else exclude.add("password")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (not self.access_token)
            and (self.use_my_platform_login_credentials != "yes")
            else exclude.add("username")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
