#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Service Models."""

import json
import requests
from ibm_watsonx_data_integration.common.constants import (
    DATASTAGE,
    DEFAULT_RESOURCE_REGION_ID_MAP,
    RESOURCE_PLAN_ID_MAP,
)
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from pydantic import Field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class Service(BaseModel):
    """The Model for Services."""

    id: str = Field(repr=False, frozen=True)
    guid: str = Field(repr=True, frozen=True)
    url: str = Field(repr=False, frozen=True)
    created_at: str = Field(repr=False, frozen=True)
    updated_at: str = Field(repr=False, frozen=True)
    deleted_at: str | None = Field(repr=False, frozen=True)
    created_by: str = Field(repr=False, frozen=True)
    updated_by: str = Field(repr=False, frozen=True)
    deleted_by: str = Field(repr=False, frozen=True)
    scheduled_reclaim_at: str | None = Field(repr=False, frozen=True)
    restored_at: str | None = Field(repr=False, frozen=True)
    scheduled_reclaim_by: str = Field(repr=False, frozen=True)
    restored_by: str = Field(repr=False, frozen=True)
    name: str = Field(repr=True)
    region_id: str = Field(repr=False, frozen=True)
    account_id: str = Field(repr=False, frozen=True)
    reseller_channel_id: str = Field(repr=False, frozen=True)
    resource_plan_id: str = Field(repr=False, frozen=True)
    resource_group_id: str = Field(repr=False, frozen=True)
    dashboard_url: None | str = Field(repr=False, default=None, frozen=True)
    resource_group_crn: str = Field(repr=False, frozen=True)
    target_crn: str = Field(repr=False, frozen=True)
    allow_cleanup: bool = Field(repr=False, frozen=True)
    crn: str = Field(repr=False, frozen=True)
    state: str = Field(repr=False, frozen=True)
    type: str = Field(repr=False, frozen=True)
    resource_id: str = Field(repr=False, frozen=True)
    last_operation: dict | None = Field(repr=False, frozen=True)
    resource_aliases_url: str = Field(repr=False, frozen=True)
    resource_bindings_url: str = Field(repr=False, frozen=True)
    resource_keys_url: str = Field(repr=False, frozen=True)
    plan_history: list | None = Field(repr=False, frozen=True)
    migrated: bool = Field(repr=False, frozen=True)
    controlled_by: str = Field(repr=False, frozen=True)
    locked: bool = Field(repr=False, frozen=True)
    onetime_credentials: bool = Field(repr=False, frozen=True)

    def __init__(self, platform: Optional["Platform"] = None, **service_json: dict) -> None:
        """The __init__ of the Service.

        Args:
            service_json: The JSON for the Service.
            platform: The Platform object.
        """
        super().__init__(**service_json)
        self._platform = platform

    @staticmethod
    def _create(
        platform: "Platform",
        instance_type: str,
        name: str,
        target: str | None = None,
        tags: list | None = None,
    ) -> "Service":
        resource_plan_id = RESOURCE_PLAN_ID_MAP[instance_type]
        resource_group_id = platform._resource_controller_api.get_resource_groups().json()["resources"][0]["id"]
        target = target if target else DEFAULT_RESOURCE_REGION_ID_MAP[instance_type]
        tags = tags if tags else []

        data = {
            "name": name,
            "target": target,
            "resource_plan_id": resource_plan_id,
            "resource_group": resource_group_id,
            "tags": tags,
        }

        response = platform._resource_controller_api.create_resource_instance(json.dumps(data))

        return Service(platform=platform, **response.json())

    def _delete(self, delete_keys: bool = True) -> requests.Response:
        return self._platform._resource_controller_api.delete_resource_instance(self.guid, recursive=delete_keys)


class Services(CollectionModel):
    """Collection of Service instances."""

    def __init__(self, platform: "Platform") -> None:
        """The __init__ of the Services class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self._platform = platform
        self.unique_id = "id"
        self.resource_id = next((k for k, v in platform._service_id_to_name_map.items() if v == DATASTAGE))

    def __len__(self) -> int:
        """The len of the Services class."""
        res = self._platform._resource_controller_api.get_resource_instances({"type": "service_instance"})
        res_json = res.json()
        return res_json["rows_count"]

    def _request_parameters(self) -> list:
        return ["start", "type", "limit"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        if request_params.get("start", None):
            request_params["start"] = request_params["start"].split("start=")[1]

        request_params_defaults = {"start": None, "type": "service_instance"}
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)
        response = self._platform._resource_controller_api.get_resource_instances(
            params={k: v for k, v in request_params_unioned.items() if v is not None}
        ).json()
        return CollectionModelResults(
            response,
            Service,
            "next_url",
            "start",
            "resources",
            {"platform": self._platform},
        )
