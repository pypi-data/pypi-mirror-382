from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import DV_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    apikey = "apikey"
    username_password = "username_password"


class InstanceEnvironment(Enum):
    cloud = "cloud"
    private = "private"


class DvConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "dv"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    access_token: str = Field(None, alias="access_token")
    api_key: str = Field(None, alias="api_key")
    application_name: str | None = Field(None, alias="application_name")
    auth_method: DV_CONNECTION.AuthMethod | None = Field(None, alias="auth_method")
    auto_discovery: bool | None = Field(None, alias="auto_discovery")
    avoid_timestamp_conversion: bool | None = Field(None, alias="avoid_timestamp_conversion")
    client_accounting_information: str | None = Field(None, alias="client_accounting_information")
    client_hostname: str | None = Field(None, alias="client_hostname")
    client_user: str | None = Field(None, alias="client_user")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    command_timeout: int | None = Field(600, alias="command_timeout")
    database: str = Field("bigsql", alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    host: str = Field(None, alias="host")
    inherit_access_token: bool | None = Field(False, alias="inherit_access_token")
    instance_environment: DV_CONNECTION.InstanceEnvironment | None = Field(None, alias="instance_environment")
    instance_id: str = Field(None, alias="instance_id")
    password: str = Field(None, alias="password")
    port: int = Field(None, alias="port")
    service_name: str | None = Field(None, alias="service_name")
    sg_gateway_id: str | None = Field(None, alias="sg_gateway_id")
    sg_host_original: str | None = Field(None, alias="sg_host_original")
    sg_http_proxy: bool | None = Field(None, alias="sg_http_proxy")
    sg_security_token: str | None = Field(None, alias="sg_security_token")
    sg_service_url: str | None = Field(None, alias="sg_service_url")
    sl_client_cert: str | None = Field(None, alias="sl_client_cert")
    sl_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    sl_connector_id: str | None = Field(None, alias="sl_connector_id")
    sl_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    sl_endpoint_name: str | None = Field(None, alias="sl_endpoint_name")
    sl_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    sl_host_original: str | None = Field(None, alias="sl_host_original")
    sl_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    sl_location_id: str | None = Field(None, alias="sl_location_id")
    sl_service_url: str | None = Field(None, alias="sl_service_url")
    ssl: bool | None = Field(False, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    use_s2s_ssl_certificate: bool | None = Field(False, alias="use_s2s_ssl_certificate")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    properties: str | None = Field(None, alias="properties")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("ssl_certificate")
            if ((((not self.ssl_certificate_file))) and (self.ssl))
            else exclude.add("ssl_certificate")
        )
        (
            include.add("access_token")
            if (
                ((not self.defer_credentials))
                and (not self.username)
                and (not self.password)
                and (not self.api_key)
                and (self.inherit_access_token)
            )
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (not self.access_token)
                and (not self.inherit_access_token)
                and (not self.api_key)
                and (
                    self.auth_method
                    and (
                        (hasattr(self.auth_method, "value") and self.auth_method.value == "username_password")
                        or (self.auth_method == "username_password")
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("use_s2s_ssl_certificate")
            if (((self.ssl)) and (self.ssl_certificate))
            else exclude.add("use_s2s_ssl_certificate")
        )
        (
            include.add("sl_connector_id")
            if (((not self.sg_gateway_id)) and (not self.sl_location_id))
            else exclude.add("sl_connector_id")
        )
        (
            include.add("api_key")
            if (
                ((not self.defer_credentials))
                and (not self.username)
                and (not self.access_token)
                and (not self.inherit_access_token)
                and (
                    self.auth_method
                    and (
                        (hasattr(self.auth_method, "value") and self.auth_method.value == "apikey")
                        or (self.auth_method == "apikey")
                    )
                )
            )
            else exclude.add("api_key")
        )
        include.add("inherit_access_token") if (not self.defer_credentials) else exclude.add("inherit_access_token")
        (
            include.add("sl_location_id")
            if (((not self.sg_gateway_id)) and (not self.sl_connector_id))
            else exclude.add("sl_location_id")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (not self.access_token)
                and (not self.inherit_access_token)
                and (not self.api_key)
                and (
                    self.auth_method
                    and (
                        (hasattr(self.auth_method, "value") and self.auth_method.value == "username_password")
                        or (self.auth_method == "username_password")
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
        include.add("properties") if (self.hidden_dummy_property1) else exclude.add("properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        (
            include.add("sl_connector_id")
            if (not self.sg_gateway_id) and (not self.sl_location_id)
            else exclude.add("sl_connector_id")
        )
        (
            include.add("use_s2s_ssl_certificate")
            if (self.ssl == "true" or self.ssl) and (self.ssl_certificate)
            else exclude.add("use_s2s_ssl_certificate")
        )
        (
            include.add("auth_method")
            if (
                self.instance_environment
                and (
                    (hasattr(self.instance_environment, "value") and self.instance_environment.value == "cloud")
                    or (self.instance_environment == "cloud")
                )
            )
            else exclude.add("auth_method")
        )
        (
            include.add("api_key")
            if (not self.defer_credentials)
            and (not self.username)
            and (not self.access_token)
            and (not self.inherit_access_token)
            and (
                self.auth_method
                and (
                    (
                        hasattr(self.auth_method, "value")
                        and self.auth_method.value
                        and "apikey" in str(self.auth_method.value)
                    )
                    or ("apikey" in str(self.auth_method))
                )
            )
            else exclude.add("api_key")
        )
        include.add("inherit_access_token") if (not self.defer_credentials) else exclude.add("inherit_access_token")
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.ssl == "true" or self.ssl)
            else exclude.add("ssl_certificate_file")
        )
        (
            include.add("access_token")
            if (not self.defer_credentials)
            and (not self.username)
            and (not self.password)
            and (not self.api_key)
            and (self.inherit_access_token)
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (not self.access_token)
            and (not self.inherit_access_token)
            and (not self.api_key)
            and (
                self.auth_method
                and (
                    (
                        hasattr(self.auth_method, "value")
                        and self.auth_method.value
                        and "username_password" in str(self.auth_method.value)
                    )
                    or ("username_password" in str(self.auth_method))
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (not self.access_token)
            and (not self.inherit_access_token)
            and (not self.api_key)
            and (
                self.auth_method
                and (
                    (
                        hasattr(self.auth_method, "value")
                        and self.auth_method.value
                        and "username_password" in str(self.auth_method.value)
                    )
                    or ("username_password" in str(self.auth_method))
                )
            )
            else exclude.add("username")
        )
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.ssl == "true" or self.ssl)
            else exclude.add("ssl_certificate")
        )
        (
            include.add("sl_location_id")
            if (not self.sg_gateway_id) and (not self.sl_connector_id)
            else exclude.add("sl_location_id")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
