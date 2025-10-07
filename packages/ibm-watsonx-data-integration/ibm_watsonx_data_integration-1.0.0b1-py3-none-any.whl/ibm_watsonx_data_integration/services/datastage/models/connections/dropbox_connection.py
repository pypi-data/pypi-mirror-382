from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import DROPBOX_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    accesstoken = "accesstoken"
    refreshtoken = "refreshtoken"


class DropboxConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "507b850c-f4a1-41d7-ad64-4182a1264014"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    access_token: str = Field(None, alias="access_token")
    app_key_client_id: str = Field(None, alias="app_key")
    app_secret_client_secret: str = Field(None, alias="app_secret")
    authentication_method: DROPBOX_CONNECTION.AuthMethod | None = Field(
        DROPBOX_CONNECTION.AuthMethod.accesstoken, alias="auth_method"
    )
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    refresh_token: str = Field(None, alias="refresh_token")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("access_token")
            if (
                ((not self.refresh_token))
                and (not self.app_key_client_id)
                and (not self.app_secret_client_secret)
                and (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "accesstoken"
                        )
                        or (self.authentication_method == "accesstoken")
                    )
                )
            )
            else exclude.add("access_token")
        )
        (
            include.add("refresh_token")
            if (
                ((not self.access_token))
                and (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "refreshtoken"
                        )
                        or (self.authentication_method == "refreshtoken")
                    )
                )
            )
            else exclude.add("refresh_token")
        )
        (
            include.add("app_key_client_id")
            if (
                ((not self.access_token))
                and (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "refreshtoken"
                        )
                        or (self.authentication_method == "refreshtoken")
                    )
                )
            )
            else exclude.add("app_key_client_id")
        )
        (
            include.add("app_secret_client_secret")
            if (
                ((not self.access_token))
                and (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "refreshtoken"
                        )
                        or (self.authentication_method == "refreshtoken")
                    )
                )
            )
            else exclude.add("app_secret_client_secret")
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
            include.add("app_secret_client_secret")
            if (not self.access_token)
            and (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "refreshtoken" in str(self.authentication_method.value)
                    )
                    or ("refreshtoken" in str(self.authentication_method))
                )
            )
            else exclude.add("app_secret_client_secret")
        )
        (
            include.add("app_key_client_id")
            if (not self.access_token)
            and (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "refreshtoken" in str(self.authentication_method.value)
                    )
                    or ("refreshtoken" in str(self.authentication_method))
                )
            )
            else exclude.add("app_key_client_id")
        )
        (
            include.add("access_token")
            if (not self.refresh_token)
            and (not self.app_key_client_id)
            and (not self.app_secret_client_secret)
            and (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "accesstoken" in str(self.authentication_method.value)
                    )
                    or ("accesstoken" in str(self.authentication_method))
                )
            )
            else exclude.add("access_token")
        )
        (
            include.add("refresh_token")
            if (not self.access_token)
            and (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "refreshtoken" in str(self.authentication_method.value)
                    )
                    or ("refreshtoken" in str(self.authentication_method))
                )
            )
            else exclude.add("refresh_token")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
