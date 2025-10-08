from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import IBM_MQ_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class ClientChannelDefinitionTransportType(Enum):
    tcp = "tcp"
    udp = "udp"


class IbmMqConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "21364ca9-5b2d-323e-bd4d-59ba961f75fb"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    cas_lite_service_authorization_header: str | None = Field(None, alias="cas_lite_auth_header")
    channel_name: str | None = Field(None, alias="client_channel_definition.channel_name")
    connection_name: str | None = Field(None, alias="client_channel_definition.connection_name")
    transport_type: IBM_MQ_CONNECTION.ClientChannelDefinitionTransportType | None = Field(
        IBM_MQ_CONNECTION.ClientChannelDefinitionTransportType.tcp, alias="client_channel_definition.transport_type"
    )
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    password: str | None = Field(None, alias="password")
    queue_manager_name: str | None = Field(None, alias="queue_manager_name")
    cipher_spec: str | None = Field("ECDHE_RSA_AES_128_CBC_SHA256", alias="ssl_cipher_spec")
    client_ssl_certificate: str | None = Field(None, alias="ssl_client_certificate")
    client_ssl_key: str | None = Field(None, alias="ssl_client_key")
    ssl_connection: bool | None = Field(False, alias="ssl_connection")
    server_ssl_certificate: str | None = Field(None, alias="ssl_server_certificate")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    username: str | None = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("password") if (not self.defer_credentials) else exclude.add("password")
        include.add("cipher_spec") if (self.ssl_connection) else exclude.add("cipher_spec")
        include.add("client_ssl_key") if (self.ssl_connection) else exclude.add("client_ssl_key")
        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        include.add("client_ssl_certificate") if (self.ssl_connection) else exclude.add("client_ssl_certificate")
        include.add("server_ssl_certificate") if (self.ssl_connection) else exclude.add("server_ssl_certificate")
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

        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service == "true" or self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        (
            include.add("server_ssl_certificate")
            if (self.ssl_connection == "true" or self.ssl_connection)
            else exclude.add("server_ssl_certificate")
        )
        (
            include.add("client_ssl_key")
            if (self.ssl_connection == "true" or self.ssl_connection)
            else exclude.add("client_ssl_key")
        )
        include.add("password") if (not self.defer_credentials) else exclude.add("password")
        include.add("username") if (not self.defer_credentials) else exclude.add("username")
        (
            include.add("client_ssl_certificate")
            if (self.ssl_connection == "true" or self.ssl_connection)
            else exclude.add("client_ssl_certificate")
        )
        (
            include.add("cipher_spec")
            if (self.ssl_connection == "true" or self.ssl_connection)
            else exclude.add("cipher_spec")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
