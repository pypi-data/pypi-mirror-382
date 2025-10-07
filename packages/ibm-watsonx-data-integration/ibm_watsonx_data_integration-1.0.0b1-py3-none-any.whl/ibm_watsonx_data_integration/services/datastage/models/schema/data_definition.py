import ibm_watsonx_data_integration.services.datastage.models.schema.field as SchemaField
import json
from ibm_watsonx_data_integration.services.datastage.models.enums import FIELD
from ibm_watsonx_data_integration.services.datastage.models.flow_json_model import FieldModelComplex
from ibm_watsonx_data_integration.services.datastage.models.schema import field
from ibm_watsonx_data_integration.services.datastage.models.schema.field.base_field import BaseField
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from typing import Literal, Optional, overload

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


class DataDefinitionMetadata(BaseModel):
    """System metadata about a table definition.

    :param str name: table definition name.
    :param str description: table definition description.
    """

    name: str = Field()
    description: str = Field("")

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataDefinitionMetadata":
        """Initialize a DataDefinitionMetadata object from a json dictionary."""
        args = {}
        if (name := _dict.get("name")) is not None:
            args["name"] = name
        else:
            raise ValueError("Required property 'name' not present in DataDefinitionMetadata JSON")
        if (description := _dict.get("description")) is not None:
            args["description"] = description
        else:
            args["description"] = ""
        return cls(**args)


class DataDefinitionDataAsset(BaseModel):
    """column definitions and table properties.

    :param str mime_type: (optional)
    :param bool dataset: (optional)
    :param list[FieldModel] columns:
    :param object additional_properties: table properties.
    """

    columns: list[FieldModelComplex] = Field([])
    additional_properties: dict = Field({})
    mime_type: str | None = Field(None)
    dataset: bool | None = Field(None)

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataDefinitionDataAsset":
        """Initialize a datadefinitiondataasset object from a json dictionary."""
        args = {}
        if (mime_type := _dict.get("mime_type")) is not None:
            args["mime_type"] = mime_type
        if (dataset := _dict.get("dataset")) is not None:
            args["dataset"] = dataset
        if (columns := _dict.get("columns")) is not None:
            args["columns"] = [FieldModelComplex.from_data_definition_column_dict(v) for v in columns]
        else:
            raise ValueError("Required property 'columns' not present in DataDefinitionDataAsset JSON")
        if (additional_properties := _dict.get("additionalProperties")) is not None:
            args["additional_properties"] = additional_properties
        else:
            raise ValueError("Required property 'additionalProperties' not present in DataDefinitionDataAsset JSON")
        return cls(**args)


class DataDefinitionTypeDefaults(BaseModel):
    """default properties for data types.

    :param dict general: (optional)
    :param dict string: (optional)
    :param dict decimal: (optional)
    :param dict numeric: (optional)
    :param dict date: (optional)
    :param dict time: (optional)
    :param dict timestamp: (optional)
    """

    general: dict | None = (None,)
    string: dict | None = (None,)
    decimal: dict | None = (None,)
    numeric: dict | None = (None,)
    date: dict | None = (None,)
    time: dict | None = (None,)
    timestamp: dict | None = (None,)

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataDefinitionTypeDefaults":
        """Initialize a DataDefinitionTypeDefaults object from a json dictionary."""
        args = {}
        if (general := _dict.get("general")) is not None:
            args["general"] = general
        if (string := _dict.get("string")) is not None:
            args["string"] = string
        if (decimal := _dict.get("decimal")) is not None:
            args["decimal"] = decimal
        if (numeric := _dict.get("numeric")) is not None:
            args["numeric"] = numeric
        if (date := _dict.get("date")) is not None:
            args["date"] = date
        if (time := _dict.get("time")) is not None:
            args["time"] = time
        if (timestamp := _dict.get("timestamp")) is not None:
            args["timestamp"] = timestamp
        return cls(**args)


