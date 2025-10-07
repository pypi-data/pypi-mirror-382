# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""Authentication module."""

import logging
import requests
import time
from abc import ABC, abstractmethod
from ibm_watsonx_data_integration.common.exceptions import InvalidApiKeyError, InvalidUrlError
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger(__name__)


class BaseAuthenticator(ABC):
    """Base Authenticator classes to be inherited by other authenticators."""

    @abstractmethod
    def get_authorization_header(self) -> str:
        """Returns the token formatted to be plugged into the Authorization header of a request.

        Returns:
            A :py:obj:`str` ready to be used as an Authorization header.
        """
        pass


class IAMAuthenticator(BaseAuthenticator):
    """Authenticator class to authenticate using an IBM Cloud IBM API Key.

    Attributes:
        api_key: API key being used to authenticate.
        token_url: URL being used to authenticate against.
        iam_token: The token generated using the api_key and url.
        token_expiry_time: UNIX time in seconds for when the token will expire.
    """

    # give a time buffer for expiration, to have ample time to make a request without the token being expired.
    EXPIRATION_TIME_BUFFER = 5

    def __init__(self, api_key: str, base_auth_url: str = "https://cloud.ibm.com") -> None:
        """Initializes IAM Authenticator.

        Args:
            api_key: The API key to be used for authentication.
            base_auth_url: The base URL of the IBM cloud instance to be used for authentication.

        Raises:
            InvalidApiKeyError: If api_key is not of type str, or is an empty str.
            InvalidUrlError: If base_auth_url is not of type str, or is an empty str.
            requests.exceptions.HTTPError: If there is an error getting a valid token.
        """
        if not isinstance(api_key, str):
            raise InvalidApiKeyError("api_key should be of type str.")
        if not api_key:
            raise InvalidApiKeyError("api_key should not be an empty str.")

        if not isinstance(base_auth_url, str):
            raise InvalidUrlError("base_auth_url should be of type str.")
        if not base_auth_url:
            raise InvalidUrlError("base_auth_url should not be an empty str.")

        self.api_key = api_key

        # base_auth_url looks like: "https://cloud.ibm.com"
        # token url looks like: "https://iam.cloud.ibm.com/identity/token"
        parsed_url = urlparse(url=base_auth_url)
        new_netloc = "iam." + parsed_url.netloc
        new_path = parsed_url.path + "/identity/token"
        self.token_url = urlunparse((parsed_url.scheme, new_netloc, new_path, "", "", ""))

        self.iam_token = None
        self.token_expiry_time = None
        self.request_token()

    def request_token(self) -> None:
        """Request a token from the servers using the API key.

        Raises:
            InvalidApiKeyError: If api_key is invalid.
            InvalidUrlError: If token_url is invalid.
            requests.exceptions.HTTPError: If there is an error getting a valid token.
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"apikey": self.api_key, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}

        try:
            response = requests.post(self.token_url, headers=headers, data=data)
        except requests.exceptions.ConnectionError as e:
            logger.error("IAMAuthenticator incorrect URL. %s", e)
            raise InvalidUrlError("IAMAuthenticator incorrect URL.")
        if response.status_code == 400:
            raise InvalidApiKeyError("IAMAuthenticator api_key is not valid.")
        response.raise_for_status()

        self.iam_token = response.json()["access_token"]
        self.token_expiry_time = response.json()["expiration"]

    def get_token(self) -> str:
        """Get existing token, or request a new one if the current token is expired.

        Returns:
            A :py:obj:`str` containing the current token.
        """
        current_time = int(time.time())
        if self.iam_token is None:
            logger.debug("Getting first token.")
            self.request_token()
        elif (current_time + self.EXPIRATION_TIME_BUFFER) >= self.token_expiry_time:
            logger.debug("Previous token expired, refreshing.")
            self.request_token()

        return self.iam_token

    def get_authorization_header(self) -> str:
        """Returns the token formatted to be plugged into the Authorization header of a request.

        Returns:
            A :py:obj:`str` ready to be used as an Authorization header.
        """
        return f"Bearer {self.get_token()}"
