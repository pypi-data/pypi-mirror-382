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
date_formatters.py

date formatters

"""
from datetime import datetime
from typing import Any

import numpy
from pandas import Timedelta, to_datetime
from pytz import UTC

from eopf.exceptions import FormattingError

from .abstract import EOAbstractSingleValueFormatter


class ToUNIXTimeSLSTRL1(EOAbstractSingleValueFormatter):
    """Formatter for unix time conversion for SLSTR L1 ANX time and calibration time variables"""

    # docstr-coverage: inherited
    name = "to_unix_time"

    def _format(self, xpath_input: Any) -> int:
        """Convert input to unix time

        Parameters
        ----------
        xpath_input: Any

        Returns
        ----------
        eov: EOVariable
            EOVariable with the data converted to unix time

        Raises
        ----------
        FormattingError
            When formatting can not be performed
        """
        try:
            # compute the start and end times
            start = to_datetime(datetime.fromtimestamp(0, tz=UTC))
            end = to_datetime(xpath_input[:], utc=True)

            # compute and convert the time difference into microseconds
            time_delta = numpy.int64((end - start) // Timedelta("1microsecond"))

            # convert to int since neither datetime nor numpy int types are serialisable
            return int(time_delta)
        except Exception as e:
            raise FormattingError(f"{e}") from e


class ToISO8601(EOAbstractSingleValueFormatter):
    """Formatter for ISO8601 (time) conversion"""

    # docstr-coverage: inherited
    name = "to_ISO8601"

    def _format(self, xpath_input: str) -> str:
        """Convert time to ISO8601 standard, e.g: 20220506T072719 -> 2022-05-06T07:27:19Z

        Parameters
        ----------
        xpath_input: str
            xpath

        Returns
        ----------
        date_string: strftime (string-like time format)
            String containing date converted to ISO standard.

        Raises
        ----------
        FormattingError
            When formatting can not be performed
        """
        try:
            dt_obj = datetime.strptime(xpath_input, "%Y%m%dT%H%M%S")
            date_string = dt_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
            return date_string
        except ValueError as exc:
            raise FormattingError(f"Input {xpath_input} cannot be converted to ISO standard.") from exc
