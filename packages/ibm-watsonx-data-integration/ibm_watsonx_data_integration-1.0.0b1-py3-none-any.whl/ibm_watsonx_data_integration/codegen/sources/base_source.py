#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Source interface class."""

from abc import ABC, abstractmethod


class Source(ABC):
    """Interface for flow definition sources."""

    @abstractmethod
    def to_json(self) -> dict:
        """Here we should return source data as dictionary."""
