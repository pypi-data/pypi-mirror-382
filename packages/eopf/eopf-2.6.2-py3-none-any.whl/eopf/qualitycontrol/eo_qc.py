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

eo_qc.py

EOQC checks and result definitions

"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from eopf import EOContainer
from eopf.product import EOProduct
from eopf.qualitycontrol.eo_qc_utils import EOQCFormulaEvaluator


@dataclass(frozen=True)
class EOQCPartialCheckResult:
    """
    Check result partial output of _check
    """

    status: bool = True
    message: str = ""

    def __add__(self, other: "EOQCPartialCheckResult") -> "EOQCPartialCheckResult":
        """
        Concatenate two partial results.
        If at least one is failed the result is failed
        Concatenate the messages
        Parameters
        ----------
        other : EOQCPartialCheckResult, the other partial result to concat with

        Returns
        -------
        EOQCPartialCheckResult, Concatenated result
        """
        if not isinstance(other, EOQCPartialCheckResult):
            raise TypeError("Operands must be an EOQCPartialCheckResult")
        if self.message != "":
            return EOQCPartialCheckResult(self.status and other.status, f"{self.message} ; {other.message}".strip())
        return EOQCPartialCheckResult(self.status and other.status, f"{other.message}".strip())


@dataclass(frozen=True)
class EOQCCheckResult:
    """
    Check result
    """

    identifier: str
    version: str
    thematic: str
    description: str
    status: bool
    message: str

    @classmethod
    def from_partial(
        cls,
        partial_result: EOQCPartialCheckResult,
        *,
        identifier: str,
        version: str,
        thematic: str,
        description: str,
    ) -> "EOQCCheckResult":
        """
        Returns a complete check result from a partial one
        Basically it adds the missing info

        Parameters
        ----------
        partial_result : EOQCPartialCheckResult, the partial result from a check
        identifier : str, the identifier of the check
        version : str, version of the check code
        thematic : str, thematic of the check
        description : str, description of the check

        Returns
        -------
        A complete Check result
        """
        return EOQCCheckResult(
            identifier=identifier,
            version=version,
            thematic=thematic,
            description=description,
            message=partial_result.message,
            status=partial_result.status,
        )


@dataclass
class EOQC(ABC):
    """Quality check class.

    Parameters
    ----------
    identifier : str
        The identifier of the quality check.
    version: str
        The version of the quality check in format XX.YY.ZZ .
    thematic: str
        Thematic of the check RADIOMETRIC_QUALITY/GEOMETRIC_QUALITY/GENERAL_QUALITY...
    description: str
        Simple description of the check (less than 100 chars)
    precondition: EOQCFormulaEvaluator
        Precondition evaluator

    Methods
    --------
    _check: EOQCPartialCheckResult
        Abstract method to be implemented by checks implementation



    """

    identifier: str
    version: str
    thematic: str
    description: str
    precondition: EOQCFormulaEvaluator

    def check(self, eo_object: EOProduct | EOContainer) -> EOQCCheckResult:
        """Check method for a quality check.

        Parameters
        ----------
        eo_object: EOProduct | EOContainer
            The product to check.

        Returns
        -------
        bool
            Status of the quality check, true if it's ok, false if not.
        """
        if not bool(self.precondition.evaluate(eo_object=eo_object)):
            partial_result = EOQCPartialCheckResult(
                status=True,
                message=f"SKIPPED: Precondition evaluate False with formula : {self.precondition.formula}",
            )
        else:
            partial_result = self._check(eo_object)

        # Create and return
        return EOQCCheckResult.from_partial(
            partial_result=partial_result,
            identifier=self.identifier,
            version=self.version,
            thematic=self.thematic,
            description=self.description,
        )

    @abstractmethod
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
