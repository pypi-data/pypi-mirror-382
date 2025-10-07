from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import SAPDELTAEXTRACT_CONNECTION
from pydantic import ConfigDict, Field
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


class SapdeltaextractConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "ec42cd4a-18ab-469c-bfd7-f6dc52e1db26"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    client_number: str = Field(None, alias="client_number")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    connection_type: SAPDELTAEXTRACT_CONNECTION.ConnectionType = Field(
        SAPDELTAEXTRACT_CONNECTION.ConnectionType.application_server, alias="connection_type"
    )
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    gateway_url: str | None = Field(None, alias="gateway_url")
    group: str = Field(None, alias="group")
    enable_x_509_certificate: bool | None = Field(False, alias="isx509enabled")
    jar_uris: str | None = Field(None, alias="jar_uris")
    language: str = Field(None, alias="language")
    message_server: str = Field(None, alias="message_server")
    sap_password: str | None = Field(None, alias="password")
    application_server: str = Field(None, alias="sap_application_server")
    sap_application_system_number: str = Field(None, alias="sap_application_system_number")
    sap_router: str | None = Field(None, alias="sap_router")
    snc_name: str = Field(None, alias="snc_name")
    snc_partner_name: str = Field(None, alias="snc_partner_name")
    snc_qop: SAPDELTAEXTRACT_CONNECTION.SncQop | None = Field(
        SAPDELTAEXTRACT_CONNECTION.SncQop.auth_integrity_privacy, alias="snc_qop"
    )
    odp_subscriber_name: str = Field("", alias="subscriber_name")
    system_id: str = Field(None, alias="system_id")
    system_number: str = Field(None, alias="system_number")
    use_system_number: bool | None = Field(True, alias="use_system_number")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    x_509_certificate: str = Field(None, alias="x509_cert")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("client_number") if (not self.defer_credentials) else exclude.add("client_number")
        (
            include.add("system_number")
            if (
                ((self.use_system_number))
                and (
                    (
                        (
                            self.connection_type
                            and (
                                (
                                    hasattr(self.connection_type, "value")
                                    and self.connection_type.value == "load_balancing"
                                )
                                or (self.connection_type == "load_balancing")
                            )
                        )
                    )
                    or (
                        self.connection_type
                        and (
                            (
                                hasattr(self.connection_type, "value")
                                and self.connection_type.value == "snc_load_balancing"
                            )
                            or (self.connection_type == "snc_load_balancing")
                        )
                    )
                )
            )
            else exclude.add("system_number")
        )
        (
            include.add("use_system_number")
            if (
                (
                    (
                        self.connection_type
                        and (
                            (hasattr(self.connection_type, "value") and self.connection_type.value == "load_balancing")
                            or (self.connection_type == "load_balancing")
                        )
                    )
                )
                or (
                    self.connection_type
                    and (
                        (hasattr(self.connection_type, "value") and self.connection_type.value == "snc_load_balancing")
                        or (self.connection_type == "snc_load_balancing")
                    )
                )
            )
            else exclude.add("use_system_number")
        )
        (
            include.add("system_id")
            if (
                (((not self.use_system_number)))
                and (
                    (
                        (
                            self.connection_type
                            and (
                                (
                                    hasattr(self.connection_type, "value")
                                    and self.connection_type.value == "load_balancing"
                                )
                                or (self.connection_type == "load_balancing")
                            )
                        )
                    )
                    or (
                        self.connection_type
                        and (
                            (
                                hasattr(self.connection_type, "value")
                                and self.connection_type.value == "snc_load_balancing"
                            )
                            or (self.connection_type == "snc_load_balancing")
                        )
                    )
                )
            )
            else exclude.add("system_id")
        )
        (
            include.add("sap_application_system_number")
            if (
                (
                    (
                        self.connection_type
                        and (
                            (
                                hasattr(self.connection_type, "value")
                                and self.connection_type.value == "application_server"
                            )
                            or (self.connection_type == "application_server")
                        )
                    )
                )
                or (
                    self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value == "snc_application_server"
                        )
                        or (self.connection_type == "snc_application_server")
                    )
                )
            )
            else exclude.add("sap_application_system_number")
        )
        include.add("language") if (not self.defer_credentials) else exclude.add("language")
        (
            include.add("enable_x_509_certificate")
            if (
                (
                    (
                        self.connection_type
                        and (
                            (
                                hasattr(self.connection_type, "value")
                                and self.connection_type.value == "snc_application_server"
                            )
                            or (self.connection_type == "snc_application_server")
                        )
                    )
                )
                or (
                    self.connection_type
                    and (
                        (hasattr(self.connection_type, "value") and self.connection_type.value == "snc_load_balancing")
                        or (self.connection_type == "snc_load_balancing")
                    )
                )
            )
            else exclude.add("enable_x_509_certificate")
        )
        (
            include.add("snc_partner_name")
            if (
                (
                    (
                        self.connection_type
                        and (
                            (
                                hasattr(self.connection_type, "value")
                                and self.connection_type.value == "snc_application_server"
                            )
                            or (self.connection_type == "snc_application_server")
                        )
                    )
                )
                or (
                    self.connection_type
                    and (
                        (hasattr(self.connection_type, "value") and self.connection_type.value == "snc_load_balancing")
                        or (self.connection_type == "snc_load_balancing")
                    )
                )
            )
            else exclude.add("snc_partner_name")
        )
        (
            include.add("snc_name")
            if (
                (
                    (
                        self.connection_type
                        and (
                            (
                                hasattr(self.connection_type, "value")
                                and self.connection_type.value == "snc_application_server"
                            )
                            or (self.connection_type == "snc_application_server")
                        )
                    )
                )
                or (
                    self.connection_type
                    and (
                        (hasattr(self.connection_type, "value") and self.connection_type.value == "snc_load_balancing")
                        or (self.connection_type == "snc_load_balancing")
                    )
                )
            )
            else exclude.add("snc_name")
        )
        (
            include.add("sap_password")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            (
                                self.connection_type
                                and (
                                    (
                                        hasattr(self.connection_type, "value")
                                        and self.connection_type.value == "application_server"
                                    )
                                    or (self.connection_type == "application_server")
                                )
                            )
                        )
                        or (
                            (
                                self.connection_type
                                and (
                                    (
                                        hasattr(self.connection_type, "value")
                                        and self.connection_type.value == "load_balancing"
                                    )
                                    or (self.connection_type == "load_balancing")
                                )
                            )
                        )
                    )
                    or (not self.enable_x_509_certificate)
                )
            )
            else exclude.add("sap_password")
        )
        (
            include.add("application_server")
            if (
                (
                    (
                        self.connection_type
                        and (
                            (
                                hasattr(self.connection_type, "value")
                                and self.connection_type.value == "application_server"
                            )
                            or (self.connection_type == "application_server")
                        )
                    )
                )
                or (
                    self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value == "snc_application_server"
                        )
                        or (self.connection_type == "snc_application_server")
                    )
                )
            )
            else exclude.add("application_server")
        )
        (
            include.add("message_server")
            if (
                (
                    (
                        self.connection_type
                        and (
                            (hasattr(self.connection_type, "value") and self.connection_type.value == "load_balancing")
                            or (self.connection_type == "load_balancing")
                        )
                    )
                )
                or (
                    self.connection_type
                    and (
                        (hasattr(self.connection_type, "value") and self.connection_type.value == "snc_load_balancing")
                        or (self.connection_type == "snc_load_balancing")
                    )
                )
            )
            else exclude.add("message_server")
        )
        (
            include.add("x_509_certificate")
            if (
                ((self.enable_x_509_certificate))
                and (
                    (
                        (
                            self.connection_type
                            and (
                                (
                                    hasattr(self.connection_type, "value")
                                    and self.connection_type.value == "snc_application_server"
                                )
                                or (self.connection_type == "snc_application_server")
                            )
                        )
                    )
                    or (
                        self.connection_type
                        and (
                            (
                                hasattr(self.connection_type, "value")
                                and self.connection_type.value == "snc_load_balancing"
                            )
                            or (self.connection_type == "snc_load_balancing")
                        )
                    )
                )
            )
            else exclude.add("x_509_certificate")
        )
        (
            include.add("snc_qop")
            if (
                (
                    (
                        self.connection_type
                        and (
                            (
                                hasattr(self.connection_type, "value")
                                and self.connection_type.value == "snc_application_server"
                            )
                            or (self.connection_type == "snc_application_server")
                        )
                    )
                )
                or (
                    self.connection_type
                    and (
                        (hasattr(self.connection_type, "value") and self.connection_type.value == "snc_load_balancing")
                        or (self.connection_type == "snc_load_balancing")
                    )
                )
            )
            else exclude.add("snc_qop")
        )
        (
            include.add("group")
            if (
                (
                    (
                        self.connection_type
                        and (
                            (hasattr(self.connection_type, "value") and self.connection_type.value == "load_balancing")
                            or (self.connection_type == "load_balancing")
                        )
                    )
                )
                or (
                    self.connection_type
                    and (
                        (hasattr(self.connection_type, "value") and self.connection_type.value == "snc_load_balancing")
                        or (self.connection_type == "snc_load_balancing")
                    )
                )
            )
            else exclude.add("group")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            (
                                self.connection_type
                                and (
                                    (
                                        hasattr(self.connection_type, "value")
                                        and self.connection_type.value == "application_server"
                                    )
                                    or (self.connection_type == "application_server")
                                )
                            )
                        )
                        or (
                            (
                                self.connection_type
                                and (
                                    (
                                        hasattr(self.connection_type, "value")
                                        and self.connection_type.value == "load_balancing"
                                    )
                                    or (self.connection_type == "load_balancing")
                                )
                            )
                        )
                    )
                    or (not self.enable_x_509_certificate)
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
            include.add("application_server")
            if (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "application_server" in str(self.connection_type.value)
                    )
                    or ("application_server" in str(self.connection_type))
                )
                or self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_application_server" in str(self.connection_type.value)
                    )
                    or ("snc_application_server" in str(self.connection_type))
                )
            )
            else exclude.add("application_server")
        )
        (
            include.add("system_id")
            if (self.use_system_number == "false" or not self.use_system_number)
            and (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "load_balancing" in str(self.connection_type.value)
                    )
                    or ("load_balancing" in str(self.connection_type))
                )
                and self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_load_balancing" in str(self.connection_type.value)
                    )
                    or ("snc_load_balancing" in str(self.connection_type))
                )
            )
            else exclude.add("system_id")
        )
        (
            include.add("use_system_number")
            if (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "load_balancing" in str(self.connection_type.value)
                    )
                    or ("load_balancing" in str(self.connection_type))
                )
                or self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_load_balancing" in str(self.connection_type.value)
                    )
                    or ("snc_load_balancing" in str(self.connection_type))
                )
            )
            else exclude.add("use_system_number")
        )
        include.add("client_number") if (not self.defer_credentials) else exclude.add("client_number")
        (
            include.add("system_number")
            if (self.use_system_number == "true" or self.use_system_number)
            and (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "load_balancing" in str(self.connection_type.value)
                    )
                    or ("load_balancing" in str(self.connection_type))
                )
                and self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_load_balancing" in str(self.connection_type.value)
                    )
                    or ("snc_load_balancing" in str(self.connection_type))
                )
            )
            else exclude.add("system_number")
        )
        (
            include.add("enable_x_509_certificate")
            if (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_application_server" in str(self.connection_type.value)
                    )
                    or ("snc_application_server" in str(self.connection_type))
                )
                or self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_load_balancing" in str(self.connection_type.value)
                    )
                    or ("snc_load_balancing" in str(self.connection_type))
                )
            )
            else exclude.add("enable_x_509_certificate")
        )
        (
            include.add("snc_partner_name")
            if (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_application_server" in str(self.connection_type.value)
                    )
                    or ("snc_application_server" in str(self.connection_type))
                )
                or self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_load_balancing" in str(self.connection_type.value)
                    )
                    or ("snc_load_balancing" in str(self.connection_type))
                )
            )
            else exclude.add("snc_partner_name")
        )
        (
            include.add("sap_application_system_number")
            if (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "application_server" in str(self.connection_type.value)
                    )
                    or ("application_server" in str(self.connection_type))
                )
                or self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_application_server" in str(self.connection_type.value)
                    )
                    or ("snc_application_server" in str(self.connection_type))
                )
            )
            else exclude.add("sap_application_system_number")
        )
        (
            include.add("sap_password")
            if (not self.defer_credentials)
            and (
                (
                    self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value
                            and "application_server" in str(self.connection_type.value)
                        )
                        or ("application_server" in str(self.connection_type))
                    )
                    or self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value
                            and "load_balancing" in str(self.connection_type.value)
                        )
                        or ("load_balancing" in str(self.connection_type))
                    )
                )
                or (self.enable_x_509_certificate == "false" or not self.enable_x_509_certificate)
            )
            else exclude.add("sap_password")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                (
                    self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value
                            and "application_server" in str(self.connection_type.value)
                        )
                        or ("application_server" in str(self.connection_type))
                    )
                    or self.connection_type
                    and (
                        (
                            hasattr(self.connection_type, "value")
                            and self.connection_type.value
                            and "load_balancing" in str(self.connection_type.value)
                        )
                        or ("load_balancing" in str(self.connection_type))
                    )
                )
                or (self.enable_x_509_certificate == "false" or not self.enable_x_509_certificate)
            )
            else exclude.add("username")
        )
        (
            include.add("snc_qop")
            if (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_application_server" in str(self.connection_type.value)
                    )
                    or ("snc_application_server" in str(self.connection_type))
                )
                or self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_load_balancing" in str(self.connection_type.value)
                    )
                    or ("snc_load_balancing" in str(self.connection_type))
                )
            )
            else exclude.add("snc_qop")
        )
        include.add("language") if (not self.defer_credentials) else exclude.add("language")
        (
            include.add("x_509_certificate")
            if (self.enable_x_509_certificate == "true" or self.enable_x_509_certificate)
            and (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_application_server" in str(self.connection_type.value)
                    )
                    or ("snc_application_server" in str(self.connection_type))
                )
                and self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_load_balancing" in str(self.connection_type.value)
                    )
                    or ("snc_load_balancing" in str(self.connection_type))
                )
            )
            else exclude.add("x_509_certificate")
        )
        (
            include.add("message_server")
            if (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "load_balancing" in str(self.connection_type.value)
                    )
                    or ("load_balancing" in str(self.connection_type))
                )
                or self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_load_balancing" in str(self.connection_type.value)
                    )
                    or ("snc_load_balancing" in str(self.connection_type))
                )
            )
            else exclude.add("message_server")
        )
        (
            include.add("group")
            if (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "load_balancing" in str(self.connection_type.value)
                    )
                    or ("load_balancing" in str(self.connection_type))
                )
                or self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_load_balancing" in str(self.connection_type.value)
                    )
                    or ("snc_load_balancing" in str(self.connection_type))
                )
            )
            else exclude.add("group")
        )
        (
            include.add("snc_name")
            if (
                self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_application_server" in str(self.connection_type.value)
                    )
                    or ("snc_application_server" in str(self.connection_type))
                )
                or self.connection_type
                and (
                    (
                        hasattr(self.connection_type, "value")
                        and self.connection_type.value
                        and "snc_load_balancing" in str(self.connection_type.value)
                    )
                    or ("snc_load_balancing" in str(self.connection_type))
                )
            )
            else exclude.add("snc_name")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
