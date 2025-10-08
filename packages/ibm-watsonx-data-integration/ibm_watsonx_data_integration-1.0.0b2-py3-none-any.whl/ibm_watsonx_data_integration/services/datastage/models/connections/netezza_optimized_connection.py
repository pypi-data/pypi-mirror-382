from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from pydantic import ConfigDict, Field
from typing import ClassVar


class NetezzaOptimizedConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "63e2d853-e650-3b59-91a5-95e7bf725b9b"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    cas_lite_service_authorization_header: str | None = Field(None, alias="cas_lite_auth_header")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    database: str = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    hostname: str = Field(None, alias="hostname")
    password: str = Field(None, alias="password")
    port: int = Field(5480, alias="port")
    satellite_client_certificate: str | None = Field(None, alias="sl_client_cert")
    satellite_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    satellite_connector_id: str | None = Field(None, alias="sl_connector_id")
    satellite_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    satellite_endpoint_display_name: str | None = Field(None, alias="sl_endpoint_name")
    satellite_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    original_hostname_of_the_resource: str | None = Field(None, alias="sl_host_original")
    satellite_as_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    satellite_location_id: str | None = Field(None, alias="sl_location_id")
    satellite_service_url: str | None = Field(None, alias="sl_service_url")
    ssl_certificate_pem: str | None = Field(None, alias="ssl_certificate")
    ssl_connection: bool | None = Field(False, alias="ssl_connection")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    use_separate_connection_for_twt: bool | None = Field(False, alias="use_separate_connection_for_twt")
    twt_separate_connection_database_name: str = Field(None, alias="use_separate_connection_for_twt.database")
    twt_separate_connection_password: str | None = Field(None, alias="use_separate_connection_for_twt.password")
    user_name: str | None = Field(None, alias="use_separate_connection_for_twt.username")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("ssl_certificate_pem") if (self.ssl_connection) else exclude.add("ssl_certificate_pem")
        include.add("password") if (not self.defer_credentials) else exclude.add("password")
        include.add("user_name") if (self.use_separate_connection_for_twt) else exclude.add("user_name")
        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("twt_separate_connection_database_name")
            if (self.use_separate_connection_for_twt)
            else exclude.add("twt_separate_connection_database_name")
        )
        (
            include.add("twt_separate_connection_password")
            if (self.use_separate_connection_for_twt)
            else exclude.add("twt_separate_connection_password")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        include.add("username") if (not self.defer_credentials) else exclude.add("username")
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
            include.add("twt_separate_connection_password")
            if (self.use_separate_connection_for_twt == "true" or self.use_separate_connection_for_twt)
            else exclude.add("twt_separate_connection_password")
        )
        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service == "true" or self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        (
            include.add("twt_separate_connection_database_name")
            if (self.use_separate_connection_for_twt == "true" or self.use_separate_connection_for_twt)
            else exclude.add("twt_separate_connection_database_name")
        )
        include.add("password") if not self.defer_credentials else exclude.add("password")
        (
            include.add("user_name")
            if (self.use_separate_connection_for_twt == "true" or self.use_separate_connection_for_twt)
            else exclude.add("user_name")
        )
        include.add("username") if not self.defer_credentials else exclude.add("username")
        (
            include.add("ssl_certificate_pem")
            if (self.ssl_connection == "true" or self.ssl_connection)
            else exclude.add("ssl_certificate_pem")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
