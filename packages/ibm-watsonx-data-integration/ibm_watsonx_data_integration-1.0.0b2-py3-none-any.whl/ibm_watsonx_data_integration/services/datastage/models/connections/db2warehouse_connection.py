from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import DB2WAREHOUSE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    apikey = "apikey"
    username_password = "username_password"


class Db2warehouseConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "cfdcb449-1204-44ba-baa6-9a8a878e6aa7"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    access_token: str = Field(None, alias="access_token")
    api_key: str = Field(None, alias="api_key")
    application_name: str | None = Field(None, alias="application_name")
    authentication_method: DB2WAREHOUSE_CONNECTION.AuthMethod | None = Field(None, alias="auth_method")
    discover_data_assets: bool | None = Field(None, alias="auto_discovery")
    avoid_timestamp_conversion: bool | None = Field(None, alias="avoid_timestamp_conversion")
    client_accounting_information: str | None = Field(None, alias="client_accounting_information")
    client_hostname: str | None = Field(None, alias="client_hostname")
    client_user: str | None = Field(None, alias="client_user")
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
    secure_gateway_id: str | None = Field(None, alias="sg_gateway_id")
    sg_host_original: str | None = Field(None, alias="sg_host_original")
    secure_gateway_as_http_proxy: bool | None = Field(None, alias="sg_http_proxy")
    secure_gateway_security_token: str | None = Field(None, alias="sg_security_token")
    secure_gateway_service_url: str | None = Field(None, alias="sg_service_url")
    satellite_client_certificate: str | None = Field(None, alias="sl_client_cert")
    satellite_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    satellite_connector_id: str | None = Field(None, alias="sl_connector_id")
    satellite_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    satellite_endpoint_display_name: str | None = Field(None, alias="sl_endpoint_name")
    satellite_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    sl_host_original: str | None = Field(None, alias="sl_host_original")
    satellite_as_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    satellite_location_id: str | None = Field(None, alias="sl_location_id")
    satellite_service_url: str | None = Field(None, alias="sl_service_url")
    port_is_ssl_enabled: bool | None = Field(True, alias="ssl")
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

        (
            include.add("ssl_certificate")
            if ((((not self.ssl_certificate_file))) and (self.port_is_ssl_enabled))
            else exclude.add("ssl_certificate")
        )
        (
            include.add("access_token")
            if (
                ((not self.defer_credentials))
                and (not self.username)
                and (not self.password)
                and (not self.api_key)
                and (self.use_my_platform_login_credentials)
            )
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (not self.access_token)
                and (not self.use_my_platform_login_credentials)
                and (not self.api_key)
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
        (
            include.add("satellite_connector_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_location_id))
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("api_key")
            if (
                ((not self.defer_credentials))
                and (not self.username)
                and (not self.access_token)
                and (not self.use_my_platform_login_credentials)
                and (
                    self.authentication_method
                    and (
                        (hasattr(self.authentication_method, "value") and self.authentication_method.value == "apikey")
                        or (self.authentication_method == "apikey")
                    )
                )
            )
            else exclude.add("api_key")
        )
        (
            include.add("use_my_platform_login_credentials")
            if (not self.defer_credentials)
            else exclude.add("use_my_platform_login_credentials")
        )
        (
            include.add("satellite_location_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_connector_id))
            else exclude.add("satellite_location_id")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (not self.access_token)
                and (not self.use_my_platform_login_credentials)
                and (not self.api_key)
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
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        (
            include.add("satellite_connector_id")
            if (not self.secure_gateway_id) and (not self.satellite_location_id)
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("api_key")
            if (not self.defer_credentials)
            and (not self.username)
            and (not self.access_token)
            and (self.use_my_platform_login_credentials != "yes")
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "apikey" in str(self.authentication_method.value)
                    )
                    or ("apikey" in str(self.authentication_method))
                )
            )
            else exclude.add("api_key")
        )
        (
            include.add("use_my_platform_login_credentials")
            if (not self.defer_credentials)
            else exclude.add("use_my_platform_login_credentials")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        (
            include.add("access_token")
            if (not self.defer_credentials)
            and (not self.username)
            and (not self.password)
            and (not self.api_key)
            and (self.use_my_platform_login_credentials == "yes")
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (not self.access_token)
            and (self.use_my_platform_login_credentials != "yes")
            and (not self.api_key)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password" in str(self.authentication_method.value)
                    )
                    or ("username_password" in str(self.authentication_method))
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (not self.access_token)
            and (self.use_my_platform_login_credentials != "yes")
            and (not self.api_key)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password" in str(self.authentication_method.value)
                    )
                    or ("username_password" in str(self.authentication_method))
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
            include.add("satellite_location_id")
            if (not self.secure_gateway_id) and (not self.satellite_connector_id)
            else exclude.add("satellite_location_id")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
