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
eo_qc_impl.py

General EOQC checks implementations

"""

import importlib
from dataclasses import dataclass
from datetime import datetime
from re import match
from typing import Any, Tuple

from eopf import EOContainer
from eopf.common import date_utils
from eopf.common.constants import (
    PROCESSING_HISTORY_ATTR,
    PROCESSING_HISTORY_OUTPUT_LEVEL_PATTERN,
    PROCESSING_HISTORY_TIME_FIELD,
    PROCESSING_HISTORY_TIME_FORMAT,
)
from eopf.common.file_utils import compute_json_size
from eopf.common.functions_utils import resolve_path_in_dict
from eopf.common.history_utils import check_history_entry
from eopf.product import EOProduct
from eopf.product.eo_container_validation import (
    check_coherent_dimension_container,
    is_valid_container,
)
from eopf.product.eo_product_validation import (
    check_coherent_dimension_product,
    is_valid_product,
)
from eopf.product.eo_validation import AnomalyDescriptor, ValidationMode
from eopf.qualitycontrol.eo_qc import EOQC, EOQCCheckResult, EOQCPartialCheckResult
from eopf.qualitycontrol.eo_qc_factory import EOQCFactory
from eopf.qualitycontrol.eo_qc_utils import EOQCFormulaEvaluator


@dataclass
@EOQCFactory.register_eoqc("formulas")
class EOQCFormula(EOQC):
    """Quality formula check class.

      eval of the formula given, parameters, variables and attributes are available under their alias
      eoproduct is also available as 'eoproduct'.

      .. code-block:: JSON

        {
            "id": "fake_inspection",
            "version": "0.0.1",
            "type": "formulas",
            "thematic": "GENERAL_QUALITY",
            "description": "validate that orbit number is between value",
            "precondition": {},
            "evaluator": {
                "parameters": [
                    {
                        "name": "v_min",
                        "value": 0
                    },
                    {
                        "name": "v_max",
                        "value": 9999999
                    }
                ],
                "variables": [
                    {
                        "name": "oa01",
                        "path": "measurements/radiance/oa01"
                    }
                ],
                "attributes": [
                    {
                        "name": "absolute_orbit",
                        "path": "stac_discovery/properties/sat:absolute_orbit"
                    }
                ],
                "formula": "v_min < absolute_orbit < v_max"
            }
        },

    Parameters
    ----------
    identifier: str
        The identifier of the quality check.
    version: str
        The version of the quality check in format XX.YY.ZZ .
    thematic: str
        Thematic of the check RADIOMETRIC_QUALITY/GEOMETRIC_QUALITY/GENERAL_QUALITY...
    description: str
        Simple description of the check (less than 100 chars)
    precondition: EOQCFormulaEvaluator
        Precondition evaluator
    evaluator: EOQCFormulaEvaluator
        Expression evaluator
    """

    evaluator: EOQCFormulaEvaluator

    # docstr-coverage: inherited
    def _check(self, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:

        # Applying the formula
        result = bool(self.evaluator.evaluate(eo_object))
        if result:
            message = f"PASSED: Formula {self.evaluator.formula} evaluate True on the product {eo_object.name}"
        else:
            message = f"FAILED: Formula {self.evaluator.formula} evaluate False on the product {eo_object.name}"
        return EOQCPartialCheckResult(status=result, message=message)


@dataclass
@EOQCFactory.register_eoqc("validate")
class EOQCValid(EOQC):
    """
    Validate a product

    Parameters
    ----------
    identifier: str
        The identifier of the quality check.
    version: str
        The version of the quality check in format XX.YY.ZZ .
    thematic: str
        Thematic of the check RADIOMETRIC_QUALITY/GEOMETRIC_QUALITY/GENERAL_QUALITY...
    description: str
        Simple description of the check (less than 100 chars)
    precondition: EOQCFormulaEvaluator
        Precondition evaluator

    """

    validation_mode: ValidationMode = ValidationMode.STAC | ValidationMode.STRUCTURE

    def _check(self, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        if isinstance(eo_object, EOProduct):
            result_valid, anomalies = is_valid_product(eo_object, validation_mode=self.validation_mode)
        elif isinstance(eo_object, EOContainer):
            result_valid, anomalies = is_valid_container(eo_object, validation_mode=self.validation_mode)
        else:
            raise ValueError("Unhandled object type")

        message_sensing, result_sensing_time = self._check_datetime(eo_object)
        if result_valid:
            if result_sensing_time:
                message = f"PASSED: The product {eo_object.name} has valid structure;{message_sensing}"
            else:
                message = f"FAILED: The product {eo_object.name} has valid structure;{message_sensing}"
        else:
            message_valid = ""
            for anom in anomalies:
                message_valid += f";category : {anom.category}, descr: {anom.description.splitlines()[0]}"
            message = f"FAILED: The product {eo_object.name} has invalid structure : {message_valid};{message_sensing}"
        return EOQCPartialCheckResult(status=result_valid and result_sensing_time, message=message)

    @staticmethod
    def _check_datetime(eo_object: EOProduct | EOContainer) -> Tuple[str, bool]:
        """
        Check the validity of the datetime
        Parameters
        ----------
        eo_object : object to check datettime on

        Returns
        -------
        Tuple (check_msg, check_status)

        """
        result_sensing_time = True
        message_sensing = "Sensing times are valid"
        start_datetime = "2022-08-31T02:17:58.477712Z"
        end_datetime = "2022-08-31T02:17:58.477712Z"
        try:
            start_datetime = resolve_path_in_dict(eo_object.attrs, "stac_discovery/properties/start_datetime")
        except KeyError:
            result_sensing_time = False
            message_sensing = "Start_datetime is missing"
        try:
            end_datetime = resolve_path_in_dict(eo_object.attrs, "stac_discovery/properties/end_datetime")
        except KeyError:
            result_sensing_time = False
            message_sensing = "End_datetime is missing"
        if result_sensing_time:
            result_sensing_time = date_utils.get_datetime_from_utc(start_datetime) < date_utils.get_datetime_from_utc(
                end_datetime,
            )
            if result_sensing_time:
                message_sensing = "STAC datetime are valid"
            else:
                message_sensing = "STAC datetime are not valid"
        return message_sensing, result_sensing_time


@dataclass
@EOQCFactory.register_eoqc("dimensions")
class EOQCCoherentDimensions(EOQC):
    """
    Validate a product dimension coherency

    the same dimension name for different dimensions (in the same EOProduct) is well defined and aligned.

    Parameters
    ----------
    identifier: str
        The identifier of the quality check.
    version: str
        The version of the quality check in format XX.YY.ZZ .
    thematic: str
        Thematic of the check RADIOMETRIC_QUALITY/GEOMETRIC_QUALITY/GENERAL_QUALITY...
    description: str
        Simple description of the check (less than 100 chars)
    precondition: EOQCFormulaEvaluator
        Precondition evaluator

    """

    def _check(self, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        anomalies: list[AnomalyDescriptor] = []
        if isinstance(eo_object, EOProduct):
            check_coherent_dimension_product(eo_object, anomalies, None)
        else:
            check_coherent_dimension_container(eo_object, anomalies, None)
        if len(anomalies) == 0:
            return EOQCPartialCheckResult(True, "PASSED : No anomaly found in dimensions")
        return EOQCPartialCheckResult(False, "FAILED : " + ";".join([a.description for a in anomalies]))


@dataclass
@EOQCFactory.register_eoqc("eoqc_runner")
class EOQCRunner(EOQC):
    """
    This EOQC allows to dynamically load an  EOQC and run it.

    Parameters
    ----------
    identifier: str
        The identifier of the quality check.
    version: str
        The version of the quality check in format XX.YY.ZZ .
    thematic: str
        Thematic of the check RADIOMETRIC_QUALITY/GEOMETRIC_QUALITY/GENERAL_QUALITY...
    description: str
        Simple description of the check (less than 100 chars)
    precondition: EOQCFormulaEvaluator
        Precondition evaluator
    module: str
        Name to the module to import.
    eoqc_class: str
        eoqc class to be executed in the module.
    parameters: dict[str, Any]
        Parameters to instance the eoqc_class.


    """

    module: str
    eoqc_class: str
    parameters: dict[str, Any]

    # docstr-coverage: inherited
    def check(self, eo_object: EOProduct | EOContainer) -> EOQCCheckResult:
        module = importlib.import_module(self.module)
        eoqc_class = getattr(module, self.eoqc_class)

        if not issubclass(eoqc_class, EOQC):
            raise TypeError(f"{self.module}/{self.eoqc_class} is not a valid EOQC")
        params = {
            "identifier": self.identifier,
            "version": self.version,
            "thematic": self.thematic,
            "description": self.description,
            "precondition": self.precondition,
        }
        params.update(self.parameters)

        eoqc: EOQC = eoqc_class(**params)

        return eoqc.check(eo_object)

    def _check(self, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        """Check method for a quality check.

        Parameters
        ----------
         eo_object: EOProduct | EOContainer
            The product to check.

        Returns
        -------
        EOQCPartialCheckResult
            Status of the quality check, and the result message
        """

        raise NotImplementedError


@dataclass
@EOQCFactory.register_eoqc("product_data_size")
class EOQCProductDataSize(EOQC):
    """
    This EOQC checks that the product data size is within range.

    Parameters
    ----------
    identifier: str
        The identifier of the quality check.
    version: str
        The version of the quality check in format XX.YY.ZZ .
    thematic: str
        Thematic of the check RADIOMETRIC_QUALITY/GEOMETRIC_QUALITY/GENERAL_QUALITY...
    description: str
        Simple description of the check (less than 100 chars)
    precondition: EOQCFormulaEvaluator
        Precondition evaluator
    min: int
        Min of the range
    max: int
        Maximum of the range

    """

    min: int
    max: int

    def _check(self, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        datasize: int = eo_object.datasize
        result = self.min < datasize < self.max
        if result:
            message = (
                f"PASSED: The product {eo_object.name} datasize ({datasize}) "
                f"is within range [{self.min},{self.max}]"
            )
        else:
            message = (
                f"FAILED: The product {eo_object.name} datasize ({datasize}) "
                f"is not within range [{self.min},{self.max}]"
            )
        return EOQCPartialCheckResult(status=result, message=message)


@dataclass
@EOQCFactory.register_eoqc("product_attr_size")
class EOQCProductAttrSize(EOQC):
    """
    This EOQC checks that the product attr file size in json is within range.

    Parameters
    ----------
    identifier: str
        The identifier of the quality check.
    version: str
        The version of the quality check in format XX.YY.ZZ .
    thematic: str
        Thematic of the check RADIOMETRIC_QUALITY/GEOMETRIC_QUALITY/GENERAL_QUALITY...
    description: str
        Simple description of the check (less than 100 chars)
    precondition: EOQCFormulaEvaluator
        Precondition evaluator
    min: int
        Min of the range
    max: int
        Maximum of the range

    """

    min: int
    max: int

    def _check(self, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        datasize: int = compute_json_size(eo_object.attrs)
        result = self.min < datasize < self.max
        if result:
            message = (
                f"PASSED: The product {eo_object.name} attr size ({datasize}) "
                f"is within range [{self.min},{self.max}]"
            )
        else:
            message = (
                f"FAILED: The product {eo_object.name} attr size ({datasize}) "
                f"is not within range [{self.min},{self.max}]"
            )
        return EOQCPartialCheckResult(status=result, message=message)


@dataclass
@EOQCFactory.register_eoqc("product_processing_history")
class EOQCProductProcessingHistory(EOQC):
    """
    This EOQC checks that the product attr file size in json is within range.

    Parameters
    ----------
    id: str
        The identifier of the quality check.
    version: str
        The version of the quality check in format XX.YY.ZZ .
    thematic: str
        Thematic of the check RADIOMETRIC_QUALITY/GEOMETRIC_QUALITY/GENERAL_QUALITY...
    description: str
        Simple description of the check (less than 100 chars)
    precondition: EOQCFormulaEvaluator
        Precondition evaluator

    """

    @staticmethod
    def _check_product_processing_history(eo_object: EOProduct) -> EOQCPartialCheckResult:

        product_status = EOQCPartialCheckResult()
        if PROCESSING_HISTORY_ATTR not in eo_object.attrs:
            message = f"FAILED : {PROCESSING_HISTORY_ATTR} is missing from EOProduct attributes: {eo_object.name}"
            return EOQCPartialCheckResult(status=False, message=message)

        if len(eo_object.attrs[PROCESSING_HISTORY_ATTR].keys()) == 0:
            message = f"FAILED : No processing history event is present in EOProduct attributes: {eo_object.name}"
            return EOQCPartialCheckResult(status=False, message=message)

        # check level names
        history_entries = []
        for level in eo_object.attrs[PROCESSING_HISTORY_ATTR]:
            if match(PROCESSING_HISTORY_OUTPUT_LEVEL_PATTERN, level) is None:
                message = (
                    f"FAILED : Level: {level} of {eo_object.name} history"
                    f" does not match the definition: {PROCESSING_HISTORY_OUTPUT_LEVEL_PATTERN}"
                )
                product_status += EOQCPartialCheckResult(status=False, message=message)
            history_entries.extend(eo_object.attrs[PROCESSING_HISTORY_ATTR][level])

        # check the processing time is ascending
        for index_entry in enumerate(history_entries):
            index = index_entry[0]
            entry = index_entry[1]
            is_valid, reason = check_history_entry(entry)
            if not is_valid:
                message = f"FAILED : {reason} for {entry} under {eo_object.name}"
                product_status += EOQCPartialCheckResult(status=False, message=message)

            if index > 0:
                cur_entry_time = datetime.strptime(entry[PROCESSING_HISTORY_TIME_FIELD], PROCESSING_HISTORY_TIME_FORMAT)
                prev_entry_time = datetime.strptime(
                    history_entries[index - 1][PROCESSING_HISTORY_TIME_FIELD],
                    PROCESSING_HISTORY_TIME_FORMAT,
                )

                if prev_entry_time > cur_entry_time:
                    message = (
                        f"FAILED : Not ascending time between current entry {entry[PROCESSING_HISTORY_TIME_FIELD]}"
                        f" and previous entry {history_entries[index-1][PROCESSING_HISTORY_TIME_FIELD]}"
                        f"in {eo_object.name} history"
                    )
                    product_status += EOQCPartialCheckResult(status=False, message=message)

        if product_status.status:
            message = f"PASSED : Processing history is valid for EOProduct: {eo_object.name}"
            return EOQCPartialCheckResult(status=True, message=message)
        return product_status

    def _check(self, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        if isinstance(eo_object, EOProduct):
            return self._check_product_processing_history(eo_object)
        if isinstance(eo_object, EOContainer):
            result = EOQCPartialCheckResult()
            for child_eoobj in eo_object:
                result += self._check(eo_object[child_eoobj])
            return result
        raise ValueError("Only EOProduct or EOContainer allowed")
