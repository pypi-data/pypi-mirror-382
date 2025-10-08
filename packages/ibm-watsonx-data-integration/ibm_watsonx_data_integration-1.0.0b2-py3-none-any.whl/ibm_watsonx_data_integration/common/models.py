# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""Model module."""

import collections
from copy import deepcopy
from ibm_watsonx_data_integration.common.constants import EXPOSE_SUB_CLASS, HIDDEN_DICTIONARY, DataActions
from ibm_watsonx_data_integration.common.utils import SeekableList, TraversableDict, matches_filters
from operator import attrgetter
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, SerializationInfo, model_serializer, model_validator
from typing import Any, ClassVar


class BaseModel(PydanticBaseModel):
    """BaseModel class to standardize objects ."""

    # Use this var to control exposing nested dictionaries from you data
    # The order in which the keys are provided matter
    # Base level IGNORE will happen first
    EXPOSED_DATA_PATH: ClassVar[dict] = {}
    """"Dictionary of key paths used to expose data as attributes

    :meta private:
    """

    # Pydantic variable
    model_config = ConfigDict(
        extra="allow",  # Allow extra fields in the base layer of the data to be attributes
        arbitrary_types_allowed=True,  # Allow non pydantic BaseModel classes to be included in the model
        use_enum_values=True,  # Populate models with the value property of enums,
        #  rather than the raw enum (on model dump)
    )

    def __setattr__(self, name: str, value: Any) -> None:  # noqa: ANN401
        """Setter for attributes.

        Arguments:
           name: Name of the attribute to set
           value: Value of the attribute
        """
        if name in self.__pydantic_extra__:
            self.model_config["extra"] = "allow"

        try:
            super().__setattr__(name, value)
        finally:
            self.model_config["extra"] = "forbid"

    def __repr__(self) -> str:
        """Representation of object.

        Returns:
              A :py:obj:`str` representing the object.
        """
        if hasattr(self, EXPOSE_SUB_CLASS):
            if not getattr(self, EXPOSE_SUB_CLASS):
                return self.__repr_str__(" ")  # Returns __repr__ w/o class name
        return super().__repr__()

    def __str__(self) -> str:
        """String representation of object.

        Returns:
              A :py:obj:`str` representing the object.
        """
        return f"{self.__class__.__name__}({super().__str__()})"

    def __repr_args__(self) -> list:
        """Gets a list of attributes that represent the object.

        Returns:
              A :py:obj:`list` containing attributes that represent the object.
        """
        # Taken from pydantic
        attrs_names = []
        for i in self.__pydantic_fields__:
            if self.__pydantic_fields__[i].repr:
                attrs_names.append(i)
        attrs = ((s, getattr(self, s)) for s in attrs_names)

        # Check if attrs has _expose and is set to False
        # If _expose is set to False don't show class name
        attr_args = []
        for a, v in attrs:
            if v is not None:
                if hasattr(v, EXPOSE_SUB_CLASS) and not v._expose:
                    attr_args.extend(v.__repr_args__())
                elif v is not self:
                    attr_args.append((a, v))
                else:
                    attr_args.append((a, self.__repr_recursion__(v)))
        return attr_args

    @model_validator(mode="before")
    @classmethod
    def entity_validation(cls, data: dict) -> dict:
        """Flattens/Manipulates the data.

        Arguments:
           data: Data to be manipulated on

        Returns:
              A :py:obj:`dict` with manipulated data.
        """

        def _flatten_from_key_path(data: dict, key_path: str, key_path_value: dict) -> None:
            data[HIDDEN_DICTIONARY][key_path] = {}
            keys = key_path.split(".")
            expose_keys = key_path_value.get(DataActions.EXPOSE, None)
            ignore_keys = key_path_value.get(DataActions.IGNORE, None)
            tmp_data = data

            # Traverse to the key depth
            for key in keys[:-1]:
                tmp_data = tmp_data[key]
            tmp_data = tmp_data.pop(keys[-1])

            # Keep track of what keys belong
            if expose_keys:
                ignore_keys = tmp_data.keys() - expose_keys
            elif ignore_keys:
                expose_keys = tmp_data.keys() - ignore_keys
            else:
                expose_keys = tmp_data.keys()
                ignore_keys = []

            data[HIDDEN_DICTIONARY][key_path]["exposed_keys"] = list(expose_keys)
            data[HIDDEN_DICTIONARY][key_path]["ignored"] = {}
            # These keys overwrite data exposed in the base layer, need to be maintained
            # so we don't delete it from the base layer
            data[HIDDEN_DICTIONARY][key_path]["overwrite"] = []

            # Flatten out the data
            for key in expose_keys:
                if key in data.keys():
                    data[HIDDEN_DICTIONARY][key_path]["overwrite"].append(key)
                data[key] = tmp_data[key]
            for key in ignore_keys:
                data[HIDDEN_DICTIONARY][key_path]["ignored"][key] = tmp_data[key]

        def _hide_data(data: dict, keys_to_hide: list) -> None:
            for key in keys_to_hide:
                data[HIDDEN_DICTIONARY]["base_keys"][key] = data[key]
                del data[key]

        if HIDDEN_DICTIONARY not in data:
            data[HIDDEN_DICTIONARY] = {}

        key_paths = list(cls.EXPOSED_DATA_PATH.keys())

        # Check for base level actions
        data = deepcopy(data)  # So we don't manipulate the original data
        if DataActions.IGNORE in key_paths:
            key_paths.remove(DataActions.IGNORE)
            data[HIDDEN_DICTIONARY]["base_keys"] = {}
            _hide_data(data, cls.EXPOSED_DATA_PATH[DataActions.IGNORE])

        for key_path in key_paths:
            key_action = cls.EXPOSED_DATA_PATH[key_path]
            _flatten_from_key_path(data, key_path, key_action)
        return data

    @model_serializer(mode="wrap")
    def serialize_model(self, handler: Any, info: SerializationInfo) -> dict:  # noqa: ANN401
        """Serializes the data, back into it's original formatting.

        Returns:
              A :py:obj:`dict` with updated information
        """
        data = handler(self)
        base_keys = data[HIDDEN_DICTIONARY].get("base_keys", None)
        if base_keys:
            for key in base_keys.keys():
                data[key] = data[HIDDEN_DICTIONARY]["base_keys"][key]
            del data[HIDDEN_DICTIONARY]["base_keys"]

        for key_path in data[HIDDEN_DICTIONARY]:
            keys = key_path.split(".")
            tmp_data = data

            # Traverse through the keys
            for key in keys:
                tmp_data.setdefault(key, {})
                tmp_data = tmp_data[key]

            # Wrap back the data in its appropriate field
            for key in data[HIDDEN_DICTIONARY][key_path]["exposed_keys"]:
                tmp_data[key] = data[key]
                if key not in data[HIDDEN_DICTIONARY][key_path]["overwrite"]:
                    del data[key]
            tmp_data.update(data[HIDDEN_DICTIONARY][key_path]["ignored"])
        del data[HIDDEN_DICTIONARY]
        return data

    def model_dump(self, by_alias: bool = True, **kwargs: any) -> dict:
        """Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.

        Returns:
           A dictionary representation of the model.
        """
        return super().model_dump(by_alias=by_alias, **kwargs)

    def model_post_init(self, __context: Any) -> None:  # Automatically runs post init # noqa: ANN401
        """Don't allow extra variables after initialization."""
        self.model_config["extra"] = "ignore"  # Doesn't allow extra variables to be set


