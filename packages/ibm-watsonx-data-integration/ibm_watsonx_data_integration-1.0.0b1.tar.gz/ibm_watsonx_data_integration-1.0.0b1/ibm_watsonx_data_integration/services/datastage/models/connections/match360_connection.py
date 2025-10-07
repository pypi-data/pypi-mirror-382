from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class Match360Conn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "99265578-2e54-4b6b-baea-3058fc2ecc96"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    api_key: str = Field(None, alias="api_key")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    cpd_user: str | None = Field(None, alias="cpd_user")
    crn: str | None = Field(None, alias="crn")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    gateway_url: str | None = Field(None, alias="gateway_url")
    iam_url: str | None = Field(None, alias="iam_url")
    mdm_instance_id: str | None = Field(None, alias="mdm_instance_id")
    route_host: str | None = Field(None, alias="route_host")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("api_key") if (not self.defer_credentials) else exclude.add("api_key")
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
        include.add("mdm_instance_id") if (self.hidden_dummy_property1) else exclude.add("mdm_instance_id")
        include.add("cpd_user") if (self.hidden_dummy_property1) else exclude.add("cpd_user")
        include.add("route_host") if (self.hidden_dummy_property1) else exclude.add("route_host")

        include.add("api_key") if (not self.defer_credentials) else exclude.add("api_key")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
