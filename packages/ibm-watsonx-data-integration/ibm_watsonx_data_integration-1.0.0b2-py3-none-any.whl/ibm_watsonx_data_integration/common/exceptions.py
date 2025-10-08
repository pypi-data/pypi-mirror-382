# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""Module containing exceptions for IBM Cloud."""

import json
from requests import Response
from requests.exceptions import HTTPError, JSONDecodeError


class IbmCloudApiException(HTTPError):
    """Exception class for errors returned by APIs."""

    def __init__(self, *args: any, **kwargs: any) -> None:
        """__init__ for the exception.

        Args:
            args: Any arguments for the error
            kwargs: Any keyword args for the error, expects a "response" object to be present.
        """
        response = kwargs.get("response")
        if isinstance(response, Response) and response.content:
            try:
                pretty_response_json = json.dumps(response.json(), indent=4)
                super().__init__(pretty_response_json, *args, **kwargs)
            except JSONDecodeError:
                super().__init__(f"<{response.status_code}> {response.reason}", *args, **kwargs)

        else:
            super().__init__(*args, **kwargs)


class IAMAuthenticationError(Exception):
    """Base class for IAM authenticator exceptions."""

    pass


class InvalidUrlError(IAMAuthenticationError):
    """Raised when the IAM URL is incorrect."""

    pass


class InvalidApiKeyError(IAMAuthenticationError):
    """Raised when the API key is invalid."""

    pass


class CloudObjectStorageNotFoundError(Exception):
    """Raised when the Cloud Object Storage resource is missing."""

    pass


class NoEnginesInstalledError(Exception):
    """Raised when no engines are installed in the environment."""

    pass


class StageNotFoundError(Exception):
    """Raised when a stage with the given label or name is not found."""

    pass


class UniqueStageNameNotFoundError(Exception):
    """Raised when a unique instance name for a stage cannot be determined."""

    pass
