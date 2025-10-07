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

zarr.py

Zarr accessor

mostly used in kerchunk for netcdf parsing

"""

import pathlib
from typing import TYPE_CHECKING, Any, Iterator, MutableMapping, Optional

import zarr
from dask import array as da
from distributed import Future
from numcodecs import Blosc
from zarr.storage import Store, contains_array, contains_group

from eopf import EOLogging
from eopf.accessor.abstract import EOAccessor
from eopf.common.constants import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.common.functions_utils import not_none
from eopf.common.type_utils import Chunk, convert_to_native_python_type
from eopf.dask_utils import dask_helpers
from eopf.dask_utils.dask_helpers import FutureLike
from eopf.exceptions import AccessorNotOpenError
from eopf.product import EOGroup, EOVariable

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject


class EOZarrAccessor(EOAccessor):
    """
    Accessor representation to access to a Zarr file on the given URL.

    Url can be used to access to S3 and/or zip files.

    .. warning::
        zip file on S3 is not available in writing mode.

    Parameters
    ----------
    url: str | anypath
        path url to the zarr

    Attributes
    ----------
    url: str
        url to the zarr

    Examples
    --------
    >>> zarr_store = EOZarrAccessor(AnyPath("zip::s3://eopf_store/S3A_OL_1_EFR___LN1_O_NT_002.zarr",**storage_options))

    Notes
    -----
    Non local URL should be passed as an AnyPath ( see eopf.common.path_utils)

    See Also
    -------
    zarr.storage
    """

    sep = "/"
    default_alg = "zstd"
    default_comp = 3
    default_shuffle = Blosc.BITSHUFFLE
    DEFAULT_COMPRESSOR = Blosc(cname=default_alg, clevel=default_comp, shuffle=default_shuffle)

    # docstr-coverage: inherited
    def __init__(self, url: str | AnyPath | Store, *args: Any, **kwargs: Any) -> None:
        self._scale_apply = True
        self._mask_apply = True
        self._root: Optional[zarr.hierarchy.Group] = None
        self._zstore: Optional[Store] = None
        self._logger = EOLogging().get_logger("eopf.accessor.zarr")
        self._delayed_writing: bool = True
        self._futures_list: list[Future | FutureLike] = []
        self._zarr_kwargs: dict[str, Any] = {}
        self._dask_kwargs: dict[str, Any] = {}
        self._waiting_attrs: dict[str, Any] = {}

        if isinstance(url, Store):
            self._zstore = url
            super().__init__("", *args, **kwargs)
        else:
            super().__init__(url, *args, **kwargs)
            self._zstore = self.url.to_zarr_store()
        # docstr-coverage: inherited

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        *,
        consolidated: bool = True,
        delayed_writing: bool = True,
        zarr_kwargs: Optional[dict[str, Any]] = None,
        dask_kwargs: Optional[dict[str, Any]] = None,
        scale_apply: bool = True,
        mask_apply: bool = True,
        **kwargs: Any,
    ) -> "EOAccessor":
        """Open the file in the given mode

        library specifics parameters :
            - compressor : numcodecs compressor. ex : Blosc(cname="zstd", clevel=3, shuffle=Blosc.BITSHUFFLE)

        Parameters
        ----------
        mask_apply
            Apply or not the mask
        chunk_sizes
        mode: str, optional
            mode to open the store
        consolidated: bool
            in reading mode, indicate if consolidate metadata file should be use or not
        delayed_writing: bool
            writing should be made when closing or when setting an item
        zarr_kwargs: dict
            kwargs for zarr library
        dask_kwargs: dict
            kwargs for dask
        mask apply: bool
           toggle masking of read data.
        scale_apply: bool
           toggle scaling of read data.
        **kwargs: Any
            extra kwargs of open on library used.
        """
        super().open(mode, chunk_sizes)
        # dask can take specific kwargs (and probably zarr too).

        if zarr_kwargs is None:
            zarr_kwargs = {}

        if dask_kwargs is None:
            dask_kwargs = {}

        # ~ dask_kwargs.setdefault("storage_options", dict())
        if self._mode not in [OpeningMode.OPEN, OpeningMode.UPDATE]:
            dask_kwargs.setdefault("compressor", self.DEFAULT_COMPRESSOR)
            dask_kwargs.setdefault("compute", False)
            dask_kwargs.setdefault("overwrite", True)
            if {"dask_compression", "dask_comp_level", "dask_shuffle"} <= kwargs.keys():
                compressor_alg = kwargs.pop("dask_compression", self.default_alg)
                compressor_level = kwargs.pop("dask_comp_level", self.default_comp)
                compressor_shuffle = kwargs.pop("dask_shuffle", self.default_shuffle)
                custom_compressor = Blosc(cname=compressor_alg, clevel=compressor_level, shuffle=compressor_shuffle)
                dask_kwargs["compressor"] = custom_compressor
        self._delayed_writing = delayed_writing
        self._zarr_kwargs = zarr_kwargs
        self._dask_kwargs = dask_kwargs
        # ~ self._zarr_kwargs.update(**kwargs)
        # ~ self._dask_kwargs.update(**kwargs)
        self._mask_apply = mask_apply
        self._scale_apply = scale_apply
        self._chunk_sizes = chunk_sizes

        # test if file exists, reference is a special case with kerchunk
        if self._mode == OpeningMode.OPEN and not self.url.protocol == "reference":
            if not self.url.exists():
                raise FileNotFoundError(f"File {self.url} not found")

        # call zarr.open_group which does not support reading with a chunk parameters
        if self._mode == OpeningMode.OPEN and consolidated:
            self._root = zarr.open_consolidated(
                store=self._zstore,
                mode=self._mode.value.file_opening_mode,
                **self._zarr_kwargs,
            )
        else:
            self._root = zarr.open(store=self._zstore, mode=self._mode.value.file_opening_mode, **self._zarr_kwargs)

        return self

    def _compute(self) -> None:
        if len(self._futures_list) > 0:
            self._logger.debug("Starting Dask delayed computation")
            dask_helpers.wait_and_get_results(self._futures_list)
            self._logger.debug("Dask delayed computation finished")
        if self._root is None and len(self._waiting_attrs) > 0:
            raise AccessorNotOpenError("Store must be open before access to it")
        for group_path, attrs in self._waiting_attrs.items():
            self._root[group_path].attrs.update(convert_to_native_python_type(attrs))  # type: ignore[index]
        self._futures_list = []
        self._waiting_attrs = {}

    # docstr-coverage: inherited
    def close(self) -> None:
        self.check_is_opened()
        root: zarr.hierarchy.Group = not_none(self._root)
        self._compute()

        # only if we write
        if self._mode in [OpeningMode.CREATE, OpeningMode.CREATE_OVERWRITE, OpeningMode.UPDATE]:
            zarr.consolidate_metadata(root.store)
        super().close()
        self._root = None

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        return contains_group(self._zstore, path=path)

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        self.check_is_opened()
        return contains_array(self._zstore, path=path)

    # docstr-coverage: inherited
    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        self.check_is_opened()
        self._waiting_attrs[group_path] = attrs if attrs is not None else {}

    def write(self) -> None:
        """
        Finalise the writing for asynchronous vars/groups ( delayed)
        Returns
        -------

        """
        self.check_is_opened()
        root: zarr.hierarchy.Group = not_none(self._root)
        self._logger.debug("Starting write")
        self._compute()

        # only if we write
        if self._mode in [OpeningMode.CREATE, OpeningMode.CREATE_OVERWRITE, OpeningMode.UPDATE]:
            zarr.consolidate_metadata(root.store)

    # docstr-coverage: inherited
    def iter(self, path: str) -> Iterator[str]:
        self.check_is_opened()
        root: zarr.hierarchy.Group = not_none(self._root)
        return iter(root.get(path, []))

    def __getitem__(self, key: str) -> "EOObject":
        """
        Get the zarr data at key
        Parameters
        ----------
        key

        Returns
        -------
        Group or variable depending on the zarr

        """

        self.check_is_opened()
        root: zarr.hierarchy.Group = not_none(self._root)
        obj = root[key]
        if self.is_group(key):
            return EOGroup(attrs=obj.attrs)
        # Use dask instead of zarr to read the object data to :
        # - avoid memory leak/let dask manage lazily close the data file
        # - read in parallel
        z_array = zarr.Array(self._zstore, read_only=True, path=key)
        # ~ var_data = da.from_zarr(self.url, component=key, storage_options=self._dask_kwargs["storage_options"])
        var_data = da.from_zarr(z_array)
        raw_variable = EOVariable(data=var_data, attrs=obj.attrs)
        return raw_variable

    def __setitem__(self, key: str, value: "EOObject") -> None:
        """
        Wrtie the value to the zarr
        Parameters
        ----------
        key : path to set to the zarr
        value : variable or group to set

        Returns
        -------

        """

        self.check_is_opened()
        root: zarr.hierarchy.Group = not_none(self._root)
        if isinstance(value, EOGroup):
            root.create_group(key, overwrite=True)
            self.write_attrs(key, value.attrs)
        elif isinstance(value, EOVariable):
            # apply scale and offset, convert masked into filled array
            if self._scale_apply:
                value.unscale(remove_scale_attrs=False)
            dask_array = da.asarray(value.data, dtype=value.dtype)  # .data is generally already a dask array.
            if "fill_value" in value.attrs:
                fill_value = value.attrs["fill_value"]
            else:
                fill_value = None
            if dask_array.size > 0:
                # We must use to_zarr for writing on a distributed cluster,
                # but to_zarr fail to write array with a 0 dim (divide by zero Exception)
                if dask_array.name.startswith("concatenate") or dask_array.name.startswith("reshape"):
                    out = value.data.compute()
                    zarr_path = self.url + key
                    zarr_data = zarr.array(
                        out,
                        chunks=dask_array.chunksize,
                        shape=dask_array.shape,
                        fill_value=fill_value,
                    )
                    zarr_data.attrs.put(convert_to_native_python_type(value.attrs))
                    zarr.save(zarr_path.to_zarr_store(), zarr_data)
                else:
                    self.write_attrs(key, value.attrs)
                    delayed_val = dask_array.to_zarr(
                        self.url.to_zarr_store(),
                        component=key,
                        fill_value=fill_value,
                        **self._dask_kwargs,
                    )
                    if delayed_val is not None:
                        self._futures_list.extend(dask_helpers.compute(delayed_val))
            else:
                root.create(key, shape=dask_array.shape)
                self.write_attrs(key, value.attrs)
        else:
            raise TypeError("Only EOGroup and EOVariable can be set")
        if not self._delayed_writing:
            self._compute()

    def __delitem__(self, key: str) -> None:
        self.check_is_opened()
        root: zarr.hierarchy.Group = not_none(self._root)
        del root[key]

    def __len__(self) -> int:
        self.check_is_opened()
        return len(not_none(self._root))

    def __iter__(self) -> Iterator[str]:
        self.check_is_opened()
        return iter(not_none(self._root))

    # docstr-coverage: inherited
    @staticmethod
    def guess_can_read(file_path: str) -> bool:
        return pathlib.Path(file_path).suffix in [".zarr", ".zip", ""]
