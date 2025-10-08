import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as model
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer
from typing import Any, Literal


class NativeType(Enum):
    Binary = "BINARY"
    NativeBinary = "NATIVE_BINARY"
    Decimal = "DECIMAL"
    DisplayNumeric = "DISPLAY_NUMERIC"
    Float = "FLOAT"
    Character = "CHARACTER"
    VarChar = "VARCHAR"
    Group = "GROUP"
    GraphicN = "GRAPHIC_N"
    GraphicG = "GRAPHIC_G"
    VarGraphicN = "VARGRAPHIC_N"
    VarGraphicG = "VARGRAPHIC_G"


class Usage(Enum):
    none = ""
    COMP = "COMP"
    COMP_1 = "COMP-1"
    COMP_2 = "COMP-2"
    COMP_3 = "COMP-3"
    COMP_5 = "COMP-5"
    DISPLAY = "DISPLAY"
    DISPLAY_1 = "DISPLAY-1"


class Extended(Enum):
    Unsigned = "unsigned"
    Unicode = "unicode"


class SignOption(Enum):
    none = 0
    Leading = "1"
    Trailing = "2"
    LeadingSeparate = "3"
    TrailingSeparate = "4"


class ArrayHandling(Enum):
    ArrayHandling = 0
    ArrayHandlingAsIs = 1
    ArrayHandlingDenormalize = 2


