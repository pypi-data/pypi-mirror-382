#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing configuration class, useful for legacy+platform streamsets objects."""

import json
import warnings
from collections.abc import Iterable


class Configuration:
    """Abstraction for configurations.

    This class enables easy access to and modification of data stored as a list of dictionaries. A Configuration is
    stored in the form:

    .. code-block:: none

        [{"name" : "<name_1>","value" : "<value_1>"}, {"name" : "<name_2>", value" : "<value_2>"},...]

    However, the passed in configuration parameter can be a list of Configurations such as:

    .. code-block:: none

        [[{"name" : "<name_1>","value" : "<value_1>"}, {"name" : "<name_2>", value" : "<value_2>"},...],
        [{"name" : "<name_3>","value" : "<value_3>"}, {"name" : "<name_4>", value" : "<value_4>"},...],...]
    """

    # Use an uber secret class attribute to specify whether other attributes can be assigned by __setattr__.
    __frozen = False

    def __init__(
        self,
        configuration: dict | list[dict] | None = None,
        compatibility_map: dict | None = None,
        property_key: str = "name",
        property_value: str = "value",
        id_to_remap: dict | None = None,
    ) -> None:
        """The __init__ for the configuration class.

        Args:
            configuration: The configuration to represent with this class.
            compatibility_map: Any backwards compatibility map for older version of things
            property_key: The key on which a configuration's key exists
            property_value: The key on which a configuration's value exists
            id_to_remap: If we want to change certain names of configurations
        """
        # Apply overrides to initial data
        if compatibility_map:
            for configuration_entry in configuration:
                configuration_name = configuration_entry.get(property_key)
                configuration_value = configuration_entry.get(property_value)

                if configuration_name in compatibility_map:
                    overrides = compatibility_map[configuration_name]
                    override_values = overrides.get("values", {})

                    configuration_entry[property_key] = overrides["name"]

                    if configuration_value in override_values:
                        configuration_entry[property_value] = override_values[configuration_value]
                        warnings.warn(
                            "Configuration {}={} has been deprecated. Please use {}={} instead.".format(
                                configuration_name,
                                configuration_value,
                                overrides["name"],
                                override_values[configuration_value],
                            ),
                            DeprecationWarning,
                        )
                    else:
                        warnings.warn(
                            "Configuration {} has been deprecated. Please use {} instead.".format(
                                configuration_name, overrides["name"]
                            ),
                            DeprecationWarning,
                        )

        self._compatibility_map = compatibility_map or {}
        self.property_key = property_key
        self.property_value = property_value

        self._id_to_remap = id_to_remap or {}

        # Ensure the input 'configuration' is properly formatted, handling both single configurations and lists.
        self._data = [configuration] if isinstance(configuration[0], dict) else configuration
        self._configuration_index_map = self._create_configuration_index_map()

        self.__frozen = True

    def _create_configuration_index_map(self) -> dict:
        """Creates a mapping {config_item_name: (config_item_index, config_list_index)} for efficient lookups."""
        configuration_index_map = {}
        for config_list_index, config_list in enumerate(self._data):
            if not isinstance(config_list, list):
                raise TypeError("Please pass in a list of configurations")

            for config_item_index, config_item in enumerate(config_list):
                if not isinstance(config_item, dict):
                    raise TypeError("A Configuration must be a list of dictionaries")
                if self.property_key not in config_item:
                    raise TypeError(f"Configuration {config_item} does not contain property_key:{self.property_key}")
                configuration_index_map[config_item[self.property_key]] = (config_item_index, config_list_index)

        return configuration_index_map

    def __getattr__(self, key: str) -> any:
        """Gets the configuration key as an attribute."""
        if not self.__frozen:
            super().__getattr__(key)
            return

        return self.__getitem__(key)

    def __getitem__(self, key: str) -> any:
        """Gets the configuration key as an item."""
        if key in self._id_to_remap:
            key = self._id_to_remap[key]

        if key not in self._configuration_index_map:
            raise AttributeError(key)

        index, configuration_index = self._configuration_index_map[key]
        config = self._data[configuration_index][index]
        return self._convert_value(config)

    def __setattr__(self, key: str, value: any) -> None:
        """Sets a configuration value as an attribute."""
        self.__setitem__(key, value)

    def __setitem__(self, key: str, value: any) -> None:
        """Sets a configuration value as an item."""
        if not self.__frozen:
            super().__setattr__(key, value)
            return

        if key in self._id_to_remap:
            key = self._id_to_remap[key]

        if key in self._compatibility_map:
            overrides = self._compatibility_map[key]
            if "values" in overrides and value in self._compatibility_map[key]["values"]:
                warnings.warn(
                    "Deprecation warning: Configuration {}={} is deprecated on this engine version. "
                    "Updating value to {}={}.".format(key, value, overrides["name"], overrides["values"][value]),
                    DeprecationWarning,
                )
                value = overrides["values"][value]
            else:
                warnings.warn(
                    "Configuration {} has been deprecated. Please use {} instead.".format(key, overrides["name"]),
                    DeprecationWarning,
                )

            key = overrides["name"]

        if key not in self._configuration_index_map:
            raise AttributeError(key)

        index, configuration_index = self._configuration_index_map[key]
        config = self._data[configuration_index][index]

        config[self.property_value] = value

    def __contains__(self, item: str) -> bool:
        """Checks if a configuration contains a particular key."""
        return item in self._id_to_remap or item in self._configuration_index_map

    def __repr__(self) -> str:
        """Representation of a configuration."""
        configs = {}
        for configuration in self._data:
            for config in configuration:
                key = config[self.property_key]
                configs[key] = self._convert_value(config)

        # If a key has a remapped key, delete the original key and add the remapped key into configs
        for remapped_key, original_key in self._id_to_remap.items():
            if original_key != remapped_key and original_key in configs:
                configs[remapped_key] = configs[original_key]
                del configs[original_key]

        return "{{{}}}".format(", ".join(f"'{k}': {v}" for k, v in configs.items()))

    def __dir__(self) -> list:
        """The dir of the configuration."""
        id_to_remap_cleaned = [key for key in self._id_to_remap.keys() if " " not in key]
        return sorted(list(dir(object)) + list(self.__dict__.keys()) + id_to_remap_cleaned)

    def items(self) -> Iterable[tuple]:
        """Gets the configuration's items."""
        configuration_dict = {}
        for configuration in self._data:
            for config in configuration:
                configuration_dict[config[self.property_key]] = self._convert_value(config)

        for config_property in self._id_to_remap:
            key = self._id_to_remap[config_property]
            if key in configuration_dict:
                configuration_dict[config_property] = configuration_dict[key]
                del configuration_dict[key]
        return configuration_dict.items()

    def get(self, key: str, default: any = None) -> any:
        """Return the value of key or, if not in the configuration, the default value."""
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, configs: dict) -> None:
        """Update instance with a collection of configurations.

        Args:
            configs: Dictionary of configurations to use.
        """
        for key, value in configs.items():
            self[key] = value

    def _convert_value(self, config: dict) -> any:
        if config.get("type") == "boolean":
            return json.loads(config[self.property_value])
        elif config.get("type") == "integer":
            return int(config[self.property_value])
        else:
            return config.get(self.property_value, None)
