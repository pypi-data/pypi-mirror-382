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
log.py

overall logging setup management
"""
import logging
import re
from json import load
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    NOTSET,
    WARNING,
    Logger,
    LogRecord,
    getLogger,
)
from logging.config import dictConfig
from pathlib import Path
from typing import Any, Optional, Union

import yaml
from yaml import SafeLoader

from eopf.config.config import EOConfiguration
from eopf.exceptions import (
    LoggingConfigurationDirDoesNotExist,
    LoggingConfigurationFileTypeNotSupported,
    LoggingConfigurationNotRegistered,
    LoggingDictConfigurationInvalid,
)
from eopf.exceptions.warnings import (
    LoggingDictConfigurationIsNotValid,
    LoggingLevelIsNoneStandard,
    NoLoggingConfigurationFile,
)

DEFAULT_CFG_DIR = Path(__file__).parent / "conf"

EOConfiguration().register_requested_parameter(
    "logging__folder",
    param_is_optional=True,
    default_value=DEFAULT_CFG_DIR,
    description="Folder to look for json/yaml logging dictConfig files ",
)
EOConfiguration().register_requested_parameter(
    "logging__level",
    param_is_optional=True,
    default_value="WARNING",
    description="Default logging level",
)
EOConfiguration().register_requested_parameter(
    "logging__dask_level",
    param_is_optional=True,
    description="Default logging level for dask loggers",
)
EOConfiguration().register_requested_parameter(
    "logging__obfuscate",
    param_is_optional=True,
    default_value=True,
    description="Obfuscate or not the sensitive elements : password;usernam etc",
)
EOConfiguration().register_requested_parameter(
    "logging__load_default",
    param_is_optional=True,
    default_value=False,
    description="Load the default logging config",
)
EOConfiguration().register_requested_parameter(
    "logging__disable_existing_loggers",
    param_is_optional=True,
    default_value=True,
    description="Disable existing loggers before setting up, same default as per dictConfig",
)


class PasswordFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        record.msg = obfuscate_passwords(record.getMessage())
        return True


SENSITIVE_TAGS = ["password", "pwd", "passphrase", "api_token", "username", "key", "secret"]


def obfuscate_passwords(text: str, mask: str = "****") -> str:
    """
    Obfuscates sensitive data in a given string.
    Supports common formats like key-value pairs and JSON-like structures.

    Parameters
    ----------
    text: str
        the input string containing sensitive data.
    mask: str
        the mask to replace sensitive data with (default: "****").

    Returns
    --------
    The string with sensitive data obfuscated.
    """
    # Regular expression to match sensitive data patterns with optional quotes
    sensitive_pattern = rf'(["\']?({"|".join(SENSITIVE_TAGS)})["\']?\s*[:=]\s*["\']?)([^"\'\s]+)(["\']?)'

    text = re.sub(sensitive_pattern, lambda m: m.group(1) + mask + m.group(4), text)

    return text


class EOLogging:
    """A factory singleton generating Python Logger based on given configuration"""

    DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s : [%(levelname)s] %(module)s : %(funcName)s :: %(message)s"
    DEFAULT_LOG_LEVEL = logging.INFO
    """Default directory containing configurations"""

    _instance: Optional["EOLogging"] = None
    _initialized: bool = False

    def __init__(self) -> None:
        """Initializes by registering logger configurations in the ``cfg_dir``

        Raises
        ----------
        LoggingConfigurationDirDoesNotExist
            When the preset or given logging directory does not exist
        """

        if not EOLogging._initialized:
            self.default_cfg_dir: Optional[Path] = None
            """path to the directory containing logger configurations"""
            self._cfgs: dict[str, Path] = {}
            """dictionary of logger configurations"""
            EOLogging._initialized = True
            self.register_default_conf = EOConfiguration().logging__load_default
            self.default_conf_loaded = False
            EOLogging._set_dask_loggers_level()

    def __new__(cls) -> "EOLogging":
        """Ensures there is only one object of EOLogFactory (singleton)"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def disable_default_conf(self) -> None:
        """
        Disable the loading of the default conf in the cfg_dir folder
        Returns
        -------

        """
        self.register_default_conf = False

    def enable_default_conf(self) -> None:
        """
        Enable the loading of the default conf in the cfg_dir folder
        Returns
        -------

        """
        self.register_default_conf = True
        self.default_conf_loaded = False

    @property
    def config_dict(self) -> dict[str, Path]:
        """
        Returns
        -------
        The dictionary of loaded files
        """
        return self._cfgs

    @staticmethod
    def setup_basic_config(
        level: Optional[int] = None,
        format: Optional[str] = None,
        file: Optional[str] = None,
    ) -> None:
        """
        Setup a basic config
        Wrapper of logging.basicConfig

        Parameters
        ----------
        level
        format
        file

        Returns
        -------

        """

        if format is None:
            format_str = EOLogging.DEFAULT_LOG_FORMAT
        else:
            format_str = format
        # override the logging level from the cfg file
        if level and level != NOTSET:
            if level not in [DEBUG, INFO, WARNING, ERROR, CRITICAL]:
                raise LoggingLevelIsNoneStandard(
                    "The given log level is register_requested_parameter to a value which is none Python standard",
                )
        elif EOConfiguration().has_value("logging__level"):
            level = logging.getLevelName(EOConfiguration().logging__level)
            if level not in [DEBUG, INFO, WARNING, ERROR, CRITICAL]:
                raise LoggingLevelIsNoneStandard(
                    "The given log level is register_requested_parameter to a value which is none Python standard",
                )
        else:
            level = EOLogging.DEFAULT_LOG_LEVEL
        if file is not None:
            logging.basicConfig(level=level, format=format_str, filename=file)
        else:
            logging.basicConfig(level=level, format=format_str)

    def reset(self) -> None:
        """
        Clear all the logging configuration
        Beware : if someone still has a reference to the logger it  will not be destroyed by the garbage collect
        but will no longer have handlers
        Returns
        -------

        """
        self.default_conf_loaded = False
        self._cfgs = {}
        # Iterate through all loggers and their handlers
        for logger in logging.Logger.manager.loggerDict.values():
            if isinstance(logger, logging.Logger):
                # Close and remove handlers associated with the logger
                for handler in logger.handlers:
                    handler.close()
                    logger.removeHandler(handler)

        # Clear the logger hierarchy by removing all loggers from the logger dictionary
        logging.Logger.manager.loggerDict.clear()

    def set_default_cfg_dir(self, url: Optional[Union[str, Path]]) -> None:
        """Set the ``cfg_dir`` parameter, remove old configurations and add those in the new ``cfg_dir``

        Parameters
        ----------
        url: Union[str, Path]
            path to a directory containing logger configurations

        Raises
        ----------
        LoggingConfigurationDirDoesNotExist
            When the preset or given logging directory does not exist
        """

        if url is None:
            # Set the default config dir according to the eopf configuration folder if none given
            self.default_cfg_dir = self.get_default_cfg_dir()
        elif not isinstance(url, Path):
            self.default_cfg_dir = Path(url)
        else:
            self.default_cfg_dir = url
        if not self.default_cfg_dir.is_dir():
            raise LoggingConfigurationDirDoesNotExist("The logging configuration directory must exist")
        self.enable_default_conf()
        self.register_cfg_dir(self.default_cfg_dir, True)

    def get_default_cfg_dir(self) -> Path:
        """
        Get the default config dir used to load default config files
        Returns
        -------
        the dir used
        """
        if self.default_cfg_dir is None:
            conf = EOConfiguration()
            if conf.has_value("logging__folder"):
                self.default_cfg_dir = Path(conf.logging__folder)
            else:
                self.default_cfg_dir = DEFAULT_CFG_DIR
        return self.default_cfg_dir

    def register_cfg(self, cfg_name: str, cfg_path: Union[Path, str]) -> None:
        """Register a logger configuration by name and path

        Parameters
        ----------
        cfg_name: str
            name of the logger configuration

        cfg_path: Union[Path, str]
            path of the logger configuration

        Raises
        ----------
        FileNotFoundError
            When a file is not found at given location
        LoggingConfigurationFileTypeNotSupported
            When the logging file name does not have a .json extension
        """

        # if the configuration does not exists register it
        if cfg_name not in self._cfgs:
            if not isinstance(cfg_path, Path):
                cfg_file_path = Path(cfg_path)
            else:
                cfg_file_path = cfg_path
            if not cfg_file_path.is_file():
                raise FileNotFoundError(f"File {cfg_file_path} can not be found")
            if cfg_file_path.suffix not in [".json", ".yaml"]:
                raise LoggingConfigurationFileTypeNotSupported("Unsupported configuration file type")
            if cfg_file_path.suffix == ".json":
                # load_file the json configuration
                try:
                    logging.debug(f"Registering logging config for {cfg_name} with file {cfg_file_path}")
                    with open(cfg_file_path, "r", encoding="utf-8") as f:
                        json_cfg = load(f)
                        EOLogging._dict_cfg(json_cfg)
                        self._cfgs[cfg_name] = cfg_file_path
                except Exception as e:
                    raise LoggingDictConfigurationInvalid(
                        f"Can not setup dict given logging configuration due to: {e} in file {cfg_file_path}",
                    ) from e
            elif cfg_file_path.suffix == ".yaml":
                # load_file the json configuration
                try:
                    logging.debug(f"Registering logging config for {cfg_name} with file {cfg_file_path}")
                    with open(cfg_file_path, "r", encoding="utf-8") as f:
                        yaml_cfg = yaml.load(f, Loader=SafeLoader)
                        EOLogging._dict_cfg(yaml_cfg)
                        self._cfgs[cfg_name] = cfg_file_path
                except Exception as e:
                    raise LoggingDictConfigurationInvalid(
                        f"Can not setup dict given logging configuration due to: {e} in file {cfg_file_path}",
                    ) from e

    def register_cfg_dir(self, cfg_dir: Path, mandatory: bool = False) -> None:
        """

        Parameters
        ----------
        cfg_dir : directory to load_file from
        mandatory : flag if the dir should mandatory have conf file in it

        Returns
        -------
        None
        """
        # register the configurations in the cfg_dir
        configuration_present = False
        if cfg_dir is not None:
            # root logger prevails
            for cfg_path in cfg_dir.glob("root*.json"):
                configuration_present = True
                self.register_cfg(cfg_path.stem, cfg_path)
            for cfg_path in cfg_dir.glob("*.json"):
                configuration_present = True
                self.register_cfg(cfg_path.stem, cfg_path)
            for cfg_path in cfg_dir.glob("*.yaml"):
                configuration_present = True
                self.register_cfg(cfg_path.stem, cfg_path)

        if not configuration_present and mandatory:
            raise NoLoggingConfigurationFile(
                f"No logging configuration file .json/.yaml is present in {self.default_cfg_dir}",
            )

    @staticmethod
    def _dict_cfg(cfg: dict[Any, Any]) -> None:
        """Setting a logger configuration by providing a config dict

        Parameters
        ----------
        cfg: dict
            dictionary containing the logger configuration

        Raises
        ----------
        LoggingDictConfigurationIsNotValid
            When the provided configuration is not valid

        """

        try:
            # Default to not disable existing loggers. Loggers are removed by us if logger__disable_existing_loggers
            # EOConfiguration is set
            cfg.setdefault("disable_existing_loggers", EOConfiguration().logging__disable_existing_loggers)
            dictConfig(cfg)
        except Exception as e:
            raise LoggingDictConfigurationIsNotValid(f"Invalid configuration, reason: {e}") from e

    def get_cfg_path(self, cfg_name: str) -> Path:
        """Retrieve a logger configuration path by its name

        Parameters
        ----------
        cfg_name: str
            name of the logger configuration

        Raises
        ----------
        LoggingConfigurationNotRegistered
            When a given logging configuration name is not registered
        """

        if cfg_name not in self._cfgs:
            raise LoggingConfigurationNotRegistered(f"No log configuration {cfg_name} is registered")
        return self._cfgs[cfg_name]

    def get_logger(
        self,
        name: str = "eopf",
        level: Optional[int] = None,
    ) -> Logger:
        """Retrieve a logger by specifying the name of the configuration
        and register_requested_parameter the logger's level
        Warning : this will register_requested_parameter the level for all code having this logger

        Parameters
        ----------
        name: str
            name of the logger or actual configuration dictionary

        level: int
            logger level

        Raises
        ----------
        LoggingConfigurationFileIsNotValid
            When a given logging configuration file .conf/.yaml cannot be applied
        """

        # if not init try to init with defaults
        if not self.default_conf_loaded and self.register_default_conf:
            self.set_default_cfg_dir(url=None)
        # if the requested logger is defined in the config file it will be returned else a new one will be created with
        # a default config
        logger = getLogger(name)
        # override the logging level from the cfg file
        if level is not None:
            logger.setLevel(level=level)
        elif EOConfiguration().has_value("logging__level"):
            level_str: str = str(EOConfiguration().logging__level).upper()
            logger.setLevel(level_str)
        if EOConfiguration().logging__obfuscate and not any(isinstance(f, PasswordFilter) for f in logger.filters):
            logger.addFilter(PasswordFilter())
        return logger

    @staticmethod
    def _set_dask_loggers_level() -> None:
        if EOConfiguration().has_value("logging__dask_level"):
            dask_logging_level = EOConfiguration().logging__dask_level
            dask_logger_prefixes = ["distributed", "dask"]
            logger_dict = logging.root.manager.loggerDict
            for name, logger in logger_dict.items():
                if isinstance(logger, logging.Logger) and any(name.startswith(p) for p in dask_logger_prefixes):
                    logger.setLevel(dask_logging_level)
