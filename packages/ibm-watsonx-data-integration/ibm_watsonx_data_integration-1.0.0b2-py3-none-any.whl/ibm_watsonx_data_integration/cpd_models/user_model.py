#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Modules containing UserProfile Model and UserSettings Model."""

from __future__ import annotations

import json
import requests
from enum import Enum
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from pydantic import ConfigDict, Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class UserState(Enum):
    """An enumeration representing the possible states of a user's account."""

    PROCESSING = "PROCESSING"
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    DISABLED_CLASSIC_INFRASTRUCTURE = "DISABLED_CLASSIC_INFRASTRUCTURE"
    VPN_ONLY = "VPN_ONLY"


class UserProfile(BaseModel):
    """Model representing a user profile.

    Attributes:
        id: Unique identifier of the user.
        iam_id: The user's IAM ID.
        realm: The realm to which the user belongs.
        user_id: The user's identifier (often their email address).
        first_name: The first name (given name) of the user.
        last_name: The last name (family name) of the user.
        state: The current state of the user's account (e.g. PROCESSING, PENDING, ACTIVE,
            DISABLED_CLASSIC_INFRASTRUCTURE, VPN_ONLY).
        sub_state: The substate of the user's account, if applicable.
        email: The email address of the user.
        phone: The primary phone number of the user.
        alt_phone: An alternative phone number for the user.
        photo: A URL or reference to the user's photo.
        account_id: Unique identifier of the account the user belongs to.
        added_on: Timestamp of when the user was added.
        invited_on: Timestamp of when the user was invited.
    """

    id: str = Field(repr=True)
    iam_id: str = Field(repr=True)
    realm: str = Field(repr=False)
    user_id: str = Field(repr=True)
    first_name: str | None = Field(default=None, alias="firstname", repr=False)
    last_name: str | None = Field(default=None, alias="lastname", repr=False)
    state: UserState = Field(repr=True)
    sub_state: str | None = Field(default=None, repr=False)
    email: str = Field(repr=True)
    phone: str | None = Field(default=None, alias="phonenumber", repr=False)
    alt_phone: str | None = Field(default=None, alias="altphonenumber", repr=False)
    photo: str | None = Field(default=None, repr=False)
    account_id: str = Field(repr=True)
    added_on: str = Field(repr=True)
    invited_on: str | None = Field(default=None, alias="invitedOn", repr=False)

    model_config = ConfigDict(use_enum_values=True, frozen=True)
    _expose: bool = True

    def __init__(self, platform: Platform | None = None, **user_profile_json: dict) -> None:
        """The __init__ of the User Profile.

        Args:
            platform: The Platform object.
            user_profile_json: The JSON for the User Profile.
        """
        super().__init__(**user_profile_json)
        self._platform = platform
        if platform is not None and hasattr(platform, "_user_api"):
            self._user_api = platform._user_api

    @property
    def settings(self) -> UserSettings:
        """Returns the user settings associated with the current IAM identity and the current account.

        Returns:
            A User Settings instance retrieved from the API.
        """
        resp = self._user_api.get_user_settings(self.account_id, self.iam_id)
        return UserSettings(platform=self._platform, **resp.json())

    def update_user_settings(self, user_settings: UserSettings) -> requests.Response:
        """Update the settings for a specific user in an account.

        Args:
            user_settings: Instance of a UserSettings to update.

        Returns:
            A HTTP response.
        """
        payload = {
            "language": user_settings.language,
            "notification_language": user_settings.notification_language,
            "allowed_ip_addresses": user_settings.allowed_ip_addresses,
            "self_manage": user_settings.self_manage,
        }
        return self._user_api.update_user_settings(
            account_id=self.account_id, iam_id=self.iam_id, data=json.dumps(payload)
        )

    @property
    def type(self) -> str:
        """This property returns the member type "user".

        Returns:
            The member type.
        """
        return "user"


class UserSettings(BaseModel):
    """Model representing user settings preferences.

    Attributes:
        language: The user's preferred language. This field may be empty.
        notification_language: The preferred language for notifications. This field may be empty.
        allowed_ip_addresses: A string representing allowed IP addresses (e.g., comma-separated).
            This field may be empty.
        self_manage: Flag indicating if the user has permission to manage their settings.
        two_fa: Flag that indicates whether two-factor authentication is enabled.
                This field is mapped from the JSON key "2FA".
        security_questions_required: Flag indicating if security questions are required for the user.
        security_questions_setup: Flag that indicates whether the user has set up their security questions.
    """

    language: str = Field(default="", repr=False)
    notification_language: str = Field(default="", repr=False)
    allowed_ip_addresses: str = Field(default="", repr=False)
    self_manage: bool = Field(default=False, repr=True)
    two_fa: bool = Field(default=False, alias="2FA", repr=False)
    security_questions_required: bool = Field(default=False, repr=False)
    security_questions_setup: bool = Field(default=False, repr=False)

    _expose: bool = True

    def __init__(self, platform: Platform | None = None, **settings_json: dict) -> None:
        """The __init__ of the UserSettings model.

        Args:
            platform: The Platform object.
            settings_json: The JSON for the user settings.
        """
        super().__init__(**settings_json)
        self._platform = platform


class UserProfiles(CollectionModel):
    """Collection of UserProfile instances."""

    def __init__(self, platform: Platform) -> None:
        """The __init__ of the UserProfiles class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "id"
        self.account_id = platform.current_account.account_id

    def __len__(self) -> int:
        """Total number of user profiles."""
        query_params = {
            "limit": 1,
        }
        res = self._platform._user_api.get_users(self.account_id, params=query_params)
        res_json = res.json()
        return res_json["total_results"]

    def _request_parameters(self) -> list:
        return ["iam_id", "limit", "_start", "user_id"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        if "_start" in request_params:
            request_params["_start"] = request_params["_start"].split("_start=")[1].split("&")[0]

        request_params_defaults = {
            "iam_id": None,
            "limit": None,
            "_start": None,
            "user_id": None,
        }
        request_params_unioned = request_params_defaults.copy()
        request_params_unioned.update(request_params)

        iam_id = request_params_unioned.get("iam_id")
        user_id = request_params_unioned.get("user_id")

        if iam_id and user_id:
            raise ValueError("Only one of 'iam_id' or 'user_id' can be provided, not both.")

        if iam_id:
            response = self._platform._user_api.get_user_profile(self.account_id, iam_id).json()
            response = {"resources": [response]}
        else:
            response = self._platform._user_api.get_users(
                account_id=self.account_id,
                params={k: v for k, v in request_params_unioned.items() if v is not None},
            ).json()
        return CollectionModelResults(
            response,
            UserProfile,
            "next_url",
            "_start",
            "resources",
            {"platform": self._platform},
        )
