#
# Copyright (C) 2025 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
config.py

Overall singleton configuration implementation


"""
import configparser
import enum
import json
import logging
import os
from collections.abc import MutableMapping
from typing import Any, Callable, Dict, Literal, Optional, Sequence, Set, Tuple

import toml
import yaml

from eopf.common.constants import EOPF_CPM_DEFAULT_CONFIG_FILE
from eopf.common.functions_utils import expand_env_var_in_dict
from eopf.common.type_utils import Singleton
from eopf.exceptions.errors import (
    InvalidConfigurationError,
    MissingConfigurationParameterError,
)


class ConfigFileType(enum.Enum):
    """
    Hold the possible types for config files
    """

    TOML = ".toml"
    INI = ".ini"
    JSON = ".json"
    YAML = ".yaml"


SUB_DICT_SEPARATOR = "__"
ENVIRON_PREFIX = "EOPF_"


class EOConfiguration(metaclass=Singleton):
    """Store and manage current configurations parameters

    Dict parameters coming from config files or dict are flattened and sublevel is separated with a __:
     { logging : {level : "DEBUG" } will become logging__level = "DEBUG"

    To register a parameter :
    EOConfiguration().register_requested_parameter("logging__level", default_value="DEBUG")

    To load a file:
    EOConfiguration().load_file("toto.toml")

    To load a file:
    EOConfiguration().load_file("toto.toml")

    To check if a parameter has a value:
    EOConfiguration().has_value("logging__level")

    To get the value of a parameter and throw is not register_requested_parameter:
    EOConfiguration().get("logging__level",throws=True)

    To reset all the configurations:
     conf.clear_loaded_configurations()

    To load_file an additional configuration file:
     conf.load_file("file.ini", ConfigType.INI)

     Internal naming convention is with . for sub elements


    """

    _reserved_parameters: list[str] = ["CONFIGURATION_FOLDER"]

    def __init__(self) -> None:
        self._loader: dict[ConfigFileType, Callable[[str, str], None]] = {
            ConfigFileType.TOML: self._load_toml,
            ConfigFileType.INI: self._load_ini,
            ConfigFileType.JSON: self._load_json,
            ConfigFileType.YAML: self._load_yaml,
        }
        self._secrets_file_list: Set[str] = set()
        self._secrets: dict[str, dict[Any, Any]] = {}
        self._config_internal: dict[str, Any] = {}

        self._param_file_list: Set[str] = set()
        self._registered_params: Dict[str, Tuple[str, Any, bool, Optional[str]]] = {}
        self._param_list_requested_mandatory: Set[str] = set()
        self._param_list_requested_optional: Set[str] = set()

        # Load the default installed
        if "EOPF_CONFIGURATION_FOLDER" in os.environ:
            try:
                self.load_file(os.path.join(os.environ["EOPF_CONFIGURATION_FOLDER"], "eopf.toml"))
            except InvalidConfigurationError as e:
                raise InvalidConfigurationError(
                    f"EOPF_CONFIGURATION_FOLDER env var provided has invalid eopf.toml file in it : {e}",
                ) from e
        else:
            self.load_file(EOPF_CPM_DEFAULT_CONFIG_FILE.path)

    def __getattr__(self, item: str) -> Any:
        try:
            # Refresh from environ if updated
            self._load_environ()
            return self.__getitem__(item)
        except AttributeError as e:
            raise MissingConfigurationParameterError(
                f"Missing configuration parameter {item} in files {self._param_file_list}, "
                f"availables : {self.param_list_available}",
            ) from e

    def __getitem__(self, item: str) -> Any:
        keys = EOConfiguration.to_internal_naming_convention(item).split(".")
        result = self._config_internal
        try:
            for k in keys:
                result = result[k]
        except KeyError as e:
            raise MissingConfigurationParameterError(
                f"No {item} in EOConfiguration : {self.param_list_available}",
            ) from e
        return result

    def __delitem__(self, key: str) -> None:
        keys = EOConfiguration.to_internal_naming_convention(key).split(".")
        result = self._config_internal
        for i, k in enumerate(keys):
            if i == len(keys) - 1:
                result.pop(k)
            else:
                result = result[k]

    def __setitem__(self, key: str, value: Any) -> None:
        key = EOConfiguration.to_internal_naming_convention(key)
        keys = key.split(".")
        EOConfiguration.__assign(keys, value, self._config_internal)

    @staticmethod
    def __assign(
        keys: Sequence[str],
        value: Any,
        d: dict[str, Any],
        policy: Literal["old", "new"] = "new",
    ) -> None:
        key = EOConfiguration.to_internal_naming_convention(keys[0])

        if len(keys) == 1 and (policy == "new" or key not in d):
            d[key] = value
        else:
            d.setdefault(key, {})
            EOConfiguration.__assign(keys[1:], value, d[key])

    def secrets(self, secret_name: Optional[str] = None) -> dict[str, Any]:
        """
        Return the secret dict for the secret name where keys are the first level groups:
        For example if you loaded a json file containing ::

            {
            "common" : {
                            "key" : "key",
                            "secret" : "<SECRET>",
                            "endpoint_url" : "<URL>",
                            "region_name" : "<REGION>"
                        },
            "cpm-input" : {
                            "key" : "key",
                            "secret" : "<SECRET>",
                            "endpoint_url" : "<URL>",
                            "region_name" : "<REGION>"
                        }
            }

        If not found for the name will throw an exception


        """
        if secret_name:
            if secret_name not in self._secrets:
                raise MissingConfigurationParameterError(
                    f"Missing secret {secret_name} in secret files {self._secrets_file_list}",
                )
            return self._secrets[secret_name]
        return self._secrets

    @property
    def param_list_available(self) -> Set[str]:
        """
        Get the list of all available parameters loaded in conf either from a file or from the user
        Convention is with __ for sub dicts

        Returns
        -------
        The list of available params

        """
        ret: Set[str] = set()
        self.__get_sub_keys(self._config_internal, ret, "")
        return ret

    def __get_sub_keys(self, d: MutableMapping[str, Any], s: Set[str], p: str) -> None:
        prefix = p + "__" if p != "" else ""
        if isinstance(d, MutableMapping):
            if p != "":
                s.add(p)
            for k, v in d.items():
                self.__get_sub_keys(v, s, prefix + k)
        else:
            s.add(p)

    def mandatory_list(self, prefix: str = "") -> Set[str]:
        """
        Get the list of mandatory parameters registered

        Parameters
        ----------
        prefix: str

        Example
        --------
        To get only the logging parameters do::

                EOConfiguration().mandatory_list("logging")

        Returns
        -------
        The list of mandatory parameters for the suffix

        """
        return {k for k in self._param_list_requested_mandatory if k.startswith(prefix)}

    def optional_list(self, prefix: str = "") -> Set[str]:
        """
        Get the list of optional parameters registered
        Parameters
        ----------
        prefix: The prefix to search for. For example to get only the logging parameters do
                EOConfiguration().mandatory_list("logging")

        Returns
        -------
        The list of mandatory parameters for the suffix
        """
        return {k for k in self._param_list_requested_optional if k.startswith(prefix)}

    def load_secret_file(self, secret_file: str) -> None:
        """
        Parse a secret JSON file and add these params to the SECRETS__ group or params

        """
        try:
            with open(secret_file, "r", encoding="utf-8") as fid:
                secrets = expand_env_var_in_dict(json.load(fid))

            self._secrets.update(secrets)
        except Exception as e:
            raise InvalidConfigurationError(f"Error loading secret file {secret_file} : {e}") from e

    def load_file(
        self,
        config_file: str,
        file_config_type: Optional[ConfigFileType] = None,
        prefix: str = "",
    ) -> None:
        """Parse and load_file the given configuration file

        Parameters
        ----------
        config_file: Union[str, Mapping[str, Any]]
            path to config file that store settings
        file_config_type: ConfigFileType, optional
            type of the config file given if not provided will use extension to define format
        prefix: prefix to register the file with, for example for logging params "logging__"

        Return
        ------
        None
        """

        try:
            logging.info(f"Registering EOConfig file : {config_file}")
            if file_config_type is not None:
                self._loader[file_config_type](config_file, prefix)
            else:
                extension = os.path.splitext(config_file)[1]
                found: bool = False
                for config_type in ConfigFileType:
                    if config_type.value == extension:
                        self._loader[config_type](config_file, prefix)
                        found = True
                if not found:
                    raise InvalidConfigurationError(f"No loader found for {config_file}")
            self._param_file_list.add(config_file)
        except Exception as e:
            raise InvalidConfigurationError(f"Error loading configuration file {config_file} : {e}") from e
        # Env always prevails
        self._load_environ()

    @staticmethod
    def __update_dict(
        config_to_update: dict[str, Any],
        new_dict: dict[str, Any],
        policy: Literal["old", "new"] = "new",
    ) -> dict[str, Any]:
        """

        Update a nested dictionary with values from another

        This is like dict.update except that it smoothly merges nested values

        Parameters
        ----------
        policy: string {'old', 'new'}
            If new (default) then the new dictionary has preference.
            Otherwise the old dictionary does.

        """
        for k, v in new_dict.items():
            k = EOConfiguration.to_internal_naming_convention(k)

            if isinstance(v, dict):
                if (
                    k not in config_to_update
                    or config_to_update[k] is None
                    or not isinstance(config_to_update[k], dict)
                ):
                    config_to_update[k] = {}
                EOConfiguration.__update_dict(
                    config_to_update[k],
                    v,
                    policy=policy,
                )
            else:
                EOConfiguration.__assign(k.split("."), v, config_to_update, policy)

        return config_to_update

    def load_dict(
        self,
        entry_dict: dict[str, Any],
        prefix: str = "",
        policy: Literal["new", "old"] = "new",
    ) -> None:
        """
        Load a dict into the config
        Parameters
        ----------
        policy
        entry_dict : A dict to load
        prefix: prefix to register the dict with, for example for logging params "logging__"

        Return
        ------
        None
        """
        config_dict_to_modify = self._config_internal
        if prefix != "":
            for key in EOConfiguration.to_internal_naming_convention(prefix).split("."):
                config_dict_to_modify.setdefault(key, {})
                config_dict_to_modify = config_dict_to_modify[key]

        EOConfiguration.__update_dict(config_dict_to_modify, entry_dict, policy=policy)

    def register_requested_parameter(
        self,
        name: str,
        default_value: Optional[Any] = None,
        param_is_optional: bool = False,
        description: Optional[str] = None,
    ) -> None:
        """

        Parameters
        ----------
        description
        name
        default_value : default value to set if nobody provides this value
        param_is_optional : optional or not ?

        Returns
        -------
        Nothing
        """
        internal_name = EOConfiguration.to_internal_naming_convention(name)
        if internal_name in self._registered_params:
            self._param_list_requested_optional.discard(internal_name)
            self._param_list_requested_mandatory.discard(internal_name)
        param_tuple = (
            internal_name,
            default_value,
            param_is_optional or default_value is not None,
            description if description is not None else "",
        )
        # Keep the track of user setting not to clean them at reset
        self._registered_params[internal_name] = param_tuple
        # No default values
        if default_value is None:
            if param_is_optional:
                self._param_list_requested_optional.add(internal_name)
            else:
                self._param_list_requested_mandatory.add(internal_name)
        else:
            # params with default value are always considered optional
            self._param_list_requested_optional.add(internal_name)
            # Happens that there is already a provider of this one, so don't overload
            if not self.has_value(internal_name):
                self[internal_name] = default_value

    def has_value(self, param_name: str) -> bool:
        """
        Test if the param_name has a value in the config
        Parameters
        ----------
        param_name: The name of the param in canonical form i.e with subgroup separated by __or .

        Returns
        -------
        True if either a file or a user has fill a value for this param

        """
        res = EOConfiguration.to_internal_naming_convention(param_name) in [
            EOConfiguration.to_internal_naming_convention(x) for x in self.param_list_available
        ]
        return res

    def get(self, param_name: str, default: Any = None, throws: bool = False) -> Optional[Any]:
        """
        Get the value of a param.
        If throws==True and no value is available then will throw a MissingConfigurationParameter error
        If throws==False will simply return None

        Parameters
        ----------
        default : default value to return if not found, will also set the value
        param_name: The name of the param in canonical form i.e with subgroup separated by __
        throws: flag to throw or not in case of unavailable value

        Returns
        -------
        the value of the parameter or None is throws==False and no value registered in conf

        """

        try:
            return self[param_name]
        except MissingConfigurationParameterError:
            if throws:
                raise
            self[param_name] = default
            return default

    def validate_mandatory_parameters(self, prefix: str = "", throws: bool = True) -> bool:
        """
        Validate that all the mandatory parameters with "prefix" have a value in the configuration
        If throws==True will throw a Error exception,
        If not will simply return False

        Parameters
        ----------
        prefix: prefix for parameters to validate
        throws: flag to throw or not in case of unavailable value

        Returns
        -------
        the boolean flag: True if all params are available, False if not

        """

        for param in self.mandatory_list(prefix):
            try:
                self[param]
            except KeyError as e:
                if throws:
                    raise MissingConfigurationParameterError(
                        f"Missing parameter {param} in configuration files {self._param_file_list}",
                    ) from e
                return False
        # No one to say the contrary
        return True

    @classmethod
    def reset(cls) -> None:
        """
        Will completely reset the configuration state, all declared parameters will be deleted and all
        Returns
        -------

        """
        cls.clear()

    def clear_loaded_configurations(self) -> None:
        """
        Will clear_loaded_configurations all the configurations and states
        Basically only for testing purpose to reset state between tests

        Returns
        -------

        """
        self._config_internal = {}
        self._param_file_list = set()
        self._param_list_requested_mandatory = set()
        self._param_list_requested_optional = set()
        for (
            param_name,
            param_default_value,
            param_is_optional,
            description,
        ) in self._registered_params.values():
            self.register_requested_parameter(param_name, param_default_value, param_is_optional, description)

    def requested_params_description(self) -> Dict[str, Any]:
        """
        Export the list of requested params information to dict
        Parameters
        ----------

        Returns
        -------
        A dict with mandatory and optional sub element
        """
        out_dict: Dict[str, Any] = {"mandatory": {}, "optional": {}}
        for var in self._param_list_requested_optional:
            tuple_value = self._registered_params[var]
            out_dict["optional"][var] = {
                "name": tuple_value[0],
                "optional": tuple_value[2],
                "default": tuple_value[1],
                "description": tuple_value[3],
            }
        for var in self._param_list_requested_mandatory:
            tuple_value = self._registered_params[var]
            out_dict["mandatory"][var] = {
                "name": tuple_value[0],
                "optional": tuple_value[2],
                "default": tuple_value[1],
                "description": tuple_value[3],
            }

        return out_dict

    def _load_environ(self) -> None:
        for env_var, value in os.environ.items():
            if env_var.startswith(ENVIRON_PREFIX):
                self[env_var[len(ENVIRON_PREFIX) :].lower()] = value

    def _load_ini(self, filename: str, prefix: str = "") -> None:
        base_config_data = configparser.ConfigParser()
        base_config_data.read(filenames=[filename])
        self.load_dict(
            {s: dict(base_config_data.items(s)) for s in base_config_data.sections()},
            prefix,
        )

    def _load_toml(self, filename: str, prefix: str = "") -> None:
        with open(filename, encoding="utf-8") as f:
            base_config_data = toml.load(f)
        self.load_dict(base_config_data, prefix)

    def _load_json(self, filename: str, prefix: str = "") -> None:
        with open(filename, encoding="utf-8") as f:
            base_config_data = json.load(f)
        self.load_dict(base_config_data, prefix)

    def _load_yaml(self, filename: str, prefix: str = "") -> None:
        with open(filename, encoding="utf-8") as f:
            base_config_data = yaml.safe_load(f)
        self.load_dict(base_config_data, prefix)

    @staticmethod
    def to_internal_naming_convention(name: str) -> str:
        """
        internal naming convention is with . for sub elements
        Parameters
        ----------
        name

        Returns
        -------

        """
        return name.replace("-", "_").replace(SUB_DICT_SEPARATOR, ".")
