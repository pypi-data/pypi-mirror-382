from enum import Enum
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    model_serializer,
)
from typing import Any, Literal


class Method(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthenticationType(Enum):
    none = "NoAuth"
    api_key = "APIKeyAuth"
    bearer_token = "BearerAuth"
    basic_auth = "BasicAuth"
    digest_auth = "DigestAuth"


class AddTo(Enum):
    request_header = "HEADER"
    query_param = "QUERY_PARAMS"


class BodyType(Enum):
    none = "NONE"
    form_data = "FORM_DATA"
    x_www_form_urlencoded = "X_WWW_FORM_URLENCODED"
    raw = "RAW"
    binary = "BINARY"


class CertificateType(Enum):
    pem_text = "PEM_TEXT"
    pem_file = "PEM_FILE"
    store_file = "STORE_FILE"


class StoreType(Enum):
    PKCS12 = "PKCS12"
    JKS = "JKS"
    JCEKS = "JCEKS"


class ActionOnFailure(Enum):
    abort = "ABORT"
    reject = "REJECT"
    ignore = "IGNORE"


class DataOutputControl(Enum):
    no_output = "NO_OUTPUT"
    output_per_iteration = "PER_ITERATION"
    output_when_request_complete = "FINAL_ITERATION"


class DataType(Enum):
    Integer = "INTEGER"
    Float = "FLOAT"
    Long = "LONG"
    Double = "DOUBLE"
    BigInteger = "BIG_INTEGER"
    BigDecimal = "BIG_DECIMAL"
    String = "STRING"
    Boolean = "BOOLEAN"
    List = "LIST"
    Set = "SET"
    Map = "MAP"
    Unknown = "UNKNOWN"


class Authentication(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    same_config: bool = Field(False, alias="inherit", description="The same configuration as request 0")
    authentication_type: AuthenticationType = Field(AuthenticationType.none, alias="type")
    add_to: AddTo = Field(None, alias="add_to")
    key: str = Field(None, alias="key")
    value: str = Field(None, alias="value")
    token: str = Field(None, alias="token")
    username: str = Field(None, alias="username")
    password: str = Field(None, alias="password")
    use_expression_token: bool = Field(None, alias="expression_bearerToken_on")
    use_expression_key: bool = Field(None, alias="expression_authKey_on")
    use_expression_value: bool = Field(None, alias="expression_authValue_on")
    use_expression_username: bool = Field(None, alias="expression_username_on")
    use_expression_password: bool = Field(None, alias="expression_password_on")

    @field_serializer("key")
    def serialize_key(self, key: str | dict | None) -> dict | None:
        if key is None:
            return key
        if isinstance(key, dict):
            return key
        if self.use_expression_key:
            return {"expression": key}
        return {"expression": f"`{key}`"}

    @field_serializer("value")
    def serialize_value(self, value: str | dict | None) -> dict | None:
        if value is None:
            return value
        if isinstance(value, dict):
            return value
        if self.use_expression_value:
            return {"expression": value}
        return {"expression": f"`{value}`"}

    @field_serializer("token")
    def serialize_token(self, token: str | dict | None) -> dict | None:
        if token is None:
            return token
        if isinstance(token, dict):
            return token
        if self.use_expression_token:
            return {"expression": token}
        return {"expression": f"`{token}`"}

    @field_serializer("username")
    def serialize_username(self, username: str | dict | None) -> dict | None:
        if username is None:
            return username
        if isinstance(username, dict):
            return username
        if self.use_expression_username:
            return {"expression": username}
        return {"expression": f"`{username}`"}

    @field_serializer("password")
    def serialize_password(self, password: str | dict | None) -> dict | None:
        if password is None:
            return password
        if isinstance(password, dict):
            return password
        if self.use_expression_password:
            return {"expression": password}
        return {"expression": f"`{password}`"}


class Parameter(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str = Field("", alias="key")
    default_value: str = Field("", alias="default_value")
    derivation: str = Field("", alias="derivation")
    description: str = Field("", alias="description")

    @field_serializer("derivation")
    def serialize_derivation(self, derivation: str | dict | None) -> dict | None:
        if derivation is None:
            return derivation
        if isinstance(derivation, dict):
            return derivation
        return {"expression": derivation}


class Header(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str = Field("", alias="key")
    default_value: str = Field("", alias="default_value")
    derivation: str = Field("", alias="derivation")
    description: str = Field("", alias="description")

    @field_serializer("derivation")
    def serialize_derivation(self, derivation: str | dict | None) -> dict | None:
        if derivation is None:
            return derivation
        if isinstance(derivation, dict):
            return derivation
        return {"expression": derivation}


class Cookie(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str = Field("", alias="key")
    default_value: str = Field("", alias="default_value")
    derivation: str = Field("", alias="derivation")
    description: str = Field("", alias="description")

    @field_serializer("derivation")
    def serialize_derivation(self, derivation: str | dict | None) -> dict | None:
        if derivation is None:
            return derivation
        if isinstance(derivation, dict):
            return derivation
        return {"expression": derivation}


class FormData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str = Field("", alias="key")
    default_value: str = Field("", alias="default_value")
    derivation: str = Field("", alias="derivation")
    description: str = Field("", alias="description")
    content_type: str = Field("", alias="content_type")
    type: Literal["TEXT", "FILE"] = Field("TEXT", alias="type")

    @field_serializer("derivation")
    def serialize_derivation(self, derivation: str | dict | None) -> dict | None:
        if derivation is None:
            return derivation
        if isinstance(derivation, dict):
            return derivation
        return {"expression": derivation}


class FormURLEncodedData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    key: str = Field("", alias="key")
    default_value: str = Field("", alias="default_value")
    derivation: str = Field("", alias="derivation")
    description: str = Field("", alias="description")

    @field_serializer("derivation")
    def serialize_derivation(self, derivation: str | dict | None) -> dict | None:
        if derivation is None:
            return derivation
        if isinstance(derivation, dict):
            return derivation
        return {"expression": derivation}


class Body(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: BodyType = Field(BodyType.none, alias="type")
    form_data: list[FormData] = Field([], alias="form_data")
    form_urlencoded_data: list[FormURLEncodedData] = Field([], alias="form_urlencoded_data")
    content_type: str = Field("", alias="content_type")
    encoding_type: str = Field("UTF-8", alias="charset")
    source: Literal["TEXT", "FILE", "DATA"] = Field(None, alias="source")
    file_path: str = Field(None, alias="file_path")
    raw_text: str = Field(None, alias="raw_text")
    binary_data: str = Field(None, alias="binary_data")
    use_expression_file_path: bool = Field(None, alias="expression_filePath_on")
    use_expression_text: bool = Field(None, alias="use_expression_text")
    use_expression_data: bool = Field(None, alias="use_expression_data")

    @field_serializer("source")
    def serialize_source(self, source: str | None) -> str | None:
        if source:
            return source
        type = self.type.value if hasattr(self.type, "value") else self.type
        if type not in ["BINARY", "RAW"]:
            return source
        if self.file_path:
            return "FILE"
        elif self.raw_text:
            return "TEXT"
        elif self.binary_data:
            return "DATA"
        return "FILE"

    @computed_field
    @property
    def data(self) -> dict | list:
        if self.type.value == "RAW":
            if self.source == "FILE":
                if self.file_path is None:
                    return {"expression": ""}
                elif isinstance(self.file_path, dict):
                    return self.file_path
                elif self.use_expression_file_path:
                    return {"expression": f"{self.file_path}"}
                else:
                    return {"expression": f"`{self.file_path}`"}
            elif self.source == "TEXT":
                if self.raw_text is None:
                    return {"expression": ""}
                elif isinstance(self.raw_text, dict):
                    return self.raw_text
                elif self.use_expression_text:
                    return {"expression": self.raw_text}
                else:
                    return {"expression": f"`{self.raw_text}`"}
            else:
                self.source = "TEXT"
                if self.raw_text is None:
                    return {"expression": ""}
                elif isinstance(self.raw_text, dict):
                    return self.raw_text
                elif self.use_expression_text:
                    return {"expression": self.raw_text}
                else:
                    return {"expression": f"`{self.raw_text}`"}
        elif self.type.value == "BINARY":
            if self.source == "DATA":
                if self.binary_data is None:
                    return {"expression": ""}
                elif isinstance(self.binary_data, dict):
                    return self.binary_data
                elif self.use_expression_data:
                    return {"expression": self.binary_data}
                else:
                    return {"expression": f"`{self.binary_data}`"}
            elif self.source == "FILE":
                if self.file_path is None:
                    return {"expression": ""}
                elif isinstance(self.file_path, dict):
                    return self.file_path
                elif self.use_expression_file_path:
                    return {"expression": self.file_path}
                else:
                    return {"expression": f"`{self.file_path}`"}
            else:
                self.source = "FILE"
                if self.file_path is None:
                    return {"expression": ""}
                elif isinstance(self.file_path, dict):
                    return self.file_path
                elif self.use_expression_file_path:
                    return {"expression": self.file_path}
                else:
                    return {"expression": f"`{self.file_path}`"}
        elif self.type.value == "FORM_DATA":
            return self.form_data
        elif self.type.value == "X_WWW_FORM_URLENCODED":
            return self.form_urlencoded_data
        elif self.type.value == "NONE":
            return {"expression": ""}
        else:
            return None

    @computed_field
    @property
    def expression_text_on(self) -> bool:
        return self.use_expression_text or self.use_expression_data


class RequestInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    same_config: bool = Field(False, alias="inherit", description="The same configuration as request 0")
    query_parameters: list[Parameter] = Field([], alias="params")
    custom_headers: list[Header] = Field([], alias="headers")
    additional_headers_on: bool = Field(False, alias="additional_headers_on")
    additional_headers: str | None = Field(None, alias="additional_headers")
    custom_cookies: list[Cookie] = Field([], alias="cookies")
    body: Body = Field(Body(), alias="body")

    @field_serializer("additional_headers")
    def serialize_additional_headers(self, additional_headers: str | dict | None) -> dict | None:
        if additional_headers is None:
            return additional_headers
        if isinstance(additional_headers, dict):
            return additional_headers
        return {"expression": additional_headers}


class Response(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    same_config: bool = Field(False, alias="inherit", description="The same configuration as request 0")
    type: Literal["TEXT", "FILE"] = Field("TEXT", alias="target")
    content_type: str = Field("", alias="content_type")
    encoding_type: str = Field("UTF-8", alias="charset")
    file_path: str = Field(None, alias="file_path")
    use_expression_file_path: bool = Field(None, alias="expression_filePath_on")

    @computed_field
    @property
    def content(self) -> dict:
        if self.type == "TEXT":
            return {
                "target": self.type,
            }
        elif self.type == "FILE":
            if self.use_expression_file_path:
                return {
                    "target": self.type,
                    "file_path": {"expression": f"`{self.file_path}`" or ""},
                }
            return {
                "target": self.type,
                "file_path": {"expression": f"{self.file_path}" or ""},
            }


class ServerCertificate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    certificate_type: CertificateType = Field(CertificateType.pem_text, alias="type")
    certificate: str = Field(None, alias="certificate")
    certificate_file: str = Field(None, alias="certificate_file")
    truststore_file: str = Field(None, alias="file_path")
    truststore_type: StoreType = Field(None, alias="store_type")
    truststore_password: str = Field(None, alias="password")
    use_expression_certificate: bool = Field(None, alias="is_expression_server_certificate")
    use_expression_certificate_file: bool = Field(None, alias="is_expression_server_certificate_file")
    use_expression_truststore_file: bool = Field(None, alias="is_expression_server_truststore_file")
    use_expression_truststore_password: bool = Field(None, alias="is_expression_server_truststore_password")

    @field_serializer("truststore_type")
    def serialize_truststore_type(self, truststore_type: StoreType | None) -> StoreType | None:
        if truststore_type:
            return truststore_type
        type = self.certificate_type.value if hasattr(self.certificate_type, "value") else self.certificate_type
        if type == "STORE_FILE":
            return StoreType.PKCS12
        return None

    @field_serializer("certificate")
    def serialize_certificate(self, certificate: str | dict | None) -> dict | None:
        if certificate is None:
            return certificate
        if isinstance(certificate, dict):
            return certificate
        if self.use_expression_certificate:
            return {"expression": certificate}
        return {"expression": f"`{certificate}`"}

    @field_serializer("certificate_file")
    def serialize_certificate_file(self, certificate_file: str | dict | None) -> dict | None:
        if certificate_file is None:
            return certificate_file
        if isinstance(certificate_file, dict):
            return certificate_file
        if self.use_expression_certificate_file:
            return {"expression": certificate_file}
        return {"expression": f"`{certificate_file}`"}

    @field_serializer("truststore_file")
    def serialize_truststore_file(self, truststore_file: str | dict | None) -> dict | None:
        if truststore_file is None:
            return truststore_file
        if isinstance(truststore_file, dict):
            return truststore_file
        if self.use_expression_truststore_file:
            return {"expression": truststore_file}
        return {"expression": f"`{truststore_file}`"}

    @field_serializer("truststore_password")
    def serialize_truststore_password(self, truststore_password: str | dict | None) -> dict | None:
        if truststore_password is None:
            return truststore_password
        if isinstance(truststore_password, dict):
            return truststore_password
        return {"expression": f"`{truststore_password}`"}


class ClientCertificate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    certificate_type: CertificateType = Field(CertificateType.pem_text, alias="type")
    certificate: str = Field(None, alias="certificate")
    private_key: str = Field(None, alias="private_key")
    certificate_file: str = Field(None, alias="certificate_file")
    private_key_file: str = Field(None, alias="private_key_file")
    keystore_file: str = Field(None, alias="file_path")
    keystore_type: StoreType = Field(None, alias="store_type")
    keystore_password: str = Field(None, alias="password")
    use_expression_certificate: bool = Field(None, alias="is_expression_client_certificate")
    use_expression_private_key: bool = Field(None, alias="is_expression_client_private_key")
    use_expression_certificate_file: bool = Field(None, alias="is_expression_client_certificate_file")
    use_expression_private_key_file: bool = Field(None, alias="is_expression_client_private_key_file")
    use_expression_keystore_file: bool = Field(None, alias="is_expression_client_keystore_file")
    use_expression_keystore_password: bool = Field(None, alias="is_expression_client_keystore_password")

    @field_serializer("keystore_type")
    def serialize_keystore_type(self, keystore_type: StoreType | None) -> StoreType | None:
        if keystore_type:
            return keystore_type
        type = self.certificate_type.value if hasattr(self.certificate_type, "value") else self.certificate_type
        if type == "STORE_FILE":
            return StoreType.PKCS12
        return None

    @field_serializer("certificate")
    def serialize_certificate(self, certificate: str | dict | None) -> dict | None:
        if certificate is None:
            return certificate
        if isinstance(certificate, dict):
            return certificate
        elif self.use_expression_certificate:
            return {"expression": certificate}
        return {"expression": f"`{certificate}`"}

    @field_serializer("private_key")
    def serialize_private_key(self, private_key: str | dict | None) -> dict | None:
        if private_key is None:
            return private_key
        if isinstance(private_key, dict):
            return private_key
        elif self.use_expression_private_key:
            return {"expression": private_key}
        return {"expression": f"`{private_key}`"}

    @field_serializer("certificate_file")
    def serialize_certificate_file(self, certificate_file: str | dict | None) -> dict | None:
        if certificate_file is None:
            return certificate_file
        if isinstance(certificate_file, dict):
            return certificate_file
        elif self.use_expression_certificate_file:
            return {"expression": certificate_file}
        return {"expression": f"`{certificate_file}`"}

    @field_serializer("private_key_file")
    def serialize_private_key_file(self, private_key_file: str | dict | None) -> dict | None:
        if private_key_file is None:
            return private_key_file
        if isinstance(private_key_file, dict):
            return private_key_file
        elif self.use_expression_private_key_file:
            return {"expression": private_key_file}
        return {"expression": f"`{private_key_file}`"}

    @field_serializer("keystore_file")
    def serialize_keystore_file(self, keystore_file: str | dict | None) -> dict | None:
        if keystore_file is None:
            return keystore_file
        if isinstance(keystore_file, dict):
            return keystore_file
        elif self.use_expression_keystore_file:
            return {"expression": keystore_file}
        return {"expression": f"`{keystore_file}`"}

    @field_serializer("keystore_password")
    def serialize_keystore_password(self, keystore_password: str | dict | None) -> dict | None:
        if keystore_password is None:
            return keystore_password
        if isinstance(keystore_password, dict):
            return keystore_password
        elif self.use_expression_keystore_password:
            return {"expression": keystore_password}
        return {"expression": f"`{keystore_password}`"}


class Proxy(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    host: str = Field("", alias="host")
    port: str = Field("", alias="port")
    username: str = Field("", alias="username")
    password: str = Field("", alias="password")


class Settings(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    same_config: bool = Field(False, alias="inherit", description="The same configuration as request 0")
    enable_ssl: bool = Field(False, alias="enable_ssl")
    accept_self_signed_certificate: bool = Field(False, alias="accept_self_signed_certificate")
    verify_host_name: bool = Field(False, alias="verify_host")
    ssl_server_authentication: bool = Field(False, alias="enable_ssl_server")
    server_certificate: ServerCertificate = Field(None, alias="server_cert")
    ssl_client_authentication: bool = Field(False, alias="enable_ssl_client")
    client_certificate: ClientCertificate = Field(None, alias="client_cert")
    timeout_duration: int = Field(180000, alias="timeout_duration")
    retry_on_failure: int = Field(5, alias="retry_on_failure")
    use_proxy_server: bool = Field(False, alias="use_proxy")
    proxy: Proxy = Field(Proxy(), alias="proxy")
    action_on_failure: ActionOnFailure = Field(ActionOnFailure.abort, alias="on_error_control")

    @computed_field(alias="server_certificate")
    @property
    def server_cert(self) -> str | None:
        if self.server_certificate:
            return None
        return ""

    @computed_field(alias="client_certificate")
    @property
    def client_cert(self) -> str | None:
        if self.client_certificate:
            return None
        return ""


class Control(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    same_config: bool = Field(False, alias="inherit", description="The same configuration as request 0")
    enable_pagination: bool = Field(False, alias="iteration")
    pagination_condition: str = Field("", alias="prerequisite")
    data_output_control: DataOutputControl = Field(DataOutputControl.output_when_request_complete, alias="output_type")
    pre_action: str = Field("", alias="pre_action")
    post_action: str = Field("", alias="post_action")
    ignore_request_when_pre_action_false: bool = Field(False, alias="skip_on_pre_action_false")

    @field_serializer("pre_action")
    def serialize_pre_action(self, pre_action: str | dict | None) -> dict | None:
        if pre_action is None:
            return pre_action
        if isinstance(pre_action, dict):
            return pre_action
        return {"expression": pre_action}

    @field_serializer("post_action")
    def serialize_post_action(self, post_action: str | dict | None) -> dict | None:
        if post_action is None:
            return post_action
        if isinstance(post_action, dict):
            return post_action
        return {"expression": post_action}

    @field_serializer("pagination_condition")
    def serialize_(self, pagination_condition: str | dict | None) -> dict | None:
        if pagination_condition is None:
            return pagination_condition
        if isinstance(pagination_condition, dict):
            return pagination_condition
        return {"expression": pagination_condition}


class Request(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    method: Method = Field(Method.GET, alias="method")
    url: str = Field(None, alias="url")
    use_expression_url: bool = Field(None, alias="expression_endpoint_on")
    authentication: Authentication = Field(None, alias="authentication")
    request: RequestInfo = Field(None, alias="request")
    response: Response = Field(None, alias="response")
    settings: Settings = Field(None, alias="settings")
    control: Control = Field(None, alias="control")

    @computed_field
    @property
    def endpoint(self) -> dict:
        ep = {"method": self.method, "url": {"expression": f"`{self.url}`" or ""}}
        if self.use_expression_url:
            ep["expression_endpoint_on"] = self.use_expression_url
            ep["url"] = {"expression": self.url}
        return ep

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        model_dict = {
            "endpoint": self.endpoint,
            "authentication": {
                "inherit": self.authentication.same_config,
                "body": self.authentication.model_dump(by_alias=True, exclude={"same_config"}, exclude_none=True),
            },
            "request": self.request.model_dump(
                exclude_none=True,
                by_alias=True,
                exclude={"body", "additional_headers_on"},
            ),
            "response": self.response.model_dump(exclude_none=True, by_alias=True, include={"same_config"}),
            "settings": self.settings.model_dump(exclude_none=True, by_alias=True),
            "control": self.control.model_dump(exclude_none=True, by_alias=True),
        }
        if self.request.body:
            model_dict["request"]["body"] = {
                "content": self.request.body.model_dump(
                    exclude_none=True,
                    by_alias=True,
                    exclude={
                        "form_data",
                        "form_urlencoded_data",
                        "file_path",
                        "raw_test",
                        "use_expression_text",
                        "use_expression_data",
                        "use_expression_file_path",
                        "expression_text_on",
                    },
                ),
                **self.request.body.model_dump(
                    exclude_none=True,
                    by_alias=True,
                    include={"use_expression_file_path", "expression_text_on"},
                ),
                **self.request.model_dump(
                    include={"additional_headers_on"},
                    exclude_none=True,
                    by_alias=True,
                    exclude_defaults=True,
                ),
            }
        model_dict["response"]["body"] = self.response.model_dump(
            exclude_none=True,
            by_alias=True,
            include={
                "content",
                "content_type",
                "encoding_type",
                "use_expression_file_path",
            },
        )

        if "params" in model_dict["request"]:
            for i, param in enumerate(model_dict["request"]["params"]):
                param["id"] = i
        if "headers" in model_dict["request"]:
            for i, header in enumerate(model_dict["request"]["headers"]):
                header["id"] = i
        if "cookies" in model_dict["request"]:
            for i, cookie in enumerate(model_dict["request"]["cookies"]):
                cookie["id"] = i
        if "body" in model_dict["request"] and "data" in model_dict["request"]["body"]["content"]:
            if isinstance(model_dict["request"]["body"]["content"]["data"], list):
                for i, data in enumerate(model_dict["request"]["body"]["content"]["data"]):
                    data["id"] = i
        return model_dict


class Variable(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field("", alias="name")
    data_type: DataType = Field("", alias="type")
    default_value: str = Field("", alias="default_value")
    derivation: str = Field("", alias="derivation")
    description: str = Field("", alias="description")

    @field_serializer("derivation")
    def serialize_(self, derivation: str | dict | None) -> dict | None:
        if derivation is None:
            return derivation
        if isinstance(derivation, dict):
            return derivation
        return {"expression": derivation}


class rest:
    Method = Method
    AuthenticationType = AuthenticationType
    AddTo = AddTo
    BodyType = BodyType
    CertificateType = CertificateType
    StoreType = StoreType
    ActionOnFailure = ActionOnFailure
    DataOutputControl = DataOutputControl
    DataType = DataType
    Authentication = Authentication
    Parameter = Parameter
    Header = Header
    Cookie = Cookie
    FormData = FormData
    FormURLEncodedData = FormURLEncodedData
    Body = Body
    RequestInfo = RequestInfo
    Response = Response
    ServerCertificate = ServerCertificate
    ClientCertificate = ClientCertificate
    Proxy = Proxy
    Settings = Settings
    Control = Control
    Request = Request
    Variable = Variable
