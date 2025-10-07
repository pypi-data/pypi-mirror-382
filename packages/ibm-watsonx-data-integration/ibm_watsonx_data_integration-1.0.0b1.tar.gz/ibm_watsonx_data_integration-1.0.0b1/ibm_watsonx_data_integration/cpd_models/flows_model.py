# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""Flows module."""

# Can't be part of flow_model.py due to circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models.project_model import Project
import itertools
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel
from ibm_watsonx_data_integration.common.utils import SeekableList
from ibm_watsonx_data_integration.services.datastage.models import (
    DataStageFlows,
)
from ibm_watsonx_data_integration.services.streamsets.models import (
    StreamsetsFlows,
)


class Flows(CollectionModel):
    """Collection of DataStageFlow and StreamsetsFlow objects."""

    def __init__(self, project: "Project") -> None:
        """The __init__ of the Flows class.

        Args:
            project: The Project object.
        """
        self._sx_flows = StreamsetsFlows(project)
        self._data_flows = DataStageFlows(project)

    def _paginate(self, **kwargs: dict) -> BaseModel:
        for item in itertools.chain(self._sx_flows, self._data_flows):
            yield item

    def get_all(self, flow_type: str = None, **kwargs: dict) -> SeekableList:
        """Used to get multiple (all) results from flows api.

        Args:
            flow_type: The type of flow to be returned
            **kwargs: Optional other arguments to be passed to filter the results.

        Returns:
            A :py:obj:`list` of inherited instances of
                :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        if flow_type == "streamsets":
            return self._sx_flows.get_all(**kwargs)
        elif flow_type == "datastage":
            return self._data_flows.get_all(**kwargs)
        else:
            return self._sx_flows.get_all(**kwargs) + self._data_flows.get_all(**kwargs)

    def get(self, flow_type: str = None, **kwargs: dict) -> SeekableList:
        """Used to get an instant result from the api.

        Args:
            flow_type: The type of flow to be returned
            **kwargs: Optional arguments to be passed to filter the results.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.

        Raises:
            ValueError: If instance is not in the list.
        """
        if flow_type == "streamsets":
            return self._sx_flows.get(**kwargs)
        elif flow_type == "datastage":
            return self._data_flows.get(**kwargs)
        else:
            try:
                return self._sx_flows.get(**kwargs)
            except Exception:
                return self._data_flows.get(**kwargs)
