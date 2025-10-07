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
eo_qc_config.py

EOQC Configuration file handling

"""

import os
import re
from dataclasses import dataclass
from typing import Any, List, Mapping, Optional, Union

import dacite

import eopf.qualitycontrol.impl  # noqa
from eopf import EOLogging
from eopf.common.constants import EOPF_CPM_PATH
from eopf.common.file_utils import AnyPath, load_json_file
from eopf.common.functions_utils import nested_apply
from eopf.config.config import EOConfiguration
from eopf.exceptions.errors import (
    EOQCConfigMalformed,
    EOQCConfigMissing,
    EOQCInspectionMalformed,
    EOQCInspectionMissing,
)
from eopf.qualitycontrol.eo_qc import EOQC
from eopf.qualitycontrol.eo_qc_factory import EOQCFactory

# Warning do not remove it initialise the factory

EOConfiguration().register_requested_parameter(
    name="qualitycontrol__folder",
    default_value=os.path.join(EOPF_CPM_PATH.path, "qualitycontrol/config/"),
    description="path to the folder where checklist *.json and inspections *_inspections.json are stored",
)


@dataclass
class EOQCConfig:
    """
    EOQC Config definition

    """

    identifier: str
    product_type: str
    version: str
    inspection_dict: Mapping[str, EOQC]


class EOQCConfigBuilder:
    """Quality control configuration factory. It contains one or multiple quality control configuration.

    Attributes
    ----------
    _configs: list[EOQCConfig]
        The list of quality control configuration.
    """

    PATTERN_REPLACE = r"@@@(\w+)@@@"

    def __init__(self, config_folders: Optional[List[Union[AnyPath, str]]] = None) -> None:
        # logger
        self._logger = EOLogging().get_logger("eopf.quality_control.config")
        # Cache
        self._configs: dict[str, EOQCConfig] = {}
        self._inspections: dict[str, EOQC] = {}
        # Config
        self._qc_inspection_files: List[AnyPath] = []
        self._qc_config_files: List[AnyPath] = []
        # If set to None then no folder registered
        if config_folders is None:
            config_folders = [AnyPath.cast(EOConfiguration().qualitycontrol__folder)]
        for folder in config_folders:
            self.add_config_folder(folder)

    def add_config_folder(self, config_folder: Union[AnyPath, str]) -> None:
        """
        Add a new config folder to look for

        Parameters
        ----------
        config_folder : Union[AnyPath, str]

        Returns
        -------

        """
        self._logger.debug(f"Added EOQC config folder : {str(config_folder)}")
        config_anypath = AnyPath.cast(config_folder)
        if not config_anypath.exists() or not config_anypath.isdir():
            raise ValueError(f"No folder found under {config_anypath}")
        self._qc_config_files.extend(
            [j for j in config_anypath.glob("*json") if not j.path.endswith("_inspections.json")],
        )
        self._qc_inspection_files.extend(config_anypath.glob("*_inspections.json"))
        self._logger.debug(f"Loaded config files : {self._qc_config_files}")
        self._logger.debug(f"Loaded inspection files : {self._qc_inspection_files}")

    def get_qc_config(self, product_type: str, parameters: Optional[dict[str, Any]] = None) -> EOQCConfig:
        """Get all the quality control configuration for a specific product type.

        Parameters
        ----------
        parameters
        product_type: str
            The product type.

        Returns
        -------
        list[EOQCConfig]
            The list of quality control configuration for the parameter product type.
        """
        if product_type in self._configs:
            return self._configs[product_type]

        qc_config_dict = self._find_config(product_type)
        return self._load_config(qc_config_dict, parameters)

    def load_config(self, config_file: Union[AnyPath, str], parameters: Optional[dict[str, Any]] = None) -> EOQCConfig:
        """
        Directly load an EOQC config file, no product id lookup

        Parameters
        ----------
        parameters
        config_file : config file to load

        Returns
        -------
        EOQCConfig
        """
        config_content = load_json_file(config_file)
        if "product_type" not in config_content:
            raise EOQCConfigMalformed(f"No Product type info in {config_file}")
        if "inspection_list" not in config_content:
            raise EOQCConfigMalformed(f"No inspection_list found in {config_file}")

        return self._load_config(config_content, parameters=parameters)

    def _find_config(self, product_type: str) -> dict[str, Any]:
        """
        Find the config file corresponding to the product type, load it and return the dict
        Parameters
        ----------
        product_type : str

        Returns
        -------
        JSON of the config loaded as dict
        """
        for config_file in self._qc_config_files:
            config_content = load_json_file(config_file)
            if "product_type" not in config_content:
                raise EOQCConfigMalformed(f"No Product type info in {config_file}")
            if config_content["product_type"] == product_type:
                if "inspection_list" not in config_content:
                    raise EOQCConfigMalformed(f"No inspection_list found in {config_file}")
                self._logger.debug(f"Found config file {config_file} for {product_type}")
                return config_content
        raise EOQCConfigMissing(f"No config was found for product_type : {product_type} in {self._qc_config_files}")

    def _load_config(self, config_dict: dict[str, Any], parameters: Optional[dict[str, Any]] = None) -> EOQCConfig:
        """
        Load an EOQCConfig based on the dict content
        Parameters
        ----------
        config_dict

        Returns
        -------
        An EOQCConfig
        """
        inspection_id_list = config_dict["inspection_list"]
        inspection_dict = {}
        internal_parameters = {} if parameters is None else parameters
        for inspection_id in inspection_id_list:
            if inspection_id in self._inspections:
                inspection_dict[inspection_id] = self._inspections[inspection_id]
            else:
                inspection_json_base = self._find_inspection(inspection_id)
                try:
                    inspection_json = EOQCConfigBuilder._replace_parameters(
                        inspection_json_base,
                        parameters=internal_parameters,
                    )
                except KeyError as e:
                    raise KeyError(f"Missing replacement parameter for inspection {inspection_id} : {e}") from e
                if inspection_json["type"] == "group":
                    for sub_id in inspection_json["inspections"]:
                        sub_inspection_dict_base = self._find_inspection(sub_id)
                        try:
                            sub_inspection_dict = EOQCConfigBuilder._replace_parameters(
                                sub_inspection_dict_base,
                                parameters=internal_parameters,
                            )
                        except KeyError as e:
                            raise KeyError(f"Missing replacement parameter for inspection {sub_id} : {e}") from e
                        sub_inspection_type = EOQCFactory.get_eoqc_type(sub_inspection_dict["type"])
                        sub_inspection = dacite.from_dict(sub_inspection_type, sub_inspection_dict)
                        inspection_dict[sub_id] = sub_inspection
                else:
                    inspection_type = EOQCFactory.get_eoqc_type(inspection_json["type"])
                    inspection = dacite.from_dict(inspection_type, inspection_json)
                    inspection_dict[inspection_id] = inspection

        return EOQCConfig(
            product_type=config_dict["product_type"],
            version=config_dict["version"],
            identifier=config_dict["identifier"],
            inspection_dict=inspection_dict,
        )

    def _find_inspection(self, inspection_id: str) -> dict[str, Any]:
        for inspection_file in self._qc_inspection_files:
            inspection_content = load_json_file(inspection_file)
            if "quality_inspections" not in inspection_content:
                raise EOQCInspectionMalformed(f"No quality_inspection list in {inspection_file}")
            for inspection in inspection_content["quality_inspections"]:
                if inspection["identifier"] == inspection_id:
                    return inspection

        raise EOQCInspectionMissing(f"No inspection was found for identifier : {inspection_id}")

    @staticmethod
    def _replace_parameters(config_dict: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:

        def replace_with_dict_value(text: Any) -> Any:
            if isinstance(text, str):
                match = re.fullmatch(EOQCConfigBuilder.PATTERN_REPLACE, text)
                if match:
                    key = match.group(1)  # Extract the key (FOO from @@@FOO@@@)
                    return parameters[key]  # Replace with dict value or leave as is
            return text

        # Substitute all placeholders in the text
        return nested_apply(config_dict, replace_with_dict_value)

    @staticmethod
    def detect_replace_symbol(data: Any) -> bool:
        """
        Recursively checks if any string in a nested dictionary, list, or other structure
        contains the substring '@@@'.
        :param data: The data to inspect (can be dict, list, or other structures).
        :return: True if any string contains '@@@', False otherwise.
        """
        if isinstance(data, str):
            return re.fullmatch(EOQCConfigBuilder.PATTERN_REPLACE, data) is not None  # Check if the string contains @@@
        if isinstance(data, dict):
            # Check recursively for all values in the dictionary
            return any(EOQCConfigBuilder.detect_replace_symbol(value) for value in data.values())
        if isinstance(data, list):
            # Check recursively for all elements in the list
            return any(EOQCConfigBuilder.detect_replace_symbol(item) for item in data)
        if isinstance(data, tuple):
            # Check recursively for all elements in the tuple
            return any(EOQCConfigBuilder.detect_replace_symbol(item) for item in data)
        # Other data types (int, float, None, etc.) are ignored
        return False
