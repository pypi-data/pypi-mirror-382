from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import COGNOS_ANALYTICS_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    anonymous = "anonymous"
    username_apikey_namespace_cpdca = "username_apikey_namespace_cpdca"
    username_password_namespace_cpdca = "username_password_namespace_cpdca"
    cognos_analytics_apikey = "cognos_analytics_apikey"
    username_password_namespace = "username_password_namespace"


class CognosAnalyticsConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "11f3029d-a1cf-4c4d-b8e7-64422fa54a94"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_physical_collection: str | None = Field(None, alias="_physical_collection")
    ds_port: str | None = Field(None, alias="_port")
    access_token: str = Field(None, alias="access_token")
    api_key: str = Field(None, alias="api_key")
    authentication_method: COGNOS_ANALYTICS_CONNECTION.AuthMethod | None = Field(None, alias="auth_method")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    use_my_platform_login_credentials: bool | None = Field(False, alias="inherit_access_token")
    namespace_id: str = Field(None, alias="namespace_id")
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
            include.add("access_token")
            if (
                ((not self.defer_credentials))
                and (not self.use_anonymous_access)
                and (not self.username)
                and (not self.namespace_id)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value != "anonymous"
                        )
                        or (self.authentication_method != "anonymous")
                    )
                )
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
                and (not self.use_anonymous_access)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "username_password_namespace"
                                )
                                or (self.authentication_method == "username_password_namespace")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "username_password_namespace_cpdca"
                            )
                            or (self.authentication_method == "username_password_namespace_cpdca")
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        include.add("authentication_method") if (not self.defer_credentials) else exclude.add("authentication_method")
        (
            include.add("namespace_id")
            if (
                ((not self.defer_credentials))
                and (not self.access_token)
                and (not self.use_my_platform_login_credentials)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "username_apikey_namespace_cpdca"
                                )
                                or (self.authentication_method == "username_apikey_namespace_cpdca")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "username_password_namespace"
                            )
                            or (self.authentication_method == "username_password_namespace")
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "username_password_namespace_cpdca"
                            )
                            or (self.authentication_method == "username_password_namespace_cpdca")
                        )
                    )
                )
            )
            else exclude.add("namespace_id")
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
                and (not self.access_token)
                and (not self.use_my_platform_login_credentials)
                and (not self.use_anonymous_access)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "cognos_analytics_apikey"
                                )
                                or (self.authentication_method == "cognos_analytics_apikey")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "username_apikey_namespace_cpdca"
                            )
                            or (self.authentication_method == "username_apikey_namespace_cpdca")
                        )
                    )
                )
            )
            else exclude.add("api_key")
        )
        (
            include.add("use_my_platform_login_credentials")
            if (
                ((not self.defer_credentials))
                and (not self.use_anonymous_access)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "username_password_namespace"
                        )
                        or (self.authentication_method == "username_password_namespace")
                    )
                )
            )
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
                and (not self.use_anonymous_access)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "username_apikey_namespace_cpdca"
                                )
                                or (self.authentication_method == "username_apikey_namespace_cpdca")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "username_password_namespace"
                            )
                            or (self.authentication_method == "username_password_namespace")
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "username_password_namespace_cpdca"
                            )
                            or (self.authentication_method == "username_password_namespace_cpdca")
                        )
                    )
                )
            )
            else exclude.add("username")
        )
        (
            include.add("use_anonymous_access")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "anonymous"
                        )
                        or (self.authentication_method == "anonymous")
                    )
                )
            )
            else exclude.add("use_anonymous_access")
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

        (
            include.add("satellite_connector_id")
            if (not self.secure_gateway_id) and (not self.satellite_location_id)
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("api_key")
            if (not self.defer_credentials)
            and (not self.access_token)
            and (self.use_my_platform_login_credentials != "yes")
            and (not self.use_anonymous_access)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "cognos_analytics_apikey" in str(self.authentication_method.value)
                    )
                    or ("cognos_analytics_apikey" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_apikey_namespace_cpdca" in str(self.authentication_method.value)
                    )
                    or ("username_apikey_namespace_cpdca" in str(self.authentication_method))
                )
            )
            else exclude.add("api_key")
        )
        include.add("authentication_method") if (not self.defer_credentials) else exclude.add("authentication_method")
        (
            include.add("use_my_platform_login_credentials")
            if (not self.defer_credentials)
            and (not self.use_anonymous_access)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "username_password_namespace"
                    )
                    or (self.authentication_method == "username_password_namespace")
                )
            )
            else exclude.add("use_my_platform_login_credentials")
        )
        (
            include.add("use_anonymous_access")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "anonymous")
                    or (self.authentication_method == "anonymous")
                )
            )
            else exclude.add("use_anonymous_access")
        )
        (
            include.add("access_token")
            if (not self.defer_credentials)
            and (not self.use_anonymous_access)
            and (not self.username)
            and (not self.namespace_id)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value != "anonymous")
                    or (self.authentication_method != "anonymous")
                )
            )
            and (self.use_my_platform_login_credentials == "yes")
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (not self.access_token)
            and (self.use_my_platform_login_credentials != "yes")
            and (not self.use_anonymous_access)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password_namespace" in str(self.authentication_method.value)
                    )
                    or ("username_password_namespace" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password_namespace_cpdca" in str(self.authentication_method.value)
                    )
                    or ("username_password_namespace_cpdca" in str(self.authentication_method))
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (not self.access_token)
            and (self.use_my_platform_login_credentials != "yes")
            and (not self.use_anonymous_access)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_apikey_namespace_cpdca" in str(self.authentication_method.value)
                    )
                    or ("username_apikey_namespace_cpdca" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password_namespace" in str(self.authentication_method.value)
                    )
                    or ("username_password_namespace" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password_namespace_cpdca" in str(self.authentication_method.value)
                    )
                    or ("username_password_namespace_cpdca" in str(self.authentication_method))
                )
            )
            else exclude.add("username")
        )
        (
            include.add("namespace_id")
            if (not self.defer_credentials)
            and (not self.access_token)
            and (self.use_my_platform_login_credentials != "yes")
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_apikey_namespace_cpdca" in str(self.authentication_method.value)
                    )
                    or ("username_apikey_namespace_cpdca" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password_namespace" in str(self.authentication_method.value)
                    )
                    or ("username_password_namespace" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password_namespace_cpdca" in str(self.authentication_method.value)
                    )
                    or ("username_password_namespace_cpdca" in str(self.authentication_method))
                )
            )
            else exclude.add("namespace_id")
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
