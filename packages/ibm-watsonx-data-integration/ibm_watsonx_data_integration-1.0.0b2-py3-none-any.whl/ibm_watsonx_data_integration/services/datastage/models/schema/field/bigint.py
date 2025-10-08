import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as models
from ibm_watsonx_data_integration.services.datastage.models.enums import FIELD
from ibm_watsonx_data_integration.services.datastage.models.schema.field.base_field import BaseField
from typing import TypeVar
T = TypeVar("T", bound="BigInt")

class BigInt(BaseField):
    def __init__(self, name: str):
        super().__init__(name)
        self._set_model_type("integer")
        self._set_app_type_code("INT64")
        self._set_app_odbc_type("BIGINT")
        self.configuration.metadata.min_length = 0
        self.configuration.metadata.max_length = 6

    def _create_from_model(self, model: models.FieldModelComplex)-> T:
        field = BigInt(model.name)
        field.configuration = model
        return field

    def unsigned(self):
        return self._unsigned()

    def byte_to_skip(self, num_bytes: int):
        return self._byte_to_skip(num_bytes)

    def delimiter(self, delim: FIELD.Delim):
        return self._delim(delim)

    def delimiter_string(self, delimiter_string: str):
        return self._delim_string(delimiter_string)

    def generate_on_output(self):
        return self._generate_on_output()

    def prefix_bytes(self, prefix_bytes: FIELD.Prefix):
        return self._prefix_bytes(prefix_bytes)

    def quote(self, quote_type: FIELD.Quote):
        return self._quote(quote_type)

    def start_position(self, position: int):
        return self._start_position(position)

    def tag_case_value(self, tag_case_value: int):
        return self._tagcase(tag_case_value)

    def byte_order(self, byte_order: FIELD.ByteOrder):
        return self._byte_order(byte_order)

    def c_format(self, c_format: str):
        return self._c_format(c_format)

    def charset(self, charset: FIELD.CharSet):
        return self._charset(charset)

    def data_format(self, data_format: FIELD.DataFormat):
        return self._data_format(data_format)

    def default(self, default: int):
        return self._default(default)

    def field_max_width(self, max_width: int):
        return self._max_width(max_width)

    def field_width(self, width: int):
        return self._width(width)

    def is_link_field(self):
        return self._link_keep()

    def out_format(self, out_format: str):
        return self._out_format(out_format)

    def padchar(self, padchar: FIELD.PadChar):
        return self._padchar(padchar)

    def generate_type(self, generate_type: FIELD.GenerateType):
        return self._generate_type(generate_type)

    def cycle_increment(self, cycle_increment: FIELD.CycleIncrement | int):
        return self._cycle_increment(cycle_increment)

    def cycle_initial_value(self, cycle_initial_value: FIELD.CycleInitialValue | int):
        return self._cycle_initial_value(cycle_initial_value)

    def cycle_limit(self, cycle_limit: FIELD.CycleLimit | int):
        return self._cycle_limit(cycle_limit)

    def random_limit(self, random_limit: FIELD.RandomLimit):
        return self._random_limit(random_limit)

    def random_seed(self, random_seed: FIELD.RandomSeed):
        return self._random_seed(random_seed)

    def random_signed(self):
        return self._random_signed()

    def null_seed(self, seed: int):
        return self._null_seed(seed)

    def percent_null(self, percent_null: int):
        return self._percent_null(percent_null)
