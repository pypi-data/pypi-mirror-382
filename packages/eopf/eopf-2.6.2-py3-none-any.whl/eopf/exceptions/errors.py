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
Exception recovering mecanism
"""
from abc import ABC, abstractmethod
from typing import Any, Optional


########################
# Recovery Policy Pattern
########################
class BaseRecoveryPolicy(ABC):
    """
    abstract recovery policy
    """

    @abstractmethod
    def recover(self, context: Any) -> bool:
        """Base recovery logic to be implemented."""


class NoRecoveryPolicy(BaseRecoveryPolicy):
    """
    No recovery policy
    """

    def recover(self, context: Any) -> bool:
        return False


########################
# General exceptions
########################


class ExceptionWithExitCode(Exception):
    """
    Exception with an exit code for CLI commands to be able to return deidcated return code
    """

    def __init__(self, *args: Any, exit_code: int = 1):
        super().__init__(*args)
        self.exit_code = exit_code


class CriticalException(ExceptionWithExitCode):
    """Critical one not recoverable"""


class RecoverableException(ExceptionWithExitCode):
    """
    Recoverable exceptions,

    WIP : recover from an exception

    """

    def __init__(self, *args: Any, context: Any = None, policy: Optional[BaseRecoveryPolicy] = None) -> None:
        """
        Constructor
        Parameters
        ----------
        args
        context
        policy
        """
        super().__init__(*args)
        self.context = context or {}
        self.policy = policy or NoRecoveryPolicy()

    def recover(self) -> bool:
        """
        Call the recovery function
        Returns
        -------
        Flag for successfull recovery
        """
        return self.policy.recover(self.context)


class TimeOutError(ExceptionWithExitCode):
    """Raised when a function call exceed the timeout"""


class MissingArgumentError(ExceptionWithExitCode):
    """Raised when missing an argument on a function call"""


class EOConfigurationError(ExceptionWithExitCode):
    """Parent class of all configuration errors"""


class MissingConfigurationParameterError(ExceptionWithExitCode):
    """Raised when object configuration is not register_requested_parameter"""


class InvalidConfigurationError(ExceptionWithExitCode):
    """Raised when object configuration is not register_requested_parameter"""


class NetcdfIncompatibilityError(ExceptionWithExitCode):
    """Raised when a request is incompatible with the netcdf format or library"""


class XmlParsingError(ExceptionWithExitCode):
    """Raised when xml has a non-expected structure"""


class XmlXpathError(ExceptionWithExitCode):
    """Raised when an error occurs on an XPath query"""


class JSONParsingError(ExceptionWithExitCode):
    """Raised when json have a non-valid structure"""


class FormattingError(ExceptionWithExitCode):
    """When a formatter raises exceptions"""


class FormattingDecoratorMissingUri(ExceptionWithExitCode):
    """When the decorated function is missing an argument path, url or key"""


class XmlManifestNetCDFError(ExceptionWithExitCode):
    """When trying to compile the manifest from NetCDF data (Sentinel-3)"""


class DaskProfilerError(ExceptionWithExitCode):
    """When the dask_profiler raises any error"""


class DaskClusterNotFound(CriticalException):
    """When the dask gateway cluster requested is not available"""


class DaskClusterTimeout(CriticalException):
    """When the dask gateway cluster request has a timeout : scaling, connect ..."""


class DaskComputingError(ExceptionWithExitCode):
    """When a dask computation has gone wrong"""


class DaskMonitorCriticalError(CriticalException):
    """When a dask computation has gone wrong"""


class SingleThreadProfilerError(ExceptionWithExitCode):
    """When the single_thread_profiler raises any error"""


class EOPathError(ExceptionWithExitCode):
    """Raised by any eopath problem"""


class ProductRetrievalError(ExceptionWithExitCode):
    """Raised when a legacy product can not be retrieved"""


########################
# EOProduct exceptions
########################


class EOProductError(Exception):
    """Parent class of product Exception"""


class EOGroupExistError(EOProductError):
    """Raised by EOGroup when one redefines an existing key"""


class EOGroupResolutionError(EOProductError):
    """Raised by EOGroup in case of resolution problem"""


class EOGroupInvalidRequestError(EOProductError):
    """When a bad request has been done in eogroup"""


class EOGroupReadError(EOProductError):
    """Raised when group can not be read from disk"""


class EOVariableReadError(EOProductError):
    """Raised when variable can not be read from disk"""


class EOVariableSubSetError(EOProductError):
    """Raised by EOVariable when an error occurs in subsetting"""


class EOVariableInvalidDimensionsError(EOProductError):
    """Raised when an invalid dimension is detected"""


class EOVariableAssignCoordsError(EOProductError):
    """Raised when a coordinate could not be assigned to an EOVariable"""


class EOObjectMultipleParentError(EOProductError):
    """Raised by `EOObject` with already register_requested_parameter parent and
    manipulated in context with an other parent"""


class InvalidProductError(EOProductError):
    """Raised when trying to manipulate a product without valid requirement"""


class ProductNotLoaded(EOProductError):
    """Raised when compute is called on an EOProduct that is not loaded"""


class ProductAlreadyOpened(EOProductError):
    """Raised when opening an already opened product"""


########################
# Computing Exceptions
########################


class EOComputingError(ExceptionWithExitCode):
    """ " Parent class for all computing errors"""


