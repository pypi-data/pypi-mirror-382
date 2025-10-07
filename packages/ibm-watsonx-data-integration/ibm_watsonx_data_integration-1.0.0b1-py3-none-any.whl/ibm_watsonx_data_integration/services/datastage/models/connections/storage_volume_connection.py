from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class StorageVolumeConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "9f30e3c3-b854-4144-b5c3-98b7a835dc79"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    access_token: str = Field(None, alias="access_token")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    gateway_url: str = Field(None, alias="gateway_url")
    inherit_access_token: bool | None = Field(False, alias="inherit_access_token")
    instance_id: str | None = Field(None, alias="instance_id")
    password: str | None = Field(None, alias="password")
    pvc: str | None = Field(None, alias="pvc")
    read_timeout: int | None = Field(300, alias="read_timeout")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    trust_all_ssl_cert: bool | None = Field(False, alias="trust_all_ssl_cert")
    username: str | None = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    volume: str = Field(None, alias="volume")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        (
            include.add("access_token")
            if (((not self.defer_credentials)) and (not self.username))
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (((not self.defer_credentials)) and (not self.access_token) and (not self.inherit_access_token))
            else exclude.add("password")
        )
        (
            include.add("username")
            if (((not self.defer_credentials)) and (not self.access_token) and (not self.inherit_access_token))
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
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        include.add("ssl_certificate_file") if (not self.ssl_certificate) else exclude.add("ssl_certificate_file")
        (
            include.add("access_token")
            if (not self.defer_credentials) and (not self.username)
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (not self.defer_credentials) and (not self.access_token) and (not self.inherit_access_token)
            else exclude.add("password")
        )
        (
            include.add("username")
            if (not self.defer_credentials) and (not self.access_token) and (not self.inherit_access_token)
            else exclude.add("username")
        )
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
