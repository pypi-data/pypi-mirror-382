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
qualitycontrol_parser.py

parser for the eoqc section of triggering file


"""
from typing import Any, Optional

from eopf.triggering.general_utils import EOTriggeringKeyParser
from eopf.triggering.interfaces import EOQCTriggeringConf


class EOQualityControlParser(EOTriggeringKeyParser):
    """breakpoints section Parser"""

    KEY = "eoqc"
    OPTIONAL_KEYS = (
        "config_folders",
        "parameters",
        "update_attrs",
        "report_path",
    )
    OPTIONAL = True
    DEFAULT: Optional[EOQCTriggeringConf] = None

    def _parse(self, data_to_parse: Any, **kwargs: Any) -> tuple[Any, list[str]]:
        errors = self.check_mandatory(data_to_parse) + self.check_unknown(data_to_parse)
        if errors:
            return None, errors

        return (
            EOQCTriggeringConf(
                config_folders=data_to_parse.get("config_folders", None),
                parameters=data_to_parse.get("parameters", None),
                update_attrs=bool(data_to_parse.get("update_attrs", True)),
                report_path=data_to_parse.get("report_path", None),
            ),
            errors,
        )

    def parse(self, data_to_parse: Any, **kwargs: Any) -> Any:
        result = super().parse(data_to_parse, **kwargs)
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return result
