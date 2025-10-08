from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import APACHE_HBASE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class FilePathMode(Enum):
    content = "content"
    path = "path"


class ApacheHbaseConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "4f4f7244-9459-3f91-a149-f49f4cc59c54"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    cas_lite_service_authorization_header: str | None = Field(None, alias="cas_lite_auth_header")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    core_site_xml: str = Field(None, alias="core-site")
    core_site_xml_path: str = Field(None, alias="core-site_path")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    input_method_for_xml_files: APACHE_HBASE_CONNECTION.FilePathMode | None = Field(
        APACHE_HBASE_CONNECTION.FilePathMode.content, alias="file_path_mode"
    )
    hadoop_identity: str | None = Field("", alias="hadoop_identity")
    hbase_site_xml: str = Field(None, alias="hbase-site")
    hbase_site_xml_path: str = Field(None, alias="hbase-site_path")
    hbase_identity: str | None = Field("", alias="hbase_identity")
    simple_authentication_sasl_username: str = Field(None, alias="simple_auth_username")
    use_cas_lite_service: bool | None = Field(True, alias="use_cas_lite")
    use_kerberos_authentication: bool = Field(False, alias="use_kerberos")
    krb5_conf_location: str = Field(None, alias="use_kerberos.krb5conf")
    password: str = Field("password", alias="use_kerberos.password")
    user_principal_name: str = Field("user@REALM", alias="use_kerberos.principal")
    ticket_cache_location: str | None = Field(None, alias="use_kerberos.ticket_cache_location")
    use_keytab: bool = Field(False, alias="use_kerberos.use_keytab")
    keytab: str = Field("", alias="use_kerberos.use_keytab.keytab")
    use_ticket_cache: bool = Field(False, alias="use_kerberos.use_ticket_cache")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("keytab") if (((self.use_kerberos_authentication)) and (self.use_keytab)) else exclude.add("keytab")
        include.add("krb5_conf_location") if (self.use_kerberos_authentication) else exclude.add("krb5_conf_location")
        (
            include.add("core_site_xml_path")
            if (
                self.input_method_for_xml_files
                and (
                    (
                        hasattr(self.input_method_for_xml_files, "value")
                        and self.input_method_for_xml_files.value == "path"
                    )
                    or (self.input_method_for_xml_files == "path")
                )
            )
            else exclude.add("core_site_xml_path")
        )
        (
            include.add("simple_authentication_sasl_username")
            if (
                ((not self.defer_credentials))
                and (((not self.use_kerberos_authentication)) or (not self.use_kerberos_authentication))
            )
            else exclude.add("simple_authentication_sasl_username")
        )
        (
            include.add("use_ticket_cache")
            if (((self.use_kerberos_authentication)) and (not self.use_keytab))
            else exclude.add("use_ticket_cache")
        )
        include.add("use_keytab") if (self.use_kerberos_authentication) else exclude.add("use_keytab")
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        (
            include.add("hbase_site_xml")
            if (
                self.input_method_for_xml_files
                and (
                    (
                        hasattr(self.input_method_for_xml_files, "value")
                        and self.input_method_for_xml_files.value == "content"
                    )
                    or (self.input_method_for_xml_files == "content")
                )
            )
            else exclude.add("hbase_site_xml")
        )
        include.add("user_principal_name") if (self.use_kerberos_authentication) else exclude.add("user_principal_name")
        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("ticket_cache_location")
            if (((self.use_kerberos_authentication)) and (not self.use_keytab) and (self.use_ticket_cache))
            else exclude.add("ticket_cache_location")
        )
        (
            include.add("password")
            if ((((self.use_kerberos_authentication))) and (not self.use_keytab))
            else exclude.add("password")
        )
        (
            include.add("core_site_xml")
            if (
                self.input_method_for_xml_files
                and (
                    (
                        hasattr(self.input_method_for_xml_files, "value")
                        and self.input_method_for_xml_files.value == "content"
                    )
                    or (self.input_method_for_xml_files == "content")
                )
            )
            else exclude.add("core_site_xml")
        )
        (
            include.add("hbase_site_xml_path")
            if (
                self.input_method_for_xml_files
                and (
                    (
                        hasattr(self.input_method_for_xml_files, "value")
                        and self.input_method_for_xml_files.value == "path"
                    )
                    or (self.input_method_for_xml_files == "path")
                )
            )
            else exclude.add("hbase_site_xml_path")
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
            include.add("use_keytab")
            if (self.use_kerberos_authentication == "true" or self.use_kerberos_authentication)
            else exclude.add("use_keytab")
        )
        (
            include.add("ticket_cache_location")
            if (self.use_kerberos_authentication == "true" or self.use_kerberos_authentication)
            and (self.use_keytab == "false" or not self.use_keytab)
            and (self.use_ticket_cache == "true" or self.use_ticket_cache)
            else exclude.add("ticket_cache_location")
        )
        (
            include.add("hbase_site_xml")
            if (
                self.input_method_for_xml_files
                and (
                    (
                        hasattr(self.input_method_for_xml_files, "value")
                        and self.input_method_for_xml_files.value == "content"
                    )
                    or (self.input_method_for_xml_files == "content")
                )
            )
            else exclude.add("hbase_site_xml")
        )
        (
            include.add("hbase_site_xml_path")
            if (
                self.input_method_for_xml_files
                and (
                    (
                        hasattr(self.input_method_for_xml_files, "value")
                        and self.input_method_for_xml_files.value == "path"
                    )
                    or (self.input_method_for_xml_files == "path")
                )
            )
            else exclude.add("hbase_site_xml_path")
        )
        (
            include.add("krb5_conf_location")
            if (self.use_kerberos_authentication == "true" or self.use_kerberos_authentication)
            else exclude.add("krb5_conf_location")
        )
        (
            include.add("keytab")
            if (self.use_kerberos_authentication == "true" or self.use_kerberos_authentication)
            and (self.use_keytab == "true" or self.use_keytab)
            else exclude.add("keytab")
        )
        (
            include.add("use_cas_lite_service")
            if (self.cas_lite_service_authorization_header)
            else exclude.add("use_cas_lite_service")
        )
        (
            include.add("user_principal_name")
            if (self.use_kerberos_authentication == "true" or self.use_kerberos_authentication)
            else exclude.add("user_principal_name")
        )
        (
            include.add("use_ticket_cache")
            if (self.use_kerberos_authentication == "true" or self.use_kerberos_authentication)
            and (self.use_keytab == "false" or not self.use_keytab)
            else exclude.add("use_ticket_cache")
        )
        (
            include.add("core_site_xml")
            if (
                self.input_method_for_xml_files
                and (
                    (
                        hasattr(self.input_method_for_xml_files, "value")
                        and self.input_method_for_xml_files.value == "content"
                    )
                    or (self.input_method_for_xml_files == "content")
                )
            )
            else exclude.add("core_site_xml")
        )
        (
            include.add("simple_authentication_sasl_username")
            if (not self.defer_credentials)
            and (
                (not self.use_kerberos_authentication)
                or (self.use_kerberos_authentication == "false" or not self.use_kerberos_authentication)
            )
            else exclude.add("simple_authentication_sasl_username")
        )
        (
            include.add("cas_lite_service_authorization_header")
            if (self.use_cas_lite_service == "true" or self.use_cas_lite_service)
            else exclude.add("cas_lite_service_authorization_header")
        )
        (
            include.add("core_site_xml_path")
            if (
                self.input_method_for_xml_files
                and (
                    (
                        hasattr(self.input_method_for_xml_files, "value")
                        and self.input_method_for_xml_files.value == "path"
                    )
                    or (self.input_method_for_xml_files == "path")
                )
            )
            else exclude.add("core_site_xml_path")
        )
        (
            include.add("password")
            if (self.use_kerberos_authentication == "true" or self.use_kerberos_authentication)
            and (self.use_keytab == "false" or not self.use_keytab)
            else exclude.add("password")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
