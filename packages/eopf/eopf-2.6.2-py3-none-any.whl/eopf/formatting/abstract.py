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
abstract.py

Abstract definition for the formatting module

"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Self, Union

import lxml.etree

from eopf.common import xml_utils
from eopf.logging import EOLogging


class EOAbstractFormatter(ABC):
    """Abstract formatter representation"""

    def __init__(self, inner_formatter: Optional[Self] = None) -> None:
        self._inner_formatter = inner_formatter
        self._logger = EOLogging().get_logger("eopf.formatting")

    @property
    @abstractmethod
    def name(self) -> str:
        """Set the name of the formatter, for registering it"""
        raise NotImplementedError

    def format(self, xpath_input: Any) -> Any:
        """Function that returns the formatted input"""
        if self._inner_formatter is not None:
            return self._format(self._inner_formatter.format(xpath_input))
        return self._format(xpath_input)

    @abstractmethod
    def _format(self, xpath_input: Any) -> Any:
        """Function that returns the formatted input"""
        raise NotImplementedError

    def reverse_format(self, xpath_input: Any) -> Any:
        """Function that returns the reverse of the formatted input"""
        return xpath_input

    @abstractmethod
    def format_xpath_results(self, xpath_results: Any) -> Any:
        """abstract method to format the xpath result from the stac_mapper function"""
        raise NotImplementedError

    def format_stac_mapper(self, dom: lxml.etree._ElementTree, xpath: str, namespaces: dict[str, str]) -> Any:
        """public method called in xml_accessors: stac_mapper function"""
        return self.format_xpath_results(xml_utils.get_xpath_results(dom, xpath, namespaces))


class EOAbstractTextFormatter(EOAbstractFormatter):
    """Abstract formatter representation for a text value"""

    @abstractmethod
    def format_text(self, text: Union[List[str], str, None]) -> Any:
        """abstract method to format the xpath result from the stac_mapper function"""
        raise NotImplementedError

    def format_xpath_results(self, xpath_results: Any) -> Any:
        """format xpath first result"""
        if isinstance(xpath_results, (str, int, float)):
            return self.format(xpath_results)
        return self.format_text(xml_utils.get_text(xpath_results))


class EOAbstractSingleValueFormatter(EOAbstractTextFormatter):
    """Abstract formatter representation for a single value"""

    @abstractmethod
    def _format(self, xpath_input: str) -> Any:
        """Function that returns the formatted input"""
        raise NotImplementedError

    def format_text(self, text: Union[List[str], str, None]) -> Any:
        """format xpath first result"""
        if isinstance(text, list):
            if len(text) > 0:
                return self.format(text[0])
        return self.format(text)


class EOAbstractListValuesFormatter(EOAbstractTextFormatter):
    """Abstract formatter representation for a list"""

    @abstractmethod
    def _format(self, xpath_input: List[str]) -> Any:
        """Function that returns the formatted input"""
        raise NotImplementedError

    def format_text(self, text: Union[List[str], str, None]) -> Any:
        """format xpath results list, not only the first element"""
        if text:
            return self.format(text)
        self._logger.debug("unexpected empty xpath result in EOAbstractListValuesFormatter")
        return None


class EOAbstractXMLFormatter(EOAbstractFormatter):
    """Abstract formatter representation for xml"""

    @abstractmethod
    def _format(self, xpath_input: List[lxml.etree._Element]) -> Any:
        """Function that returns the formatted input"""
        raise NotImplementedError

    def format_xpath_results(self, xpath_results: Any) -> Any:
        """format xpath results list, not only the first element"""
        if xpath_results:
            return self.format(xpath_results)
        self._logger.debug("unexpected empty xpath result in EOAbstractXMLFormatter")
        return None


class EOAbstractGenericXMLFormatter(EOAbstractFormatter):
    """Abstract formatter representation for xml with a generic xpath_input"""

    @abstractmethod
    def _format(self, xpath_input: Any) -> Any:
        """Function that returns the formatted input"""
        raise NotImplementedError

    def format_xpath_results(self, xpath_results: Any) -> Any:
        """format xpath results list, not only the first element"""
        if xpath_results:
            return self.format(xpath_results)
        self._logger.debug("unexpected empty xpath result in EOAbstractXMLFormatter")
        return None
