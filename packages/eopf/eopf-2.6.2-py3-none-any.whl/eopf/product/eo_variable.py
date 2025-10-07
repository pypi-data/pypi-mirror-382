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
eo_vartiable.py

EOVariable implementation file

"""
import ast
import copy
import os
import pprint
from typing import (
    Any,
    Callable,
    Hashable,
    Iterator,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
    Union,
    cast,
)

import xarray
from dask import array as da
from numpy.typing import DTypeLike
from xarray import DataArray
from xarray.core.types import ErrorOptionsWithWarn

from eopf.common.constants import (
    ADD_OFFSET,
    COORDINATES,
    DIMENSIONS,
    DIMENSIONS_NAME,
    DTYPE,
    EOV_IS_MASKED,
    EOV_IS_SCALED,
    FILL_VALUE,
    FLAG_MASKS,
    FLAG_MEANINGS,
    FLAG_VALUES,
    LONG_NAME,
    SCALE_FACTOR,
    STANDARD_NAME,
    UNITS,
    XARRAY_FILL_VALUE,
    Style,
)
from eopf.common.file_utils import AnyPath
from eopf.common.type_utils import Chunk
from eopf.config.config import EOConfiguration
from eopf.exceptions.errors import (
    EOVariableInvalidDimensionsError,
    EOVariableSubSetError,
)
from eopf.logging import EOLogging
from eopf.product.eo_mixins import (
    EOVariableEqualMixin,
    EOVariableOperatorsMixin,
    EOVariableScaleMaskMixin,
)
from eopf.product.eo_object import EOObject, EOObjectWithDims

# EOVar attrs that are gathered from xarray attrs
XARRAY_TO_EOV_ATTRS = [
    FILL_VALUE,
    ADD_OFFSET,
    SCALE_FACTOR,
    UNITS,
    FLAG_VALUES,
    FLAG_MASKS,
    FLAG_MEANINGS,
    DIMENSIONS,
    STANDARD_NAME,
    LONG_NAME,
    DTYPE,
]

# Conversion from xarray names to eovar names
XARRAY_TO_EOV_NAME_CONVERSION: dict[str, str] = {DIMENSIONS_NAME: DIMENSIONS, XARRAY_FILL_VALUE: FILL_VALUE}

# Conversion from xarray names to eovar names
EOV_TO_XARRAY_NAME_CONVERSION: dict[str, str] = {FILL_VALUE: XARRAY_FILL_VALUE, DIMENSIONS: DIMENSIONS_NAME}


class EOVariable(
    EOObjectWithDims,
    EOVariableOperatorsMixin["EOVariable"],
    EOVariableScaleMaskMixin["EOVariable"],
    EOVariableEqualMixin,
):
    """Wrapper around xarray.DataArray to provide Multi dimensional Array (Tensor)
    in earth observation context

    Parameters
    ----------
    name: str, optional
        name of this group
    data: any, optional
        any data accept by :obj:`xarray.DataArray`
    parent: EOProduct or EOGroup, optional
        parent to link to this group
    attrs: MutableMapping[str, Any], optional
        attributes to assign to eovar attrs, no xarray update
    dims: tuple[str], optional
        dimensions to assign
    **kwargs: Any
        any arguments to construct an :obj:`xarray.DataArray`

    See Also
    --------
    xarray.DataArray
    """

    def __init__(
        self,
        name: str = "",
        data: Optional[Any] = None,
        parent: Optional["EOObject"] = None,
        attrs: Optional[MutableMapping[str, Any]] = None,
        dims: tuple[str, ...] = tuple(),
        **kwargs: Any,
    ):
        self._logger = EOLogging().get_logger("eopf.product.eo_variable")

        # Keep compatibility with 2.0.0
        if "mask_and_scale" in kwargs:
            kwargs.pop("mask_and_scale")

        # Parse attrs to keep only valid ones, purely xarray attributes are filtered out
        xarray_attrs, eovar_attrs = self._parse_attrs(attrs)
        self._attrs: dict[str, Any] = eovar_attrs

        xarray_attrs = self._init_data(xarray_attrs, name, data, **kwargs)

        if not dims:
            external_dims = xarray_attrs.pop(DIMENSIONS, None)  # ignore data.attrs to give priority to data.dims
            dims = external_dims or self._data.dims  # type: ignore[assignment]
        if isinstance(dims, str):
            # in some cases, the dims can be a string
            if dims.startswith("["):
                dims = ast.literal_eval(dims)
            else:
                dims = dims.split(" ")

        # test if the given parent is an EOGroup
        # Lazy import for circular deps
        from eopf.product.eo_group import (
            EOGroup,  # pylint: disable=import-outside-toplevel
        )

        if parent is not None and not isinstance(parent, EOGroup):
            raise TypeError("Only eogroup accepted as parent of variable")

        super().__init__(name, parent, dims=tuple(dims))

    def _init_data(
        self,
        xarray_attrs: dict[str, Any],
        name: str = "",
        data: Optional[Any] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Initialize the internal data from incomming data

        Parameters
        ----------
        xarray_attrs : xarray attrs extracted from init attrs
        name : name of the variable, will also be the name in the xarray
        data : actual data, can be anything, will try to map it to dataarray
        kwargs : any other args passed to xarray constructor

        Returns
        -------
        Updated xarray attrs dict in case the input data is an xarray

        """
        if isinstance(data, EOVariable):
            data = data._data  # xarray.DataArray
        xda_data: xarray.DataArray
        if data is None:
            xda_data = xarray.DataArray(name=name, attrs=xarray_attrs, **kwargs)
        elif isinstance(data, xarray.DataArray):
            xarray_attrs = data.attrs | xarray_attrs  # prioritise attrs over data.attrs
            xda_data = data.copy()
        else:  # generic numpy/dask like array
            try:
                lazy_data = da.asarray(data)
            except NotImplementedError:
                # Some types of data don't support a method used by dask
                # when it ask the data size in order to choose the optimal chunk size.
                lazy_data = da.asarray(data, chunks=2000)
            xda_data = xarray.DataArray(data=lazy_data, name=name, attrs=xarray_attrs, **kwargs)
            if hasattr(data, "dtype"):
                xda_data = xda_data.astype(data.dtype)
        self._data: xarray.DataArray = xda_data
        return xarray_attrs

    def _init_similar(self, data: xarray.DataArray) -> "EOVariable":
        # let the current data working with their dimensions
        attrs = copy.deepcopy(self.attrs)
        attrs.pop(DIMENSIONS, None)
        dims = self.dims if len(data.shape) == len(self.dims) else tuple()
        return EOVariable(data=data, attrs=attrs, dims=dims)

    def assign_dims(self, dims: tuple[Hashable, ...]) -> None:
        dims = tuple(dims)
        if len(dims) != len(self._data.dims):
            raise EOVariableInvalidDimensionsError(
                f"Invalid number of dimensions : given {dims} while expected {len(self._data.dims)}.",
            )
        self._data.attrs[DIMENSIONS_NAME] = dims
        if self._data.dims != dims:
            self._data = self._data.swap_dims(dict(zip(self._data.dims, dims)))
            if isinstance(self._data, DataArray):
                current_dims = self._data.dims
                new_dims_dict = {}
                for idx, v in enumerate(current_dims):
                    new_dims_dict[v] = dims[idx]
                self._data.rename(new_dims_dict)

    def assign_coords(self, *args: Any, **kwargs: Any) -> "EOVariable":
        """
        Shortcut to assign on the underlying xarray
        """
        self._data = self._data.assign_coords(*args, **kwargs)
        return self

    def astype(self, dtype: DTypeLike, **kwargs: Any) -> "EOVariable":
        # kwargs are ignored for the moment, however in the future
        # they might be used
        return self._init_similar(self._data.data.astype(dtype))

    # docstr-coverage: inherited
    @property
    def coords(self) -> Any:
        return self._data.coords

    @property
    def chunksizes(self) -> Mapping[Any, tuple[int, ...]]:
        """
        Mapping from dimension names to block lengths for this dataarray's data, or None if
        the underlying data is not a dask array.

        Cannot be modified directly, but can be modified by calling .chunk().
        Differs from EOVariable.chunks because it returns a mapping of dimensions to chunk shapes
        instead of a tuple of chunk shapes.

        See Also
        --------
        EOVariable.chunk
        EOVariable.chunks
        """
        return self._data.chunksizes

    @property
    def chunks(self) -> Optional[tuple[tuple[int, ...], ...]]:
        """
        Tuple of block lengths for this dataarray's data, in order of dimensions, or None if
        the underlying data is not a dask array.

        See Also
        --------
        EOVariable.chunk
        EOVariable.chunksizes
        """
        return self._data.chunks

    @property
    def data(self) -> DataArray:
        return self._data

    @property
    def sizes(self) -> Mapping[Hashable, int]:
        """
        Ordered mapping from dimension names to lengths.
        Immutable.
        """
        return self._data.sizes

    @property
    def ndim(self) -> int:
        return self.data.ndim

    @property
    def loc(self) -> "_LocIndexer":
        return _LocIndexer(self._init_similar(self._data))

    @property
    def shape(self) -> tuple[int, ...]:
        return self._data.shape

    @property
    def datasize(self) -> int:
        """
        Compute the data size in bytes

        Returns
        -------

        """
        return self._data.size * self._data.dtype.itemsize + sum(
            coord.size * coord.dtype.itemsize for coord in self._data.coords.values()
        )

    def compute(self, **kwargs: Any) -> "EOVariable":
        """Manually triggers loading of this array's data from disk or a
        remote source into memory and return a new array. The original is
        left unaltered.

        Normally, it should not be necessary to call this method in user code,
        because all xarray functions should either work on deferred data or
        load_file data automatically. However, this method can be necessary when
        working with many file objects on disk.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments passed on to ``dask.compute``.

        See Also
        --------
        xarray.DataArray.compute
        dask.compute
        """
        return self._init_similar(self._data.compute(**kwargs))

    def graph(self, folder: Optional[AnyPath]) -> None:
        """
        Export dask graph of the data

        Parameters
        ----------
        folder : folder to write the graph to

        Returns
        -------

        """
        if folder is None and not EOConfiguration().has_value("dask__export_graphs"):
            # nothing to do
            return
        folder_out: str = EOConfiguration().dask__export_graphs if folder is None else folder.path
        da.asarray(self._data.data).visualize(
            filename=os.path.join(
                folder_out,
                self.product.name + "_" + self.path.replace(os.sep, "__") + "_" + self.name + ".svg",
            ),
        )

    @property
    def attrs(self) -> dict[str, Any]:
        """
        CF eovar attrs are updated using the xarray attrs that have CF correspondences.

        Return
        ----------
        dict[str, Any]: Attributes defined by this object

        """
        # CF attributes coming from the xarray attributes are converted to EOVar attributes
        for xarray_attr_name in self._data.attrs.keys():
            eovar_attr_name = XARRAY_TO_EOV_NAME_CONVERSION.get(xarray_attr_name, xarray_attr_name)
            if eovar_attr_name in XARRAY_TO_EOV_ATTRS:
                self._attrs[eovar_attr_name] = self._data.attrs[xarray_attr_name]

        # add coordinates attr from the data if it exists
        if len(self._data.coords) > 0:
            self._attrs[COORDINATES] = tuple(self._data.coords)
        else:
            self._attrs.pop(COORDINATES, None)

        return self._attrs

    @attrs.setter
    def attrs(self, new_attrs: dict[str, Any]) -> None:
        # keep only valid CF attrs for eovar and not for the xarray
        _, eovar_attrs = self._parse_attrs(new_attrs)
        self._attrs.update(eovar_attrs)

    def chunk(
        self,
        chunks: Optional[Chunk] = None,
        name_prefix: str = "eopf-",
        token: Optional[str] = None,
        lock: bool = False,
    ) -> "EOVariable":
        """Coerce this array's data into a dask arrays with the given chunks.
        If this variable is a non-dask array, it will be converted to dask
        array. If it's a dask array, it will be rechunked to the given chunk
        sizes.

        If neither chunks is not provided for one or more dimensions, chunk
        sizes along that dimension will not be updated; non-dask arrays will be
        converted into dask arrays with a single block.

        Parameters
        ----------
        chunks : int, tuple of int or mapping of hashable to int, optional
            Chunk sizes along each dimension, e.g., ``5``, ``(5, 5)`` or
            ``{'x': 5, 'y': 5}``.
        name_prefix : str, optional
            Prefix for the name of the new dask array.
        token : str, optional
            Token uniquely identifying this array.
        lock : optional
            Passed on to :py:func:`dask.array.from_array`, if the array is not
            already as dask array.

        Returns
        -------
        chunked : eopf.product.EOVariable
        """
        if chunks is None:
            chunks = {}
        if not isinstance(chunks, dict):
            self._data = self._data.chunk(chunks, name_prefix=name_prefix, token=token, lock=lock)
        else:
            chunk_size_by_dim: dict[Hashable, int] = {}
            for dim, _ in self.sizes.items():
                if dim in chunks:
                    chunk_size_by_dim[dim] = chunks[str(dim)]
            self._data = self._data.chunk(chunk_size_by_dim, name_prefix=name_prefix, token=token, lock=lock)
        return self

    @property
    def dtype(self) -> DTypeLike:
        return self.data.dtype

    @property
    def is_scaled(self) -> bool:
        """
        An EOVar is scaled if EOV_IS_SCALED is True and under EOVar attributes
        """
        return EOV_IS_SCALED in self._attrs and self._attrs[EOV_IS_SCALED]

    @property
    def is_masked(self) -> bool:
        return EOV_IS_MASKED in self._attrs and self._attrs[EOV_IS_MASKED]

    @property
    def dims(self) -> tuple[str, ...]:
        """tuple[str, ...]: dimensions"""
        return tuple(self._data.attrs.get(DIMENSIONS_NAME, tuple()))

    def map_chunk(
        self,
        func: Callable[..., xarray.DataArray],
        *args: Any,
        template: Optional[xarray.DataArray] = None,
        **kwargs: Any,
    ) -> "EOVariable":
        """
        Apply a function to each chunk of this EOVariable.

        .. warning::
            This method is based on the experimental method ``DataArray.map_blocks`` and its signature may change.

        Parameters
        ----------
        func : callable
            User-provided function that accepts a DataArray as its first
            parameter. The function will receive a subset or 'block' of this EOVariable (see below),
            corresponding to one chunk along each chunked dimension. ``func`` will be
            executed as ``func(subset_dataarray, *subset_args, **kwargs)``.
            This function must return either a single EOVariable.
            This function cannot add a new chunked dimension.
        args : sequence
            Passed to func after unpacking and subsetting any eovariable objects by blocks.
            eovariable objects in args must be aligned with this object, otherwise an error is raised.
        kwargs : mapping
            Passed verbatim to func after unpacking. eovariable objects, if any, will not be
            subset to blocks. Passing dask collections in kwargs is not allowed.
        template : DataArray or Dataset, optional
            eovariable object representing the final result after compute is called. If not provided,
            the function will be first run on mocked-up data, that looks like this object but
            has sizes 0, to determine properties of the returned object such as dtype,
            variable names, attributes, new dimensions and new indexes (if any).
            ``template`` must be provided if the function changes the size of existing dimensions.
            When provided, ``attrs`` on variables in `template` are copied over to the result. Any
            ``attrs`` register_requested_parameter by ``func`` will be ignored.

        Returns
        -------
        A single DataArray or Dataset with dask backend, reassembled from the outputs of the
        function.

        See Also
        --------
        dask.array.map_blocks, xarray.apply_ufunc, xarray.Dataset.map_blocks, xarray.DataArray.map_blocks
        """
        self._data = self._data.map_blocks(func, args, kwargs, template=template)
        return self

    def isel(
        self,
        indexers: Optional[Mapping[Any, Any]] = None,
        drop: bool = False,
        missing_dims: ErrorOptionsWithWarn = "raise",
        **indexers_kwargs: Any,
    ) -> "EOVariable":
        """Return a new EOVariable whose data is given by integer indexing
        along the specified dimension(s).

        Parameters
        ----------
        indexers : dict, optional
            A dict with keys matching dimensions and values given
            by integers, slice objects or arrays.
            indexer can be a integer, slice, array-like or EOVariable.
            If EOVariables are passed as indexers, xarray-style indexing will be
            carried out.
            One of indexers or indexers_kwargs must be provided.
        drop : bool, optional
            If ``drop=True``, drop coordinates_dict variables indexed by integers
            instead of making them scalar.
        missing_dims : {"raise", "warn", "ignore"}, default: "raise"
            What to do if dimensions that should be selected from are not present in the
            EOVariable:
            - "raise": raise an exception
            - "warn": raise a warning, and ignore the missing dimensions
            - "ignore": ignore the missing dimensions
        **indexers_kwargs : {dim: indexer, ...}, optional
            The keyword arguments form of ``indexers``.

        See Also
        --------
        DataArray.sel
        DataArray.isel
        EOVariable.sel
        """
        if indexers is None:
            indexers = {}
        return self._init_similar(
            self._data.isel(
                indexers=indexers,
                drop=drop,
                missing_dims=missing_dims,
                **indexers_kwargs,
            ),
        )

    def persist(self, **kwargs: Any) -> "EOVariable":
        """Trigger computation in constituent dask arrays
        This keeps them as dask arrays but encourages them to keep data in
        memory.  This is particularly useful when on a distributed machine.
        When on a single machine consider using ``.compute()`` instead.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments passed on to ``dask.persist``.

        See Also
        --------
        xarray.Dataset.persist
        dask.persist
        """
        return self._init_similar(self._data.persist(**kwargs))

    def sel(
        self,
        indexers: Optional[Mapping[Any, Any]] = None,
        method: Optional[str] = None,
        tolerance: Any = None,
        drop: bool = False,
        **indexers_kwargs: Any,
    ) -> "EOVariable":
        """Return a new EOVariable whose data is given by selecting index
        labels along the specified dimension(s).
        In contrast to `EOVariable.isel`, indexers for this method should use
        labels instead of integers.

        Under the hood, this method is powered by using pandas's powerful Index
        objects. This makes label based indexing essentially just as fast as
        using integer indexing.
        It also means this method uses pandas's (well documented) logic for
        indexing. This means you can use string shortcuts for datetime indexes
        (e.g., '2000-01' to select all values in January 2000). It also means
        that slices are treated as inclusive of both the start and stop values,
        unlike normal Python indexing.

        .. warning::

          Do not try to assign values when using any of the indexing methods
          ``isel`` or ``sel``::

            da = xr.EOVariable([0, 1, 2, 3], dims=['x'])
            # DO NOT do this
            da.isel(x=[0, 1, 2])[1] = -1

          Assigning values with the chained indexing using ``.sel`` or
          ``.isel`` fails silently.

        Parameters
        ----------
        indexers : dict, optional
            A dict with keys matching dimensions and values given
            by scalars, slices or arrays of tick labels. For dimensions with
            multi-index, the indexer may also be a dict-like object with keys
            matching index level names.
            If EOVariables are passed as indexers, xarray-style indexing will be
            carried out.
            One of indexers or indexers_kwargs must be provided.
        method : {None, "nearest", "pad", "ffill", "backfill", "bfill"}, optional
            Method to use for inexact matches:
            * None (default): only exact matches
            * pad / ffill: propagate last valid index value forward
            * backfill / bfill: propagate next valid index value backward
            * nearest: use nearest valid index value
        tolerance : optional
            Maximum distance between original and new labels for inexact
            matches. The values of the index at the matching locations must
            satisfy the equation ``abs(index[indexer] - target) <= tolerance``.
        drop : bool, optional
            If ``drop=True``, drop coordinates_dict variables in `indexers` instead
            of making them scalar.
        **indexers_kwargs : {dim: indexer, ...}, optional
            The keyword arguments form of ``indexers``.
            One of indexers or indexers_kwargs must be provided.

        Returns
        -------
        obj : EOVariable
            A new EOVariable with the same contents as this EOVariable, except the
            data and each dimension is indexed by the appropriate indexers.
            If indexer EOVariables have coordinates_dict that do not conflict with
            this object, then these coordinates_dict will be attached.
            In general, each array's data will be a view of the array's data
            in this EOVariable, unless vectorized indexing was triggered by using
            an array indexer, in which case the data will be a copy.

        See Also
        --------
        DataArray.isel
        DataArray.sel
        EOVariable.isel
        """

        sel_data = self._data.sel(
            indexers,
            method,
            tolerance,
            drop,
            **indexers_kwargs,
        )

        return self._init_similar(sel_data)

    def plot(self, **kwargs: dict[Any, Any]) -> None:
        """Wrapper around the xarray plotting functionality.

        Parameters
        ----------
        The parameters MUST follow the xarray.DataArray.plot() options.

        See Also
        --------
        DataArray.plot
        """

        try:
            # TODO check type
            self._data.plot(**kwargs)  # type: ignore
        except Exception as e:
            self._logger.warning(f"Cannot display plot. Error {e}")

    def _subset_one_dim(
        self,
        dim_name: str,
        subset: slice,
    ) -> Any:
        dimension = self._data.attrs["_ARRAY_DIMENSIONS"].index(dim_name)
        if dimension <= 4:
            data = self._data.data[tuple([*[slice(None)] * dimension, subset])]
        else:
            raise EOVariableSubSetError(f"too many dimensions in variable {self.name} for subset")
        return data

    def _subset_variable_x_and_y(self, region: tuple[int, int, int, int]) -> "EOVariable":
        x, y, width, height = region
        return self._init_similar(
            self._data.data[slice(x, x + width), slice(y, y + height)].rechunk(self._data.data.chunksize),
        )

    def _subset_variable_x_or_y(
        self,
        region: tuple[int, int, int, int],
        dim_names_y_x: tuple[str, str],
    ) -> "EOVariable":
        x, y, width, height = region
        try:
            data = self._subset_one_dim(dim_names_y_x[1], slice(y, y + height))
        except ValueError:
            try:
                data = self._subset_one_dim(dim_names_y_x[0], slice(x, x + width))
            except ValueError as exc:
                raise EOVariableSubSetError(f"cannot find dimension {dim_names_y_x} in variable {self.name}") from exc
        return self._init_similar(data.data.data.rechunk(self._data.data.chunksize))

    def subset(
        self,
        region: tuple[int, int, int, int],
        reference: Optional[Union[str, "EOVariable"]] = "",
    ) -> "EOVariable":
        """
        Creates a spatial subset and/or band subset of this EOVariable.

        Parameters
        ----------
        region: tuple
            pixel region as string x,y,w,h, w,h positive
        reference: str
            short name of measurement variable to be used for the geometry, optional

        Returns
        -------
        New EOGroup with selected extent and/or measurement variables
        """
        ref_var: Optional[EOVariable]
        if isinstance(reference, str) and reference:
            ref_var = cast(EOVariable, self.product[reference])
        elif isinstance(reference, EOVariable):
            ref_var = reference
        else:
            ref_var = self

        dim_names = ref_var._data.attrs["_ARRAY_DIMENSIONS"]
        if self.sizes == ref_var.sizes:
            return self._subset_variable_x_and_y(region)
        if dim_names[0] in self.sizes or dim_names[1] in self.sizes:
            return self._subset_variable_x_or_y(region, dim_names)
        return self._init_similar(self.data.data)

    def __getitem__(self, key: Any) -> "EOVariable":
        data = self._data[key]
        return self._init_similar(data)

    def __setitem__(self, key: Any, value: Any) -> None:
        self._data[key] = value

    def __delitem__(self, key: Any) -> None:
        del self._data[key]

    def __iter__(self) -> Iterator["EOVariable"]:
        for data in self._data:
            yield EOVariable(data.name, data)

    def __len__(self) -> int:
        return len(self._data)

    def __ne__(self, other: Any) -> bool:
        return EOVariableEqualMixin.__ne__(self, other)

    def __eq__(self, other: Any) -> bool:
        return EOVariableEqualMixin.__eq__(self, other)

    def _print_tree_structure(
        self,
        buffer: List[str],
        obj: Union["EOObject", tuple[str, "EOObject"]],
        continues: tuple[bool, ...],
        level: int,
        detailed: bool,
    ) -> None:

        style = Style()
        if isinstance(obj, tuple):
            variable = obj[1]
        else:
            variable = obj
        if not isinstance(variable, EOVariable):
            return

        fill, pre = EOObject._compute_tree_indents(continues)

        buffer.append(f"{pre}Variable({variable.name})")

        # display details about variables
        if detailed:
            buffer.append(f"{fill}{style.cont}Attributes:")
            pretty_attrs = pprint.pformat(variable.attrs)
            buffer.extend([f"{fill}{style.vertical}{style.empty}{line}" for line in pretty_attrs.splitlines()])
            # for name, value in variable.attrs.items():
            #    buffer.append(f"{fill}{style.vertical}{style.empty}{name}:{value}")
            buffer.append(f"{fill}{style.end}Data:")
            str_data = str(variable.data)
            for dat in str_data.splitlines():
                buffer.append(f"{fill}{style.empty}{style.empty}{dat}")

    def __copy__(self) -> "EOObject":
        cls = type(self)
        new_instance = cls.__new__(cls)
        new_instance.__dict__.update(self.__dict__)
        return new_instance

    def __deepcopy__(self, memo: dict[int, Any]) -> "EOVariable":
        new_var = EOVariable(
            self.name,
            copy.deepcopy(self.data),
            attrs=copy.deepcopy(self.attrs),
            dims=copy.deepcopy(self.dims),
        )
        memo[id(self)] = new_var
        return new_var

    def _repr_html_(self) -> str:
        """Returns the html representation of the current variable displaying the tree."""
        from eopf.product.rendering import renderer

        return renderer("variable.html", variable=self)

    def _parse_attrs(self, attrs: Optional[MutableMapping[str, Any]]) -> Tuple[dict[str, Any], dict[str, Any]]:
        """Parse attrs to keep only valid ones and allow attrs operations"""

        # attrs coming from zarr are read-only hence they are converted to dict to be  managed easily
        attrs = dict(attrs) if attrs is not None else {}

        xarray_attrs = {}
        for attr_name, attr_value in attrs.items():
            if attr_name in XARRAY_TO_EOV_ATTRS:
                xarry_attr_name = EOV_TO_XARRAY_NAME_CONVERSION.get(attr_name, attr_name)
                xarray_attrs[xarry_attr_name] = attr_value

        # CF attributes coming from the xarray attributes are converted to EOVar attributes
        eovar_attrs = {}
        for attr_name, attr_value in attrs.items():
            eovar_attr_name = XARRAY_TO_EOV_NAME_CONVERSION.get(attr_name, attr_name)
            eovar_attrs[eovar_attr_name] = attr_value

        return xarray_attrs, eovar_attrs


class _LocIndexer:
    """ """

    __slots__ = ("variable",)

    def __init__(self, variable: EOVariable):
        self.variable = variable

    def __getitem__(self, key: Any) -> EOVariable:
        return EOVariable(self.variable.name, self.variable.data.loc[key])

    def __setitem__(self, key: Any, value: Any) -> None:
        self.variable.data[key] = value
