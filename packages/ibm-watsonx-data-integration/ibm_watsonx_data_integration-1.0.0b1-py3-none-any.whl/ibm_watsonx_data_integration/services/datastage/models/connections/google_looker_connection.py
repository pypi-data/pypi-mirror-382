from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class GoogleLookerConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "69857d6b-2be8-4a59-8a70-723405f09708"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    client_id: str = Field(None, alias="client_id")
    client_secret: str = Field(None, alias="client_secret")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    hostname_or_ip_address: str = Field(None, alias="host")
    port: int | None = Field(19999, alias="port")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("client_secret") if (not self.defer_credentials) else exclude.add("client_secret")
        include.add("client_id") if (not self.defer_credentials) else exclude.add("client_id")
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

        include.add("client_id") if (not self.defer_credentials) else exclude.add("client_id")
        include.add("client_secret") if (not self.defer_credentials) else exclude.add("client_secret")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
