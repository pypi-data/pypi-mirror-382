import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as models
import json
from abc import ABC, abstractmethod
from ibm_watsonx_data_integration.services.datastage.models.enums import FIELD
from typing import TypeVar
T = TypeVar("T", bound="BaseField")

class BaseField(ABC):
    def __init__(self, name: str, configuration: models.FieldModelComplex = None):
        if configuration:
            self.configuration = configuration
            self.configuration.name = name
        else:
            default_meta = models.Metadata(
                is_key=False,
                item_index=0,
                is_signed=True,
                description="",
                min_length=0,
                decimal_precision=100,
                decimal_scale=0,
            )
            self.configuration = models.FieldModelComplex(
                name=name,
                type="string",
                odbc_type="CHAR",
                metadata=default_meta,
                nullable=False,
                app_data={"time_scale": 0},
            )

    def __str__(self):
        dictionary = {}
        dictionary["name"] = self.configuration.name
        dictionary["type"] = self.configuration.type
        if self.configuration.metadata:
            dictionary["metadata"] = json.loads(str(self.configuration.metadata))
        dictionary["nullable"] = self.configuration.nullable
        dictionary["app_data"] = self.configuration.app_data

        return json.dumps(dictionary, indent=4)

    @abstractmethod
    def _create_from_model(self, model: models.FieldModelComplex)-> T: ...

    def clone(self):
        model = self.configuration.model_copy(deep=True)
        return self._create_from_model(model)

    def _set_model_type(self, typ: str):
        self.configuration.type = typ
        return self

    def _set_app_type_code(self, typ_code: str):
        self.configuration.app_data["type_code"] = typ_code
        return self

    def _set_app_odbc_type(self, odbc_typ: str):
        self.configuration.app_data["odbc_type"] = odbc_typ
        self.configuration.odbc_type = odbc_typ

    def name(self, name: str)-> T:
        self.configuration.name = name
        return self

    def nullable(self, is_nullable: bool = True):
        self.configuration.nullable = is_nullable
        return self

    def key(self, is_key: bool = True):
        self.configuration.metadata.is_key = is_key
        self.configuration.primary_key = True
        return self

    def source(self, name: str):
        self.configuration.metadata.source_field_id = name
        return self

    def description(self, description: str):
        self.configuration.metadata.description = description
        self.configuration.description = description
        return self

    def pivot(self, pivot_property: str = None):
        self.configuration.app_data["pivot_property"] = pivot_property
        return self

    def _min_length(self, length: int):
        self.configuration.metadata.min_length = length
        return self

    def _max_length(self, length: int):
        self.configuration.metadata.max_length = length
        return self

    def _length(self, length: int):
        self.configuration.length = length
        return self

    def _decimal_precision(self, precision: int):
        self.configuration.metadata.decimal_precision = precision
        return self

    def _decimal_scale(self, scale: int):
        self.configuration.metadata.decimal_scale = scale
        self.configuration.scale = scale
        return self

    def _unicode(self, is_unicode: bool = True):
        self.configuration.app_data["is_unicode_string"] = is_unicode
        self.configuration.unicode = FIELD.Unicode.true if is_unicode else FIELD.Unicode.false
        return self

    def _unsigned(self):
        self.configuration.metadata.is_signed = False
        self.configuration.signed = False
        return self

    def _extended_type(self, typ: str):
        self.configuration.app_data["extended_type"] = typ
        self.configuration.extended_type = typ
        self._decimal_scale(6)  # default changes to 6, not sure why
        return self

    def _cluster_key_change(self):
        self.configuration.app_data["cluster_key_change"] = True
        return self

    def _key_change(self):
        self.configuration.app_data["key_change"] = True
        return self

    def difference(self):
        self.configuration.app_data["difference"] = True
        return self

    def _dimension_min_size(self, size: int)-> T:
        self.configuration.app_data["dimension_min_size"] = size
        self.configuration.dimension_min_size = size
        return self

    def _dimension_max_size(self, size: int)-> T:
        self.configuration.app_data["dimension_max_size"] = size
        # FYI: dimension_max_size is not a model property, while dimension_min_size is
        return self

    def _time_scale(self, time_scale: int)-> T:
        self.configuration.app_data["time_scale"] = time_scale
        self.configuration.time_scale = time_scale
        return self

    def _c_format(self, c_format: str)-> T:
        self.configuration.c_format = c_format
        return self

    def _default(self, default: str | int)-> T:
        self.configuration.default = default
        return self

    def _date_format(self, date_format: str)-> T:
        self.configuration.date_format = date_format
        return self

    def _decimal_separator(self, decimal_separator: FIELD.DecimalSeparator)-> T:
        self.configuration.decimal_separator = decimal_separator
        return self

    def _timestamp_format(self, timestamp_format: str)-> T:
        self.configuration.timestamp_format = timestamp_format
        return self

    def _out_format(self, out_format: str)-> T:
        self.configuration.out_format = out_format
        return self

    def _link_field_reference(self, link_field_reference: str)-> T:
        self.configuration.reference = link_field_reference
        return self

    def _padchar(self, padchar: FIELD.PadChar)-> T:
        self.configuration.padchar = padchar
        return self

    def _prefix_bytes(self, prefix_bytes: FIELD.Prefix)-> T:
        self.configuration.prefix_bytes = prefix_bytes
        return self

    def vector_prefix(self, vector_prefix: FIELD.VectorPrefix)-> T:
        self.configuration.vector_prefix = vector_prefix
        return self

    def _epoch(self, epoch: int)-> T:
        self.configuration.epoch = epoch
        return self

    def _max_width(self, max_width: int)-> T:
        self.configuration.max_width = max_width
        return self

    def _precision(self, precision: int)-> T:
        self.configuration.precision = precision
        return self

    def _time_scale_factor(self, time_scale_factor: int)-> T:
        self.configuration.time_scale_factor = time_scale_factor
        return self

    def _start_position(self, start_position: int)-> T:
        self.configuration.start_position = start_position
        return self

    def _generated_percent_invalid(self, generated_percent_invalid: int)-> T:
        self.configuration.generated_percent_invalid = generated_percent_invalid
        return self

    def _generated_percent_zeros(self, generated_percent_zeros: int)-> T:
        self.configuration.generated_percent_zeros = generated_percent_zeros
        return self

    def _tagcase(self, tagcase: int)-> T:
        self.configuration.tagcase = tagcase
        return self

    def _days_since(self, days_since: int)-> T:
        self.configuration.days_since = days_since
        return self

    def _width(self, width: int)-> T:
        self.configuration.width = width
        return self

    def _generate_on_output(self)-> T:
        self.configuration.generate = True
        return self

    def _julian(self)-> T:
        self.configuration.julian = True
        return self

    def _link_keep(self)-> T:
        self.configuration.link_keep = True
        return self

    def _check_decimal_packed(self)-> T:
        self.configuration.check_decimal_packed = True
        return self

    def _export_ebcdic_as_ascii(self)-> T:
        self.configuration.export_ebcdic_as_ascii = True
        return self

    def _decimal_packed_signed(self)-> T:
        self.configuration.decimal_packed_signed = True
        return self

    def _midnight_seconds(self)-> T:
        self.configuration.midnight_seconds = True
        return self

    def _decimal_packed(self, packed_option: FIELD.DecimalPacked)-> T:
        self.configuration.decimal_packed = packed_option
        return self

    def _byte_order(self, byte_order: FIELD.ByteOrder)-> T:
        self.configuration.byte_order = byte_order
        return self

    def _charset(self, charset: FIELD.CharSet)-> T:
        self.configuration.charset = charset
        return self

    def _allow_all_zeros(self)-> T:
        self.configuration.allow_all_zeros = FIELD.AllowAllZeros.fix_zero
        return self

    def _sign_position(self, sign_position: FIELD.SignPosition)-> T:
        self.configuration.sign_position = sign_position
        return self

    def _data_format(self, data_format: FIELD.DataFormat)-> T:
        self.configuration.data_format = data_format
        return self

    def level_number(self, level_number: int)-> T:
        self.configuration.level_no = level_number
        self.configuration.metadata.item_index = level_number
        return self

    def vector(self, vector_length_type: FIELD.VectorType):
        instance_to_update = self
        if vector_length_type == FIELD.VectorType.variable:
            instance_to_update = self._dimension_min_size(0)
        instance_to_update.configuration.vector_length_type = vector_length_type
        return self

    def vector_occurs(self, vector_occurs: int)-> T:
        self.configuration.occurs = vector_occurs
        self._dimension_min_size(vector_occurs)
        self._dimension_max_size(vector_occurs)
        return self

    def _byte_to_skip(self, byte_to_skip: int)-> T:
        self.configuration.byte_to_skip = byte_to_skip
        return self

    def _delim(self, delim: FIELD.Delim)-> T:
        self.configuration.delim = delim
        return self

    def _delim_string(self, delim_string: str)-> T:
        self.configuration.delim_string = delim_string
        return self

    def _quote(self, quote: FIELD.Quote)-> T:
        self.configuration.quote = quote
        return self

    def _cycle_increment(self, cycle_increment: FIELD.CycleIncrement | int)-> T:
        self.configuration.cycle_increment = cycle_increment
        return self

    def _cycle_initial_value(self, cycle_initial_value: FIELD.CycleInitialValue | int)-> T:
        self.configuration.cycle_initial_value = cycle_initial_value
        return self

    def _cycle_limit(self, cycle_limit: FIELD.CycleLimit | int)-> T:
        self.configuration.cycle_limit = cycle_limit
        return self

    def _cycle_values(self, cycle_values: list[int | str])-> T:
        self.configuration.cycle_values = cycle_values
        return self

    def _alphabet(self, alphabet: str)-> T:
        self.configuration.alphabet = alphabet
        return self

    def _generate_algorithm(self, generate_algorithm: FIELD.GenerateAlgorithm)-> T:
        self.configuration.generate_algorithm = generate_algorithm
        return self

    def _generate_type(self, generate_type: FIELD.GenerateType)-> T:
        self.configuration.generate_type = generate_type
        return self

    def _random_limit(self, random_limit: FIELD.RandomLimit)-> T:
        self.configuration.random_limit = random_limit
        return self

    def _random_seed(self, random_seed: FIELD.RandomSeed)-> T:
        self.configuration.random_seed = random_seed
        return self

    def _random_signed(self)-> T:
        self.configuration.random_signed = True
        return self

    def _use_current_date(self)-> T:
        self.configuration.use_current_date = True
        return self

    def _round(self, rounding: FIELD.Round)-> T:
        self.configuration.rounding = rounding
        return self

    def _increment_scale(self, increment_scale: int)-> T:
        self.configuration.increment_scale = increment_scale
        return self

    def actual_field_length(self, length: int):
        self.configuration.actual_length = length
        return self

    def null_field_length(self, length: int):
        self.configuration.null_length = length
        return self

    def null_field_value(self, value: str):
        self.configuration.null_field = value
        return self

    # It is possible this option is not meant to be settable and the canvas option is a bug
    def _decimal_type_scale(self, scale: int):
        self.configuration.increment_scale = scale
        return self

    def _null_seed(self, seed: int):
        self.configuration.nullseed = seed
        return self

    def _percent_null(self, percent_null: int):
        self.configuration.nulls = percent_null
        return self

    def change_code(self):
        self.configuration.app_data["change_code"] = True
        return self

    def derivation(self, derivation: str):
        self.configuration.app_data["derivation"] = derivation
        return self
