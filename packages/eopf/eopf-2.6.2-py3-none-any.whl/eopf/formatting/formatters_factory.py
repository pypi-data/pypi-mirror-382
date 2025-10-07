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
formatters_factory.py

Yet again an other factory pattern

"""
# Proper to factory to register plugin
# pylint: disable=import-outside-toplevel

import re
from typing import Any, Optional, Union

from eopf.exceptions.warnings import FormatterAlreadyRegistered
from eopf.formatting.abstract import EOAbstractFormatter


class EOFormatterFactory:
    """
    Factory for formatters

    Parameters
    ----------
    default_formatters: bool
        If True the default way of registering formatters are used

    Attributes
    ----------
    formatters: dict[str, type[EOAbstractFormatter]]
        dictionary of formatters

    Examples
    ----------
    >>> def get_the_data(path):
    ...     ...
    >>> def formatter_func():
    >>>     formatter, path = EOFormatterFactory().get_formatter("to_str(/tmp/some_file.nc)")
    >>>     the_data = get_the_data(path)
    >>>     if formatter:
    ...         return formatter(the_data)
    >>>     return the_data
    """

    def __init__(self, default_formatters: bool = True) -> None:
        self._formatters: dict[str, type[EOAbstractFormatter]] = {}
        if default_formatters:
            from eopf.formatting.basic_formatters import (
                IsOptional,
                ToAuto,
                ToBool,
                ToCorrectedDateISO8601,
                ToFloat,
                ToInt,
                ToLowerStr,
                ToMicromFromNanom,
                ToNumber,
                ToStr,
            )
            from eopf.formatting.date_formatters import ToISO8601, ToUNIXTimeSLSTRL1
            from eopf.formatting.geometry_formatters import ToBbox, ToGeoJson
            from eopf.formatting.misc_formatters import Text, ToImageSize
            from eopf.formatting.xml_formatters import (
                ToBands,
                ToBoolInt,
                ToDatetime,
                ToDegradationFlags,
                ToDetectors,
                ToList,
                ToListFloat,
                ToListInt,
                ToListStr,
                ToMean,
                TomissingElements,
                ToPlatform,
                ToPosList,
                ToProcessingHistoryS01,
                ToProcessingHistoryS03,
                ToProcessingSoftware,
                ToProductTimeliness,
                ToProviders,
                ToS02Adfs,
                ToSarPolarizations,
                ToSatOrbitState,
                ToSciDOI,
                ToUTMZone,
            )

            self.register_formatter(ToStr)
            self.register_formatter(ToLowerStr)
            self.register_formatter(ToFloat)
            self.register_formatter(ToMicromFromNanom)
            self.register_formatter(ToBool)
            self.register_formatter(ToUNIXTimeSLSTRL1)
            self.register_formatter(ToISO8601)
            self.register_formatter(ToBbox)
            self.register_formatter(ToDatetime)
            self.register_formatter(ToGeoJson)
            self.register_formatter(ToInt)
            self.register_formatter(Text)
            self.register_formatter(ToImageSize)
            self.register_formatter(IsOptional)
            self.register_formatter(ToBands)
            self.register_formatter(ToMean)
            self.register_formatter(ToDetectors)
            self.register_formatter(ToList)
            self.register_formatter(ToProcessingHistoryS03)
            self.register_formatter(ToProcessingHistoryS01)
            self.register_formatter(ToListStr)
            self.register_formatter(ToListInt)
            self.register_formatter(ToListFloat)
            self.register_formatter(ToBoolInt)
            self.register_formatter(ToProcessingSoftware)
            self.register_formatter(ToAuto)
            self.register_formatter(ToNumber)
            self.register_formatter(ToSciDOI)
            self.register_formatter(ToProductTimeliness)
            self.register_formatter(ToCorrectedDateISO8601)
            self.register_formatter(ToSatOrbitState)
            self.register_formatter(ToProviders)
            self.register_formatter(ToPlatform)
            self.register_formatter(ToSarPolarizations)
            self.register_formatter(ToUTMZone)
            self.register_formatter(ToPosList)
            self.register_formatter(TomissingElements)
            self.register_formatter(ToDegradationFlags)
            self.register_formatter(ToS02Adfs)
        else:
            # to implement another logic of importing formatters
            pass

    def register_formatter(self, formatter: type[EOAbstractFormatter]) -> None:
        """
        Function to register new formatters

        Parameters
        ----------
        formatter: type[EOAbstractFormatter]
            a formatter
        """
        formatter_name = str(formatter.name)
        if formatter_name in self._formatters:
            raise FormatterAlreadyRegistered(f"{formatter_name} already registered")
        self._formatters[formatter_name] = formatter

    def get_formatter(
        self,
        path: Any,
    ) -> tuple[Union[str, None], Optional[EOAbstractFormatter], Any]:
        """
        Function retrieves a formatter and path without the formatter pattern

        Parameters
        ----------
        path: Any
            a path to an object/file

        Returns
        ----------
        tuple[Union[str, None], Union[Callable[[EOAbstractFormatter], Any], None], Any]:
            A tuple containing the formatter name, the formatting method and
            a the path (without the formatter name)
        """

        # try to get a string representation of the path
        try:
            str_repr = str(path)
        except ValueError:  # noqa
            # path can not be searched and is passed to the reader/accessor as is
            return None, None, path

        # build regex expression for formatters
        registered_formaters = "|".join(self._formatters.keys())
        regex = re.compile("^(.+:/{2,})?(%s)\\((.+)\\)" % registered_formaters)
        # check if regex matches
        m = regex.match(str_repr)
        if m:
            prefix = m[1]
            formatter_name = m[2]
            inner_path = m[3]
            # nested formatting ?
            m_inner = regex.match(inner_path)
            if m_inner:
                _, nested_formatter, nested_path = (
                    EOFormatterFactory().get_formatter(prefix + inner_path)
                    if prefix
                    else EOFormatterFactory().get_formatter(inner_path)
                )
                return formatter_name, self._formatters[formatter_name](nested_formatter), nested_path

            return (
                (formatter_name, self._formatters[formatter_name](), prefix + inner_path)
                if prefix
                else (formatter_name, self._formatters[formatter_name](), inner_path)
            )
        # no formatter pattern found
        return None, None, path
