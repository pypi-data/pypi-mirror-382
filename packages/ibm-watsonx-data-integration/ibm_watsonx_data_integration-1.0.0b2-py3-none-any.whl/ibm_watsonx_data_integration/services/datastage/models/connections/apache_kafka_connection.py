from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import APACHE_KAFKA_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class SaslOauthbearer(Enum):
    SASL_OAUTH2 = "SASL_OAUTH2"


class SchemaRegistryAuthentication(Enum):
    none = "none"
    reuse_sasl_credentials = "reuse_sasl_credentials"
    user_credentials = "user_credentials"


class SchemaRegistrySecure(Enum):
    kerberos = "kerberos"
    none = "none"
    ssl = "ssl"
    reuse_ssl = "reuse_ssl"


class SchemaRegistryType(Enum):
    confluent = "confluent"
    eventstreamsconfluent = "eventstreamsconfluent"


class SecureConnection(Enum):
    kerberos = "kerberos"
    none = "None"
    SASL_OAUTHBEARER = "SASL_OAUTHBEARER"
    SASL_PLAIN = "SASL_PLAIN"
    SASL_SSL = "SASL_SSL"
    SCRAM_SHA_256 = "SCRAM-SHA-256"
    SCRAM_SHA_512 = "SCRAM-SHA-512"
    SSL = "SSL"


class ApacheKafkaConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "f13bc9b7-4a46-48f4-99c3-01d943334ba7"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    key_chain_pem: str | None = Field(None, alias="key_chain_pem")
    key_password: str | None = Field(None, alias="key_password")
    key_pem: str | None = Field(None, alias="key_pem")
    keystore_location: str | None = Field(None, alias="keystore_location")
    keystore_password: str | None = Field(None, alias="keystore_password")
    keytab: str | None = Field(None, alias="keytab")
    legacy_registry_security_conf: bool | None = Field(None, alias="legacy_registry_security_conf")
    legacy_security_conf: bool | None = Field(None, alias="legacy_security_conf")
    additional_properties: str | None = Field(None, alias="oauthbearer_advanced_settings")
    client_id: str | None = Field(None, alias="oauthbearer_client_id")
    client_secret: str | None = Field(None, alias="oauthbearer_client_secret")
    scope: str | None = Field(None, alias="oauthbearer_scope")
    server_url: str | None = Field(None, alias="oauthbearer_token_endpoint_url")
    password: str | None = Field(None, alias="password")
    registry_key_chain_pem: str | None = Field(None, alias="registry_key_chain_pem")
    registry_key_password: str | None = Field(None, alias="registry_key_password")
    registry_key_pem: str | None = Field(None, alias="registry_key_pem")
    registry_keystore_location: str | None = Field(None, alias="registry_keystore_location")
    registry_keystore_password: str | None = Field(None, alias="registry_keystore_password")
    registry_keytab: str | None = Field(None, alias="registry_keytab")
    registry_password: str | None = Field(None, alias="registry_password")
    registry_principal_name: str | None = Field(None, alias="registry_principal_name")
    registry_truststore_location: str | None = Field(None, alias="registry_truststore_location")
    registry_truststore_password: str | None = Field(None, alias="registry_truststore_password")
    registry_truststore_pem: str | None = Field(None, alias="registry_truststore_pem")
    registry_username: str | None = Field(None, alias="registry_username")
    oauth_bearer_authentication: APACHE_KAFKA_CONNECTION.SaslOauthbearer | None = Field(
        APACHE_KAFKA_CONNECTION.SaslOauthbearer.SASL_OAUTH2, alias="sasl_oauthbearer"
    )
    schema_registry_authentication: APACHE_KAFKA_CONNECTION.SchemaRegistryAuthentication | None = Field(
        APACHE_KAFKA_CONNECTION.SchemaRegistryAuthentication.none, alias="schema_registry_authentication"
    )
    schema_registry_secure: APACHE_KAFKA_CONNECTION.SchemaRegistrySecure | None = Field(
        APACHE_KAFKA_CONNECTION.SchemaRegistrySecure.none, alias="schema_registry_secure"
    )
    schema_registry_type: APACHE_KAFKA_CONNECTION.SchemaRegistryType | None = Field(
        APACHE_KAFKA_CONNECTION.SchemaRegistryType.confluent, alias="schema_registry_type"
    )
    registry_url: str | None = Field(None, alias="schema_registry_url")
    secure_connection: APACHE_KAFKA_CONNECTION.SecureConnection | None = Field(
        APACHE_KAFKA_CONNECTION.SecureConnection.none, alias="secure_connection"
    )
    kafka_server_host_name: str = Field(None, alias="server_name")
    truststore_location: str | None = Field(None, alias="truststore_location")
    truststore_password: str | None = Field(None, alias="truststore_password")
    truststore_pem: str | None = Field(None, alias="truststore_pem")
    use_schema_registry_for_message_format: bool | None = Field(False, alias="use_schema_registry")
    username: str | None = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("registry_key_pem")
            if (
                (
                    (
                        (
                            self.schema_registry_secure
                            and (
                                (
                                    hasattr(self.schema_registry_secure, "value")
                                    and self.schema_registry_secure.value == "ssl"
                                )
                                or (self.schema_registry_secure == "ssl")
                            )
                        )
                    )
                )
                and (self.use_schema_registry_for_message_format)
                and (not self.defer_credentials)
            )
            else exclude.add("registry_key_pem")
        )
        (
            include.add("schema_registry_authentication")
            if (((((self.use_schema_registry_for_message_format)))) or (self.use_schema_registry_for_message_format))
            else exclude.add("schema_registry_authentication")
        )
        (
            include.add("truststore_pem")
            if (
                (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_OAUTHBEARER"
                                    )
                                    or (self.secure_connection == "SASL_OAUTHBEARER")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "kerberos"
                                    )
                                    or (self.secure_connection == "kerberos")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_OAUTHBEARER"
                                    )
                                    or (self.secure_connection == "SASL_OAUTHBEARER")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "kerberos"
                                    )
                                    or (self.secure_connection == "kerberos")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("truststore_pem")
        )
        (
            include.add("keytab")
            if (
                (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "kerberos"
                                    )
                                    or (self.secure_connection == "kerberos")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "kerberos"
                                    )
                                    or (self.secure_connection == "kerberos")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("keytab")
        )
        (
            include.add("client_secret")
            if (
                (
                    (
                        (
                            (
                                self.oauth_bearer_authentication
                                and (
                                    (
                                        hasattr(self.oauth_bearer_authentication, "value")
                                        and self.oauth_bearer_authentication.value == "SASL_OAUTH2"
                                    )
                                    or (self.oauth_bearer_authentication == "SASL_OAUTH2")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.oauth_bearer_authentication
                                and (
                                    (
                                        hasattr(self.oauth_bearer_authentication, "value")
                                        and self.oauth_bearer_authentication.value == "SASL_OAUTH2"
                                    )
                                    or (self.oauth_bearer_authentication == "SASL_OAUTH2")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("client_secret")
        )
        (
            include.add("registry_keystore_location")
            if (
                (
                    (((self.legacy_registry_security_conf)))
                    and (
                        (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "ssl"
                                    )
                                    or (self.schema_registry_secure == "ssl")
                                )
                            )
                        )
                    )
                    and (((self.use_schema_registry_for_message_format)))
                )
                or (
                    (((self.legacy_registry_security_conf)))
                    and (
                        self.schema_registry_secure
                        and (
                            (
                                hasattr(self.schema_registry_secure, "value")
                                and self.schema_registry_secure.value == "ssl"
                            )
                            or (self.schema_registry_secure == "ssl")
                        )
                    )
                    and (self.use_schema_registry_for_message_format)
                )
            )
            else exclude.add("registry_keystore_location")
        )
        (
            include.add("keystore_password")
            if (
                (
                    (((self.legacy_security_conf)))
                    and (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (((self.legacy_security_conf)))
                    and (
                        self.secure_connection
                        and (
                            (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                            or (self.secure_connection == "SSL")
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("keystore_password")
        )
        (
            include.add("client_id")
            if (
                (
                    (
                        (
                            (
                                self.oauth_bearer_authentication
                                and (
                                    (
                                        hasattr(self.oauth_bearer_authentication, "value")
                                        and self.oauth_bearer_authentication.value == "SASL_OAUTH2"
                                    )
                                    or (self.oauth_bearer_authentication == "SASL_OAUTH2")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.oauth_bearer_authentication
                                and (
                                    (
                                        hasattr(self.oauth_bearer_authentication, "value")
                                        and self.oauth_bearer_authentication.value == "SASL_OAUTH2"
                                    )
                                    or (self.oauth_bearer_authentication == "SASL_OAUTH2")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("client_id")
        )
        (
            include.add("password")
            if (
                (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_PLAIN"
                                    )
                                    or (self.secure_connection == "SASL_PLAIN")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    ((not self.defer_credentials))
                    and (
                        (
                            (
                                (
                                    self.secure_connection
                                    and (
                                        (
                                            hasattr(self.secure_connection, "value")
                                            and self.secure_connection.value == "SASL_PLAIN"
                                        )
                                        or (self.secure_connection == "SASL_PLAIN")
                                    )
                                )
                            )
                            or (
                                (
                                    self.secure_connection
                                    and (
                                        (
                                            hasattr(self.secure_connection, "value")
                                            and self.secure_connection.value == "SASL_SSL"
                                        )
                                        or (self.secure_connection == "SASL_SSL")
                                    )
                                )
                            )
                            or (
                                (
                                    self.secure_connection
                                    and (
                                        (
                                            hasattr(self.secure_connection, "value")
                                            and self.secure_connection.value == "SCRAM-SHA-256"
                                        )
                                        or (self.secure_connection == "SCRAM-SHA-256")
                                    )
                                )
                            )
                            or (
                                (
                                    self.secure_connection
                                    and (
                                        (
                                            hasattr(self.secure_connection, "value")
                                            and self.secure_connection.value == "SCRAM-SHA-512"
                                        )
                                        or (self.secure_connection == "SCRAM-SHA-512")
                                    )
                                )
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (
                                    hasattr(self.secure_connection, "value")
                                    and self.secure_connection.value == "SASL_SSL"
                                )
                                or (self.secure_connection == "SASL_SSL")
                            )
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("key_pem")
            if (
                (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("key_pem")
        )
        (
            include.add("registry_password")
            if (
                (
                    (
                        (
                            self.schema_registry_authentication
                            and (
                                (
                                    hasattr(self.schema_registry_authentication, "value")
                                    and self.schema_registry_authentication.value == "user_credentials"
                                )
                                or (self.schema_registry_authentication == "user_credentials")
                            )
                        )
                    )
                )
                and (self.use_schema_registry_for_message_format)
                and (not self.defer_credentials)
            )
            else exclude.add("registry_password")
        )
        (
            include.add("truststore_password")
            if (
                (
                    (((self.legacy_security_conf)))
                    and (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_OAUTHBEARER"
                                    )
                                    or (self.secure_connection == "SASL_OAUTHBEARER")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "kerberos"
                                    )
                                    or (self.secure_connection == "kerberos")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (((self.legacy_security_conf)))
                    and (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_OAUTHBEARER"
                                    )
                                    or (self.secure_connection == "SASL_OAUTHBEARER")
                                )
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (
                                    hasattr(self.secure_connection, "value")
                                    and self.secure_connection.value == "SASL_SSL"
                                )
                                or (self.secure_connection == "SASL_SSL")
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (
                                    hasattr(self.secure_connection, "value")
                                    and self.secure_connection.value == "SCRAM-SHA-256"
                                )
                                or (self.secure_connection == "SCRAM-SHA-256")
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (
                                    hasattr(self.secure_connection, "value")
                                    and self.secure_connection.value == "SCRAM-SHA-512"
                                )
                                or (self.secure_connection == "SCRAM-SHA-512")
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                or (self.secure_connection == "SSL")
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (
                                    hasattr(self.secure_connection, "value")
                                    and self.secure_connection.value == "kerberos"
                                )
                                or (self.secure_connection == "kerberos")
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("truststore_password")
        )
        (
            include.add("registry_truststore_location")
            if (
                (
                    (((self.legacy_registry_security_conf)))
                    and (
                        (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "kerberos"
                                    )
                                    or (self.schema_registry_secure == "kerberos")
                                )
                            )
                        )
                        or (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "ssl"
                                    )
                                    or (self.schema_registry_secure == "ssl")
                                )
                            )
                        )
                    )
                    and (((self.use_schema_registry_for_message_format)))
                )
                or (
                    (((self.legacy_registry_security_conf)))
                    and (
                        (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "kerberos"
                                    )
                                    or (self.schema_registry_secure == "kerberos")
                                )
                            )
                        )
                        or (
                            self.schema_registry_secure
                            and (
                                (
                                    hasattr(self.schema_registry_secure, "value")
                                    and self.schema_registry_secure.value == "ssl"
                                )
                                or (self.schema_registry_secure == "ssl")
                            )
                        )
                    )
                    and (self.use_schema_registry_for_message_format)
                )
            )
            else exclude.add("registry_truststore_location")
        )
        (
            include.add("key_password")
            if (
                (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("key_password")
        )
        (
            include.add("registry_keytab")
            if (
                (
                    (
                        (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "kerberos"
                                    )
                                    or (self.schema_registry_secure == "kerberos")
                                )
                            )
                        )
                    )
                    and (((self.use_schema_registry_for_message_format)))
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "kerberos"
                                    )
                                    or (self.schema_registry_secure == "kerberos")
                                )
                            )
                        )
                    )
                    and (self.use_schema_registry_for_message_format)
                    and (self.use_schema_registry_for_message_format)
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("registry_keytab")
        )
        (
            include.add("registry_principal_name")
            if (
                (
                    (
                        (
                            self.schema_registry_secure
                            and (
                                (
                                    hasattr(self.schema_registry_secure, "value")
                                    and self.schema_registry_secure.value == "kerberos"
                                )
                                or (self.schema_registry_secure == "kerberos")
                            )
                        )
                    )
                )
                and (self.use_schema_registry_for_message_format)
                and (not self.defer_credentials)
            )
            else exclude.add("registry_principal_name")
        )
        (
            include.add("registry_key_chain_pem")
            if (
                (
                    (
                        (
                            self.schema_registry_secure
                            and (
                                (
                                    hasattr(self.schema_registry_secure, "value")
                                    and self.schema_registry_secure.value == "ssl"
                                )
                                or (self.schema_registry_secure == "ssl")
                            )
                        )
                    )
                )
                and (self.use_schema_registry_for_message_format)
                and (not self.defer_credentials)
            )
            else exclude.add("registry_key_chain_pem")
        )
        (
            include.add("registry_truststore_password")
            if (
                (
                    (((self.legacy_registry_security_conf)))
                    and (
                        (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "kerberos"
                                    )
                                    or (self.schema_registry_secure == "kerberos")
                                )
                            )
                        )
                        or (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "ssl"
                                    )
                                    or (self.schema_registry_secure == "ssl")
                                )
                            )
                        )
                    )
                    and (((self.use_schema_registry_for_message_format)))
                )
                or (
                    (((self.legacy_registry_security_conf)))
                    and (
                        (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "kerberos"
                                    )
                                    or (self.schema_registry_secure == "kerberos")
                                )
                            )
                        )
                        or (
                            self.schema_registry_secure
                            and (
                                (
                                    hasattr(self.schema_registry_secure, "value")
                                    and self.schema_registry_secure.value == "ssl"
                                )
                                or (self.schema_registry_secure == "ssl")
                            )
                        )
                    )
                    and (self.use_schema_registry_for_message_format)
                )
            )
            else exclude.add("registry_truststore_password")
        )
        (
            include.add("registry_keystore_password")
            if (
                (
                    (((self.legacy_registry_security_conf)))
                    and (
                        (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "ssl"
                                    )
                                    or (self.schema_registry_secure == "ssl")
                                )
                            )
                        )
                    )
                    and (((self.use_schema_registry_for_message_format)))
                )
                or (
                    (((self.legacy_registry_security_conf)))
                    and (
                        self.schema_registry_secure
                        and (
                            (
                                hasattr(self.schema_registry_secure, "value")
                                and self.schema_registry_secure.value == "ssl"
                            )
                            or (self.schema_registry_secure == "ssl")
                        )
                    )
                    and (self.use_schema_registry_for_message_format)
                )
            )
            else exclude.add("registry_keystore_password")
        )
        (
            include.add("server_url")
            if (
                (
                    (
                        (
                            (
                                self.oauth_bearer_authentication
                                and (
                                    (
                                        hasattr(self.oauth_bearer_authentication, "value")
                                        and self.oauth_bearer_authentication.value == "SASL_OAUTH2"
                                    )
                                    or (self.oauth_bearer_authentication == "SASL_OAUTH2")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.oauth_bearer_authentication
                                and (
                                    (
                                        hasattr(self.oauth_bearer_authentication, "value")
                                        and self.oauth_bearer_authentication.value == "SASL_OAUTH2"
                                    )
                                    or (self.oauth_bearer_authentication == "SASL_OAUTH2")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("server_url")
        )
        (
            include.add("legacy_registry_security_conf")
            if (
                (
                    (
                        (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "kerberos"
                                    )
                                    or (self.schema_registry_secure == "kerberos")
                                )
                            )
                        )
                        or (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "ssl"
                                    )
                                    or (self.schema_registry_secure == "ssl")
                                )
                            )
                        )
                    )
                    and (((self.use_schema_registry_for_message_format)))
                )
                or (
                    (
                        (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "kerberos"
                                    )
                                    or (self.schema_registry_secure == "kerberos")
                                )
                            )
                        )
                        or (
                            (
                                self.schema_registry_secure
                                and (
                                    (
                                        hasattr(self.schema_registry_secure, "value")
                                        and self.schema_registry_secure.value == "ssl"
                                    )
                                    or (self.schema_registry_secure == "ssl")
                                )
                            )
                        )
                    )
                    and (self.use_schema_registry_for_message_format)
                )
            )
            else exclude.add("legacy_registry_security_conf")
        )
        (
            include.add("truststore_location")
            if (
                (
                    (((self.legacy_security_conf)))
                    and (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_OAUTHBEARER"
                                    )
                                    or (self.secure_connection == "SASL_OAUTHBEARER")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "kerberos"
                                    )
                                    or (self.secure_connection == "kerberos")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (((self.legacy_security_conf)))
                    and (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_OAUTHBEARER"
                                    )
                                    or (self.secure_connection == "SASL_OAUTHBEARER")
                                )
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (
                                    hasattr(self.secure_connection, "value")
                                    and self.secure_connection.value == "SASL_SSL"
                                )
                                or (self.secure_connection == "SASL_SSL")
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (
                                    hasattr(self.secure_connection, "value")
                                    and self.secure_connection.value == "SCRAM-SHA-256"
                                )
                                or (self.secure_connection == "SCRAM-SHA-256")
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (
                                    hasattr(self.secure_connection, "value")
                                    and self.secure_connection.value == "SCRAM-SHA-512"
                                )
                                or (self.secure_connection == "SCRAM-SHA-512")
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                or (self.secure_connection == "SSL")
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (
                                    hasattr(self.secure_connection, "value")
                                    and self.secure_connection.value == "kerberos"
                                )
                                or (self.secure_connection == "kerberos")
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("truststore_location")
        )
        (
            include.add("schema_registry_type")
            if (((((self.use_schema_registry_for_message_format)))) or (self.use_schema_registry_for_message_format))
            else exclude.add("schema_registry_type")
        )
        (
            include.add("oauth_bearer_authentication")
            if (
                (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_OAUTHBEARER"
                                    )
                                    or (self.secure_connection == "SASL_OAUTHBEARER")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_OAUTHBEARER"
                                    )
                                    or (self.secure_connection == "SASL_OAUTHBEARER")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("oauth_bearer_authentication")
        )
        include.add("registry_url") if (self.use_schema_registry_for_message_format) else exclude.add("registry_url")
        (
            include.add("registry_username")
            if (
                (
                    (
                        (
                            self.schema_registry_authentication
                            and (
                                (
                                    hasattr(self.schema_registry_authentication, "value")
                                    and self.schema_registry_authentication.value == "user_credentials"
                                )
                                or (self.schema_registry_authentication == "user_credentials")
                            )
                        )
                    )
                )
                and (self.use_schema_registry_for_message_format)
                and (not self.defer_credentials)
            )
            else exclude.add("registry_username")
        )
        (
            include.add("key_chain_pem")
            if (
                (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("key_chain_pem")
        )
        (
            include.add("registry_truststore_pem")
            if (
                (
                    (
                        (
                            self.schema_registry_secure
                            and (
                                (
                                    hasattr(self.schema_registry_secure, "value")
                                    and self.schema_registry_secure.value == "kerberos"
                                )
                                or (self.schema_registry_secure == "kerberos")
                            )
                        )
                    )
                    or (
                        (
                            self.schema_registry_secure
                            and (
                                (
                                    hasattr(self.schema_registry_secure, "value")
                                    and self.schema_registry_secure.value == "ssl"
                                )
                                or (self.schema_registry_secure == "ssl")
                            )
                        )
                    )
                )
                and (self.use_schema_registry_for_message_format)
                and (not self.defer_credentials)
            )
            else exclude.add("registry_truststore_pem")
        )
        (
            include.add("legacy_security_conf")
            if (
                (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_OAUTHBEARER"
                                    )
                                    or (self.secure_connection == "SASL_OAUTHBEARER")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "kerberos"
                                    )
                                    or (self.secure_connection == "kerberos")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_OAUTHBEARER"
                                    )
                                    or (self.secure_connection == "SASL_OAUTHBEARER")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "kerberos"
                                    )
                                    or (self.secure_connection == "kerberos")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("legacy_security_conf")
        )
        (
            include.add("schema_registry_secure")
            if (((((self.use_schema_registry_for_message_format)))) or (self.use_schema_registry_for_message_format))
            else exclude.add("schema_registry_secure")
        )
        (
            include.add("registry_key_password")
            if (
                (
                    (
                        (
                            self.schema_registry_secure
                            and (
                                (
                                    hasattr(self.schema_registry_secure, "value")
                                    and self.schema_registry_secure.value == "ssl"
                                )
                                or (self.schema_registry_secure == "ssl")
                            )
                        )
                    )
                )
                and (self.use_schema_registry_for_message_format)
                and (not self.defer_credentials)
            )
            else exclude.add("registry_key_password")
        )
        (
            include.add("additional_properties")
            if (
                (
                    (
                        (
                            (
                                self.oauth_bearer_authentication
                                and (
                                    (
                                        hasattr(self.oauth_bearer_authentication, "value")
                                        and self.oauth_bearer_authentication.value == "SASL_OAUTH2"
                                    )
                                    or (self.oauth_bearer_authentication == "SASL_OAUTH2")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.oauth_bearer_authentication
                                and (
                                    (
                                        hasattr(self.oauth_bearer_authentication, "value")
                                        and self.oauth_bearer_authentication.value == "SASL_OAUTH2"
                                    )
                                    or (self.oauth_bearer_authentication == "SASL_OAUTH2")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("additional_properties")
        )
        (
            include.add("keystore_location")
            if (
                (
                    (((self.legacy_security_conf)))
                    and (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                                    or (self.secure_connection == "SSL")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (((self.legacy_security_conf)))
                    and (
                        self.secure_connection
                        and (
                            (hasattr(self.secure_connection, "value") and self.secure_connection.value == "SSL")
                            or (self.secure_connection == "SSL")
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("keystore_location")
        )
        (
            include.add("scope")
            if (
                (
                    (
                        (
                            (
                                self.oauth_bearer_authentication
                                and (
                                    (
                                        hasattr(self.oauth_bearer_authentication, "value")
                                        and self.oauth_bearer_authentication.value == "SASL_OAUTH2"
                                    )
                                    or (self.oauth_bearer_authentication == "SASL_OAUTH2")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    (
                        (
                            (
                                self.oauth_bearer_authentication
                                and (
                                    (
                                        hasattr(self.oauth_bearer_authentication, "value")
                                        and self.oauth_bearer_authentication.value == "SASL_OAUTH2"
                                    )
                                    or (self.oauth_bearer_authentication == "SASL_OAUTH2")
                                )
                            )
                        )
                    )
                    and (not self.defer_credentials)
                )
            )
            else exclude.add("scope")
        )
        (
            include.add("username")
            if (
                (
                    (
                        (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_PLAIN"
                                    )
                                    or (self.secure_connection == "SASL_PLAIN")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SASL_SSL"
                                    )
                                    or (self.secure_connection == "SASL_SSL")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-256"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-256")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "SCRAM-SHA-512"
                                    )
                                    or (self.secure_connection == "SCRAM-SHA-512")
                                )
                            )
                        )
                        or (
                            (
                                self.secure_connection
                                and (
                                    (
                                        hasattr(self.secure_connection, "value")
                                        and self.secure_connection.value == "kerberos"
                                    )
                                    or (self.secure_connection == "kerberos")
                                )
                            )
                        )
                    )
                    and ((not self.defer_credentials))
                )
                or (
                    ((not self.defer_credentials))
                    and (
                        (
                            (
                                (
                                    self.secure_connection
                                    and (
                                        (
                                            hasattr(self.secure_connection, "value")
                                            and self.secure_connection.value == "SASL_PLAIN"
                                        )
                                        or (self.secure_connection == "SASL_PLAIN")
                                    )
                                )
                            )
                            or (
                                (
                                    self.secure_connection
                                    and (
                                        (
                                            hasattr(self.secure_connection, "value")
                                            and self.secure_connection.value == "SASL_SSL"
                                        )
                                        or (self.secure_connection == "SASL_SSL")
                                    )
                                )
                            )
                            or (
                                (
                                    self.secure_connection
                                    and (
                                        (
                                            hasattr(self.secure_connection, "value")
                                            and self.secure_connection.value == "SCRAM-SHA-256"
                                        )
                                        or (self.secure_connection == "SCRAM-SHA-256")
                                    )
                                )
                            )
                            or (
                                (
                                    self.secure_connection
                                    and (
                                        (
                                            hasattr(self.secure_connection, "value")
                                            and self.secure_connection.value == "SCRAM-SHA-512"
                                        )
                                        or (self.secure_connection == "SCRAM-SHA-512")
                                    )
                                )
                            )
                            or (
                                (
                                    self.secure_connection
                                    and (
                                        (
                                            hasattr(self.secure_connection, "value")
                                            and self.secure_connection.value == "kerberos"
                                        )
                                        or (self.secure_connection == "kerberos")
                                    )
                                )
                            )
                        )
                        or (
                            self.secure_connection
                            and (
                                (
                                    hasattr(self.secure_connection, "value")
                                    and self.secure_connection.value == "SASL_SSL"
                                )
                                or (self.secure_connection == "SASL_SSL")
                            )
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
        (
            include.add("registry_truststore_password")
            if (self.hidden_dummy_property1)
            else exclude.add("registry_truststore_password")
        )
        (
            include.add("registry_keystore_password")
            if (self.hidden_dummy_property1)
            else exclude.add("registry_keystore_password")
        )
        (
            include.add("legacy_registry_security_conf")
            if (self.hidden_dummy_property1)
            else exclude.add("legacy_registry_security_conf")
        )
        include.add("truststore_location") if (self.hidden_dummy_property1) else exclude.add("truststore_location")
        include.add("keytab") if (self.hidden_dummy_property1) else exclude.add("keytab")
        (
            include.add("registry_keystore_location")
            if (self.hidden_dummy_property1)
            else exclude.add("registry_keystore_location")
        )
        include.add("keystore_password") if (self.hidden_dummy_property1) else exclude.add("keystore_password")
        include.add("legacy_security_conf") if (self.hidden_dummy_property1) else exclude.add("legacy_security_conf")
        include.add("truststore_password") if (self.hidden_dummy_property1) else exclude.add("truststore_password")
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        (
            include.add("registry_truststore_location")
            if (self.hidden_dummy_property1)
            else exclude.add("registry_truststore_location")
        )
        include.add("keystore_location") if (self.hidden_dummy_property1) else exclude.add("keystore_location")
        include.add("registry_keytab") if (self.hidden_dummy_property1) else exclude.add("registry_keytab")
        (
            include.add("registry_principal_name")
            if (self.hidden_dummy_property1)
            else exclude.add("registry_principal_name")
        )

        (
            include.add("server_url")
            if (
                (
                    self.oauth_bearer_authentication
                    and (
                        (
                            hasattr(self.oauth_bearer_authentication, "value")
                            and self.oauth_bearer_authentication.value
                            and "SASL_OAUTH2" in str(self.oauth_bearer_authentication.value)
                        )
                        or ("SASL_OAUTH2" in str(self.oauth_bearer_authentication))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.oauth_bearer_authentication
                    and (
                        (
                            hasattr(self.oauth_bearer_authentication, "value")
                            and self.oauth_bearer_authentication.value
                            and "SASL_OAUTH2" in str(self.oauth_bearer_authentication.value)
                        )
                        or ("SASL_OAUTH2" in str(self.oauth_bearer_authentication))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("server_url")
        )
        (
            include.add("schema_registry_type")
            if (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            or (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            else exclude.add("schema_registry_type")
        )
        (
            include.add("schema_registry_secure")
            if (
                self.schema_registry_type
                and (
                    (hasattr(self.schema_registry_type, "value") and self.schema_registry_type.value == "confluent")
                    or (self.schema_registry_type == "confluent")
                )
            )
            and (
                self.schema_registry_type
                and (
                    (
                        hasattr(self.schema_registry_type, "value")
                        and self.schema_registry_type.value == "eventstreamsconfluent"
                    )
                    or (self.schema_registry_type == "eventstreamsconfluent")
                )
            )
            else exclude.add("schema_registry_secure")
        )
        (
            include.add("keystore_location")
            if (
                (self.legacy_security_conf and "true" in str(self.legacy_security_conf))
                and (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (self.legacy_security_conf and "true" in str(self.legacy_security_conf))
                and (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("keystore_location")
        )
        (
            include.add("key_password")
            if (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("key_password")
        )
        (
            include.add("registry_password")
            if (
                self.schema_registry_authentication
                and (
                    (
                        hasattr(self.schema_registry_authentication, "value")
                        and self.schema_registry_authentication.value
                        and "user_credentials" in str(self.schema_registry_authentication.value)
                    )
                    or ("user_credentials" in str(self.schema_registry_authentication))
                )
            )
            and (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            and (not self.defer_credentials)
            else exclude.add("registry_password")
        )
        (
            include.add("additional_properties")
            if (
                (
                    self.oauth_bearer_authentication
                    and (
                        (
                            hasattr(self.oauth_bearer_authentication, "value")
                            and self.oauth_bearer_authentication.value
                            and "SASL_OAUTH2" in str(self.oauth_bearer_authentication.value)
                        )
                        or ("SASL_OAUTH2" in str(self.oauth_bearer_authentication))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.oauth_bearer_authentication
                    and (
                        (
                            hasattr(self.oauth_bearer_authentication, "value")
                            and self.oauth_bearer_authentication.value
                            and "SASL_OAUTH2" in str(self.oauth_bearer_authentication.value)
                        )
                        or ("SASL_OAUTH2" in str(self.oauth_bearer_authentication))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("additional_properties")
        )
        (
            include.add("registry_username")
            if (
                self.schema_registry_authentication
                and (
                    (
                        hasattr(self.schema_registry_authentication, "value")
                        and self.schema_registry_authentication.value
                        and "user_credentials" in str(self.schema_registry_authentication.value)
                    )
                    or ("user_credentials" in str(self.schema_registry_authentication))
                )
            )
            and (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            and (not self.defer_credentials)
            else exclude.add("registry_username")
        )
        (
            include.add("registry_key_pem")
            if (
                self.schema_registry_secure
                and (
                    (
                        hasattr(self.schema_registry_secure, "value")
                        and self.schema_registry_secure.value
                        and "ssl" in str(self.schema_registry_secure.value)
                    )
                    or ("ssl" in str(self.schema_registry_secure))
                )
            )
            and (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            and (not self.defer_credentials)
            else exclude.add("registry_key_pem")
        )
        (
            include.add("registry_truststore_pem")
            if (
                self.schema_registry_secure
                and (
                    (
                        hasattr(self.schema_registry_secure, "value")
                        and self.schema_registry_secure.value
                        and "kerberos" in str(self.schema_registry_secure.value)
                    )
                    or ("kerberos" in str(self.schema_registry_secure))
                )
                and self.schema_registry_secure
                and (
                    (
                        hasattr(self.schema_registry_secure, "value")
                        and self.schema_registry_secure.value
                        and "ssl" in str(self.schema_registry_secure.value)
                    )
                    or ("ssl" in str(self.schema_registry_secure))
                )
            )
            and (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            and (not self.defer_credentials)
            else exclude.add("registry_truststore_pem")
        )
        (
            include.add("registry_keytab")
            if (
                (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "kerberos" in str(self.schema_registry_secure.value)
                        )
                        or ("kerberos" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "kerberos" in str(self.schema_registry_secure.value)
                        )
                        or ("kerberos" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
                and (not self.defer_credentials)
            )
            else exclude.add("registry_keytab")
        )
        (
            include.add("legacy_registry_security_conf")
            if (
                (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "kerberos" in str(self.schema_registry_secure.value)
                        )
                        or ("kerberos" in str(self.schema_registry_secure))
                    )
                    and self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "ssl" in str(self.schema_registry_secure.value)
                        )
                        or ("ssl" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
            )
            or (
                (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "kerberos" in str(self.schema_registry_secure.value)
                        )
                        or ("kerberos" in str(self.schema_registry_secure))
                    )
                    and self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "ssl" in str(self.schema_registry_secure.value)
                        )
                        or ("ssl" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
            )
            else exclude.add("legacy_registry_security_conf")
        )
        (
            include.add("schema_registry_secure")
            if (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            or (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            else exclude.add("schema_registry_secure")
        )
        (
            include.add("client_secret")
            if (
                (
                    self.oauth_bearer_authentication
                    and (
                        (
                            hasattr(self.oauth_bearer_authentication, "value")
                            and self.oauth_bearer_authentication.value
                            and "SASL_OAUTH2" in str(self.oauth_bearer_authentication.value)
                        )
                        or ("SASL_OAUTH2" in str(self.oauth_bearer_authentication))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.oauth_bearer_authentication
                    and (
                        (
                            hasattr(self.oauth_bearer_authentication, "value")
                            and self.oauth_bearer_authentication.value
                            and "SASL_OAUTH2" in str(self.oauth_bearer_authentication.value)
                        )
                        or ("SASL_OAUTH2" in str(self.oauth_bearer_authentication))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("client_secret")
        )
        (
            include.add("key_pem")
            if (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("key_pem")
        )
        (
            include.add("key_chain_pem")
            if (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("key_chain_pem")
        )
        (
            include.add("truststore_location")
            if (
                (self.legacy_security_conf and "true" in str(self.legacy_security_conf))
                and (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_OAUTHBEARER" in str(self.secure_connection.value)
                        )
                        or ("SASL_OAUTHBEARER" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (self.legacy_security_conf and "true" in str(self.legacy_security_conf))
                and (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_OAUTHBEARER" in str(self.secure_connection.value)
                        )
                        or ("SASL_OAUTHBEARER" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("truststore_location")
        )
        (
            include.add("scope")
            if (
                (
                    self.oauth_bearer_authentication
                    and (
                        (
                            hasattr(self.oauth_bearer_authentication, "value")
                            and self.oauth_bearer_authentication.value
                            and "SASL_OAUTH2" in str(self.oauth_bearer_authentication.value)
                        )
                        or ("SASL_OAUTH2" in str(self.oauth_bearer_authentication))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.oauth_bearer_authentication
                    and (
                        (
                            hasattr(self.oauth_bearer_authentication, "value")
                            and self.oauth_bearer_authentication.value
                            and "SASL_OAUTH2" in str(self.oauth_bearer_authentication.value)
                        )
                        or ("SASL_OAUTH2" in str(self.oauth_bearer_authentication))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("scope")
        )
        (
            include.add("keytab")
            if (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("keytab")
        )
        (
            include.add("registry_key_password")
            if (
                self.schema_registry_secure
                and (
                    (
                        hasattr(self.schema_registry_secure, "value")
                        and self.schema_registry_secure.value
                        and "ssl" in str(self.schema_registry_secure.value)
                    )
                    or ("ssl" in str(self.schema_registry_secure))
                )
            )
            and (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            and (not self.defer_credentials)
            else exclude.add("registry_key_password")
        )
        (
            include.add("registry_truststore_location")
            if (
                (self.legacy_registry_security_conf and "true" in str(self.legacy_registry_security_conf))
                and (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "kerberos" in str(self.schema_registry_secure.value)
                        )
                        or ("kerberos" in str(self.schema_registry_secure))
                    )
                    and self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "ssl" in str(self.schema_registry_secure.value)
                        )
                        or ("ssl" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
            )
            or (
                (self.legacy_registry_security_conf and "true" in str(self.legacy_registry_security_conf))
                and (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "kerberos" in str(self.schema_registry_secure.value)
                        )
                        or ("kerberos" in str(self.schema_registry_secure))
                    )
                    and self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "ssl" in str(self.schema_registry_secure.value)
                        )
                        or ("ssl" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
            )
            else exclude.add("registry_truststore_location")
        )
        (
            include.add("registry_keystore_password")
            if (
                (self.legacy_registry_security_conf and "true" in str(self.legacy_registry_security_conf))
                and (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "ssl" in str(self.schema_registry_secure.value)
                        )
                        or ("ssl" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
            )
            or (
                (self.legacy_registry_security_conf and "true" in str(self.legacy_registry_security_conf))
                and (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "ssl" in str(self.schema_registry_secure.value)
                        )
                        or ("ssl" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
            )
            else exclude.add("registry_keystore_password")
        )
        (
            include.add("schema_registry_authentication")
            if (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            or (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            else exclude.add("schema_registry_authentication")
        )
        (
            include.add("registry_url")
            if (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            else exclude.add("registry_url")
        )
        (
            include.add("legacy_security_conf")
            if (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_OAUTHBEARER" in str(self.secure_connection.value)
                        )
                        or ("SASL_OAUTHBEARER" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_OAUTHBEARER" in str(self.secure_connection.value)
                        )
                        or ("SASL_OAUTHBEARER" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("legacy_security_conf")
        )
        (
            include.add("password")
            if (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_PLAIN" in str(self.secure_connection.value)
                        )
                        or ("SASL_PLAIN" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (not self.defer_credentials)
                and (
                    (
                        self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "SASL_PLAIN" in str(self.secure_connection.value)
                            )
                            or ("SASL_PLAIN" in str(self.secure_connection))
                        )
                        or self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "SASL_SSL" in str(self.secure_connection.value)
                            )
                            or ("SASL_SSL" in str(self.secure_connection))
                        )
                        or self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "SCRAM-SHA-256" in str(self.secure_connection.value)
                            )
                            or ("SCRAM-SHA-256" in str(self.secure_connection))
                        )
                        or self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "SCRAM-SHA-512" in str(self.secure_connection.value)
                            )
                            or ("SCRAM-SHA-512" in str(self.secure_connection))
                        )
                    )
                    or (
                        self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "SASL_SSL" in str(self.secure_connection.value)
                            )
                            or ("SASL_SSL" in str(self.secure_connection))
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_PLAIN" in str(self.secure_connection.value)
                        )
                        or ("SASL_PLAIN" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (not self.defer_credentials)
                and (
                    (
                        self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "SASL_PLAIN" in str(self.secure_connection.value)
                            )
                            or ("SASL_PLAIN" in str(self.secure_connection))
                        )
                        or self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "SASL_SSL" in str(self.secure_connection.value)
                            )
                            or ("SASL_SSL" in str(self.secure_connection))
                        )
                        or self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "SCRAM-SHA-256" in str(self.secure_connection.value)
                            )
                            or ("SCRAM-SHA-256" in str(self.secure_connection))
                        )
                        or self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "SCRAM-SHA-512" in str(self.secure_connection.value)
                            )
                            or ("SCRAM-SHA-512" in str(self.secure_connection))
                        )
                        or self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "kerberos" in str(self.secure_connection.value)
                            )
                            or ("kerberos" in str(self.secure_connection))
                        )
                    )
                    or (
                        self.secure_connection
                        and (
                            (
                                hasattr(self.secure_connection, "value")
                                and self.secure_connection.value
                                and "SASL_SSL" in str(self.secure_connection.value)
                            )
                            or ("SASL_SSL" in str(self.secure_connection))
                        )
                    )
                )
            )
            else exclude.add("username")
        )
        (
            include.add("truststore_pem")
            if (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_OAUTHBEARER" in str(self.secure_connection.value)
                        )
                        or ("SASL_OAUTHBEARER" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_OAUTHBEARER" in str(self.secure_connection.value)
                        )
                        or ("SASL_OAUTHBEARER" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("truststore_pem")
        )
        (
            include.add("registry_key_chain_pem")
            if (
                self.schema_registry_secure
                and (
                    (
                        hasattr(self.schema_registry_secure, "value")
                        and self.schema_registry_secure.value
                        and "ssl" in str(self.schema_registry_secure.value)
                    )
                    or ("ssl" in str(self.schema_registry_secure))
                )
            )
            and (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            and (not self.defer_credentials)
            else exclude.add("registry_key_chain_pem")
        )
        (
            include.add("oauth_bearer_authentication")
            if (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_OAUTHBEARER" in str(self.secure_connection.value)
                        )
                        or ("SASL_OAUTHBEARER" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_OAUTHBEARER" in str(self.secure_connection.value)
                        )
                        or ("SASL_OAUTHBEARER" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("oauth_bearer_authentication")
        )
        (
            include.add("client_id")
            if (
                (
                    self.oauth_bearer_authentication
                    and (
                        (
                            hasattr(self.oauth_bearer_authentication, "value")
                            and self.oauth_bearer_authentication.value
                            and "SASL_OAUTH2" in str(self.oauth_bearer_authentication.value)
                        )
                        or ("SASL_OAUTH2" in str(self.oauth_bearer_authentication))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (
                    self.oauth_bearer_authentication
                    and (
                        (
                            hasattr(self.oauth_bearer_authentication, "value")
                            and self.oauth_bearer_authentication.value
                            and "SASL_OAUTH2" in str(self.oauth_bearer_authentication.value)
                        )
                        or ("SASL_OAUTH2" in str(self.oauth_bearer_authentication))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("client_id")
        )
        (
            include.add("registry_keystore_location")
            if (
                (self.legacy_registry_security_conf and "true" in str(self.legacy_registry_security_conf))
                and (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "ssl" in str(self.schema_registry_secure.value)
                        )
                        or ("ssl" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
            )
            or (
                (self.legacy_registry_security_conf and "true" in str(self.legacy_registry_security_conf))
                and (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "ssl" in str(self.schema_registry_secure.value)
                        )
                        or ("ssl" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
            )
            else exclude.add("registry_keystore_location")
        )
        (
            include.add("registry_principal_name")
            if (
                self.schema_registry_secure
                and (
                    (
                        hasattr(self.schema_registry_secure, "value")
                        and self.schema_registry_secure.value
                        and "kerberos" in str(self.schema_registry_secure.value)
                    )
                    or ("kerberos" in str(self.schema_registry_secure))
                )
            )
            and (
                self.use_schema_registry_for_message_format
                and "true" in str(self.use_schema_registry_for_message_format)
            )
            and (not self.defer_credentials)
            else exclude.add("registry_principal_name")
        )
        (
            include.add("truststore_password")
            if (
                (self.legacy_security_conf and "true" in str(self.legacy_security_conf))
                and (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_OAUTHBEARER" in str(self.secure_connection.value)
                        )
                        or ("SASL_OAUTHBEARER" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (self.legacy_security_conf and "true" in str(self.legacy_security_conf))
                and (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_OAUTHBEARER" in str(self.secure_connection.value)
                        )
                        or ("SASL_OAUTHBEARER" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "kerberos" in str(self.secure_connection.value)
                        )
                        or ("kerberos" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("truststore_password")
        )
        (
            include.add("keystore_password")
            if (
                (self.legacy_security_conf and "true" in str(self.legacy_security_conf))
                and (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SASL_SSL" in str(self.secure_connection.value)
                        )
                        or ("SASL_SSL" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-256" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-256" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SCRAM-SHA-512" in str(self.secure_connection.value)
                        )
                        or ("SCRAM-SHA-512" in str(self.secure_connection))
                    )
                    and self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            or (
                (self.legacy_security_conf and "true" in str(self.legacy_security_conf))
                and (
                    self.secure_connection
                    and (
                        (
                            hasattr(self.secure_connection, "value")
                            and self.secure_connection.value
                            and "SSL" in str(self.secure_connection.value)
                        )
                        or ("SSL" in str(self.secure_connection))
                    )
                )
                and (not self.defer_credentials)
            )
            else exclude.add("keystore_password")
        )
        (
            include.add("registry_truststore_password")
            if (
                (self.legacy_registry_security_conf and "true" in str(self.legacy_registry_security_conf))
                and (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "kerberos" in str(self.schema_registry_secure.value)
                        )
                        or ("kerberos" in str(self.schema_registry_secure))
                    )
                    and self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "ssl" in str(self.schema_registry_secure.value)
                        )
                        or ("ssl" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
            )
            or (
                (self.legacy_registry_security_conf and "true" in str(self.legacy_registry_security_conf))
                and (
                    self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "kerberos" in str(self.schema_registry_secure.value)
                        )
                        or ("kerberos" in str(self.schema_registry_secure))
                    )
                    and self.schema_registry_secure
                    and (
                        (
                            hasattr(self.schema_registry_secure, "value")
                            and self.schema_registry_secure.value
                            and "ssl" in str(self.schema_registry_secure.value)
                        )
                        or ("ssl" in str(self.schema_registry_secure))
                    )
                )
                and (
                    self.use_schema_registry_for_message_format
                    and "true" in str(self.use_schema_registry_for_message_format)
                )
            )
            else exclude.add("registry_truststore_password")
        )
        (
            include.add("schema_registry_secure")
            if (
                self.schema_registry_type
                and (
                    (hasattr(self.schema_registry_type, "value") and self.schema_registry_type.value == "cloudera")
                    or (self.schema_registry_type == "cloudera")
                )
            )
            else exclude.add("schema_registry_secure")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
