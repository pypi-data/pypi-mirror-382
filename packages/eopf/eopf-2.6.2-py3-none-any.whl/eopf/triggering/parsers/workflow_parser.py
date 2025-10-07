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
workflow_parser.py

parser for the workflow section of triggering file


"""
import importlib
from typing import Any, Optional, Union

from eopf import EOLogging
from eopf.exceptions.errors import TriggerInvalidWorkflow
from eopf.triggering.general_utils import EOTriggeringKeyParser
from eopf.triggering.workflow import EOProcessorWorkFlow, WorkFlowUnitDescription


class EOTriggerWorkflowParser(EOTriggeringKeyParser):
    """workflow section Parser"""

    KEY: str = "workflow"
    MANDATORY_KEYS = ("name", "module", "processing_unit")
    OPTIONAL_KEYS = ("parameters", "inputs", "outputs", "adfs", "step", "active", "validate")

    def __init__(self) -> None:
        super().__init__()
        self.LOGGER = EOLogging().get_logger()

    def _parse(
        self,
        data_to_parse: Any,
        **kwargs: Any,
    ) -> tuple[Optional[WorkFlowUnitDescription], list[str]]:
        """
        Parse the section
        Parameters
        ----------
        data_to_parse : section loaded data
        kwargs :

        Returns
        -------
        WorkFlowUnitDescription, list(errors)
        """
        errors = self.check_mandatory(data_to_parse) + self.check_unknown(data_to_parse)
        if errors:
            return None, errors
        module_name = data_to_parse.get("module")
        class_name = data_to_parse.get("processing_unit")
        processing_name = data_to_parse.get("name")
        parameters = data_to_parse.get("parameters", {}).copy()
        inputs = data_to_parse.get("inputs", {})
        outputs = data_to_parse.get("outputs", {})
        adfs = data_to_parse.get("adfs", {})
        step: int = data_to_parse.get("step", 0)
        active = data_to_parse.get("active", True)
        validate = data_to_parse.get("validate", True)
        if active:
            try:
                module = importlib.import_module(module_name)
                try:
                    unit_class = getattr(module, class_name)
                    unit = unit_class(processing_name)
                except AttributeError:
                    return None, [f"Class {class_name} not found in module {module_name} for workflow"]
            except (
                ImportError,
                ModuleNotFoundError,
                SyntaxError,
                AttributeError,
                PermissionError,
                ValueError,
                TypeError,
                OSError,
                NameError,
            ) as e:
                return None, [f"Error while importing module {module_name} : {type(e)} {e}"]
            # verify that the input list contains the mandatory elements
            if not all(i in inputs.keys() for i in unit.get_mandatory_input_list(**parameters)):
                raise TriggerInvalidWorkflow(
                    f"Missing input for unit {module_name}.{class_name}:{processing_name}, provided {inputs.keys()} "
                    f"while requested {unit.get_mandatory_input_list(**parameters)}",
                )
            # verify that the input list contains the mandatory elements
            if not all(i in adfs.keys() for i in unit.get_mandatory_adf_list(**parameters)):
                raise TriggerInvalidWorkflow(
                    f"Missing input adf for unit {module_name}.{class_name}:{processing_name}, provided {adfs.keys()} "
                    f"while requested {unit.get_mandatory_adf_list(**parameters)}",
                )
        else:
            unit = None
        processing_unit_descr = WorkFlowUnitDescription(active, unit, inputs, adfs, outputs, parameters, step, validate)

        return processing_unit_descr, errors

    def parse(self, data_to_parse: Union[str, dict[str, Any]], **kwargs: Any) -> EOProcessorWorkFlow:
        self.LOGGER.debug(f" >> {EOTriggerWorkflowParser.parse.__qualname__}")
        result = super().parse(data_to_parse, **kwargs)

        return EOProcessorWorkFlow(workflow_units=[workflow_unit for workflow_unit in result if workflow_unit.active])
