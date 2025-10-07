from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import GOOGLE_PUB_SUB_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    credentials = "credentials"
    credentials_oauth2 = "credentials_oauth2"
    credentials_file = "credentials_file"
    workload_identity_federation_token = "workload_identity_federation_token"
    workload_identity_federation_token_url = "workload_identity_federation_token_url"


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


class GooglePubSubConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "693c2a02-39d1-4394-9426-fcdcfc4f3d7a"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    access_token: str = Field(None, alias="access_token")
    authentication_method: GOOGLE_PUB_SUB_CONNECTION.AuthMethod | None = Field(None, alias="auth_method")
    client_id: str = Field(None, alias="client_id")
    client_secret: str = Field(None, alias="client_secret")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    credentials: str = Field(None, alias="credentials")
    credentials_file_path: str = Field(None, alias="credentials_file")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    project_id: str | None = Field(None, alias="project_id")
    refresh_token: str = Field(None, alias="refresh_token")
    service_account_email: str = Field(None, alias="service_account_email")
    service_account_token_lifetime: int | None = Field(None, alias="service_account_token_lifetime")
    security_token_service_audience: str = Field(None, alias="sts_audience")
    token_field_name: str = Field(None, alias="token_field_name")
    token_format: GOOGLE_PUB_SUB_CONNECTION.TokenFormat | None = Field(
        GOOGLE_PUB_SUB_CONNECTION.TokenFormat.text, alias="token_format"
    )
    token_type: GOOGLE_PUB_SUB_CONNECTION.TokenType | None = Field(
        GOOGLE_PUB_SUB_CONNECTION.TokenType.id_token, alias="token_type"
    )
    token_url: str = Field(None, alias="token_url")
    request_body: str | None = Field(None, alias="token_url_body")
    http_headers: str | None = Field(None, alias="token_url_headers")
    http_method: GOOGLE_PUB_SUB_CONNECTION.TokenUrlMethod | None = Field(
        GOOGLE_PUB_SUB_CONNECTION.TokenUrlMethod.get, alias="token_url_method"
    )
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("credentials_file_path")
            if (
                (
                    ((not self.credentials))
                    and ((not self.client_id))
                    and ((not self.client_secret))
                    and ((not self.access_token))
                    and ((not self.refresh_token))
                    and ((not self.security_token_service_audience))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "credentials_file"
                                    )
                                    or (self.authentication_method == "credentials_file")
                                )
                            )
                        )
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
            )
            else exclude.add("refresh_token")
        )
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
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")

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
            include.add("credentials_file_path")
            if (
                (not self.credentials)
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
            )
            and (not self.defer_credentials)
            else exclude.add("credentials_file_path")
        )
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
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
