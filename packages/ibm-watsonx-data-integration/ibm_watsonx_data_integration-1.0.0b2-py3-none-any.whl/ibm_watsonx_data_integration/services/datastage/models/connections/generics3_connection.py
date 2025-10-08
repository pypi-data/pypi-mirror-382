from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import GENERICS3_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class ListObjectsApiVersion(Enum):
    v1 = "v1"
    v2 = "v2"


class Generics3Conn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "38714ac2-8f66-4a8c-9b40-806ffb61c759"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    access_key: str = Field(None, alias="access_key")
    bucket: str | None = Field(None, alias="bucket")
    das_api_key: str = Field(None, alias="cas_api_key")
    das_endpoint: str = Field(None, alias="cas_endpoint")
    das_instance_id: str = Field(None, alias="cas_instance_id")
    catalog_name: str | None = Field(None, alias="catalog_name")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    disable_chunked_encoding: bool | None = Field(False, alias="disable_chunked_encoding")
    enable_global_bucket_access: bool | None = Field(True, alias="enable_global_bucket_access")
    enable_path_style_access: bool | None = Field(None, alias="enable_path_style_access")
    s3_list_objects_version: GENERICS3_CONNECTION.ListObjectsApiVersion | None = Field(
        GENERICS3_CONNECTION.ListObjectsApiVersion.v1, alias="list_objects_api_version"
    )
    iceberg_rest_catalog_endpoint: str | None = Field(None, alias="mds_rest_endpoint")
    region: str | None = Field(None, alias="region")
    secret_key: str = Field(None, alias="secret_key")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    trust_all_ssl_certificates: bool | None = Field(False, alias="trust_all_ssl_cert")
    url: str = Field(None, alias="url")
    use_watsonx_credential_provider: bool | None = Field(None, alias="use_watsonx_credential_provider")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        (
            include.add("secret_key")
            if (((not self.defer_credentials)) and (not self.use_watsonx_credential_provider))
            else exclude.add("secret_key")
        )
        include.add("das_api_key") if (self.use_watsonx_credential_provider) else exclude.add("das_api_key")
        (
            include.add("access_key")
            if (((not self.defer_credentials)) and (not self.use_watsonx_credential_provider))
            else exclude.add("access_key")
        )
        include.add("das_instance_id") if (self.use_watsonx_credential_provider) else exclude.add("das_instance_id")
        include.add("das_endpoint") if (self.use_watsonx_credential_provider) else exclude.add("das_endpoint")
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

        include.add("das_api_key") if (self.use_watsonx_credential_provider) else exclude.add("das_api_key")
        (
            include.add("secret_key")
            if (not self.defer_credentials) and (not self.use_watsonx_credential_provider)
            else exclude.add("secret_key")
        )
        include.add("das_endpoint") if (self.use_watsonx_credential_provider) else exclude.add("das_endpoint")
        include.add("ssl_certificate_file") if (not self.ssl_certificate) else exclude.add("ssl_certificate_file")
        include.add("das_instance_id") if (self.use_watsonx_credential_provider) else exclude.add("das_instance_id")
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        (
            include.add("access_key")
            if (not self.defer_credentials) and (not self.use_watsonx_credential_provider)
            else exclude.add("access_key")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
