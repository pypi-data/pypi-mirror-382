from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import TABLEAU_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    access_token = "access_token"
    username_and_password = "username_and_password"


class TableauConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "9ebc33eb-8c01-43fd-be1e-7202cf5c2c82"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_port: str | None = Field(None, alias="_port")
    access_token_name: str = Field(None, alias="access_token_name")
    access_token_secret: str = Field(None, alias="access_token_secret")
    authentication_method: TABLEAU_CONNECTION.AuthMethod | None = Field(
        TABLEAU_CONNECTION.AuthMethod.username_and_password, alias="auth_method"
    )
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    hostname_or_ip_address: str = Field(None, alias="host")
    password: str = Field(None, alias="password")
    port: int | None = Field(None, alias="port")
    secure_gateway_id: str | None = Field(None, alias="sg_gateway_id")
    sg_host_original: str | None = Field(None, alias="sg_host_original")
    secure_gateway_as_http_proxy: bool | None = Field(None, alias="sg_http_proxy")
    secure_gateway_security_token: str | None = Field(None, alias="sg_security_token")
    secure_gateway_service_url: str | None = Field(None, alias="sg_service_url")
    site: str | None = Field(None, alias="site")
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
    trust_all_ssl_certificates: bool | None = Field(False, alias="trust_all_ssl_cert")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
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
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (not self.access_token_name)
                and (not self.access_token_secret)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "username_and_password"
                        )
                        or (self.authentication_method == "username_and_password")
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
            include.add("access_token_name")
            if (
                ((not self.username))
                and (not self.password)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "access_token"
                        )
                        or (self.authentication_method == "access_token")
                    )
                )
            )
            else exclude.add("access_token_name")
        )
        (
            include.add("access_token_secret")
            if (
                ((not self.username))
                and (not self.password)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "access_token"
                        )
                        or (self.authentication_method == "access_token")
                    )
                )
            )
            else exclude.add("access_token_secret")
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
                and (not self.access_token_name)
                and (not self.access_token_secret)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "username_and_password"
                        )
                        or (self.authentication_method == "username_and_password")
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
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        (
            include.add("satellite_connector_id")
            if (not self.secure_gateway_id) and (not self.satellite_location_id)
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("access_token_secret")
            if (not self.username)
            and (not self.password)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "access_token"
                    )
                    or (self.authentication_method == "access_token")
                )
            )
            else exclude.add("access_token_secret")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (not self.access_token_name)
            and (not self.access_token_secret)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "username_and_password"
                    )
                    or (self.authentication_method == "username_and_password")
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (not self.access_token_name)
            and (not self.access_token_secret)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "username_and_password"
                    )
                    or (self.authentication_method == "username_and_password")
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
        (
            include.add("access_token_name")
            if (not self.username)
            and (not self.password)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "access_token"
                    )
                    or (self.authentication_method == "access_token")
                )
            )
            else exclude.add("access_token_name")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
