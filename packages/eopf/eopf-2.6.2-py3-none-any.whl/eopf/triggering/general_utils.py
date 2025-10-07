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
general_utils.py

Utilities for triggering parsing

"""
import json
from abc import ABC, abstractmethod
from typing import Any, Iterator, Optional, Sequence

from eopf.common.functions_utils import expand_env_var_in_dict
from eopf.config.config import EOConfiguration
from eopf.exceptions import (
    MissingConfigurationParameterError,
    TriggeringConfigurationError,
)
from eopf.logging import EOLogging


class ParseLoader(ABC):
    """Abstract class to Parse triggering payload data"""

    def __init__(self) -> None:
        super().__init__()
        self.logger = EOLogging().get_logger()

    def load(self, data_to_parse: Any, load_json: bool) -> Any:
        """Load the data to provide a full plain dict object (follow link).

        Parameters
        ----------
        data_to_parse: str or dict or list
            if is a string, the data is load_file with json.load_file
        load_json: bool

        Returns
        -------
        json loaded object
        """
        if isinstance(data_to_parse, str) and load_json:
            with open(data_to_parse, encoding="utf-8") as f:
                data_to_parse = json.load(f)
        return data_to_parse

    @abstractmethod
    def parse(self, data_to_parse: Any, **kwargs: Any) -> Any:
        """Retrieve and parse the given data for the dedicated Key

        Parameters
        ----------
        data_to_parse

        Returns
        -------
        parsed items
        """


class EOTriggeringKeyParser(ParseLoader):
    """Abstract class to parse key in triggering payload data"""

    KEY: str = ""
    """Corresponding key in the payload"""
    OPTIONAL: bool = False
    """this key can not be here ?"""
    LOAD_JSON: bool = True
    """this key can not be here ?"""
    DEFAULT: Any = {}
    """default for optional if not present"""
    OPTIONAL_KEYS: Sequence[str] = tuple()
    """subkeys not mandatory"""
    MANDATORY_KEYS: Sequence[str] = tuple()
    """subkeys mandatory"""
    NEEDS: Sequence[str] = tuple()
    """Name of elements needed at the same level"""

    def is_multiple(self, data_to_parse: Any) -> bool:
        """Check if the corresponding data can be a list of item or a unique element

        Parameters
        ----------
        data_to_parse: dict or list
            corresponding data to this key

        Returns
        -------
        True or False
        """
        return isinstance(data_to_parse, list)

    @property
    def keys(self) -> tuple[str, ...]:
        """All subkeys"""
        return tuple([*self.OPTIONAL_KEYS, *self.MANDATORY_KEYS])

    def get_data(self, data_to_parse: Any, load_json: bool) -> Iterator[Any]:
        """yield data from parsable input data

        Parameters
        ----------
        data_to_parse
        load_json load json files

        Yields
        ------
        a unique items
        """
        data = self.load(data_to_parse, load_json)
        if self.is_multiple(data_to_parse):
            yield from data
        else:
            yield data

    def parse(self, data_to_parse: Any, **kwargs: Any) -> Any:
        data = self.load(data_to_parse, self.LOAD_JSON)
        data = data.get(self.KEY)
        if not data and not self.OPTIONAL:
            raise TriggeringConfigurationError(f"mandatory section {self.KEY} is misconfigured")
        if data:
            results, errors = [], []
            for data in self.get_data(data, self.LOAD_JSON):
                step_result, step_errors = self._parse(data, **kwargs)
                errors.extend(step_errors)
                results.append(step_result)
            if errors:
                raise TriggeringConfigurationError("\n".join(errors))
            return results
        return self.DEFAULT

    @abstractmethod
    def _parse(self, data_to_parse: Any, **kwargs: Any) -> tuple[Any, list[str]]:
        """Specific parse method, use to parse a unique item.

        In the case of multiple, is called one time per item

        Parameters
        ----------
        data_to_parse

        Returns
        -------
        tuple of result and errors.
        """

    def check_mandatory(self, data_to_parse: dict[str, Any]) -> list[str]:
        """Check if all mandatory keys are present.

        Returns
        -------
        list of errors
        """
        return [f'missing "{key}" in "{self.KEY}" section' for key in self.MANDATORY_KEYS if key not in data_to_parse]

    def check_unknown(self, data_to_parse: dict[str, Any]) -> list[str]:
        """Check if only defined keys are present

        Returns
        -------
        list of errors
        """
        return [f'Unkown {key=} in "{self.KEY} section"' for key in data_to_parse if key not in self.keys]


class EOProcessParser(ParseLoader):
    """Parser aggregator, use to parse multiple keys for on payload data

    Parameters
    ----------
    *parsers: EOTriggeringKeyParser
        parsers to use

    """

    def __init__(self, *parsers: type[EOTriggeringKeyParser]) -> None:
        super().__init__()
        self.parsers = {parser.KEY: parser for parser in parsers}

    def parse(self, data_to_parse: Any, result: Optional[dict[str, Any]] = None, **kwargs: Any) -> Any:
        result = {}
        for parse_name, parser in self.parsers.items():
            if parse_name not in result:
                if parser.NEEDS:
                    result |= EOProcessParser(*(self.parsers[key] for key in parser.NEEDS)).parse(
                        data_to_parse,
                        result=result,
                    )
                result[parse_name] = parser().parse(
                    data_to_parse,
                    **{key: res for key, res in result.items() if key in parser.NEEDS},
                )
        return result


def parse_store_params(store_params: dict[str, Any]) -> dict[str, Any]:
    """Retrieve store parameters depending on the used secrets_type"""
    s3_alias = store_params.pop("s3_secret_alias", None)
    storage_options: Optional[dict[str, Any]] = store_params.pop("storage_options", None)
    if s3_alias is not None:
        s3_cloud = EOConfiguration().secrets(s3_alias)
        if (
            ("key" not in s3_cloud)
            or ("secret" not in s3_cloud)
            or ("endpoint_url" not in s3_cloud)
            or ("region_name" not in s3_cloud)
        ):
            raise MissingConfigurationParameterError

        store_params["storage_options"] = {
            "key": s3_cloud["key"],
            "secret": s3_cloud["secret"],
            "client_kwargs": {"endpoint_url": s3_cloud["endpoint_url"], "region_name": s3_cloud["region_name"]},
        }
    elif storage_options is not None:
        store_params["storage_options"] = expand_env_var_in_dict(storage_options)
    else:
        # nothing provided
        store_params["storage_options"] = {}

    return store_params
