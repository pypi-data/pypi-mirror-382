from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class BoxConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "99c3c67b-2133-4006-81f6-2b375a0048a3"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    access_token: str | None = Field(None, alias="access_token")
    client_id: str = Field(None, alias="client_id")
    client_secret: str = Field(None, alias="client_secret")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    enterprise_id: str = Field(None, alias="enterprise_id")
    private_key: str = Field(None, alias="private_key")
    private_key_password: str | None = Field(None, alias="private_key_password")
    public_key: str = Field(None, alias="public_key")
    username: str | None = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("access_token") if (not self.defer_credentials) else exclude.add("access_token")
        include.add("public_key") if (not self.defer_credentials) else exclude.add("public_key")
        (
            include.add("private_key_password")
            if (((not self.defer_credentials)) and (not self.access_token))
            else exclude.add("private_key_password")
        )
        (
            include.add("private_key")
            if (((not self.defer_credentials)) and (not self.access_token))
            else exclude.add("private_key")
        )
        (
            include.add("client_secret")
            if (((not self.defer_credentials)) and (not self.access_token))
            else exclude.add("client_secret")
        )
        (
            include.add("enterprise_id")
            if (((not self.defer_credentials)) and (not self.access_token))
            else exclude.add("enterprise_id")
        )
        (
            include.add("client_id")
            if (((not self.defer_credentials)) and (not self.access_token))
            else exclude.add("client_id")
        )
        (
            include.add("username")
            if (((not self.defer_credentials)) and (not self.access_token))
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
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")

        (
            include.add("enterprise_id")
            if (not self.defer_credentials) and (not self.access_token)
            else exclude.add("enterprise_id")
        )
        include.add("public_key") if (not self.defer_credentials) else exclude.add("public_key")
        (
            include.add("client_id")
            if (not self.defer_credentials) and (not self.access_token)
            else exclude.add("client_id")
        )
        (
            include.add("private_key_password")
            if (not self.defer_credentials) and (not self.access_token)
            else exclude.add("private_key_password")
        )
        include.add("access_token") if (not self.defer_credentials) else exclude.add("access_token")
        (
            include.add("private_key")
            if (not self.defer_credentials) and (not self.access_token)
            else exclude.add("private_key")
        )
        include.add("username") if (not self.defer_credentials) and (not self.access_token) else exclude.add("username")
        (
            include.add("client_secret")
            if (not self.defer_credentials) and (not self.access_token)
            else exclude.add("client_secret")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
