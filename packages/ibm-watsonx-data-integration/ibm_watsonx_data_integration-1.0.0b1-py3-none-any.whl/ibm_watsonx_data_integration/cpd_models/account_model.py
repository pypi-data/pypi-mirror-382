#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025


"""Module containing Account Model."""

from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from pydantic import ConfigDict, Field, PrivateAttr
from typing import TYPE_CHECKING, Any, ClassVar, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class AccountMetadata(BaseModel):
    """Model representing metadata for an account."""

    # required and is hidden from the model’s string representation.
    guid: str = Field(repr=False)
    url: str = Field(repr=False)
    created_at: str = Field(repr=False)
    created_by: str | None = Field(default=None, repr=False)
    updated_at: str = Field(repr=False)
    updated_by: str = Field(repr=False)
    update_comments: str = Field(repr=False)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class BluemixSubscription(BaseModel):
    """Model representing a Bluemix subscription with payment details."""

    type: str = Field(repr=False)
    state: str = Field(repr=False)
    payment_method: dict = Field(repr=False)
    subscription_id: str = Field(repr=False)
    part_number: str = Field(repr=False)
    subscriptionTags: list[Any] = Field(repr=False)
    history: list[Any] | None = Field(default=None, repr=False)
    current_state_timestamp: str = Field(repr=False)
    billing_system: str = Field(repr=False)
    category: str = Field(repr=False)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)

    @property
    def payment_type(self) -> str | None:
        """Access the ``type`` in payment_method.

        Returns:
            A payment type.
        """
        return self.payment_method.get("type")

    @property
    def payment_started(self) -> str | None:
        """Access the ``started`` in payment_method.

        Returns:
            A started payment type.
        """
        return self.payment_method.get("started")

    @property
    def payment_ended(self) -> str | None:
        """Access the ``ended`` in payment_method.

        Returns:
            A ended payment type.
        """
        return self.payment_method.get("ended")


class Account(BaseModel):
    """Model representing an account, including metadata and flattened entity details."""

    metadata: AccountMetadata = Field(repr=False)

    name: str = Field(repr=True)
    account_type: str = Field(alias="type", repr=True)
    state: str = Field(repr=False)
    # not required, default to an empty string ("") and is hidden from the model’s string representation.
    owner: str | None = Field("", repr=False)
    owner_userid: str = Field(repr=False)
    owner_unique_id: str = Field(repr=False)
    iam_id: str = Field(alias="owner_iam_id", repr=False)
    account_id: str = Field(alias="customer_id", repr=True, default_factory=lambda fields: fields["metadata"].guid)
    country_code: str = Field(repr=False)
    currency_code: str = Field(repr=False)
    billing_country_code: str = Field(repr=False)
    isIBMer: bool = Field(repr=False)
    terms_and_conditions: dict = Field(repr=False)
    tags: list[Any] = Field(default_factory=list, repr=False)
    team_directory_enabled: bool = Field(repr=False)
    organizations_region: list[Any] = Field(default_factory=list, repr=False)
    linkages: list[dict] = Field(repr=False)
    bluemix_subscriptions: list[BluemixSubscription] = Field(repr=False)
    subscription_id: str = Field(repr=False)
    current_billing_system: str = Field(repr=False)
    configuration_id: str | None = Field(default=None, repr=False)
    onboarded: int = Field(repr=False)
    origin: str = Field(repr=False)

    model_config = ConfigDict(frozen=True)
    _expose: bool = True
    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity": {}}

    def __init__(self, platform: Optional["Platform"] = None, **account_json: dict) -> None:
        """The __init__ of the Account.

        Args:
            platform: The Platform object.
            account_json: The JSON for the Account.
        """
        super().__init__(**account_json)
        self._platform = platform


class Accounts(CollectionModel):
    """Collection of Account instances."""

    def __init__(self, platform: "Platform") -> None:
        """The __init__ of the Accounts class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "metadata.guid"

    def __len__(self) -> int:
        """Total number of accounts."""
        query_params = {
            "limit": 1,
        }
        res = self._platform._account_api.get_accounts(params=query_params)
        res_json = res.json()
        return res_json["total_results"]

    def _request_parameters(self) -> list:
        return ["account_id"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        # TODO (WSDK-196): Add filtering parameters once they have been verified to work correctly.

        request_params_defaults = {
            "account_id": None,
        }
        request_params_unioned = request_params_defaults.copy()
        request_params_unioned.update(request_params)
        account_id = request_params_unioned.get("account_id")

        if account_id:
            response = self._platform._account_api.get_account(account_id).json()
            response = {"resources": [response]}
        else:
            response = self._platform._account_api.get_accounts(
                params={k: v for k, v in request_params_unioned.items() if v is not None}
            ).json()

        if "next_url" in response and response["next_url"] is None:
            response.pop("next_url")

        return CollectionModelResults(
            response,
            Account,
            "next_url",
            "next_url",
            "resources",
            {"platform": self._platform},
        )