class EOComputeMissingInputError(EOComputingError):
    """When an input is missing to run"""


class EOComputeBadConfigurationError(EOComputingError):
    """When a processor is not correctly configured"""


########################
# Store Exceptions
########################


class EOContainerError(ExceptionWithExitCode):
    """Parent class of EOContainer Exception"""


class EOContainerSetitemError(ExceptionWithExitCode):
    """Parent class of EOContainer Exception"""


########################
# Store Exceptions
########################


class EOStoreException(ExceptionWithExitCode):
    """Parent exception for all store exceptions"""


class EOStoreInvalidRequestError(EOStoreException):
    """When a bad request has been done in an eostore"""


class EOStoreAlreadyOpenRequestError(EOStoreException):
    """When opening an already opened eostore"""


class EOStoreInvalidPathError(EOStoreException):
    """When a wrong path has been register_requested_parameter in an eostore"""


class EOStoreProductAlreadyExistsError(EOStoreException):
    """When creating an already existing eostore"""


class MappingAccessorNotFoundError(EOStoreException):
    """Raised when the corresponding accessor is not found"""


class MappingConfigurationError(EOStoreException):
    """Raised when an error occurs while retrieving an accessor config from the mapping"""


class TemplateMissingError(EOStoreException):
    """Raised when no template has been found for a product type"""


class EOSafeStoreInvalidPathError(EOStoreException):
    """Raised when a requested path does not exist in the store"""


class EOCogStoreInvalidPathError(EOStoreException):
    """Raise when an invalid path to a group/variable is requested"""


class EOStoreFactoryNoRegisteredStoreError(EOStoreException):
    """Raised when no store can be provided"""


class StoreNotDefinedError(EOStoreException):
    """Raised when store is None in the given context"""


class StoreNotOpenError(EOStoreException):
    """Raised when trying to access a closed store"""


class StoreMissingAttr(EOStoreException):
    """Raised when a store does not have defined an attribute"""


class StoreInvalidMode(EOStoreException):
    """Raised when opening a store in an invalid mode"""


class StoreOpenFailure(EOStoreException):
    """Raised when a store fails to open"""


class StoreLoadFailure(EOStoreException):
    """Raised when a store fails to load an EOProduct"""


class StoreWriteFailure(EOStoreException):
    """Raised when a store fails to write an EOProduct"""


class StoreReadFailure(EOStoreException):
    """Raised when a product can not be read by Store"""


class RecognitionFunctionNotDefinedError(EOStoreException):
    """Raised when a product can not be read by Store"""


########################
# Accessors exceptions
########################


class AccessorError(ExceptionWithExitCode):
    """Parent exception on all accessor exceptions"""


class AccessorNotDefinedError(AccessorError):
    """Raised when accessor is None in the given context"""


class AccessorNotOpenError(AccessorError):
    """Raised when trying to access a closed accessor"""


class AccessorInvalidRequestError(AccessorError):
    """Raised when an invalid request is done on an accessor, for example with a non-existing path"""


class AccessorInvalidPathError(EOStoreException):
    """When a wrong path has been register_requested_parameter in an eoaccessor"""


