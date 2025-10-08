from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import DB2FORDATASTAGE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthenticationType(Enum):
    api_key = "api_key"
    username_and_password = "username_and_password"


class Db2fordatastageConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "fa31fba9-10e9-32d7-968c-f677fffd1e3b"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    advanced_connection_settings: bool | None = Field(True, alias="advanced")
    api_key: str | None = Field(None, alias="advanced.api_key")
    hostname: str = Field(None, alias="advanced.hostname")
    options: str | None = Field(None, alias="advanced.options")
    port: int = Field(50000, alias="advanced.port")
    ssl_certificate_arm: str | None = Field(None, alias="advanced.ssl_certificate")
    ssl_connection: bool | None = Field(False, alias="advanced.ssl_connection")
    credentials: DB2FORDATASTAGE_CONNECTION.AuthenticationType | None = Field(
        DB2FORDATASTAGE_CONNECTION.AuthenticationType.username_and_password, alias="authentication_type"
    )
    cas_lite_service_authorization_header: str | None = Field(None, alias="cas_lite_auth_header")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    database: str = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    keep_conductor_connection_alive: bool | None = Field(False, alias="keep_conductor_connection_alive")
    password: str = Field(None, alias="password")
    satellite_client_certificate: str | None = Field(None, alias="sl_client_cert")
    satellite_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    satellite_connector_id: str | None = Field(None, alias="sl_connector_id")
    satellite_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    satellite_endpoint_display_name: str | None = Field(None, alias="sl_endpoint_name")
    satellite_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    original_hostname_of_the_resource: str | None = Field(None, alias="sl_host_original")
    satellite_as_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    satellite_location_id: str | None = Field(None, alias="sl_location_id")
    satellite_service_url: str | None = Field(None, alias="sl_service_url")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    use_direct_connections: bool | None = Field(False, alias="use_direct_connections")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("options") if (self.advanced_connection_settings) else exclude.add("options")
        (
            include.add("password")
            if (
                (
                    (
                        self.credentials
                        and (
                            (hasattr(self.credentials, "value") and self.credentials.value == "username_and_password")
                            or (self.credentials == "username_and_password")
                        )
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("password")
        )
        include.add("hostname") if (self.advanced_connection_settings) else exclude.add("hostname")
        (
            include.add("api_key")
            if (
                ((self.advanced_connection_settings))
                and (
                    self.credentials
                    and (
                        (hasattr(self.credentials, "value") and self.credentials.value == "api_key")
                        or (self.credentials == "api_key")
                    )
                )
            )
            else exclude.add("api_key")
        )
        include.add("port") if (self.advanced_connection_settings) else exclude.add("port")
        include.add("ssl_connection") if (self.advanced_connection_settings) else exclude.add("ssl_connection")
        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("ssl_certificate_arm")
            if (((self.advanced_connection_settings)) and (self.ssl_connection))
            else exclude.add("ssl_certificate_arm")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        (
            include.add("username")
            if (
                (
                    (
                        self.credentials
                        and (
                            (hasattr(self.credentials, "value") and self.credentials.value == "username_and_password")
                            or (self.credentials == "username_and_password")
                        )
                    )
                )
                and (not self.defer_credentials)
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

        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("api_key")
            if (self.advanced_connection_settings == "true" or self.advanced_connection_settings)
            and (
                self.credentials
                and (
                    (hasattr(self.credentials, "value") and self.credentials.value == "api_key")
                    or (self.credentials == "api_key")
                )
            )
            else exclude.add("api_key")
        )
        (
            include.add("hostname")
            if (self.advanced_connection_settings == "true" or self.advanced_connection_settings)
            else exclude.add("hostname")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service == "true" or self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        (
            include.add("ssl_certificate_arm")
            if (self.advanced_connection_settings == "true" or self.advanced_connection_settings)
            and (self.ssl_connection == "true" or self.ssl_connection)
            else exclude.add("ssl_certificate_arm")
        )
        (
            include.add("ssl_connection")
            if (self.advanced_connection_settings == "true" or self.advanced_connection_settings)
            else exclude.add("ssl_connection")
        )
        (
            include.add("password")
            if (
                self.credentials
                and (
                    (hasattr(self.credentials, "value") and self.credentials.value == "username_and_password")
                    or (self.credentials == "username_and_password")
                )
            )
            and (not self.defer_credentials)
            else exclude.add("password")
        )
        (
            include.add("options")
            if (self.advanced_connection_settings == "true" or self.advanced_connection_settings)
            else exclude.add("options")
        )
        (
            include.add("username")
            if (
                self.credentials
                and (
                    (hasattr(self.credentials, "value") and self.credentials.value == "username_and_password")
                    or (self.credentials == "username_and_password")
                )
            )
            and (not self.defer_credentials)
            else exclude.add("username")
        )
        (
            include.add("port")
            if (self.advanced_connection_settings == "true" or self.advanced_connection_settings)
            else exclude.add("port")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
