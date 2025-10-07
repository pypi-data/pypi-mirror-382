from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import PLANNING_ANALYTICS_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthType(Enum):
    bearer = "bearer"
    cam_credentials = "cam_credentials"
    basic = "basic"


class PlanningAnalyticsConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "tm1odata"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    access_token: str = Field(None, alias="access_token")
    authentication_type: PLANNING_ANALYTICS_CONNECTION.AuthType | None = Field(None, alias="auth_type")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    gateway_url: str | None = Field(None, alias="gateway_url")
    use_my_platform_login_credentials: bool | None = Field(False, alias="inherit_access_token")
    namespace: str = Field(None, alias="namespace")
    password: str = Field(None, alias="password")
    tm1_server_api_root_url: str = Field(None, alias="service_root")
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
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    ssl_certificate_hostname: str | None = Field(None, alias="ssl_certificate_host")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
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
            if (
                (
                    ((not self.defer_credentials))
                    and ((not self.access_token))
                    and ((not self.use_my_platform_login_credentials))
                )
                and (
                    ((not self.defer_credentials))
                    and (
                        (
                            (
                                self.authentication_type
                                and (
                                    (
                                        hasattr(self.authentication_type, "value")
                                        and self.authentication_type.value == "basic"
                                    )
                                    or (self.authentication_type == "basic")
                                )
                            )
                        )
                        or (
                            self.authentication_type
                            and (
                                (
                                    hasattr(self.authentication_type, "value")
                                    and self.authentication_type.value == "bearer"
                                )
                                or (self.authentication_type == "bearer")
                            )
                        )
                        or (
                            self.authentication_type
                            and (
                                (
                                    hasattr(self.authentication_type, "value")
                                    and self.authentication_type.value == "cam_credentials"
                                )
                                or (self.authentication_type == "cam_credentials")
                            )
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        include.add("sl_connector_id") if (not self.sl_location_id) else exclude.add("sl_connector_id")
        (
            include.add("gateway_url")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_type
                    and (
                        (hasattr(self.authentication_type, "value") and self.authentication_type.value == "bearer")
                        or (self.authentication_type == "bearer")
                    )
                )
                and (
                    (
                        (
                            self.authentication_type
                            and (
                                (
                                    hasattr(self.authentication_type, "value")
                                    and self.authentication_type.value != "basic"
                                )
                                or (self.authentication_type != "basic")
                            )
                        )
                    )
                    and (
                        self.authentication_type
                        and (
                            (
                                hasattr(self.authentication_type, "value")
                                and self.authentication_type.value != "cam_credentials"
                            )
                            or (self.authentication_type != "cam_credentials")
                        )
                    )
                )
            )
            else exclude.add("gateway_url")
        )
        (
            include.add("namespace")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_type
                    and (
                        (
                            hasattr(self.authentication_type, "value")
                            and self.authentication_type.value == "cam_credentials"
                        )
                        or (self.authentication_type == "cam_credentials")
                    )
                )
                and (
                    (
                        (
                            self.authentication_type
                            and (
                                (
                                    hasattr(self.authentication_type, "value")
                                    and self.authentication_type.value != "basic"
                                )
                                or (self.authentication_type != "basic")
                            )
                        )
                    )
                    and (
                        self.authentication_type
                        and (
                            (hasattr(self.authentication_type, "value") and self.authentication_type.value != "bearer")
                            or (self.authentication_type != "bearer")
                        )
                    )
                )
            )
            else exclude.add("namespace")
        )
        (
            include.add("ssl_certificate_hostname")
            if (((self.ssl_certificate)) and (self.validate_ssl_certificate))
            else exclude.add("ssl_certificate_hostname")
        )
        include.add("sl_location_id") if (not self.sl_connector_id) else exclude.add("sl_location_id")
        (
            include.add("username")
            if (
                (
                    ((not self.defer_credentials))
                    and ((not self.access_token))
                    and ((not self.use_my_platform_login_credentials))
                )
                and (
                    ((not self.defer_credentials))
                    and (
                        (
                            (
                                self.authentication_type
                                and (
                                    (
                                        hasattr(self.authentication_type, "value")
                                        and self.authentication_type.value == "basic"
                                    )
                                    or (self.authentication_type == "basic")
                                )
                            )
                        )
                        or (
                            self.authentication_type
                            and (
                                (
                                    hasattr(self.authentication_type, "value")
                                    and self.authentication_type.value == "bearer"
                                )
                                or (self.authentication_type == "bearer")
                            )
                        )
                        or (
                            self.authentication_type
                            and (
                                (
                                    hasattr(self.authentication_type, "value")
                                    and self.authentication_type.value == "cam_credentials"
                                )
                                or (self.authentication_type == "cam_credentials")
                            )
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
        include.add("access_token") if (self.hidden_dummy_property1) else exclude.add("access_token")
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        (
            include.add("use_my_platform_login_credentials")
            if (self.hidden_dummy_property1)
            else exclude.add("use_my_platform_login_credentials")
        )
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        include.add("sl_connector_id") if (not self.sl_location_id) else exclude.add("sl_connector_id")
        (
            include.add("ssl_certificate_hostname")
            if (self.ssl_certificate) and (self.validate_ssl_certificate == "true" or self.validate_ssl_certificate)
            else exclude.add("ssl_certificate_hostname")
        )
        (
            include.add("namespace")
            if (not self.defer_credentials)
            and (
                self.authentication_type
                and (
                    (hasattr(self.authentication_type, "value") and self.authentication_type.value == "cam_credentials")
                    or (self.authentication_type == "cam_credentials")
                )
            )
            and (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "basic" not in str(self.authentication_type.value)
                    )
                    or ("basic" not in str(self.authentication_type))
                )
                and self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "bearer" not in str(self.authentication_type.value)
                    )
                    or ("bearer" not in str(self.authentication_type))
                )
            )
            else exclude.add("namespace")
        )
        (
            include.add("gateway_url")
            if (not self.defer_credentials)
            and (
                self.authentication_type
                and (
                    (hasattr(self.authentication_type, "value") and self.authentication_type.value == "bearer")
                    or (self.authentication_type == "bearer")
                )
            )
            and (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "basic" not in str(self.authentication_type.value)
                    )
                    or ("basic" not in str(self.authentication_type))
                )
                and self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "cam_credentials" not in str(self.authentication_type.value)
                    )
                    or ("cam_credentials" not in str(self.authentication_type))
                )
            )
            else exclude.add("gateway_url")
        )
        include.add("ssl_certificate_file") if (not self.ssl_certificate) else exclude.add("ssl_certificate_file")
        (
            include.add("access_token")
            if (not self.defer_credentials) and (not self.username)
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (
                (not self.defer_credentials)
                and (not self.access_token)
                and (self.use_my_platform_login_credentials != "yes")
            )
            and (
                (not self.defer_credentials)
                and (
                    self.authentication_type
                    and (
                        (
                            hasattr(self.authentication_type, "value")
                            and self.authentication_type.value
                            and "basic" in str(self.authentication_type.value)
                        )
                        or ("basic" in str(self.authentication_type))
                    )
                    and self.authentication_type
                    and (
                        (
                            hasattr(self.authentication_type, "value")
                            and self.authentication_type.value
                            and "bearer" in str(self.authentication_type.value)
                        )
                        or ("bearer" in str(self.authentication_type))
                    )
                    and self.authentication_type
                    and (
                        (
                            hasattr(self.authentication_type, "value")
                            and self.authentication_type.value
                            and "cam_credentials" in str(self.authentication_type.value)
                        )
                        or ("cam_credentials" in str(self.authentication_type))
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                (not self.defer_credentials)
                and (not self.access_token)
                and (self.use_my_platform_login_credentials != "yes")
            )
            and (
                (not self.defer_credentials)
                and (
                    self.authentication_type
                    and (
                        (
                            hasattr(self.authentication_type, "value")
                            and self.authentication_type.value
                            and "basic" in str(self.authentication_type.value)
                        )
                        or ("basic" in str(self.authentication_type))
                    )
                    and self.authentication_type
                    and (
                        (
                            hasattr(self.authentication_type, "value")
                            and self.authentication_type.value
                            and "bearer" in str(self.authentication_type.value)
                        )
                        or ("bearer" in str(self.authentication_type))
                    )
                    and self.authentication_type
                    and (
                        (
                            hasattr(self.authentication_type, "value")
                            and self.authentication_type.value
                            and "cam_credentials" in str(self.authentication_type.value)
                        )
                        or ("cam_credentials" in str(self.authentication_type))
                    )
                )
            )
            else exclude.add("username")
        )
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        include.add("sl_location_id") if (not self.sl_connector_id) else exclude.add("sl_location_id")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
