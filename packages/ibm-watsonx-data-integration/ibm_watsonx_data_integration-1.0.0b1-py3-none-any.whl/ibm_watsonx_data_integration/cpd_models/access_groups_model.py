#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing AccessGroup Model."""

import json
import requests
from ibm_watsonx_data_integration.common.exceptions import IbmCloudApiException
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.cpd_models.service_id_model import ServiceID
from ibm_watsonx_data_integration.cpd_models.trusted_profile_model import TrustedProfile
from ibm_watsonx_data_integration.cpd_models.user_model import UserProfile
from pydantic import Field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class AccessGroup(BaseModel):
    """Model representing an Access Group, including Rules."""

    id: str = Field(frozen=True, repr=False)
    name: str = Field(repr=True)
    description: str = Field(repr=True)
    created_at: str = Field(repr=False, frozen=True)
    created_by_id: str = Field(repr=False, frozen=True)
    last_modified_at: str = Field(repr=False, frozen=True)
    last_modified_by_id: str = Field(repr=False, frozen=True)

    def __init__(self, platform: Optional["Platform"] = None, **access_group_json: dict) -> None:
        """The __init__ of the AccessGroup class.

        Args:
            platform: The Platform object.
            access_group_json: The JSON for the AccessGroup.
        """
        super().__init__(**access_group_json)
        self._platform = platform

    def __repr__(self) -> str:
        """The access group's representation."""
        desc = self.description
        try:
            self.description = (desc[:75] + "...") if len(desc) > 75 else desc
            return super().__repr__()
        finally:
            self.description = desc

    @staticmethod
    def _create(platform: "Platform", name: str, description: str | None = None) -> "AccessGroup":
        data = {"name": name, "description": description}
        data = json.dumps(data)

        params = {"account_id": platform.current_account.account_id}

        response = platform._access_group_api.create_access_group(params=params, data=data)

        access_group_json = response.json()
        access_group_json["etag"] = response.headers["Etag"]
        return AccessGroup(platform=platform, **access_group_json)

    def _update(self) -> requests.Response:
        data = {"name": self.name, "description": self.description}
        data = json.dumps(data)

        get_ag = self._platform._access_group_api.get_access_group(access_group_id=self.id)
        etag = get_ag.headers["Etag"]

        response = self._platform._access_group_api.update_access_group(access_group_id=self.id, etag=etag, data=data)

        return response

    def _delete(self) -> requests.Response:
        return self._platform._access_group_api.delete_access_group(self.id)

    def add_members_to_access_group(
        self, members: UserProfile | ServiceID | TrustedProfile | list[UserProfile | ServiceID | TrustedProfile]
    ) -> requests.Response:
        """Adds members to an AccessGroup.

        Args:
            members: The members to be added to the access group.

        Returns:
            A HTTP response.
        """
        if not isinstance(members, list):
            m_list = [members]
            members = m_list

        members_list = []
        for m in members:
            members_list.append({"iam_id": m.iam_id, "type": m.type})
        data = {"members": members_list}
        data = json.dumps(data)
        return self._platform._access_group_api.add_members(self.id, data)

    def get_access_group_members(self) -> list:
        """Gets all members of an AccessGroup.

        Returns:
            A list of current members of an Access Group
        """
        ag_members_json_list = self._platform._access_group_api.get_members(self.id).json()["members"]

        user_id_set = set()
        service_id_set = set()
        trusted_profile_id_set = set()

        for member in ag_members_json_list:
            iam_id = member["iam_id"]
            if member["type"] == "user":
                user_id_set.add(iam_id)
            elif member["type"] == "service":
                service_id_set.add(iam_id)
            elif member["type"] == "profile":
                trusted_profile_id_set.add(iam_id)

        users_list = self.get_users(user_id_set)
        service_id_list = self.get_service_ids(service_id_set)
        trusted_profile_id_list = self.get_trusted_profiles(trusted_profile_id_set)

        return [*users_list, *service_id_list, *trusted_profile_id_list]

    def remove_members_from_access_group(
        self, members: UserProfile | ServiceID | TrustedProfile | list[UserProfile | ServiceID | TrustedProfile]
    ) -> requests.Response:
        """Removes members from access group.

        Args:
            members: List of members to remove from access group.

        Returns:
            A HTTP response.
        """
        if not isinstance(members, list):
            m_list = [members]
            members = m_list

        member_ids = []
        for m in members:
            member_ids.append(m.iam_id)

        data = {"members": member_ids}
        data = json.dumps(data)

        return self._platform._access_group_api.remove_members_from_access_group(self.id, data)

    def check_membership(self, member: UserProfile | ServiceID | TrustedProfile) -> requests.Response:
        """Checks the membership of a member in an access group.

        Args:
            member: The member object to check membership of.

        Returns:
            A HTTP response.
        """
        try:
            response = self._platform._access_group_api.check_membership(access_group_id=self.id, iam_id=member.iam_id)
            return response
        except IbmCloudApiException as e:
            return e.response

    def get_users(self, user_id_set: set) -> list:
        """Gets all users with membership to the current access group.

        Args:
            user_id_set: The set of all users in the current account

        Returns:
            list_of_users: List of all users with membership to current access group.
        """
        list_of_users = []

        for user in self._platform.users:
            if user.iam_id in user_id_set:
                list_of_users.append(user)
        return list_of_users

    def get_service_ids(self, service_id_set: set) -> list:
        """Gets all service IDs with membership to the current access group.

        Args:
            service_id_set: The set of all service IDs in the current account

        Returns:
            list_of_service_ids: List of all service IDs with membership to current access group.
        """
        list_of_service_ids = []

        for service_id in self._platform.service_ids:
            if service_id.iam_id in service_id_set:
                list_of_service_ids.append(service_id)

        return list_of_service_ids

    def get_trusted_profiles(self, trusted_profile_set: set) -> list:
        """Gets all trusted profiles with membership to the current access group.

        Args:
            trusted_profile_set: The set of all trusted profiles in the current account

        Returns:
            list_of_trusted_profles: List of all trusted profiles with membership to current access group.
        """
        list_of_trusted_profiles = []

        for trusted_profile in self._platform.trusted_profiles:
            if trusted_profile.iam_id in trusted_profile_set:
                list_of_trusted_profiles.append(trusted_profile)

        return list_of_trusted_profiles


