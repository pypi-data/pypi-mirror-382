#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""This module defines a utility function to create JSON Patch format payloads.

Implementation is limited to the following use cases:
    1. Changing property values.
    2. Removing entries from a collection list.
    3. Adding entries to a collection list.
"""

import json
import jsondiff
from abc import ABC, abstractmethod
from collections.abc import MutableMapping


def prepare_json_patch_payload(origin: dict, updated: dict, exclude_properties: list[str] | None = None) -> str:
    """Entrypoint function for creating a JSON Patch format-compliant payload.

    Args:
        origin: Dictionary with original data before changes.
        updated: Dictionary after applying changes and updates.
        exclude_properties: List of flatten keys for properties to not include in payload.

    Returns:
        A JSON string compliant with the JSON Patch format standard.
    """
    difference = jsondiff.diff(origin, updated, syntax="explicit")
    flatten = flatten_jsondiff_explicit_result(difference)
    return create_json_patch_document(flatten, exclude_properties=exclude_properties)


def flatten_jsondiff_explicit_result(
    dictionary: MutableMapping, parent_key: str = "", separator: str = "/", last_operation: str = ""
) -> dict:
    """Flattens key paths from the result of ``jsondiff.diff``.

    This function is tightly coupled with the 3rd party library ``jsondiff``.
    It will work correctly for results returned by the ``explicit`` flag for the ``syntax`` argument.

    Args:
        dictionary: A result from ``jsondiff.diff`` execution.
        parent_key: Parent key from the perspective of the current processing key.
        separator: Character that will be used to delimit keys.
        last_operation: Operations mean keys starting with the ``$`` character.
            This parameter holds the last one in the current traversable path.

    Returns:
        A dictionary with flattened paths as keys and the original values as values.
    """
    items = []

    for key, value in dictionary.items():
        if str(key).startswith("$"):
            last_operation = key
            new_key = f"{parent_key}" if parent_key else ""
        else:
            new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, MutableMapping):
            items.extend(
                flatten_jsondiff_explicit_result(
                    value, new_key, separator=separator, last_operation=last_operation
                ).items()
            )
        else:
            items.append((f"{last_operation}{separator}{new_key}", value))
    return dict(items)


def create_json_patch_document(flatten_dict: dict, exclude_properties: list[str] | None = None) -> str:
    """Creates JSON document compliant with JSON Path format standard.

    Args:
        flatten_dict: Dictionary with flatted keys to values returned by ``flatten_jsondiff_explicit_result``.
        exclude_properties: List of flatten key paths for properties to exclude from patch document.

    Returns:
        A string representing JSON Path format document.
    """
    if exclude_properties is None:
        exclude_properties = list()

    exclude_properties_lower = list(map(lambda s: s.lower(), exclude_properties))
    operations = []

    for k, v in flatten_dict.items():
        path = k[k.find("/") :]

        if path.lower() in exclude_properties_lower:
            continue

        operation = map_operations(k[: k.find("/")], path, v)
        operations.extend(operation.value)

    return json.dumps(sorted(operations, key=operation_weight_sort_key))


class Operation(ABC):
    """Represent single operation acceptable by JSON Patch Format."""

    def __init__(self, path: str, raw_data: list | dict | object) -> None:
        """Initialize Operation class with private attributes.

        Args:
            path: Flatten key path.
            raw_data: Value for given key, format defined by ``json.diff``.
        """
        self._path = path
        self._raw_data = raw_data

    @property
    @abstractmethod
    def value(self) -> list[dict]:
        """Returns list with JSON Path format operation objects."""
        raise NotImplementedError


class AddOperation(Operation):
    """Creates operations for adding objects."""

    @property
    def value(self) -> list[dict]:
        """Returns list with JSON Path format operation objects."""
        result = []
        if isinstance(self._raw_data, list):
            for add_object in self._raw_data:
                index = add_object[0]
                value = add_object[1]
                result.append({"op": "add", "path": f"{self._path}/{index}", "value": value})
        else:
            result.append(
                {
                    "op": "add",
                    "path": self._path,
                    "value": self._raw_data,
                }
            )
        return result


class RemoveOperation(Operation):
    """Creates operations for removing objects."""

    @property
    def value(self) -> list[dict]:
        """Returns list with JSON Path format operation objects."""
        result = []
        if isinstance(self._raw_data, list):
            for index in self._raw_data:
                result.append({"op": "remove", "path": f"{self._path}/{index}"})
        else:
            result.append(
                {
                    "op": "remove",
                    "path": self._path,
                }
            )
        return result


class ReplaceOperation(Operation):
    """Creates operations for replacing objects."""

    @property
    def value(self) -> list[dict]:
        """Returns list with JSON Path format operation objects."""
        result = [{"op": "replace", "path": self._path, "value": self._raw_data}]
        return result


def map_operations(op_name: str, path: str, raw_data: dict | list | object) -> Operation:
    """Maps an operation from the ``jsondiff`` library to  corresponding in the JSON Path format specification.

    Args:
        op_name: Operation name used in ``jsondiff`` library, prefixed with ``$``.
        path: Flatten key path.
        raw_data: Operation related information created by ``jsondiff`` library.

    Returns:
        An Operation object that performs the creation of the appropriate operation object.

    Raises:
        ValueError: If an undefined operation is provided.
    """
    op_name_lower = op_name.lower()

    if op_name_lower == "$update":
        return ReplaceOperation(path, raw_data)
    elif op_name_lower == "$insert":
        return AddOperation(path, raw_data)
    elif op_name_lower == "$delete":
        return RemoveOperation(path, raw_data)
    else:
        raise ValueError("Undefined operation!")


def operation_weight_sort_key(operation: dict) -> int:
    """Controls the order of operation execution.

    Args:
        operation: A JSON Path format operation dictionary.

    Returns:
        A weight for the given operation, which will be used when sorting.
    """
    op_weight_map = {
        "remove": 1,
        "add": 2,
        "replace": 3,
    }
    return op_weight_map[operation["op"]]
