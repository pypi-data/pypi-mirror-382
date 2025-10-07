from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import AMAZONS3_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    basic_credentials = "basic_credentials"
    temporary_credentials = "temporary_credentials"
    trusted_role_credentials = "trusted_role_credentials"


class Amazons3Conn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "a0b1d14a-4767-404c-aac1-4ce0e62818c3"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    access_key: str | None = Field(None, alias="access_key")
    bucket: str | None = Field(None, alias="bucket")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    proxy: bool | None = Field(False, alias="proxy")
    proxy_host: str = Field(None, alias="proxy_host")
    proxy_password: str | None = Field(None, alias="proxy_password")
    proxy_port: int = Field(None, alias="proxy_port")
    proxy_username: str | None = Field(None, alias="proxy_user")
    region: str | None = Field(None, alias="region")
    secret_key: str = Field(None, alias="secret_key")
    url: str | None = Field(None, alias="url")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    authentication_method: AMAZONS3_CONNECTION.AuthMethod | None = Field(None, alias="auth_method")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    duration_seconds: int | None = Field(None, alias="duration_seconds")
    external_id: str | None = Field(None, alias="external_id")
    role_arn: str | None = Field(None, alias="role_arn")
    role_session_name: str = Field(None, alias="role_session_name")
    session_token: str | None = Field(None, alias="session_token")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        (
            include.add("secret_key")
            if (
                (((not self.defer_credentials)) and ((self.access_key)))
                or (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "basic_credentials"
                                )
                                or (self.authentication_method == "basic_credentials")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "temporary_credentials"
                            )
                            or (self.authentication_method == "temporary_credentials")
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "trusted_role_credentials"
                            )
                            or (self.authentication_method == "trusted_role_credentials")
                        )
                    )
                )
            )
            else exclude.add("secret_key")
        )
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        (
            include.add("access_key")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "basic_credentials"
                                )
                                or (self.authentication_method == "basic_credentials")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "temporary_credentials"
                            )
                            or (self.authentication_method == "temporary_credentials")
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "trusted_role_credentials"
                            )
                            or (self.authentication_method == "trusted_role_credentials")
                        )
                    )
                )
            )
            else exclude.add("access_key")
        )
        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        (
            include.add("session_token")
            if (
                (
                    ((not self.defer_credentials))
                    and ((self.access_key))
                    and ((not self.role_arn))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "temporary_credentials"
                                    )
                                    or (self.authentication_method == "temporary_credentials")
                                )
                            )
                        )
                    )
                )
                or (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "temporary_credentials"
                        )
                        or (self.authentication_method == "temporary_credentials")
                    )
                )
            )
            else exclude.add("session_token")
        )
        (
            include.add("duration_seconds")
            if (
                (
                    ((not self.defer_credentials))
                    and ((self.role_arn))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "trusted_role_credentials"
                                    )
                                    or (self.authentication_method == "trusted_role_credentials")
                                )
                            )
                        )
                    )
                )
                or (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "trusted_role_credentials"
                        )
                        or (self.authentication_method == "trusted_role_credentials")
                    )
                )
            )
            else exclude.add("duration_seconds")
        )
        (
            include.add("role_arn")
            if (
                (
                    ((not self.defer_credentials))
                    and ((self.access_key))
                    and ((not self.session_token))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "trusted_role_credentials"
                                    )
                                    or (self.authentication_method == "trusted_role_credentials")
                                )
                            )
                        )
                    )
                )
                or (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "trusted_role_credentials"
                        )
                        or (self.authentication_method == "trusted_role_credentials")
                    )
                )
            )
            else exclude.add("role_arn")
        )
        (
            include.add("role_session_name")
            if (
                (
                    ((not self.defer_credentials))
                    and ((self.role_arn))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "trusted_role_credentials"
                                    )
                                    or (self.authentication_method == "trusted_role_credentials")
                                )
                            )
                        )
                    )
                )
                or (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "trusted_role_credentials"
                        )
                        or (self.authentication_method == "trusted_role_credentials")
                    )
                )
            )
            else exclude.add("role_session_name")
        )
        (
            include.add("external_id")
            if (
                (
                    ((not self.defer_credentials))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "trusted_role_credentials"
                                    )
                                    or (self.authentication_method == "trusted_role_credentials")
                                )
                            )
                        )
                    )
                )
                or (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "trusted_role_credentials"
                        )
                        or (self.authentication_method == "trusted_role_credentials")
                    )
                )
            )
            else exclude.add("external_id")
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
            include.add("role_arn")
            if (
                (not self.defer_credentials)
                and (self.access_key)
                and (not self.session_token)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "trusted_role_credentials" in str(self.authentication_method.value)
                        )
                        or ("trusted_role_credentials" in str(self.authentication_method))
                    )
                )
            )
            or (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "trusted_role_credentials" in str(self.authentication_method.value)
                    )
                    or ("trusted_role_credentials" in str(self.authentication_method))
                )
            )
            else exclude.add("role_arn")
        )
        (
            include.add("duration_seconds")
            if (
                (not self.defer_credentials)
                and (self.role_arn)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "trusted_role_credentials" in str(self.authentication_method.value)
                        )
                        or ("trusted_role_credentials" in str(self.authentication_method))
                    )
                )
            )
            or (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "trusted_role_credentials" in str(self.authentication_method.value)
                    )
                    or ("trusted_role_credentials" in str(self.authentication_method))
                )
            )
            else exclude.add("duration_seconds")
        )
        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
        (
            include.add("secret_key")
            if ((not self.defer_credentials) and (self.access_key))
            or (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "basic_credentials" in str(self.authentication_method.value)
                    )
                    or ("basic_credentials" in str(self.authentication_method))
                )
                or self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "temporary_credentials" in str(self.authentication_method.value)
                    )
                    or ("temporary_credentials" in str(self.authentication_method))
                )
                or self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "trusted_role_credentials" in str(self.authentication_method.value)
                    )
                    or ("trusted_role_credentials" in str(self.authentication_method))
                )
            )
            else exclude.add("secret_key")
        )
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        (
            include.add("role_session_name")
            if (
                (not self.defer_credentials)
                and (self.role_arn)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "trusted_role_credentials" in str(self.authentication_method.value)
                        )
                        or ("trusted_role_credentials" in str(self.authentication_method))
                    )
                )
            )
            or (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "trusted_role_credentials" in str(self.authentication_method.value)
                    )
                    or ("trusted_role_credentials" in str(self.authentication_method))
                )
            )
            else exclude.add("role_session_name")
        )
        (
            include.add("session_token")
            if (
                (not self.defer_credentials)
                and (self.access_key)
                and (not self.role_arn)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "temporary_credentials" in str(self.authentication_method.value)
                        )
                        or ("temporary_credentials" in str(self.authentication_method))
                    )
                )
            )
            or (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "temporary_credentials" in str(self.authentication_method.value)
                    )
                    or ("temporary_credentials" in str(self.authentication_method))
                )
            )
            else exclude.add("session_token")
        )
        (
            include.add("external_id")
            if (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "trusted_role_credentials" in str(self.authentication_method.value)
                        )
                        or ("trusted_role_credentials" in str(self.authentication_method))
                    )
                )
            )
            or (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "trusted_role_credentials" in str(self.authentication_method.value)
                    )
                    or ("trusted_role_credentials" in str(self.authentication_method))
                )
            )
            else exclude.add("external_id")
        )
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        (
            include.add("access_key")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "basic_credentials" in str(self.authentication_method.value)
                    )
                    or ("basic_credentials" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "temporary_credentials" in str(self.authentication_method.value)
                    )
                    or ("temporary_credentials" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "trusted_role_credentials" in str(self.authentication_method.value)
                    )
                    or ("trusted_role_credentials" in str(self.authentication_method))
                )
            )
            else exclude.add("access_key")
        )
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
