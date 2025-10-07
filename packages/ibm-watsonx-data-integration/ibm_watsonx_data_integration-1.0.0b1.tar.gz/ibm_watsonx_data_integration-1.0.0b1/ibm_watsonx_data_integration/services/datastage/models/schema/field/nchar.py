import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as models
from ibm_watsonx_data_integration.services.datastage.models.enums import FIELD
from ibm_watsonx_data_integration.services.datastage.models.schema.field.base_field import BaseField
from typing import TypeVar
T = TypeVar("T", bound="NChar")

class NChar(BaseField):
    def __init__(self, name: str):
        super().__init__(name)
        self._set_model_type("string")
        self._set_app_type_code("STRING")
        self._set_app_odbc_type("WCHAR")
        self.configuration.metadata.min_length = 100
        self.configuration.metadata.max_length = 100

    def _create_from_model(self, model: models.FieldModelComplex)-> T:
        field = NChar(model.name)
        field.configuration = model
        return field

    def length(self, length: int):
        """Set the length of this field.

        Args:
            length: The length to set for this field.

        Returns:
            A new instance of the field with the updated length.

        """
        return self._length(length)._min_length(length)._max_length(length)

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

    def default(self, default: str):
        return self._default(default)

    def field_max_width(self, max_width: int):
        return self._max_width(max_width)

    def field_width(self, width: int):
        return self._width(width)

    def is_link_field(self):
        return self._link_keep()

    def padchar(self, padchar: FIELD.PadChar):
        return self._padchar(padchar)

    def generate_algorithm(self, generate_algorithm: FIELD.GenerateAlgorithm):
        return self._generate_algorithm(generate_algorithm)

    def cycle_values(self, cycle_values: list[str]):
        return self.cycle_values(cycle_values)

    def alphabet(self, alphabet: str):
        return self._alphabet(alphabet)

    def link_field_reference(self, link_field_reference):
        return self._link_field_reference(link_field_reference)

    def null_seed(self, seed: int):
        return self._null_seed(seed)

    def percent_null(self, percent_null: int):
        return self._percent_null(percent_null)
