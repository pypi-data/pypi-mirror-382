from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class MinioConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "81641c94-a3a7-4d3e-9ea8-bdf79bdd3b06"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    access_key: str = Field(None, alias="access_key")
    bucket: str | None = Field(None, alias="bucket")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    secret_key: str = Field(None, alias="secret_key")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    url: str = Field(None, alias="url")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        include.add("secret_key") if (not self.defer_credentials) else exclude.add("secret_key")
        include.add("access_key") if (not self.defer_credentials) else exclude.add("access_key")
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
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        include.add("secret_key") if (not self.defer_credentials) else exclude.add("secret_key")
        include.add("ssl_certificate_file") if (not self.ssl_certificate) else exclude.add("ssl_certificate_file")
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        include.add("access_key") if (not self.defer_credentials) else exclude.add("access_key")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
