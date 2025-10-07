from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import SAPODATA_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthType(Enum):
    api_key = "api_key"
    none = "none"
    basic = "basic"


class SapOdataServiceVersion(Enum):
    V2 = "V2"
    V4 = "V4"


class SapodataConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "79a0a133-cbb6-48d0-a3b0-0956a9655401"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    api_key: str = Field(None, alias="api_key")
    authentication_type: SAPODATA_CONNECTION.AuthType | None = Field(None, alias="auth_type")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    password: str = Field(None, alias="password")
    client_private_key: str | None = Field(None, alias="private_key")
    client_certificate_chain: str | None = Field(None, alias="private_key_certificate_chain")
    private_key_passphrase: str | None = Field(None, alias="private_key_passphrase")
    sap_catalog_service_version: int | None = Field(None, alias="sap_catalog_version")
    sap_gateway_url: str = Field(None, alias="sap_gateway_url")
    sap_odata_service_version: SAPODATA_CONNECTION.SapOdataServiceVersion | None = Field(
        None, alias="sap_odata_service_version"
    )
    sl_client_cert: str | None = Field(None, alias="sl_client_cert")
    sl_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    sl_connector_id: str | None = Field(None, alias="sl_connector_id")
    sl_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    sl_endpoint_name: str | None = Field(None, alias="sl_endpoint_name")
    sl_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    sl_host_original: str | None = Field(None, alias="sl_host_original")
    sl_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    sl_location_id: str | None = Field(None, alias="sl_location_id")
    sl_service_url: str | None = Field(None, alias="sl_service_url")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    ssl_certificate_hostname: str | None = Field(None, alias="ssl_certificate_host")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    timeout_seconds: int | None = Field(None, alias="timeout_seconds")
    use_mutual_authentication: bool | None = Field(False, alias="use_mtls")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    additional_properties: str | None = Field(None, alias="properties")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_type
                    and (
                        (hasattr(self.authentication_type, "value") and self.authentication_type.value == "basic")
                        or (self.authentication_type == "basic")
                    )
                )
                and (
                    (
                        (
                            self.authentication_type
                            and (
                                (
                                    hasattr(self.authentication_type, "value")
                                    and self.authentication_type.value != "api_key"
                                )
                                or (self.authentication_type != "api_key")
                            )
                        )
                    )
                    and (
                        self.authentication_type
                        and (
                            (hasattr(self.authentication_type, "value") and self.authentication_type.value != "none")
                            or (self.authentication_type != "none")
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        include.add("sl_connector_id") if (not self.sl_location_id) else exclude.add("sl_connector_id")
        (
            include.add("api_key")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_type
                    and (
                        (hasattr(self.authentication_type, "value") and self.authentication_type.value == "api_key")
                        or (self.authentication_type == "api_key")
                    )
                )
                and (
                    (
                        (
                            self.authentication_type
                            and (
                                (
                                    hasattr(self.authentication_type, "value")
                                    and self.authentication_type.value != "basic"
                                )
                                or (self.authentication_type != "basic")
                            )
                        )
                    )
                    and (
                        self.authentication_type
                        and (
                            (hasattr(self.authentication_type, "value") and self.authentication_type.value != "none")
                            or (self.authentication_type != "none")
                        )
                    )
                )
            )
            else exclude.add("api_key")
        )
        (
            include.add("client_certificate_chain")
            if (self.use_mutual_authentication)
            else exclude.add("client_certificate_chain")
        )
        (
            include.add("ssl_certificate_hostname")
            if (((self.ssl_certificate)) and (self.validate_ssl_certificate))
            else exclude.add("ssl_certificate_hostname")
        )
        include.add("client_private_key") if (self.use_mutual_authentication) else exclude.add("client_private_key")
        (
            include.add("private_key_passphrase")
            if (self.use_mutual_authentication)
            else exclude.add("private_key_passphrase")
        )
        include.add("sl_location_id") if (not self.sl_connector_id) else exclude.add("sl_location_id")
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_type
                    and (
                        (hasattr(self.authentication_type, "value") and self.authentication_type.value == "basic")
                        or (self.authentication_type == "basic")
                    )
                )
                and (
                    (
                        (
                            self.authentication_type
                            and (
                                (
                                    hasattr(self.authentication_type, "value")
                                    and self.authentication_type.value != "api_key"
                                )
                                or (self.authentication_type != "api_key")
                            )
                        )
                    )
                    and (
                        self.authentication_type
                        and (
                            (hasattr(self.authentication_type, "value") and self.authentication_type.value != "none")
                            or (self.authentication_type != "none")
                        )
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
            include.add("client_certificate_chain")
            if (self.hidden_dummy_property1)
            else exclude.add("client_certificate_chain")
        )
        include.add("client_private_key") if (self.hidden_dummy_property1) else exclude.add("client_private_key")
        (
            include.add("private_key_passphrase")
            if (self.hidden_dummy_property1)
            else exclude.add("private_key_passphrase")
        )
        (
            include.add("use_mutual_authentication")
            if (self.hidden_dummy_property1)
            else exclude.add("use_mutual_authentication")
        )
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")
        (
            include.add("sap_odata_service_version")
            if (self.hidden_dummy_property1)
            else exclude.add("sap_odata_service_version")
        )

        include.add("sl_connector_id") if (not self.sl_location_id) else exclude.add("sl_connector_id")
        (
            include.add("ssl_certificate_hostname")
            if (self.ssl_certificate) and (self.validate_ssl_certificate == "true" or self.validate_ssl_certificate)
            else exclude.add("ssl_certificate_hostname")
        )
        (
            include.add("api_key")
            if (not self.defer_credentials)
            and (
                self.authentication_type
                and (
                    (hasattr(self.authentication_type, "value") and self.authentication_type.value == "api_key")
                    or (self.authentication_type == "api_key")
                )
            )
            and (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "basic" not in str(self.authentication_type.value)
                    )
                    or ("basic" not in str(self.authentication_type))
                )
                and self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "none" not in str(self.authentication_type.value)
                    )
                    or ("none" not in str(self.authentication_type))
                )
            )
            else exclude.add("api_key")
        )
        (
            include.add("client_certificate_chain")
            if (self.use_mutual_authentication and "true" in str(self.use_mutual_authentication))
            else exclude.add("client_certificate_chain")
        )
        (
            include.add("private_key_passphrase")
            if (self.use_mutual_authentication and "true" in str(self.use_mutual_authentication))
            else exclude.add("private_key_passphrase")
        )
        include.add("ssl_certificate_file") if (not self.ssl_certificate) else exclude.add("ssl_certificate_file")
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                self.authentication_type
                and (
                    (hasattr(self.authentication_type, "value") and self.authentication_type.value == "basic")
                    or (self.authentication_type == "basic")
                )
            )
            and (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "api_key" not in str(self.authentication_type.value)
                    )
                    or ("api_key" not in str(self.authentication_type))
                )
                and self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "none" not in str(self.authentication_type.value)
                    )
                    or ("none" not in str(self.authentication_type))
                )
            )
            else exclude.add("password")
        )
        (
            include.add("client_private_key")
            if (self.use_mutual_authentication and "true" in str(self.use_mutual_authentication))
            else exclude.add("client_private_key")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                self.authentication_type
                and (
                    (hasattr(self.authentication_type, "value") and self.authentication_type.value == "basic")
                    or (self.authentication_type == "basic")
                )
            )
            and (
                self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "api_key" not in str(self.authentication_type.value)
                    )
                    or ("api_key" not in str(self.authentication_type))
                )
                and self.authentication_type
                and (
                    (
                        hasattr(self.authentication_type, "value")
                        and self.authentication_type.value
                        and "none" not in str(self.authentication_type.value)
                    )
                    or ("none" not in str(self.authentication_type))
                )
            )
            else exclude.add("username")
        )
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        include.add("sl_location_id") if (not self.sl_connector_id) else exclude.add("sl_location_id")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
