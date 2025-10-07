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
"""Provide generic Exceptions and Warnings for eopf modules"""

from .errors import (
    AccessorNotDefinedError,
    AccessorNotOpenError,
    DaskProfilerError,
    EOContainerSetitemError,
    EOGroupExistError,
    EOObjectMultipleParentError,
    EOQCConfigMalformed,
    EOQCConfigMissing,
    EOQCInspectionMalformed,
    EOQCInspectionMissing,
    FormattingDecoratorMissingUri,
    FormattingError,
    InvalidProductError,
    JSONParsingError,
    LoggingConfigurationDirDoesNotExist,
    LoggingConfigurationFileIsNotValid,
    LoggingConfigurationFileTypeNotSupported,
    LoggingConfigurationNotRegistered,
    LoggingDictConfigurationInvalid,
    MissingConfigurationParameterError,
    ProductNotLoaded,
    ProgressConfigurationError,
    ProgressStepProgress,
    SingleThreadProfilerError,
    StoreMissingAttr,
    StoreNotDefinedError,
    StoreNotOpenError,
    TriggeringConfigurationError,
    XmlManifestNetCDFError,
    XmlParsingError,
)

__all__ = [
    "EOGroupExistError",
    "EOObjectMultipleParentError",
    "InvalidProductError",
    "MissingConfigurationParameterError",
    "StoreNotDefinedError",
    "StoreNotOpenError",
    "AccessorNotDefinedError",
    "AccessorNotOpenError",
    "XmlParsingError",
    "JSONParsingError",
    "LoggingConfigurationDirDoesNotExist",
    "LoggingConfigurationFileTypeNotSupported",
    "LoggingConfigurationNotRegistered",
    "LoggingConfigurationFileIsNotValid",
    "DaskProfilerError",
    "SingleThreadProfilerError",
    "FormattingError",
    "FormattingDecoratorMissingUri",
    "XmlManifestNetCDFError",
    "EOQCConfigMissing",
    "EOQCConfigMalformed",
    "EOQCInspectionMissing",
    "EOQCInspectionMalformed",
    "TriggeringConfigurationError",
    "ProgressConfigurationError",
    "ProgressStepProgress",
    "ProductNotLoaded",
    "StoreMissingAttr",
    "LoggingDictConfigurationInvalid",
    "EOContainerSetitemError",
]
