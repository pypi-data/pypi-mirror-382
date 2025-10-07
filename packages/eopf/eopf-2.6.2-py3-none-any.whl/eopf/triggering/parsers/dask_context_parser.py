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
dask_context_parser.py

parser for the dask_context section of triggering file


"""
from contextlib import nullcontext
from typing import Any

from eopf.dask_utils import DaskContext
from eopf.dask_utils.dask_cluster_type import get_enum_from_value
from eopf.triggering.general_utils import EOTriggeringKeyParser


class EODaskContextParser(EOTriggeringKeyParser):
    """Dask context Parser"""

    KEY = "dask_context"
    OPTIONAL = True
    OPTIONAL_KEYS = (
        "cluster_type",
        "cluster_config",
        "client_config",
        "dask_config",
        "performance_report_file",
    )
    MANDATORY_KEYS = ()
    DEFAULT = nullcontext()

    def _parse(self, data_to_parse: Any, **kwargs: Any) -> tuple[Any, list[str]]:
        if data_to_parse is None:
            return {}, []
        if not isinstance(data_to_parse, dict):
            return None, [f"dask context misconfigured, should be dict, but is {type(data_to_parse)}"]
        errors = self.check_mandatory(data_to_parse) + self.check_unknown(data_to_parse)
        if errors:
            return None, errors
        if "cluster_type" not in data_to_parse and "address" not in data_to_parse:
            return None, ["address dask context parameter should be provided when no cluster type given"]

        return (
            DaskContext(
                cluster_type=get_enum_from_value(str(data_to_parse.get("cluster_type", "address"))),
                cluster_config=data_to_parse.get("cluster_config", None),
                client_config=data_to_parse.get("client_config", None),
                dask_config=data_to_parse.get("dask_config", None),
                performance_report_file=data_to_parse.get("performance_report_file", None),
            ),
            errors,
        )

    def parse(self, data_to_parse: Any, **kwargs: Any) -> Any:
        result = super().parse(data_to_parse, **kwargs)
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return result
