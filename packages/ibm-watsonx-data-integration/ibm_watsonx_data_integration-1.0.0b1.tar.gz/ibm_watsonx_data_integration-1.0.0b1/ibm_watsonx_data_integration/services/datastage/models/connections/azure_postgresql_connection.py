from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import AZURE_POSTGRESQL_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    entra_id_service = "entra_id_service"
    entra_id_user = "entra_id_user"
    user_credentials = "user_credentials"


class AzurePostgresqlConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "a10fa240-20cf-4292-879c-48f73e8b451e"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    authentication_method: AZURE_POSTGRESQL_CONNECTION.AuthMethod | None = Field(
        AZURE_POSTGRESQL_CONNECTION.AuthMethod.user_credentials, alias="auth_method"
    )
    discover_data_assets: bool | None = Field(None, alias="auto_discovery")
    client_id: str = Field(None, alias="client_id")
    client_secret: str = Field(None, alias="client_secret")
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
    port_is_ssl_enabled: bool | None = Field(True, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    ssl_certificate_hostname: str | None = Field(None, alias="ssl_certificate_host")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    tenant_id: str = Field(None, alias="tenant_id")
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
            include.add("tenant_id")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "entra_id_service"
                                )
                                or (self.authentication_method == "entra_id_service")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "entra_id_user"
                            )
                            or (self.authentication_method == "entra_id_user")
                        )
                    )
                )
            )
            else exclude.add("tenant_id")
        )
        (
            include.add("ssl_certificate")
            if ((((not self.ssl_certificate_file))) and (self.port_is_ssl_enabled))
            else exclude.add("ssl_certificate")
        )
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
        (
            include.add("ssl_certificate_hostname")
            if (self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_hostname")
        )
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        (
            include.add("client_id")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "entra_id_service"
                        )
                        or (self.authentication_method == "entra_id_service")
                    )
                )
            )
            else exclude.add("client_id")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    ((not self.defer_credentials))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "entra_id_user"
                                    )
                                    or (self.authentication_method == "entra_id_user")
                                )
                            )
                        )
                        or (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "user_credentials"
                                )
                                or (self.authentication_method == "user_credentials")
                            )
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        include.add("authentication_method") if (not self.defer_credentials) else exclude.add("authentication_method")
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        (
            include.add("validate_ssl_certificate")
            if (self.port_is_ssl_enabled)
            else exclude.add("validate_ssl_certificate")
        )
        (
            include.add("client_secret")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "entra_id_service"
                        )
                        or (self.authentication_method == "entra_id_service")
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
                    ((not self.defer_credentials))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "entra_id_user"
                                    )
                                    or (self.authentication_method == "entra_id_user")
                                )
                            )
                        )
                        or (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "user_credentials"
                                )
                                or (self.authentication_method == "user_credentials")
                            )
                        )
                    )
                )
            )
            else exclude.add("username")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "entra_id_user"
                                )
                                or (self.authentication_method == "entra_id_user")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "user_credentials"
                            )
                            or (self.authentication_method == "user_credentials")
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "entra_id_user"
                                )
                                or (self.authentication_method == "entra_id_user")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "user_credentials"
                            )
                            or (self.authentication_method == "user_credentials")
                        )
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
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        include.add("authentication_method") if (not self.defer_credentials) else exclude.add("authentication_method")
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        (
            include.add("client_id")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "entra_id_service"
                    )
                    or (self.authentication_method == "entra_id_service")
                )
            )
            else exclude.add("client_id")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "entra_id_user" in str(self.authentication_method.value)
                        )
                        or ("entra_id_user" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "user_credentials" in str(self.authentication_method.value)
                        )
                        or ("user_credentials" in str(self.authentication_method))
                    )
                )
            )
            else exclude.add("password")
        )
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "entra_id_user" in str(self.authentication_method.value)
                        )
                        or ("entra_id_user" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "user_credentials" in str(self.authentication_method.value)
                        )
                        or ("user_credentials" in str(self.authentication_method))
                    )
                )
            )
            else exclude.add("username")
        )
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate")
        )
        (
            include.add("client_secret")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "entra_id_service"
                    )
                    or (self.authentication_method == "entra_id_service")
                )
            )
            else exclude.add("client_secret")
        )
        (
            include.add("validate_ssl_certificate")
            if (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("validate_ssl_certificate")
        )
        (
            include.add("ssl_certificate_hostname")
            if (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_hostname")
        )
        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
        (
            include.add("tenant_id")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "entra_id_service" in str(self.authentication_method.value)
                    )
                    or ("entra_id_service" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "entra_id_user" in str(self.authentication_method.value)
                    )
                    or ("entra_id_user" in str(self.authentication_method))
                )
            )
            else exclude.add("tenant_id")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
