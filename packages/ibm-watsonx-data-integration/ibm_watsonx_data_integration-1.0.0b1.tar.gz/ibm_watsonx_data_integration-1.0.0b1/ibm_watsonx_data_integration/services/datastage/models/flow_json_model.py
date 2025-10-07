import json
import re
from enum import Enum
from ibm_watsonx_data_integration.services.datastage.models.enums import FIELD
from pydantic import BaseModel, ConfigDict, Discriminator, Field, RootModel, Tag
from typing import Annotated, Any, Literal, Union


class Version(Enum):
    v3 = "3.0"


class JsonSchema(Enum):
    http = "http://api.dataplatform.ibm.com/schemas/common-pipeline/pipeline-flow/pipeline-flow-v3-schema.json"
    https = "https://api.dataplatform.ibm.com/schemas/common-pipeline/pipeline-flow/pipeline-flow-v3-schema.json"


class SubflowRef(BaseModel):
    url: str | None = None
    pipeline_id_ref: str
    name: str | None = None


class JsonSchema1(Enum):
    datarecord_schema = "https://api.dataplatform.ibm.com/schemas/common-pipeline/datarecord-metadata/datarecord-metadata-v3-schema.json"


class Measure(Enum):
    range = "range"
    discrete = "discrete"
    flag = "flag"
    set = "set"
    ordered_set = "ordered-set"
    typeless = "typeless"
    collection = "collection"
    geospatial = "geospatial"
    default = "default"

    def __str__(self):
        return self.name


class ModelingRole(Enum):
    input = "input"
    target = "target"
    both = "both"
    none = "none"
    partition = "partition"
    split = "split"
    frequency = "frequency"
    record_id = "record-id"

    def __str__(self):
        return self.name


class Range(BaseModel):
    min: str | float
    max: str | float


class Metadata(BaseModel):
    description: str | None = None
    measure: Measure | None = None
    modeling_role: ModelingRole | None = None
    max_length: int | None = None
    min_length: int | None = None
    decimal_precision: int | None = None
    decimal_scale: int | None = None
    values: list[str | int | bool] | None = None
    range: Range | None = None
    runtime_type: str | None = None
    is_key: bool | None = None
    is_signed: bool | None = None
    item_index: int | None = None
    source_field_id: str | None = None

    def __str__(self):
        dictionary = {
            "description": self.description,
            "measure": self.measure,
            "modeling_role": self.modeling_role,
            "max_length": self.max_length,
            "min_length": self.min_length,
            "decimal_precision": self.decimal_precision,
            "decimal_scale": self.decimal_scale,
            "values": self.values,
            "range": self.range,
            "runtime_type": self.runtime_type,
            "is_key": self.is_key,
            "is_signed": self.is_signed,
            "item_index": self.item_index,
            "source_field_id": self.source_field_id,
        }

        # remove all fields that is None.
        for key, value in dictionary.copy().items():
            if value is None:
                dictionary.pop(key)

        return json.dumps(dictionary, indent=4)


class AppDataDef(BaseModel):
    pass


class ParamSet(BaseModel):
    name: str | None = None
    ref: str
    catalog_ref: str | None = None
    project_ref: str | None = None
    space_ref: str | None = None


