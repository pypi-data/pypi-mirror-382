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
warnings.py

CPm warnings definitions
"""


class AlreadyClose(Warning):
    """When a store is already close"""


class AlreadyOpen(Warning):
    """When a store is already open"""


class StoreNotOpen(Warning):
    """When a store is not open"""


class IgnoredConfigurationParameter(Warning):
    """When a parameter in conf is ignored because reserved"""


class AlreadyRegisteredConfigurationParameter(Warning):
    """When a parameter in conf have already been registered"""


class NoLoggingConfigurationFile(Warning):
    """When the preset/given logging configuration file does not contain any .conf or yaml file"""


class NoMappingFile(Warning):
    """When the preset/given logging configuration file does not contain any .conf or yaml file"""


class DaskProfilerHtmlDisplayNotWorking(Warning):
    """When the report display of the dask_profiler is not working"""


class LoggingLevelIsNoneStandard(Warning):
    """When the given log level is register_requested_parameter to a value which is none Python standard"""


class FormatterAlreadyRegistered(Warning):
    """When a formatter with the same name was already registered"""


class LoggingDictConfigurationIsNotValid(Warning):
    """When a provided dict configuration is not valid"""


class EOPFDeprecated(Warning):
    """When a previous functionality is no longer used"""


class MaskingWarning(Warning):
    """When an warning is issued during the masking of an EOVariable"""


class ScalingWarning(Warning):
    """When an warning is issued during the scaling of an EOVariable"""


class EOZarrStoreWarning(Warning):
    """When an warning is issued during the scaling of an EOVariable"""


# Mapping warnings


class MappingMissingDimensionsWarning(Warning):
    """When an eo object description has missing dimensions"""


class MissingMappingWarning(Warning):
    """When a mapping is not found for a product"""


class IgnoredAttribute(Warning):
    """When users provide non-official attributes to an EOVariable"""


class EOSafeStoreWarning(Warning):
    """Warnings raised by the EOSafeStore"""


class ProcessingHistoryWarning(Warning):
    """Warnings raised when playing with processing history"""
