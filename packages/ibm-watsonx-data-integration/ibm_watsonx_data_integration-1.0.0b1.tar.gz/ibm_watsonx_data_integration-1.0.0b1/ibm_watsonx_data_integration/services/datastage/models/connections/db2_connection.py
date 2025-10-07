from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import DB2_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class UsernamePasswordEncryption(Enum):
    aes_256_bit = "aes_256_bit"
    des_56_bit = "des_56_bit"
    default = "default"


class UsernamePasswordSecurity(Enum):
    clear_text = "clear_text"
    default = "default"
    encrypted_password = "encrypted_password"
    encrypted_username = "encrypted_username"
    encrypted_username_password = "encrypted_username_password"
    encrypted_username_password_data = "encrypted_username_password_data"
    kerberos_credentials = "kerberos_credentials"


class Db2Conn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "8c1a4480-1c29-4b33-9086-9cb799d7b157"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    access_token: str = Field(None, alias="access_token")
    application_name: str | None = Field(None, alias="application_name")
    discover_data_assets: bool | None = Field(None, alias="auto_discovery")
    avoid_timestamp_conversion: bool | None = Field(None, alias="avoid_timestamp_conversion")
    client_accounting_information: str | None = Field(None, alias="client_accounting_information")
    client_hostname: str | None = Field(None, alias="client_hostname")
    client_user: str | None = Field(None, alias="client_user")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    command_timeout: int | None = Field(600, alias="command_timeout")
    database: str = Field(None, alias="database")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    hostname_or_ip_address: str = Field(None, alias="host")
    impersonate_user: str | None = Field(None, alias="impersonate_user")
    use_my_platform_login_credentials: bool | None = Field(False, alias="inherit_access_token")
    kerberos_sso: bool | None = Field(None, alias="kerberos_sso")
    kerberos_sso_keytab: str | None = Field(None, alias="kerberos_sso_keytab")
    kerberos_sso_principal: str | None = Field(None, alias="kerberos_sso_principal")
    kerberos_user_principal_name: str = Field(None, alias="kerberos_user_principal_name")
    kerberos_user_principal_password: str = Field(None, alias="kerberos_user_principal_password")
    max_transport_objects: int | None = Field(None, alias="max_transport_objects")
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
    username: str = Field(None, alias="username")
    username_and_password_encryption_algorithm: DB2_CONNECTION.UsernamePasswordEncryption | None = Field(
        DB2_CONNECTION.UsernamePasswordEncryption.default, alias="username_password_encryption"
    )
    security_mechanism: DB2_CONNECTION.UsernamePasswordSecurity | None = Field(
        DB2_CONNECTION.UsernamePasswordSecurity.default, alias="username_password_security"
    )
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    additional_properties: str | None = Field(None, alias="properties")
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
            include.add("access_token")
            if (
                (((not self.defer_credentials)) and ((not self.username)))
                and (
                    self.security_mechanism
                    and (
                        (
                            hasattr(self.security_mechanism, "value")
                            and self.security_mechanism.value != "kerberos_credentials"
                        )
                        or (self.security_mechanism != "kerberos_credentials")
                    )
                )
            )
            else exclude.add("access_token")
        )
        (
            include.add("kerberos_sso")
            if (
                ((not self.defer_credentials))
                and (
                    self.security_mechanism
                    and (
                        (
                            hasattr(self.security_mechanism, "value")
                            and self.security_mechanism.value == "kerberos_credentials"
                        )
                        or (self.security_mechanism == "kerberos_credentials")
                    )
                )
            )
            else exclude.add("kerberos_sso")
        )
        (
            include.add("password")
            if (
                (
                    ((not self.defer_credentials))
                    and ((not self.access_token))
                    and ((not self.use_my_platform_login_credentials))
                )
                and (
                    self.security_mechanism
                    and (
                        (
                            hasattr(self.security_mechanism, "value")
                            and self.security_mechanism.value != "kerberos_credentials"
                        )
                        or (self.security_mechanism != "kerberos_credentials")
                    )
                )
                and (((not self.defer_credentials)) and (not self.kerberos_sso))
            )
            else exclude.add("password")
        )
        (
            include.add("service_principal_name")
            if (
                self.security_mechanism
                and (
                    (
                        hasattr(self.security_mechanism, "value")
                        and self.security_mechanism.value == "kerberos_credentials"
                    )
                    or (self.security_mechanism == "kerberos_credentials")
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
            include.add("kerberos_user_principal_name")
            if (
                ((not self.kerberos_sso))
                and (
                    self.security_mechanism
                    and (
                        (
                            hasattr(self.security_mechanism, "value")
                            and self.security_mechanism.value == "kerberos_credentials"
                        )
                        or (self.security_mechanism == "kerberos_credentials")
                    )
                )
            )
            else exclude.add("kerberos_user_principal_name")
        )
        (
            include.add("kerberos_user_principal_password")
            if (
                ((not self.kerberos_sso))
                and (
                    self.security_mechanism
                    and (
                        (
                            hasattr(self.security_mechanism, "value")
                            and self.security_mechanism.value == "kerberos_credentials"
                        )
                        or (self.security_mechanism == "kerberos_credentials")
                    )
                )
            )
            else exclude.add("kerberos_user_principal_password")
        )
        (
            include.add("username_and_password_encryption_algorithm")
            if (
                self.security_mechanism
                and (
                    (
                        hasattr(self.security_mechanism, "value")
                        and self.security_mechanism.value != "kerberos_credentials"
                    )
                    or (self.security_mechanism != "kerberos_credentials")
                )
            )
            else exclude.add("username_and_password_encryption_algorithm")
        )
        (
            include.add("satellite_location_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_connector_id))
            else exclude.add("satellite_location_id")
        )
        (
            include.add("username")
            if (
                (
                    ((not self.defer_credentials))
                    and ((not self.access_token))
                    and ((not self.use_my_platform_login_credentials))
                )
                and (
                    self.security_mechanism
                    and (
                        (
                            hasattr(self.security_mechanism, "value")
                            and self.security_mechanism.value != "kerberos_credentials"
                        )
                        or (self.security_mechanism != "kerberos_credentials")
                    )
                )
                and (((not self.defer_credentials)) and (not self.kerberos_sso))
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
        include.add("access_token") if (self.hidden_dummy_property1) else exclude.add("access_token")
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
        (
            include.add("kerberos_user_principal_name")
            if (self.hidden_dummy_property1)
            else exclude.add("kerberos_user_principal_name")
        )
        (
            include.add("use_my_platform_login_credentials")
            if (self.hidden_dummy_property1)
            else exclude.add("use_my_platform_login_credentials")
        )
        (
            include.add("kerberos_user_principal_password")
            if (self.hidden_dummy_property1)
            else exclude.add("kerberos_user_principal_password")
        )
        include.add("additional_properties") if (self.hidden_dummy_property1) else exclude.add("additional_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        (
            include.add("kerberos_sso")
            if (not self.defer_credentials)
            and (
                self.security_mechanism
                and (
                    (
                        hasattr(self.security_mechanism, "value")
                        and self.security_mechanism.value == "kerberos_credentials"
                    )
                    or (self.security_mechanism == "kerberos_credentials")
                )
            )
            else exclude.add("kerberos_sso")
        )
        (
            include.add("kerberos_user_principal_name")
            if (self.kerberos_sso != "true" or not self.kerberos_sso)
            and (
                self.security_mechanism
                and (
                    (
                        hasattr(self.security_mechanism, "value")
                        and self.security_mechanism.value == "kerberos_credentials"
                    )
                    or (self.security_mechanism == "kerberos_credentials")
                )
            )
            else exclude.add("kerberos_user_principal_name")
        )
        (
            include.add("satellite_connector_id")
            if (not self.secure_gateway_id) and (not self.satellite_location_id)
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("service_principal_name")
            if (
                self.security_mechanism
                and (
                    (
                        hasattr(self.security_mechanism, "value")
                        and self.security_mechanism.value == "kerberos_credentials"
                    )
                    or (self.security_mechanism == "kerberos_credentials")
                )
            )
            else exclude.add("service_principal_name")
        )
        (
            include.add("username_and_password_encryption_algorithm")
            if (
                self.security_mechanism
                and (
                    (
                        hasattr(self.security_mechanism, "value")
                        and self.security_mechanism.value != "kerberos_credentials"
                    )
                    or (self.security_mechanism != "kerberos_credentials")
                )
            )
            else exclude.add("username_and_password_encryption_algorithm")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        (
            include.add("access_token")
            if ((not self.defer_credentials) and (not self.username))
            and (
                self.security_mechanism
                and (
                    (
                        hasattr(self.security_mechanism, "value")
                        and self.security_mechanism.value != "kerberos_credentials"
                    )
                    or (self.security_mechanism != "kerberos_credentials")
                )
            )
            else exclude.add("access_token")
        )
        (
            include.add("password")
            if (
                (not self.defer_credentials)
                and (not self.access_token)
                and (self.use_my_platform_login_credentials != "yes")
            )
            and (
                self.security_mechanism
                and (
                    (
                        hasattr(self.security_mechanism, "value")
                        and self.security_mechanism.value != "kerberos_credentials"
                    )
                    or (self.security_mechanism != "kerberos_credentials")
                )
            )
            and ((not self.defer_credentials) and (self.kerberos_sso != "true" or not self.kerberos_sso))
            else exclude.add("password")
        )
        (
            include.add("username")
            if (
                (not self.defer_credentials)
                and (not self.access_token)
                and (self.use_my_platform_login_credentials != "yes")
            )
            and (
                self.security_mechanism
                and (
                    (
                        hasattr(self.security_mechanism, "value")
                        and self.security_mechanism.value != "kerberos_credentials"
                    )
                    or (self.security_mechanism != "kerberos_credentials")
                )
            )
            and ((not self.defer_credentials) and (self.kerberos_sso != "true" or not self.kerberos_sso))
            else exclude.add("username")
        )
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate")
        )
        (
            include.add("satellite_location_id")
            if (not self.secure_gateway_id) and (not self.satellite_connector_id)
            else exclude.add("satellite_location_id")
        )
        (
            include.add("kerberos_user_principal_password")
            if (self.kerberos_sso != "true" or not self.kerberos_sso)
            and (
                self.security_mechanism
                and (
                    (
                        hasattr(self.security_mechanism, "value")
                        and self.security_mechanism.value == "kerberos_credentials"
                    )
                    or (self.security_mechanism == "kerberos_credentials")
                )
            )
            else exclude.add("kerberos_user_principal_password")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
