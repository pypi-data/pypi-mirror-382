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
eo_qc_attr_impl.py

Attributes checks implementation

"""

import re
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np

from eopf import EOContainer, EOProduct
from eopf.common.functions_utils import resolve_path_in_dict
from eopf.qualitycontrol.eo_qc import EOQC, EOQCPartialCheckResult
from eopf.qualitycontrol.eo_qc_factory import EOQCFactory


@dataclass
class EOQCAttrBase(EOQC):
    """
    This EOQC is the base of all attributes checks.

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
    attributes: list[str]
        List of the attributes to check, in posix like path /stac_discovery/properties/sat:relative_orbit


    """

    attributes: list[str]

    # docstr-coverage: inherited
    def _check(self, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        res = EOQCPartialCheckResult()
        if len(self.attributes) == 0:
            return EOQCPartialCheckResult(status=True, message="SKIPPED: No attribute to check")
        for attrib_path in self.attributes:
            try:
                attr_value = resolve_path_in_dict(eo_object.attrs, attrib_path)
            except KeyError:
                res = res + EOQCPartialCheckResult(
                    status=False,
                    message=f"FAILED : Attribute {attrib_path} is not "
                    f"available in product for check {type(self).__name__}",
                )
                continue
            res = res + self._attr_check(attrib_path, attr_value, eo_object)
        if res is None:
            return EOQCPartialCheckResult(status=False, message="ERROR: This should not happen")
        return res

    @abstractmethod
    def _attr_check(self, attrib_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        pass


@dataclass
@EOQCFactory.register_eoqc("attr_exists")
class EOQCAttrAvailable(EOQCAttrBase):
    """
    This EOQC validate that the attributes are available in the product.

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
    attributes: list[str]
        List of the attributes to check, in posix like path /stac_discovery/properties/sat:relative_orbit

    """

    def _attr_check(self, attrib_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        if value is not None:
            return EOQCPartialCheckResult(
                status=True,
                message=f"PASSED : Attribute {attrib_path} is available in product",
            )
        return EOQCPartialCheckResult(
            status=False,
            message=f"FAILED : Attribute {attrib_path} is available in product but has None value",
        )


@dataclass
@EOQCFactory.register_eoqc("attr_in_range")
class EOQCAttrInRange(EOQCAttrBase):
    """
    This EOQC verify that the attributes values are within the ranges.

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
    attributes: list[str]
        List of the attributes to check, in posix like path /stac_discovery/properties/sat:relative_orbit
    min: np.float64
        Min of the range
    max: np.float64
        Maximum of the range
    strict: bool
        Perform a strict compare < of an equal one <=

    """

    min: np.float64
    max: np.float64
    strict: bool = False

    def _attr_check(self, attrib_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:

        if self.strict:
            if self.min < np.float64(value) < self.max:
                return EOQCPartialCheckResult(
                    status=True,
                    message=f"PASSED: {attrib_path} is strictly within {self.min} and {self.max}",
                )
            return EOQCPartialCheckResult(
                status=False,
                message=f"FAILED: {attrib_path} is not strictly within {self.min} and {self.max}",
            )
        if self.min <= np.float64(value) <= self.max:
            return EOQCPartialCheckResult(
                status=True,
                message=f"PASSED: {attrib_path} is within {self.min} and {self.max}",
            )
        return EOQCPartialCheckResult(
            status=False,
            message=f"FAILED: {attrib_path} is not within {self.min} and {self.max}",
        )


@dataclass
@EOQCFactory.register_eoqc("attr_in_list")
class EOQCAttrInPossibleValues(EOQCAttrBase):
    """
    This EOQC check that the attributes values are in the given list.

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
    attributes: list[str]
        List of the attributes to check, in posix like path /stac_discovery/properties/sat:relative_orbit
    possible_values: list[str]
        List of possible values accepted

    """

    possible_values: list[str]

    def _attr_check(self, attrib_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        if value not in self.possible_values:
            return EOQCPartialCheckResult(
                status=False,
                message=f"FAILED: {attrib_path}:{value} is not in the possible list {self.possible_values}",
            )
        return EOQCPartialCheckResult(
            status=True,
            message=f"PASSED: {attrib_path}:{value} is in the possible list {self.possible_values}",
        )


@dataclass
@EOQCFactory.register_eoqc("attr_matches")
class EOQCAttrRegexMatch(EOQCAttrBase):
    """
    This EOQC check that the attributes values are matching the given pattern.

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
    attributes: list[str]
        List of the attributes to check, in posix like path /stac_discovery/properties/sat:relative_orbit
    pattern: str
        Pattern accepted

    """

    pattern: str

    def _attr_check(self, attrib_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        if re.fullmatch(self.pattern, value) is None:
            return EOQCPartialCheckResult(
                status=False,
                message=f"FAILED: {attrib_path} value {value} is not matching the pattern {self.pattern}",
            )
        return EOQCPartialCheckResult(
            status=True,
            message=f"PASSED: {attrib_path} value {value} is matching the pattern {self.pattern}",
        )


@dataclass
@EOQCFactory.register_eoqc("attr_count")
class EOQCCountAttr(EOQCAttrBase):
    """
    This EOQC check that the attributes has the number of expected sub elements.

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
    attributes: list[str]
        List of the attributes to check, in posix like path /stac_discovery/properties/sat:relative_orbit
    expected: int
        Expected sub attributes elements

    """

    expected: int

    def _attr_check(self, attrib_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:

        if not isinstance(value, (dict, list, set, tuple)):
            return EOQCPartialCheckResult(
                status=False,
                message=f"FAILED: {attrib_path} doesn't point to a dict/list/set/tuple, can't count elements",
            )

        if len(value) != self.expected:
            return EOQCPartialCheckResult(
                status=False,
                message=f"FAILED: Expected {self.expected} attributes under {attrib_path}, found {len(value)}",
            )
        return EOQCPartialCheckResult(
            status=True,
            message=f"PASSED: {self.expected} attributes found under {attrib_path}",
        )
