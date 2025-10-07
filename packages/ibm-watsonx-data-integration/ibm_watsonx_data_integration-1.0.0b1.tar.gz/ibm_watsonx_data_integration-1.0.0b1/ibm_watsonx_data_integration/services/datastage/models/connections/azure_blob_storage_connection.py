from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import AZURE_BLOB_STORAGE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    connection_string = "connection_string"
    entra_id = "entra_id"
    entra_id_user = "entra_id_user"


class AzureBlobStorageConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "9a22e0af-8d19-4c4e-9aea-1d733e81315b"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    authentication_method: AZURE_BLOB_STORAGE_CONNECTION.AuthMethod | None = Field(
        AZURE_BLOB_STORAGE_CONNECTION.AuthMethod.connection_string, alias="auth_method"
    )
    cas_api_key: str = Field(None, alias="cas_api_key")
    cas_endpoint: str = Field(None, alias="cas_endpoint")
    cas_instance_id: str = Field(None, alias="cas_instance_id")
    catalog_name: str | None = Field(None, alias="catalog_name")
    client_id: str = Field(None, alias="client_id")
    client_secret: str = Field(None, alias="client_secret")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    connection_string: str = Field(None, alias="connection_string")
    container: str | None = Field(None, alias="container")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    mds_rest_endpoint: str | None = Field(None, alias="mds_rest_endpoint")
    password: str = Field(None, alias="password")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    storage_account_url: str = Field(None, alias="storage_account_url")
    tenant_id: str = Field(None, alias="tenant_id")
    use_watsonx_credential_provider: bool | None = Field(None, alias="use_watsonx_credential_provider")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("tenant_id")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "entra_id"
                        )
                        or (self.authentication_method == "entra_id")
                    )
                )
                and (not self.use_watsonx_credential_provider)
            )
            else exclude.add("tenant_id")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "entra_id_user"
                        )
                        or (self.authentication_method == "entra_id_user")
                    )
                )
                and (not self.use_watsonx_credential_provider)
            )
            else exclude.add("password")
        )
        (
            include.add("authentication_method")
            if (((not self.defer_credentials)) and (not self.use_watsonx_credential_provider))
            else exclude.add("authentication_method")
        )
        include.add("cas_api_key") if (self.use_watsonx_credential_provider) else exclude.add("cas_api_key")
        include.add("cas_instance_id") if (self.use_watsonx_credential_provider) else exclude.add("cas_instance_id")
        (
            include.add("storage_account_url")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "entra_id"
                                )
                                or (self.authentication_method == "entra_id")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "entra_id_user"
                            )
                            or (self.authentication_method == "entra_id_user")
                        )
                    )
                )
                and (not self.use_watsonx_credential_provider)
            )
            else exclude.add("storage_account_url")
        )
        (
            include.add("client_secret")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "entra_id"
                        )
                        or (self.authentication_method == "entra_id")
                    )
                )
                and (not self.use_watsonx_credential_provider)
            )
            else exclude.add("client_secret")
        )
        include.add("cas_endpoint") if (self.use_watsonx_credential_provider) else exclude.add("cas_endpoint")
        (
            include.add("connection_string")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "connection_string"
                        )
                        or (self.authentication_method == "connection_string")
                    )
                )
                and (not self.use_watsonx_credential_provider)
            )
            else exclude.add("connection_string")
        )
        (
            include.add("client_id")
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
                                        and self.authentication_method.value == "ami"
                                    )
                                    or (self.authentication_method == "ami")
                                )
                            )
                        )
                        or (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "entra_id"
                                    )
                                    or (self.authentication_method == "entra_id")
                                )
                            )
                        )
                        or (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "entra_id_user"
                                    )
                                    or (self.authentication_method == "entra_id_user")
                                )
                            )
                        )
                    )
                    and ((not self.use_watsonx_credential_provider))
                )
                or (
                    ((not self.defer_credentials))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "entra_id"
                                    )
                                    or (self.authentication_method == "entra_id")
                                )
                            )
                        )
                        or (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "entra_id_user"
                                )
                                or (self.authentication_method == "entra_id_user")
                            )
                        )
                    )
                    and (not self.use_watsonx_credential_provider)
                )
            )
            else exclude.add("client_id")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "entra_id_user"
                        )
                        or (self.authentication_method == "entra_id_user")
                    )
                )
                and (not self.use_watsonx_credential_provider)
            )
            else exclude.add("username")
        )
        (
            include.add("tenant_id")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "entra_id"
                        )
                        or (self.authentication_method == "entra_id")
                    )
                )
            )
            else exclude.add("tenant_id")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "entra_id_user"
                        )
                        or (self.authentication_method == "entra_id_user")
                    )
                )
            )
            else exclude.add("password")
        )
        include.add("authentication_method") if (not self.defer_credentials) else exclude.add("authentication_method")
        (
            include.add("storage_account_url")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "entra_id"
                                )
                                or (self.authentication_method == "entra_id")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "entra_id_user"
                            )
                            or (self.authentication_method == "entra_id_user")
                        )
                    )
                )
            )
            else exclude.add("storage_account_url")
        )
        (
            include.add("client_secret")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "entra_id"
                        )
                        or (self.authentication_method == "entra_id")
                    )
                )
            )
            else exclude.add("client_secret")
        )
        (
            include.add("connection_string")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "connection_string"
                        )
                        or (self.authentication_method == "connection_string")
                    )
                )
            )
            else exclude.add("connection_string")
        )
        (
            include.add("client_id")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "entra_id"
                                )
                                or (self.authentication_method == "entra_id")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "entra_id_user"
                            )
                            or (self.authentication_method == "entra_id_user")
                        )
                    )
                )
            )
            else exclude.add("client_id")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "entra_id_user"
                        )
                        or (self.authentication_method == "entra_id_user")
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

        (
            include.add("storage_account_url")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "entra_id" in str(self.authentication_method.value)
                    )
                    or ("entra_id" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "entra_id_user" in str(self.authentication_method.value)
                    )
                    or ("entra_id_user" in str(self.authentication_method))
                )
            )
            and (not self.use_watsonx_credential_provider)
            else exclude.add("storage_account_url")
        )
        include.add("cas_api_key") if (self.use_watsonx_credential_provider) else exclude.add("cas_api_key")
        (
            include.add("authentication_method")
            if (not self.defer_credentials) and (not self.use_watsonx_credential_provider)
            else exclude.add("authentication_method")
        )
        include.add("cas_endpoint") if (self.use_watsonx_credential_provider) else exclude.add("cas_endpoint")
        (
            include.add("tenant_id")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "entra_id")
                    or (self.authentication_method == "entra_id")
                )
            )
            and (not self.use_watsonx_credential_provider)
            else exclude.add("tenant_id")
        )
        (
            include.add("client_id")
            if (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "ami" in str(self.authentication_method.value)
                        )
                        or ("ami" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "entra_id" in str(self.authentication_method.value)
                        )
                        or ("entra_id" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "entra_id_user" in str(self.authentication_method.value)
                        )
                        or ("entra_id_user" in str(self.authentication_method))
                    )
                )
                and (not self.use_watsonx_credential_provider)
            )
            or (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "entra_id" in str(self.authentication_method.value)
                        )
                        or ("entra_id" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "entra_id_user" in str(self.authentication_method.value)
                        )
                        or ("entra_id_user" in str(self.authentication_method))
                    )
                )
                and (not self.use_watsonx_credential_provider)
            )
            else exclude.add("client_id")
        )
        (
            include.add("connection_string")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "connection_string"
                    )
                    or (self.authentication_method == "connection_string")
                )
            )
            and (not self.use_watsonx_credential_provider)
            else exclude.add("connection_string")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "entra_id_user"
                    )
                    or (self.authentication_method == "entra_id_user")
                )
            )
            and (not self.use_watsonx_credential_provider)
            else exclude.add("password")
        )
        include.add("cas_instance_id") if (self.use_watsonx_credential_provider) else exclude.add("cas_instance_id")
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "entra_id_user"
                    )
                    or (self.authentication_method == "entra_id_user")
                )
            )
            and (not self.use_watsonx_credential_provider)
            else exclude.add("username")
        )
        (
            include.add("client_secret")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "entra_id")
                    or (self.authentication_method == "entra_id")
                )
            )
            and (not self.use_watsonx_credential_provider)
            else exclude.add("client_secret")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
