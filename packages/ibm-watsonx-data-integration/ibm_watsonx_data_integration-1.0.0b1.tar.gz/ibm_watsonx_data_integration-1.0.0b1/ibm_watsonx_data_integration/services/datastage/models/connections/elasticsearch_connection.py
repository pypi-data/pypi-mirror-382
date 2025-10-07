from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import ELASTICSEARCH_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    apikey = "apikey"
    username_password = "username_password"


class ElasticsearchConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "200d71ab-24a5-4b3d-85a4-a365bdd0d4cb"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    api_key: str = Field(None, alias="api_key")
    authentication_method: ELASTICSEARCH_CONNECTION.AuthMethod | None = Field(None, alias="auth_method")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    password: str = Field(None, alias="password")
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
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    url: str = Field(None, alias="url")
    use_anonymous_access: bool | None = Field(False, alias="use_anonymous_access")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("password")
            if (
                (
                    ((not self.defer_credentials))
                    and ((not self.use_anonymous_access))
                    and (
                        (
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
                    and ((not self.api_key))
                )
                and (((not self.defer_credentials)) and (not self.use_anonymous_access))
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
                and (not self.use_anonymous_access)
                and (
                    self.authentication_method
                    and (
                        (hasattr(self.authentication_method, "value") and self.authentication_method.value == "apikey")
                        or (self.authentication_method == "apikey")
                    )
                )
                and (not self.username)
                and (not self.password)
            )
            else exclude.add("api_key")
        )
        (
            include.add("satellite_location_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_connector_id))
            else exclude.add("satellite_location_id")
        )
        (
            include.add("username")
            if (
                (
                    ((not self.defer_credentials))
                    and ((not self.use_anonymous_access))
                    and (
                        (
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
                    and ((not self.api_key))
                )
                and (((not self.defer_credentials)) and (not self.use_anonymous_access))
            )
            else exclude.add("username")
        )
        include.add("use_anonymous_access") if (not self.defer_credentials) else exclude.add("use_anonymous_access")
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
            include.add("api_key")
            if (not self.defer_credentials)
            and (not self.use_anonymous_access)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "apikey")
                    or (self.authentication_method == "apikey")
                )
            )
            and (not self.username)
            and (not self.password)
            else exclude.add("api_key")
        )
        include.add("use_anonymous_access") if (not self.defer_credentials) else exclude.add("use_anonymous_access")
        (
            include.add("password")
            if (
                (not self.defer_credentials)
                and (not self.use_anonymous_access)
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
                and (not self.api_key)
            )
            and ((not self.defer_credentials) and (not self.use_anonymous_access))
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                (not self.defer_credentials)
                and (not self.use_anonymous_access)
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
                and (not self.api_key)
            )
            and ((not self.defer_credentials) and (not self.use_anonymous_access))
            else exclude.add("username")
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
