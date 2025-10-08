from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from typing import ClassVar


class ConnectionType(Enum):
    application_server = "application_server"
    load_balancing = "load_balancing"
    snc_application_server = "snc_application_server"
    snc_load_balancing = "snc_load_balancing"


class SncQop(Enum):
    auth_only = "1"
    auth_integrity = "2"
    auth_integrity_privacy = "3"
    global_default = "8"
    max_protection = "9"


class SapbapiConn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "sapbapi"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    connection_type: ConnectionType = Field(ConnectionType.application_server, alias="connection_type")
    jar_uris: str | None = Field(None, alias="jar_uris")
    gateway_url: str | None = Field(None, alias="gateway_url")
    sap_application_server: str = Field(None, alias="sap_application_server")
    sap_application_system_number: str = Field(None, alias="sap_application_system_number")
    message_server: str = Field(None, alias="message_server")
    use_system_number: bool | None = Field(True, alias="use_system_number")
    system_number: str = Field(None, alias="system_number")
    system_id: str = Field(None, alias="system_id")
    group: str = Field(None, alias="group")
    sap_router: str | None = Field(None, alias="sap_router")
    snc_name: str = Field(None, alias="snc_name")
    snc_partner_name: str = Field(None, alias="snc_partner_name")
    snc_qop: SncQop | None = Field(SncQop.auth_integrity_privacy, alias="snc_qop")
    custom_namespace: str | None = Field("", alias="custom_namespace")
    isx509enabled: bool | None = Field(False, alias="isx509enabled")
    x509_cert: str = Field(None, alias="x509_cert")
    username: str = Field(None, alias="username")
    password: str = Field(None, alias="password")
    client_number: str = Field(None, alias="client_number")
    language: str = Field(None, alias="language")
    cluster_access_token: str = Field(None, alias="cluster_access_token")
    cluster_user_name: str = Field(None, alias="cluster_user_name")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (include.add("client_number") if (not self.defer_credentials) else exclude.add("client_number"))
        (
            include.add("system_number")
            if (self.use_system_number)
            and (
                (self.connection_type.value == "load_balancing") or (self.connection_type.value == "snc_load_balancing")
            )
            else exclude.add("system_number")
        )
        (
            include.add("use_system_number")
            if (
                (self.connection_type.value == "load_balancing") or (self.connection_type.value == "snc_load_balancing")
            )
            else exclude.add("use_system_number")
        )
        (
            include.add("system_id")
            if (not self.use_system_number)
            and (
                (self.connection_type.value == "load_balancing") or (self.connection_type.value == "snc_load_balancing")
            )
            else exclude.add("system_id")
        )
        (
            include.add("sap_application_system_number")
            if (
                (self.connection_type.value == "application_server")
                or (self.connection_type.value == "snc_application_server")
            )
            else exclude.add("sap_application_system_number")
        )
        (include.add("language") if (not self.defer_credentials) else exclude.add("language"))
        (
            include.add("isx509enabled")
            if (
                (self.connection_type.value == "snc_application_server")
                or (self.connection_type.value == "snc_load_balancing")
            )
            else exclude.add("isx509enabled")
        )
        (
            include.add("snc_partner_name")
            if (
                (self.connection_type.value == "snc_application_server")
                or (self.connection_type.value == "snc_load_balancing")
            )
            else exclude.add("snc_partner_name")
        )
        (
            include.add("snc_name")
            if (
                (self.connection_type.value == "snc_application_server")
                or (self.connection_type.value == "snc_load_balancing")
            )
            else exclude.add("snc_name")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                (
                    (self.connection_type.value == "application_server")
                    or (self.connection_type.value == "load_balancing")
                )
                or (not self.isx509enabled)
            )
            else exclude.add("password")
        )
        (
            include.add("sap_application_server")
            if (
                (self.connection_type.value == "application_server")
                or (self.connection_type.value == "snc_application_server")
            )
            else exclude.add("sap_application_server")
        )
        (
            include.add("message_server")
            if (
                (self.connection_type.value == "load_balancing") or (self.connection_type.value == "snc_load_balancing")
            )
            else exclude.add("message_server")
        )
        (
            include.add("x509_cert")
            if (self.isx509enabled)
            and (
                (self.connection_type.value == "snc_application_server")
                or (self.connection_type.value == "snc_load_balancing")
            )
            else exclude.add("x509_cert")
        )
        (
            include.add("snc_qop")
            if (
                (self.connection_type.value == "snc_application_server")
                or (self.connection_type.value == "snc_load_balancing")
            )
            else exclude.add("snc_qop")
        )
        (
            include.add("group")
            if (
                (self.connection_type.value == "load_balancing") or (self.connection_type.value == "snc_load_balancing")
            )
            else exclude.add("group")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                (
                    (self.connection_type.value == "application_server")
                    or (self.connection_type.value == "load_balancing")
                )
                or (not self.isx509enabled)
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

        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls(**properties)
