from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import AZURE_DATABRICKS_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    entra_id = "entra_id"
    oauth_m2m = "oauth_m2m"
    userpass = "userpass"


class AzureDatabricksConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "d6cd87ca-ec13-11ee-a951-0242ac120002"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    authentication_method: AZURE_DATABRICKS_CONNECTION.AuthMethod | None = Field(None, alias="auth_method")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    microsoft_entra_id_token: str | None = Field(None, alias="entra_id_token")
    hostname_or_ip_address: str = Field(None, alias="host")
    http_path: str | None = Field(None, alias="http_path")
    client_id_of_service_principal: str = Field(None, alias="oauth_m2m_client_id")
    client_secret_of_service_principal: str = Field(None, alias="oauth_m2m_client_secret")
    password: str = Field(None, alias="password")
    port: int = Field(None, alias="port")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("microsoft_entra_id_token")
            if (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "entra_id")
                    or (self.authentication_method == "entra_id")
                )
            )
            else exclude.add("microsoft_entra_id_token")
        )
        (
            include.add("password")
            if (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "userpass")
                    or (self.authentication_method == "userpass")
                )
            )
            else exclude.add("password")
        )
        (
            include.add("client_id_of_service_principal")
            if (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "oauth_m2m")
                    or (self.authentication_method == "oauth_m2m")
                )
            )
            else exclude.add("client_id_of_service_principal")
        )
        (
            include.add("client_secret_of_service_principal")
            if (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "oauth_m2m")
                    or (self.authentication_method == "oauth_m2m")
                )
            )
            else exclude.add("client_secret_of_service_principal")
        )
        (
            include.add("username")
            if (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "userpass")
                    or (self.authentication_method == "userpass")
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

        (
            include.add("client_id_of_service_principal")
            if (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "oauth_m2m" in str(self.authentication_method.value)
                    )
                    or ("oauth_m2m" in str(self.authentication_method))
                )
            )
            else exclude.add("client_id_of_service_principal")
        )
        (
            include.add("password")
            if (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "userpass" in str(self.authentication_method.value)
                    )
                    or ("userpass" in str(self.authentication_method))
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "userpass" in str(self.authentication_method.value)
                    )
                    or ("userpass" in str(self.authentication_method))
                )
            )
            else exclude.add("username")
        )
        (
            include.add("microsoft_entra_id_token")
            if (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "entra_id" in str(self.authentication_method.value)
                    )
                    or ("entra_id" in str(self.authentication_method))
                )
            )
            else exclude.add("microsoft_entra_id_token")
        )
        (
            include.add("client_secret_of_service_principal")
            if (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "oauth_m2m" in str(self.authentication_method.value)
                    )
                    or ("oauth_m2m" in str(self.authentication_method))
                )
            )
            else exclude.add("client_secret_of_service_principal")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
