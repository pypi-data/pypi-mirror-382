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
overlap.py

Xarray map overlap implementation as it s not yet provided in xarray

"""
import functools
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Hashable, TypeVar

import dask.array
import dask.array.overlap
import xarray as xr
from dask.array import Array as DaskArray
from xarray import DataArray, Dataset

T_Xarray = TypeVar("T_Xarray", "DataArray", "Dataset")


def _get_dask_depth_or_boundary(
    depth_or_boundary: Any | Mapping[Hashable, Any],
    obj: T_Xarray,
) -> Any | Mapping[Hashable, Any]:
    """
    Get the dask boundaries corresponding to dims
    Parameters
    ----------
    depth_or_boundary
    obj

    Returns
    -------

    """
    if not isinstance(depth_or_boundary, dict):
        return depth_or_boundary

    if unknown_dims := set(obj.dims) - set(depth_or_boundary):
        raise ValueError(f"Unknown 'depth' or 'boundary' dimensions: {unknown_dims!r}.")
    return {obj.get_axis_num(dim): depth_or_boundary[dim] for dim in obj.dims}


def _apply_dask_array_overlap_func(
    func: Callable[..., DaskArray],
    obj: T_Xarray,
    depth: int | tuple[int, int] | Mapping[Hashable, int | tuple[int, int]],
    boundary: Any | Mapping[Hashable, Any],
    add_coords: bool = True,
) -> T_Xarray:
    """
    Apply the dask function with overap
    Parameters
    ----------
    func
    obj
    depth
    boundary
    add_coords

    Returns
    -------

    """
    if obj.chunks is None:
        raise ValueError("Object is not chunked.")

    coords = {}
    if add_coords:
        for name, dataarray in obj.coords.items():
            data = dataarray.data
            if not isinstance(data, DaskArray):
                data = dask.array.from_array(
                    data,
                    chunks=tuple(obj.chunksizes[dim] for dim in dataarray.dims),
                )
            data = func(
                data,
                depth=_get_dask_depth_or_boundary(depth, dataarray),
                boundary=_get_dask_depth_or_boundary(boundary, dataarray),
            )
            coords[name] = DataArray(data, dims=dataarray.dims, attrs=dataarray.attrs)

    if isinstance(obj, DataArray):
        data = func(
            obj.data,
            depth=_get_dask_depth_or_boundary(depth, obj),
            boundary=_get_dask_depth_or_boundary(boundary, obj),
        )
        return DataArray(data, name=obj.name, dims=obj.dims, coords=coords, attrs=obj.attrs)

    data_vars = {
        name: _apply_dask_array_overlap_func(func, dataarray, depth=depth, boundary=boundary, add_coords=False)
        for name, dataarray in obj.data_vars.items()
    }
    return Dataset(data_vars, coords=coords, attrs=obj.attrs)


def map_overlap(
    func: Callable[..., T_Xarray],
    obj: T_Xarray,
    args: Sequence[T_Xarray] = (),
    kwargs: Mapping[str, Any] | None = None,
    template: T_Xarray | None = None,
    depth: int | tuple[int, int] | Mapping[Hashable, int | tuple[int, int]] = 0,
    boundary: Any | Mapping[Hashable, Any] = "reflect",
    trim: bool = True,
) -> T_Xarray:
    """Apply a function to each block of a DataArray or Dataset with some overlap.

    Parameters
    ----------
    func : callable
        User-provided function that accepts a DataArray or Dataset as its first
        parameter ``obj``. The function will receive a subset or 'block' of ``obj`` (see below),
        corresponding to one chunk along each chunked dimension. ``func`` will be
        executed as ``func(subset_obj, *subset_args, **kwargs)``.

        This function must return either a single DataArray or a single Dataset.

        This function cannot add a new chunked dimension.
    obj : DataArray, Dataset
        Passed to the function as its first argument, one block at a time.
    args : sequence
        Passed to func after unpacking and subsetting any xarray objects by blocks.
        xarray objects in args must be aligned with obj, otherwise an error is raised.
    kwargs : mapping
        Passed verbatim to func after unpacking. xarray objects, if any, will not be
        subset to blocks. Passing dask collections in kwargs is not allowed.
    template : DataArray or Dataset, optional
        xarray object representing the final result after compute is called. If not provided,
        the function will be first run on mocked-up data, that looks like ``obj`` but
        has sizes 0, to determine properties of the returned object such as dtype,
        variable names, attributes, new dimensions and new indexes (if any).
        ``template`` must be provided if the function changes the size of existing dimensions.
        When provided, ``attrs`` on variables in `template` are copied over to the result. Any
        ``attrs`` set by ``func`` will be ignored.
    depth : int, tuple, dict
        The number of elements that each block should share with its neighbours
        If a dict then this can be different per dimension.
        Asymmetric depths may be specified using tuples.
    boundary : str, scalar, dict
        How to handle the boundaries.
        Values include 'reflect', 'periodic', 'nearest', 'none',
        or any constant value like 0 or np.nan.
        If a dict then this can be different per dimension.
    trim : bool
        Whether or not to trim ``depth`` elements from each block after
        calling the map function.
        Set this to False if your mapping function already does this for you.

    Returns
    -------
    obj : same as obj
        A single DataArray or Dataset with dask backend, reassembled from the outputs of the
        function.

    See Also
    --------
    dask.array.map_overlap, xarray.map_blocks

    Examples
    --------
    >>> import numpy as np
    >>> import xarray as xr
    >>> from eopf.computing import map_overlap
    >>> def correlate(obj, kernel):
    ...     return (
    ...         obj.rolling(dict(zip(obj.dims, kernel.shape)), center=True)
    ...         .construct(dict(zip(obj.dims, kernel.dims)))
    ...         .dot(kernel)
    ...     )
    >>> obj = xr.DataArray(np.arange(25).reshape(5, 5), dims=("x", "y"), name="foo").chunk(2)
    >>> kernel = xr.DataArray([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dims=("xk", "yk"))
    >>> correlation = map_overlap(
    ...     correlate,
    ...     obj,
    ...     kwargs={"kernel": kernel},
    ...     depth=1,
    ...     boundary="reflect",
    ...     template=obj,
    ... )
    >>> correlation.compute()
    <xarray.DataArray 'foo' (x: 5, y: 5)> Size: 200B
    array([[  6.,  10.,  15.,  20.,  24.],
           [ 26.,  30.,  35.,  40.,  44.],
           [ 51.,  55.,  60.,  65.,  69.],
           [ 76.,  80.,  85.,  90.,  94.],
           [ 96., 100., 105., 110., 114.]])
    Dimensions without coordinates: x, y
    """
    # Apply dask.array.overlap.overlap to all xarray's objects
    # excluding kwargs as passing dask collections in kwargs is not allowed.
    apply_overlap = functools.partial(
        _apply_dask_array_overlap_func,
        func=dask.array.overlap.overlap,
        depth=depth,
        boundary=boundary,
    )
    obj = apply_overlap(obj=obj)
    args = tuple(apply_overlap(obj=arg) if isinstance(arg, DataArray | Dataset) else arg for arg in args)
    if trim and template is not None:
        template = apply_overlap(obj=template)

    obj = xr.map_blocks(
        func,
        obj,
        args=args,
        kwargs=kwargs,
        template=template,
    )
    if trim:
        obj = _apply_dask_array_overlap_func(
            dask.array.overlap.trim_overlap,
            obj,
            depth=depth,
            boundary=boundary,
        )
    return obj
