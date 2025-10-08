#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Source class from Flow model."""

from ibm_watsonx_data_integration.codegen.sources.base_source import Source
from typing import TYPE_CHECKING
from typing_extensions import override

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models.flow_model import Flow


class FlowObjectSource(Source):
    """Loads and convert to intermediate format flow definition from ``Flow`` object."""

    def __init__(self, flow: "Flow") -> None:
        """The __init__ of the FlowObjectSource class.

        Args:
            flow: Flow object instance.
        """
        # TODO: Add validation if flow is StreamSets type.
        self._flow = flow

    @override
    def to_json(self) -> dict:
        return self._flow.model_dump()