class DataDefinitionDSInfo(BaseModel):
    """data type defaults and format properties.

    :param List[object] data_types: (optional) definitions for custom data type.
    :param dict record_level: (optional)
    :param dict field_defaults: (optional)
    :param DataDefinitionTypeDefaults type_defaults: (optional) default properties
          for data types.
    """

    data_types: list[object] | None = (None,)
    record_level: dict | None = (None,)
    field_defaults: dict | None = (None,)
    type_defaults: Optional["DataDefinitionTypeDefaults"] = (None,)

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataDefinitionDSInfo":
        """Initialize a DataDefinitionDSInfo object from a json dictionary."""
        args = {}
        if (data_types := _dict.get("data_types")) is not None:
            args["data_types"] = data_types
        if (record_level := _dict.get("record_level")) is not None:
            args["record_level"] = record_level
        if (field_defaults := _dict.get("field_defaults")) is not None:
            args["field_defaults"] = field_defaults
        if (type_defaults := _dict.get("type_defaults")) is not None:
            args["type_defaults"] = DataDefinitionTypeDefaults.from_dict(type_defaults)
        return cls(**args)


class DirectoryAsset(BaseModel):
    """DirectoryAsset.

    :param str path: (optional) The directory asset id.
    """

    path: str | None = None

    @classmethod
    def from_dict(cls, _dict: dict) -> "DirectoryAsset":
        """Initialize a DirectoryAsset object from a json dictionary."""
        args = {}
        if (path := _dict.get("path")) is not None:
            args["path"] = path
        return cls(**args)


class DataDefinitionEntity(BaseModel):
    """The underlying table definition.

    :param DataDefinitionDataAsset data_asset: column definitions and table
          properties.
    :param dict column_info:
    :param dict data_definition:
    :param DataDefinitionDSInfo ds_info: data type defaults and format properties.
    :param DirectoryAsset directory_asset: (optional)
    """

    data_asset: "DataDefinitionDataAsset"
    column_info: dict
    data_definition: dict
    ds_info: "DataDefinitionDSInfo"
    directory_asset: Optional["DirectoryAsset"] = None

    @classmethod
    def from_dict(cls, _dict: dict) -> "DataDefinitionEntity":
        """Initialize a DataDefinitionEntity object from a json dictionary."""
        args = {}
        if (data_asset := _dict.get("data_asset")) is not None:
            args["data_asset"] = DataDefinitionDataAsset.from_dict(data_asset)
        else:
            raise ValueError("Required property 'data_asset' not present in DataDefinitionEntity JSON")
        if (column_info := _dict.get("column_info")) is not None:
            args["column_info"] = column_info
        else:
            raise ValueError("Required property 'column_info' not present in DataDefinitionEntity JSON")
        if (data_definition := _dict.get("data_definition")) is not None:
            args["data_definition"] = data_definition
        else:
            raise ValueError("Required property 'data_definition' not present in DataDefinitionEntity JSON")
        if (ds_info := _dict.get("ds_info")) is not None:
            args["ds_info"] = DataDefinitionDSInfo.from_dict(ds_info)
        else:
            raise ValueError("Required property 'ds_info' not present in DataDefinitionEntity JSON")
        if (directory_asset := _dict.get("directory_asset")) is not None:
            args["directory_asset"] = DirectoryAsset.from_dict(directory_asset)
        return cls(**args)


