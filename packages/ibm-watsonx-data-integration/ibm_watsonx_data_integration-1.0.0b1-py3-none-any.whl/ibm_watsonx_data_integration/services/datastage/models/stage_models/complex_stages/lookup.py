from ibm_watsonx_data_integration.services.datastage.models.enums import LOOKUP
from pydantic import BaseModel, ConfigDict, Field


class LookupDerivation(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    lookup_failure: LOOKUP.LookupFail = Field(LOOKUP.LookupFail.fail, alias="lookupFail")
    reference_link: str = Field(None, alias="reference_link")
    condition: str | None = Field(None, alias="Condition")
    condition_not_met: LOOKUP.ConditionNotMet | None = Field(LOOKUP.ConditionNotMet.fail, alias="conditionNotMet")
    derivations: list[dict] | None = Field([], alias="derivations")


class lookup:
    LookupDerivation = LookupDerivation
