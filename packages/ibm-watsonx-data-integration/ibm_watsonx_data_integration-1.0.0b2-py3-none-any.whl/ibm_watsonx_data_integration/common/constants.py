# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module contains project-wide constants."""

from enum import Enum

DATASTAGE = "datastage"

RESOURCE_PLAN_ID_MAP = {DATASTAGE: "aaa6e83e-27df-4393-9a55-63feec09c685"}
DEFAULT_RESOURCE_REGION_ID_MAP = {DATASTAGE: "us-south"}

# BASE MODEL VARS
HIDDEN_DICTIONARY = "_hidden_key_paths"
EXPOSE_SUB_CLASS = "_expose"

# PROD URLS
PROD_BASE_API_URL = "https://api.dataplatform.cloud.ibm.com"
PROD_BASE_URL = "https://cloud.ibm.com"


class DataActions(str, Enum):
    """Actions supported in EXPOSED_DATH_PATH."""

    IGNORE = "IGNORE"
    EXPOSE = "EXPOSE"  # Shouldn't be used on the base level


SUPPORTED_FLOWS = {"streamsets", "datastage"}
