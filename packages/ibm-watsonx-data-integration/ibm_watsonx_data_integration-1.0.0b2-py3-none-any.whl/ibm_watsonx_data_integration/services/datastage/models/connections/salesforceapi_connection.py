from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import SALESFORCEAPI_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthenticationType(Enum):
    oauth_jwt = "oauth_jwt"
    oauth_username_and_password = "oauth_username_and_password"
    username_and_password = "username_and_password"


class SalesforceapiConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "3a00dbd2-2540-4976-afc2-5fc59f68ed35"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    authentication_type: SALESFORCEAPI_CONNECTION.AuthenticationType | None = Field(
        SALESFORCEAPI_CONNECTION.AuthenticationType.username_and_password, alias="authentication_type"
    )
    cas_lite_service_authorization_header: str | None = Field(None, alias="cas_lite_auth_header")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    consumer_key: str | None = Field(None, alias="consumer_key")
    consumer_secret_key: str | None = Field(None, alias="consumer_secret_key")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    password: str = Field(None, alias="password")
    proxy_server: bool | None = Field(False, alias="proxy_server")
    proxy_server_hostname_or_ip_address: str = Field(None, alias="proxy_server_host")
    proxy_server_password: str | None = Field(None, alias="proxy_server_password")
    proxy_server_port: str = Field(None, alias="proxy_server_port")
    proxy_server_username: str | None = Field(None, alias="proxy_server_username")
    schema_name: str | None = Field(None, alias="schema_name")
    server_certificate_key: str | None = Field(None, alias="server_certificate")
    token_expiry_time: int | None = Field(None, alias="token_expiry_time")
    url: str = Field(None, alias="url")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("consumer_key")
            if (
                (
                    (
                        self.authentication_type
                        and (
                            (
                                hasattr(self.authentication_type, "value")
                                and self.authentication_type.value == "oauth_jwt"
                            )
                            or (self.authentication_type == "oauth_jwt")
                        )
                    )
                )
                or (
                    self.authentication_type
                    and (
                        (
                            hasattr(self.authentication_type, "value")
                            and self.authentication_type.value == "oauth_username_and_password"
                        )
                        or (self.authentication_type == "oauth_username_and_password")
                    )
                )
            )
            else exclude.add("consumer_key")
        )
        (
            include.add("server_certificate_key")
            if (
                self.authentication_type
                and (
                    (hasattr(self.authentication_type, "value") and self.authentication_type.value == "oauth_jwt")
                    or (self.authentication_type == "oauth_jwt")
                )
            )
            else exclude.add("server_certificate_key")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.authentication_type
                            and (
                                (
                                    hasattr(self.authentication_type, "value")
                                    and self.authentication_type.value == "oauth_username_and_password"
                                )
                                or (self.authentication_type == "oauth_username_and_password")
                            )
                        )
                    )
                    or (
                        self.authentication_type
                        and (
                            (
                                hasattr(self.authentication_type, "value")
                                and self.authentication_type.value == "username_and_password"
                            )
                            or (self.authentication_type == "username_and_password")
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        include.add("proxy_server_password") if (self.proxy_server) else exclude.add("proxy_server_password")
        (
            include.add("consumer_secret_key")
            if (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value == "oauth_username_and_password"
                    )
                    or (self.authentication_type == "oauth_username_and_password")
                )
            )
            else exclude.add("consumer_secret_key")
        )
        include.add("proxy_server_username") if (self.proxy_server) else exclude.add("proxy_server_username")
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
        include.add("proxy_server_port") if (self.proxy_server) else exclude.add("proxy_server_port")
        (
            include.add("proxy_server_hostname_or_ip_address")
            if (self.proxy_server)
            else exclude.add("proxy_server_hostname_or_ip_address")
        )
        include.add("username") if (not self.defer_credentials) else exclude.add("username")
        (
            include.add("token_expiry_time")
            if (
                self.authentication_type
                and (
                    (hasattr(self.authentication_type, "value") and self.authentication_type.value == "oauth_jwt")
                    or (self.authentication_type == "oauth_jwt")
                )
            )
            else exclude.add("token_expiry_time")
        )
        (
            include.add("password")
            if (
                (
                    (
                        self.authentication_type
                        and (
                            (
                                hasattr(self.authentication_type, "value")
                                and self.authentication_type.value == "oauth_username_and_password"
                            )
                            or (self.authentication_type == "oauth_username_and_password")
                        )
                    )
                )
                or (
                    self.authentication_type
                    and (
                        (
                            hasattr(self.authentication_type, "value")
                            and self.authentication_type.value == "username_and_password"
                        )
                        or (self.authentication_type == "username_and_password")
                    )
                )
            )
            else exclude.add("password")
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

        (
            include.add("server_certificate_key")
            if (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "oauth_jwt" in str(self.authentication_type.value)
                    )
                    or ("oauth_jwt" in str(self.authentication_type))
                )
            )
            else exclude.add("server_certificate_key")
        )
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
            include.add("token_expiry_time")
            if (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "oauth_jwt" in str(self.authentication_type.value)
                    )
                    or ("oauth_jwt" in str(self.authentication_type))
                )
            )
            else exclude.add("token_expiry_time")
        )
        (
            include.add("proxy_server_port")
            if (self.proxy_server and "true" in str(self.proxy_server))
            else exclude.add("proxy_server_port")
        )
        (
            include.add("proxy_server_password")
            if (self.proxy_server and "true" in str(self.proxy_server))
            else exclude.add("proxy_server_password")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "oauth_username_and_password" in str(self.authentication_type.value)
                    )
                    or ("oauth_username_and_password" in str(self.authentication_type))
                )
                or self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "username_and_password" in str(self.authentication_type.value)
                    )
                    or ("username_and_password" in str(self.authentication_type))
                )
            )
            else exclude.add("password")
        )
        include.add("username") if not self.defer_credentials else exclude.add("username")
        (
            include.add("proxy_server_username")
            if (self.proxy_server and "true" in str(self.proxy_server))
            else exclude.add("proxy_server_username")
        )
        (
            include.add("consumer_key")
            if (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "oauth_jwt" in str(self.authentication_type.value)
                    )
                    or ("oauth_jwt" in str(self.authentication_type))
                )
                or self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "oauth_username_and_password" in str(self.authentication_type.value)
                    )
                    or ("oauth_username_and_password" in str(self.authentication_type))
                )
            )
            else exclude.add("consumer_key")
        )
        (
            include.add("proxy_server_hostname_or_ip_address")
            if (self.proxy_server and "true" in str(self.proxy_server))
            else exclude.add("proxy_server_hostname_or_ip_address")
        )
        (
            include.add("consumer_secret_key")
            if (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "oauth_username_and_password" in str(self.authentication_type.value)
                    )
                    or ("oauth_username_and_password" in str(self.authentication_type))
                )
            )
            else exclude.add("consumer_secret_key")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
