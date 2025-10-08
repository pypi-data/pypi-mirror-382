#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Trusted Profile Model."""

from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from pydantic import Field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class TrustedProfile(BaseModel):
    """Model representing a Service ID."""

    id: str = Field(repr=True, frozen=True)
    name: str = Field(repr=True)
    iam_id: str = Field(repr=False, frozen=True)
    account_id: str = Field(repr=False, frozen=True)
    entity_tag: str = Field(repr=False, frozen=True)
    crn: str = Field(repr=False)
    created_at: str = Field(repr=False, frozen=True)
    modified_at: str = Field(repr=False)

    def __init__(self, platform: Optional["Platform"] = None, **trusted_profile_json: dict) -> None:
        """The __init__ of the TrustedProfile Wrapper class.

        Args:
            trusted_profile_json: The JSON for the Trusted Profile.
            platform: The Platform object. Default: ``None``
        """
        super().__init__(**trusted_profile_json)
        self._platform = platform

    @property
    def type(self) -> str:
        """This property returns the member type "profile".

        Returns:
            The member type.
        """
        return "profile"


class TrustedProfiles(CollectionModel):
    """Collection of TrustedProfile instances."""

    def __init__(self, platform: Optional["Platform"] = None) -> None:
        """The __init__ of the TrustedProfiles class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "id"

    def __len__(self) -> int:
        """Total amount of trusted profiles."""
        self._platform.current_account
        list_of_trusted_profiles = self._platform._trusted_profile_api.list_all_trusted_profiles(
            params={"account_id": self._platform._current_account.account_id}
        ).json()["profiles"]
        return len(list_of_trusted_profiles)

    def _request_parameters(self) -> list:
        return ["account_id", "name", "pagesize", "sort", "order", "include_history", "pagetoken", "filter"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of a TrustedProfile API request to list_all_trusted_profiles."""
        page_token = None
        if "account_id" in request_params:
            next_url = request_params.pop("account_id")
            page_token = next_url.split("pagetoken=")[1]

        request_params_defaults = {
            "account_id": self._platform._current_account.account_id,
            "name": None,
            "pagesize": 1,
            "sort": None,
            "order": None,
            "include_history": None,
            "pagetoken": page_token,
            "filter": None,
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)
        response = self._platform._trusted_profile_api.list_all_trusted_profiles(
            params={k: v for k, v in request_params_unioned.items() if v is not None}
        ).json()
        return CollectionModelResults(
            response,
            TrustedProfile,
            "next",
            "account_id",
            "profiles",
            {"platform": self._platform},
        )
