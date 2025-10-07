#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Python Generator custom class to hold generated script."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Code:
    """Utility class to hold generate script of recreating pipeline."""

    def __init__(self, content: str) -> None:
        """The __init__ of the Code class.

        Args:
            content: Generated script as string.
        """
        self._content = content

    def __str__(self) -> str:
        """String representation of containing script."""
        return self._content

    def save(self, path: "Path") -> "Path":
        """Save script content to given path.

        Args:
            path: Location where to save containing script.

        Return:
            Path where generate script was saved.
        """
        with open(path, "w") as f:
            f.write(self._content)

        return path


class Coder(ABC):
    """Interface for classes that should return generated scrip wrapped in ``Code`` class."""

    @abstractmethod
    def to_code(self) -> Code:
        """Here we should return code representation."""
