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
basic_formatters.py

basic formatter : float etc

"""
from ast import literal_eval
from typing import Any, List, Union

import numpy

from eopf.common import xml_utils
from eopf.exceptions import FormattingError

from .abstract import (
    EOAbstractFormatter,
    EOAbstractListValuesFormatter,
    EOAbstractSingleValueFormatter,
)


class ToStr(EOAbstractSingleValueFormatter):
    """Formatter for string conversion"""

    # docstr-coverage: inherited
    name = "to_str"

    # docstr-coverage: inherited
    def _format(self, xpath_input: str) -> str:
        """Convert input to string

        Parameters
        ----------
        xpath_input: str

        Returns
        ----------
        str:
            String representation of the input

        Raises
        ----------
        FormattingError
            When formatting can not be carried out
        """
        try:
            return str(xpath_input)
        except Exception as e:
            raise FormattingError(f"{e}") from e


class ToLowerStr(EOAbstractListValuesFormatter):
    """Formatter for string conversion to lowercase"""

    # docstr-coverage: inherited
    name = "to_str_lower"

    # docstr-coverage: inherited
    def _format(self, xpath_input: List[str]) -> list[str] | str:
        """Convert input to string

        Parameters
        ----------
        xpath_input: List[str]

        Returns
        ----------
        str:
            String representation of the input

        Raises
        ----------
        FormattingError
            When formatting can not be carried out
        """
        try:
            if isinstance(xpath_input, list):
                if len(xpath_input) == 1:
                    return str(xpath_input[0]).lower()
                return [str(x).lower() for x in xpath_input]
            return str(xpath_input).lower()
        except Exception as e:
            raise FormattingError(f"{e}") from e


class ToFloat(EOAbstractSingleValueFormatter):
    """Formatter for float conversion"""

    # docstr-coverage: inherited
    name = "to_float"

    def _format(self, xpath_input: str) -> float:
        """Convert input to float

        Parameters
        ----------
        xpath_input: str

        Returns
        ----------
        float:
            Float representation of the input

        Raises
        ----------
        FormattingError
            When formatting can not be carried out
        """
        try:
            return float(xpath_input)
        except Exception as e:
            raise FormattingError(f"{e}") from e


class ToInt(EOAbstractSingleValueFormatter):
    """Formatter for int conversion"""

    # docstr-coverage: inherited
    name = "to_int"

    def _format(self, xpath_input: str) -> Union[int, float]:
        """Convert input to int

        Parameters
        ----------
        xpath_input: str

        Returns
        ----------
        int:
            Integer representation of the input

        Raises
        ----------
        FormattingError
            When formatting can not be carried out
        """
        try:
            if xpath_input is None or xpath_input == "N/A":
                return numpy.nan
            # NOTE: int(float(..)) allow to parse '176008.000000'
            # avoid: ValueError: invalid literal for int() with base 10: '176008.000000'
            return int(float(xpath_input))
        except Exception as e:
            raise FormattingError(f"{e}") from e


class ToBool(EOAbstractSingleValueFormatter):
    """Formatter for bool conversion"""

    # docstr-coverage: inherited
    name = "to_bool"

    def _format(self, xpath_input: str) -> bool:
        """Convert input to boolean

        Parameters
        ----------
        xpath_input: str

        Returns
        ----------
        bool:
            Boolean representation of the input

        Raises
        ----------
        FormattingError
            When formatting can not be carried out
        """
        try:
            return bool(xpath_input)
        except Exception as e:
            raise FormattingError(f"{e}") from e


class IsOptional(EOAbstractFormatter):
    """Formatter for optional conversion"""

    # docstr-coverage: inherited
    name = "is_optional"

    def format_xpath_results(self, xpath_results: Any) -> Any:
        """format xpath first result"""
        try:
            if isinstance(xpath_results, list):
                if len(xpath_results) == 0:
                    return "null"
                xpath_results = xpath_results[0]
            if isinstance(xpath_results, (str, int, float)):
                return self.format(xpath_results)

            return self.format(xml_utils.get_text(xpath_results))
        except Exception:
            return "null"

    def _format(self, xpath_input: Any) -> Any:
        # can pass here if ".dat:" in path (memmap_accessor)
        return "null" if xpath_input is None else xpath_input


class ToMicromFromNanom(EOAbstractSingleValueFormatter):
    """Formatter converting nanometers to micrometers"""

    # docstr-coverage: inherited
    name = "to_microm_from_nanom"

    def _format(self, xpath_input: str) -> float:
        """Convert nanometers to micrometers

        Parameters
        ----------
        xpath_input: str

        Returns
        ----------
        float:
            Float representation of the input

        Raises
        ----------
        FormattingError
            When formatting can not be carried out
        """
        try:
            return float(xpath_input) * float(0.001)
        except Exception as e:
            raise FormattingError(f"{e}") from e


class ToNumber(EOAbstractSingleValueFormatter):
    """Formatter for number representation"""

    # docstr-coverage: inherited
    name = "to_number"

    def _format(self, xpath_input: str) -> Any:
        """Formatter converting a string which represents a number to a specific data type. eg: '12' int(12)

        Parameters
        ----------
        xpath_input: str

        Returns
        ----------
        Any:
            int, float, numpy, complex .. whatever the number type might be

        Raises
        ----------
        FormattingError
            When formatting can not be carried out
        """
        try:
            data = None
            num_types = [
                numpy.uint8,
                numpy.uint16,
                numpy.uint32,
                numpy.uint64,
                numpy.int8,
                numpy.int16,
                numpy.int32,
                numpy.int64,
                numpy.float16,
                numpy.float32,
                numpy.float64,
                numpy.longdouble,
                numpy.complex64,
                numpy.complex128,
            ]
            for num_type in num_types:
                data = ToNumber._try_type(num_type, xpath_input)
                if data is not None:
                    break
            if data is None:
                data = literal_eval(xpath_input)
                data + data, data - data, data * data, data**2, data / data
        except ZeroDivisionError:
            return data
        except Exception as e:
            raise FormattingError(f"{e}") from e
        else:
            return data

    @staticmethod
    def _try_type(tested_type: Any, xpath_input: str) -> Any:

        try:
            # check the current dtype that is floating or not
            if numpy.issubdtype(tested_type, numpy.floating):
                type_info: Any = numpy.finfo(tested_type)
                # get the maximum possible value of the number
                potential_number = float(xpath_input)
                # check in case we have overflow
                if type_info.min <= potential_number <= type_info.max and xpath_input == str(
                    tested_type(xpath_input),
                ):
                    return tested_type(xpath_input)
                return None
            type_info = numpy.iinfo(tested_type)
            # get the maximum possible value of the number
            potential_number = float(xpath_input)
            # check in case we have overflow
            if type_info.min <= potential_number <= type_info.max and xpath_input == str(
                tested_type(xpath_input),
            ):
                return tested_type(xpath_input)
            return None
        except Exception as _:  # nosec # noqa: F841
            return None


class ToAuto(EOAbstractSingleValueFormatter):
    """Formatter for converting data to what it is supposed to be"""

    # docstr-coverage: inherited
    name = "auto"

    def _format(self, xpath_input: str) -> Any:
        """Convert input to whatever it should be

        Parameters
        ----------
        xpath_input: str

        Returns
        ----------
        Any:
            Output with data type as what it supposed to be

        Raises
        ----------
        FormattingError
            When formatting can not be carried out
        """
        try:
            return literal_eval(xpath_input)
        except Exception as e:
            raise FormattingError(f"{e}") from e


class ToCorrectedDateISO8601(EOAbstractSingleValueFormatter):
    """Formatter to correct the date given as string"""

    name = "corrected_Date_ISO8601"

    def _format(self, xpath_input: str) -> Any:
        """This formatter should be used when the date has to be corrected.
        A real case would be for missing characters such as 'Z' which stands for UTC

        Parameters
        ----------
        xpath_input: string

        Returns
        ----------
        string

        Raises
        ----------
        FormattingError
            When formatting can not be carried out
        """
        try:
            if xpath_input and xpath_input[-1] != "Z":
                return xpath_input + "Z"
            return xpath_input
        except Exception as e:
            raise FormattingError(f"{e}") from e
