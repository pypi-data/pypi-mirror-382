#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025


"""Module containing Roles Models."""

import json
import requests
from enum import Enum
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from pydantic import Field
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class RoleType(str, Enum):
    """The model for RoleType enums."""

    SYSTEM_ROLE = "system_role"
    SERVICE_ROLE = "service_role"
    CUSTOM_ROLE = "custom_role"


class Role(BaseModel):
    """The model for a role."""

    display_name: str = Field(repr=True)
    role_type: RoleType = Field(repr=True, frozen=True)
    actions: list[str] = Field(repr=True)
    description: str | None = Field("", repr=False)
    crn: str | None = Field("", frozen=True, repr=False)
    name: str = Field(None, repr=False, frozen=True)
    account_id: str = Field(None, frozen=True, repr=False)
    service_name: str = Field(None, repr=False, frozen=True)
    id: str = Field("", frozen=True, repr=False)
    created_at: str | None = Field("", frozen=True, repr=False)
    created_by_id: str | None = Field("", frozen=True, repr=False)
    last_modified_at: str | None = Field("", frozen=True, repr=False)
    last_modified_by_id: str | None = Field("", frozen=True, repr=False)
    href: str | None = Field("", frozen=True, repr=False)
    etag: str | None = Field("", repr=False)

    def __init__(self, platform: Optional["Platform"] = None, **custom_role_json: dict) -> None:
        """The __init__ of the CustomRole class.

        Args:
            platform: The Platform object.
            custom_role_json: The JSON for the CustomRole.
        """
        super().__init__(**custom_role_json)
        self._platform = platform

    @staticmethod
    def _create(
        platform: "Platform",
        name: str,
        display_name: str,
        service_name: str,
        actions: list,
        description: str | None = None,
    ) -> "Role":
        if name and name[0].islower():
            name = name[0].upper() + name[1:]

        data = {
            "name": name,
            "display_name": display_name,
            "account_id": platform.current_account.account_id,
            "service_name": service_name,
            "actions": actions,
        }

        if description:
            data["description"] = description

        response = platform._role_api_client.create_role(json.dumps(data))
        response_json = response.json()
        response_json["role_type"] = RoleType.CUSTOM_ROLE
        return Role(platform=platform, **response_json)

    def _update(self) -> requests.Response:
        if self.role_type is not RoleType.CUSTOM_ROLE.value:
            raise TypeError("You can only update a custom role.")

        data = {
            "display_name": self.display_name,
            "description": self.description,
            "actions": self.actions,
        }

        if not self.etag:
            api_response = self._platform._role_api_client.retrieve_role(self.id)
            etag = api_response.headers.get("etag")
        else:
            etag = self.etag

        return self._platform._role_api_client.update_role(self.id, etag, json.dumps(data))

    def _delete(self) -> requests.Response:
        if self.role_type is not RoleType.CUSTOM_ROLE.value:
            raise TypeError("You can only delete a custom role.")

        return self._platform._role_api_client.delete_role(self.id)


class Roles(CollectionModel):
    """Collection of Roles instances."""

    def __init__(self, platform: "Platform") -> None:
        """The __init__ of the Role class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform=platform)
        self.unique_id = "display_name"

    def __len__(self) -> int:
        """Total amount of roles."""
        request_params_defaults = {
            "account_id": self._platform.current_account.account_id,
        }

        api_response = self._platform._role_api_client.get_roles(request_params_defaults).json()
        length = (
            len(api_response["system_roles"]) + len(api_response["service_roles"]) + len(api_response["custom_roles"])
        )
        return length

    def _request_parameters(self) -> list:
        return ["role_id", "account_id", "service_name", "source_service_name", "policy_type", "service_group_id"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "role_id": None,
            "account_id": self._platform.current_account.account_id,
            "service_name": None,
            "source_service_name": None,
            "policy_type": None,
            "service_group_id": None,
        }
        request_params_unioned: dict[str, Any] = request_params_defaults
        if request_params:
            request_params_unioned.update(request_params)

        role_id = request_params_unioned.get("role_id")

        if role_id:
            api_response = self._platform._role_api_client.retrieve_role(role_id)
            etag = api_response.headers.get("etag")
            response_json = api_response.json()
            response_json["etag"] = etag
            response_json["role_type"] = "custom_role"
            response = {"results": [response_json]}
        else:
            api_response = self._platform._role_api_client.get_roles(
                params={k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()

            response = {
                "results": [
                    {**role, "role_type": role_type}
                    for key, role_type in [
                        ("system_roles", RoleType.SYSTEM_ROLE),
                        ("service_roles", RoleType.SERVICE_ROLE),
                        ("custom_roles", RoleType.CUSTOM_ROLE),
                    ]
                    for role in api_response.get(key, [])
                ]
            }

        return CollectionModelResults(
            response,
            Role,
            "",
            "",
            "results",
            constructor_params={"platform": self._platform},
        )
