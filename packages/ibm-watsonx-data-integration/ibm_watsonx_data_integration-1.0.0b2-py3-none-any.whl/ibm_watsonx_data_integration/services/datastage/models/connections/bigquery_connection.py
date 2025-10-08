from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import BIGQUERY_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    credentials = "credentials"
    credentials_oauth2 = "credentials_oauth2"
    workload_identity_federation_token = "workload_identity_federation_token"
    workload_identity_federation_token_url = "workload_identity_federation_token_url"


class JsonFormat(Enum):
    pretty = "pretty"
    raw = "raw"


class MetadataDiscovery(Enum):
    no_remarks = "no_remarks"
    remarks = "remarks"


class ProxyProtocol(Enum):
    http = "http"
    https = "https"


class TokenFormat(Enum):
    json = "json"
    text = "text"


class TokenType(Enum):
    aws4_request = "aws4_request"
    access_token = "access_token"
    id_token = "id_token"
    jwt = "jwt"
    saml2 = "saml2"


class TokenUrlMethod(Enum):
    get = "get"
    post = "post"
    put = "put"


class BigqueryConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "933152db-99e1-453a-8ce5-ae0e6714d1a9"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    access_token: str = Field(None, alias="access_token")
    api_service_url: str | None = Field(None, alias="api_service_url")
    authentication_method: BIGQUERY_CONNECTION.AuthMethod | None = Field(None, alias="auth_method")
    client_id: str = Field(None, alias="client_id")
    client_secret: str = Field(None, alias="client_secret")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    credentials: str = Field(None, alias="credentials")
    credentials_file_path: str = Field(None, alias="credentials_file")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    output_json_string_format: BIGQUERY_CONNECTION.JsonFormat | None = Field(None, alias="json_format")
    metadata_discovery: BIGQUERY_CONNECTION.MetadataDiscovery | None = Field(None, alias="metadata_discovery")
    project_id: str | None = Field(None, alias="project_id")
    proxy: bool | None = Field(False, alias="proxy")
    proxy_host: str = Field(None, alias="proxy_host")
    proxy_password: str | None = Field(None, alias="proxy_password")
    proxy_port: int = Field(None, alias="proxy_port")
    proxy_protocol: BIGQUERY_CONNECTION.ProxyProtocol | None = Field(
        BIGQUERY_CONNECTION.ProxyProtocol.https, alias="proxy_protocol"
    )
    proxy_username: str | None = Field(None, alias="proxy_user")
    refresh_token: str = Field(None, alias="refresh_token")
    service_account_email: str = Field(None, alias="service_account_email")
    service_account_token_lifetime: int | None = Field(None, alias="service_account_token_lifetime")
    port_is_ssl_enabled: bool | None = Field(False, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    security_token_service_audience: str = Field(None, alias="sts_audience")
    token_field_name: str = Field(None, alias="token_field_name")
    token_format: BIGQUERY_CONNECTION.TokenFormat | None = Field(
        BIGQUERY_CONNECTION.TokenFormat.text, alias="token_format"
    )
    token_type: BIGQUERY_CONNECTION.TokenType | None = Field(BIGQUERY_CONNECTION.TokenType.id_token, alias="token_type")
    token_url: str = Field(None, alias="token_url")
    request_body: str | None = Field(None, alias="token_url_body")
    http_headers: str | None = Field(None, alias="token_url_headers")
    http_method: BIGQUERY_CONNECTION.TokenUrlMethod | None = Field(
        BIGQUERY_CONNECTION.TokenUrlMethod.get, alias="token_url_method"
    )
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    additional_properties: str | None = Field(None, alias="properties")
    oauth_endpoint_uri: str | None = Field(None, alias="oauth_endpoint_uri")
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
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        (
            include.add("credentials_file_path")
            if (
                ((not self.credentials))
                and (not self.client_id)
                and (not self.client_secret)
                and (not self.access_token)
                and (not self.refresh_token)
                and (not self.security_token_service_audience)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "credentials_file"
                        )
                        or (self.authentication_method == "credentials_file")
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("credentials_file_path")
        )
        (
            include.add("token_field_name")
            if (
                self.token_format
                and (
                    (hasattr(self.token_format, "value") and self.token_format.value == "json")
                    or (self.token_format == "json")
                )
            )
            else exclude.add("token_field_name")
        )
        (
            include.add("credentials")
            if (
                (((not self.defer_credentials)))
                and (
                    ((not self.credentials_file_path))
                    and (not self.client_id)
                    and (not self.client_secret)
                    and (not self.access_token)
                    and (not self.refresh_token)
                    and (not self.security_token_service_audience)
                    and (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "credentials"
                            )
                            or (self.authentication_method == "credentials")
                        )
                    )
                )
            )
            else exclude.add("credentials")
        )
        (
            include.add("http_method")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.access_token)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "workload_identity_federation_token_url"
                        )
                        or (self.authentication_method == "workload_identity_federation_token_url")
                    )
                )
            )
            else exclude.add("http_method")
        )
        (
            include.add("http_headers")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.access_token)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "workload_identity_federation_token_url"
                        )
                        or (self.authentication_method == "workload_identity_federation_token_url")
                    )
                )
            )
            else exclude.add("http_headers")
        )
        include.add("proxy_protocol") if (self.proxy) else exclude.add("proxy_protocol")
        (
            include.add("security_token_service_audience")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.client_id)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "workload_identity_federation_token"
                                )
                                or (self.authentication_method == "workload_identity_federation_token")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "workload_identity_federation_token_url"
                            )
                            or (self.authentication_method == "workload_identity_federation_token_url")
                        )
                    )
                )
            )
            else exclude.add("security_token_service_audience")
        )
        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
        (
            include.add("token_type")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.client_id)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "workload_identity_federation_token"
                                )
                                or (self.authentication_method == "workload_identity_federation_token")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "workload_identity_federation_token_url"
                            )
                            or (self.authentication_method == "workload_identity_federation_token_url")
                        )
                    )
                )
            )
            else exclude.add("token_type")
        )
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        (
            include.add("port_is_ssl_enabled")
            if (
                ((self.proxy))
                and (
                    self.proxy_protocol
                    and (
                        (hasattr(self.proxy_protocol, "value") and self.proxy_protocol.value == "https")
                        or (self.proxy_protocol == "https")
                    )
                )
            )
            else exclude.add("port_is_ssl_enabled")
        )
        (
            include.add("client_id")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.security_token_service_audience)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "credentials_oauth2"
                        )
                        or (self.authentication_method == "credentials_oauth2")
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("client_id")
        )
        (
            include.add("access_token")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.token_url)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "credentials_oauth2"
                                )
                                or (self.authentication_method == "credentials_oauth2")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "workload_identity_federation_token"
                            )
                            or (self.authentication_method == "workload_identity_federation_token")
                        )
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("access_token")
        )
        (
            include.add("refresh_token")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.security_token_service_audience)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "credentials_oauth2"
                        )
                        or (self.authentication_method == "credentials_oauth2")
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("refresh_token")
        )
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        (
            include.add("token_format")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.client_id)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "workload_identity_federation_token"
                                )
                                or (self.authentication_method == "workload_identity_federation_token")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "workload_identity_federation_token_url"
                            )
                            or (self.authentication_method == "workload_identity_federation_token_url")
                        )
                    )
                )
            )
            else exclude.add("token_format")
        )
        (
            include.add("request_body")
            if (
                (
                    (
                        self.http_method
                        and (
                            (hasattr(self.http_method, "value") and self.http_method.value == "post")
                            or (self.http_method == "post")
                        )
                    )
                )
                or (
                    self.http_method
                    and (
                        (hasattr(self.http_method, "value") and self.http_method.value == "put")
                        or (self.http_method == "put")
                    )
                )
            )
            else exclude.add("request_body")
        )
        (
            include.add("validate_ssl_certificate")
            if (self.port_is_ssl_enabled)
            else exclude.add("validate_ssl_certificate")
        )
        (
            include.add("client_secret")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.security_token_service_audience)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "credentials_oauth2"
                        )
                        or (self.authentication_method == "credentials_oauth2")
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("client_secret")
        )
        (
            include.add("service_account_email")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.client_id)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "workload_identity_federation_token"
                                )
                                or (self.authentication_method == "workload_identity_federation_token")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "workload_identity_federation_token_url"
                            )
                            or (self.authentication_method == "workload_identity_federation_token_url")
                        )
                    )
                )
            )
            else exclude.add("service_account_email")
        )
        (
            include.add("token_url")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.access_token)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "workload_identity_federation_token_url"
                        )
                        or (self.authentication_method == "workload_identity_federation_token_url")
                    )
                )
            )
            else exclude.add("token_url")
        )
        (
            include.add("service_account_token_lifetime")
            if (
                ((not self.credentials))
                and (not self.credentials_file_path)
                and (not self.client_id)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "workload_identity_federation_token"
                                )
                                or (self.authentication_method == "workload_identity_federation_token")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "workload_identity_federation_token_url"
                            )
                            or (self.authentication_method == "workload_identity_federation_token_url")
                        )
                    )
                )
            )
            else exclude.add("service_account_token_lifetime")
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
        include.add("credentials_file_path") if (self.hidden_dummy_property1) else exclude.add("credentials_file_path")
        include.add("oauth_endpoint_uri") if (self.hidden_dummy_property1) else exclude.add("oauth_endpoint_uri")
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        (
            include.add("token_field_name")
            if (
                self.token_format
                and (
                    (hasattr(self.token_format, "value") and self.token_format.value == "json")
                    or (self.token_format == "json")
                )
            )
            else exclude.add("token_field_name")
        )
        include.add("proxy_protocol") if (self.proxy) else exclude.add("proxy_protocol")
        (
            include.add("port_is_ssl_enabled")
            if (self.proxy)
            and (
                self.proxy_protocol
                and (
                    (hasattr(self.proxy_protocol, "value") and self.proxy_protocol.value == "https")
                    or (self.proxy_protocol == "https")
                )
            )
            else exclude.add("port_is_ssl_enabled")
        )
        (
            include.add("credentials_file_path")
            if (not self.credentials)
            and (not self.client_id)
            and (not self.client_secret)
            and (not self.access_token)
            and (not self.refresh_token)
            and (not self.security_token_service_audience)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "credentials_file" in str(self.authentication_method.value)
                    )
                    or ("credentials_file" in str(self.authentication_method))
                )
            )
            and (not self.defer_credentials)
            else exclude.add("credentials_file_path")
        )
        include.add("proxy_port") if (self.proxy) else exclude.add("proxy_port")
        (
            include.add("token_format")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.client_id)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token_url" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token_url" in str(self.authentication_method))
                )
            )
            else exclude.add("token_format")
        )
        (
            include.add("client_id")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.security_token_service_audience)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "credentials_oauth2" in str(self.authentication_method.value)
                    )
                    or ("credentials_oauth2" in str(self.authentication_method))
                )
            )
            and (not self.defer_credentials)
            else exclude.add("client_id")
        )
        (
            include.add("http_method")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.access_token)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "workload_identity_federation_token_url"
                    )
                    or (self.authentication_method == "workload_identity_federation_token_url")
                )
            )
            else exclude.add("http_method")
        )
        include.add("proxy_password") if (self.proxy) else exclude.add("proxy_password")
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate")
        )
        (
            include.add("service_account_email")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.client_id)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token_url" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token_url" in str(self.authentication_method))
                )
            )
            else exclude.add("service_account_email")
        )
        (
            include.add("token_type")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.client_id)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token_url" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token_url" in str(self.authentication_method))
                )
            )
            else exclude.add("token_type")
        )
        (
            include.add("credentials")
            if (not self.defer_credentials)
            and (
                (not self.credentials_file_path)
                and (not self.client_id)
                and (not self.client_secret)
                and (not self.access_token)
                and (not self.refresh_token)
                and (not self.security_token_service_audience)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "credentials" in str(self.authentication_method.value)
                        )
                        or ("credentials" in str(self.authentication_method))
                    )
                )
            )
            else exclude.add("credentials")
        )
        (
            include.add("client_secret")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.security_token_service_audience)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "credentials_oauth2" in str(self.authentication_method.value)
                    )
                    or ("credentials_oauth2" in str(self.authentication_method))
                )
            )
            and (not self.defer_credentials)
            else exclude.add("client_secret")
        )
        (
            include.add("request_body")
            if (
                self.http_method
                and (
                    (
                        hasattr(self.http_method, "value")
                        and self.http_method.value
                        and "post" in str(self.http_method.value)
                    )
                    or ("post" in str(self.http_method))
                )
                and self.http_method
                and (
                    (
                        hasattr(self.http_method, "value")
                        and self.http_method.value
                        and "put" in str(self.http_method.value)
                    )
                    or ("put" in str(self.http_method))
                )
            )
            else exclude.add("request_body")
        )
        (
            include.add("validate_ssl_certificate")
            if (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("validate_ssl_certificate")
        )
        (
            include.add("service_account_token_lifetime")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.client_id)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token_url" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token_url" in str(self.authentication_method))
                )
            )
            else exclude.add("service_account_token_lifetime")
        )
        (
            include.add("token_url")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.access_token)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "workload_identity_federation_token_url"
                    )
                    or (self.authentication_method == "workload_identity_federation_token_url")
                )
            )
            else exclude.add("token_url")
        )
        include.add("proxy_username") if (self.proxy) else exclude.add("proxy_username")
        (
            include.add("http_headers")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.access_token)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value == "workload_identity_federation_token_url"
                    )
                    or (self.authentication_method == "workload_identity_federation_token_url")
                )
            )
            else exclude.add("http_headers")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        (
            include.add("access_token")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.token_url)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "credentials_oauth2" in str(self.authentication_method.value)
                    )
                    or ("credentials_oauth2" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token" in str(self.authentication_method))
                )
            )
            and (not self.defer_credentials)
            else exclude.add("access_token")
        )
        (
            include.add("refresh_token")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.security_token_service_audience)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "credentials_oauth2" in str(self.authentication_method.value)
                    )
                    or ("credentials_oauth2" in str(self.authentication_method))
                )
            )
            and (not self.defer_credentials)
            else exclude.add("refresh_token")
        )
        (
            include.add("security_token_service_audience")
            if (not self.credentials)
            and (not self.credentials_file_path)
            and (not self.client_id)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "workload_identity_federation_token_url" in str(self.authentication_method.value)
                    )
                    or ("workload_identity_federation_token_url" in str(self.authentication_method))
                )
            )
            else exclude.add("security_token_service_audience")
        )
        include.add("proxy_host") if (self.proxy) else exclude.add("proxy_host")
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
