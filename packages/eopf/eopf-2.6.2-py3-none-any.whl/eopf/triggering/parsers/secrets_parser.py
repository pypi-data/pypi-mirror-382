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
secrets_parser.py

parser for the secrets section of triggering file


"""
import os
from typing import Any

from eopf.triggering.general_utils import EOTriggeringKeyParser


class EOSecretConfParser(EOTriggeringKeyParser):
    """
    Secrets section parser
    """

    KEY: str = "secret"
    OPTIONAL: bool = True
    DEFAULT: list[str] = []
    LOAD_JSON: bool = False

    def _parse(self, data_to_parse: Any, **kwargs: Any) -> tuple[Any, list[str]]:
        if data_to_parse is None:
            return self.DEFAULT, []
        if not isinstance(data_to_parse, str):
            return self.DEFAULT, [f"secrets misconfigured, should be a str, but is {type(data_to_parse)}"]
        return os.path.expandvars(data_to_parse), []

    def parse(self, data_to_parse: Any, **kwargs: Any) -> dict[str, Any]:
        data = super().parse(data_to_parse, **kwargs)
        return data
