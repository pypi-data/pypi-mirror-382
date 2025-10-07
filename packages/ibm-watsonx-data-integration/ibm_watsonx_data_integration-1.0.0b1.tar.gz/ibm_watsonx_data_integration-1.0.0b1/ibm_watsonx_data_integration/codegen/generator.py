# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module contains PythonGenerator class."""

from ibm_watsonx_data_integration.codegen.processors.streaming_processor import StreamingProcessor
from ibm_watsonx_data_integration.codegen.sources import source_factory
from ibm_watsonx_data_integration.common.constants import (
    PROD_BASE_API_URL,
    PROD_BASE_URL,
)
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.codegen.code import Coder
    from ibm_watsonx_data_integration.common.auth import IAMAuthenticator
    from ibm_watsonx_data_integration.cpd_models.flow_model import Flow


class PythonGenerator:
    """Flow code generation entrypoint."""

    def __init__(
        self,
        source: "Flow",
        destination: str | Path,
        auth: "IAMAuthenticator",  # pragma: allowlist secret
        **kwargs: str | object,
    ) -> None:
        """The __init__ of the PythonGenerator class.

        Args:
            source: Location from ``Flow`` definition will be loaded.
            destination: Location where save generated script.
            auth: Reference to authenticator object.
            kwargs: Additional configuration values.
        """
        self._source = source_factory(source)
        self._destination = Path(destination)
        base_url = kwargs.get("base_url", PROD_BASE_URL)
        base_api_url = kwargs.get("base_api_url", PROD_BASE_API_URL)
        self._processor: Coder = StreamingProcessor(
            source_data=self._source.to_json(), auth=auth, base_url=base_url, base_api_url=base_api_url
        )

    def save(self) -> Path:
        """Run code generation then save it to destination.

        Returns:
            Path to the location where the generated script was saved.
        """
        code = self._processor.to_code()
        return code.save(self._destination)
