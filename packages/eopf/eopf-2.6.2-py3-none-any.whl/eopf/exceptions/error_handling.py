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
error_handling.py

Provide an hiogher level error handler to allow errors not to stop the processing

Mostly used in triggering

"""
from abc import ABC, abstractmethod
from typing import Optional, Type

from eopf import EOLogging
from eopf.exceptions.errors import CriticalException, ExceptionWithExitCode


class ErrorPolicy(ABC):
    """
    Error policy pattern implementation
    """

    def __init__(self) -> None:
        self._errors: list[Exception] = []
        self._raised_error: Optional[Exception] = None
        self._logger = EOLogging().get_logger("eopf.error_policy")

    @abstractmethod
    def handle(self, exc: Exception) -> None:
        """handle the incoming error, re raise if the policy etc ..."""

    def finalize(self) -> None:
        """Optionally raise if needed at end"""
        if self._raised_error is not None:
            raise self._raised_error
        if len(self.errors) == 0:
            return
        # Create a synthetic exception at the end
        exit_code = 1
        message = ""
        has_critical: bool = False
        for f in self.errors:
            if isinstance(f, ExceptionWithExitCode):
                exit_code = f.exit_code if f.exit_code > exit_code else exit_code
            if isinstance(f, CriticalException):
                has_critical = True
            message += f"{str(f)};"
        if has_critical:
            raise CriticalException(message, exit_code=exit_code)
        raise ExceptionWithExitCode(message, exit_code=exit_code)

    @property
    def errors(self) -> list[Exception]:
        return self._errors

    @property
    def raised(self) -> bool:
        return self._raised_error is not None


class FailFastPolicy(ErrorPolicy):
    """
    FailFastPolicy : fail at any exception
    """

    def handle(self, exc: Exception) -> None:
        self.errors.append(exc)
        # In case it has already raised an exception we always raise the initial one
        if self.raised:
            self._logger.error(f"Error occurs while handling a previous error {exc}")
            raise self._raised_error
        self._raised_error = exc
        # All exceptions
        raise exc


class BestEffortPolicy(ErrorPolicy):
    """
    BestEffort : don't fail at any CPM errors (ExceptionWithExitCode derived)
    Fail at any other exception that are not derived from ours
    """

    def handle(self, exc: Exception) -> None:
        self.errors.append(exc)
        # In case it has already raised an exception we always raise the initial one
        if self.raised:
            self._logger.error(f"Error occurs while handling a previous error {exc}")
            raise self._raised_error
        # Only our exception get a bypass, all the other ones are re raised
        if not isinstance(exc, ExceptionWithExitCode):
            self._raised_error = exc
            raise exc


class FailOnCriticalPolicy(ErrorPolicy):
    """
    FailOnCritical :  Fail only at CriticalException derived and any other exceptions not derived from CPM ones.

    """

    def handle(self, exc: Exception) -> None:
        self.errors.append(exc)
        # In case it has already raised an exception we always raise the initial one
        if self.raised:
            self._logger.error(f"Error occurs while handling a previous error {exc}")
            raise self._raised_error
        if isinstance(exc, CriticalException) or not isinstance(exc, ExceptionWithExitCode):
            self._raised_error = exc
            raise exc


ERROR_POLICY_MAPPING: dict[str, Type[FailFastPolicy] | Type[FailOnCriticalPolicy] | Type[BestEffortPolicy]] = {
    "FAIL_FAST": FailFastPolicy,
    "FAIL_ON_CRITICAL": FailOnCriticalPolicy,
    "BEST_EFFORT": BestEffortPolicy,
}
