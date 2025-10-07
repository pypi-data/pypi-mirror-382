import warnings
from ibm_watsonx_data_integration.services.datastage.models.base_stage import BaseStage
from ibm_watsonx_data_integration.services.datastage.models.enums import REST
from pydantic import Field
from typing import ClassVar


class rest(BaseStage):

    op_name: ClassVar[str] = "PxRest"
    node_type: ClassVar[str] = "execution_node"
    image: ClassVar[str] = "/data-intg/flows/graphics/palette/REST.svg"
    label: ClassVar[str] = "Rest"
    runtime_column_propagation: bool = Field(False, alias="runtime_column_propagation")
    combinability: REST.Combinability | None = Field(REST.Combinability.auto, alias="combinability")
    execmode: REST.Execmode | None = Field(REST.Execmode.default_seq, alias="execmode")
    input_count: int | None = Field(0, alias="input_count")
    is_reject_link: bool | None = Field(False, alias="is_reject_link")
    link_name: str | None = Field(" ", alias="link_name")
    log_level: REST.LogLevel | None = Field(REST.LogLevel.warning, alias="log_level")
    log_reject_error: bool | None = Field(False, alias="log_reject_error")
    output_count: int | None = Field(0, alias="output_count")
    parameters: str | None = Field(" ", alias="parameters")
    part_coll: str | None = Field("part_type", alias="part_coll")
    preserve: REST.Preserve | None = Field(REST.Preserve.default_propagate, alias="preserve")
    reject_message_column: REST.RejectMessageColumn | None = Field(
        REST.RejectMessageColumn.custom, alias="reject_message_column"
    )
    requests: list = Field([], alias="requests")
    runtime_column_propagation: int | None = Field(1, alias="runtime_column_propagation")
    variables: dict = Field([], alias="variables")

    def validate(self) -> tuple[set, set]:
        include = set()
        exclude = set()

        return include, exclude

    def get_input_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = {"link_name", "part_coll", "runtime_column_propagation"}
        required = set()
        props = props & (self.model_fields_set | required)
        conflict = exclude & self.model_fields_set & props
        if conflict:
            conflict = list(conflict)
            if len(conflict) == 1:
                warnings.warn(f"\n\033[33mFound conflicting property: {conflict[0]}\033[0m")
            else:
                warnings.warn(
                    f'\n\033[33mFound conflicting properties: {", ".join(conflict[:-1])} and {conflict[-1]}\033[0m'
                )
        exclude = exclude - self.model_fields_set
        return self.model_dump(include=props - exclude, by_alias=True, exclude_none=True, warnings=False)

    def get_input_cardinality(self) -> dict:
        return {"min": 0, "max": -1}

    def get_output_ports_props(self) -> dict:
        include, exclude = self.validate()
        props = {"is_reject_link", "reject_message_column"}
        required = set()
        props = props & (self.model_fields_set | required)
        conflict = exclude & self.model_fields_set & props
        if conflict:
            conflict = list(conflict)
            if len(conflict) == 1:
                warnings.warn(f"\n\033[33mFound conflicting property: {conflict[0]}\033[0m")
            else:
                warnings.warn(
                    f'\n\033[33mFound conflicting properties: {", ".join(conflict[:-1])} and {conflict[-1]}\033[0m'
                )
        exclude = exclude - self.model_fields_set
        return self.model_dump(include=props - exclude, by_alias=True, exclude_none=True, warnings=False)

    def get_output_cardinality(self) -> dict:
        return {"min": 0, "max": -1}

    def get_parameters_props(self) -> dict:
        include, exclude = self.validate()
        props = {
            "combinability",
            "execmode",
            "input_count",
            "log_level",
            "log_reject_error",
            "output_count",
            "parameters",
            "preserve",
            "requests",
            "variables",
        }
        required = {"requests", "variables"}
        props = props & (self.model_fields_set | required)
        conflict = exclude & self.model_fields_set & props
        if conflict:
            conflict = list(conflict)
            if len(conflict) == 1:
                warnings.warn(f"\n\033[33mFound conflicting property {conflict[0]}\033[0m")
            else:
                warnings.warn(
                    f'\n\033[33mFound conflicting properties {", ".join(conflict[:-1])} and {conflict[-1]}\033[0m'
                )
        exclude = exclude - self.model_fields_set
        return self.model_dump(include=props - exclude, by_alias=True, exclude_none=True, warnings=False)

    def get_app_data_props(self) -> dict:
        return {
            "datastage": {
                "maxRejectOutputs": 0,
                "minRejectOutputs": 0,
                "maxReferenceInputs": 0,
                "minReferenceInputs": 0,
            }
        }
