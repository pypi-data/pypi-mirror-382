#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""The __init__ for the data module."""

from ibm_watsonx_data_integration.services.streamsets.data.pipeline_definition import (
    create_pipeline_definition_for_new_flow,
)

__all__ = ["create_pipeline_definition_for_new_flow"]
