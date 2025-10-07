#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Flow Model."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from ibm_watsonx_data_integration.common.models import BaseModel
from typing import Any, ClassVar, TypeVar
from typing_extensions import override

F = TypeVar("F", bound="Flow")


class Flow(BaseModel):
    """Represents a generic Flow object."""

    _flow_registry: ClassVar[dict[str, type[F]]] = {}

    @classmethod
    def register(cls: type[F], flow_type: str) -> Callable[[type[F]], type[F]]:
        """Class decorator to register a new Flow subclass.

        Args:
            flow_type (str):
                The key under which the subclass will be stored in `flow_registry`.

        Returns:
            Callable[[Type[F]], Type[F]]:
                A decorator that registers the subclass and returns it unchanged.
        """

        def inner(subclass: type[F]) -> type[F]:
            cls._flow_registry[flow_type] = subclass
            return subclass

        return inner


class PayloadExtender(ABC):
    """Interface class for flows with custom payload logic.

    This interface should be implemented by any flow that requires custom logic for generating a job's payload.
    It ensures a consistent contract for flows that need to override the default payload creation behavior.

    :meta: private
    """

    @abstractmethod
    def extend(self, payload: dict[str, Any], flow: Flow) -> dict[str, Any]:
        """Here we should modify and return payload for job creation."""
        raise NotImplementedError


class DefaultFlowPayloadExtender(PayloadExtender):
    """Default payload extender which setup only `asset_ref`.

    :meta: private
    """

    @override
    def extend(self, payload: dict[str, Any], flow: Flow) -> dict[str, Any]:
        payload["asset_ref"] = flow.flow_id
        return payload
