from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import AZUREDATALAKE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    client_credentials = "client_credentials"
    username_password = "username_password"


class ProxyProtocol(Enum):
    http = "http"
    https = "https"


class AzuredatalakeConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "6863060d-97c4-4653-abbe-958bde533f8c"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    authentication_method: AZUREDATALAKE_CONNECTION.AuthMethod | None = Field(
        AZUREDATALAKE_CONNECTION.AuthMethod.client_credentials, alias="auth_method"
    )
    client_id: str = Field(None, alias="client_id")
    client_secret: str = Field(None, alias="client_secret")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    no_proxy: str | None = Field(None, alias="no_proxy")
    password: str = Field(None, alias="password")
    proxy: bool | None = Field(False, alias="proxy")
    proxy_host: str = Field(None, alias="proxy_host")
    proxy_port: int = Field(None, alias="proxy_port")
    proxy_protocol: AZUREDATALAKE_CONNECTION.ProxyProtocol | None = Field(None, alias="proxy_protocol")
    encrypted_proxy_communication: bool | None = Field(None, alias="proxy_secured")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    tenant_id: str = Field(None, alias="tenant_id")
    url: str = Field(None, alias="url")
    use_home_as_root: bool | None = Field(True, alias="use_home_as_root")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    endpoint: str | None = Field(None, alias="endpoint")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("tenant_id")
            if (((not self.defer_credentials)) and (not self.endpoint))
            else exclude.add("tenant_id")
        )
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        (
            include.add("encrypted_proxy_communication")
            if (
                ((self.proxy))
                and (
                    self.proxy_protocol
                    and (
                        (hasattr(self.proxy_protocol, "value") and self.proxy_protocol.value == "http")
                        or (self.proxy_protocol == "http")
                    )
                )
            )
            else exclude.add("encrypted_proxy_communication")
        )
        include.add("no_proxy") if (self.proxy) else exclude.add("no_proxy")
        include.add("proxy_protocol") if (self.proxy) else exclude.add("proxy_protocol")
        include.add("client_id") if (not self.defer_credentials) else exclude.add("client_id")
        include.add("url") if (not self.endpoint) else exclude.add("url")
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "username_password"
                        )
                        or (self.authentication_method == "username_password")
                    )
                )
            )
            else exclude.add("password")
        )
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        (
            include.add("client_secret")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "client_credentials"
                        )
                        or (self.authentication_method == "client_credentials")
                    )
                )
            )
            else exclude.add("client_secret")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "username_password"
                        )
                        or (self.authentication_method == "username_password")
                    )
                )
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
        include.add("endpoint") if (self.hidden_dummy_property1) else exclude.add("endpoint")
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        include.add("proxy_protocol") if (self.proxy) else exclude.add("proxy_protocol")
        include.add("no_proxy") if (self.proxy) else exclude.add("no_proxy")
        include.add("url") if (not self.endpoint) else exclude.add("url")
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        include.add("client_id") if (not self.defer_credentials) else exclude.add("client_id")
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "username_password"
                    )
                    or (self.authentication_method == "username_password")
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "username_password"
                    )
                    or (self.authentication_method == "username_password")
                )
            )
            else exclude.add("username")
        )
        (
            include.add("encrypted_proxy_communication")
            if (self.proxy)
            and (
                self.proxy_protocol
                and (
                    (hasattr(self.proxy_protocol, "value") and self.proxy_protocol.value == "http")
                    or (self.proxy_protocol == "http")
                )
            )
            else exclude.add("encrypted_proxy_communication")
        )
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        (
            include.add("client_secret")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "client_credentials"
                    )
                    or (self.authentication_method == "client_credentials")
                )
            )
            else exclude.add("client_secret")
        )
        include.add("endpoint") if (not self.url) else exclude.add("endpoint")
        include.add("tenant_id") if (not self.defer_credentials) and (not self.endpoint) else exclude.add("tenant_id")
        include.add("ssl_certificate_file") if (not self.ssl_certificate) else exclude.add("ssl_certificate_file")
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
