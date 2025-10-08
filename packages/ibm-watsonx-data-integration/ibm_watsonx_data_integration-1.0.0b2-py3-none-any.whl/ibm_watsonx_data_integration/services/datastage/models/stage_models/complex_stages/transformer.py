from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_serializer


class BeforeAfter(Enum):
    before = "Before-Stage"
    after = "After-Stage"

    @classmethod
    def from_str(cls, value: str) -> "BeforeAfter":
        try:
            return cls[value]
        except KeyError:
            raise ValueError(
                f"Unknown BeforeAfter value: {value}. Valid options are: {', '.join(cls._member_names_)}"
            ) from None


class SqlType(Enum):
    BIGINT = "BIGINT"
    BINARY = "BINARY"
    BIT = "BIT"
    CHAR = "CHAR"
    DATE = "DATE"
    DECIMAL = "DECIMAL"
    DOUBLE = "DOUBLE"
    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    LONGNVARCHAR = "LONGNVARCHAR"
    LONGVARBINARY = "LONGVARBINARY"
    LONGVARCHAR = "LONGVARCHAR"
    NCHAR = "NCHAR"
    NUMERIC = "NUMERIC"
    NVARCHAR = "NVARCHAR"
    REAL = "REAL"
    SMALLINT = "SMALLINT"
    TIME = "TIME"
    TIMESTAMP = "TIMESTAMP"
    TINYINT = "TINYINT"
    UNKNOWN = "UNKNOWN"
    VARBINARY = "VARBINARY"
    VARCHAR = "VARCHAR"

    @classmethod
    def from_str(cls, value: str) -> "SqlType":
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Unknown SQL type: {value}. Valid options are: {', '.join(cls._member_names_)}") from None


class LoopVariable(BaseModel):
    model_config = ConfigDict(validate_by_alias=False, validate_by_name=True, use_enum_values=True)
    name: str = Field(None, alias="Name")
    sql_type: SqlType = Field(None, alias="SqlType")
    derivation: str = Field(None, alias="Derivation")
    length: int = Field(6, alias="Precision")
    scale: int = Field(0, alias="Scale")
    initial_value: str = Field("", alias="InitialValue")
    extended: bool = Field(False, alias="Extended")
    description: str = Field("", alias="Description")

    @field_serializer("length")
    def serialize_length(self, length: int) -> str:
        return str(length)

    @field_serializer("scale")
    def serialize_scale(self, scale: str) -> str:
        return str(scale)

    @field_serializer("extended")
    def serialize_extended(self, extended: bool) -> str:
        return str(extended).lower()


class StageVariable(BaseModel):
    model_config = ConfigDict(validate_by_alias=False, validate_by_name=True, use_enum_values=True)
    name: str = Field(None, alias="Name")
    sql_type: SqlType = Field(None, alias="SqlType")
    derivation: str = Field(None, alias="Derivation")
    length: int = Field(100, alias="Precision")
    scale: int = Field(None, alias="Scale")
    initial_value: str = Field(None, alias="InitialValue")
    extended: bool = Field(False, alias="Extended")
    description: str = Field(None, alias="Description")

    @field_serializer("length")
    def serialize_length(self, length: int) -> str:
        return str(length)

    @field_serializer("scale")
    def serialize_scale(self, scale: str) -> str:
        return str(scale)

    @field_serializer("extended")
    def serialize_extended(self, extended: bool) -> str:
        return str(extended).lower()


class Trigger(BaseModel):
    model_config = ConfigDict(validate_by_alias=False, validate_by_name=True, use_enum_values=True)
    routine_name: str = Field(None, alias="RoutineName")
    before_after: BeforeAfter = Field(BeforeAfter.before, alias="Location")
    arguments: list[str] = Field([], alias="arguments")

    @field_serializer("arguments")
    def serialize_arguments(self, arguments: list[str]) -> dict[str, str]:
        return {f"Argument{i + 1}": arg for i, arg in enumerate(arguments)}


class Constraint(BaseModel):
    model_config = ConfigDict(validate_by_alias=False, validate_by_name=True, use_enum_values=True)
    output_name: str = Field(None, alias="output_name")
    constraint: str = Field(None, alias="TransformerConstraint")
    otherwise_log: bool = Field(False, alias="Reject")
    abort_after_rows: int = Field(0, alias="RowLimit")


class transformer:
    LoopVariable = LoopVariable
    StageVariable = StageVariable
    Trigger = Trigger
    Constraint = Constraint
    SqlType = SqlType
    BeforeAfter = BeforeAfter
