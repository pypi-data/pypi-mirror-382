#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing exceptions specific to streamsets."""


class StageDefinitionNotFound(Exception):
    """Exception for when a stage's definition uses no services."""

    def __init__(self, message: str) -> None:
        """The __init__ for the exception.

        Args:
            message: error message to print with the exception.
        """
        super().__init__(message)
