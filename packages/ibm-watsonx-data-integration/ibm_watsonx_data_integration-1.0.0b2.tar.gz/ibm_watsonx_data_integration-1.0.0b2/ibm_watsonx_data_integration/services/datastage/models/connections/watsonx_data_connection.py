from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import WATSONX_DATA_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    username_apikey = "username_apikey"
    username_password = "username_password"


class DeploymentType(Enum):
    software_dev = "software_dev"
    saas = "saas"
    software_ent = "software_ent"


class WatsonxDataConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "lakehouse"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    api_key: str = Field(None, alias="api_key")
    authentication_method: WATSONX_DATA_CONNECTION.AuthMethod | None = Field(
        WATSONX_DATA_CONNECTION.AuthMethod.username_password, alias="auth_method"
    )
    cloud_resource_name: str = Field(None, alias="cloud_resource_name")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    crn: str | None = Field(None, alias="crn")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    deployment_type: WATSONX_DATA_CONNECTION.DeploymentType | None = Field(None, alias="deployment_type")
    engine_hostname: str | None = Field(None, alias="engine_host")
    engine_id: str | None = Field(None, alias="engine_id")
    engine_port: int | None = Field(None, alias="engine_port")
    engine_ssl_enabled: bool | None = Field(None, alias="engine_ssl")
    engine_ssl_certificate: str | None = Field(None, alias="engine_ssl_certificate")
    hostname_or_ip_address: str = Field(None, alias="host")
    instance_id: str = Field(None, alias="instance_id")
    instance_name: str = Field(None, alias="instance_name")
    connect_to_ibm_watsonx_data_on_red_hat_open_shift: bool | None = Field(False, alias="is_cpd")
    password: str = Field(None, alias="password")
    port: int = Field(None, alias="port")
    service_to_service_authorization: bool | None = Field(None, alias="s2s")
    ssl_is_enabled: bool | None = Field(True, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
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
            if ((((not self.ssl_certificate_file))) and (self.ssl_is_enabled))
            else exclude.add("ssl_certificate")
        )
        include.add("engine_ssl_certificate") if (self.engine_ssl_enabled) else exclude.add("engine_ssl_certificate")
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    ((not self.api_key))
                    and (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value != "username_apikey"
                            )
                            or (self.authentication_method != "username_apikey")
                        )
                    )
                    and (
                        self.deployment_type
                        and (
                            (hasattr(self.deployment_type, "value") and self.deployment_type.value != "saas")
                            or (self.deployment_type != "saas")
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("authentication_method")
            if (
                ((self.connect_to_ibm_watsonx_data_on_red_hat_open_shift))
                or (
                    self.deployment_type
                    and (
                        (hasattr(self.deployment_type, "value") and self.deployment_type.value == "software_ent")
                        or (self.deployment_type == "software_ent")
                    )
                )
            )
            else exclude.add("authentication_method")
        )
        (
            include.add("instance_name")
            if (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and not self.deployment_type.value)
                    or (not self.deployment_type)
                )
            )
            else exclude.add("instance_name")
        )
        (
            include.add("instance_id")
            if (
                (
                    (
                        self.deployment_type
                        and (
                            (hasattr(self.deployment_type, "value") and not self.deployment_type.value)
                            or (not self.deployment_type)
                        )
                    )
                )
                or (
                    self.deployment_type
                    and (
                        (hasattr(self.deployment_type, "value") and self.deployment_type.value == "software_ent")
                        or (self.deployment_type == "software_ent")
                    )
                )
                or (
                    self.deployment_type
                    and (
                        (hasattr(self.deployment_type, "value") and self.deployment_type.value == "software_dev")
                        or (self.deployment_type == "software_dev")
                    )
                )
            )
            else exclude.add("instance_id")
        )
        (
            include.add("service_to_service_authorization")
            if (
                (
                    (
                        self.deployment_type
                        and (
                            (hasattr(self.deployment_type, "value") and self.deployment_type.value == "saas")
                            or (self.deployment_type == "saas")
                        )
                    )
                )
                and (not self.connect_to_ibm_watsonx_data_on_red_hat_open_shift)
            )
            else exclude.add("service_to_service_authorization")
        )
        (
            include.add("api_key")
            if (
                (
                    ((not self.password))
                    and (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value != "username_password"
                                )
                                or (self.authentication_method != "username_password")
                            )
                        )
                    )
                )
                and (
                    ((self.connect_to_ibm_watsonx_data_on_red_hat_open_shift))
                    or (
                        self.deployment_type
                        and (
                            (hasattr(self.deployment_type, "value") and self.deployment_type.value == "saas")
                            or (self.deployment_type == "saas")
                        )
                    )
                    or (
                        self.deployment_type
                        and (
                            (hasattr(self.deployment_type, "value") and self.deployment_type.value == "software_ent")
                            or (self.deployment_type == "software_ent")
                        )
                    )
                )
            )
            else exclude.add("api_key")
        )
        (
            include.add("cloud_resource_name")
            if (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and self.deployment_type.value == "saas")
                    or (self.deployment_type == "saas")
                )
            )
            else exclude.add("cloud_resource_name")
        )
        (
            include.add("connect_to_ibm_watsonx_data_on_red_hat_open_shift")
            if (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and not self.deployment_type.value)
                    or (not self.deployment_type)
                )
            )
            else exclude.add("connect_to_ibm_watsonx_data_on_red_hat_open_shift")
        )
        include.add("crn") if (not self.connect_to_ibm_watsonx_data_on_red_hat_open_shift) else exclude.add("crn")
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    self.deployment_type
                    and (
                        (hasattr(self.deployment_type, "value") and self.deployment_type.value != "saas")
                        or (self.deployment_type != "saas")
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
            include.add("instance_id")
            if (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and not self.deployment_type.value)
                    or (not self.deployment_type)
                )
            )
            or (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and self.deployment_type.value == "software_ent")
                    or (self.deployment_type == "software_ent")
                )
            )
            or (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and self.deployment_type.value == "software_dev")
                    or (self.deployment_type == "software_dev")
                )
            )
            else exclude.add("instance_id")
        )
        (
            include.add("api_key")
            if (
                (not self.password)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value != "username_password"
                        )
                        or (self.authentication_method != "username_password")
                    )
                )
            )
            and (
                (
                    self.connect_to_ibm_watsonx_data_on_red_hat_open_shift == "true"
                    or self.connect_to_ibm_watsonx_data_on_red_hat_open_shift
                )
                or (
                    self.deployment_type
                    and (
                        (hasattr(self.deployment_type, "value") and self.deployment_type.value == "saas")
                        or (self.deployment_type == "saas")
                    )
                )
                or (
                    self.deployment_type
                    and (
                        (hasattr(self.deployment_type, "value") and self.deployment_type.value == "software_ent")
                        or (self.deployment_type == "software_ent")
                    )
                )
            )
            else exclude.add("api_key")
        )
        (
            include.add("authentication_method")
            if (
                self.connect_to_ibm_watsonx_data_on_red_hat_open_shift == "true"
                or self.connect_to_ibm_watsonx_data_on_red_hat_open_shift
            )
            or (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and self.deployment_type.value == "software_ent")
                    or (self.deployment_type == "software_ent")
                )
            )
            else exclude.add("authentication_method")
        )
        (
            include.add("cloud_resource_name")
            if (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and self.deployment_type.value == "saas")
                    or (self.deployment_type == "saas")
                )
            )
            else exclude.add("cloud_resource_name")
        )
        (
            include.add("service_to_service_authorization")
            if (
                (
                    self.deployment_type
                    and (
                        (hasattr(self.deployment_type, "value") and self.deployment_type.value == "saas")
                        or (self.deployment_type == "saas")
                    )
                )
                and (not self.connect_to_ibm_watsonx_data_on_red_hat_open_shift)
            )
            else exclude.add("service_to_service_authorization")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.ssl_is_enabled == "true" or self.ssl_is_enabled)
            else exclude.add("ssl_certificate_file")
        )
        (
            include.add("connect_to_ibm_watsonx_data_on_red_hat_open_shift")
            if (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and not self.deployment_type.value)
                    or (not self.deployment_type)
                )
            )
            else exclude.add("connect_to_ibm_watsonx_data_on_red_hat_open_shift")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                (not self.api_key)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value != "username_apikey"
                        )
                        or (self.authentication_method != "username_apikey")
                    )
                )
                and (
                    self.deployment_type
                    and (
                        (hasattr(self.deployment_type, "value") and self.deployment_type.value != "saas")
                        or (self.deployment_type != "saas")
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("engine_ssl_certificate")
            if (self.engine_ssl_enabled == "true" or self.engine_ssl_enabled)
            else exclude.add("engine_ssl_certificate")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and self.deployment_type.value != "saas")
                    or (self.deployment_type != "saas")
                )
            )
            else exclude.add("username")
        )
        (
            include.add("crn")
            if (
                self.connect_to_ibm_watsonx_data_on_red_hat_open_shift == "false"
                or not self.connect_to_ibm_watsonx_data_on_red_hat_open_shift
            )
            else exclude.add("crn")
        )
        (
            include.add("instance_name")
            if (
                self.deployment_type
                and (
                    (hasattr(self.deployment_type, "value") and not self.deployment_type.value)
                    or (not self.deployment_type)
                )
            )
            else exclude.add("instance_name")
        )
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.ssl_is_enabled == "true" or self.ssl_is_enabled)
            else exclude.add("ssl_certificate")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
