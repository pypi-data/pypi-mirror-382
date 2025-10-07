#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing AccountOwner Model."""

from ibm_watsonx_data_integration.common.models import BaseModel
from pydantic import ConfigDict, Field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class AccountOwner(BaseModel):
    """Model representing the owner of an account.

    Attributes:
        user_name: The username of the account owner (often the email).
        email: The email address of the account owner.
        given_name: The given name of the account owner.
        family_name: The family name of the account owner.
    """

    user_name: str = Field(alias="userName", repr=True)
    email: str = Field(repr=False)
    given_name: str = Field(alias="givenName", repr=False)
    family_name: str = Field(alias="familyName", repr=False)

    model_config = ConfigDict(frozen=True)

    def __init__(self, platform: Optional["Platform"] = None, **account_owner_json: dict) -> None:
        """The __init__ of the Account Owner.

        Args:
            platform: The Platform object.
            account_owner_json: The JSON for the Account Owner.
        """
        super().__init__(**account_owner_json)
        self._platform = platform
