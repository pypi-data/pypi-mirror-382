from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import HDFS_APACHE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthenticationMethod(Enum):
    kerberos = "kerberos"
    password = "password"


class FilesystemType(Enum):
    httpfs = "httpfs"
    webhdfs = "webhdfs"


class HdfsApacheConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "c10e5224-f17d-4524-844f-e97b1305e489"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    authentication_method: HDFS_APACHE_CONNECTION.AuthenticationMethod | None = Field(
        HDFS_APACHE_CONNECTION.AuthenticationMethod.password, alias="authentication_method"
    )
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    connect_to_apache_hive: bool | None = Field(False, alias="connect_to_apache_hive")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    hive_database: str | None = Field(None, alias="hive_db")
    hive_host: str | None = Field(None, alias="hive_host")
    hive_http_path: str | None = Field(None, alias="hive_http_path")
    hive_keytab_file: str | None = Field(None, alias="hive_keytab")
    hive_password: str | None = Field(None, alias="hive_password")
    hive_port: int | None = Field(None, alias="hive_port")
    hive_service_principal_name: str | None = Field(None, alias="hive_service_principal")
    enable_ssl_for_hive: bool | None = Field(True, alias="hive_ssl")
    hive_username: str | None = Field(None, alias="hive_user")
    hive_user_principal_name: str | None = Field(None, alias="hive_user_principal")
    keytab_file: str | None = Field(None, alias="keytab")
    password: str | None = Field(None, alias="password")
    service_principal_name: str | None = Field(None, alias="service_principal")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    url: str = Field(None, alias="url")
    use_home_as_root: bool | None = Field(True, alias="use_home_as_root")
    user_principal_name: str = Field(None, alias="user_principal")
    username: str = Field(None, alias="username")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
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
    file_system_type: HDFS_APACHE_CONNECTION.FilesystemType | None = Field(None, alias="filesystem_type")
    hive_login_config_name: str | None = Field(None, alias="hive_login_config_name")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("hive_password")
            if (
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
                and (self.connect_to_apache_hive)
            )
            else exclude.add("hive_password")
        )
        include.add("hive_port") if (self.connect_to_apache_hive) else exclude.add("hive_port")
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        include.add("hive_http_path") if (self.connect_to_apache_hive) else exclude.add("hive_http_path")
        (
            include.add("keytab_file")
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
            else exclude.add("keytab_file")
        )
        (
            include.add("hive_username")
            if (
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
                and (self.connect_to_apache_hive)
            )
            else exclude.add("hive_username")
        )
        include.add("hive_database") if (self.connect_to_apache_hive) else exclude.add("hive_database")
        (
            include.add("hive_service_principal_name")
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
                and (self.connect_to_apache_hive)
            )
            else exclude.add("hive_service_principal_name")
        )
        (
            include.add("hive_user_principal_name")
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
                and (self.connect_to_apache_hive)
            )
            else exclude.add("hive_user_principal_name")
        )
        (
            include.add("service_principal_name")
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
            else exclude.add("service_principal_name")
        )
        (
            include.add("password")
            if (
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
            else exclude.add("password")
        )
        include.add("hive_host") if (self.connect_to_apache_hive) else exclude.add("hive_host")
        (
            include.add("user_principal_name")
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
            else exclude.add("user_principal_name")
        )
        (
            include.add("hive_keytab_file")
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
                and (self.connect_to_apache_hive)
            )
            else exclude.add("hive_keytab_file")
        )
        (
            include.add("username")
            if (
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
            else exclude.add("username")
        )
        (
            include.add("satellite_connector_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_location_id))
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("satellite_location_id")
            if (((not self.secure_gateway_id)) and (not self.satellite_connector_id))
            else exclude.add("satellite_location_id")
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
        include.add("authentication_method") if (self.hidden_dummy_property1) else exclude.add("authentication_method")
        (
            include.add("hive_user_principal_name")
            if (self.hidden_dummy_property1)
            else exclude.add("hive_user_principal_name")
        )
        (
            include.add("service_principal_name")
            if (self.hidden_dummy_property1)
            else exclude.add("service_principal_name")
        )
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        include.add("keytab_file") if (self.hidden_dummy_property1) else exclude.add("keytab_file")
        include.add("user_principal_name") if (self.hidden_dummy_property1) else exclude.add("user_principal_name")
        (
            include.add("hive_login_config_name")
            if (self.hidden_dummy_property1)
            else exclude.add("hive_login_config_name")
        )
        include.add("hive_keytab_file") if (self.hidden_dummy_property1) else exclude.add("hive_keytab_file")
        include.add("file_system_type") if (self.hidden_dummy_property1) else exclude.add("file_system_type")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")
        (
            include.add("hive_service_principal_name")
            if (self.hidden_dummy_property1)
            else exclude.add("hive_service_principal_name")
        )

        (
            include.add("satellite_connector_id")
            if (not self.secure_gateway_id) and (not self.satellite_location_id)
            else exclude.add("satellite_connector_id")
        )
        (
            include.add("user_principal_name")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "kerberos")
                    or (self.authentication_method == "kerberos")
                )
            )
            else exclude.add("user_principal_name")
        )
        (
            include.add("hive_keytab_file")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "kerberos")
                    or (self.authentication_method == "kerberos")
                )
            )
            and (self.connect_to_apache_hive == "true" or self.connect_to_apache_hive)
            else exclude.add("hive_keytab_file")
        )
        (
            include.add("password")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value != "kerberos")
                    or (self.authentication_method != "kerberos")
                )
            )
            else exclude.add("password")
        )
        (
            include.add("username")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value != "kerberos")
                    or (self.authentication_method != "kerberos")
                )
            )
            else exclude.add("username")
        )
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        (
            include.add("hive_username")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value != "kerberos")
                    or (self.authentication_method != "kerberos")
                )
            )
            and (self.connect_to_apache_hive == "true" or self.connect_to_apache_hive)
            else exclude.add("hive_username")
        )
        (
            include.add("hive_service_principal_name")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "kerberos")
                    or (self.authentication_method == "kerberos")
                )
            )
            and (self.connect_to_apache_hive == "true" or self.connect_to_apache_hive)
            else exclude.add("hive_service_principal_name")
        )
        (
            include.add("satellite_location_id")
            if (not self.secure_gateway_id) and (not self.satellite_connector_id)
            else exclude.add("satellite_location_id")
        )
        (
            include.add("hive_user_principal_name")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "kerberos")
                    or (self.authentication_method == "kerberos")
                )
            )
            and (self.connect_to_apache_hive == "true" or self.connect_to_apache_hive)
            else exclude.add("hive_user_principal_name")
        )
        (
            include.add("service_principal_name")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "kerberos")
                    or (self.authentication_method == "kerberos")
                )
            )
            else exclude.add("service_principal_name")
        )
        (
            include.add("hive_port")
            if (self.connect_to_apache_hive and "true" in str(self.connect_to_apache_hive))
            else exclude.add("hive_port")
        )
        (
            include.add("hive_database")
            if (self.connect_to_apache_hive and "true" in str(self.connect_to_apache_hive))
            else exclude.add("hive_database")
        )
        (
            include.add("hive_password")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value != "kerberos")
                    or (self.authentication_method != "kerberos")
                )
            )
            and (self.connect_to_apache_hive == "true" or self.connect_to_apache_hive)
            else exclude.add("hive_password")
        )
        (
            include.add("hive_http_path")
            if (self.connect_to_apache_hive and "true" in str(self.connect_to_apache_hive))
            else exclude.add("hive_http_path")
        )
        (
            include.add("keytab_file")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "kerberos")
                    or (self.authentication_method == "kerberos")
                )
            )
            else exclude.add("keytab_file")
        )
        (
            include.add("hive_login_config_name")
            if (not self.defer_credentials)
            and (
                self.authentication_method
                and (
                    (hasattr(self.authentication_method, "value") and self.authentication_method.value == "kerberos")
                    or (self.authentication_method == "kerberos")
                )
            )
            and (self.connect_to_apache_hive == "true" or self.connect_to_apache_hive)
            else exclude.add("hive_login_config_name")
        )
        include.add("ssl_certificate_file") if (not self.ssl_certificate) else exclude.add("ssl_certificate_file")
        (
            include.add("hive_host")
            if (self.connect_to_apache_hive and "true" in str(self.connect_to_apache_hive))
            else exclude.add("hive_host")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
