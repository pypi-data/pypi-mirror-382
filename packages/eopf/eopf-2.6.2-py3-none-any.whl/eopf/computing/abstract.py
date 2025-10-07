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
abstract.py

Abstract classes definition for the computing module

"""
import inspect
import os.path
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional, TypeAlias, Union

from xarray.core.datatree import DataTree

import eopf
from eopf import EOConfiguration, EOContainer, EOLogging
from eopf.common import date_utils, file_utils, history_utils
from eopf.common.file_utils import AnyPath, load_json_file
from eopf.common.functions_utils import camel_to_snake
from eopf.exceptions.errors import (
    EOComputeBadConfigurationError,
    EOComputeMissingInputError,
    MissingArgumentError,
)
from eopf.product import EOProduct
from eopf.product.eo_container_validation import (
    EOContainerModel,
    validate_container_against_model,
)
from eopf.product.eo_product_validation import (
    EOProductModel,
    validate_product_against_model,
)
from eopf.product.eo_validation import AnomalyDescriptor, ValidationMode

DataType: TypeAlias = Union[EOProduct, EOContainer, DataTree]
MappingDataType: TypeAlias = Mapping[str, DataType | Iterable[DataType]]

EOConfiguration().register_requested_parameter(
    "processing_facility",
    param_is_optional=True,
    description="Processing facility to put in history",
)


@dataclass
class AuxiliaryDataFile:
    """
    AuxiliaryDataFile

    dataclass holding an ADF definition

    """

    name: str
    path: AnyPath
    store_params: Optional[dict[str, Any]] = None
    # Data pointer to store opened data or whatever you wants
    data_ptr: Any = None

    def __repr__(self) -> str:
        """
        string repr
        Returns
        -------

        """
        return f"ADF {self.name} : {self.path} : {self.data_ptr}"


ADF: TypeAlias = AuxiliaryDataFile
MappingAuxiliary: TypeAlias = Mapping[str, AuxiliaryDataFile]


class EOProcessingBase(ABC):
    """
    Define base functionalities for all processing elements such as identifier and representation
    """

    @property
    def identifier(self) -> Any:
        """Identifier of the processing step"""
        return self._identifier

    def __init__(self, identifier: Any = ""):
        self._identifier = identifier or str(id(self))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<{self.identifier}>"

    def __repr__(self) -> str:
        return f"[{id(self)}]{str(self)}"


class EOProcessingStep(EOProcessingBase):
    """Converts one or several input arrays (of one or several variables)
    into one array (of one intermediate or output variable).

    These algorithms should be usable outside a Dask context to allow re-use in other
    software or integration of existing algorithms.


    Parameters
    ----------
    identifier: str, optional
        a string to identify this processing step (useful for logging)

    See Also
    --------
    dask.array.Array
    """

    def __init__(self, identifier: Any = ""):
        warnings.warn("Deprecated, we no longer enforce the use of ProcessingSteps", DeprecationWarning)
        super().__init__(identifier)

    @abstractmethod
    def apply(self, *inputs: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Abstract method that is applied for one block of the inputs.

        It creates a new array from arrays, can be any accepted type by map_block function from Dask.

        Parameters
        ----------
        *inputs: any
            input arrays (numpy, xarray) with same number of chunks each compatible with map_block functions
        **kwargs: any
            any needed kwargs

        Returns
        -------
        Any : same kind as the input type ( numpy array or xarray DataArray)
        """


