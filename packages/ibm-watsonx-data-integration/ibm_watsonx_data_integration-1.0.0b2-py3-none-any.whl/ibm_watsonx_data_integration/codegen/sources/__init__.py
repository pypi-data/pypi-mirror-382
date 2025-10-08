# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module contains common sources for PythonGenerator."""

from ibm_watsonx_data_integration.codegen.sources.base_source import Source
from ibm_watsonx_data_integration.codegen.sources.flow_object_source import FlowObjectSource
from ibm_watsonx_data_integration.cpd_models.flow_model import Flow


def source_factory(source: str | Flow) -> Source:
    """Factory wrapping source to appropriate object.

    Args:
        source: Input source that contains flow definition.

    Raises:
        TypeError: If input source type is not supported.
    """
    if not isinstance(source, Flow):
        raise TypeError("Currently only Flow class instance is supported as a source.")

    return FlowObjectSource(source)


__all__ = ["source_factory"]
