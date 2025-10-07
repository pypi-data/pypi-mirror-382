from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import SNOWFLAKE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    key_pair = "key_pair"
    username_password = "username_password"


class LineageExtractionType(Enum):
    account_usage = "account_usage"
    information_schema = "information_schema"


class SnowflakeConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "2fc1372f-b58c-4d45-b0c4-dfb32a1c78a5"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    account_name: str = Field(None, alias="account_name")
    authentication_method: SNOWFLAKE_CONNECTION.AuthMethod | None = Field(
        SNOWFLAKE_CONNECTION.AuthMethod.username_password, alias="auth_method"
    )
    url_endpoint: str | None = Field(None, alias="authenticator_url")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    database: str = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    error_on_nondeterministic_merge: bool | None = Field(None, alias="error_on_nondeterministic_merge")
    hostname_or_ip_address: str | None = Field("@account_name@.snowflakecomputing.com", alias="host")
    keep_client_session_alive: bool | None = Field(None, alias="keep_alive")
    heartbeat_frequency: int | None = Field(None, alias="keep_alive_heartbeat_frequency")
    key_passphrase: str | None = Field(None, alias="key_passphrase")
    lineage_extraction_type: SNOWFLAKE_CONNECTION.LineageExtractionType | None = Field(
        None, alias="lineage_extraction_type"
    )
    password: str = Field(None, alias="password")
    port: int | None = Field(443, alias="port")
    private_key: str = Field(None, alias="private_key")
    query_timeout: int | None = Field(None, alias="query_timeout")
    role: str | None = Field(None, alias="role")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    warehouse: str = Field(None, alias="warehouse")
    properties: str | None = Field(None, alias="properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("key_passphrase")
            if (
                (
                    ((not self.defer_credentials))
                    and ((not self.password))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "key_pair"
                                    )
                                    or (self.authentication_method == "key_pair")
                                )
                            )
                        )
                        or (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "key_pair_path"
                                    )
                                    or (self.authentication_method == "key_pair_path")
                                )
                            )
                        )
                    )
                )
                or (
                    ((not self.defer_credentials))
                    and (not self.password)
                    and (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "key_pair"
                            )
                            or (self.authentication_method == "key_pair")
                        )
                    )
                )
            )
            else exclude.add("key_passphrase")
        )
        (
            include.add("private_key")
            if (
                ((not self.defer_credentials))
                and (not self.password)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "key_pair"
                        )
                        or (self.authentication_method == "key_pair")
                    )
                )
            )
            else exclude.add("private_key")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (not self.private_key)
                and (not self.key_passphrase)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "username_password"
                        )
                        or (self.authentication_method == "username_password")
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                (
                    ((not self.defer_credentials))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "key_pair"
                                    )
                                    or (self.authentication_method == "key_pair")
                                )
                            )
                        )
                        or (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "key_pair_path"
                                    )
                                    or (self.authentication_method == "key_pair_path")
                                )
                            )
                        )
                        or (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "oauth"
                                    )
                                    or (self.authentication_method == "oauth")
                                )
                            )
                        )
                        or (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "username_password"
                                    )
                                    or (self.authentication_method == "username_password")
                                )
                            )
                        )
                    )
                )
                or (
                    ((not self.defer_credentials))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "key_pair"
                                    )
                                    or (self.authentication_method == "key_pair")
                                )
                            )
                        )
                        or (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "username_password"
                                )
                                or (self.authentication_method == "username_password")
                            )
                        )
                    )
                )
            )
            else exclude.add("username")
        )
        (
            include.add("key_passphrase")
            if (
                ((not self.defer_credentials))
                and (not self.password)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "key_pair"
                        )
                        or (self.authentication_method == "key_pair")
                    )
                )
            )
            else exclude.add("key_passphrase")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "key_pair"
                                )
                                or (self.authentication_method == "key_pair")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "username_password"
                            )
                            or (self.authentication_method == "username_password")
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
        include.add("properties") if (self.hidden_dummy_property1) else exclude.add("properties")

        (
            include.add("key_passphrase")
            if (
                (not self.defer_credentials)
                and (not self.password)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "key_pair" in str(self.authentication_method.value)
                        )
                        or ("key_pair" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "key_pair_path" in str(self.authentication_method.value)
                        )
                        or ("key_pair_path" in str(self.authentication_method))
                    )
                )
            )
            or (
                (not self.defer_credentials)
                and (not self.password)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "key_pair" in str(self.authentication_method.value)
                        )
                        or ("key_pair" in str(self.authentication_method))
                    )
                )
            )
            else exclude.add("key_passphrase")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (not self.private_key)
            and (not self.key_passphrase)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password" in str(self.authentication_method.value)
                    )
                    or ("username_password" in str(self.authentication_method))
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "key_pair" in str(self.authentication_method.value)
                        )
                        or ("key_pair" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "key_pair_path" in str(self.authentication_method.value)
                        )
                        or ("key_pair_path" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "oauth" in str(self.authentication_method.value)
                        )
                        or ("oauth" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "username_password" in str(self.authentication_method.value)
                        )
                        or ("username_password" in str(self.authentication_method))
                    )
                )
            )
            or (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "key_pair" in str(self.authentication_method.value)
                        )
                        or ("key_pair" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "username_password" in str(self.authentication_method.value)
                        )
                        or ("username_password" in str(self.authentication_method))
                    )
                )
            )
            else exclude.add("username")
        )
        (
            include.add("private_key")
            if (not self.defer_credentials)
            and (not self.password)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "key_pair" in str(self.authentication_method.value)
                    )
                    or ("key_pair" in str(self.authentication_method))
                )
            )
            else exclude.add("private_key")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
