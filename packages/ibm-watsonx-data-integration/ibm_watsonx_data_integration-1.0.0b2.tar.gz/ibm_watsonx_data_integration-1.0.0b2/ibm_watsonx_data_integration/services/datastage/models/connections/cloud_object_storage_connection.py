from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.connections.base_connection import BaseConnection
from ibm_watsonx_data_integration.services.datastage.models.enums import CLOUD_OBJECT_STORAGE_CONNECTION
from pydantic import ConfigDict, Field
from typing import ClassVar


class AuthMethod(Enum):
    accesskey_secretkey = "accesskey_secretkey"
    instanceid_apikey = "instanceid_apikey"
    instanceid_apikey_accesskey_secretkey = "instanceid_apikey_accesskey_secretkey"
    credentials = "credentials"


class CloudObjectStorageConn(BaseConnection):
    model_config = ConfigDict(populate_by_name=True)

    datasource_type: ClassVar[str] = "193a97c1-4475-4a19-b90c-295c4fdc6517"
    asset_id: str | None = None
    proj_id: str | None = None
    name: str = Field(None, alias="name")
    ds_host: str | None = Field(None, alias="_host")
    ds_port: str | None = Field(None, alias="_port")
    access_key: str | None = Field(None, alias="access_key")
    api_key: str = Field(None, alias="api_key")
    authentication_method: CLOUD_OBJECT_STORAGE_CONNECTION.AuthMethod | None = Field(None, alias="auth_method")
    discover_data_assets: bool | None = Field(None, alias="auto_discovery")
    bucket: str | None = Field(None, alias="bucket")
    cluster_access_token: str | None = Field(None, alias="cluster_access_token")
    cluster_user_name: str | None = Field(None, alias="cluster_user_name")
    service_credentials: str | None = Field(None, alias="credentials")
    credentials_file_path: str | None = Field(None, alias="credentials_file")
    defer_credentials: bool | None = Field(False, alias="defer_credentials")
    iam_cos_url: str | None = Field(None, alias="iam_cos_url")
    iam_url: str | None = Field(None, alias="iam_url")
    region_deprecated: str | None = Field(None, alias="region")
    resource_instance_id: str | None = Field(None, alias="resource_instance_id")
    secret_key: str = Field(None, alias="secret_key")
    ssl_certificate: str | None = Field(None, alias="ssl_certificate")
    validate_ssl_certificate: bool | None = Field(None, alias="ssl_certificate_validation")
    trust_all_ssl_certificates: bool | None = Field(False, alias="trust_all_ssl_cert")
    url: str = Field(None, alias="url")
    vaulted_properties: str | None = Field(None, alias="vaulted_properties")
    ssl_certificate_file: str | None = Field(None, alias="ssl_certificate_file")
    hidden_dummy_property1: str | None = Field(None, alias="hiddenDummyProperty1")
    hidden_dummy_property2: str | None = Field(None, alias="hiddenDummyProperty2")

    def validate(self):
        include = set()
        exclude = set()

        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        (
            include.add("secret_key")
            if (
                (
                    ((not self.defer_credentials))
                    and ((self.access_key))
                    and ((not self.service_credentials))
                    and ((not self.credentials_file_path))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "accesskey_secretkey"
                                    )
                                    or (self.authentication_method == "accesskey_secretkey")
                                )
                            )
                        )
                        or (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "instanceid_apikey_accesskey_secretkey"
                                    )
                                    or (self.authentication_method == "instanceid_apikey_accesskey_secretkey")
                                )
                            )
                        )
                    )
                )
                or (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "accesskey_secretkey"
                                )
                                or (self.authentication_method == "accesskey_secretkey")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "instanceid_apikey_accesskey_secretkey"
                            )
                            or (self.authentication_method == "instanceid_apikey_accesskey_secretkey")
                        )
                    )
                )
            )
            else exclude.add("secret_key")
        )
        (
            include.add("credentials_file_path")
            if (
                ((not self.defer_credentials))
                and (not self.access_key)
                and (not self.api_key)
                and (not self.service_credentials)
                and (not self.resource_instance_id)
                and (not self.secret_key)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "credentials_file"
                        )
                        or (self.authentication_method == "credentials_file")
                    )
                )
            )
            else exclude.add("credentials_file_path")
        )
        (
            include.add("service_credentials")
            if (
                ((not self.defer_credentials))
                and (not self.access_key)
                and (not self.api_key)
                and (not self.credentials_file_path)
                and (not self.resource_instance_id)
                and (not self.secret_key)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value == "credentials"
                        )
                        or (self.authentication_method == "credentials")
                    )
                )
            )
            else exclude.add("service_credentials")
        )
        (
            include.add("api_key")
            if (
                (
                    ((not self.defer_credentials))
                    and ((not self.service_credentials))
                    and ((not self.credentials_file_path))
                    and ((self.resource_instance_id))
                    and (
                        (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "instanceid_apikey"
                                    )
                                    or (self.authentication_method == "instanceid_apikey")
                                )
                            )
                        )
                        or (
                            (
                                self.authentication_method
                                and (
                                    (
                                        hasattr(self.authentication_method, "value")
                                        and self.authentication_method.value == "instanceid_apikey_accesskey_secretkey"
                                    )
                                    or (self.authentication_method == "instanceid_apikey_accesskey_secretkey")
                                )
                            )
                        )
                    )
                )
                or (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "instanceid_apikey"
                                )
                                or (self.authentication_method == "instanceid_apikey")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "instanceid_apikey_accesskey_secretkey"
                            )
                            or (self.authentication_method == "instanceid_apikey_accesskey_secretkey")
                        )
                    )
                )
            )
            else exclude.add("api_key")
        )
        (
            include.add("resource_instance_id")
            if (
                ((not self.defer_credentials))
                and (not self.service_credentials)
                and (not self.credentials_file_path)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "instanceid_apikey"
                                )
                                or (self.authentication_method == "instanceid_apikey")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "instanceid_apikey_accesskey_secretkey"
                            )
                            or (self.authentication_method == "instanceid_apikey_accesskey_secretkey")
                        )
                    )
                )
            )
            else exclude.add("resource_instance_id")
        )
        (
            include.add("access_key")
            if (
                ((not self.defer_credentials))
                and (not self.service_credentials)
                and (not self.credentials_file_path)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "accesskey_secretkey"
                                )
                                or (self.authentication_method == "accesskey_secretkey")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "instanceid_apikey_accesskey_secretkey"
                            )
                            or (self.authentication_method == "instanceid_apikey_accesskey_secretkey")
                        )
                    )
                )
            )
            else exclude.add("access_key")
        )
        include.add("region_deprecated") if (self.resource_instance_id) else exclude.add("region_deprecated")
        (
            include.add("api_key")
            if (
                ((not self.defer_credentials))
                and (not self.service_credentials)
                and (not self.credentials_file_path)
                and (self.resource_instance_id)
                and (
                    (
                        (
                            self.authentication_method
                            and (
                                (
                                    hasattr(self.authentication_method, "value")
                                    and self.authentication_method.value == "instanceid_apikey"
                                )
                                or (self.authentication_method == "instanceid_apikey")
                            )
                        )
                    )
                    or (
                        self.authentication_method
                        and (
                            (
                                hasattr(self.authentication_method, "value")
                                and self.authentication_method.value == "instanceid_apikey_accesskey_secretkey"
                            )
                            or (self.authentication_method == "instanceid_apikey_accesskey_secretkey")
                        )
                    )
                )
            )
            else exclude.add("api_key")
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
        include.add("credentials_file_path") if (self.hidden_dummy_property1) else exclude.add("credentials_file_path")
        include.add("vaulted_properties") if (self.hidden_dummy_property1) else exclude.add("vaulted_properties")
        include.add("ssl_certificate_file") if (self.hidden_dummy_property1) else exclude.add("ssl_certificate_file")

        include.add("region_deprecated") if (self.resource_instance_id) else exclude.add("region_deprecated")
        (
            include.add("api_key")
            if (
                (not self.defer_credentials)
                and (not self.service_credentials)
                and (not self.credentials_file_path)
                and (self.resource_instance_id)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "instanceid_apikey" in str(self.authentication_method.value)
                        )
                        or ("instanceid_apikey" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "instanceid_apikey_accesskey_secretkey" in str(self.authentication_method.value)
                        )
                        or ("instanceid_apikey_accesskey_secretkey" in str(self.authentication_method))
                    )
                )
            )
            or (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "instanceid_apikey" in str(self.authentication_method.value)
                    )
                    or ("instanceid_apikey" in str(self.authentication_method))
                )
                or self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "instanceid_apikey_accesskey_secretkey" in str(self.authentication_method.value)
                    )
                    or ("instanceid_apikey_accesskey_secretkey" in str(self.authentication_method))
                )
            )
            else exclude.add("api_key")
        )
        (
            include.add("secret_key")
            if (
                (not self.defer_credentials)
                and (self.access_key)
                and (not self.service_credentials)
                and (not self.credentials_file_path)
                and (
                    self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "accesskey_secretkey" in str(self.authentication_method.value)
                        )
                        or ("accesskey_secretkey" in str(self.authentication_method))
                    )
                    and self.authentication_method
                    and (
                        (
                            hasattr(self.authentication_method, "value")
                            and self.authentication_method.value
                            and "instanceid_apikey_accesskey_secretkey" in str(self.authentication_method.value)
                        )
                        or ("instanceid_apikey_accesskey_secretkey" in str(self.authentication_method))
                    )
                )
            )
            or (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "accesskey_secretkey" in str(self.authentication_method.value)
                    )
                    or ("accesskey_secretkey" in str(self.authentication_method))
                )
                or self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "instanceid_apikey_accesskey_secretkey" in str(self.authentication_method.value)
                    )
                    or ("instanceid_apikey_accesskey_secretkey" in str(self.authentication_method))
                )
            )
            else exclude.add("secret_key")
        )
        (
            include.add("credentials_file_path")
            if (not self.defer_credentials)
            and (not self.access_key)
            and (not self.api_key)
            and (not self.service_credentials)
            and (not self.resource_instance_id)
            and (not self.secret_key)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "credentials_file" in str(self.authentication_method.value)
                    )
                    or ("credentials_file" in str(self.authentication_method))
                )
            )
            else exclude.add("credentials_file_path")
        )
        include.add("ssl_certificate_file") if (not self.ssl_certificate) else exclude.add("ssl_certificate_file")
        include.add("ssl_certificate") if (not self.ssl_certificate_file) else exclude.add("ssl_certificate")
        (
            include.add("resource_instance_id")
            if (not self.defer_credentials)
            and (not self.service_credentials)
            and (not self.credentials_file_path)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "instanceid_apikey" in str(self.authentication_method.value)
                    )
                    or ("instanceid_apikey" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "instanceid_apikey_accesskey_secretkey" in str(self.authentication_method.value)
                    )
                    or ("instanceid_apikey_accesskey_secretkey" in str(self.authentication_method))
                )
            )
            else exclude.add("resource_instance_id")
        )
        (
            include.add("service_credentials")
            if (not self.defer_credentials)
            and (not self.access_key)
            and (not self.api_key)
            and (not self.credentials_file_path)
            and (not self.resource_instance_id)
            and (not self.secret_key)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "credentials" in str(self.authentication_method.value)
                    )
                    or ("credentials" in str(self.authentication_method))
                )
            )
            else exclude.add("service_credentials")
        )
        (
            include.add("access_key")
            if (not self.defer_credentials)
            and (not self.service_credentials)
            and (not self.credentials_file_path)
            and (
                self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "accesskey_secretkey" in str(self.authentication_method.value)
                    )
                    or ("accesskey_secretkey" in str(self.authentication_method))
                )
                and self.authentication_method
                and (
                    (
                        hasattr(self.authentication_method, "value")
                        and self.authentication_method.value
                        and "instanceid_apikey_accesskey_secretkey" in str(self.authentication_method.value)
                    )
                    or ("instanceid_apikey_accesskey_secretkey" in str(self.authentication_method))
                )
            )
            else exclude.add("access_key")
        )
        return include, exclude

    @classmethod
    def from_dict(cls, properties):
        return cls.model_construct(**properties)
