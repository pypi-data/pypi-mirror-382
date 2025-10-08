from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import FTP_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    username_password = "username_password"
    username_password_key = "username_password_key"
    username_key = "username_key"


class ConnectionMode(Enum):
    anonymous = "anonymous"
    basic = "basic"
    mvssftp = "mvssftp"
    sftp = "sftp"
    ftps = "ftps"


class FtpConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "d5dbc62f-7c4c-4d49-8eb2-dab6cef2969c"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    authentication_method: FTP_CONNECTION.AuthMethod | None = Field(None, alias="auth_method")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    connection_mode: FTP_CONNECTION.ConnectionMode = Field(None, alias="connection_mode")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    ftadv_strings: str | None = Field(None, alias="ftadv")
    hostname_or_ip_address: str = Field(None, alias="host")
    key_passphrase: str | None = Field(None, alias="key_passphrase")
    access_mvs_dataset: bool | None = Field(None, alias="mvs_dataset")
    password: str | None = Field(None, alias="password")
    port: int | None = Field(None, alias="port")
    private_key: str | None = Field(None, alias="private_key")
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
    port_is_ssl_enabled: bool | None = Field(True, alias="ssl")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    ssl_certificate_hostname: str | None = Field(None, alias="ssl_certificate_host")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    use_home_as_root: bool | None = Field(True, alias="use_home_as_root")
    username: str = Field("anonymous", alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
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
            include.add("key_passphrase")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.connection_mode
                            and (
                                (hasattr(self.connection_mode, "value") and self.connection_mode.value == "mvssftp")
                                or (self.connection_mode == "mvssftp")
                            )
                        )
                    )
                    or (
                        self.connection_mode
                        and (
                            (hasattr(self.connection_mode, "value") and self.connection_mode.value == "sftp")
                            or (self.connection_mode == "sftp")
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
                                    and self.authentication_method.value == "username_key"
                                )
                                or (self.authentication_method == "username_key")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "username_password_key"
                            )
                            or (self.authentication_method == "username_password_key")
                        )
                    )
                )
            )
            else exclude.add("key_passphrase")
        )
        (
            include.add("satellite_connector_id")
            if (
                (((not self.secure_gateway_id)) and ((not self.satellite_location_id)))
                and (
                    (
                        (
                            self.connection_mode
                            and (
                                (hasattr(self.connection_mode, "value") and self.connection_mode.value == "mvssftp")
                                or (self.connection_mode == "mvssftp")
                            )
                        )
                    )
                    or (
                        self.connection_mode
                        and (
                            (hasattr(self.connection_mode, "value") and self.connection_mode.value == "sftp")
                            or (self.connection_mode == "sftp")
                        )
                    )
                )
            )
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("ssl_certificate_hostname")
            if (self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_hostname")
        )
        (
            include.add("use_home_as_root")
            if (
                self.connection_mode
                and (
                    (hasattr(self.connection_mode, "value") and self.connection_mode.value == "sftp")
                    or (self.connection_mode == "sftp")
                )
            )
            else exclude.add("use_home_as_root")
        )
        (
            include.add("private_key")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.connection_mode
                            and (
                                (hasattr(self.connection_mode, "value") and self.connection_mode.value == "mvssftp")
                                or (self.connection_mode == "mvssftp")
                            )
                        )
                    )
                    or (
                        self.connection_mode
                        and (
                            (hasattr(self.connection_mode, "value") and self.connection_mode.value == "sftp")
                            or (self.connection_mode == "sftp")
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
                                    and self.authentication_method.value == "username_key"
                                )
                                or (self.authentication_method == "username_key")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "username_password_key"
                            )
                            or (self.authentication_method == "username_password_key")
                        )
                    )
                )
            )
            else exclude.add("private_key")
        )
        (
            include.add("secure_gateway_id")
            if (
                (
                    (
                        self.connection_mode
                        and (
                            (hasattr(self.connection_mode, "value") and self.connection_mode.value == "mvssftp")
                            or (self.connection_mode == "mvssftp")
                        )
                    )
                )
                or (
                    self.connection_mode
                    and (
                        (hasattr(self.connection_mode, "value") and self.connection_mode.value == "sftp")
                        or (self.connection_mode == "sftp")
                    )
                )
            )
            else exclude.add("secure_gateway_id")
        )
        (
            include.add("port_is_ssl_enabled")
            if (
                self.connection_mode
                and (
                    (hasattr(self.connection_mode, "value") and self.connection_mode.value == "ftps")
                    or (self.connection_mode == "ftps")
                )
            )
            else exclude.add("port_is_ssl_enabled")
        )
        (
            include.add("access_mvs_dataset")
            if (
                self.connection_mode
                and (
                    (hasattr(self.connection_mode, "value") and self.connection_mode.value == "mvssftp")
                    or (self.connection_mode == "mvssftp")
                )
            )
            else exclude.add("access_mvs_dataset")
        )
        (
            include.add("password")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            (
                                (
                                    self.connection_mode
                                    and (
                                        (
                                            hasattr(self.connection_mode, "value")
                                            and self.connection_mode.value == "mvssftp"
                                        )
                                        or (self.connection_mode == "mvssftp")
                                    )
                                )
                            )
                            or (
                                (
                                    self.connection_mode
                                    and (
                                        (
                                            hasattr(self.connection_mode, "value")
                                            and self.connection_mode.value == "sftp"
                                        )
                                        or (self.connection_mode == "sftp")
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
                                            and self.authentication_method.value == "username_password"
                                        )
                                        or (self.authentication_method == "username_password")
                                    )
                                )
                            )
                            or (
                                (
                                    self.authentication_method
                                    and (
                                        (
                                            hasattr(self.authentication_method, "value")
                                            and self.authentication_method.value == "username_password_key"
                                        )
                                        or (self.authentication_method == "username_password_key")
                                    )
                                )
                            )
                        )
                    )
                    or (
                        (
                            (
                                self.connection_mode
                                and (
                                    (hasattr(self.connection_mode, "value") and self.connection_mode.value == "basic")
                                    or (self.connection_mode == "basic")
                                )
                            )
                        )
                        or (
                            self.connection_mode
                            and (
                                (hasattr(self.connection_mode, "value") and self.connection_mode.value == "ftps")
                                or (self.connection_mode == "ftps")
                            )
                        )
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("authentication_method")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            self.connection_mode
                            and (
                                (hasattr(self.connection_mode, "value") and self.connection_mode.value == "mvssftp")
                                or (self.connection_mode == "mvssftp")
                            )
                        )
                    )
                    or (
                        self.connection_mode
                        and (
                            (hasattr(self.connection_mode, "value") and self.connection_mode.value == "sftp")
                            or (self.connection_mode == "sftp")
                        )
                    )
                )
            )
            else exclude.add("authentication_method")
        )
        include.add("ftadv_strings") if (self.access_mvs_dataset) else exclude.add("ftadv_strings")
        (
            include.add("validate_ssl_certificate")
            if (self.port_is_ssl_enabled)
            else exclude.add("validate_ssl_certificate")
        )
        (
            include.add("satellite_location_id")
            if (
                (((not self.secure_gateway_id)) and ((not self.satellite_connector_id)))
                and (
                    (
                        (
                            self.connection_mode
                            and (
                                (hasattr(self.connection_mode, "value") and self.connection_mode.value == "mvssftp")
                                or (self.connection_mode == "mvssftp")
                            )
                        )
                    )
                    or (
                        self.connection_mode
                        and (
                            (hasattr(self.connection_mode, "value") and self.connection_mode.value == "sftp")
                            or (self.connection_mode == "sftp")
                        )
                    )
                )
            )
            else exclude.add("satellite_location_id")
        )
        (
            include.add("username")
            if (
                ((not self.defer_credentials))
                and (
                    (
                        (
                            (
                                (
                                    self.connection_mode
                                    and (
                                        (
                                            hasattr(self.connection_mode, "value")
                                            and self.connection_mode.value == "mvssftp"
                                        )
                                        or (self.connection_mode == "mvssftp")
                                    )
                                )
                            )
                            or (
                                (
                                    self.connection_mode
                                    and (
                                        (
                                            hasattr(self.connection_mode, "value")
                                            and self.connection_mode.value == "sftp"
                                        )
                                        or (self.connection_mode == "sftp")
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
                                            and self.authentication_method.value == "username_key"
                                        )
                                        or (self.authentication_method == "username_key")
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
                            or (
                                (
                                    self.authentication_method
                                    and (
                                        (
                                            hasattr(self.authentication_method, "value")
                                            and self.authentication_method.value == "username_password_key"
                                        )
                                        or (self.authentication_method == "username_password_key")
                                    )
                                )
                            )
                        )
                    )
                    or (
                        (
                            (
                                self.connection_mode
                                and (
                                    (hasattr(self.connection_mode, "value") and self.connection_mode.value == "basic")
                                    or (self.connection_mode == "basic")
                                )
                            )
                        )
                        or (
                            self.connection_mode
                            and (
                                (hasattr(self.connection_mode, "value") and self.connection_mode.value == "ftps")
                                or (self.connection_mode == "ftps")
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

        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")
        (
            include.add("satellite_connector_id")
            if ((not self.secure_gateway_id) and (not self.satellite_location_id))
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "mvssftp" in str(self.connection_mode.value)
                    )
                    or ("mvssftp" in str(self.connection_mode))
                )
                and self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "sftp" in str(self.connection_mode.value)
                    )
                    or ("sftp" in str(self.connection_mode))
                )
            )
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("ftadv_strings")
            if (self.access_mvs_dataset and "true" in str(self.access_mvs_dataset))
            else exclude.add("ftadv_strings")
        )
        (
            include.add("port_is_ssl_enabled")
            if (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "ftps" in str(self.connection_mode.value)
                    )
                    or ("ftps" in str(self.connection_mode))
                )
            )
            else exclude.add("port_is_ssl_enabled")
        )
        (
            include.add("authentication_method")
            if (not self.defer_credentials)
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "mvssftp" in str(self.connection_mode.value)
                    )
                    or ("mvssftp" in str(self.connection_mode))
                )
                and self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "sftp" in str(self.connection_mode.value)
                    )
                    or ("sftp" in str(self.connection_mode))
                )
            )
            else exclude.add("authentication_method")
        )
        (
            include.add("use_home_as_root")
            if (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "sftp" in str(self.connection_mode.value)
                    )
                    or ("sftp" in str(self.connection_mode))
                )
            )
            else exclude.add("use_home_as_root")
        )
        (
            include.add("key_passphrase")
            if (not self.defer_credentials)
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "mvssftp" in str(self.connection_mode.value)
                    )
                    or ("mvssftp" in str(self.connection_mode))
                )
                and self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "sftp" in str(self.connection_mode.value)
                    )
                    or ("sftp" in str(self.connection_mode))
                )
            )
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_key" in str(self.authentication_method.value)
                    )
                    or ("username_key" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password_key" in str(self.authentication_method.value)
                    )
                    or ("username_password_key" in str(self.authentication_method))
                )
            )
            else exclude.add("key_passphrase")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                (
                    (
                        self.connection_mode
                        and (
                            (
                                hasattr(self.connection_mode, "value")
                                and self.connection_mode.value
                                and "mvssftp" in str(self.connection_mode.value)
                            )
                            or ("mvssftp" in str(self.connection_mode))
                        )
                        and self.connection_mode
                        and (
                            (
                                hasattr(self.connection_mode, "value")
                                and self.connection_mode.value
                                and "sftp" in str(self.connection_mode.value)
                            )
                            or ("sftp" in str(self.connection_mode))
                        )
                    )
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
                        and self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value
                                and "username_password_key" in str(self.authentication_method.value)
                            )
                            or ("username_password_key" in str(self.authentication_method))
                        )
                    )
                )
                or (
                    self.connection_mode
                    and (
                        (
                            hasattr(self.connection_mode, "value")
                            and self.connection_mode.value
                            and "basic" in str(self.connection_mode.value)
                        )
                        or ("basic" in str(self.connection_mode))
                    )
                    or self.connection_mode
                    and (
                        (
                            hasattr(self.connection_mode, "value")
                            and self.connection_mode.value
                            and "ftps" in str(self.connection_mode.value)
                        )
                        or ("ftps" in str(self.connection_mode))
                    )
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                (
                    (
                        self.connection_mode
                        and (
                            (
                                hasattr(self.connection_mode, "value")
                                and self.connection_mode.value
                                and "mvssftp" in str(self.connection_mode.value)
                            )
                            or ("mvssftp" in str(self.connection_mode))
                        )
                        and self.connection_mode
                        and (
                            (
                                hasattr(self.connection_mode, "value")
                                and self.connection_mode.value
                                and "sftp" in str(self.connection_mode.value)
                            )
                            or ("sftp" in str(self.connection_mode))
                        )
                    )
                    and (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value
                                and "username_key" in str(self.authentication_method.value)
                            )
                            or ("username_key" in str(self.authentication_method))
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
                        and self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value
                                and "username_password_key" in str(self.authentication_method.value)
                            )
                            or ("username_password_key" in str(self.authentication_method))
                        )
                    )
                )
                or (
                    self.connection_mode
                    and (
                        (
                            hasattr(self.connection_mode, "value")
                            and self.connection_mode.value
                            and "basic" in str(self.connection_mode.value)
                        )
                        or ("basic" in str(self.connection_mode))
                    )
                    or self.connection_mode
                    and (
                        (
                            hasattr(self.connection_mode, "value")
                            and self.connection_mode.value
                            and "ftps" in str(self.connection_mode.value)
                        )
                        or ("ftps" in str(self.connection_mode))
                    )
                )
            )
            else exclude.add("username")
        )
        (
            include.add("ssl_certificate")
            if (not self.ssl_certificate_file) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate")
        )
        (
            include.add("satellite_location_id")
            if ((not self.secure_gateway_id) and (not self.satellite_connector_id))
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "mvssftp" in str(self.connection_mode.value)
                    )
                    or ("mvssftp" in str(self.connection_mode))
                )
                and self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "sftp" in str(self.connection_mode.value)
                    )
                    or ("sftp" in str(self.connection_mode))
                )
            )
            else exclude.add("satellite_location_id")
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
            include.add("secure_gateway_id")
            if (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "mvssftp" in str(self.connection_mode.value)
                    )
                    or ("mvssftp" in str(self.connection_mode))
                )
                and self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "sftp" in str(self.connection_mode.value)
                    )
                    or ("sftp" in str(self.connection_mode))
                )
            )
            else exclude.add("secure_gateway_id")
        )
        (
            include.add("ssl_certificate_file")
            if (not self.ssl_certificate) and (self.port_is_ssl_enabled == "true" or self.port_is_ssl_enabled)
            else exclude.add("ssl_certificate_file")
        )
        (
            include.add("private_key")
            if (not self.defer_credentials)
            and (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "mvssftp" in str(self.connection_mode.value)
                    )
                    or ("mvssftp" in str(self.connection_mode))
                )
                and self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "sftp" in str(self.connection_mode.value)
                    )
                    or ("sftp" in str(self.connection_mode))
                )
            )
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_key" in str(self.authentication_method.value)
                    )
                    or ("username_key" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "username_password_key" in str(self.authentication_method.value)
                    )
                    or ("username_password_key" in str(self.authentication_method))
                )
            )
            else exclude.add("private_key")
        )
        (
            include.add("access_mvs_dataset")
            if (
                self.connection_mode
                and (
                    (
                        hasattr(self.connection_mode, "value")
                        and self.connection_mode.value
                        and "mvssftp" in str(self.connection_mode.value)
                    )
                    or ("mvssftp" in str(self.connection_mode))
                )
            )
            else exclude.add("access_mvs_dataset")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