CollectionModelResults = collections.namedtuple(
    "CollectionModelResults",
    ["results", "class_type", "response_bookmark", "request_bookmark", "response_location", "constructor_params"],
)


class CollectionModel:
    """Base class wrapper with abstractions for pagination."""

    def __init__(self, platform: object = None) -> None:
        """The __init__ of the Project class.

        Args:
            platform: The Platform object.
        """
        self._platform = platform

    def _paginate(self, **kwargs: dict) -> BaseModel:
        """Allows fetching of items in batches (pages).

        Returns:
            An inherited instance of :py:class:`ibm_watsonx_data_integration.common.models.BaseModel`.
        """
        filters = kwargs
        local_filters = {key: value for key, value in filters.items() if key not in self._request_parameters()}
        all_ids = set()
        retriever = attrgetter(self.unique_id)
        current_results_len = len(self)

        # Iterate over pages
        while current_results_len > 0:
            response, class_type, response_bookmark, request_bookmark, response_location, constructor_params = (
                self._get_results_from_api(filters)
            )
            response = TraversableDict(response)
            current_results = list(class_type(**constructor_params, **item) for item in response[response_location])
            for result in current_results:
                # This check is to avoid duplicates
                item_id = retriever(result)
                if (item_id not in all_ids) and matches_filters(result, **local_filters):
                    all_ids.add(item_id)
                    yield result

            if response.get(response_bookmark, None):
                filters[request_bookmark] = response[response_bookmark]
            else:
                break

            current_results_len = len(current_results)

    def __repr__(self) -> str:
        """List representation of the objects.

        Returns:
              A :py:obj:`str` representing the objects.
        """
        return str([item for item in self._paginate()])

    def __iter__(self) -> BaseModel:
        """Iterate over the objects obtained.

        Returns:
            An inherited instance of :py:class:`ibm_watsonx_data_integration.common.models.BaseModel`.
        """
        for item in self._paginate():
            yield item

    def __len__(self) -> int:
        """Provides length (count) of items."""
        raise NotImplementedError(f"Function has not been implemented for class {type(self).__name__}")

    def __getitem__(self, i: int) -> BaseModel:
        """Enables the user to fetch items by index.

        Args:
            i (:obj:`int`): Index of the item.

        Returns:
            An inherited instance of :py:class:`ibm_watsonx_data_integration.common.models.BaseModel`.
        """
        return list(self._paginate())[i]

    def _get_all_results_from_api(self, **kwargs: dict) -> CollectionModelResults:
        """Used to get multiple (all) results from api.

        Args:
            **kwargs: Optional arguments to be passed to filter the results.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:obj:`list`): a list of inherited instances of :py:class:`streamsets.sdk.sch_models.BaseModel`
                class_type (:py:class:`streamsets.sdk.sch_models.BaseModel`): the type of class to instantiate
                response_bookmark (:obj:`str`): the location of the bookmark in the results
                request_bookmark (:obj:`str`): the location of where to put the bookmark when making a new request
                response_location (:obj:`str`): the location of the results needed to create object in the results
        """
        raise NotImplementedError(f"Function has not been implemented for class {type(self).__name__}")

    def _request_parameters(self) -> list:
        """Get a list of params that is used when making a api request."""
        raise NotImplementedError(f"Function has not been implemented for class {type(self).__name__}")

    def get_all(self, **kwargs: dict) -> list:
        """Used to get multiple (all) results from api.

        Args:
            **kwargs: Optional other arguments to be passed to filter the results.

        Returns:
            A :py:obj:`list` of inherited instances of
                :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        return SeekableList(self._paginate(**kwargs))

    def get(self, **kwargs: dict) -> BaseModel:
        """Used to get an instant result from the api.

        Args:
            **kwargs: Optional arguments to be passed to filter the results.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.

        Raises:
            ValueError: If instance is not in the list.
        """
        for item in self._paginate(**kwargs):
            return item
        # Raise instance doesn't exist if not found at the end
        raise ValueError("Instance ({}) is not in list".format(", ".join(f"{k}={v}" for k, v in kwargs.items())))
