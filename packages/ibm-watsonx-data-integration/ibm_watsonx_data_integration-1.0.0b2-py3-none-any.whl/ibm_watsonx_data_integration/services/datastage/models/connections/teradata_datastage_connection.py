from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import TERADATA_DATASTAGE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class LogOnMech(Enum):
    default = "default"
    ldap = "ldap"
    td2 = "td2"


class SslMode(Enum):
    allow = "allow"
    disable = "disable"
    prefer = "prefer"
    require = "require"
    verify_ca = "verify_ca"
    verify_full = "verify_full"


class TransactionMode(Enum):
    ansi = "ansi"
    teradata = "teradata"


class TeradataDatastageConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "96441cf3-4edf-3eb8-89e7-0d16cab7ccec"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    account: str | None = Field(None, alias="account")
    automatically_map_character_set_encoding: bool | None = Field(True, alias="auto_map_charset_encoding")
    cas_lite_service_authorization_header: str | None = Field(None, alias="cas_lite_auth_header")
    client_character_set: str | None = Field("UTF8", alias="client_character_set")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    database: str | None = Field(None, alias="database")
    default_port: int | None = Field(1025, alias="default_port")
    delimiter: str | None = Field(":", alias="host_port_separator")
    logon_mechanism: TERADATA_DATASTAGE_CONNECTION.LogOnMech | None = Field(
        TERADATA_DATASTAGE_CONNECTION.LogOnMech.default, alias="log_on_mech"
    )
    maximum_bytes_per_character: int = Field(None, alias="max_bytes_per_character")
    nls_map_name: str = Field(None, alias="nls_map_name")
    password: str = Field(None, alias="password")
    query_band_expression: str | None = Field(None, alias="queryband")
    read_query_band_expression_from_the_file: bool | None = Field(False, alias="queryband.read_from_file")
    iana_character_set_name: str | None = Field(None, alias="queryband.read_from_file.character_set")
    server: str = Field(None, alias="server")
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
    ssl_mode: TERADATA_DATASTAGE_CONNECTION.SslMode | None = Field(None, alias="ssl_mode")
    ssl_certificate: str | None = Field(None, alias="ssl_mode.ssl_certificate")
    transaction_mode: TERADATA_DATASTAGE_CONNECTION.TransactionMode | None = Field(
        TERADATA_DATASTAGE_CONNECTION.TransactionMode.ansi, alias="transaction_mode"
    )
    unicode_pass_through: bool | None = Field(False, alias="unicode_pass_thru")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("ssl_certificate")
            if (
                (
                    (
                        self.ssl_mode
                        and (
                            (hasattr(self.ssl_mode, "value") and self.ssl_mode.value == "verify_ca")
                            or (self.ssl_mode == "verify_ca")
                        )
                    )
                )
                or (
                    self.ssl_mode
                    and (
                        (hasattr(self.ssl_mode, "value") and self.ssl_mode.value == "verify_full")
                        or (self.ssl_mode == "verify_full")
                    )
                )
            )
            else exclude.add("ssl_certificate")
        )
        (
            include.add("maximum_bytes_per_character")
            if (not self.automatically_map_character_set_encoding)
            else exclude.add("maximum_bytes_per_character")
        )
        (
            include.add("nls_map_name")
            if (not self.automatically_map_character_set_encoding)
            else exclude.add("nls_map_name")
        )
        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("iana_character_set_name")
            if (self.read_query_band_expression_from_the_file)
            else exclude.add("iana_character_set_name")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
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
        include.add("ssl_certificate") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate")
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")

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
            include.add("iana_character_set_name")
            if (
                self.read_query_band_expression_from_the_file == "true" or self.read_query_band_expression_from_the_file
            )
            else exclude.add("iana_character_set_name")
        )
        (
            include.add("ssl_certificate")
            if (
                self.ssl_mode
                and (
                    (
                        hasattr(self.ssl_mode, "value")
                        and self.ssl_mode.value
                        and "verify_ca" in str(self.ssl_mode.value)
                    )
                    or ("verify_ca" in str(self.ssl_mode))
                )
                or self.ssl_mode
                and (
                    (
                        hasattr(self.ssl_mode, "value")
                        and self.ssl_mode.value
                        and "verify_full" in str(self.ssl_mode.value)
                    )
                    or ("verify_full" in str(self.ssl_mode))
                )
            )
            else exclude.add("ssl_certificate")
        )
        (
            include.add("nls_map_name")
            if (
                self.automatically_map_character_set_encoding == "false"
                or not self.automatically_map_character_set_encoding
            )
            else exclude.add("nls_map_name")
        )
        (
            include.add("maximum_bytes_per_character")
            if (
                self.automatically_map_character_set_encoding == "false"
                or not self.automatically_map_character_set_encoding
            )
            else exclude.add("maximum_bytes_per_character")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