class AccessGroups(CollectionModel):
    """Collection of AccessGroup instances."""

    def __init__(self, platform: Optional["Platform"] = None) -> None:
        """The __init__ of the AccessGroups class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "id"

    def __len__(self) -> int:
        """Total amount of access groups."""
        self._platform.current_account
        return self._platform._access_group_api.get_all_access_groups(
            params={"account_id": self._platform._current_account.account_id}
        ).json()["total_count"]

    def _request_parameters(self) -> list:
        return [
            "account_id",
            "iam_id",
            "search",
            "membership_type",
            "limit",
            "offset",
            "sort",
            "show_federated",
            "hide_public_access",
            "show_crn",
            "access_group_id",
        ]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        if "account_id" in request_params:
            next_url = request_params.pop("account_id")
            account_id = next_url["href"].split("account_id=")[1]
            offset = next_url["href"].split("offset=")[1].split("&")[0]
        else:
            account_id = self._platform._current_account.account_id
            offset = 0
        request_params_defaults = {
            "account_id": account_id,
            "iam_id": None,
            "access_group_id": None,
            "search": None,
            "membership_type": None,
            "limit": 100,
            "offset": offset,
            "sort": None,
            "show_federated": None,
            "hide_public_access": None,
            "show_crn": None,
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)

        access_group_id = request_params_unioned.get("access_group_id")

        if access_group_id:
            response = self._platform._access_group_api.get_access_group(access_group_id=access_group_id)
            response = {"groups": [response.json()]}
        else:
            response = self._platform._access_group_api.get_all_access_groups(
                params={k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()
        return CollectionModelResults(
            response,
            AccessGroup,
            "next",
            "account_id",
            "groups",
            {"platform": self._platform},
        )
