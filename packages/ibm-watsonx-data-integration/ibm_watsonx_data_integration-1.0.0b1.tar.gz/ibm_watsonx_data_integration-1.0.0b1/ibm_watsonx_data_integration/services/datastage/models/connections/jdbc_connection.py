from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import JDBC_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class RowLimitSupport(Enum):
    none = "none"
    prefix = "prefix"
    suffix = "suffix"


class JdbcConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "e59b1c36-6f30-4879-9f74-7e81dde4cca6"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    allow_filter_pushdown: bool | None = Field(None, alias="allow_push_filters")
    batch_size: int | None = Field(None, alias="batch_size")
    case_sensitive_ids: bool | None = Field(None, alias="case_sensitive_ids")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    fetch_size: int | None = Field(None, alias="fetch_size")
    gateway_url: str | None = Field(None, alias="gateway_url")
    jdbc_driver_files: str | None = Field(None, alias="jar_uris")
    jdbc_driver_class: str = Field(None, alias="jdbc_driver")
    jdbc_properties: str | None = Field(None, alias="jdbc_properties")
    jdbc_url: str = Field(None, alias="jdbc_url")
    password: str | None = Field(None, alias="password")
    row_limit_prefix: str | None = Field(None, alias="row_limit_prefix")
    row_limit_suffix: str | None = Field(None, alias="row_limit_suffix")
    row_limit_support: JDBC_CONNECTION.RowLimitSupport | None = Field(None, alias="row_limit_support")
    secure_gateway_id: str | None = Field(None, alias="sg_gateway_id")
    sg_host_original: str | None = Field(None, alias="sg_host_original")
    secure_gateway_as_http_proxy: bool | None = Field(None, alias="sg_http_proxy")
    secure_gateway_security_token: str | None = Field(None, alias="sg_security_token")
    secure_gateway_service_url: str | None = Field(None, alias="sg_service_url")
    port_is_ssl_enabled: bool | None = Field(False, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    table_types: str | None = Field(None, alias="table_types")
    trust_all_ssl_certificates: bool | None = Field(False, alias="trust_all_ssl_cert")
    username: str | None = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    auto_commit_in_metadata_discovery: bool | None = Field(None, alias="auto_commit_discovery")
    connector_uses_catalog_structure: bool | None = Field(False, alias="catalog_support")
    satellite_client_certificate: str | None = Field(None, alias="sl_client_cert")
    satellite_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    satellite_connector_id: str | None = Field(None, alias="sl_connector_id")
    satellite_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    satellite_endpoint_display_name: str | None = Field(None, alias="sl_endpoint_name")
    satellite_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    sl_host_original: str | None = Field(None, alias="sl_host_original")
    satellite_as_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    satellite_location_id: str | None = Field(None, alias="sl_location_id")
    satellite_service_url: str | None = Field(None, alias="sl_service_url")
    use_column_name_in_the_statements: bool | None = Field(None, alias="use_column_name")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("ssl_certificate")
            if ((((not self.ssl_certificate_file))) and (self.port_is_ssl_enabled))
            else exclude.add("ssl_certificate")
        )
        (
            include.add("row_limit_suffix")
            if (
                self.row_limit_support
                and (
                    (hasattr(self.row_limit_support, "value") and self.row_limit_support.value == "suffix")
                    or (self.row_limit_support == "suffix")
                )
            )
            else exclude.add("row_limit_suffix")
        )
        (
            include.add("row_limit_prefix")
            if (
                self.row_limit_support
                and (
                    (hasattr(self.row_limit_support, "value") and self.row_limit_support.value == "prefix")
                    or (self.row_limit_support == "prefix")
                )
            )
            else exclude.add("row_limit_prefix")
        )
        (
            include.add("satellite_connector_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_location_id))
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("satellite_location_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_connector_id))
            else exclude.add("satellite_location_id")
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
        (
            include.add("satellite_client_certificate")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_client_certificate")
        )
        (
            include.add("secure_gateway_service_url")
            if (self.hidden_dummy_property1)
            else exclude.add("secure_gateway_service_url")
        )
        include.add("sl_host_original") if (self.hidden_dummy_property1) else exclude.add("sl_host_original")
        (
            include.add("satellite_client_private_key")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_client_private_key")
        )
        (
            include.add("satellite_connector_id")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_connector_id")
        )
        include.add("sg_host_original") if (self.hidden_dummy_property1) else exclude.add("sg_host_original")
        (
            include.add("secure_gateway_as_http_proxy")
            if (self.hidden_dummy_property1)
            else exclude.add("secure_gateway_as_http_proxy")
        )
        include.add("secure_gateway_id") if (self.hidden_dummy_property1) else exclude.add("secure_gateway_id")
        (
            include.add("secure_gateway_security_token")
            if (self.hidden_dummy_property1)
            else exclude.add("secure_gateway_security_token")
        )
        include.add("satellite_service_url") if (self.hidden_dummy_property1) else exclude.add("satellite_service_url")
        (
            include.add("satellite_endpoint_display_name")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_endpoint_display_name")
        )
        (
            include.add("satellite_endpoint_host")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_endpoint_host")
        )
        (
            include.add("satellite_endpoint_port")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_endpoint_port")
        )
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")
        (
            include.add("satellite_as_http_proxy")
            if (self.hidden_dummy_property1)
            else exclude.add("satellite_as_http_proxy")
        )
        include.add("satellite_location_id") if (self.hidden_dummy_property1) else exclude.add("satellite_location_id")

        (
            include.add("row_limit_prefix")
            if (
                self.row_limit_support
                and (
                    (
                        hasattr(self.row_limit_support, "value")
                        and self.row_limit_support.value
                        and "prefix" in str(self.row_limit_support.value)
                    )
                    or ("prefix" in str(self.row_limit_support))
                )
            )
            else exclude.add("row_limit_prefix")
        )
        (
            include.add("satellite_connector_id")
            if (not self.secure_gateway_id) and (not self.satellite_location_id)
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("row_limit_suffix")
            if (
                self.row_limit_support
                and (
                    (
                        hasattr(self.row_limit_support, "value")
                        and self.row_limit_support.value
                        and "suffix" in str(self.row_limit_support.value)
                    )
                    or ("suffix" in str(self.row_limit_support))
                )
            )
            else exclude.add("row_limit_suffix")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate")
        )
        (
            include.add("satellite_location_id")
            if (not self.secure_gateway_id) and (not self.satellite_connector_id)
            else exclude.add("satellite_location_id")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
