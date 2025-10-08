#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Service ID Model."""

from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from pydantic import Field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class ServiceID(BaseModel):
    """Model representing a Service ID."""

    id: str = Field(repr=True, frozen=True)
    name: str = Field(repr=True)
    iam_id: str = Field(repr=False, frozen=True)
    account_id: str = Field(repr=False, frozen=True)
    entity_tag: str = Field(repr=False, frozen=True)
    crn: str = Field(repr=False, frozen=True)
    locked: bool = Field(repr=False)
    created_at: str = Field(repr=False, frozen=True)
    modified_at: str = Field(repr=False)

    def __init__(self, platform: Optional["Platform"] = None, **service_id_json: dict) -> None:
        """The __init__ of the ServiceID Wrapper class.

        Args:
            service_id_json: The JSON for the Service ID.
            platform: The Platform object. Default: ``None``
        """
        super().__init__(**service_id_json)
        self._platform = platform

    @property
    def type(self) -> str:
        """This property returns the member type "service".

        Returns:
            The member type.
        """
        return "service"


class ServiceIDs(CollectionModel):
    """Collection of ServiceID instances."""

    def __init__(self, platform: Optional["Platform"] = None) -> None:
        """The __init__ of the ServiceIDs class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "id"

    def __len__(self) -> int:
        """Total amount of service IDs."""
        self._platform.current_account
        list_of_service_ids = self._platform._service_id_api.list_all_service_ids(
            params={"account_id": self._platform._current_account.account_id}
        ).json()["serviceids"]
        return len(list_of_service_ids)

    def _request_parameters(self) -> list:
        return [
            "account_id",
            "group_id",
            "name",
            "pagesize",
            "pagetoken",
            "sort",
            "order",
            "include_history",
            "filter",
            "show_group_id",
        ]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of a ServiceID API request to list_all_service_ids."""
        page_token = None
        if "account_id" in request_params:
            next_url = request_params.pop("account_id")
            page_token = next_url.split("pagetoken=")[1]

        request_params_defaults = {
            "account_id": self._platform._current_account.account_id,
            "group_id": None,
            "name": None,
            "pagesize": 100,
            "pagetoken": page_token,
            "sort": None,
            "order": None,
            "include_history": None,
            "filter": None,
            "show_group_id": None,
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)
        response = self._platform._service_id_api.list_all_service_ids(
            params={k: v for k, v in request_params_unioned.items() if v is not None}
        ).json()
        return CollectionModelResults(
            response,
            ServiceID,
            "next",
            "account_id",
            "serviceids",
            {"platform": self._platform},
        )
