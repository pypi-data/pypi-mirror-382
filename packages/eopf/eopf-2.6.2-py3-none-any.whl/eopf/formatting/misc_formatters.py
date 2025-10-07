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
misc_formatters.py

Miscellaneous formatters

"""
from typing import Any

from eopf.common import xml_utils

from .abstract import EOAbstractFormatter


class Text(EOAbstractFormatter):
    """Silent Formatter used to read metadata files"""

    # docstr-coverage: inherited
    name = "Text"

    def format_stac_mapper(self, dom: xml_utils._ElementOrTree, xpath: str, namespaces: dict[str, str]) -> Any:
        """Silent formatter, used only for parsing the path
        logic is present in stac_mapper method of XMLManifestAccessor

        Parameters
        ----------
        xpath: str

        Returns
        -------
        Returns the xpath input
        """
        return xpath

    def _format(self, xpath_input: Any) -> Any:
        """Returns the input"""
        return xpath_input

    def format_xpath_results(self, xpath_results: Any) -> Any:
        """Returns the input"""
        return xpath_results


class ToImageSize(Text):
    """Silent Formatter used to read metadata files"""

    # docstr-coverage: inherited
    name = "to_imageSize"
