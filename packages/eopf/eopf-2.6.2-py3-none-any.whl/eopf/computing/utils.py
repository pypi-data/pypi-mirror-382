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
dask_helpers.py

Utilities for processor implementation


"""
import ast
from typing import Any, Dict, List, Optional, Tuple

import dask.array as da
import numpy as np

from eopf import EOContainer
from eopf.computing import eopf_breakpoint_decorator
from eopf.computing.abstract import (
    DataType,
    EOProcessingUnit,
    MappingAuxiliary,
    MappingDataType,
)
from eopf.product import EOProduct
from eopf.product.eo_group import EOGroup
from eopf.product.eo_variable import EOVariable


class EOExtractRoiUnit(EOProcessingUnit):
    """Processing unit responsible for extracting of the region of interest to be processed"""

    @staticmethod
    def get_available_modes() -> List[str]:
        return ["nominal", "passthrought"]

    @staticmethod
    def get_default_mode() -> str:
        return "nominal"

    @eopf_breakpoint_decorator(identifier="EOExtractRoiUnit")
    def run(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> MappingDataType:
        """
        Processing unit implementation method for ROI filtering.
        EOContainers are not allowed

        Parameters
        ----------
        inputs: Mapping[str, DataType]
            The products from which we want to extract the region of interest.
        adfs: Mapping[str,AuxiliaryDataFile]
            all the ADFs needed to process
        mode: mode to select
        kwargs: Any


        Returns
        -------
        MappingDataType
            containing the ROI processed
        """
        region: str = kwargs["region"]
        ref_variable: Optional[str] = kwargs.get("ref_variable", None)

        # return the ROI
        ret: dict[str, DataType] = {}
        for key, eoproduct in inputs.items():
            if not isinstance(eoproduct, EOProduct):
                raise TypeError("EOContainer/Datatree/Iterable not allowed on this processing Unit")
            ret[key] = eoproduct.subset(region=ast.literal_eval(region), reference=ref_variable)
        return ret


class EORechunkingUnit(EOProcessingUnit):
    """Processing unit responsible of re-chunking all EOProduct variables"""

    def run(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> MappingDataType:
        """
        Processing unit implementation method for the rechunking.
        Works inplace and modifies the input eoproducts

        Parameters
        ----------
        inputs: Mapping[str, EOProduct | EOContainer | DataTree]
            The product that is going to be re-chunked.

        adfs: Mapping[str,AuxiliaryDataFile]
            all the ADFs needed to process

        mode: mode to select

        chunks: Dict
            new chunks to be applied : {'rows':1000,'columns' : -1}
            -1 indicates the full size of the corresponding dimension.

        Returns
        -------
        Mapping[str, EOProduct|DataTree]
            rechunked inputs using the provided dimensions sizes
        """
        chunks: Dict[str, int] = kwargs["chunks"]
        for eoproduct in inputs.values():
            if not isinstance(eoproduct, EOProduct):
                raise TypeError("Only EOProduct allowed on this ProcessingUnit")
            self.rechunk_product(eoproduct, chunks)
        return inputs

    def rechunk_product(self, prod: DataType, chunks: Dict[str, int]) -> None:
        """
        Rechunk a whole procut by iterating through variables
        Parameters
        ----------
        prod : product to rechunk
        chunks : chunks to apply

        Returns
        -------

        """
        if isinstance(prod, EOContainer):
            for prod_keys in prod.keys():
                self.rechunk_product(prod[prod_keys], chunks)
        elif isinstance(prod, EOProduct):
            self.rechunk_all_variables(prod, chunks)

    def rechunk_all_variables(
        self,
        eogroup: EOGroup,
        chunks: Dict[str, int],
    ) -> None:
        """
        re-chunk all variables of a given EOProduct or EOGroup using the new dimensions provided within chunks dict.
        In-place modifier
        """
        # loop over all groups of the eocontainer
        for _, group in eogroup.groups:
            # do the same thing for all sub-groups
            self.rechunk_all_variables(group, chunks)
            # re-chunk all concerned variables
            for _, var in group.variables:
                new_chunks = {}
                for dim, chunk in chunks.items():
                    if dim in var.dims:
                        new_chunks[dim] = chunk
                # re-chunk the variable
                if len(new_chunks) > 0:
                    var.chunk(new_chunks)


class EOConstantUnit(EOProcessingUnit):
    """Add a constant variable in the product"""

    def run(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> MappingDataType:
        """
        Add a new variable with the given name to an EOProduct
        EOContainer are not allowed
        Parameters
        ----------
        inputs: Mapping[str, DataType]
            The product that is going to be modified.

        adfs: Mapping[str,AuxiliaryDataFile]
            all the ADFs needed to process

        mode: mode to select

        value: np.float64
            constant value of the new variable to add.

        variable_path: str
            path to the variable in the eoproduct

        variable_name: str
            name of he variable

        shape: Tuple[int,...]
            shape of the new variable

        Returns
        -------
        Mapping[str, EOProduct| EOContainer | DataTree]
            input with the new variable added
        """
        value: np.float64 = kwargs["value"]
        variable_path: str = kwargs["variable_path"]
        shape: Tuple[int, ...] = kwargs["shape"]
        for eoproduct in inputs.values():
            if not isinstance(eoproduct, EOProduct):
                raise TypeError("Only EOProduct allowed on this ProcessingUnit")
            eoproduct[variable_path] = EOVariable(data=da.full(shape, value, dtype=np.float64))
        return inputs


class EODummyUnit(EOProcessingUnit):
    """Dummy unit that returns the inputs"""

    @eopf_breakpoint_decorator(
        identifier="dummy",
        description="Dummy breakpoint for tutorial purpose",
        filename_prefix="Dummy_",
    )
    def run(
        self,
        inputs: MappingDataType,
        adfs: Optional[MappingAuxiliary] = None,
        mode: Optional[str] = None,
        **kwargs: Any,
    ) -> MappingDataType:  # pragma: no cover
        """
        Parameters
        -----------------
        inputs: MappingDataType
            The product that is going to be modified.
        adfs: Optional[MappingAuxiliary]
            all the ADFs needed to process
        mode: mode to select
        kwargs: Any

        Returns
        -------
        Mapping[str, DataType]
            inputs
        """
        return inputs