ODBC_TO_CLASS = {
    "BIGINT": SchemaField.BigInt,
    "BINARY": SchemaField.Binary,
    "BIT": SchemaField.Bit,
    "CHAR": SchemaField.Char,
    "DATE": SchemaField.Date,
    "DECIMAL": SchemaField.Decimal,
    "DOUBLE": SchemaField.Double,
    "FLOAT": SchemaField.Float,
    "INTEGER": SchemaField.Integer,
    "LONGVARBINARY": SchemaField.LongVarBinary,
    "LONGVARCHAR": SchemaField.LongVarChar,
    "LONGNVARCHAR": SchemaField.LongVarChar,
    "NUMERIC": SchemaField.Numeric,
    "REAL": SchemaField.Real,
    "SMALLINT": SchemaField.SmallInt,
    "TIME": SchemaField.Time,
    "TIMESTAMP": SchemaField.Timestamp,
    "TINYINT": SchemaField.TinyInt,
    "UNKNOWN": SchemaField.Unknown,
    "VARBINARY": SchemaField.VarBinary,
    "VARCHAR": SchemaField.VarChar,
    "NCHAR": SchemaField.NChar,
    "NVARCHAR": SchemaField.VarChar,
    "WCHAR": SchemaField.NChar,
    "WLONGVARCHAR": SchemaField.LongNVarChar,
    "WVARCHAR": SchemaField.NVarChar,
}


class DataDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True, serialize_by_alias=True)
    asset_id: str | None = None
    proj_id: str | None = None
    name: str
    description: str = ""
    additional_properties: dict = Field({}, alias="additionalProperties")
    mime_type: str = "application/json"
    dataset: bool = True
    column_info: dict = {}
    data_definition: dict = {}
    data_types: list = []

    # Record level extended properties
    record_level_fill_char: FIELD.Fill | None = Field(None, alias="fill")
    record_level_final_delimiter: FIELD.FinalDelim | str | None = Field(None, alias="final_delim")
    record_level_final_delimiter_string: str | None = Field(None, alias="final_delim_string")
    record_level_intact: str | None = Field(None, alias="intact")
    record_level_check_intact: bool | None = Field(None, alias="check_intact")
    record_level_record_delimiter: FIELD.RecordDelim | None = Field(None, alias="record_delim")
    record_level_record_delimiter_string: str | None = Field(None, alias="record_delim_string")
    record_level_record_length: FIELD.RecordLength | None = Field(None, alias="record_length")
    record_level_record_prefix: FIELD.RecordPrefix | None = Field(None, alias="record_prefix")
    record_level_record_type: FIELD.RecordType | None = Field(None, alias="type")
    record_level_record_format: FIELD.Format | None = Field(None, alias="format")

    # Field defaults extended properties
    field_defaults_actual_field_length: int | None = Field(None, alias="actual_length")
    field_defaults_delimiter: FIELD.FieldDelim | str | None = Field(None, alias="delim")
    field_defaults_delimiter_string: str | None = Field(None, alias="delim_string")
    field_defaults_null_field_length: int | None = Field(None, alias="null_length")
    field_defaults_null_field_value: str | None = Field(None, alias="null_field")
    field_defaults_null_field_value_separator: FIELD.ValueSeparator | None = Field(None, alias="value_separator")
    field_defaults_prefix_bytes: FIELD.Prefix | None = Field(None, alias="prefix")
    field_defaults_print_field: bool | None = Field(False, alias="print_field")
    field_defaults_quote: FIELD.Quote | None = Field(None, alias="quote")
    field_defaults_vector_prefix: FIELD.VectorPrefix | None = Field(None, alias="vector_prefix")

    # Type defaults extended properties
    ## General
    general_byte_order: FIELD.ByteOrder | None = Field(None, alias="byte_order")
    general_char_set: FIELD.CharSet | None = Field(
        None, alias="char_set"
    )  # internal values may need to be uppercased during serialization
    general_data_format: FIELD.DataFormat | None = Field(None, alias="data_format")
    general_max_width: int | None = Field(None, alias="max_width")
    general_pad_char: FIELD.PadChar | int | None = Field(
        None, alias="pad_char"
    )  # TODO: This padchar has the wrong internal values, figure out how to resolve
    general_width: int | None = Field(None, alias="width")

    ## String
    string_export_ebcdic_as_ascii: bool | None = Field(None, alias="export_ebcdic_as_ascii")
    string_import_ascii_as_ebcdic: bool | None = Field(None, alias="import_ascii_as_ebcdic")

    ## Decimal
    decimal_allow_all_zeros: bool | None = Field(None, alias="allow_all_zeros")
    decimal_separator: FIELD.DecimalSeparator | None = Field(None, alias="decimal_separator")
    decimal_packed: FIELD.DecimalPacked | None = Field(None, alias="packed_value")
    decimal_sign_position: FIELD.SignPosition | None = Field(None, alias="sign_position")
    decimal_packed_signed: bool | None = Field(None, alias="packed_signed")  # TODO: is true by default
    decimal_precision: int | None = Field(None, alias="precision")  # TODO: str(int) when serialized
    decimal_rounding: FIELD.Round | None = Field(None, alias="round")
    decimal_scale: int | None = Field(None, alias="scale")  # TODO: str(int) when serialized

    ## Numeric
    numeric_c_format: str | None = Field(None, alias="c_format")
    numeric_in_format: str | None = Field(None, alias="in_format")
    numeric_out_format: str | None = Field(None, alias="out_format")

    ## Date
    date_days_since: int | None = Field(None, alias="days_since")  # TODO: str(int) when serialized
    date_format_string: str | None = Field(None, alias="format_string")
    date_is_julian: bool | None = Field(None, alias="julian")  # TODO: default as False

    ## Time
    time_format_string: str | None = Field(None, alias="format_string")
    time_midnight_seconds: bool | None = Field(None, alias="midnight_seconds")  # TODO: default as false

    ## Timestamp
    timestamp_format_string: str | None = Field(None, alias="format_string")

    directory_asset_path: str | None = None
    selected_fields: list[str] = []
    columns: list[FieldModelComplex] = []

    def select_fields(self, field_names: list[str]):
        self.selected_fields.extend(field_names)
        return self

    def select_field(self, field_name: str):
        self.selected_fields.append(field_name)
        return self

    def _get_fields(self) -> list[BaseField]:
        return [
            ODBC_TO_CLASS[column.odbc_type](column.name)._create_from_model(model=column)
            for column in self.columns
            if column.name in self.selected_fields
        ]

    def _get_metadata_props(self):
        props = {"name", "description"}
        return self.model_dump(include=props)

    def _get_entity_props(self):
        props = {"column_info", "data_definition"}
        dumped = self.model_dump(include=props)
        dumped["data_asset"] = self._get_data_asset_props()
        dumped["ds_info"] = self._get_ds_info_props()

        return dumped

    def _get_data_asset_props(self):
        props = {"mime_type", "dataset", "additional_properties"}

        dumped = self.model_dump(include=props, by_alias=True)
        dumped["columns"] = self._get_columns()

        return dumped

    def _get_columns(self):
        return [column.serialize_to_data_definition_column() for column in self.columns]

    def _get_ds_info_props(self):
        props = {"data_types"}

        dumped = self.model_dump(include=props)
        dumped["record_level"] = self._get_record_level_props()
        dumped["field_defaults"] = self._get_field_defaults_props()
        dumped["type_defaults"] = self._get_type_defaults_props()

        return dumped

    def _get_record_level_props(self):
        props = {
            "record_level_fill_char",
            "record_level_final_delimiter",
            "record_level_final_delimiter_string",
            "record_level_record_delimiter",
            "record_level_record_delimiter_string",
            "record_level_record_length",
            "record_level_record_prefix",
        }
        dumped: dict = json.loads(self.model_dump_json(include=props, exclude_none=True))
        dumped["intact"] = self._get_intact_props()
        if not dumped["intact"]:
            dumped.pop("intact")
        dumped["record_format"] = self._get_record_format()
        if not dumped["record_format"]:
            dumped.pop("record_format")
        return dumped

    def _get_intact_props(self):
        props = {"record_level_intact", "record_level_check_intact"}
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        return dumped

    def _get_record_format(self):
        props = {"record_level_record_type", "record_level_record_format"}
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        return dumped

    def _get_field_defaults_props(self):
        props = {
            "field_defaults_actual_field_length",
            "field_defaults_delimiter",
            "field_defaults_delimiter_string",
            "field_defaults_null_field_length",
            "field_defaults_prefix_bytes",
            "field_defaults_print_field",
            "field_defaults_quote",
            "field_defaults_vector_prefix",
        }
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        dumped["null_field"] = self._get_null_field_props()
        if not dumped["null_field"]:
            dumped.pop("null_field")
        return dumped

    def _get_null_field_props(self):
        props = {
            "field_defaults_null_field_value",
            "field_defaults_null_field_value_separator",
        }
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        return dumped

    def _get_type_defaults_props(self):
        dumped = {}
        dumped["general"] = self._get_general_props()
        dumped["string"] = self._get_string_props()
        dumped["decimal"] = self._get_decimal_props()
        dumped["numeric"] = self._get_numeric_props()
        dumped["date"] = self._get_date_props()
        dumped["time"] = self._get_time_props()
        dumped["timestamp"] = self._get_timestamp_props()
        return dumped

    def _get_general_props(self):
        props = {
            "general_byte_order",
            "general_char_set",
            "general_data_format",
            "general_max_width",
            "general_pad_char",
            "general_width",
        }
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        return dumped

    def _get_string_props(self):
        props = {"string_export_ebcdic_as_ascii", "string_import_ascii_as_ebcdic"}
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        return dumped

    def _get_decimal_props(self):
        props = {
            "decimal_allow_all_zeros",
            "decimal_separator",
            "decimal_packed",
            "decimal_sign_position",
            "decimal_packed_signed",
            "decimal_precision",
            "decimal_rounding",
            "decimal_scale",
        }
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        return dumped

    def _get_numeric_props(self):
        props = {"numeric_c_format", "numeric_in_format", "numeric_out_format"}
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        return dumped

    def _get_date_props(self):
        props = {"date_days_since", "date_format_string", "date_is_julian"}
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        return dumped

    def _get_time_props(self):
        props = {"time_format_string", "time_midnight_seconds"}
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        return dumped

    def _get_timestamp_props(self):
        props = {"timestamp_format_string"}
        dumped = json.loads(self.model_dump_json(include=props, exclude_none=True))
        return dumped

    def from_dict(properties: dict) -> "DataDefinition":
        metadata = DataDefinitionMetadata.from_dict(properties["metadata"])
        entity = DataDefinitionEntity.from_dict(properties["entity"])
        if entity.directory_asset is None:
            director_asset_path = None
        else:
            director_asset_path = entity.directory_asset.path

        def wrap_in_enum(value, enum_class):
            return enum_class(value) if value is not None else None

        record_level = entity.ds_info.record_level
        if record_level.get("intact"):
            record_level_intact = record_level["intact"].get("intact")
            record_level_check_intact = record_level["intact"].get("check_intact")
        else:
            record_level_intact = None
            record_level_check_intact = None
        if record_level.get("final_delim") == "\\\\t":
            record_level_final_delimiter = r"\\t"
        else:
            record_level_final_delimiter = wrap_in_enum(record_level.get("final_delim"), FIELD.FinalDelim)

        if record_level.get("record_format"):
            record_level_record_format = wrap_in_enum(record_level["record_format"].get("format"), FIELD.Format)
            record_level_record_type = wrap_in_enum(record_level["record_format"].get("type"), FIELD.RecordType)
        else:
            record_level_record_format = None
            record_level_record_type = None

        field_defaults = entity.ds_info.field_defaults

        if field_defaults.get("null_field") and isinstance(field_defaults.get("null_field"), dict):
            field_defaults_null_field_value = field_defaults["null_field"].get("null_field")
            field_defaults_null_field_value_separator = wrap_in_enum(
                field_defaults["null_field"].get("value_separator"),
                FIELD.ValueSeparator,
            )
        elif field_defaults.get("null_field") and isinstance(field_defaults.get("null_field"), str):
            field_defaults_null_field_value = field_defaults.get("null_field")
            field_defaults_null_field_value_separator = None
        else:
            field_defaults_null_field_value = None
            field_defaults_null_field_value_separator = None

        if field_defaults.get("delim") == "\\\\t":
            field_defaults_delimiter = r"\\t"
        else:
            field_defaults_delimiter = wrap_in_enum(field_defaults.get("delim"), FIELD.Delim)

        general = entity.ds_info.type_defaults.general
        string = entity.ds_info.type_defaults.string
        decimal = entity.ds_info.type_defaults.decimal
        numeric = entity.ds_info.type_defaults.numeric
        date = entity.ds_info.type_defaults.date
        time_dict = entity.ds_info.type_defaults.time
        timestamp = entity.ds_info.type_defaults.timestamp

        return DataDefinition(
            name=metadata.name,
            description=metadata.description,
            additional_properties=entity.data_asset.additional_properties,
            mime_type=entity.data_asset.mime_type,
            dataset=entity.data_asset.dataset,
            column_info=entity.column_info,
            data_definition=entity.data_definition,
            data_types=entity.ds_info.data_types,
            record_level_fill_char=wrap_in_enum(record_level.get("fill"), FIELD.Fill),
            record_level_final_delimiter=record_level_final_delimiter,
            record_level_final_delimiter_string=record_level.get("final_delim_string"),
            record_level_intact=record_level_intact,
            record_level_check_intact=record_level_check_intact,
            record_level_record_delimiter=wrap_in_enum(
                (record_level.get("record_delim").replace("\\n", "\n") if record_level.get("record_delim") else None),
                FIELD.RecordDelim,
            ),
            record_level_record_delimiter_string=record_level.get("record_delim_string"),
            record_level_record_length=wrap_in_enum(record_level.get("record_length"), FIELD.RecordLength),
            record_level_record_prefix=wrap_in_enum(record_level.get("record_prefix"), FIELD.RecordPrefix),
            record_level_record_type=record_level_record_type,
            record_level_record_format=record_level_record_format,
            field_defaults_actual_field_length=field_defaults.get("actual_length"),
            field_defaults_delimiter=field_defaults_delimiter,
            field_defaults_delimiter_string=field_defaults.get("delim_string"),
            field_defaults_null_field_length=field_defaults.get("null_length"),
            field_defaults_null_field_value=field_defaults_null_field_value,
            field_defaults_null_field_value_separator=field_defaults_null_field_value_separator,
            field_defaults_prefix_bytes=wrap_in_enum(field_defaults.get("prefix"), FIELD.Prefix),
            field_defaults_print_field=field_defaults.get("print_field"),
            field_defaults_quote=wrap_in_enum(field_defaults.get("quote"), FIELD.Quote),
            field_defaults_vector_prefix=wrap_in_enum(field_defaults.get("vector_prefix"), FIELD.VectorPrefix),
            general_byte_order=wrap_in_enum(general.get("byte_order"), FIELD.ByteOrder),
            general_char_set=wrap_in_enum(general.get("char_set"), FIELD.CharSet),
            general_data_format=wrap_in_enum(general.get("data_format"), FIELD.DataFormat),
            general_max_width=general.get("max_width"),
            general_pad_char=wrap_in_enum(general.get("pad_char"), FIELD.PadChar),
            general_width=general.get("width"),
            string_export_ebcdic_as_ascii=string.get("export_ebcdic_as_ascii"),
            string_import_ascii_as_ebcdic=string.get("import_ascii_as_ebcdic"),
            decimal_allow_all_zeros=decimal.get("allow_all_zeros"),
            decimal_separator=wrap_in_enum(decimal.get("decimal_separator"), FIELD.DecimalSeparator),
            decimal_packed=wrap_in_enum(decimal.get("packed_value"), FIELD.DecimalPacked),
            decimal_sign_position=wrap_in_enum(decimal.get("sign_position"), FIELD.SignPosition),
            decimal_packed_signed=decimal.get("packed_signed"),
            decimal_precision=decimal.get("precision"),
            decimal_rounding=wrap_in_enum(decimal.get("round"), FIELD.Round),
            decimal_scale=decimal.get("scale"),
            numeric_c_format=numeric.get("c_format"),
            numeric_in_format=numeric.get("in_format"),
            numeric_out_format=numeric.get("out_format"),
            date_days_since=date.get("days_since"),
            date_format_string=date.get("format_string"),
            date_is_julian=date.get("julian"),
            time_format_string=time_dict.get("format_string"),
            time_midnight_seconds=time_dict.get("midnight_seconds"),
            timestamp_format_string=timestamp.get("format_string"),
            directory_asset_path=director_asset_path,
            columns=entity.data_asset.columns,
        )

    def set_record_level_check_intact(self, record_level_check_intact: bool):
        self.record_level_check_intact = record_level_check_intact
        return self

    def set_description(self, description: str):
        self.description = description
        return self

    def set_record_level_record_length(self, record_level_record_length: FIELD.RecordLength):
        self.record_level_record_length = record_level_record_length
        return self

    def set_numeric_c_format(self, numeric_c_format: str):
        self.numeric_c_format = numeric_c_format
        return self

    def set_date_is_julian(self, date_is_julian: bool):
        self.date_is_julian = date_is_julian
        return self

    def set_field_defaults_vector_prefix(self, field_defaults_vector_prefix: FIELD.VectorPrefix):
        self.field_defaults_vector_prefix = field_defaults_vector_prefix
        return self

    def set_decimal_sign_position(self, decimal_sign_position: FIELD.SignPosition):
        self.decimal_sign_position = decimal_sign_position
        return self

    def set_decimal_packed(self, decimal_packed: FIELD.DecimalPacked):
        self.decimal_packed = decimal_packed
        return self

    def set_field_defaults_print_field(self, field_defaults_print_field: bool):
        self.field_defaults_print_field = field_defaults_print_field
        return self

    def set_date_days_since(self, date_days_since: int):
        self.date_days_since = date_days_since
        return self

    def set_general_byte_order(self, general_byte_order: FIELD.ByteOrder):
        self.general_byte_order = general_byte_order
        return self

    def set_record_level_record_type(self, record_level_record_type: FIELD.RecordType):
        self.record_level_record_type = record_level_record_type
        return self

    def set_record_level_record_format(self, record_level_record_format: FIELD.Format):
        self.record_level_record_format = record_level_record_format
        return self

    def set_decimal_rounding(self, decimal_rounding: FIELD.Round):
        self.decimal_rounding = decimal_rounding
        return self

    def set_general_data_format(self, general_data_format: FIELD.DataFormat):
        self.general_data_format = general_data_format
        return self

    def set_record_level_final_delimiter_string(self, record_level_final_delimiter_string: str):
        self.record_level_final_delimiter_string = record_level_final_delimiter_string

        return self

    def set_timestamp_format_string(self, timestamp_format_string: str):
        self.timestamp_format_string = timestamp_format_string
        return self

    def set_string_import_ascii_as_ebcdic(self, string_import_ascii_as_ebcdic: bool):
        self.string_import_ascii_as_ebcdic = string_import_ascii_as_ebcdic
        return self

    def set_general_max_width(self, general_max_width: int):
        self.general_max_width = general_max_width
        return self

    def set_general_pad_char(self, general_pad_char: FIELD.PadChar):
        if general_pad_char.name == "space":
            general_pad_char = (
                32  # Handling for incompatiblility between existing PadChar enum value and PadChar value used here
            )
        self.general_pad_char = general_pad_char
        return self

    def set_field_defaults_delimiter(self, field_defaults_delimiter: FIELD.FieldDelim):
        self.field_defaults_delimiter = field_defaults_delimiter
        return self

    def set_field_defaults_prefix_bytes(self, field_defaults_prefix_bytes: FIELD.Prefix):
        self.field_defaults_prefix_bytes = field_defaults_prefix_bytes
        return self

    def set_decimal_scale(self, decimal_scale: int):
        self.decimal_scale = decimal_scale
        return self

    def set_time_midnight_seconds(self, time_midnight_seconds: bool):
        self.time_midnight_seconds = time_midnight_seconds
        return self

    def set_record_level_final_delimiter(self, record_level_final_delimiter: FIELD.FinalDelim):
        self.record_level_final_delimiter = record_level_final_delimiter
        return self

    def set_general_width(self, general_width: int):
        self.general_width = general_width
        return self

    def set_decimal_precision(self, decimal_precision: int):
        self.decimal_precision = decimal_precision
        return self

    def set_field_defaults_null_field_value_separator(
        self,
        field_defaults_null_field_value_separator: FIELD.ValueSeparator,
    ):
        self.field_defaults_null_field_value_separator = field_defaults_null_field_value_separator

        return self

    def set_general_char_set(self, general_char_set: FIELD.CharSet):
        self.general_char_set = general_char_set
        return self

    def set_record_level_record_delimiter_string(self, record_level_record_delimiter_string: str):
        self.record_level_record_delimiter_string = record_level_record_delimiter_string

        return self

    def set_field_defaults_actual_field_length(self, field_defaults_actual_field_length: int):
        self.field_defaults_actual_field_length = field_defaults_actual_field_length

        return self

    def set_numeric_in_format(self, numeric_in_format: str):
        self.numeric_in_format = numeric_in_format
        return self

    def set_numeric_out_format(self, numeric_out_format: str):
        self.numeric_out_format = numeric_out_format
        return self

    def set_string_export_ebcdic_as_ascii(self, string_export_ebcdic_as_ascii: bool):
        self.string_export_ebcdic_as_ascii = string_export_ebcdic_as_ascii
        return self

    def set_field_defaults_null_field_value(self, field_defaults_null_field_value: str):
        self.field_defaults_null_field_value = field_defaults_null_field_value
        return self

    def set_decimal_separator(self, decimal_separator: FIELD.DecimalSeparator):
        self.decimal_separator = decimal_separator
        return self

    def set_record_level_fill_char(self, record_level_fill_char: FIELD.Fill):
        self.record_level_fill_char = record_level_fill_char
        return self

    def set_decimal_allow_all_zeros(self, decimal_allow_all_zeros: bool):
        self.decimal_allow_all_zeros = decimal_allow_all_zeros
        return self

    def set_date_format_string(self, date_format_string: str):
        self.date_format_string = date_format_string
        return self

    def set_decimal_packed_signed(self, decimal_packed_signed: bool):
        self.decimal_packed_signed = decimal_packed_signed
        return self

    def set_field_defaults_delimiter_string(self, field_defaults_delimiter_string: str):
        self.field_defaults_delimiter_string = field_defaults_delimiter_string
        return self

    def set_field_defaults_quote(self, field_defaults_quote: FIELD.Quote):
        self.field_defaults_quote = field_defaults_quote
        return self

    def set_record_level_intact(self, record_level_intact: str):
        self.record_level_intact = record_level_intact
        return self

    def set_record_level_record_delimiter(self, record_level_record_delimiter: FIELD.RecordDelim):
        self.record_level_record_delimiter = record_level_record_delimiter
        return self

    def set_field_defaults_null_field_length(self, field_defaults_null_field_length: int):
        self.field_defaults_null_field_length = field_defaults_null_field_length

        return self

    def set_record_level_record_prefix(self, record_level_record_prefix: FIELD.RecordPrefix):
        self.record_level_record_prefix = record_level_record_prefix
        return self

    def set_time_format_string(self, time_format_string: str):
        self.time_format_string = time_format_string
        return self

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
            self.columns.append(new_field.configuration)
            self.selected_fields.append(new_field.configuration.name)
            return new_field
        else:
            raise ValueError(
                f"Unsupported field type: {odbc_type}. Supported types are: {list(_ODBC_TYPE_TO_FIELD_CLASS.keys())}"
            )