class EOProcessingUnit(EOProcessingBase):
    """Abstract base class of processors i.e. processing units
    that provide valid EOProducts with coordinates etc.

    Parameters
    ----------
    identifier: str, optional
        a string to identify this processing unit (useful for logging and tracing)

    See Also
    --------
    eopf.product.EOProduct
    """

    # To be overloaded if needed
    PROCESSOR_NAME = ""
    PROCESSOR_VERSION = ""
    PROCESSOR_LEVEL = ""
    DEFAULT_MODE = "default"
    MODES = [DEFAULT_MODE]
    MANDATORY_INPUTS: dict[str, list[str]] = {DEFAULT_MODE: []}
    MANDATORY_ADFS: dict[str, list[str]] = {DEFAULT_MODE: []}
    OUTPUT_PRODUCTS: dict[str, list[str]] = {DEFAULT_MODE: []}

    def __init__(self, identifier: Any = "") -> None:
        super().__init__(identifier)
        # Flag to update history of output product or not
        self._update_history = False
        # Additional infos to add in history.
        # See https://cpm.pages.eopf.copernicus.eu/eopf-cpm/main/PSFD/7-metadata.html#processing-history
        self._additional_history: dict[str, Any] = {}
        # Load a default configuration is any
        self._load_default_configuration()

    @classmethod
    def get_available_modes(cls) -> List[str]:
        """
        Get the list of available mode for the processor

        Returns
        -------
        The list of processor's mode
        """
        return cls.MODES

    @classmethod
    def get_default_mode(cls) -> str:
        """
        Get the default mode of the processor

        Returns
        -------
        The default processor mode
        """
        return cls.DEFAULT_MODE

    @classmethod
    def get_tasktable_description(cls, mode: Optional[str] = None, **kwargs: Any) -> Mapping[str, Any]:
        """
        Return the tasktable description for the Processing unit
        Parameters
        ----------
        mode : Optional str to specify the processing mode, if not provided default mode given
        kwargs : Any deciding parameter accepted by the processor get_tasktable_description ( see processor's doc)

        Returns
        -------
        Dictionary describing the tasktable
        """
        mode = cls._regularize_mode(mode)
        tasktable_file_path = AnyPath(
            os.path.join(
                Path(inspect.getfile(cls)).parent,
                "tasktables",
                camel_to_snake(cls.PROCESSOR_NAME) + ("_" if len(cls.PROCESSOR_NAME) != 0 else "") + mode + ".json",
            ),
        )
        if tasktable_file_path.exists():
            return file_utils.load_json_file(tasktable_file_path)
        raise KeyError(f"No tasktable file found for {mode} in {tasktable_file_path}")

    @classmethod
    def _load_default_configuration(cls, mode: Optional[str] = None, **kwargs: Any) -> None:
        """
        Get the configuration file installed if any and load it
        Parameters
        ----------
        mode : Optional str to specify the processing mode, if not provided default mode given
        kwargs : Any deciding parameter accepted by the processor get_tasktable_description ( see processor's doc)

        Returns
        -------
        Dictionary describing the tasktable
        """
        mode = cls._regularize_mode(mode)

        try:
            source_file_path = inspect.getfile(cls)
        except TypeError:
            return
        except OSError:
            return
        conf_file_path = AnyPath(
            os.path.join(
                Path(source_file_path).parent,
                "config",
                camel_to_snake(cls.PROCESSOR_NAME) + ("_" if len(cls.PROCESSOR_NAME) != 0 else "") + mode + ".toml",
            ),
        )
        if conf_file_path.exists() and conf_file_path.islocal():
            EOConfiguration().load_file(conf_file_path.path)

    @classmethod
    def _regularize_mode(cls, mode: Optional[str]) -> str:
        mode = cls.DEFAULT_MODE if mode is None else mode
        if mode not in cls.get_available_modes():
            modes_str = ", ".join(cls.get_available_modes())
            raise KeyError(f"Not accepted mode : {mode} , possibles:  {modes_str}")
        return mode

    @classmethod
    def get_mandatory_input_list(cls, mode: Optional[str] = None, **kwargs: Any) -> list[str]:
        """
        Get the list of mandatory inputs names to be provided for the run method.
        In some cases, this list might depend on parameters and ADFs.
        If parameters are not provided, default behaviour is to provide the minimal list.
        Note: This method does not verify the content of the products, it only provides the list.

        Parameters
        ----------
        mode: mode to select
        kwargs : same parameters as for the run method if available

        Returns
        -------
        the list of mandatory products to be provided
        """
        mode = cls._regularize_mode(mode)
        return cls.MANDATORY_INPUTS[mode]

    @classmethod
    def get_mandatory_adf_list(cls, mode: Optional[str] = None, **kwargs: Any) -> list[str]:
        """
        Get the list of mandatory ADF input names to be provided for the run method.
        In some cases, this list might depend on parameters.
        If parameters are not provided, default behaviour is to provide the minimal list.
        Note: This method does not verify the content of the ADF, it only provides the list.
        So no check on input ADF can be performed here.

        Parameters
        ----------
        mode: mode to select
        kwargs : same parameters as for the run method if available

        Returns
        -------
        the list of mandatory ADFs to be provided
        """
        mode = cls._regularize_mode(mode)
        return cls.MANDATORY_ADFS[mode]

    @classmethod
    def get_provided_output_list(cls, mode: Optional[str] = None, **kwargs: Any) -> list[str]:
        """
        Get the list of provided outputs for a given mode and params

        Parameters
        ----------
        mode: mode to select
        kwargs : same parameters as for the run method if available

        Returns
        -------
        the list of products provided

        """
        mode = cls._regularize_mode(mode)
        return cls.OUTPUT_PRODUCTS[mode]

    def _validate_inputs_model(
        self,
        inputs: MappingDataType,
        validation_mode: ValidationMode,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Validate inputs against their installed model in the processor folder

        Parameters
        ----------
        inputs
        mode
        kwargs

        Returns
        -------

        """
        mode = self._regularize_mode(mode)
        if not all(i in inputs.keys() for i in self.get_mandatory_input_list(mode=mode, **kwargs)):
            raise EOComputeMissingInputError(
                f"Missing mandatory input in input dict, provided : {inputs.keys()}, "
                f"requested : {self.get_mandatory_input_list(mode, **kwargs)}",
            )
        self._validate_mapping_data_type(inputs, validation_mode, mode, "in")

    def _validate_outputs_model(
        self,
        products: MappingDataType,
        validation_mode: ValidationMode,
        mode: Optional[str] = None,
    ) -> None:
        """Verify that the given products are valid.

        If the product is invalid, raise an exception.

        See Also
        --------
        eopf.product.EOProduct.validate
        """
        mode = self._regularize_mode(mode)
        self._validate_mapping_data_type(products, validation_mode, mode, "out")

    def _validate_mapping_data_type(
        self,
        inputs: MappingDataType,
        validation_mode: ValidationMode,
        mode: str,
        prefix: str = "in",
    ) -> None:
        """
        Detects if the data is a mapping or a list and sub_apply validation
        Parameters
        ----------
        inputs
        mode
        prefix

        Returns
        -------

        """
        if ValidationMode.MODEL not in validation_mode:
            return

        for input_name, input_ptr in inputs.items():
            model_file_path = AnyPath(
                os.path.join(
                    Path(inspect.getfile(type(self))).parent,
                    "models",
                    camel_to_snake(self.PROCESSOR_NAME)
                    + ("_" if len(self.PROCESSOR_NAME) != 0 else "")
                    + mode
                    + "_"
                    + prefix
                    + "_"
                    + input_name
                    + ".json",
                ),
            )
            if model_file_path.exists():
                model_file_data = load_json_file(model_file_path)
                out_anom: list[AnomalyDescriptor] = []
                # input_ptr is a list of products
                if isinstance(input_ptr, Iterable) and not isinstance(input_ptr, (EOProduct, EOContainer, DataTree)):
                    for pp in input_ptr:
                        self._validate_data_type(
                            model_file_data,
                            pp,
                            input_name=input_name,
                            model_file_path=model_file_path,
                            out_anom=out_anom,
                        )
                else:
                    self._validate_data_type(
                        model_file_data,
                        input_ptr,
                        input_name=input_name,
                        model_file_path=model_file_path,
                        out_anom=out_anom,
                    )
            else:
                raise KeyError(f"No model file found for {mode} in {model_file_path}")

    def _validate_data_type(
        self,
        model_file_data: dict[str, Any],
        product: DataType,
        *,
        input_name: str,
        model_file_path: AnyPath,
        out_anom: list[AnomalyDescriptor],
    ) -> None:
        """
        Validate that the datatype(product, container ...) validate it's model
        Parameters
        ----------
        model_file_data : model to use
        product :  product datatype to validate
        input_name : input name for logging
        model_file_path : model file path
        out_anom : output list of reported anomalies

        Returns
        -------

        """

        if isinstance(input, EOProduct):
            loaded = EOProductModel(**model_file_data)
            validate_product_against_model(
                model=loaded,
                product=product,
                mode="AT_LEAST",
                logger=EOLogging().get_logger("eopf.computing.processing_unit"),
                out_anomalies=out_anom,
            )
        elif isinstance(input, EOContainer):
            loadedc = EOContainerModel(**model_file_data)
            validate_container_against_model(
                model=loadedc,
                container=product,
                mode="AT_LEAST",
                logger=EOLogging().get_logger("eopf.computing.processing_unit"),
                out_anomalies=out_anom,
            )
        else:
            return
        if len(out_anom) != 0:
            logger = EOLogging().get_logger("eopf.computing.processing_unit")
            for anom in out_anom:
                logger.error(f"Anom : {anom.category} : {anom.description}")
            raise ValueError(
                f"Input product for '{input_name}' : '{input.name}' is not valid against schema {model_file_path.path}",
            )

    @abstractmethod
    def run(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> MappingDataType:  # pragma: no cover
        """
        Abstract method to provide an interface for algorithm implementation

        Warn : Should not be used in production as it doesn't validate anything

        Parameters
        ----------
        inputs: Mapping[str,DataType]
            all the products to process in this processing unit
        adfs: Optional[Mapping[str,AuxiliaryDataFile]]
            all the ADFs needed to process
        mode: mode to select

        **kwargs: any
            any needed kwargs (e.g. parameters)

        Returns
        -------
        Mapping[str, DataType ]
        """

    def run_validating(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        validation_mode: ValidationMode = ValidationMode.STRUCTURE,
        **kwargs: Any,
    ) -> MappingDataType:
        """Transforms input products into a new valid EOProduct/EOContainer/DataTree with new variables.

        Parameters
        ----------
        inputs: dict[str,DataType]
            all the products to process in this processing unit
        adfs: Optional[dict[str,AuxiliaryDataFile]]
            all the ADFs needed to process
        mode: mode to select
        validation_mode: AllowedValidationMode
            Mode to validate see eo_product_validation

        **kwargs: any
            any needed kwargs

        Returns
        -------
        dict[str, DataType]
        """
        mode = self._regularize_mode(mode)
        # verify that the input list is complete and valid
        self._validate_inputs_model(inputs, validation_mode=validation_mode, mode=mode, **kwargs)
        # verify that the input list is complete
        if adfs is not None and not all(i in adfs.keys() for i in self.get_mandatory_adf_list(mode=mode, **kwargs)):
            raise MissingArgumentError(
                f"Missing adf , provided {adfs.keys()} "
                f"while requested {self.get_mandatory_adf_list(mode=mode, **kwargs)}",
            )
        if adfs is not None:
            result_products = self.run(inputs, adfs, mode=mode, **kwargs)
        else:
            result_products = self.run(inputs, mode=mode, **kwargs)
        self._add_history_event(inputs=inputs, outputs=result_products, adfs=adfs, mode=mode, **kwargs)
        self._validate_outputs_model(result_products, validation_mode, mode)
        self._validate_outputs(result_products, validation_mode)
        return result_products

    def _add_history_event(
        self,
        inputs: MappingDataType,
        outputs: MappingDataType,
        mode: str,
        adfs: Optional[MappingAuxiliary] = None,
        **kwargs: Any,
    ) -> None:
        if not self._update_history:
            return

        if self.PROCESSOR_VERSION == "" or self.PROCESSOR_NAME == "" or self.PROCESSOR_LEVEL == "":
            raise EOComputeBadConfigurationError(
                "Processor is either missing version, name or processor level to create history",
            )

        # Build adf list
        adf_list = None
        if adfs is not None:
            adf_list = []
            for adf in adfs.values():
                adf_list.append(adf.name)

        # build input list
        input_list = build_id_list(inputs)

        # build output list
        output_list = build_id_list(outputs)

        new_history_entry = {
            "processor": self.PROCESSOR_NAME,
            "version": self.PROCESSOR_VERSION,
            "facility": EOConfiguration()["processing_facility"],
            "time": date_utils.get_utc_str_now(),
            "inputs": input_list,
            "outputs": output_list,
            "eopf_cpm_version": eopf.__version__,
            **self._additional_history,
        }
        if adf_list:
            new_history_entry["adfs"] = adf_list
        new_history_entry["execution_parameters"] = {"mode": mode, **kwargs}
        status, message = history_utils.check_history_entry(new_history_entry)
        if not status:
            raise EOComputeBadConfigurationError(f"History event is not valid : {message}")

        self.__add_history_event_to_outputs(new_history_entry, outputs)

    def __add_history_event_to_outputs(self, new_history_entry: dict[str, Any], outputs: MappingDataType) -> None:
        """
        Add this history event to all the sub outputs

        Parameters
        ----------
        new_history_entry : event to add
        outputs : outputs to add the event to

        Returns
        -------
        None
        """
        for output_ptr in outputs.values():
            # output_ptr is a list of products
            if isinstance(output_ptr, Iterable) and not isinstance(output_ptr, (EOProduct, EOContainer, DataTree)):
                for sub_output in output_ptr:
                    if isinstance(sub_output, (EOProduct, EOContainer)):
                        history_utils.extend_history(sub_output, new_history_entry, self.PROCESSOR_LEVEL)
                    else:
                        raise ValueError("Can't handle history for non EOProduct/EOContainer types")
            elif isinstance(output_ptr, (EOProduct, EOContainer)):
                history_utils.extend_history(output_ptr, new_history_entry, self.PROCESSOR_LEVEL)
            else:
                raise ValueError("Can't handle history for non EOProduct/EOContainer types")

    def _validate_outputs(self, products: MappingDataType, validation_mode: ValidationMode) -> None:
        """Verify that the given product is valid.

        If the product is invalid, raise an exception.

        See Also
        --------
        eopf.product.EOProduct.validate
        """
        for p in products.items():
            # input is a list of products
            if isinstance(p, Iterable) and not isinstance(p, (EOProduct, EOContainer, DataTree)):
                for pp in p:
                    if isinstance(pp, (EOProduct, EOContainer)):
                        pp.validate(validation_mode)
            elif isinstance(p[1], (EOProduct, EOContainer)):
                p[1].validate(validation_mode)


def build_id_list(mapping_data: MappingDataType) -> List[str]:
    """
    Extract the list of ids of the given MappingDataType,
    Goes through the iterables also

    Parameters
    ----------
    mapping_data

    Returns
    -------

    """
    id_list = []
    for input_ptr in mapping_data.values():
        # input_ptr is a list of products
        if isinstance(input_ptr, Iterable) and not isinstance(input_ptr, (EOProduct, EOContainer, DataTree)):
            for sub_input in input_ptr:
                if isinstance(sub_input, (EOProduct, EOContainer)):
                    id_list.append(sub_input.attrs["stac_discovery"]["id"])
                else:
                    raise ValueError("Can't handle id for non EOProduct/EOContainer types")
        elif isinstance(input_ptr, (EOProduct, EOContainer)):
            id_list.append(input_ptr.attrs["stac_discovery"]["id"])
        else:
            raise ValueError("Can't handle id for non EOProduct/EOContainer types")
    return id_list
