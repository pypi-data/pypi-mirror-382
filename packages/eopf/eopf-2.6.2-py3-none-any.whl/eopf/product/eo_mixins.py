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
eo_mixins.py

mixins for eovariables

"""

import operator
from abc import ABC, abstractmethod
from collections.abc import Hashable
from logging import Logger
from typing import Any, Callable, Generic, Optional, Tuple, TypeVar, Union

import numpy as np
import xarray as xr
from dask import array as da
from deepdiff import DeepDiff
from numpy._typing import DTypeLike
from xarray import DataArray

from eopf import EOConfiguration
from eopf.common.constants import (
    ADD_OFFSET,
    DEEP_DIFF_IGNORE_TYPE_IN_GROUPS,
    DIMENSIONS_NAME,
    DTYPE,
    EOV_IS_MASKED,
    EOV_IS_SCALED,
    FILL_VALUE,
    SCALE_FACTOR,
    TARGET_DTYPE,
    VALID_MAX,
    VALID_MIN,
    XARRAY_FILL_VALUE,
)
from eopf.product.utils.scale_mask_utils import (
    mask_array,
    scale_dask_array,
    scale_numpy_array,
    unscale_array,
)

EOV_TYPE = TypeVar("EOV_TYPE", bound="EOVariableOperatorsMixin[Any]")
EOV_MASK_SCALE_TYPE = TypeVar("EOV_MASK_SCALE_TYPE", bound="EOVariableScaleMaskMixin[Any]")


# Type of EOVariable, could be replaced by PEP 673 -- Self Type, starting with Python 3.11


class EOVariableOperatorsMixin(Generic[EOV_TYPE]):
    """
    Provide unary and binary operations on the data of it's subtype EOV_TYPE.
    All inheriting class must define the following attributes:

    Attributes
    ----------
    _data : xarray.DataArray
    """

    __slots__ = ()
    __array_priority__ = 60

    _data: xr.DataArray

    def _init_similar(self: EOV_TYPE, data: xr.DataArray) -> EOV_TYPE:  # pragma: no cover
        raise NotImplementedError

    def __bool__(self: Any) -> bool:
        return bool(self._data)

    def __float__(self: Any) -> float:
        return float(self._data)

    def __int__(self: Any) -> int:
        return int(self._data)

    def __complex__(self: Any) -> complex:
        return complex(self._data)

    def __array__(self: Any, dtype: Optional[Union[np.dtype[Any], str]] = None) -> np.ndarray[Any, Any]:
        return np.asarray(self._data, dtype=dtype)

    def __array_ufunc__(self, ufunc: Any, method: str, *inputs: Any, **kwargs: Any) -> EOV_TYPE:
        data_list = [var._data if isinstance(var, EOVariableOperatorsMixin) else var for var in inputs]
        return self._init_similar(self._data.__array_ufunc__(ufunc, method, *data_list, **kwargs))

    def __array_wrap__(self, obj: Any, context: Optional[Any] = None) -> EOV_TYPE:
        return self._init_similar(self._data.__array_wrap__(obj, context=context))

    def __apply_binary_ops__(
        self: EOV_TYPE,
        other: Any,
        ops: Callable[[Any, Any], Any],
        reflexive: Optional[bool] = False,
    ) -> EOV_TYPE:
        if isinstance(other, EOVariableOperatorsMixin):
            other_value = other._data
        else:
            other_value = other
        data = self._data

        return self._init_similar(ops(data, other_value) if not reflexive else ops(other_value, data))

    def __add__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.add)

    def __sub__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.sub)

    def __mul__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.mul)

    def __pow__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.pow)

    def __truediv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.truediv)

    def __floordiv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.floordiv)

    def __mod__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.mod)

    def __and__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.and_)

    def __xor__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.xor)

    def __or__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.or_)

    def __lt__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.lt)

    def __le__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.le)

    def __gt__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.gt)

    def __ge__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.ge)

    def __radd__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.add, reflexive=True)

    def __rsub__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.sub, reflexive=True)

    def __rmul__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.mul, reflexive=True)

    def __rpow__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.pow, reflexive=True)

    def __rtruediv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.truediv, reflexive=True)

    def __rfloordiv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.floordiv, reflexive=True)

    def __rmod__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.mod, reflexive=True)

    def __rand__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.and_, reflexive=True)

    def __rxor__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.xor, reflexive=True)

    def __ror__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_binary_ops__(other, operator.or_, reflexive=True)

    def __apply_inplace_ops__(self: EOV_TYPE, other: Any, ops: Callable[[Any, Any], Any]) -> EOV_TYPE:
        if isinstance(other, EOVariableOperatorsMixin):
            other_value = other._data
        else:
            other_value = other

        data = self._data

        self._data = ops(data, other_value)
        return self

    def __iadd__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.iadd)

    def __isub__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.isub)

    def __imul__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.imul)

    def __ipow__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.ipow)

    def __itruediv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.itruediv)

    def __ifloordiv__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.ifloordiv)

    def __imod__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.imod)

    def __iand__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.iand)

    def __ixor__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.ixor)

    def __ior__(self: EOV_TYPE, other: Any) -> EOV_TYPE:
        return self.__apply_inplace_ops__(other, operator.ior)

    def __apply_unary_ops__(self: EOV_TYPE, ops: Callable[[Any], Any], *args: Any, **kwargs: Any) -> EOV_TYPE:
        return self._init_similar(ops(self._data), *args, **kwargs)

    def __neg__(self: EOV_TYPE) -> EOV_TYPE:
        return self.__apply_unary_ops__(operator.neg)

    def __pos__(self: EOV_TYPE) -> EOV_TYPE:
        return self.__apply_unary_ops__(operator.pos)

    def __abs__(self: EOV_TYPE) -> EOV_TYPE:
        return self.__apply_unary_ops__(operator.abs)

    def __invert__(self: EOV_TYPE) -> EOV_TYPE:
        return self.__apply_unary_ops__(operator.invert)

    def round(self: EOV_TYPE, *args: Any, **kwargs: Any) -> EOV_TYPE:
        return self.__apply_unary_ops__(xr.DataArray.round, *args, **kwargs)

    def argsort(self: EOV_TYPE, *args: Any, **kwargs: Any) -> EOV_TYPE:
        return self.__apply_unary_ops__(xr.DataArray.argsort, *args, **kwargs)

    def conj(self: EOV_TYPE, *args: Any, **kwargs: Any) -> EOV_TYPE:
        return self.__apply_unary_ops__(xr.DataArray.conj, *args, **kwargs)

    def conjugate(self: EOV_TYPE, *args: Any, **kwargs: Any) -> EOV_TYPE:
        return self.__apply_unary_ops__(xr.DataArray.conjugate, *args, **kwargs)

    __add__.__doc__ = operator.add.__doc__
    __sub__.__doc__ = operator.sub.__doc__
    __mul__.__doc__ = operator.mul.__doc__
    __pow__.__doc__ = operator.pow.__doc__
    __truediv__.__doc__ = operator.truediv.__doc__
    __floordiv__.__doc__ = operator.floordiv.__doc__
    __mod__.__doc__ = operator.mod.__doc__
    __and__.__doc__ = operator.and_.__doc__
    __xor__.__doc__ = operator.xor.__doc__
    __or__.__doc__ = operator.or_.__doc__
    __lt__.__doc__ = operator.lt.__doc__
    __le__.__doc__ = operator.le.__doc__
    __gt__.__doc__ = operator.gt.__doc__
    __ge__.__doc__ = operator.ge.__doc__
    __radd__.__doc__ = operator.add.__doc__
    __rsub__.__doc__ = operator.sub.__doc__
    __rmul__.__doc__ = operator.mul.__doc__
    __rpow__.__doc__ = operator.pow.__doc__
    __rtruediv__.__doc__ = operator.truediv.__doc__
    __rfloordiv__.__doc__ = operator.floordiv.__doc__
    __rmod__.__doc__ = operator.mod.__doc__
    __rand__.__doc__ = operator.and_.__doc__
    __rxor__.__doc__ = operator.xor.__doc__
    __ror__.__doc__ = operator.or_.__doc__
    __iadd__.__doc__ = operator.iadd.__doc__
    __isub__.__doc__ = operator.isub.__doc__
    __imul__.__doc__ = operator.imul.__doc__
    __ipow__.__doc__ = operator.ipow.__doc__
    __itruediv__.__doc__ = operator.itruediv.__doc__
    __ifloordiv__.__doc__ = operator.ifloordiv.__doc__
    __imod__.__doc__ = operator.imod.__doc__
    __iand__.__doc__ = operator.iand.__doc__
    __ixor__.__doc__ = operator.ixor.__doc__
    __ior__.__doc__ = operator.ior.__doc__
    __neg__.__doc__ = operator.neg.__doc__
    __pos__.__doc__ = operator.pos.__doc__
    __abs__.__doc__ = operator.abs.__doc__
    __invert__.__doc__ = operator.invert.__doc__
    round.__doc__ = xr.DataArray.round.__doc__
    argsort.__doc__ = xr.DataArray.argsort.__doc__
    conj.__doc__ = xr.DataArray.conj.__doc__
    conjugate.__doc__ = xr.DataArray.conjugate.__doc__


class EOVariableEqualMixin(ABC):
    """
    Mixin to add the equal operator to variables
    """

    def __eq__(self, other: Any) -> bool:
        """
        Equality operator

        Parameters
        ----------
        other : other to compare to

        Returns
        -------

        """
        # Check if the other object is an instance of EOVariable
        if not isinstance(other, EOVariableEqualMixin):
            raise NotImplementedError

        if not super().__eq__(other):
            return False

        if self.is_scaled != other.is_scaled or self.is_masked != other.is_masked:
            return False  # not both masked or unmasked

        if not self.__compare_attrs(other):
            return False

        if not self.__compare_data_attrs(other):
            return False

        if not self.__compare_data_chunks(other):
            return False

        if not self.__compare_data_values(other):
            return False

        if not self.__compare_data_coords(other):
            return False

        return True

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __compare_data_coords(self, other: Any) -> bool:
        if set(self.data.coords) != set(other.data.coords):
            return False  # coordinates in self not as in other

        # Compare data coordinates
        for coord_key, coord_value in self.data.coords.items():
            if coord_value.dtype != other.data.coords[coord_key].dtype:
                return False  # not the same coordinates data type
            if coord_value.ndim != other.data.coords[coord_key].ndim:
                return False  # not the same number of array dimensions
            if coord_value.shape != other.data.coords[coord_key].shape:
                return False  # not the same array dimensions
            if coord_value.chunks != other.data.coords[coord_key].chunks:
                # if one of the chunksizes (usually the legacy) is not defined then we should not do the comparison
                # as the developper of the product has not defined it
                if coord_value.chunks is not None and other.data.coords[coord_key] is not None:
                    return False
            if not EOVariableEqualMixin.__compare_one_data_coord(coord_key, coord_value, other):
                return False
        return True

    @staticmethod
    def __compare_one_data_coord(coord_key: Hashable, coord_value: DataArray | Any, other: Any) -> bool:

        if hasattr(coord_value.data, "_meta") and isinstance(
            coord_value.data._meta,
            np.ma.core.MaskedArray,
        ):
            atol = np.finfo(float).eps  # smallest non-zero atol
            if not np.ma.allclose(
                coord_value.data.compute(),
                other.data.coords[coord_key].data.compute(),
                atol=atol,
            ):
                return False
        elif np.issubdtype(coord_value.data.dtype, np.floating):
            atol = np.finfo(float).eps  # smallest non-zero atol
            try:
                if not da.allclose(
                    coord_value.data,
                    other.data.coords[coord_key].data,
                    equal_nan=True,
                    atol=atol,
                ).compute():
                    return False  # coordinates data is different
            except np.exceptions.DTypePromotionError:  # TBC weird error under OCN IW longitude coordinate
                if not da.all(coord_value.data == other.data.coords[coord_key].data).compute():
                    return False  # coordinates data is different
        else:
            if not da.all(coord_value.data == other.data.coords[coord_key].data).compute():
                return False  # coordinates data is different

        # Compare data coordinates attributes
        if DeepDiff(
            coord_value.attrs,
            other.data.coords[coord_key].attrs,
            ignore_order=True,  # order of elements inside the list/tuple doesn’t matter
            # exclude_types=[tuple, list],  # lists and tuples equivalent if they contain the same elements
            ignore_type_in_groups=DEEP_DIFF_IGNORE_TYPE_IN_GROUPS,
            exclude_paths=[XARRAY_FILL_VALUE, DIMENSIONS_NAME],
        ):
            return False  # True when DeepDiff returns not empty dict

        return True

    def __compare_data_attrs(self, other: "EOVariableEqualMixin") -> bool:
        if self.data.dtype != other.data.dtype:
            return False  # not the same data type
        if self.data.ndim != other.data.ndim:
            return False  # not the same number of array dimensions
        if self.data.shape != other.data.shape:
            return False  # not the same array dimensions
        if self.data.sizes != other.data.sizes:
            return False  # not the same sizes

        return True

    def __compare_data_chunks(self, other: "EOVariableEqualMixin") -> bool:
        if self.data.chunksizes != other.data.chunksizes:
            if len(self.data.chunksizes) > 0 and len(other.data.chunksizes) > 0:
                # if one of the chunksizes is not defined, we should not make the comparison
                # the developper of the product did not define chunking
                return False  # not the same chunksizes
        if self.data.chunks != other.data.chunks:
            if self.data.chunks is not None and other.data.chunks is not None:
                # product developper did not define chunking
                return False  # not the same block lengths for this dataarray's data, in order of dimensions

        return True

    def __compare_data_values(self, other: "EOVariableEqualMixin") -> bool:
        if hasattr(self.data.data, "_meta") and isinstance(self.data.data._meta, np.ma.core.MaskedArray):
            atol = np.finfo(float).eps  # smallest non-zero atol
            if not np.ma.allclose(self.data.data.compute(), other.data.data.compute(), atol=atol):
                return False
        elif np.issubdtype(self.data.dtype, np.floating):
            atol = np.finfo(float).eps  # smallest non-zero atol
            if not da.allclose(self.data.data, other.data.data, equal_nan=True, atol=atol).compute():
                return False
        elif np.issubdtype(self.data.dtype, np.integer) and SCALE_FACTOR in self.attrs:
            atol = self.attrs[SCALE_FACTOR]
            if not da.allclose(self.data.data, other.data.data, equal_nan=True, atol=atol).compute():
                return False
        else:
            if not da.all(self.data.data == other.data.data).compute():
                return False

        return True

    def __compare_attrs(self, other: "EOVariableEqualMixin") -> bool:

        # Compare EOVariables attributes
        # exclude FILL_VALUE and XARRAY_FILL_VALUE as dtype may differ
        # however, if the values are different the data check should catch it
        if DeepDiff(
            self.attrs,
            other.attrs,
            ignore_order=True,
            ignore_type_in_groups=DEEP_DIFF_IGNORE_TYPE_IN_GROUPS,
            exclude_paths=[XARRAY_FILL_VALUE, FILL_VALUE],
        ):  # True when DeepDiff returns not empty dict
            return False

        # Compare EOVariables data attributes
        if DeepDiff(
            self.data.attrs,
            other.data.attrs,
            ignore_order=True,
            ignore_type_in_groups=DEEP_DIFF_IGNORE_TYPE_IN_GROUPS,
            exclude_paths=[XARRAY_FILL_VALUE, FILL_VALUE],
        ):  # True when DeepDiff returns not empty dict
            return False

        return True

    @property
    @abstractmethod
    def is_scaled(self) -> bool:
        """Return whether the object is scaled."""

    @property
    @abstractmethod
    def is_masked(self) -> bool:
        """Return whether the object is masked."""

    @property
    @abstractmethod
    def data(self) -> DataArray:
        """Return the data"""

    @property
    @abstractmethod
    def attrs(self) -> dict[str, Any]:
        """

        Returns
        -------
        Attributes dict
        """


class EOVariableScaleMaskMixin(Generic[EOV_MASK_SCALE_TYPE], ABC):
    """
    Provides scale and mask functionality
    """

    _data: xr.DataArray
    _attrs: dict[str, Any]
    _logger: Logger

    def scale(
        self: EOV_MASK_SCALE_TYPE,
        scale_factor: Optional[np.number[Any]] = None,
        add_offset: Optional[np.number[Any]] = None,
        scale_apply: Optional[bool] = None,
        target_dtype: Optional[np.dtype[Any]] = None,
    ) -> EOV_MASK_SCALE_TYPE:
        """
        Scale the data of the current EOVariable.
        The coordinates are also scaled based on their scale_factor and add_offset attributes, if present.

        Parameters
        ----------
        scale_factor : Optional[np.number[Any]]
            valid minimum value
        add_offset : Optional[np.number[Any]]
            valid maximum value
        scale_apply : Optional[bool]
            toggle scaling on or off
        target_dtype : Optional[np.dtype[Any]]
            dtype of the scaled data
        """
        if scale_apply is None:
            eopf_config = EOConfiguration()
            scale_apply = eopf_config.get("product__mask_and_scale")

        if not scale_apply:
            # no scaling applied
            self._logger.debug(f"{self.path}. Scaling not applied: scale_apply is False")
            return self

        # let the user know it is performing scaling on already scaled data
        if self.is_scaled:
            self._logger.debug(f"{self.path}. EOVariable is already scaled")
            return self

        add_offset, scale_factor, target_dtype = self._resolve_scale_params(add_offset, scale_factor, target_dtype)

        # this is done to avoid scalling values equal to fill_value (masked)
        if self.is_masked:
            self.mask()

        # scale the data
        if isinstance(self._data.data, np.ndarray):
            # numpy scaling
            self._data, scale_applied = DataArray(
                scale_numpy_array(
                    self._data,
                    scale_factor=scale_factor,
                    add_offset=add_offset,
                    target_dtype=target_dtype,
                ),
            )
        else:
            # Dask scaling
            self._data.data, scale_applied = scale_dask_array(
                self._data.data,
                scale_factor=scale_factor,
                add_offset=add_offset,
                target_dtype=target_dtype,
            )

        # update eov attrs
        if scale_factor is not None:
            self._attrs[SCALE_FACTOR] = scale_factor
        if add_offset is not None:
            self._attrs[ADD_OFFSET] = add_offset
        if target_dtype is not None:
            self._attrs[TARGET_DTYPE] = np.dtype(target_dtype).str

        # remove scale_factor and add_offset from _data.attrs to mark EOVariable has been scaled
        # the scale_factor can still be retrieved from self.attrs
        self._data.attrs.pop(SCALE_FACTOR, None)
        self._data.attrs.pop(ADD_OFFSET, None)

        # Dask scaling for coordinates: only on coordinates that have ADD_OFFSET or SCALE_FACTOR
        scale_applied = self._scale_coordinates(scale_applied)

        if scale_applied:
            self._attrs[EOV_IS_SCALED] = True

        return self

    def _resolve_scale_params(
        self: EOV_MASK_SCALE_TYPE,
        add_offset: Optional[np.number[Any]],
        scale_factor: Optional[np.number[Any]],
        target_dtype: Optional[np.dtype[Any]],
    ) -> Tuple[Optional[np.number[Any]], Optional[np.number[Any]], Optional[np.dtype[Any]]]:
        # if scale_factor, add_offset and target_dtype are not provided via parameters
        # retrieve them from the EOV attrs
        if scale_factor is None:
            if SCALE_FACTOR in self._data.attrs:
                scale_factor = self._data.attrs.get(SCALE_FACTOR)
            elif SCALE_FACTOR in self._attrs:
                scale_factor = self._attrs.get(SCALE_FACTOR)
        if add_offset is None:
            if ADD_OFFSET in self._data.attrs:
                add_offset = self._data.attrs.get(ADD_OFFSET)
            elif ADD_OFFSET in self._attrs:
                add_offset = self._attrs.get(ADD_OFFSET)
        if target_dtype is None:
            if TARGET_DTYPE in self._attrs:
                target_dtype = np.dtype(self._attrs[TARGET_DTYPE])
            elif scale_factor is not None:
                target_dtype = np.dtype(type(scale_factor))
        return add_offset, scale_factor, target_dtype

    def _scale_coordinates(self: EOV_MASK_SCALE_TYPE, scale_applied: bool) -> bool:
        # Dask scaling for coordinates: only on coordinates that have ADD_OFFSET or SCALE_FACTOR
        for coord_name in self._data.coords:
            if coord_name not in self._data.coords.indexes.dims:
                coord = self._data.coords[coord_name]
                scale_factor = coord.attrs.get(SCALE_FACTOR, None)
                add_offset = coord.attrs.get(ADD_OFFSET, None)
                if TARGET_DTYPE in coord.attrs:
                    target_dtype = np.dtype(coord.attrs[TARGET_DTYPE])
                elif scale_factor is not None:
                    # use the target_dtype of scale factor if it exists and target_dtype was not specified
                    target_dtype = np.dtype(type(scale_factor))
                    coord.attrs[TARGET_DTYPE] = np.dtype(target_dtype).str
                else:
                    target_dtype = None

                coord.data, scale_applied_on_coord = scale_dask_array(
                    coord.data,
                    scale_factor=scale_factor,
                    add_offset=add_offset,
                    target_dtype=target_dtype,
                )
                if scale_applied_on_coord is True:
                    scale_applied = True
                    coord.attrs[EOV_IS_SCALED] = True
        return scale_applied

    def unscale(
        self: EOV_MASK_SCALE_TYPE,
        scale_factor: Optional[np.number[Any]] = None,
        add_offset: Optional[np.number[Any]] = None,
        scale_apply: Optional[bool] = None,
        target_dtype: Optional[np.dtype[Any]] = None,
        remove_scale_attrs: bool = True,
    ) -> EOV_MASK_SCALE_TYPE:
        """
        Un-scale the data of the current EOVariable.
        The coordinates are also un-scaled based on their scale_factor and add_offset attributes, if present.

        Parameters
        ----------
        scale_factor : Optional[np.number[Any]]
            valid minimum value
        add_offset : Optional[np.number[Any]]
            valid maximum value
        scale_apply : Optional[bool]
            toggle scaling on or off
        target_dtype : Optional[np.dtype[Any]]
            dtype of the scaled data
        """

        # retrieve scale_apply
        if scale_apply is None:
            eopf_config = EOConfiguration()
            scale_apply = eopf_config.get("product__mask_and_scale")

        if not scale_apply:
            # no unscaling applied
            self._logger.debug(f"{self.path}. Unscaling not applied: the EOVar apply_scale is False")
            return self

        # non numeric data types are not scaled
        if not np.issubdtype(self.dtype, np.number):
            self._logger.debug(f"{self.path}. Unscaling not applied: the EOVariable dtype is non numeric")
            return self

        # let the user know it is performing an unscaling over a variable which was not scaled previously
        if not self.is_scaled:
            self._logger.debug(f"{self.path}. The current EOVariable is not scaled")
            return self

        scale_factor, add_offset, target_dtype, fill_value = self._resolve_unscale_params(
            scale_factor,
            add_offset,
            target_dtype,
        )

        # unscale the data
        self._data.data, unscale_applied = unscale_array(
            self._data.data,
            scale_factor=scale_factor,
            add_offset=add_offset,
            target_dtype=target_dtype,
            fill_value=fill_value,
        )

        # put the scale_factor and add_offset in xarray to allow re-scalling
        if scale_factor is not None:
            self._data.attrs[SCALE_FACTOR] = scale_factor
        if add_offset is not None:
            self._data.attrs[ADD_OFFSET] = add_offset

        unscale_applied = self._unscale_coords(unscale_applied)

        if unscale_applied:
            self._attrs.pop(EOV_IS_SCALED, None)

        return self

    def _unscale_coords(self, unscale_applied: bool) -> bool:
        """
        Unscale ther coordinates

        Parameters
        ----------
        unscale_applied : unscale applied on main data ?

        Returns
        -------
        update unscale flag
        """
        # unscale coordinates: coordinates with SCALE_FACTOR or ADD_OFFSET attribute
        for coord_name in self._data.coords:
            if coord_name not in self._data.coords.indexes.dims:
                coord = self._data.coords[coord_name]
                scale_factor = coord.attrs.get(SCALE_FACTOR, None)
                add_offset = coord.attrs.get(ADD_OFFSET, None)
                target_dtype = coord.attrs.get(DTYPE, None)
                fill_value = coord.attrs.get(FILL_VALUE, None)
                if target_dtype is None:
                    target_dtype = coord.data.dtype
                    # use scale_factor/add_offset type as target_dtype

                coord.data, unscale_applied_on_coord = unscale_array(
                    coord.data,
                    scale_factor=scale_factor,
                    add_offset=add_offset,
                    target_dtype=target_dtype,
                    fill_value=fill_value,
                )
                if unscale_applied_on_coord is True:
                    unscale_applied = True
                    coord.attrs.pop(EOV_IS_SCALED, None)
        return unscale_applied

    def _resolve_unscale_params(
        self,
        scale_factor: Optional[np.number[Any]] = None,
        add_offset: Optional[np.number[Any]] = None,
        target_dtype: Optional[np.dtype[Any]] = None,
    ) -> Tuple[Optional[np.number[Any]], Optional[np.number[Any]], np.dtype[Any], Any]:
        """
        Resolve the unscaling parameters

        Parameters
        ----------
        scale_factor : Optional[np.number[Any]]
            valid minimum value
        add_offset : Optional[np.number[Any]]
            valid maximum value
        target_dtype : Optional[np.dtype[Any]]
            dtype of the scaled data

        Returns
        -------

        """
        # determine scale factor
        if scale_factor is None and SCALE_FACTOR in self._attrs:
            scale_factor = self._attrs[SCALE_FACTOR]
        # determine offset
        if add_offset is None and ADD_OFFSET in self._attrs:
            add_offset = self._attrs[ADD_OFFSET]
        # determine target_dtype
        if target_dtype is None:
            if DTYPE in self._attrs:
                target_dtype = self._attrs[DTYPE]
            else:
                target_dtype = self._data.dtype
                self._logger.debug(f"{self.path}. Target dtype was not specified, using dtype of the data")
        # Determine fill value
        if FILL_VALUE in self._attrs:
            fill_value = self._attrs[FILL_VALUE]
        elif XARRAY_FILL_VALUE in self.data.attrs:
            fill_value = self.data.attrs[XARRAY_FILL_VALUE]
        else:
            fill_value = None
        return scale_factor, add_offset, target_dtype, fill_value

    def mask(
        self: EOV_MASK_SCALE_TYPE,
        valid_min: Optional[np.number[Any]] = None,
        valid_max: Optional[np.number[Any]] = None,
        fill_value: Optional[np.number[Any]] = None,
        mask_apply: Optional[bool] = None,
        create_mask: Optional[bool] = None,
    ) -> EOV_MASK_SCALE_TYPE:
        """
        Mask the data of the current EOVariable.
        The coordinates are also masked based on their fill_value, valid_min and valid_max attributes, if present.

        Parameters
        ----------
        valid_min : Optional[np.number[Any]]
            valid minimum value
        valid_max : Optional[np.number[Any]]
            valid maximum value
        fill_value : Optional[np.number[Any]]
            fill value
        mask_apply : Optional[bool]
            turn masking on or off
        create_mask : Optional[bool]
            creates a mask as per np.MaskedArray

        """

        eopf_config = EOConfiguration()
        if mask_apply is None:
            mask_apply = eopf_config.get("product__mask_and_scale")
        if create_mask is None:
            create_mask = eopf_config.get("product__create_mask")
        if not mask_apply:
            self._logger.debug(f"{self.path}. Masking not applied: mask_apply is False")
            return self

        valid_min, valid_max, fill_value = self._resolve_mask_params(valid_min, valid_max, fill_value)

        # mask the data
        self._data.data, mask_applied = mask_array(
            self._data.data,
            valid_min=valid_min,
            valid_max=valid_max,
            fill_value=fill_value,
            create_mask=create_mask,
        )

        self._mask_update_eov_attrs(valid_min, valid_max, fill_value)

        # mask the coordinates: all except index coordinates
        mask_applied = self._mask_coords(mask_applied)

        if mask_applied:
            self._attrs[EOV_IS_MASKED] = True

        return self

    def _mask_update_eov_attrs(
        self,
        valid_min: Optional[np.number[Any]] = None,
        valid_max: Optional[np.number[Any]] = None,
        fill_value: Optional[np.number[Any]] = None,
    ) -> None:
        """
        Update the EOV attributes after masking the data

        Parameters
        ----------
         valid_min : Optional[np.number[Any]]
            valid minimum value
        valid_max : Optional[np.number[Any]]
            valid maximum value
        fill_value : Optional[np.number[Any]]
            fill value

        Returns
        -------

        """
        # update eov attrs
        if valid_min is not None or valid_max is not None or fill_value is not None:
            # if one of valid_min, valid_max or fill_value is not None
            # then masking is applied, and eov attrs need to be updated
            if fill_value is None:
                self._attrs[FILL_VALUE] = np.ma.default_fill_value(self._data.data)
            else:
                self._attrs[FILL_VALUE] = fill_value
            self.data.attrs[XARRAY_FILL_VALUE] = self._attrs[FILL_VALUE]
            if valid_min is not None:
                self._attrs[VALID_MIN] = valid_min
                self.data.attrs.pop(VALID_MIN, None)
            if valid_max is not None:
                self._attrs[VALID_MAX] = valid_max
                self.data.attrs.pop(VALID_MAX, None)

    def _resolve_mask_params(
        self,
        valid_min: Optional[np.number[Any]] = None,
        valid_max: Optional[np.number[Any]] = None,
        fill_value: Optional[np.number[Any]] = None,
    ) -> Tuple[Optional[np.number[Any]], Optional[np.number[Any]], Optional[np.number[Any]]]:
        """
        Resolve the masking parameters

        Parameters
        ----------
        valid_min : Optional[np.number[Any]]
            valid minimum value
        valid_max : Optional[np.number[Any]]
            valid maximum value
        fill_value : Optional[np.number[Any]]
            fill value

        Returns
        -------
        Updated params

        """
        # numpy default fill values are considered if not fill value is given
        fill_value = self._resolve_fill_value(fill_value)
        # retrieve valid min and max from EOVar._attrs if not provided via paramters
        if valid_min is None and VALID_MIN in self._attrs:
            valid_min = self._attrs[VALID_MIN]
        if valid_max is None and VALID_MAX in self._attrs:
            valid_max = self._attrs[VALID_MAX]
        # valid_min and valid_max can not be NaN
        if valid_min is not None and np.isnan(valid_min):
            self._logger.debug(f"{self.path}. Ignoring valid_min: should not be NaN")
            valid_min = None
        if valid_max is not None and np.isnan(valid_max):
            self._logger.debug(f"{self.path}. Ignoring valid_max: should not be NaN")
            valid_max = None
        return valid_min, valid_max, fill_value

    def _resolve_fill_value(
        self: EOV_MASK_SCALE_TYPE,
        fill_value: Optional[np.number[Any]],
    ) -> Optional[np.number[Any]]:
        """
         Resolve the fill value to actually use
         Parameters
         ----------
        fill_value : Optional[np.number[Any]]
             fill value

         Returns
         -------
         Updated fill value

        """
        if fill_value is None:
            if FILL_VALUE in self._attrs:
                # when the data has been already masked and scaled
                fill_value = self._attrs[FILL_VALUE]
            elif XARRAY_FILL_VALUE in self._data.attrs:
                # when the data was not masked and scaled
                fill_value = self._data.attrs[XARRAY_FILL_VALUE]
        return fill_value

    def _mask_coords(self: EOV_MASK_SCALE_TYPE, mask_applied: bool) -> bool:
        # mask the coordinates: all except index coordinates
        for coord_name in self._data.coords:
            if coord_name not in self._data.coords.indexes.dims:
                coord = self._data.coords[coord_name]
                coord_valid_min = coord.attrs.get(VALID_MIN, None)
                coord_valid_max = coord.attrs.get(VALID_MAX, None)
                coord_fill_value = coord.attrs.get(FILL_VALUE, None)
                coord.data, mask_applied_on_coord = mask_array(
                    coord.data,
                    valid_min=coord_valid_min,
                    valid_max=coord_valid_max,
                    fill_value=coord_fill_value,
                )
                if mask_applied_on_coord is True:
                    if coord_fill_value is None:
                        coord_fill_value = np.ma.default_fill_value(coord.data)
                    mask_applied = True
                    coord.attrs[FILL_VALUE] = coord_fill_value
                    coord.attrs[XARRAY_FILL_VALUE] = coord_fill_value
                    coord.attrs[EOV_IS_MASKED] = True
        return mask_applied

    @property
    @abstractmethod
    def is_scaled(self: EOV_MASK_SCALE_TYPE) -> bool:
        """Return whether the object is scaled."""

    @property
    @abstractmethod
    def is_masked(self: EOV_MASK_SCALE_TYPE) -> bool:
        """Return whether the object is masked."""

    @property
    @abstractmethod
    def data(self: EOV_MASK_SCALE_TYPE) -> DataArray:
        """Return the data"""

    @property
    @abstractmethod
    def path(self) -> str:
        """str: Path from the top level EOProduct to this object.
        It's a string following Linux path conventions."""

    @property
    @abstractmethod
    def dtype(self) -> DTypeLike:
        """return the dtype of the data"""
