from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import IMPALA_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthenticationMethod(Enum):
    kerberos = "kerberos"
    ldap = "ldap"
    password = "password"


class ImpalaConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "impala"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    authentication_method: IMPALA_CONNECTION.AuthenticationMethod | None = Field(
        IMPALA_CONNECTION.AuthenticationMethod.password, alias="authentication_method"
    )
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    database: str | None = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    hostname_or_ip_address: str = Field(None, alias="host")
    impersonate_user: str | None = Field(None, alias="impersonate_user")
    kerberos_sso: bool | None = Field(None, alias="kerberos_sso")
    kerberos_sso_keytab: str | None = Field(None, alias="kerberos_sso_keytab")
    kerberos_sso_principal: str | None = Field(None, alias="kerberos_sso_principal")
    keytab_file: str = Field(None, alias="keytab")
    password: str = Field(None, alias="password")
    port: int = Field(None, alias="port")
    service_principal_name: str = Field(None, alias="service_principal")
    secure_gateway_id: str | None = Field(None, alias="sg_gateway_id")
    sg_host_original: str | None = Field(None, alias="sg_host_original")
    secure_gateway_as_http_proxy: bool | None = Field(None, alias="sg_http_proxy")
    secure_gateway_security_token: str | None = Field(None, alias="sg_security_token")
    secure_gateway_service_url: str | None = Field(None, alias="sg_service_url")
    satellite_client_certificate: str | None = Field(None, alias="sl_client_cert")
    satellite_client_private_key: str | None = Field(None, alias="sl_client_private_key")
    satellite_connector_id: str | None = Field(None, alias="sl_connector_id")
    satellite_endpoint_host: str | None = Field(None, alias="sl_endpoint_host")
    satellite_endpoint_display_name: str | None = Field(None, alias="sl_endpoint_name")
    satellite_endpoint_port: int | None = Field(None, alias="sl_endpoint_port")
    sl_host_original: str | None = Field(None, alias="sl_host_original")
    satellite_as_http_proxy: bool | None = Field(None, alias="sl_http_proxy")
    satellite_location_id: str | None = Field(None, alias="sl_location_id")
    satellite_service_url: str | None = Field(None, alias="sl_service_url")
    port_is_ssl_enabled: bool | None = Field(False, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    ssl_certificate_hostname: str | None = Field(None, alias="ssl_certificate_host")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    user_principal_name: str = Field(None, alias="user_principal")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    additional_properties: str | None = Field(None, alias="properties")
    login_config_name: str | None = Field(None, alias="login_config_name")
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
        (
            include.add("kerberos_sso")
            if (
                ((not self.defer_credentials))
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "kerberos"
                        )
                        or (self.authentication_method == "kerberos")
                    )
                )
            )
            else exclude.add("kerberos_sso")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    ((not self.defer_credentials))
                    and (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value != "kerberos"
                            )
                            or (self.authentication_method != "kerberos")
                        )
                    )
                )
                and (
                    ((not self.defer_credentials))
                    and (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value != "kerberos"
                            )
                            or (self.authentication_method != "kerberos")
                        )
                    )
                    and (not self.login_config_name)
                )
            )
            else exclude.add("password")
        )
        (
            include.add("service_principal_name")
            if (
                (
                    ((not self.defer_credentials))
                    and (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "kerberos"
                                )
                                or (self.authentication_method == "kerberos")
                            )
                        )
                    )
                )
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "kerberos"
                                )
                                or (self.authentication_method == "kerberos")
                            )
                        )
                    )
                    or (self.login_config_name)
                )
            )
            else exclude.add("service_principal_name")
        )
        (
            include.add("satellite_connector_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_location_id))
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("keytab_file")
            if (
                (
                    ((not self.defer_credentials))
                    and (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "kerberos"
                                )
                                or (self.authentication_method == "kerberos")
                            )
                        )
                    )
                )
                and (
                    ((not self.defer_credentials))
                    and (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "kerberos"
                            )
                            or (self.authentication_method == "kerberos")
                        )
                    )
                    and (not self.kerberos_sso)
                )
            )
            else exclude.add("keytab_file")
        )
        (
            include.add("ssl_certificate_hostname")
            if (self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_hostname")
        )
        (
            include.add("validate_ssl_certificate")
            if (self.port_is_ssl_enabled)
            else exclude.add("validate_ssl_certificate")
        )
        (
            include.add("user_principal_name")
            if (
                (
                    ((not self.defer_credentials))
                    and (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "kerberos"
                                )
                                or (self.authentication_method == "kerberos")
                            )
                        )
                    )
                )
                and (
                    ((not self.defer_credentials))
                    and (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "kerberos"
                            )
                            or (self.authentication_method == "kerberos")
                        )
                    )
                    and (not self.kerberos_sso)
                )
            )
            else exclude.add("user_principal_name")
        )
        (
            include.add("satellite_location_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_connector_id))
            else exclude.add("satellite_location_id")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    ((not self.defer_credentials))
                    and (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value != "kerberos"
                            )
                            or (self.authentication_method != "kerberos")
                        )
                    )
                )
                and (
                    ((not self.defer_credentials))
                    and (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value != "kerberos"
                            )
                            or (self.authentication_method != "kerberos")
                        )
                    )
                    and (not self.login_config_name)
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
        include.add("impersonate_user") if (self.hidden_dummy_property1) else exclude.add("impersonate_user")
        include.add("kerberos_sso") if (self.hidden_dummy_property1) else exclude.add("kerberos_sso")
        (
            include.add("kerberos_sso_principal")
            if (self.hidden_dummy_property1)
            else exclude.add("kerberos_sso_principal")
        )
        (
            include.add("service_principal_name")
            if (self.hidden_dummy_property1)
            else exclude.add("service_principal_name")
        )
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        include.add("kerberos_sso_keytab") if (self.hidden_dummy_property1) else exclude.add("kerberos_sso_keytab")
        include.add("keytab_file") if (self.hidden_dummy_property1) else exclude.add("keytab_file")
        include.add("login_config_name") if (self.hidden_dummy_property1) else exclude.add("login_config_name")
        include.add("user_principal_name") if (self.hidden_dummy_property1) else exclude.add("user_principal_name")
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        (
            include.add("kerberos_sso")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "kerberos")
                    or (self.authentication_method == "kerberos")
                )
            )
            else exclude.add("kerberos_sso")
        )
        (
            include.add("satellite_connector_id")
            if (not self.secure_gateway_id) and (not self.satellite_location_id)
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("validate_ssl_certificate")
            if (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("validate_ssl_certificate")
        )
        (
            include.add("ssl_certificate_hostname")
            if (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_hostname")
        )
        (
            include.add("service_principal_name")
            if (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "kerberos"
                        )
                        or (self.authentication_method == "kerberos")
                    )
                )
            )
            and (
                (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "kerberos"
                        )
                        or (self.authentication_method == "kerberos")
                    )
                )
                or (self.login_config_name)
            )
            else exclude.add("service_principal_name")
        )
        (
            include.add("user_principal_name")
            if (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "kerberos"
                        )
                        or (self.authentication_method == "kerberos")
                    )
                )
            )
            and (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "kerberos"
                        )
                        or (self.authentication_method == "kerberos")
                    )
                )
                and (self.kerberos_sso != "true" or not self.kerberos_sso)
            )
            else exclude.add("user_principal_name")
        )
        (
            include.add("keytab_file")
            if (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "kerberos"
                        )
                        or (self.authentication_method == "kerberos")
                    )
                )
            )
            and (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "kerberos"
                        )
                        or (self.authentication_method == "kerberos")
                    )
                )
                and (self.kerberos_sso != "true" or not self.kerberos_sso)
            )
            else exclude.add("keytab_file")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value != "kerberos"
                        )
                        or (self.authentication_method != "kerberos")
                    )
                )
            )
            and (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value != "kerberos"
                        )
                        or (self.authentication_method != "kerberos")
                    )
                )
                and (not self.login_config_name)
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value != "kerberos"
                        )
                        or (self.authentication_method != "kerberos")
                    )
                )
            )
            and (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value != "kerberos"
                        )
                        or (self.authentication_method != "kerberos")
                    )
                )
                and (not self.login_config_name)
            )
            else exclude.add("username")
        )
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate")
        )
        (
            include.add("login_config_name")
            if (
                (not self.defer_credentials)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "kerberos"
                        )
                        or (self.authentication_method == "kerberos")
                    )
                )
            )
            and ((not self.defer_credentials) and (self.kerberos_sso != "true" or not self.kerberos_sso))
            else exclude.add("login_config_name")
        )
        (
            include.add("satellite_location_id")
            if (not self.secure_gateway_id) and (not self.satellite_connector_id)
            else exclude.add("satellite_location_id")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
