from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import AZURE_COSMOS_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    entra_id = "entra_id"
    entra_id_user = "entra_id_user"
    master_key = "master_key"


class AzureCosmosConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "0c431748-2572-11ea-978f-2e728ce88125"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    authentication_method: AZURE_COSMOS_CONNECTION.AuthMethod | None = Field(
        AZURE_COSMOS_CONNECTION.AuthMethod.master_key, alias="auth_method"
    )
    client_id: str = Field(None, alias="client_id")
    client_secret: str = Field(None, alias="client_secret")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    hostname: str = Field(None, alias="host")
    master_key: str = Field(None, alias="master_key")
    password: str = Field(None, alias="password")
    port: int | None = Field(443, alias="port")
    tenant_id: str = Field(None, alias="tenant_id")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
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
            include.add("master_key")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "master_key"
                        )
                        or (self.authentication_method == "master_key")
                    )
                )
            )
            else exclude.add("master_key")
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

        include.add("authentication_method") if (not self.defer_credentials) else exclude.add("authentication_method")
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
            else exclude.add("tenant_id")
        )
        (
            include.add("client_id")
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
            else exclude.add("client_id")
        )
        (
            include.add("master_key")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "master_key")
                    or (self.authentication_method == "master_key")
                )
            )
            else exclude.add("master_key")
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
            else exclude.add("password")
        )
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
            else exclude.add("client_secret")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