class PipelineFlowUI(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    description: str | None = None
    class_name: str | None = None


class ZoomObject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    k: float


class ZoomObjectDef(RootModel[Union[int, ZoomObject]]):
    pass


class CommentLink(BaseModel):
    model_config = ConfigDict(extra="allow")

    node_ref: str
    class_name: str | None = None
    style: str | dict[str, Any] | None = None


class Type5(Enum):
    info = "info"
    error = "error"
    warning = "warning"


class Message(BaseModel):
    id_ref: str
    validation_id: str | None = None
    type: Type5
    text: str


class Position(Enum):
    topLeft = "topLeft"
    topCenter = "topCenter"
    topRight = "topRight"
    middleLeft = "middleLeft"
    middleCenter = "middleCenter"
    middleRight = "middleRight"
    bottomLeft = "bottomLeft"
    bottomCenter = "bottomCenter"
    bottomRight = "bottomRight"


class Position2(Enum):
    source = "source"
    middle = "middle"
    target = "target"


class LabelAlign(Enum):
    left = "left"
    center = "center"


class DecorationSharedProperties(BaseModel):
    id: str | None = None
    x_pos: float | None = None
    y_pos: float | None = None
    width: int | None = None
    height: int | None = None
    hotspot: bool | None = None
    class_name: str | None = None
    tooltip: str | None = None
    temporary: bool | None = None


class Cardinality(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min: int | None = 1
    max: int | None = None


class PortUI(BaseModel):
    model_config = ConfigDict(extra="allow")

    cardinality: Cardinality | None = None
    class_name: str | None = None
    style: str | dict[str, Any] | None = None
    label: str | None = None


class RuntimeUI(BaseModel):
    model_config = ConfigDict(extra="allow")

    pass


class CommonPipelineConnection(BaseModel):
    name: str | None = None
    app_data: AppDataDef | None = None
    ref: str
    catalog_ref: str | None = None
    project_ref: str | None = None
    space_ref: str | None = None
    properties: dict[str, Any] | None = None
    connData: dict[str, Any] | None = None


class Properties(BaseModel):
    model_config = ConfigDict(extra="allow")

    attachment_ref: str | None = None
    name: str | None = False
    no_write_schema: bool | None = False
    no_write_status: bool | None = False


class CommonPipelineDataAsset(BaseModel):
    app_data: AppDataDef | None = None
    ref: str | None = None
    catalog_ref: str | None = None
    project_ref: str | None = None
    space_ref: str | None = None
    properties: Properties | None = None


class AppData(BaseModel):
    model_config = ConfigDict(extra="allow")

    ui_data: PipelineFlowUI | None = None


class PortAppData(BaseModel):
    model_config = ConfigDict(extra="allow")

    ui_data: PortUI | None = None


class RuntimeAppData(BaseModel):
    model_config = ConfigDict(extra="allow")

    ui_data: RuntimeUI | None = None


class Runtime(BaseModel):
    id: str
    name: str
    version: str | None = None
    app_data: RuntimeAppData | None = None


class FieldModel(BaseModel):
    """Serializable proxy for the FieldModelComplex class. Used in serializing fields for use in schema JSONs."""

    name: str
    type: str | None = "unknown"
    nullable: bool | None = False
    metadata: Metadata | None = None
    app_data: dict[str, Any] | None = None


class FieldModelComplex(BaseModel):
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)
    name: str
    type: str | None = "unknown"
    type_code: str | None = None
    odbc_type: str
    nullable: bool | None = False
    metadata: Metadata | None = None
    app_data: dict[str, Any] | None = None
    length: int | None = None
    scale: int | None = None
    signed: bool | None = Field(True)
    description: str | None = ""
    primary_key: bool | None = False
    unicode: FIELD.Unicode | None = Field(None, alias="extended")
    sqltype: int | None = 1
    ds_data_type: str | None = "WSMQ.QUEUENAME"
    data_element: str | None = "null"
    key_position: int | None = 1
    display_size: int | None = 0
    field_pos: int | None = 1
    level_no: int | None = None
    occurs: int | None = None
    sign_option: int | None = 0
    ds_scd_purpose: int | None = 0
    ds_sync_indicator: int | None = 0
    pad_char: str | None = ""  # TODO: Why are there two padchars (pad_char and padchar)
    extended_precision: int | None = 0
    tagged_subrec: int | None = 0
    occurs_varying: int | None = 0
    Maps_from_input_column: str | None = Field("", alias="Maps from input column")
    byte_to_skip: int | str | None = Field("", alias="skip")
    delim: FIELD.Delim | None = None
    delim_string: str | None = None
    generate: bool | None = False
    prefix_bytes: FIELD.Prefix | None = Field(None, alias="prefix")
    vector_prefix: FIELD.VectorPrefix | None = (
        None  # TODO: figure out why 0 is the default, but is not in the Prefix Enum
    )
    quote: FIELD.Quote | None = None
    start_position: int | None = Field(None, alias="position")
    tagcase: int | None = None
    charset: FIELD.CharSet | None = None
    default: int | str | None = None
    export_ebcdic_as_ascii: bool | None = Field(False)
    max_width: int | None = None
    width: int | None = max_width
    link_keep: bool | None = Field(False)
    padchar: FIELD.PadChar | None = None
    cycle_increment: FIELD.CycleIncrement | int | None = None
    cycle_initial_value: FIELD.CycleInitialValue | int | None = None
    cycle_limit: FIELD.CycleLimit | int | None = None
    cycle_values: list[str | int] | None = None
    alphabet: str | None = None
    time_scale: int | None = None
    byte_order: FIELD.ByteOrder | None = None
    c_format: str | None = Field(None)  # not sure how the handle the fact that this should only be included sometimes
    data_format: FIELD.DataFormat | None = None

    out_format: str | None = None
    reference: str | None = None
    generate_algorithm: FIELD.GenerateAlgorithm | None = None
    generate_type: FIELD.GenerateType | None = None
    random_limit: FIELD.RandomLimit | None = None
    random_seed: FIELD.RandomSeed | None = None
    random_signed: bool | None = False

    days_since: int | None = None
    date_format: str | None = None
    julian: bool | None = None

    generated_percent_invalid: int = Field(None, alias="invalids")
    epoch: int | None = None
    use_current_date: bool = Field(False)

    decimal_separator: FIELD.DecimalSeparator | None = None
    rounding: FIELD.Round | None = Field(None, alias="round")
    decimal_packed: FIELD.DecimalPacked | None = None
    check_decimal_packed: bool | None = Field(None, alias="check")
    decimal_packed_signed: bool | None = None
    sign_position: FIELD.SignPosition | None = None
    generated_percent_zeros: int = Field(None, alias="zeros")
    increment_scale: int | None = None
    precision: int | None = None

    midnight_seconds: bool = Field(False)
    time_scale_factor: int = Field(None, alias="_scale")
    extended_type: FIELD.TimeExtendedType | None = None
    allow_all_zeros: FIELD.AllowAllZeros | None = None

    timestamp_format: str | None = None
    vector_length_type: FIELD.VectorType | None = None
    apt_field_properties: str | None = None

    dimension_min_size: int | None = None

    actual_length: int | None = None
    null_length: int | None = None
    null_field: str | None = None
    nullseed: int | None = None
    nulls: int | None = None

    cycle: str | None = None

    def get_length(self):
        # return value, or return default derived from data type
        if self.length is not None:
            return self.length
        elif self.odbc_type in ["TIME"]:
            return 8
        elif self.odbc_type in ["TIMESTAMP"]:
            return 19
        elif self.odbc_type in [
            "SMALLINT",
            "INTEGER",
            "FLOAT",
            "DOUBLE",
            "DATE",
            "BIT",
            "TINYINT",
        ]:
            return 0
        else:
            return 100

    def get_scale(self):
        if self.scale is not None:
            return self.scale

        if self.extended_type is not None and self.extended_type != "" and self.extended_type != " ":
            return 6  # default value if extended type is set (see TIME and TIMESTAMP data types)

        return 0  # normal default value

    def get_cycle(self):
        if self.cycle:
            return self.cycle
        if self.generate_type == FIELD.GenerateType.cycle:
            cycle_dict_elements = []
            limit = self.cycle_limit
            if limit:
                limit = FieldModelComplex._get_enum_value(limit)
                if isinstance(limit, str):
                    cycle_dict_elements += [f"limit='{limit}'"]
                elif isinstance(limit, int):
                    cycle_dict_elements += [f"limit={limit}"]
            increment = self.cycle_increment
            if increment:
                increment = FieldModelComplex._get_enum_value(increment)
                if isinstance(increment, str):
                    cycle_dict_elements += [f"incr='{increment}'"]
                elif isinstance(increment, int):
                    cycle_dict_elements += [f"incr={increment}"]
            initial_value = self.cycle_initial_value
            if initial_value:
                initial_value = FieldModelComplex._get_enum_value(initial_value)
                if isinstance(initial_value, str):
                    cycle_dict_elements += [f"init='{initial_value}'"]
                elif isinstance(initial_value, int):
                    cycle_dict_elements += [f"init={initial_value}"]
            return "{" + ",".join(cycle_dict_elements) + "}"
        elif self.generate_algorithm == FIELD.GenerateAlgorithm.cycle:
            cycle_dict_elements = []
            cycle_values = self.cycle_values
            if cycle_values:
                for val in cycle_values:
                    if isinstance(val, str):
                        cycle_dict_elements += [f"value='{val}'"]
                    elif isinstance(val, int):
                        cycle_dict_elements += [f"value={val}"]
            return "{" + ",".join(cycle_dict_elements) + "}"
        return ""

    def get_random(self):
        random_dict_elements = []
        limit = self.random_limit
        if limit:
            limit = FieldModelComplex._get_enum_value(limit)
            if isinstance(limit, str):
                random_dict_elements += [f"limit='{limit}'"]
            elif isinstance(limit, int):
                random_dict_elements += [f"limit={limit}"]
        seed = self.random_seed
        if seed:
            seed = FieldModelComplex._get_enum_value(seed)
            if isinstance(seed, str):
                random_dict_elements += [f"seed='{seed}'"]
            elif isinstance(seed, int):
                random_dict_elements += [f"seed={seed}"]
        rand_signed = self.random_signed
        if rand_signed:
            random_dict_elements += ["signed"]
        return "{" + ",".join(random_dict_elements) + "}"

    @staticmethod
    def from_field_model(field_model: FieldModel):
        conversion_args = {
            "name": field_model.name,
            "type": field_model.type,
            "app_data": field_model.app_data,
            "metadata": field_model.metadata,
            "nullable": field_model.nullable,
        }
        if "odbc_type" in field_model.app_data:
            conversion_args["odbc_type"] = field_model.app_data["odbc_type"]
        else:
            raise Exception(
                "FieldModel was created without odbc data type, conversion to FieldModelComplex is impossible"
            )

        if "apt_field_properties" in field_model.app_data:
            conversion_args["apt_field_properties"] = field_model.app_data["apt_field_properties"]

        if (
            "dimension_min_size" in field_model.app_data
            and "dimension_max_size" in field_model.app_data
            and field_model.app_data["dimension_min_size"] == field_model.app_data["dimension_max_size"]
        ):
            conversion_args["occurs"] = field_model.app_data["dimension_min_size"]

        unicode = field_model.app_data.get("is_unicode_string", None)
        if unicode is not None:
            if unicode:
                conversion_args["unicode"] = FIELD.Unicode.true
            else:
                conversion_args["unicode"] = FIELD.Unicode.false

        extended_type = field_model.app_data.get("extended_type", None)
        if extended_type is not None:
            conversion_args["extended_type"] = FIELD.TimeExtendedType(extended_type)

        # if length is a consistent value (always if not default), then set length property. Otherwise rely on existing default setting logic
        if (
            (
                conversion_args["odbc_type"] in ["BINARY", "CHAR", "WCHAR"]
                and field_model.metadata.min_length == field_model.metadata.max_length
            )
            or (
                conversion_args["odbc_type"] in ["DECIMAL", "NUMERIC", "TIME", "TIMESTAMP"]
                and field_model.metadata.decimal_precision == field_model.metadata.max_length
            )
            or (
                conversion_args["odbc_type"]
                in [
                    "WLONGVARCHAR",
                    "LONGVARBINARY",
                    "LONGVARCHAR",
                    "WVARCHAR",
                    "REAL",
                    "UNKNOWN",
                    "VARBINARY",
                    "VARCHAR",
                ]
            )
        ):
            conversion_args["length"] = field_model.metadata.max_length

        conversion_args["time_scale"] = field_model.app_data.get("time_scale", 0)

        conversion_args["scale"] = field_model.metadata.decimal_scale

        conversion_args["primary_key"] = field_model.metadata.is_key
        conversion_args["description"] = field_model.metadata.description
        conversion_args["signed"] = field_model.metadata.is_signed
        conversion_args["level_no"] = (
            field_model.metadata.item_index if field_model.metadata.item_index is not None else 0
        )

        return FieldModelComplex(**conversion_args)

    def get_field_model(self):
        self.validate_properties()
        extended_properties_app_data = self.app_data.copy()

        extended_properties_app_data["odbc_type"] = self.odbc_type

        apt_props = self.get_aptfieldproperties()
        if apt_props != "":
            extended_properties_app_data["apt_field_properties"] = apt_props

        if self.occurs is not None:
            extended_properties_app_data["dimension_min_size"] = f"{self.occurs}"
            extended_properties_app_data["dimension_max_size"] = f"{self.occurs}"

        if (
            self.vector_length_type == FIELD.VectorType.variable
            or self.vector_length_type == FIELD.VectorType.variable.value
        ):
            extended_properties_app_data["dimension_min_size"] = "0"

        if self.unicode == FIELD.Unicode.true or self.unicode == FIELD.Unicode.true.value:
            extended_properties_app_data["is_unicode_string"] = True
        elif self.unicode == FIELD.Unicode.false or self.unicode == FIELD.Unicode.false.value:
            extended_properties_app_data["is_unicode_string"] = False

        if self.extended_type is not None:
            extended_properties_app_data["extended_type"] = (
                self.extended_type.value
                if isinstance(self.extended_type, FIELD.TimeExtendedType)
                else self.extended_type
            )

        if self.length is not None:
            if self.odbc_type in ["BINARY", "CHAR", "WCHAR"]:
                self.metadata.min_length = self.length
                self.metadata.max_length = self.length
            elif self.odbc_type in ["DECIMAL", "NUMERIC", "TIME", "TIMESTAMP"]:
                self.metadata.max_length = self.length
                self.metadata.decimal_precision = self.length
            elif self.odbc_type in [
                "WLONGVARCHAR",
                "LONGVARBINARY",
                "LONGVARCHAR",
                "WVARCHAR",
                "REAL",
                "UNKNOWN",
                "VARBINARY",
                "VARCHAR",
            ]:
                self.metadata.max_length = self.length

        self.metadata.decimal_scale = self.get_scale()

        if self.time_scale is not None:
            self.app_data["time_scale"] = self.time_scale

        self.metadata.is_key = self.primary_key
        self.metadata.description = self.description
        self.metadata.is_signed = self.signed
        self.metadata.item_index = self.level_no if self.level_no is not None else 0

        if self.type_code is not None:
            extended_properties_app_data["type_code"] = self.type_code

        return FieldModel(
            name=self.name,
            type=self.type,
            nullable=self.nullable,
            metadata=self.metadata,
            app_data=extended_properties_app_data,
        )

    def serialize_to_data_definition_column(self):
        self.validate_properties()
        dumped = {"name": self.name}
        dumped["type"] = self.get_type_props()
        dumped["properties"] = self.get_properties_props()

        return dumped

    def get_type_props(self):
        props = {"length", "scale", "nullable", "signed"}
        dumped = self.model_dump(include=props, by_alias=True)
        dumped["length"] = self.get_length()
        dumped["scale"] = self.get_scale()
        type_mapping = {
            "WCHAR": "NCHAR",
            "WVARCHAR": "NVARCHAR",
            "WLONGVARCHAR": "LONGNVARCHAR",
        }
        dumped["type"] = type_mapping.get(self.odbc_type, self.odbc_type)

        return dumped

    def get_properties_props(self):
        include_props: set[str] = {
            "Maps_from_input_column",
            "alphabet",
            "charset",
            "data_element",
            "default",
            "delim",
            "delim_string",
            "description",
            "display_size",
            "ds_data_type",
            "ds_scd_purpose",
            "ds_sync_indicator",
            "export_ebcdic_as_ascii",
            "unicode",
            "extended_precision",
            "field_pos",
            "generate",
            "key_position",
            "link_keep",
            "max_width",
            "occurs_varying",
            "pad_char",
            "padchar",
            "start_position",
            "primary_key",
            "quote",
            "sign_option",
            "byte_to_skip",
            "sqltype",
            "tagcase",
            "tagged_subrec",
            "time_scale",
            "width",
        }
        # add optional properties
        optional_props = {"occurs", "level_no", "extended_type"}
        include_props.update(optional_props)

        # special case for TIMESTAMP data type
        if self.extended_type is None and self.odbc_type == "TIMESTAMP":
            self.extended_type = " "

        dumped: dict = json.loads(
            self.model_dump_json(
                include=include_props,
                by_alias=True,
            )
        )

        # remove optional properties if unset
        for optional_prop in optional_props:
            if dumped[optional_prop] is None:
                dumped.pop(optional_prop)

        dumped["APTFieldProperties"] = self.get_aptfieldproperties()
        dumped["MisFieldProperties"] = self.get_misfieldproperties()
        default_overrides_for_unset_apt_properties = {
            "position": 0,
            "tagcase": 0,
            "default": "",
            "max_width": 0,
            "width": 0,
            "charset": "",
            "padchar": "",
            "delim": "",
            "delim_string": "",
            "time_scale": 0,
            "quote": "",
            "alphabet": "",
        }

        for key, value in default_overrides_for_unset_apt_properties.items():
            if dumped[key] is None:
                dumped[key] = value

        # dealing with dominance of vector prefix over prefix
        if self.vector_prefix is not None:
            dumped["prefix"] = FieldModelComplex._get_enum_value(self.vector_prefix)
        elif self.prefix_bytes is not None:
            dumped["prefix"] = FieldModelComplex._get_enum_value(self.prefix_bytes)
        else:
            dumped["prefix"] = 0

        dumped["cycle"] = self.get_cycle()

        return dumped

    def get_aptfieldproperties(self):
        if self.apt_field_properties is not None:
            return self.apt_field_properties
        string_props: set[str] = {
            "c_format",
            "default",
            "out_format",
            "padchar",
            "reference",
            "date_format",
            "decimal_separator",
            "timestamp_format",
            "delim_string",
            "delim",
            "null_field",
        }
        integer_props: set[str] = {
            "start_position",
            "tagcase",
            "default",
            "max_width",
            "width",
            "prefix_bytes",
            "vector_prefix",
            "days_since",
            "generated_percent_invalid",
            "epoch",
            "generated_percent_zeros",
            "precision",
            "time_scale_factor",
            "byte_to_skip",
            "actual_length",
            "null_length",
            "nullseed",
            "nulls",
        }
        # not sure if default could ever be a boolean
        boolean_props: set[str] = {
            "generate",
            "link_keep",
            "export_ebcdic_as_ascii",
            "julian",
            "check_decimal_packed",
            "midnight_seconds",
        }
        # Some enums may be included in strings if they are represented internally that way
        enum_props: set[str] = {
            "byte_order",
            "charset",
            "data_format",
            "sign_position",
            "allow_all_zeros",
            "decimal_packed",
        }
        all_props: set[str] = string_props | integer_props | boolean_props | enum_props
        prop_dict: dict = json.loads(self.model_dump_json(include=all_props, by_alias=True))
        fields: list[str] = []
        integer_prop_aliases = {
            "position",
            "prefix",
            "invalids",
            "zeros",
            "_scale",
            "skip",
        }
        boolean_prop_aliases = {"generate", "check"}
        enum_prop_aliases = {}
        for key, value in prop_dict.items():
            if key == "padchar" and value == "null":
                fields += [f"{key}={value}"]
            elif key == "round" and value:
                fields += [f"{key}={value}"]
            elif (key in string_props) and isinstance(value, str):
                fields += [f"{key}='{value}'"]
            elif (key in integer_props or key in integer_prop_aliases) and isinstance(value, int):
                fields += [f"{key}={value}"]
            elif (key in boolean_props or key in boolean_prop_aliases) and isinstance(value, bool) and value:
                fields += [f"{key}"]
            elif (key in enum_props or key in enum_prop_aliases) and value is not None:
                fields += [f"{value}"]

        cycle_val = self.get_cycle()
        if cycle_val:
            fields += [f"cycle={cycle_val}"]

        if self.generate_type == FIELD.GenerateType.random:
            fields += [f"random={self.get_random()}"]
        elif self.generate_algorithm == FIELD.GenerateAlgorithm.alphabet:
            fields += [f"alphabet={self.alphabet}"]

        if self.use_current_date:
            fields += ["function=rundate"]

        if self.rounding:
            fields += [f"round={self.rounding.value}"]

        if self.increment_scale is not None:
            fields += [f"scale={self.increment_scale}"]

        if self.decimal_packed_signed:
            fields += ["signed"]

        if self.quote is not None:
            fields += [f"quote={self.quote.value}"]

        return ",".join(fields)

    def get_misfieldproperties(self):
        fields: list[str] = []
        if self.occurs is not None:
            fields += [f"dimension_min_size={self.occurs}"]
        elif self.dimension_min_size is not None:
            fields += [f"dimension_min_size={self.dimension_min_size}"]
        if self.level_no is not None:
            fields += [f"LevelNumber={self.level_no}"]
        return "|".join(fields)

    @classmethod
    def from_data_definition_column_dict(cls, _dict: dict) -> "FieldModelComplex":
        """Initialize a DataDefinitionColumn object from a json dictionary."""
        args = {}
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        else:
            raise ValueError("Required property 'name' not present in DataDefinitionColumn JSON")
        if (type := _dict.get("type").get("type")) is not None:
            args["odbc_type"] = type
        else:
            raise ValueError("Required property 'type' not present in DataDefinitionColumn JSON")
        if (length := _dict.get("type").get("length")) is not None:
            args["length"] = length
        else:
            args["length"] = None
        if (scale := _dict.get("type").get("scale")) is not None:
            args["scale"] = scale
        else:
            args["scale"] = None
        if (nullable := _dict.get("type").get("nullable")) is not None:
            args["nullable"] = nullable
        else:
            args["nullable"] = None
        if (signed := _dict.get("type").get("signed")) is not None:
            args["signed"] = signed
        else:
            args["signed"] = None
        properties_keys = {
            "APTFieldProperties",
            "Maps from input column",
            # "MisFieldProperties",
            "alphabet",
            "charset",
            "cycle",
            "data_element",
            "default",
            "delim",
            "delim_string",
            "description",
            "display_size",
            "ds_data_type",
            "ds_scd_purpose",
            "ds_sync_indicator",
            "export_ebcdic_as_ascii",
            "extended",
            "extended_precision",
            "field_pos",
            "generate",
            "key_position",
            "link_keep",
            "max_width",
            "occurs_varying",
            "pad_char",
            "padchar",
            "position",
            "prefix",
            "primary_key",
            "quote",
            "sign_option",
            "skip",
            "sqltype",
            "tagcase",
            "tagged_subrec",
            "time_scale",
            "width",
        }

        optional_properties_keys = {"occurs"}

        enum_mappings = {
            "extended": FIELD.Unicode,
            "delim": FIELD.Delim,
            "quote": FIELD.Quote,
            "charset": FIELD.CharSet,
            "padchar": FIELD.PadChar,
        }

        inverse_alias_map = {
            "extended": "unicode",
            "level_no": "level_no",
            "Maps from input column": "Maps_from_input_column",
            "skip": "byte_to_skip",
            "generate": "generate",
        }
        # TODO: deal with prefix vs vector_prefix here, dominance, etc.

        properties_dict = _dict.get("properties")

        enums_with_invalid_empty_str_defaults = {
            "quote",
            "charset",
            "padchar",
            "delim",
            "delim_string",
        }
        for key in enums_with_invalid_empty_str_defaults:
            if properties_dict.get(key) == "":
                properties_dict[key] = None
                args[key] = None
                properties_keys.remove(key)

        apt_field_props_str = properties_dict.get("APTFieldProperties")
        if apt_field_props_str and "vector_prefix" in apt_field_props_str and properties_dict.get("prefix") != 0:
            args["vector_prefix"] = FIELD.VectorPrefix(properties_dict.get("prefix"))
        elif properties_dict.get("prefix", 0) != 0:
            args["prefix_bytes"] = FIELD.Prefix(properties_dict.get("prefix"))
        properties_keys.remove("prefix")
        args["prefix_bytes"] = args.get("prefix_bytes", None)

        if apt_field_props_str and ("vector_prefix" in apt_field_props_str or "reference" in apt_field_props_str):
            args["dimension_min_size"] = "0"

        args["vector_prefix"] = args.get("vector_prefix", None)

        for key in properties_keys:
            if (key_value := properties_dict.get(key)) is not None:
                args[inverse_alias_map.get(key, key)] = FieldModelComplex._get_value_from_json_value(
                    key_value, enum_mappings.get(key, None)
                )
            else:
                args[inverse_alias_map.get(key, key)] = None

        for key in optional_properties_keys:
            if (key_value := properties_dict.get(key)) is not None:
                args[inverse_alias_map.get(key, key)] = FieldModelComplex._get_value_from_json_value(
                    key_value, enum_mappings.get(key, None)
                )

        # parse misfieldproperties
        misfield_props = properties_dict.get("MisFieldProperties")
        if misfield_props:
            dim_min_size_search = re.search(r"dimension_min_size=(\d+)", misfield_props)
        else:
            dim_min_size_search = None
        if dim_min_size_search is not None:
            dim_min_size_value = int(dim_min_size_search.group(1))
            # if vector length is variable, then dim_min_size is set to 0 when vector occurs propogates
            if dim_min_size_value == 0 and properties_dict.get("occurs") != 0:
                args["vector_length_type"] = FIELD.VectorType.variable
                args["occurs"] = None
                args["dimension_min_size"] = "0"
            else:
                args["occurs"] = dim_min_size_value
        elif properties_dict.get("occurs", 0) != 0:
            args["occurs"] = properties_dict.get("occurs")
        else:
            args["occurs"] = None
        args["dimension_min_size"] = args.get("dimension_min_size", args["occurs"])

        args["vector_length_type"] = args.get("vector_length_type", None)

        if misfield_props:
            level_number_search = re.search(r"LevelNumber=(\d+)", misfield_props)
        else:
            level_number_search = None
        if level_number_search is not None:
            args["level_no"] = int(level_number_search.group(1))
        else:
            args["level_no"] = None

        odbc_type: str = args["odbc_type"]

        odbc_type_to_type = {
            "BIGINT": "integer",
            "BINARY": "binary",
            "BIT": "boolean",
            "CHAR": "string",
            "DATE": "date",
            "DECIMAL": "double",
            "DOUBLE": "double",
            "FLOAT": "double",
            "INTEGER": "integer",
            "WLONGVARCHAR": "string",
            "LONGNVARCHAR": "string",
            "LONGVARBINARY": "binary",
            "LONGVARCHAR": "string",
            "WCHAR": "string",
            "NCHAR": "string",
            "NUMERIC": "double",
            "WVARCHAR": "string",
            "NVARCHAR": "string",
            "REAL": "double",
            "SMALLINT": "integer",
            "TIME": "time",
            "TIMESTAMP": "timestamp",
            "TINYINT": "integer",
            "UNKNOWN": "string",
            "VARBINARY": "binary",
            "VARCHAR": "string",
        }
        args["type"] = odbc_type_to_type[odbc_type]

        odbc_type_to_type_code = {
            "BIGINT": "INT64",
            "BINARY": "BINARY",
            "BIT": "BOOLEAN",
            "CHAR": "STRING",
            "DATE": "DATE",
            "DECIMAL": "DECIMAL",
            "DOUBLE": "DFLOAT",
            "FLOAT": "SFLOAT",
            "INTEGER": "INT32",
            "WLONGVARCHAR": "STRING",
            "LONGNVARCHAR": "STRING",
            "LONGVARBINARY": "BINARY",
            "LONGVARCHAR": "STRING",
            "WCHAR": "STRING",
            "NCHAR": "STRING",
            "NUMERIC": "DECIMAL",
            "WVARCHAR": "STRING",
            "NVARCHAR": "STRING",
            "REAL": "SFLOAT",
            "SMALLINT": "INT16",
            "TIME": "TIME",
            "TIMESTAMP": "DATETIME",
            "TINYINT": "INT8",
            "UNKNOWN": "UNKNOWN",
            "VARBINARY": "BINARY",
            "VARCHAR": "STRING",
        }

        args["type_code"] = odbc_type_to_type_code[odbc_type]

        imported_metadata = Metadata(
            is_key=False,
            item_index=0,
            is_signed=True,
            description="",
            min_length=0,
            decimal_precision=100,
            decimal_scale=0,
        )
        # defaults: (min_length, max_length, decimal_precision, decimal_scale)
        odbc_type_to_metadata_updates = {
            "BIGINT": (0, 6),
            "BINARY": (100, 100, 0),
            "BIT": (6, 6),
            "CHAR": (100, 100, 0),
            "DATE": (0, 10),
            "DECIMAL": (0, 100),
            "DOUBLE": (0, 6),
            "FLOAT": (0, 6),
            "INTEGER": (0, 6),
            "WLONGVARCHAR": (0, 100),
            "LONGNVARCHAR": (0, 100),
            "LONGVARBINARY": (0, 100),
            "LONGVARCHAR": (0, 100),
            "WCHAR": (100, 100),
            "NCHAR": (100, 100),
            "NUMERIC": (0, 100),
            "WVARCHAR": (0, 100),
            "NVARCHAR": (0, 100),
            "REAL": (0, 100),
            "SMALLINT": (0, 6),
            "TIME": (0, 8, 8, 0),
            "TIMESTAMP": (0, 19, 19, 0),
            "TINYINT": (0, 6),
            "UNKNOWN": (0, 100),
            "VARBINARY": (0, 100),
            "VARCHAR": (0, 100),
        }

        metadata_updates = odbc_type_to_metadata_updates[odbc_type]

        imported_metadata.min_length = metadata_updates[0]
        imported_metadata.max_length = metadata_updates[1]
        if len(metadata_updates) > 2:
            imported_metadata.decimal_precision = metadata_updates[2]
        if len(metadata_updates) > 3:
            imported_metadata.decimal_scale = metadata_updates[3]

        args["metadata"] = imported_metadata
        args["app_data"] = {"time_scale": args.get("time_scale", 0)}

        if "extended_type" in properties_dict and properties_dict["extended_type"] != " ":
            args["extended_type"] = FieldModelComplex._get_value_from_json_value(
                properties_dict["extended_type"], FIELD.TimeExtendedType
            )
        args["extended_type"] = args.get("extended_type", None)

        return FieldModelComplex(
            name=args["name"],
            metadata=args["metadata"],
            app_data=args["app_data"],
            type=args["type"],
            type_code=args["type_code"],
            odbc_type=args["odbc_type"],
            length=args["length"],
            scale=args["scale"],
            nullable=args["nullable"],
            signed=args["signed"],
            pad_char=args["pad_char"],
            primary_key=args["primary_key"],
            max_width=args["max_width"],
            tagged_subrec=args["tagged_subrec"],
            width=args["width"],
            Maps_from_input_column=args["Maps_from_input_column"],
            quote=args["quote"],
            tagcase=args["tagcase"],
            alphabet=args["alphabet"],
            delim_string=args["delim_string"],
            cycle=args["cycle"],
            byte_to_skip=args["byte_to_skip"],
            generate=args["generate"],
            ds_sync_indicator=args["ds_sync_indicator"],
            ds_scd_purpose=args["ds_scd_purpose"],
            vector_prefix=args["vector_prefix"],
            prefix_bytes=args["prefix_bytes"],
            display_size=args["display_size"],
            padchar=args["padchar"],
            data_element=args["data_element"],
            field_pos=args["field_pos"],
            description=args["description"],
            position=args["position"],
            sign_option=args["sign_option"],
            default=args["default"],
            sqltype=args["sqltype"],
            occurs_varying=args["occurs_varying"],
            time_scale=args["time_scale"],
            charset=args["charset"],
            unicode=args["unicode"],
            delim=args["delim"],
            key_position=args["key_position"],
            ds_data_type=args["ds_data_type"],
            apt_field_properties=args["APTFieldProperties"],
            extended_precision=args["extended_precision"],
            link_keep=args["link_keep"],
            export_ebcdic_as_ascii=args["export_ebcdic_as_ascii"],
            occurs=args["occurs"],
            level_no=args["level_no"],
            vector_length_type=args["vector_length_type"],
            dimension_min_size=args["dimension_min_size"],
            extended_type=args["extended_type"],
        )

    def _get_value_from_json_value(internal_value: str | int, enum_type: Enum | None):
        if enum_type is None:
            return internal_value
        return enum_type(internal_value)

    def _get_enum_value(possible_enum: Enum | int | str):
        if isinstance(possible_enum, Enum):
            return possible_enum.value
        else:
            return possible_enum

    def validate_properties(self) -> None:
        prop_to_incompatible_props: dict[str, set] = {
            "date_format": {"days_since", "julian", "data_format"},
            "reference": {"delim_string", "delim", "quote", "prefix_bytes"},
            "prefix_bytes": {"delim_string", "delim", "quote", "reference"},
            "days_since": {"data_format", "julian", "date_format"},
            "julian": {"days_since", "data_format", "date_format"},
            "data_format": {"days_since", "julian", "date_format"},
            "delim": {"delim_string", "prefix_bytes"},
            "delim_string": {"delim", "prefix_bytes"},
            "quote": {"prefix_bytes"},
            "actual_length": {"null_field"},
            "null_length": {"null_field"},
            "null_field": {"actual_length", "null_length"},
        }
        for prop, incompatible_props in prop_to_incompatible_props.items():
            self.validate_prop_with_incompatibilities(prop, incompatible_props)

        sub_properties_to_valid_super_props: dict[str, list[tuple[str, Any]]] = {
            # subproperty: [(superproperty name, valid superproperty value), ...]
            "reference": [("vector_length_type", FIELD.VectorType.variable)],
            "vector_prefix": [("vector_length_type", FIELD.VectorType.variable)],
            "check_decimal_packed": [("decimal_packed", FIELD.DecimalPacked.packed)],
            "decimal_packed_signed": [
                ("decimal_packed", FIELD.DecimalPacked.packed),
                ("decimal_packed", FIELD.DecimalPacked.zoned),
            ],
            "sign_position": [
                ("decimal_packed", FIELD.DecimalPacked.overpunch),
                ("decimal_packed", FIELD.DecimalPacked.separate),
                ("decimal_packed", FIELD.DecimalPacked.zoned),
            ],
            "occurs": [("vector_length_type", FIELD.VectorType.vector_occurs)],
            "cycle_increment": [("generate_type", FIELD.GenerateType.cycle)],
            "cycle_initial_value": [("generate_type", FIELD.GenerateType.cycle)],
            "cycle_limit": [("generate_type", FIELD.GenerateType.cycle)],
            "cycle_values": [("generate_algorithm", FIELD.GenerateAlgorithm.cycle)],
            "alphabet": [("generate_algorithm", FIELD.GenerateAlgorithm.alphabet)],
            "actual_length": [("nullable", True)],
            "null_length": [("nullable", True)],
            "null_field": [("nullable", True)],
            "nullseed": [("nullable", True)],
            "nulls": [("nullable", True)],
        }

        for sub_prop, valid_super_props in sub_properties_to_valid_super_props.items():
            self.validate_subproperty(sub_prop, valid_super_props)

    def validate_prop_with_incompatibilities(self, prop: str, incompatible_props: set[str]):
        dumped = self.model_dump(include=(incompatible_props | {prop}))
        if dumped[prop] is not None:
            for incompat_prop in incompatible_props:
                if dumped[incompat_prop] is not None:
                    print(
                        f"Property '{prop}' set on field '{self.name}', despite incompatible property '{incompat_prop}' also being set."
                    )

    def validate_subproperty(self, sub_prop: str, valid_super_props: list[tuple[str, Any]]):
        super_prop_names = set([super_prop[0] for super_prop in valid_super_props])
        dumped = self.model_dump(include=(super_prop_names | {sub_prop}))
        if dumped[sub_prop] is None:
            return
        for super_prop_name, super_prop_valid_value in valid_super_props:
            if dumped[super_prop_name] == super_prop_valid_value:
                return
        print(
            f"Subproperty '{sub_prop}' set without required/compatible superproperties being set on field '{self.name}'. Possible superproperties that could be set for subproperty include: {super_prop_names}."
        )


class Comment(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: str
    x_pos: float
    y_pos: float
    width: Annotated[float, Field(ge=10.0)]
    height: Annotated[float, Field(ge=10.0)]
    class_name: str | None = None
    style: str | dict[str, Any] | None = None
    attributes: str | None = None
    content: str | None = None
    content_type: str | None = Field(None, alias="contentType")
    associated_id_refs: list[CommentLink] | None = None


class ImageDecoration(DecorationSharedProperties):
    image: str | None = None
    outline: bool | None = None


class LabelDecoration(DecorationSharedProperties):
    label: str | None = None
    label_editable: bool | None = None
    label_align: LabelAlign | None = None
    label_single_line: bool | None = None
    label_max_characters: int | None = None
    label_allow_return_key: bool | None = None


class ShapeDecoration(DecorationSharedProperties):
    path: str | None = None


class JsxDecoration(DecorationSharedProperties):
    jsx: dict[str, Any] | None = None


class StructTypes(BaseModel):
    fields: list[FieldModel] | None = None


class RecordSchema(BaseModel):
    id: str
    name: str | None = None
    json_schema: JsonSchema1 | None = None
    type: str | None = None
    fields: list[FieldModel | FieldModelComplex]
    struct_types: dict[Annotated[str, Field(pattern=r".")], StructTypes] | None = None


class PipelineUI(BaseModel):
    model_config = ConfigDict(extra="allow")

    description: str | None = None
    zoom: ZoomObjectDef | None = None
    comments: list[Comment] | None = None


class NodeDecoration1(ImageDecoration):
    position: Position | None = None


class NodeDecoration2(LabelDecoration):
    position: Position | None = None


class NodeDecoration3(ShapeDecoration):
    position: Position | None = None


class NodeDecoration4(JsxDecoration):
    position: Position | None = None


class NodeDecoration(RootModel[Union[NodeDecoration1, NodeDecoration2, NodeDecoration3, NodeDecoration4]]):
    pass


class LinkDecoration1(ImageDecoration):
    position: Position2 | None = None
    distance: int | None = None


class LinkDecoration2(LabelDecoration):
    position: Position2 | None = None
    distance: int | None = None


class LinkDecoration3(ShapeDecoration):
    position: Position2 | None = None
    distance: int | None = None


class LinkDecoration4(JsxDecoration):
    position: Position2 | None = None
    distance: int | None = None


class LinkDecoration(RootModel[Union[LinkDecoration1, LinkDecoration2, LinkDecoration3, LinkDecoration4]]):
    pass


class PipelineAppData(BaseModel):
    model_config = ConfigDict(extra="allow")

    ui_data: PipelineUI | None = None


class Decoration(RootModel[Union[NodeDecoration, LinkDecoration]]):
    pass


class NodeLinkUI(BaseModel):
    model_config = ConfigDict(extra="allow")

    description: str | None = None
    class_name: str | None = None
    style: str | dict[str, Any] | None = None
    decorations: list[Decoration] | None = None


class LinkAppData(BaseModel):
    model_config = ConfigDict(extra="allow")

    ui_data: NodeLinkUI | None = None


class NodeLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    node_id_ref: str
    port_id_ref: str | None = None
    link_name: str | None = None
    type_attr: str | None = None
    description: str | None = None
    app_data: LinkAppData | None = None


class AssociationLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    node_ref: str
    class_name: str | None = None
    style: str | dict[str, Any] | None = None
    decorations: list[Decoration] | None = None


class Port(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    schema_ref: str | None = None
    links: list[NodeLink] | None = None
    parameters: dict[str, Any] | None = None
    app_data: PortAppData | None = None


class BoundPort(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(...)
    schema_ref: str | None = None
    links: list[NodeLink] | None = None
    subflow_node_ref: str | None = None
    parameters: dict[str, Any] | None = None
    app_data: PortAppData | None = None


class NodeUI(BaseModel):
    model_config = ConfigDict(extra="allow")

    label: str | None = None
    description: str | None = None
    class_name: str | None = None
    style: str | dict[str, Any] | None = None
    image: str | dict[str, Any] | None = None
    x_pos: float | None = None
    y_pos: float | None = None
    is_expanded: bool | None = None
    expanded_height: float | None = None
    expanded_width: float | None = None
    is_resized: bool | None = None
    resize_height: float | None = None
    resize_width: float | None = None
    sub_pipelines: list | None = None
    attributes: str | None = None
    associations: list[AssociationLink] | None = None
    messages: list[Message] | None = None
    ui_parameters: dict[str, Any] | None = None
    palette_image: str | None = None
    palette_class_name: str | None = None
    palette_disabled: bool | None = None
    decorations: list[Decoration] | None = None


class NodeAppData(BaseModel):
    model_config = ConfigDict(extra="allow")

    ui_data: NodeUI | None = None


def get_node_discriminator(v: Any):
    if isinstance(v, dict):
        node_type = v.get("type")
        has_inputs = bool(v.get("inputs"))
    else:
        node_type = getattr(v, "type")
        has_inputs = hasattr(v, "inputs")

    if node_type == "binding":
        return "binding_exit_node" if has_inputs else "binding_entry_node"
    else:
        return node_type


class Node(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    id: str
    description: str | None = None
    app_data: NodeAppData | None = None


class ExecutionNode(Node):
    type: Literal["execution_node"] = "execution_node"
    op: str
    inputs: list[Port] | None = None
    outputs: list[Port] | None = None
    parameters: dict[str, Any] | None = None
    runtime_ref: str | None = None


class BindingEntryNode(Node):
    type: Literal["binding"] = "binding"
    outputs: list[Port]
    connection: CommonPipelineConnection | None = None
    data_asset: CommonPipelineDataAsset | None = None
    op: str | None = None
    parameters: dict[str, Any] | None = None


class BindingExitNode(Node):
    type: Literal["binding"] = "binding"
    inputs: list[Port]
    outputs: list[Port] | None = None
    connection: CommonPipelineConnection | None = None
    data_asset: CommonPipelineDataAsset | None = None
    op: str | None = None
    parameters: dict[str, Any] | None = None


class ModelNode(Node):
    type: Literal["model_node"] = "model_node"
    model_ref: str | None = None
    inputs: list[Port]
    outputs: list[Port] | None = None
    op: str | None = None
    parameters: dict[str, Any] | None = None
    runtime_ref: str | None = None


class Supernode(Node):
    type: Literal["super_node"] = "super_node"
    open_with_tool: str | None = None
    subflow_ref: SubflowRef
    inputs: list[BoundPort] | None = None
    outputs: list[BoundPort] | None = None
    parameters: dict[str, Any] | None = None


class Pipeline(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    description: str | None = None
    name: str | None = None
    runtime_ref: str
    nodes: list[
        Annotated[
            Annotated[Supernode, Tag("super_node")]
            | Annotated[BindingEntryNode, Tag("binding_entry_node")]
            | Annotated[BindingExitNode, Tag("binding_exit_node")]
            | Annotated[ModelNode, Tag("model_node")]
            | Annotated[ExecutionNode, Tag("execution_node")],
            Discriminator(get_node_discriminator),
        ]
    ]
    parameters: dict[str, Any] | None = None
    app_data: PipelineAppData | None = None


class Flow(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    doc_type: str | None = "pipeline"
    version: Version = Version.v3
    json_schema: JsonSchema | None = JsonSchema.https
    open_with_tool: str | None = None
    id: str | None = None
    parameters: dict[str, Any] | None = None
    primary_pipeline: str
    pipelines: list[Pipeline]
    schemas: list[RecordSchema] | None = None
    runtimes: list[Runtime] | None = None
    external_paramsets: list[ParamSet] | None = None
    app_data: AppData | None = None
    name: str | None = None
