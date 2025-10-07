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
transformers_utils.py

transformers utility functions

"""
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Hashable,
    List,
    Optional,
    Tuple,
    Union,
)
from warnings import warn

import dask.array as da
import dask.dataframe as dd
import lxml
import numpy as np
from lxml import etree
from xarray import DataArray, Dataset, decode_cf

from eopf import EOConfiguration
from eopf.common.constants import (
    ADD_OFFSET,
    DIMENSIONS_NAME,
    DTYPE,
    FILL_VALUE,
    SCALE_FACTOR,
    TARGET_DTYPE,
    VALID_MAX,
    VALID_MIN,
    XARRAY_FILL_VALUE,
)
from eopf.product.eo_variable import EOVariable

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject


def transformation_astype(eo_obj: "EOObject", parameter: str) -> "EOObject":
    """Apply a specific dtype to a scaled variable

    Parameters
    ----------
    eo_obj: EOVariable

    parameter: str
        A string representation of numpy dtype
    """
    try:
        scale_dtype = np.dtype(parameter)
    except KeyError as e:
        raise KeyError("Unknown dtype") from e

    if isinstance(eo_obj, EOVariable):
        if np.issubdtype(parameter, np.datetime64):
            # xarray by default converts to times to nanosecods, see issue below
            # https://github.com/pydata/xarray/issues/4427, 15.02.25
            eov_attrs = eo_obj.attrs
            xds = decode_cf(Dataset({"time": (eo_obj.data.dims, eo_obj.data.data, eo_obj.data.attrs)}))
            # xarray does not like to pass units of datetime as attribute, see section CF time encoding from
            # https://docs.xarray.dev/en/stable/internals/time-coding.html, 15.02.25
            eov_attrs.pop("units", None)
            eov_attrs[DTYPE] = "<M8[ns]"
            eov = EOVariable(
                name=eo_obj.name,
                data=xds["time"],
                attrs=eov_attrs,
                parent=eo_obj.parent,
            )
        else:
            eo_obj.attrs[DTYPE] = parameter
            eov = EOVariable(
                name=eo_obj.name,
                data=eo_obj.data.astype(scale_dtype),
                attrs=eo_obj.attrs,
                dims=eo_obj.dims,
                parent=eo_obj.parent,
            )
        return eov
    return eo_obj


def transformation_expand_dims(eo_obj: "EOObject", parameter: Dict[str, Any]) -> EOVariable:
    """Expand dims of EOVariables data

    Parameters
    ----------
    eo_obj: EOVariable

    parameter: Union[int, Tuple[int]]
        A list or tuple of data dimensions
    """
    if not isinstance(eo_obj, EOVariable):
        raise TypeError("Only eovariable accepted")
    if "axis" not in parameter or "dimensions" not in parameter:
        raise KeyError("Missing parameters")
    eov = EOVariable(
        name=eo_obj.name,
        data=da.expand_dims(eo_obj.data.data, axis=tuple(parameter["axis"])),
        attrs=eo_obj.attrs,
        dims=parameter["dimensions"],
        parent=eo_obj.parent,
    )
    return eov


def transformation_squeeze(eo_obj: "EOObject", parameter: Dict[str, Any]) -> EOVariable:
    """Squeeze EOVariables data such that dims of value 1 are removed

    Parameters
    ----------
    eo_obj: EOVariable

    parameter: Union[int, Tuple[int]]
        A list or tuple of data dimensions
    """
    if not isinstance(eo_obj, EOVariable):
        raise TypeError("Only eovariable accepted")
    if "axis" not in parameter or "dimensions" not in parameter:
        raise KeyError("Missing parameters")

    eov = EOVariable(
        name=eo_obj.name,
        data=da.squeeze(eo_obj.data.data, axis=tuple(parameter["axis"])),
        attrs=eo_obj.attrs,
        dims=parameter["dimensions"],
        parent=eo_obj.parent,
        **eo_obj.kwargs,
    )
    return eov


def transformation_transpose(eo_obj: "EOObject", parameter: Union[List[int], Tuple[int]]) -> EOVariable:
    """Transpose EOVariables data such that raster dims are the last one in the list of dims

    Parameters
    ----------
    eo_obj: EOVariable

    parameter: Union[List[int], Tuple[int]]
        A list or tuple of data dimensions
    """
    if not isinstance(eo_obj, EOVariable):
        raise TypeError("Only eovariable accepted")

    eov = EOVariable(
        name=eo_obj.name,
        data=da.transpose(eo_obj.data.data, axes=parameter),
        dims=eo_obj.dims,
        attrs=eo_obj.attrs,
        parent=eo_obj.parent,
        **eo_obj.kwargs,
    )

    return eov


def transformation_dopplerTime(eo_obj: "EOObject", parameter: Union[List[int], Tuple[int]]) -> EOVariable:
    """Transpose EOVariables data such that raster dims are the last one in the list of dims

    Parameters
    ----------
    eo_obj: EOVariable

    parameter: Union[List[int], Tuple[int]]
        A list or tuple of data dimensions
    """
    if not isinstance(eo_obj, EOVariable):
        raise TypeError("Only eovariable accepted")

    input_data = eo_obj.data.data
    if len(input_data.shape) == 4:
        input_data = input_data.transpose(0, 1, 3, 2)

    new_shape = input_data.shape[:-1]

    # Flatten all dates and convert to dask dataframe
    x = input_data.ravel().reshape(-1, 26)
    df = x.to_dask_dataframe()

    # Each row consists of 26 columns each with one character of the date => join these characters
    df = df.astype(str).map_partitions(lambda pdf: pdf.apply("".join, axis=1), meta=(None, str))
    df = df.map(lambda s: None if set(s) == {"-"} else s, meta=(None, str))
    df = dd.to_datetime(df, format="%Y-%m-%d %H:%M:%S.%f", errors="coerce")

    new_data = df.to_dask_array(lengths=True).reshape(new_shape)

    eov = EOVariable(
        name=eo_obj.name,
        data=new_data,
        attrs=eo_obj.attrs,
        parent=eo_obj.parent,
        **eo_obj.kwargs,
    )
    return eov


def transformation_dimensions(eo_obj: "EOObject", parameter: Any) -> "EOObject":
    """Replace the object dimension with the list of dimensions parameter"""

    if not isinstance(eo_obj, EOVariable):
        pass
    else:
        if isinstance(parameter, str):
            parameter = parameter.split(" ")
        eo_obj.assign_dims(parameter)
        eo_obj._data.attrs[DIMENSIONS_NAME] = eo_obj.dims
    return eo_obj


def transformation_attributes(eo_obj: "EOObject", parameter: Dict[str, Any]) -> "EOObject":
    """Update the object attributes with the dictionary of attribute parameter.
    Mask and scale are applied (depending on EOConfig mask_and_scale flag which is true by default).

    """
    if not isinstance(eo_obj, EOVariable):
        pass
    else:
        # dimensions are treated by a separate transformer
        # we keep them in the mapping for the sake of backwards compatibility
        if "dimensions" in parameter:
            warn(
                "Please remove dimensions from EOVariable attributes tranformer,"
                + "dimensions are treated under dedicated tranformer",
                DeprecationWarning,
            )
            parameter.pop("dimensions")
        if isinstance(eo_obj, EOVariable):
            xarray_attrs, eovar_attrs = eo_obj._parse_attrs(parameter)
            eo_obj._attrs = eovar_attrs
            eo_obj._data.attrs = xarray_attrs

        if DTYPE in parameter:
            eo_obj = transformation_astype(eo_obj, parameter[DTYPE])

    return eo_obj


def transformation_mask_and_scale(eo_obj: "EOObject", parameter: Any) -> "EOObject":
    """
    Mask and scale are applied (depending on EOConfig mask_and_scale flag which is true by default).

    """
    if parameter is None:
        return eo_obj

    if not isinstance(eo_obj, EOVariable):
        return eo_obj

    mask_and_scale_apply: Optional[bool] = parameter.pop("mask_and_scale", None)
    if mask_and_scale_apply is None:
        eopf_config = EOConfiguration()
        mask_and_scale_apply = bool(eopf_config.get("product__mask_and_scale"))

    eo_obj = _transformation_mask(eo_obj, mask_and_scale_apply, parameter)
    return _transformation_scale(eo_obj, mask_and_scale_apply, parameter)


def _transformation_mask(eo_obj: "EOObject", mask_and_scale_apply: bool, parameter: Any) -> "EOObject":
    """
    Mask are applied (depending on EOConfig mask_and_scale flag which is true by default).

    """
    if not isinstance(eo_obj, EOVariable):
        return eo_obj

    # masking
    # retrieve masking parameters and update EOV attrs
    valid_min = parameter.get(VALID_MIN, None)
    valid_max = parameter.get(VALID_MAX, None)
    fill_value = parameter.get(FILL_VALUE, None)
    if mask_and_scale_apply:
        # apply masking
        eo_obj.mask(valid_min=valid_min, valid_max=valid_max, fill_value=fill_value, mask_apply=mask_and_scale_apply)
    else:
        # do not apply masking but update EOV._data.attrs
        if valid_min is not None:
            eo_obj._data.attrs[VALID_MIN] = valid_min
            eo_obj._attrs[VALID_MIN] = valid_min
        if valid_max is not None:
            eo_obj._data.attrs[VALID_MAX] = valid_max
            eo_obj._attrs[VALID_MAX] = valid_max
        if fill_value is not None:
            eo_obj._data.attrs[XARRAY_FILL_VALUE] = fill_value
            eo_obj._attrs[FILL_VALUE] = fill_value

    return eo_obj


def _transformation_scale(eo_obj: "EOObject", mask_and_scale_apply: bool, parameter: Any) -> "EOObject":
    """
    Scale is applied (depending on EOConfig mask_and_scale flag which is true by default).

    """
    if not isinstance(eo_obj, EOVariable):
        return eo_obj

    # scaling
    # retrieve scaling parameters and update EOV attrs
    scale_factor = parameter.get(SCALE_FACTOR, None)
    add_offset = parameter.get(ADD_OFFSET, None)
    target_dtype = parameter.get(TARGET_DTYPE, None)

    if mask_and_scale_apply:
        # apply scaling
        eo_obj.scale(scale_factor, add_offset, target_dtype=target_dtype, scale_apply=mask_and_scale_apply)
        return eo_obj
    # do not apply scalling but update EOV._data.attrs and EOV._attrs to allow future scaling
    if scale_factor is not None:
        eo_obj._data.attrs[SCALE_FACTOR] = scale_factor
        eo_obj._attrs[SCALE_FACTOR] = scale_factor
    if add_offset is not None:
        eo_obj._data.attrs[ADD_OFFSET] = add_offset
        eo_obj._attrs[ADD_OFFSET] = add_offset
    if target_dtype is not None:
        eo_obj.attrs[TARGET_DTYPE] = target_dtype

    return eo_obj


def transformation_sub_array(eo_obj: "EOObject", parameter: Any) -> EOVariable:
    """Index the array according to the parameter. If the parameter is a single index, the dimension is removed."""
    if not isinstance(eo_obj, EOVariable):
        raise TypeError("Only eovariable accepted")
    return eo_obj.isel(parameter)


def _block_pack_bit(array: np.ndarray[Any, Any], *args: Any, **kwargs: Any) -> np.ndarray[Any, Any]:
    result = np.packbits(array, *args, **kwargs)
    return result.squeeze(axis=kwargs["axis"])


def transformation_pack_bits(eo_obj: "EOObject", parameter: Any) -> EOVariable:
    """Pack bit the parameter dimension of eo_obj."""

    if not isinstance(eo_obj, EOVariable):
        raise TypeError("Only eovariable accepted")
    attrs = eo_obj.attrs
    dims: list[str] = []
    for dim in eo_obj._data.dims:
        dims.append(str(dim))
    if isinstance(parameter, str):
        dim_key = parameter
        dim_index = dims.index(parameter)
    else:
        dim_key = dims[parameter]
        dim_index = parameter

    kwargs = {"axis": dim_index, "drop_axis": dim_index, "bitorder": "little"}
    # drop_axis is used by dask to estimate the new shape.
    # axis and bitorder are packbits parameters.
    data = _xarray_to_data_map_block(_block_pack_bit, eo_obj._data, **kwargs)
    dims.remove(dim_key)
    return EOVariable(data=data, dims=tuple(dims), attrs=attrs)


def transformation_rechunk(eo_obj: "EOObject", parameter: dict[str, Any]) -> "EOObject":
    """Pack bit the parameter dimension of eo_obj."""

    if not isinstance(eo_obj, EOVariable):
        return eo_obj

    chunk_size_by_dim: dict[Hashable, int] = {}
    for dim in eo_obj.sizes:
        if dim in parameter:
            chunk_size_by_dim[dim] = parameter[str(dim)]

    return eo_obj.chunk(chunk_size_by_dim)


def transformation_scale(eo_obj: "EOObject", parameter: dict[str, Any]) -> "EOObject":
    """
    scaling transform

    Parameters
    ----------
    eo_obj
    parameter

    Returns
    -------

    """
    if not isinstance(eo_obj, EOVariable):
        raise TypeError("Only eovariable accepted")

    required_keys = ["basepath", "relpath", "spacing", "n_lines"]

    if not all(key in parameter for key in required_keys):
        raise KeyError("Missing parameters")

    # Open annotation file
    abspath = parameter["basepath"] / parameter["relpath"]
    with abspath.open("r") as fin:
        tree = etree.parse(fin)

    spacing_tag = tree.xpath("//" + parameter["spacing"])
    n_lines_tag = tree.xpath("//" + parameter["n_lines"])
    if (
        isinstance(spacing_tag, list)
        and isinstance(n_lines_tag, list)
        and isinstance(spacing_tag[0], lxml.etree._Element)
        and isinstance(n_lines_tag[0], lxml.etree._Element)
        and hasattr(spacing_tag[0], "text")
        and hasattr(n_lines_tag[0], "text")
    ):
        # Extract elements matching the XPath expressions
        spacing = np.float32(str(spacing_tag[0].text))
        n_lines = np.int16(str(n_lines_tag[0].text))
        coeff = spacing * (n_lines - 1)
        # Scale variable
        return eo_obj * coeff
    return eo_obj


def _xarray_to_data_map_block(
    func: Callable[[Any], Any],
    data_array: DataArray,
    *args: Any,
    **kwargs: Any,
) -> da.Array:
    array = data_array.data
    if isinstance(array, da.Array):
        return da.map_blocks(func, array, *args, **kwargs)
    return func(array, *args, **kwargs)
