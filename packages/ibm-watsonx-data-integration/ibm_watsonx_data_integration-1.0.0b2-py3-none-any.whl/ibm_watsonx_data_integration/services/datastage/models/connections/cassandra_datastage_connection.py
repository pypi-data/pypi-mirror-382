from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import CASSANDRA_DATASTAGE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthenticatorType(Enum):
    allow_all_authenticator = "allow_all_authenticator"
    password_authentication = "password_authentication"


class Compression(Enum):
    lz4 = "lz4"
    no_compression = "no_compression"
    snappy = "snappy"


class ProtocolVersion(Enum):
    dse_v1 = "dse_v1"
    dse_v2 = "dse_v2"
    newest_supported = "newest_supported"
    newest_beta = "newest_beta"
    v1 = "v1"
    v2 = "v2"
    v3 = "v3"
    v4 = "v4"
    v5 = "v5"
    v9 = "v9"


class CassandraDatastageConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "123e4263-dd25-44e5-8282-cf1b2eeea9bd"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    authentication_method: CASSANDRA_DATASTAGE_CONNECTION.AuthenticatorType | None = Field(
        CASSANDRA_DATASTAGE_CONNECTION.AuthenticatorType.allow_all_authenticator, alias="authenticator_type"
    )
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_contact_points: str = Field(None, alias="cluster_contact_points")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    compression_type: CASSANDRA_DATASTAGE_CONNECTION.Compression | None = Field(
        CASSANDRA_DATASTAGE_CONNECTION.Compression.no_compression, alias="compression"
    )
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    local_datacenter: str = Field("datacenter1", alias="local_datacenter")
    password: str = Field(None, alias="password")
    protocol_version: CASSANDRA_DATASTAGE_CONNECTION.ProtocolVersion | None = Field(
        CASSANDRA_DATASTAGE_CONNECTION.ProtocolVersion.newest_supported, alias="protocol_version"
    )
    keystore_password: str | None = Field(None, alias="ssl_keystore_password")
    keystore_path: str | None = Field(None, alias="ssl_keystore_path")
    truststore_password: str | None = Field(None, alias="ssl_truststore_password")
    truststore_path: str | None = Field(None, alias="ssl_truststore_path")
    use_ssl_tls: bool | None = Field(False, alias="use_ssl")
    use_client_certificate_authentication: bool | None = Field(None, alias="use_ssl_client_cert_auth")
    use_client_to_node_encryption: bool | None = Field(None, alias="use_ssl_client_encryption")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("password")
            if (
                (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "password_authentication"
                                )
                                or (self.authentication_method == "password_authentication")
                            )
                        )
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("password")
        )
        include.add("keystore_password") if (self.use_client_to_node_encryption) else exclude.add("keystore_password")
        (
            include.add("use_client_certificate_authentication")
            if (self.use_ssl_tls)
            else exclude.add("use_client_certificate_authentication")
        )
        (
            include.add("truststore_password")
            if (self.use_client_certificate_authentication)
            else exclude.add("truststore_password")
        )
        (
            include.add("truststore_path")
            if (self.use_client_certificate_authentication)
            else exclude.add("truststore_path")
        )
        include.add("keystore_path") if (self.use_client_to_node_encryption) else exclude.add("keystore_path")
        (
            include.add("use_client_to_node_encryption")
            if (self.use_ssl_tls)
            else exclude.add("use_client_to_node_encryption")
        )
        (
            include.add("username")
            if (
                (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "password_authentication"
                                )
                                or (self.authentication_method == "password_authentication")
                            )
                        )
                    )
                )
                and (not self.defer_credentials)
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
            include.add("keystore_password")
            if (self.use_client_to_node_encryption and "true" in str(self.use_client_to_node_encryption))
            else exclude.add("keystore_password")
        )
        (
            include.add("use_client_certificate_authentication")
            if (self.use_ssl_tls and "true" in str(self.use_ssl_tls))
            else exclude.add("use_client_certificate_authentication")
        )
        (
            include.add("use_client_to_node_encryption")
            if (self.use_ssl_tls and "true" in str(self.use_ssl_tls))
            else exclude.add("use_client_to_node_encryption")
        )
        (
            include.add("truststore_password")
            if (
                self.use_client_certificate_authentication and "true" in str(self.use_client_certificate_authentication)
            )
            else exclude.add("truststore_password")
        )
        (
            include.add("keystore_path")
            if (self.use_client_to_node_encryption and "true" in str(self.use_client_to_node_encryption))
            else exclude.add("keystore_path")
        )
        (
            include.add("password")
            if (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "password_authentication" in str(self.authentication_method.value)
                    )
                    or ("password_authentication" in str(self.authentication_method))
                )
            )
            and (not self.defer_credentials)
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "password_authentication" in str(self.authentication_method.value)
                    )
                    or ("password_authentication" in str(self.authentication_method))
                )
            )
            and (not self.defer_credentials)
            else exclude.add("username")
        )
        (
            include.add("truststore_path")
            if (
                self.use_client_certificate_authentication and "true" in str(self.use_client_certificate_authentication)
            )
            else exclude.add("truststore_path")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
