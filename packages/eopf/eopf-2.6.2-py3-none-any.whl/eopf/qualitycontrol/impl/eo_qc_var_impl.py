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
eo_qc_var_impl.py

EOVariable/EOGroup specific checks implementation

"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np

from eopf import EOContainer, EOGroup, EOProduct, EOVariable
from eopf.qualitycontrol.eo_qc import EOQC, EOQCPartialCheckResult
from eopf.qualitycontrol.eo_qc_factory import EOQCFactory


@dataclass
class EOQCVarBase(EOQC):
    """
    This EOQC is the base of all variables checks.

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
    variables: list[str]
        List of the variables to check

    """

    variables: list[str]

    # docstr-coverage: inherited
    def _check(self, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        """
        Check each variabless

        Parameters
        ----------
        eo_object : EOObject to analyse

        Returns
        -------
        Result of the check
        """
        if not isinstance(eo_object, EOProduct):
            raise TypeError("Target is not an EOProduct, only EOProduct accepted")
        res = EOQCPartialCheckResult()
        if len(self.variables) == 0:
            return EOQCPartialCheckResult(status=True, message="SKIPPED: No variable/group to check")
        for var_path in self.variables:
            try:
                attr_value = eo_object[var_path]
            except KeyError:
                res = res + EOQCPartialCheckResult(
                    status=False,
                    message=f"FAILED : Variable/Group {var_path} is not available "
                    f"in product for check {type(self).__name__}",
                )
                continue
            res = res + self._var_check(var_path, attr_value, eo_object)
        if res is None:
            return EOQCPartialCheckResult(status=False, message="ERROR: This should not happen")
        return res

    @abstractmethod
    def _var_check(self, var_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        """
        Placeholder to be overriden in sub class

        Parameters
        ----------
        var_path: path in the product of the var
        value : Any value to pass to the check (expected values etc)
        eo_object : : EOObject to analyse

        Returns
        -------
            Result of the check
        """


@dataclass
@EOQCFactory.register_eoqc("path_exists")
class EOQCPathAvailable(EOQCVarBase):
    """
    This EOQC checks that the variables/groups are available in the product.

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
    variables: list[str]
        List of the variables to check

    """

    def _var_check(self, var_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        """
        Path is available in the product check

        Parameters
        ----------
        var_path: path in the product of the var
        value : Any value to pass to the check (expected values etc)
        eo_object : : EOObject to analyse

        Returns
        -------
            Result of the check
        """
        if value is not None:
            return EOQCPartialCheckResult(
                status=True,
                message=f"PASSED : Variable/Group {var_path} is available in " f"product",
            )
        return EOQCPartialCheckResult(
            status=False,
            message=f"FAILED : Variable/Group {var_path} is available in product but has None value",
        )


@dataclass
@EOQCFactory.register_eoqc("var_in_range")
class EOQCVarInRange(EOQCVarBase):
    """
    This EOQC checks that the variables values are within range.

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
    variables: list[str]
        List of the variables to check
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

    def _var_check(self, var_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        """
        Check that the variable value are in the specified range

        Parameters
        ----------
        var_path: path in the product of the var
        value : Any value to pass to the check (expected values etc)
        eo_object : : EOObject to analyse

        Returns
        -------
            Result of the check
        """
        if not isinstance(value, EOVariable):
            raise TypeError("Target is not an EOVariable")
        if self.strict:
            if self.min < np.float64(value.data.max().compute().item()) < self.max:
                return EOQCPartialCheckResult(
                    status=True,
                    message=f"PASSED: Variable {var_path} is strictly within {self.min} and {self.max}",
                )
            return EOQCPartialCheckResult(
                status=False,
                message=f"FAILED: Variable {var_path} is not strictly within {self.min} and {self.max}",
            )
        if self.min <= np.float64(value.data.max().compute().item()) <= self.max:
            return EOQCPartialCheckResult(
                status=True,
                message=f"PASSED: Variable {var_path} is within {self.min} and {self.max}",
            )
        return EOQCPartialCheckResult(
            status=False,
            message=f"FAILED: Variable {var_path} is not within {self.min} and {self.max}",
        )


@dataclass
@EOQCFactory.register_eoqc("var_count")
class EOQCCountVar(EOQCVarBase):
    """
    This EOQC check that the variables/groups has the number of expected sub elements.

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
    variables: list[str]
        List of the variables to check
    expected: int
        Expected sub groups elements

    """

    expected: int

    def _var_check(self, var_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        """
        Check var has the expected number of sub elements, for example number of detectors

        Parameters
        ----------
        var_path: path in the product of the var
        value : Any value to pass to the check (expected values etc)
        eo_object : : EOObject to analyse

        Returns
        -------
            Result of the check
        """
        if not isinstance(value, EOGroup):
            raise TypeError("Target is not a group, can't count element")

        if len(value) != self.expected:
            return EOQCPartialCheckResult(
                status=False,
                message=f"FAILED: Expected {self.expected} elements under {var_path}, found {len(value)}",
            )
        return EOQCPartialCheckResult(
            status=True,
            message=f"PASSED: {self.expected} elements found under {var_path}",
        )


@dataclass
@EOQCFactory.register_eoqc("var_notzerosize")
class EOQCNotZeroSizeVar(EOQCVarBase):
    """
    This EOQC check that the variables has data.

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
    variables: list[str]
     List of the variables to check


    """

    def _var_check(self, var_path: str, value: Any, eo_object: EOProduct | EOContainer) -> EOQCPartialCheckResult:
        """
        Check that the variable is not zero sized

        Parameters
        ----------
        var_path: path in the product of the var
        value : Any value to pass to the check (expected values etc)
        eo_object : : EOObject to analyse

        Returns
        -------
            Result of the check
        """
        if not isinstance(value, EOVariable):
            raise TypeError("Target is not an EOVariable")

        if value.data.size == 0:
            return EOQCPartialCheckResult(
                status=False,
                message=f"FAILED: {var_path} variable has no data attached",
            )
        return EOQCPartialCheckResult(
            status=True,
            message=f"PASSED: {var_path} variable has data",
        )
