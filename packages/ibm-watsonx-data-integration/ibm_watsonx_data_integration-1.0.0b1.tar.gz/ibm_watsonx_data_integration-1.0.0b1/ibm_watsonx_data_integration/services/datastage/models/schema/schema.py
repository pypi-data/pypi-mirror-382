import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as models
import ibm_watsonx_data_integration.services.datastage.models.schema.field as field
import json
from ibm_watsonx_data_integration.services.datastage.models.schema.data_definition import DataDefinition
from ibm_watsonx_data_integration.services.datastage.models.schema.field.base_field import BaseField
from typing import Literal, overload

_ODBC_TYPE_TO_FIELD_CLASS = {
    "BIGINT": field.BigInt,
    "BINARY": field.Binary,
    "BIT": field.Bit,
    "CHAR": field.Char,
    "DATE": field.Date,
    "DECIMAL": field.Decimal,
    "DOUBLE": field.Double,
    "FLOAT": field.Float,
    "INTEGER": field.Integer,
    "LONGVARBINARY": field.LongVarBinary,
    "LONGVARCHAR": field.LongVarChar,
    "NUMERIC": field.Numeric,
    "REAL": field.Real,
    "SMALLINT": field.SmallInt,
    "TIME": field.Time,
    "TIMESTAMP": field.Timestamp,
    "TINYINT": field.TinyInt,
    "UNKNOWN": field.Unknown,
    "VARBINARY": field.VarBinary,
    "VARCHAR": field.VarChar,
    "NCHAR": field.NChar,
    "LONGNVARCHAR": field.LongNVarChar,
    "NVARCHAR": field.NVarChar,
}


class Schema:
    def __init__(self, fields: list[BaseField] = None):
        self.fields = fields or []

    @property
    def configuration(self) -> models.RecordSchema:
        return models.RecordSchema(id="", fields=[f.configuration.get_field_model() for f in self.fields])

    @overload
    def add_field(self, odbc_type: Literal["BIGINT"], name: str) -> field.BigInt: ...

    @overload
    def add_field(self, odbc_type: Literal["BINARY"], name: str) -> field.Binary: ...

    @overload
    def add_field(self, odbc_type: Literal["BIT"], name: str) -> field.Bit: ...

    @overload
    def add_field(self, odbc_type: Literal["CHAR"], name: str) -> field.Char: ...

    @overload
    def add_field(self, odbc_type: Literal["DATE"], name: str) -> field.Date: ...

    @overload
    def add_field(self, odbc_type: Literal["DECIMAL"], name: str) -> field.Decimal: ...

    @overload
    def add_field(self, odbc_type: Literal["DOUBLE"], name: str) -> field.Double: ...

    @overload
    def add_field(self, odbc_type: Literal["FLOAT"], name: str) -> field.Float: ...

    @overload
    def add_field(self, odbc_type: Literal["INTEGER"], name: str) -> field.Integer: ...

    @overload
    def add_field(self, odbc_type: Literal["LONGVARBINARY"], name: str) -> field.LongVarBinary: ...

    @overload
    def add_field(self, odbc_type: Literal["LONGVARCHAR"], name: str) -> field.LongVarChar: ...

    @overload
    def add_field(self, odbc_type: Literal["NUMERIC"], name: str) -> field.Numeric: ...

    @overload
    def add_field(self, odbc_type: Literal["REAL"], name: str) -> field.Real: ...

    @overload
    def add_field(self, odbc_type: Literal["SMALLINT"], name: str) -> field.SmallInt: ...

    @overload
    def add_field(self, odbc_type: Literal["TIME"], name: str) -> field.Time: ...

    @overload
    def add_field(self, odbc_type: Literal["TIMESTAMP"], name: str) -> field.Timestamp: ...

    @overload
    def add_field(self, odbc_type: Literal["TINYINT"], name: str) -> field.TinyInt: ...

    @overload
    def add_field(self, odbc_type: Literal["UNKNOWN"], name: str) -> field.Unknown: ...

    @overload
    def add_field(self, odbc_type: Literal["VARBINARY"], name: str) -> field.VarBinary: ...

    @overload
    def add_field(self, odbc_type: Literal["VARCHAR"], name: str) -> field.VarChar: ...

    @overload
    def add_field(self, odbc_type: Literal["NCHAR"], name: str) -> field.NChar: ...

    @overload
    def add_field(self, odbc_type: Literal["LONGNVARCHAR"], name: str) -> field.LongNVarChar: ...

    @overload
    def add_field(self, odbc_type: Literal["NVARCHAR"], name: str) -> field.NVarChar: ...

    def add_field(self, odbc_type: str, name: str):
        if odbc_type.upper() in _ODBC_TYPE_TO_FIELD_CLASS:
            field_class = _ODBC_TYPE_TO_FIELD_CLASS[odbc_type.upper()]
            new_field = field_class(name=name)
            self.fields.append(new_field)
            return new_field
        else:
            raise ValueError(
                f"Unsupported field type: {odbc_type}. Supported types are: {list(_ODBC_TYPE_TO_FIELD_CLASS.keys())}"
            )

    def remove_field(self, name: str):
        new_fields = []
        for cur_field in self.fields:
            if cur_field.configuration.name != name:
                new_fields.append(cur_field)
        self.fields = new_fields
        return self

    def select_fields(self, *args: str):
        new_fields = []
        for cur_field in self.fields:
            if cur_field.configuration.name in args:
                new_fields.append(cur_field)
        return Schema(new_fields)

    def clone(self):
        new_fields = [f.clone() for f in self.fields]
        return Schema(new_fields)

    def __str__(self):
        new_fields = [str(f) for f in self.fields]
        new_fields = "[" + ",\n".join(map(str, new_fields)) + "]"
        return json.dumps(json.loads(new_fields), indent=4)

    def add_data_definition(self, data_definition: DataDefinition):
        self.fields.extend(data_definition._get_fields())
        return self