class AccessorRetrieveError(AccessorError):
    """Raised when retrieval of data via the accessor is failing"""


class AccessorInvalidMode(AccessorError):
    """Raised when opening an accessor in an invalid mode"""


class AccessorInvalidMappingParameters(AccessorError):
    """Raised when parameters from mapping are invalid"""


class AccessorInitError(AccessorError):
    """Raised when an accessor can not be initialised"""


class AccessorOpenError(AccessorError):
    """Raised when an accessor can not be opened"""


########################
# Logging Exceptions
########################


class LoggingError(ExceptionWithExitCode):
    """Parent exception for all logging exceptions"""


class LoggingConfigurationDirDoesNotExist(LoggingError):
    """When the preset or given logging directory does not exist"""


class LoggingConfigurationFileTypeNotSupported(LoggingError):
    """When the logging file name does not have a .conf or .yaml extension"""


class LoggingConfigurationNotRegistered(LoggingError):
    """When a given logging configuration name is not registered"""


class LoggingConfigurationFileIsNotValid(LoggingError):
    """When a given logging configuration file .conf/.yaml cannot be applied"""


class LoggingDictConfigurationInvalid(LoggingError):
    """Raised when the logging configuration given as dict is not valid"""


########################
# QualityControl Exceptions
########################


class EOQCError(ExceptionWithExitCode):
    """Parent class of Quality Control Exceptions"""


class EOQCInspectionError(ExceptionWithExitCode):
    """When an inspection raised an exception"""


class EOQCConfigMissing(EOQCError):
    """When there is no default configuration for the given product type"""


class EOQCConfigMalformed(EOQCError):
    """When there is no default configuration for the given product type"""


class EOQCInspectionMissing(EOQCError):
    """When there is no default configuration for the given product type"""


class EOQCInspectionMalformed(EOQCError):
    """When there is no default configuration for the given product type"""


########################
# Triggering Exceptions
########################


class TriggeringError(ExceptionWithExitCode):
    """Parent class of Triggering Exceptions"""


class TriggeringConfigurationError(TriggeringError):
    """When triggering configuration file is wrong"""


class TriggeringInternalError(TriggeringError):
    """Raised when a triggering internal error occurs"""


class TriggerInvalidWorkflow(TriggeringError):
    """Raised when an error occurs in the workflow"""


########################
# Tracing Exceptions
########################


class TracingError(ExceptionWithExitCode):
    """Parent class of Triggering Exceptions"""


class ProgressConfigurationError(TracingError):
    """When progress configuration is not register_requested_parameter"""


class ProgressStepProgress(TracingError):
    """When the sum of each progress step is not sum_max_progress"""


class MaskingError(TracingError):
    """When an error occurs during the masking of an EOVariable"""


class ScalingError(TracingError):
    """When an error occurs during the scaling of an EOVariable"""


# MappingFormatter errors
class MappingFormatterError(ExceptionWithExitCode):
    """Base MappingFormatter error"""


class MissingArgumentsMappingFormatterError(ExceptionWithExitCode):
    """Raised when arguments are missing for a specific Mapping Formatter"""


class MappingDefinitionError(ExceptionWithExitCode):
    """When elements of a mapping are not correctly defined or missing"""


# MappingFactory errors
class EOPFMappingFactory(ExceptionWithExitCode):
    """Base EOPFMappingFactory error"""


class MappingRegistrationError(EOPFMappingFactory):
    """When registration of mappings fails"""


class MappingMissingError(EOPFMappingFactory):
    """When no mapping is found"""


########################
# Processing History Exceptions
########################


class ProcessingHistoryError(ExceptionWithExitCode):
    """Parent class of Processing History Exceptions"""


class ProcessingHistoryUnsortable(ProcessingHistoryError):
    """When the provided processing history can not be sorted"""


class ProcessingHistoryInvalidLevel(ProcessingHistoryError):
    """The level name must follow the defined format"""


class ProcessingHistoryMissingLevels(ProcessingHistoryError):
    """There are no levels defined in the Processing History"""


class ProcessingHistoryInvalidEntry(ProcessingHistoryError):
    """The processing history entry is not valid"""


########################
# Merging Exceptions
########################


class MergingError(ExceptionWithExitCode):
    """Base Exception gfor all merging tool errors"""
