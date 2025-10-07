from ibm_watsonx_data_integration.services.datastage.models import flow_json_model as models
from ibm_watsonx_data_integration.services.datastage.models.enums import FIELD
from ibm_watsonx_data_integration.services.datastage.models.schema.field.base_field import BaseField
from typing import TypeVar
T = TypeVar("T", bound="Time")

class Time(BaseField):
    def __init__(self, name: str):
        super().__init__(name)
        self._set_model_type("time")
        self._set_app_type_code("TIME")
        self._set_app_odbc_type("TIME")
        self.configuration.metadata.decimal_scale = 0
        self.configuration.metadata.decimal_precision = 8
        self.configuration.metadata.min_length = 0
        self.configuration.metadata.max_length = 8

    def _create_from_model(self, model: models.FieldModelComplex)-> T:
        field = Time(model.name)
        field.configuration = model
        return field

    def length(self, length: int):
        """Set the length of this field.

        Args:
            length: The length to set for this field.

        Returns:
            A new instance of the field with the updated length.

        """
        return self._length(length)._max_length(length)._decimal_precision(length)

    def scale(self, scale: int):
        return self._time_scale(scale)

    def timezone(self):
        if self.configuration.extended_type == FIELD.TimeExtendedType.microseconds:
            return self.extended_type(FIELD.TimeExtendedType.microseconds_and_timezone)
        else:
            return self.extended_type(self.extended_type(FIELD.TimeExtendedType.timezone))

    def microseconds(self):
        if self.configuration.extended_type == FIELD.TimeExtendedType.timezone:
            return self.extended_type(FIELD.TimeExtendedType.microseconds_and_timezone)
        else:
            return self.extended_type(self.extended_type(FIELD.TimeExtendedType.microseconds))

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

    def charset(self, charset: FIELD.CharSet):
        return self._charset(charset)

    def data_format(self, data_format: FIELD.DataFormat):
        return self._data_format(data_format)

    def default(self, default: str):
        return self._default(default)

    def format_string(self, format_string: str):
        return self._date_format(format_string)

    def is_midnight_seconds(self):
        return self._midnight_seconds()

    def percent_invalid(self, generated_percent_invalid: int):
        return self._generated_percent_invalid(generated_percent_invalid)

    def scale_factor(self, time_scale_factor: int):
        return self._time_scale_factor(time_scale_factor)

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

    def extended_type(self, typ: FIELD.TimeExtendedType):
        return self._extended_type(typ)

    def link_field_reference(self, link_field_reference):
        return self._link_field_reference(link_field_reference)

    def null_seed(self, seed: int):
        return self._null_seed(seed)

    def percent_null(self, percent_null: int):
        return self._percent_null(percent_null)
