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
breakpoint_parser.py

parser for the breakpoint section of triggering file


"""
from typing import Any, Optional

from eopf.triggering.general_utils import EOTriggeringKeyParser, parse_store_params
from eopf.triggering.interfaces import EOBreakPointParserResult


class EOBreakPointParser(EOTriggeringKeyParser):
    """breakpoints section Parser"""

    KEY = "breakpoints"
    MANDATORY_KEYS = ("ids",)
    OPTIONAL_KEYS = ("folder", "all", "store_params")
    OPTIONAL = True
    DEFAULT: Optional[EOBreakPointParserResult] = None

    def _parse(self, data_to_parse: Any, **kwargs: Any) -> tuple[Any, list[str]]:
        """
        Parse the section
        Parameters
        ----------
        data_to_parse : section loaded data
        kwargs :

        Returns
        -------
        EOBreakPointParserResult, list(errors)
        """
        errors = self.check_mandatory(data_to_parse) + self.check_unknown(data_to_parse)
        if errors:
            return None, errors
        ids = data_to_parse.get("ids")
        if not isinstance(ids, list):
            return {}, [f"breakpoints misconfigured, ids should be a list, but is {type(ids)}"]

        return (
            EOBreakPointParserResult(
                ids=ids,
                all=data_to_parse.get("all", False),
                folder=data_to_parse.get("folder", None),
                store_params=parse_store_params(data_to_parse.get("store_params", {}))["storage_options"],
            ),
            errors,
        )

    def parse(self, data_to_parse: Any, **kwargs: Any) -> Any:
        result = super().parse(data_to_parse, **kwargs)
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return result
