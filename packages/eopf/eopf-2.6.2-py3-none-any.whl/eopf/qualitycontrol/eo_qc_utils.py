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

eo_qc_utils.py

Provides utility function to the quality control modules

"""


from dataclasses import dataclass, field
from typing import Any

from eopf import EOContainer, EOProduct
from eopf.common.functions_utils import resolve_path_in_dict, safe_eval


@dataclass
class EOQCFormulaEvaluator:
    """
    Formula evaluator.

    Parameters
    ----------
    formula: str
        Formula to execute.
    parameters: dict[str, Any]
        The different parameters use in the formula.
    variables: dict[str, Any]
        The different variables use in the formula.
    attributes: dict[str, Any]
       The different attributes use in the formula.

    Attributes
    ----------
    formula: str
        Formula to execute.
    parameters: dict[str, Any]
        The different thresholds use in the formula.
    variables: dict[str, Any]
        The different variables use in the formula.
    attributes: dict[str, Any]
       The different attributes use in the formula.
    """

    SECURITY_TOKEN = ["rm"]

    formula: str = "True"
    parameters: list[dict[str, Any]] = field(default_factory=list)
    variables: list[dict[str, Any]] = field(default_factory=list)
    attributes: list[dict[str, Any]] = field(default_factory=list)

    # docstr-coverage: inherited
    def evaluate(self, eo_object: EOProduct | EOContainer) -> Any:
        """

        Parameters
        ----------
        eo_object : the eo_object to evaluate ( product or container

        Returns
        -------
        the result of the evaluation of the formula
        """
        # Getting and defining variables/attributes from eoproduct
        local_var = {}
        if isinstance(eo_object, EOProduct):
            for variable in self.variables:
                local_var[variable["name"]] = eo_object[variable["path"]]
        for attribute in self.attributes:
            local_var[attribute["name"]] = resolve_path_in_dict(eo_object.attrs, attribute["path"])
        # Getting and defining thresholds
        for param in self.parameters:
            local_var[param["name"]] = param["value"]
        # The eoproduct is available under eoproduct
        local_var["eoproduct"] = eo_object

        # Applying the formula
        return safe_eval(f"{self.formula}", variables=local_var)