class Column(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(None, alias="name")
    native_type: NativeType = Field(NativeType.Character, alias="native_type")
    length: int = Field(None, alias="max_length")
    min_length: int = Field(0, alias="min_length")
    scale: int = Field(None, alias="decimal_scale")
    level: int = Field(2, alias="item_index")
    is_unicode_string: bool = Field(False, alias="is_unicode_string")
    is_signed: bool = Field(False, alias="is_signed")
    usage: Usage = Field(Usage.none, alias="usage")
    description: str = Field(None, alias="description")
    nullable: bool = Field(False, alias="nullable")
    sign_option: SignOption = Field(SignOption.none, alias="sign_option")
    sync_indicator: bool = Field(False, alias="sync_indicator")
    has_sign_indicator: bool = Field(True, alias="has_sign_indicator")
    default: Any = Field(None, alias="default")
    print_fields: bool = Field(False, alias="print_field")
    field_max_width: int = Field(None, alias="max_width")
    field_width: int = Field(None, alias="width")
    prefix_bytes: Literal[0, 1, 2, 4] = Field(None, alias="prefix")
    occurs: int = Field(None, alias="dimension_max_size")
    redefined_field: str = Field(None, alias="redefined_field")
    depending_on: str = Field(None, alias="depend_field")
    # make this a literal?
    date_format: str = Field(None, alias="date_mask")
    mf_update_value: str = Field(None, alias="mf_update_value")
    array_handling: ArrayHandling = Field(ArrayHandling.ArrayHandling, alias="array_handling")

    @field_serializer("length")
    def serialize_length(self, length: int | None) -> int:
        if length:
            return length
        native_type = self.native_type.value if isinstance(self.native_type, Enum) else self.native_type
        if native_type in ["BINARY"]:
            return 18
        elif native_type in ["NATIVE_BINARY", "DECIMAL", "DISPLAY_NUMERIC", "FLOAT"]:
            return 31
        else:
            return 100

    @field_serializer("usage")
    def serialize_usage(self, usage: Usage | None) -> Usage | str:
        if usage:
            return usage
        native_type = self.native_type.value if isinstance(self.native_type, Enum) else self.native_type
        if native_type == "BINARY":
            return Usage.COMP
        elif native_type == "NATIVE_BINARY":
            return Usage.COMP_5
        elif native_type == "DECIMAL":
            return Usage.COMP_3
        elif native_type == "FLOAT":
            return Usage.COMP_2
        elif native_type in ["GRAPHIC_G", "VARGRAPHIC_G"]:
            return Usage.DISPLAY_1
        elif native_type in ["GRAPHIC_N", "VARGRAPHIC_N"]:
            return ""
        else:
            return Usage.DISPLAY

    @field_serializer("occurs")
    def serialize_occurs(self, occurs: int) -> str:
        return str(occurs)

    @computed_field
    @property
    def decimal_precision(self) -> int:
        native_type = self.native_type.value if isinstance(self.native_type, Enum) else self.native_type
        if native_type in ["NATIVE_BINARY", "DECIMAL", "DISPLAY_NUMERIC", "FLOAT"]:
            return self.length
        return 0

    @computed_field
    @property
    def dimension_min_size(self) -> str | None:
        if self.occurs:
            return str(self.occurs)
        return None

    # apt field properties persists throughout all columns in the record
    @computed_field
    @property
    def apt_field_properties(self) -> str:
        apt_string = []
        if self.prefix_bytes:
            apt_string.append(f"prefix={self.prefix_bytes}")
        if self.default:
            apt_string.append(f"default={self.default}")
        if self.field_max_width:
            apt_string.append(f"max_width={self.field_max_width}")
        if self.field_width:
            apt_string.append(f"width={self.field_width}")
        if self.print_fields:
            apt_string.append("print_field")
        return ", ".join(apt_string)

    @computed_field
    @property
    def odbc_type(self) -> str:
        native_type = self.native_type.value if isinstance(self.native_type, Enum) else self.native_type
        native_to_odbc = {
            "BINARY": "INTEGER",
            "NATIVE_BINARY": "DECIMAL",
            "DECIMAL": "DECIMAL",
            "DISPLAY_NUMERIC": "DECIMAL",
            "FLOAT": "DECIMAL",
            "VARCHAR": "VARCHAR",
            "GROUP": "CHAR",
            "GRAPHIC_N": "WCHAR",
            "GRAPHIC_G": "WCHAR",
            "VARGRAPHIC_N": "WVARCHAR",
            "VARGRAPHIC_G": "WVARCHAR",
        }
        if native_type in native_to_odbc:
            return native_to_odbc[native_type]
        if native_type == "CHARACTER":
            if self.date_format:
                return "DATE"
            else:
                return "CHAR"
        # raise error?
        return "CHAR"

    @computed_field
    @property
    def type_code(self) -> str:
        native_type = self.native_type.value if isinstance(self.native_type, Enum) else self.native_type
        native_to_type_code = {
            "BINARY": "INT32",
            "NATIVE_BINARY": "DECIMAL",
            "DECIMAL": "DECIMAL",
            "DISPLAY_NUMERIC": "DECIMAL",
            "FLOAT": "DECIMAL",
            "VARCHAR": "STRING",
            "GROUP": "STRING",
            "GRAPHIC_N": "STRING",
            "GRAPHIC_G": "STRING",
            "VARGRAPHIC_N": "STRING",
            "VARGRAPHIC_G": "STRING",
        }
        if native_type in native_to_type_code:
            return native_to_type_code[native_type]
        if native_type == "CHARACTER":
            if self.date_format:
                return "DATE"
            else:
                return "STRING"
        return "STRING"

    @computed_field
    @property
    def type(self) -> str:
        native_type = self.native_type.value if isinstance(self.native_type, Enum) else self.native_type
        native_to_type = {
            "BINARY": "integer",
            "NATIVE_BINARY": "double",
            "DECIMAL": "double",
            "DISPLAY_NUMERIC": "double",
            "FLOAT": "double",
            "VARCHAR": "string",
            "GROUP": "string",
            "GRAPHIC_N": "string",
            "GRAPHIC_G": "string",
            "VARGRAPHIC_N": "string",
            "VARGRAPHIC_G": "string",
        }
        if native_type in native_to_type:
            return native_to_type[native_type]
        if native_type == "CHARACTER":
            if self.date_format:
                return "date"
            else:
                return "string"
        return "string"

    def _to_field(self) -> model.FieldModel:
        metadata_props = {
            "length",
            "min_length",
            "decimal_precision",
            "scale",
            "is_signed",
            "level",
            "description",
        }
        app_data_props = {
            "usage",
            "sign_option",
            "sync_indicator",
            "is_unicode_string",
            "odbc_type",
            "type_code",
            "native_type",
            "has_sign_indicator",
            # "mf_update_value",
            "occurs",
            "dimension_min_size",
            "depending_on",
            "redefined_field",
            "date_format",
            "apt_field_properties",
        }

        return model.FieldModel(
            name=self.name,
            type=self.type,
            nullable=self.nullable,
            metadata=self.model_dump(include=metadata_props, exclude_none=True, by_alias=True),
            app_data=self.model_dump(include=app_data_props, exclude_none=True, by_alias=True),
        )

    def _to_output_field(self) -> model.FieldModel:
        metadata_props = {
            "length",
            "min_length",
            "decimal_precision",
            "scale",
            "is_signed",
            "level",
            "description",
        }
        app_data_props = {
            "usage",
            "sign_option",
            "sync_indicator",
            "is_unicode_string",
            "odbc_type",
            "type_code",
            "native_type",
            "has_sign_indicator",
            "occurs",
            "dimension_min_size",
            "depending_on",
            "redefined_field",
            "date_format",
        }

        return model.FieldModel(
            name=self.name,
            type=self.type,
            nullable=self.nullable,
            metadata=self.model_dump(include=metadata_props, exclude_none=True, by_alias=True),
            app_data=self.model_dump(include=app_data_props, exclude_none=True, by_alias=True),
        )

    @classmethod
    def from_dict(cls, dict: dict):
        if "apt_field_properties" in dict:
            apt_props = dict["apt_field_properties"].split(", ")
            for prop in apt_props:
                if "=" in prop:
                    key_val = prop.split("=")
                    assert len(key_val) == 2
                    key, val = key_val[0].strip(), key_val[1].strip()
                    dict[key] = val
                    if key in ["prefix", "max_width", "width"]:
                        dict[key] = int(val)
                    else:
                        dict[key] = val
                elif "print_field" in prop:
                    dict["print_field"] = True
        return cls(**dict)


class Record(BaseModel):
    name: str = Field(None, alias="name")
    columns: list[Column] = Field([], alias="columns")


class RecordID(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    record_name: str = Field(None, alias="record_name")
    column_name: str = Field(None, alias="record_id_name")
    operator: str = Field("=", alias="record_id_name_value_relation")
    value: str = Field(None, alias="record_id_value")
    schema_ref: str = Field(None, alias="schema_ref")

    @computed_field
    @property
    def name(self) -> str:
        return self.record_name


class OutputColumns(BaseModel):
    output_name: str = Field(None, alias="output_name")
    output_columns: list = Field([], alias="output_columns")


class Constraint(BaseModel):
    output_name: str = Field(None, alias="output_name")
    constraint: str = Field([], alias="constraint")


class complex_flat_file:
    Column = Column
    Record = Record
    RecordID = RecordID
    OutputColumns = OutputColumns
    Constraint = Constraint
    NativeType = NativeType
    Usage = Usage
    Extended = Extended
    SignOption = SignOption
    ArrayHandling = ArrayHandling
