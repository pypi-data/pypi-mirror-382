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
external_module_parser.py

parser for the external_module section of triggering file


"""
from typing import Any

from eopf.triggering.general_utils import EOTriggeringKeyParser
from eopf.triggering.interfaces import EOExternalModuleImportParserResult


class EOExternalModuleImportParser(EOTriggeringKeyParser):
    """
    External module section parser
    """

    KEY: str = "external_modules"
    OPTIONAL: bool = True
    MANDATORY_KEYS = ("name",)
    OPTIONAL_KEYS = ("alias", "nested", "folder")
    DEFAULT: list[EOExternalModuleImportParserResult] = []
    LOAD_JSON: bool = False

    def _parse(self, data_to_parse: Any, **kwargs: Any) -> tuple[Any, list[str]]:
        errors = self.check_mandatory(data_to_parse) + self.check_unknown(data_to_parse)
        if errors:
            return None, errors

        data_parsed = EOExternalModuleImportParserResult(
            name=data_to_parse.get("name"),
            alias=data_to_parse.get("alias", None),
            nested=bool(data_to_parse.get("nested", False)),
            folder=data_to_parse.get("folder", None),
        )
        return data_parsed, errors
