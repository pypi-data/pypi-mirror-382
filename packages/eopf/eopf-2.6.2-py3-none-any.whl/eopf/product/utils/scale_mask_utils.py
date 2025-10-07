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
scale_mask_utils.py

utilities for mask and scale on eoproducts

"""
from typing import Any, Optional

import dask.array as da
import numpy as np
from xarray import DataArray

from eopf.common.functions_utils import catch_and_raise
from eopf.exceptions.errors import MaskingError, ScalingError


@catch_and_raise(MaskingError)
def mask_array(
    data: da.Array,
    valid_min: Optional[np.number[Any]],
    valid_max: Optional[np.number[Any]],
    fill_value: Optional[np.number[Any]],
    create_mask: Optional[bool] = False,
) -> tuple[da.Array, bool]:
    """
    Mask a dask array

    Parameters
    ----------
    create_mask
    data : da.Array
        dask array to mask
    valid_min : Optional[np.number[Any]]
        valid minimum value
    valid_max : Optional[np.number[Any]]
        valid maximum value
    fill_value : Optional[np.number[Any]]
        fill value

    Returns
    -------
    da.Array
    masked_applied
    """

    masked_applied: bool = False
    # do not apply when all parameters are None
    if valid_min is None and valid_max is None and fill_value is None:
        return data, masked_applied

    # non numeric data types will not be masked
    if not np.issubdtype(data.dtype, np.number):
        return data, masked_applied

    masked_applied = True

    # if no fill_value is given then use numpy default
    if fill_value is None:
        fill_value = np.ma.default_fill_value(data)

    # data may be already masked but not marked as masked
    mask = da.logical_or(False, data == fill_value)

    if valid_min is not None:
        mask = da.logical_or(mask, data < valid_min)
    if valid_max is not None:
        mask = da.logical_or(mask, data > valid_max)

    if create_mask is True:
        return da.ma.masked_array(data, mask, fill_value=fill_value), masked_applied

    return da.where(mask, np.nan, data), masked_applied


@catch_and_raise(ScalingError)
def scale_dask_array(
    data: da.Array,
    scale_factor: Optional[np.number[Any]],
    add_offset: Optional[np.number[Any]],
    target_dtype: Optional[np.dtype[Any]],
) -> tuple[da.Array, bool]:
    """
    Scale and/or offset a dask array

    Parameters
    ----------
    data : da.Array
        dask array to mask
    scale_factor : Optional[np.number[Any]]
        valid minimum value
    add_offset : Optional[np.number[Any]]
        valid maximum value
    target_dtype: Optional[np.dtype[Any]]
        force dtype after scaling/offsetting

    Returns
    -------
    da.Array
    scale_applied
    """

    scale_applied: bool = False

    if scale_factor is None and add_offset is None and target_dtype is None:
        return data, scale_applied

    # non numeric data types will not be scaled
    if not np.issubdtype(data.dtype, np.number):
        return data, scale_applied

    # the data mask is needed to avoid scaling masked data
    if hasattr(data, "_meta") and isinstance(data._meta, np.ma.core.MaskedArray):
        data_mask = da.ma.getmaskarray(data)
    else:
        data_mask = False

    # apply scale factor if present
    if scale_factor is not None:  # for these 0 is also ignored
        scale_applied = True
        data = da.multiply(data, scale_factor, where=not data_mask)  # noqa: E712

    # apply offset if present
    if add_offset is not None:
        scale_applied = True
        data = da.add(data, add_offset, where=not data_mask)  # noqa: E712

    # make sure the scaled data has the target_dtype if present
    if target_dtype is not None:
        scale_applied = True
        data = data.astype(target_dtype)

    return data, scale_applied


@catch_and_raise(ScalingError)
def scale_numpy_array(
    data: DataArray,
    scale_factor: Optional[np.number[Any]],
    add_offset: Optional[np.number[Any]],
    target_dtype: Optional[np.dtype[Any]],
) -> tuple[DataArray, bool]:
    """
    Scale and/or offset a numpy array

    Parameters
    ----------
    data : DataArray
        dask array to mask
    scale_factor : Optional[np.number[Any]]
        valid minimum value
    add_offset : Optional[np.number[Any]]
        valid maximum value
    target_dtype: Optional[np.dtype[Any]]
        force dtype after scaling/offsetting

    Returns
    -------
    da.Array
    scale_applied
    """

    try:
        scale_applied: bool = False

        if scale_factor is None and add_offset is None and target_dtype is None:
            return data, scale_applied

        # non numeric data types will not be scaled
        if not np.issubdtype(data.dtype, np.number):
            return data, scale_applied

        scale_applied = True

        # the data mask is needed to avoid scalling masked data
        if isinstance(data, np.ma.core.MaskedArray):
            data_mask = data.mask
        else:
            data_mask = False

        # apply scale factor if present
        if scale_factor is not None:  # for these 0 is also ignored
            data = DataArray(np.multiply(data, scale_factor, where=not data_mask))  # noqa: E712

        # apply offset if present
        if add_offset is not None:
            data = DataArray(np.add(data, add_offset, where=not data_mask))  # noqa: E712

        # make sure the scaled data has the target_dtype if present
        if target_dtype is not None:
            data = data.astype(target_dtype)

        return data, scale_applied
    except Exception as e:
        raise ScalingError(f"{e}") from e


@catch_and_raise(ScalingError)
def scale_val(
    val: np.number[Any],
    scale_factor: Optional[np.number[Any]],
    add_offset: Optional[np.number[Any]],
    target_dtype: Optional[np.dtype[Any]],
) -> np.number[Any]:
    """
    Scale and/or offset a numpy number

    Parameters
    ----------
    val
    data : da.Array
        dask array to mask
    scale_factor : Optional[np.number[Any]]
        valid minimum value
    add_offset : Optional[np.number[Any]]
        valid maximum value
    target_dtype: Optional[np.dtype[Any]]
        force dtype after scaling/offsetting

    Returns
    -------
    np.number[Any]
    """

    try:
        # apply scale factor if present
        if scale_factor is not None:  # for these 0 is also ignored
            val = np.multiply(val, scale_factor)

        # apply offset if present
        if add_offset is not None:
            val = np.add(val, add_offset)

        # make sure the scaled val has the target_dtype if present
        if target_dtype is not None:
            val = np.dtype(target_dtype).type(val)

        return val
    except Exception as e:
        raise ScalingError(f"{e}") from e


@catch_and_raise(ScalingError)
def unscale_val(
    val: np.number[Any],
    scale_factor: Optional[np.number[Any]],
    add_offset: Optional[np.number[Any]],
    target_dtype: Optional[np.dtype[Any]],
) -> np.number[Any]:
    """
    Scale and/or offset a numpy number

    Parameters
    ----------
    val
    data : da.Array
        dask array to mask
    scale_factor : Optional[np.number[Any]]
        valid minimum value
    add_offset : Optional[np.number[Any]]
        valid maximum value
    target_dtype: Optional[np.dtype[Any]]
        force dtype after scaling/offsetting

    Returns
    -------
    np.number[Any]
    """

    # apply offset if present
    if add_offset is not None:
        val = np.subtract(val, add_offset)

    # apply scale factor if present
    if scale_factor is not None:  # for these 0 is also ignored
        val = np.divide(val, scale_factor)

    # make sure the unscaled val has the target_dtype if present
    if target_dtype is not None:
        val = np.dtype(target_dtype).type(val)

    return val


@catch_and_raise(ScalingError)
def unscale_array(
    data: da.Array,
    scale_factor: Optional[np.number[Any]],
    add_offset: Optional[np.number[Any]],
    target_dtype: Optional[np.dtype[Any]],
    fill_value: Optional[np.dtype[Any]],
) -> tuple[da.Array, bool]:
    """
    Un-scale and/or un-offset a dask array

    Parameters
    ----------
    fill_value
    data : da.Array
        dask array to mask
    scale_factor : Optional[np.number[Any]]
        valid minimum value
    add_offset : Optional[np.number[Any]]
        valid maximum value
    target_dtype: Optional[np.dnp.dtype[Any]]
        force dtype after un-scaling/un-offsetting

    Returns
    -------
    da.Array
    unscale_applied
    """
    unscale_applied: bool = False

    # non numeric data types will not be unscaled
    if not np.issubdtype(data.dtype, np.number):
        return data, unscale_applied

    # Get the not mask if the data is masked, return None if not masked
    data_mask_inversed = _get_array_mask(data)

    # unapply offset if present
    if add_offset is not None:
        if data_mask_inversed is not None:
            data = da.subtract(data, add_offset, where=data_mask_inversed)
        else:
            data = da.subtract(data, add_offset)
        unscale_applied = True

    # unapply scale factor if present
    if scale_factor is not None:  # for these 0 is also ignored
        if data_mask_inversed is not None:
            data = da.divide(data, scale_factor, where=data_mask_inversed)
        else:
            data = da.divide(data, scale_factor)
        unscale_applied = True

    # make sure the unscaled data has the target_dtype if present
    if target_dtype is not None:
        if data_mask_inversed is None:
            # replace nan with fill_value
            if fill_value is None:
                fill_value = np.ma.default_fill_value(data)
            data = da.where(da.isnan(data), fill_value, data)
        # round to the nearest integer as encoded data should always be integers
        if np.issubdtype(target_dtype, np.integer):
            data = da.round(data)
        data = data.astype(target_dtype)
        unscale_applied = True

    return data, unscale_applied


def _get_array_mask(data: da.Array) -> Any:
    """
    Get the "not mask" of the array if the array is masked, else return None
    Parameters
    ----------
    data : input array

    Returns
    -------
    not mask if masker, else None
    """
    if hasattr(data, "_meta") and isinstance(data._meta, np.ma.core.MaskedArray):
        # the data mask is needed to avoid unscalling masked data
        return not da.ma.getmaskarray(data)
    return None
