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

EOZarrStore implementation

"""
import copy
import os
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterator, MutableMapping, Optional, Tuple

import numpy as np
from dask.delayed import Delayed
from distributed import Future
from numcodecs import Blosc
from numpy import isnan
from xarray import Dataset, decode_cf, open_zarr
from xarray.core.types import ZarrWriteModes
from zarr import consolidate_metadata
from zarr._storage.store import Store
from zarr.errors import GroupNotFoundError
from zarr.storage import FSStore

from eopf.common.constants import (
    EOCONTAINER_CATEGORY,
    EOPF_CATEGORY_ATTR,
    EOPRODUCT_CATEGORY,
    UNKNOWN_CATEGORY,
    XARRAY_FILL_VALUE,
    ZARR_EOV_ATTRS,
    OpeningMode,
)
from eopf.common.file_utils import AnyPath
from eopf.common.type_utils import Chunk
from eopf.config.config import EOConfiguration
from eopf.dask_utils import dask_helpers
from eopf.dask_utils.dask_helpers import FutureLike
from eopf.exceptions.errors import (
    EOGroupReadError,
    EOStoreInvalidPathError,
    EOStoreProductAlreadyExistsError,
    EOVariableReadError,
    StoreInvalidMode,
    StoreLoadFailure,
)
from eopf.exceptions.warnings import EOZarrStoreWarning
from eopf.logging import EOLogging
from eopf.product import EOGroup, EOProduct, EOVariable
from eopf.product.eo_container import EOContainer
from eopf.product.eo_object import EOObject
from eopf.product.utils.eoobj_utils import NONE_EOObj
from eopf.store.abstract import EOProductStore, StorageStatus
from eopf.store.mapping_manager import EOPFAbstractMappingManager, EOPFMappingManager
from eopf.store.store_factory import EOStoreFactory

ZARR_PRODUCT_FORMAT = "zarr"


# Warning : do not remove this is the factory registry mecanism
@EOStoreFactory.register_store(ZARR_PRODUCT_FORMAT)
class EOZarrStore(EOProductStore):
    """
    EOZarrStore class
    """

    DEFAULT_COMPRESSION_ALGORITHM = "zstd"
    DEFAULT_COMPRESSION_LEVEL = 3
    DEFAULT_SHUFFLE = Blosc.BITSHUFFLE
    DEFAULT_COMPRESSOR = Blosc(
        cname=DEFAULT_COMPRESSION_ALGORITHM,
        clevel=DEFAULT_COMPRESSION_LEVEL,
        shuffle=DEFAULT_SHUFFLE,
    )
    EXTENSION = ".zarr"

    def __init__(
        self,
        url: str | AnyPath,
        *args: Any,
        mapping_manager: Optional[EOPFAbstractMappingManager] = None,
        mask_and_scale: Optional[bool] = None,
        short_names_map: Optional[dict[str, str]] = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Initializes the XarrayStore

        Parameters
        ----------
        url: str|AnyPath
            file system path to a product
        mapping_manager: EOPFAbstractMappingManager
           mapping manager used to retrieve short names
        mask_and_scale: Optional[bool] = None
            apply or not masking and scaling by overriding EOConfiguration
        args:
            None
        kwargs:
            storage_options: dict[Any, Any] parameters for AnyPath

        Raises
        -------

        Returns
        -------
        """
        if not EOProductStore.is_valid_url(url):
            raise EOStoreInvalidPathError(f"The url: {url} does not exist.")

        super().__init__(url, *args, **kwargs)
        self._chunking: Optional[Chunk] = None
        self._futures_list: list[Future | FutureLike] = []
        self._delayed_list: list[Delayed] = []
        self._consolidate_list: list[FSStore] = []
        self._cache: dict[str, EOProduct | EOContainer] = {}
        self._mapping: Dict[str, Any] = {}
        self._delayed_writing: bool = True
        self._delayed_consolidate: bool = False
        self._compressor: Any = None
        self._read_zarr_kwargs: dict[str, Any] = {}
        self._write_zarr_kwargs: dict[str, Any] = {}
        self._eov_kwargs: dict[str, Any] = {}
        self._short_names_map: dict[str, str] = short_names_map if short_names_map is not None else {}
        self._mapping_manager: EOPFAbstractMappingManager = (
            mapping_manager if mapping_manager is not None else EOPFMappingManager()
        )
        self.LOGGER = EOLogging().get_logger("eopf.store.zarr")
        if mask_and_scale is None:
            eopf_config = EOConfiguration()
            self._mask_and_scale = eopf_config.get("product__mask_and_scale")
        else:
            self._mask_and_scale = mask_and_scale

    @staticmethod
    def _decode_xarray_dataset(dataset: Dataset) -> None:
        """
        Applies decoding on the read xarray dataset

        Parameters
        ----------
        dataset

        Returns
        -------

        """
        for var_name in dataset.variables:
            # decode datatime64
            cur_var = dataset[var_name]
            cur_var_dtype = dataset[var_name].attrs.get("dtype", None)
            if np.issubdtype(cur_var_dtype, np.datetime64) or "calendar" in cur_var.attrs:
                xds = decode_cf(Dataset({"aux": (cur_var.dims, cur_var.data, cur_var.attrs)}))
                # for some reason decode_cf removes coordinates atrribute
                # which we need to correctly assign secondary coords
                if "coordinates" in cur_var.attrs:
                    xds["aux"].attrs["coordinates"] = cur_var.attrs["coordinates"]
                dataset[var_name] = xds["aux"]

    def _get_eov(self, var_name: str, dataset: Dataset) -> EOVariable:
        """Build and EOVariable from a dataarray"""

        if XARRAY_FILL_VALUE in dataset[var_name].attrs and np.isnan(dataset[var_name].attrs[XARRAY_FILL_VALUE]):
            # open_zarr with decode_cf=False will add a default _FillValue=nan
            # even if there is no fill_value necessary
            del dataset[var_name].attrs[XARRAY_FILL_VALUE]

        # deserialise eov from xarray.dataarray
        eov_attrs = dataset[var_name].attrs.pop(ZARR_EOV_ATTRS, {})

        # eov data should already have coords attached there is no need to keep coordinates attr
        # this is also done to keep eov representation harmonized over different data types
        if "coordinates" in dataset[var_name].attrs:
            # retrieve secondary coords and assign them to the data
            coords_list = dataset[var_name].attrs.pop("coordinates", "").split(" ")
            coords_dict = {}
            for coord_name in coords_list:
                coords_dict[coord_name] = dataset[coord_name]
            data = dataset[var_name].assign_coords(coords_dict)
        else:
            data = dataset[var_name]

        # create the eovariable
        eo_var: EOVariable = EOVariable(
            name=var_name,
            data=data,
            attrs=eov_attrs,
            **self._eov_kwargs,
        )

        # in oder to retrieve all attrs from zarr with xarray, we need to use decode_cf=False
        # however, the downside is that xarray will not to perform mask_and_scale
        # thus, we need to do the scale and mask on our own
        eo_var.mask(mask_apply=self._mask_and_scale)
        eo_var.scale(scale_apply=self._mask_and_scale)

        return eo_var

    def __getitem__(self, key: str) -> "EOObject":
        """
        Retrieves an EOVariable

        Parameters
        ----------
        key: str
            a EOProduct path as str

        Raises
        -------
        StoreNotOpenError
        EOGroupReadError
        EOVariableReadError

        Returns
        -------
        EOObject
        """
        self.check_is_opened()

        if self._mode != OpeningMode.OPEN:
            self.LOGGER.warning(
                f"Functionality available only in mode: {OpeningMode.OPEN} not it current mode: {self._mode}."
                f"{EOZarrStoreWarning.__name__}: {EOZarrStoreWarning.__doc__}",
            )
            return NONE_EOObj

        var_zarray_fspath = self.url / key / ".zarray"
        var_eopath = PurePosixPath(key)
        var_name = var_eopath.name
        group_eopath = var_eopath.parent
        group_fspath: AnyPath = self.url / str(group_eopath)

        if not group_fspath.exists():
            raise EOGroupReadError(f"EOGroup {group_fspath.path} does not exist")

        if not var_zarray_fspath.exists():
            self.LOGGER.warning(
                f"Only EOVariables or Products can be retrieved."
                f"{EOZarrStoreWarning.__name__}: {EOZarrStoreWarning.__doc__}",
            )
            return NONE_EOObj

        try:
            ds = open_zarr(
                group_fspath.to_zarr_store(),
                consolidated=False,
                decode_cf=False,
                **self._read_zarr_kwargs,
            )

            # decode inplace the xarray dataset
            self._decode_xarray_dataset(dataset=ds)

            eo_obj = self._get_eov(var_name=var_name, dataset=ds)

            ds.close()
        except Exception as err:
            raise EOVariableReadError(f"{var_name} retrieve error: {err}") from err

        return eo_obj

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        delayed_writing: bool = True,
        delayed_consolidate: bool = False,
        chunking: Optional[Chunk] = None,
        compressor: Any = DEFAULT_COMPRESSOR,
        **kwargs: Any,
    ) -> "EOProductStore":
        """
        Opens the store

        Parameters
        ----------
        mode: OpeningMode | str
            default OPEN

        delayed_writing: bool
            default True
        delayed_consolidate: bool
            default False, expert level parameter to delay the consolidation at close after dask delaying
        chunking: Optional[dict]
            chunking to be used upon reading
        compressor: ANY
            default DEFAULT_COMPRESSOR
        kwargs:
            read_zarr_kwargs: Xarray open_zarr kwargs
            write_zarr_kwargs: Xarray Dataset to_zarr kwargs
            eov_kwargs: EOVariable init kwargs

        Raises
        -------
        StoreInvalidMode

        Returns
        -------
        EOProductStore
        """
        # Already open
        if self.is_open():
            return self

        super().open(mode=mode, **kwargs)
        if self._mode == OpeningMode.OPEN:
            # The given url is already a .zarr
            if self.guess_can_read(self.url):
                pass
            # The given url is the root dir of zarrs, compatible with the setitem API
            elif not self.url.exists():
                raise FileNotFoundError(f"{self.url} doesn't exists")

            self._chunking = chunking

            # get xarray open_zarr kwargs
            if "read_zarr_kwargs" in kwargs:
                self._read_zarr_kwargs = kwargs.pop("read_zarr_kwargs")

            # get EOVariable kwargs
            if "eov_kwargs" in kwargs:
                self._eov_kwargs = kwargs.pop("eov_kwargs")

        elif self._mode in [
            OpeningMode.CREATE,
            OpeningMode.CREATE_OVERWRITE,
            OpeningMode.CREATE_NO_OVERWRITE,
            OpeningMode.UPDATE,
            OpeningMode.APPEND,
        ]:
            self._delayed_writing = delayed_writing
            # Can only be activated if delayed_writing is also on
            self._delayed_consolidate = delayed_consolidate and delayed_writing
            self._compressor = compressor

            # get xarray to_zarr kwargs
            if "to_zarr_kwargs" in kwargs:
                self._write_zarr_kwargs = kwargs.pop("to_zarr_kwargs")

        else:
            raise StoreInvalidMode(f"EOZarrStore does not support mode: {self._mode}")

        return self

    def close(self, cancel_flush: bool = False) -> None:
        """
        Closes the store
        """
        if hasattr(self, "_status"):
            if cancel_flush:
                self.dask_cancel_flush()
            if self._status == StorageStatus.OPEN:
                self.dask_flush()
            self._compressor = None
            self._delayed_writing = True
            self._delayed_consolidate = False
            self._cache = {}
            self._mapping = {}
            self._chunking = None
            self._read_zarr_kwargs = {}
            self._write_zarr_kwargs = {}
            self._eov_kwargs = {}

        super().close(cancel_flush=cancel_flush)

    def dask_flush(self) -> None:
        """
        Compute dask delayed and clear the list

        Returns
        -------
        None
        """
        if len(self._futures_list) != 0:
            dask_helpers.wait_and_get_results(self._futures_list)
            self._futures_list = []
            self._delayed_list = []
        for fs in self._consolidate_list:
            self._logger.debug(f"Consolidating : {fs}")
            consolidate_metadata(fs)

        self._consolidate_list = []

    def dask_cancel_flush(self) -> None:
        """
        Cancel all remaining dask task,
        call this in case of exit
        Returns
        -------

        """
        if len(self._futures_list) != 0:
            dask_helpers.cancel_futures(self._futures_list)
            self._futures_list = []
            self._delayed_list = []
        self._consolidate_list = []

    @staticmethod
    def __get_node_type(attrs: dict[str, Any]) -> str:
        """
        Get the type of product the zarr is (container, product ...)
        Parameters
        ----------
        attrs

        Returns
        -------

        """
        if "other_metadata" in attrs:
            if EOPF_CATEGORY_ATTR in attrs["other_metadata"]:
                if attrs["other_metadata"][EOPF_CATEGORY_ATTR] in (EOCONTAINER_CATEGORY, EOPRODUCT_CATEGORY):
                    return attrs["other_metadata"][EOPF_CATEGORY_ATTR]
                return UNKNOWN_CATEGORY
            return EOPRODUCT_CATEGORY
        return UNKNOWN_CATEGORY

    def load(self, name: Optional[str] = None, **kwargs: Any) -> EOProduct | EOContainer:
        """
        Loads an EOProduct or EOContainer and returns it

        Parameters
        ----------
        name: Optional[str]
            name of the EOProduct or EOContainer loaded
            default None, the EOProduct name is determined from disk storage
        kwargs:
            open_kwargs: kwargs passed to store open function
            eop_kwargs: EOProduct init kwargs
            eoc_kwargs: EOContainer init kwargs

        Raises
        -------
        NotImplementedError
        StoreLoadFailure

        Note
        -------
        There is no need to call open function before load, load will do it automatically and pass the open_kwargs

        Returns
        -------
        EOProduct | EOContainer
        """
        try:
            open_kwargs = kwargs.get("open_kwargs", {})
            eop_kwargs = kwargs.pop("eop_kwargs", {})
            eoc_kwargs = kwargs.pop("eoc_kwargs", {})

            # if store not opened, open it
            if not self.is_open():
                self.open(mode=OpeningMode.OPEN, **open_kwargs)

            if self._mode != OpeningMode.OPEN:
                raise NotImplementedError(
                    f"Functionality available only in mode: {OpeningMode.OPEN} not it current mode: {self._mode}",
                )

            # if product already loaded, retrieve it from cache
            if self.url.path in self._cache and self._cache[self.url.path] is not None:
                return self._cache[self.url.path]

            # if no name is given use the basename of the url
            if name is None:
                name = self.url.basename

            # retrieve root attrs
            root_ds = open_zarr(
                self.url.to_zarr_store(),
                consolidated=False,
                decode_cf=False,
                **self._read_zarr_kwargs,
            )
            root_attrs = root_ds.attrs
            root_ds.close()

            # create root eo_obj
            root_eoobj: EOContainer | EOProduct
            root_node_type = EOZarrStore.__get_node_type(root_attrs)
            if root_node_type == EOPRODUCT_CATEGORY:
                root_eoobj = EOProduct(name=name, attrs=root_attrs, **eop_kwargs)
            elif root_node_type == EOCONTAINER_CATEGORY:
                root_eoobj = EOContainer(name=name, attrs=root_attrs, **eoc_kwargs)
            else:
                root_eoobj = EOProduct(name=name, attrs=root_attrs, **eop_kwargs)

            # iterate over sub-directories
            self._load_sub_groups(root_eoobj, eoc_kwargs, eop_kwargs)

        except Exception as err:
            raise StoreLoadFailure(f"{self.url} can not be loaded due to: {err}") from err

        # update cache
        self._cache[self.url.path] = root_eoobj

        return root_eoobj

    def _load_sub_groups(
        self,
        root_eoobj: EOContainer | EOProduct,
        eoc_kwargs: dict[Any, Any],
        eop_kwargs: dict[Any, Any],
    ) -> None:
        """
        Iterate throught sub files to populate the group in root_eoobj

        Parameters
        ----------
        root_eoobj : product or container to populate
        eoc_kwargs : eo container args
        eop_kwargs : eo product args

        Returns
        -------
        None, root_eoobj is modified inplace
        """
        for sub_dir in self._iter_sub_dirs(self.url):
            # read data from directory
            ds = open_zarr(
                sub_dir.to_zarr_store(),
                consolidated=False,
                decode_cf=False,
                **self._read_zarr_kwargs,
            )
            # coordinates which are not index coordinates
            secondary_coords: list[str] = self.__extract_secondary_coords(ds)

            # create current eo_obj based on type
            is_group = False
            node_type = EOZarrStore.__get_node_type(ds.attrs)
            eo_obj: EOContainer | EOProduct | EOGroup
            if node_type == EOPRODUCT_CATEGORY:
                eo_obj = EOProduct(name=sub_dir.basename, attrs=ds.attrs, **eop_kwargs)
            elif node_type == EOCONTAINER_CATEGORY:
                eo_obj = EOContainer(name=sub_dir.basename, attrs=ds.attrs, **eoc_kwargs)
            else:
                # this is an EOGroup
                is_group = True
                eo_obj = EOGroup(name=sub_dir.basename, attrs=ds.attrs)

            # get relative path of the current dir compared with the root eo obj
            root_rel_path = sub_dir.relpath(self.url)
            # eo_path are always posix paths
            eo_path = Path(root_rel_path).as_posix()
            # add current eo_obj to the root
            root_eoobj[eo_path] = eo_obj

            if is_group is True:
                # decode inplace the xarray dataset
                self._decode_xarray_dataset(dataset=ds)

                for var_name in ds:
                    if var_name not in secondary_coords:
                        # secondary coordinates are assigned to EOVariables
                        # hence, they should not be added directly under the EOProduct
                        eo_var = self._get_eov(var_name=var_name, dataset=ds)

                        # add var_name to the eo_path
                        eovar_path = str(PurePosixPath(eo_path) / var_name)
                        # add variable to the root eo_obj
                        root_eoobj[eovar_path] = eo_var

            ds.close()

    @staticmethod
    def __extract_secondary_coords(ds: Dataset) -> list[str]:
        secondary_coords: list[str] = []
        for var_name in ds:
            if "coordinates" in ds[var_name].attrs:
                var_secondary_coords = ds[var_name].attrs["coordinates"].split(" ")
                for secondary_coord in var_secondary_coords:
                    if secondary_coord not in secondary_coords:
                        secondary_coords.append(secondary_coord)
        return secondary_coords

    def _iter_sub_dirs(self, url: AnyPath) -> list[AnyPath]:
        """
        Returns paths to all sub_dirroups in a zarr

        Returns
        -------
        list[str]
        """
        self.check_is_opened()
        zgroups_fspath: list[AnyPath] = url.find(".*zgroup")
        groups_fspath: list[AnyPath] = []
        for zg in zgroups_fspath:
            groups_fspath.append(zg.dirname())

        # the first path is the path of the product
        return groups_fspath[1:]

    def _write_eog(
        self,
        group_anypath: AnyPath,
        group_fsstore: Store,
        eo_obj: EOGroup | EOProduct,
        sub_group_prefix: Optional[str] = None,
        level: int = 0,
    ) -> None:
        """
        Creates and returns an EOProduct

        Parameters
        ----------
        group_fspath: Path
            group path inside the product
        eo_obj: EOGroup | EOProduct
            EOGroup | EOProduct to be written

        Raises
        -------
        StoreWriteFailure
        """
        self.LOGGER.debug(f"Writing {group_anypath}/{sub_group_prefix} and zarr kwargs {self._write_zarr_kwargs}")
        zmode: ZarrWriteModes | None = None
        if self._mode in [OpeningMode.UPDATE, OpeningMode.APPEND]:
            zmode = "a"

        # Build the dataset from the eo_obj
        append_dim, ds = self._build_dataset(
            group_anypath,
            eo_obj,
        )

        # create writing or delayed objects
        encoding = {
            var_name: {"compressor": self._compressor}
            for var_name in ds.variables
            if not self._zarray_exists(group_anypath / (sub_group_prefix or "") / var_name)
        }
        if self._delayed_writing:
            delayed_zarr = ds.to_zarr(
                store=group_fsstore,
                mode=zmode,
                group=sub_group_prefix,
                encoding=encoding,
                consolidated=False,
                compute=False,
                append_dim=append_dim,
                **self._write_zarr_kwargs,
            )
            self._futures_list.extend(dask_helpers.compute(delayed_zarr, priority=len(self._futures_list) * 10 + 10))
        else:
            ds.to_zarr(
                store=group_fsstore,
                mode=zmode,
                group=sub_group_prefix,
                encoding=encoding,
                consolidated=False,
                compute=True,
                append_dim=append_dim,
                **self._write_zarr_kwargs,
            )
        ds.close()

        # recursiverly write sub_groups
        sub_group_prefix_str = sub_group_prefix + "/" if sub_group_prefix is not None else ""
        for sub_group_name, sub_group in eo_obj.groups:
            self._write_eog(
                group_anypath,
                group_fsstore,
                sub_group,
                sub_group_prefix_str + sub_group_name,
                level=level + 1,
            )
        # If no sub group then we are top level group and we can consolidate after writing all sub group/vars
        if sub_group_prefix is None:
            self._consolidate_list.append(group_fsstore)
            if not self._delayed_consolidate:
                self.dask_flush()

    def _build_dataset(self, group_anypath: AnyPath, eo_obj: EOGroup | EOProduct) -> Tuple[Optional[Any], Dataset]:
        """
        Build an xarray dataset from the input group

        Parameters
        ----------
        group_anypath
        eo_obj

        Returns
        -------
        (dims to append, dataset)
        """
        data_vars: dict[str, Any] = {}
        coords_vars: dict[str, Any] = {}
        append_dim = None
        # building data and coordinates dict
        for var_name, var in eo_obj.variables:
            # apply mask and scale when writing
            if self._mask_and_scale is True and var.is_scaled is True:
                var.unscale(scale_apply=self._mask_and_scale)
            # serialise eov as xarray.dataarray
            data_vars[var_name] = copy.deepcopy(var.data)
            data_vars[var_name].attrs[ZARR_EOV_ATTRS] = var.attrs
            # retrieve the coordinates
            for coord_name in var.data.coords:
                if coord_name not in coords_vars:
                    coords_vars[str(coord_name)] = var.data.coords[str(coord_name)]
        # create xarray dataset with data and coords
        ds = Dataset(data_vars=data_vars, coords=coords_vars, attrs=eo_obj.attrs)
        # Handle the APPEND mode
        if self._mode == OpeningMode.APPEND and (group_anypath / ".zgroup").exists():
            current_ds = open_zarr(
                group_anypath.to_zarr_store(),
                consolidated=False,
                decode_cf=False,
                **self._read_zarr_kwargs,
            )
            if all(name in current_ds for name in data_vars):
                # find the dimension to append (if any): take the first dimension of the new variables added
                append_dim = list(ds.sizes)[0]
        return append_dim, ds

    def _write_eoc(self, container_fspath: AnyPath, container: EOContainer) -> None:
        """
        Write an EOContainer to the given AnyPath

        Parameters
        ----------
        container_fspath : Anypath , the path to write the container to
        container : container to write

        Returns
        -------
        None
        """
        self.LOGGER.info(f"Writing container {container_fspath} and zarr kwargs {self._write_zarr_kwargs}")
        main_dataset = Dataset(attrs=container.attrs)
        main_dataset.to_zarr(
            store=container_fspath.to_zarr_store(),
            **self._write_zarr_kwargs,
            compute=True,
        )
        for _, prod in container.items():
            product_name = prod.name
            product_name_with_extension = product_name
            group_fspath: AnyPath = container_fspath / product_name_with_extension
            if isinstance(prod, EOProduct):
                # EOProduct
                prod.update_variables_short_names()
                self._write_eog(group_fspath, group_fspath.to_zarr_store(), prod)
            else:
                # Nested container
                self._write_eoc(group_fspath, prod)

        consolidate_metadata(container_fspath.to_zarr_store())

    def write_attrs(self, group_path: str, attrs: MutableMapping[str, Any]) -> None:
        """
        No implementation in zarr, handled in zarr attrs

        Parameters
        ----------
        group_path
        attrs

        Returns
        -------

        """
        return super().write_attrs(group_path, attrs)

    def __setitem__(self, __key: str, __value: EOObject) -> None:
        """
        Writes and EOProduct/EOGroup to disk

        Parameters
        ----------
        __key: str
            group path inside the product
        __value: EOObject
            EOObject to be written

        Raises
        -------
        StoreWriteFailure
        """
        self.check_is_opened()

        if self._mode not in [
            OpeningMode.CREATE,
            OpeningMode.CREATE_OVERWRITE,
            OpeningMode.CREATE_NO_OVERWRITE,
            OpeningMode.UPDATE,
            OpeningMode.APPEND,
        ]:
            self.LOGGER.warning(
                f"Functionality not available in current mode: {self._mode}."
                f"{EOZarrStoreWarning.__name__}: {EOZarrStoreWarning.__doc__}",
            )
            return

        # make sure we do not modify the eo_obj when writing it
        eo_obj = copy.deepcopy(__value)

        if isinstance(eo_obj, (EOProduct, EOContainer)):
            self._setitem_container(__key, eo_obj)
        elif isinstance(eo_obj, EOGroup):
            self._setitem_group(__key, eo_obj)
        elif isinstance(eo_obj, EOVariable):
            self._setitem_variable(__key, eo_obj)
        else:
            self.LOGGER.warning("Only EOProducts, EOContainer and EOGroup can be written")

    def _setitem_variable(self, __key: str, __value: EOVariable) -> None:
        """
        setitem implementation for EOVariable input value

        Parameters
        ----------
        __key
        __value

        Returns
        -------

        """
        if __key == "":
            raise KeyError("Missing name for EOVariable")
        dummy_group = EOGroup()
        var_eopath = PurePosixPath(__key)
        var_name = var_eopath.name
        group_eopath = str(var_eopath.parent)
        if group_eopath != ".":
            group_fspath = self.url / group_eopath
        else:
            group_fspath = self.url
        dummy_group[var_name] = __value
        self._write_eog(group_fspath, group_fspath.to_zarr_store(), dummy_group)

    def _setitem_group(self, __key: str, __value: EOGroup) -> None:
        """
        setitem implementation for EOGroup input value

        Parameters
        ----------
        __key
        __value

        Returns
        -------

        """
        if __key != "":
            group_fspath = self.url / __key
        else:
            group_fspath = self.url
        self._write_eog(group_fspath, group_fspath.to_zarr_store(), __value)

    def _setitem_container(self, __key: str, __value: EOProduct | EOContainer) -> None:
        """
        setitem implementation for EOProduct/EOContainer Variable input value

        Parameters
        ----------
        __key
        __value

        Returns
        -------

        """
        if __key == "":
            product_name = __value.get_default_file_name_no_extension()
            product_name_with_extension = product_name + self.EXTENSION
            group_fspath: AnyPath = self.url / product_name_with_extension
        else:
            if not __key.endswith(self.EXTENSION):
                product_name_with_extension = __key + self.EXTENSION
            else:
                product_name_with_extension = __key
            group_fspath = self.url / product_name_with_extension
        if self._mode in [OpeningMode.CREATE, OpeningMode.CREATE_NO_OVERWRITE]:
            if group_fspath.exists():
                raise EOStoreProductAlreadyExistsError(
                    f"Product {group_fspath} already exists and {self._mode} mode doesn't allow overwriting",
                )
        if group_fspath.exists():
            if self._mode in [OpeningMode.UPDATE]:
                # do nothing
                pass
            else:
                group_fspath.rm(recursive=True)
                group_fspath.mkdir()
        else:
            group_fspath.mkdir()
        if isinstance(__value, EOProduct):
            __value.update_variables_short_names()
            self._write_eog(group_fspath, group_fspath.to_zarr_store(), __value)
        else:
            self._write_eoc(group_fspath, __value)

    @staticmethod
    def _zgroup_exists(path: AnyPath) -> bool:
        """
        Check if the path has a file .zgroup under url/path/

        Parameters
        ----------
        path: Path
            path inside the product url

        Returns
        -------
        bool
        """
        return (path / ".zgroup").exists()

    @staticmethod
    def _zarray_exists(path: AnyPath) -> bool:
        """
        Check if the path has a file .zarray file under url/path/

        Parameters
        ----------
        path: Path
            path inside the product

        Returns
        -------
        bool
        """
        return (path / ".zarray").exists()

    def _is_valid_zarr(self, path: str, has_extension: bool = True) -> bool:
        """
        Test if the subpath of self.url is a valid url
        Parameters
        ----------
        path
        has_extension

        Returns
        -------

        """
        zarr_path = (
            (self.url / path)
            if not has_extension or path.endswith(self.EXTENSION)
            else (self.url / path + self.EXTENSION)
        )
        if not zarr_path.exists():
            return False
        try:
            ds = open_zarr(zarr_path.to_zarr_store(), consolidated=True, **self._read_zarr_kwargs)
            ds.close()
        except GroupNotFoundError:
            return False
        return True

    def is_group(self, path: str) -> bool:
        """
        Check if it is an EOGroup path

        Parameters
        ----------
        path: Path
            path inside the product

        Returns
        -------
        bool
        """
        self.check_is_opened()

        if self._mode != OpeningMode.OPEN:
            self.LOGGER.warning(
                f"Functionality available only in mode: {OpeningMode.OPEN} not it current mode: {self._mode}."
                f"{EOZarrStoreWarning.__name__}: {EOZarrStoreWarning.__doc__}",
            )
            return False

        return self._zgroup_exists(self.url / path)

    def is_variable(self, path: str) -> bool:
        """
        Check if is an EOVariable path

        Parameters
        ----------
        path: Path
            path inside the product

        Returns
        -------
        bool
        """
        self.check_is_opened()

        if self._mode != OpeningMode.OPEN:
            self.LOGGER.warning(
                f"Functionality available only in mode: {OpeningMode.OPEN} not it current mode: {self._mode}."
                f"{EOZarrStoreWarning.__name__}: {EOZarrStoreWarning.__doc__}",
            )
            return False

        zarray_fspath: AnyPath = self.url / path
        return not self._zgroup_exists(zarray_fspath) and self._zarray_exists(zarray_fspath)

    def is_product(self, path: str, has_extension: bool = True) -> bool:
        """Check if the given path under root corresponding to a product representation

        Parameters
        ----------
        path: str
            path to check, either with the extension or not

        Returns
        -------
        bool
            it is a product representation or not

        Raises
        ------
        StoreNotOpenError
            If the store is closed
        """
        # For now we only check that it is a valid zarr
        return self._is_valid_zarr(path, has_extension)

    def is_container(self, path: str, has_extension: bool = True) -> bool:
        """
        Detect if the zarr is a container

        Parameters
        ----------
        path : str
            path to check, either with the extension or not
        has_extension

        Returns
        -------

        """
        zarr_path = (
            (self.url / path)
            if not has_extension or path.endswith(self.EXTENSION)
            else (self.url / path + self.EXTENSION)
        )
        try:
            ds = open_zarr(zarr_path.to_zarr_store(), consolidated=True, **self._read_zarr_kwargs)
        except GroupNotFoundError:
            return False
        is_container = EOContainer.is_container(ds)
        ds.close()
        return is_container

    # docstr-coverage: inherited
    def iter(self, path: str = "") -> Iterator[str]:
        self.check_is_opened()
        for d in self.url.glob("*" + self.EXTENSION):
            yield os.path.splitext(d.basename)[0]

    # docstr-coverage: inherited
    def __len__(self) -> int:
        self.check_is_opened()
        return super().__len__()

    @staticmethod
    def guess_can_read(file_path: str | AnyPath, **kwargs: Any) -> bool:
        """The given file path is readable or not by this store

        Parameters
        ----------
        file_path: str
            File path to check
        kwargs:
            storage_options: dict arguments for AnyPath

        Returns
        -------
        bool
        """
        url: AnyPath = AnyPath.cast(file_path, **kwargs.get("storage_options", {}))
        return url.path.endswith((EOZarrStore.EXTENSION, EOZarrStore.EXTENSION + ".zip"))

    @staticmethod
    def is_valid_url(file_path: str | AnyPath, **kwargs: Any) -> bool:
        """
        Test if the file_path exists

        Parameters
        ----------
        file_path : path to test

        Returns
        -------
        yes or not the path is a valid filename. Default all invalid

        """
        path_obj: AnyPath = AnyPath.cast(file_path, **kwargs.get("storage_options", {}))
        # Special case when directly providing a ZarrStore
        if path_obj.basename == "zarr.storage.Store":
            return True
        # special case when reading with kerchunk ( netcdfAccessor )
        if path_obj.protocol == "reference":
            return True

        return path_obj.exists()

    def _remove_nan_fill_value(self, attrs: Dict[Any, Any], var_name: str, coord_name: Optional[str] = None) -> None:
        """
        Removes the fill value if it is NaN from the attributes.

        Parameters:
            attrs (dict): The attributes dictionary to process.
            var_name (str): Variable name for logging (mandatory).
            coord_name (str, optional): Coordinate name for logging (optional).
        """
        if XARRAY_FILL_VALUE in attrs:
            try:
                # Check if the fill value is NaN, and remove it if true
                if isnan(attrs[XARRAY_FILL_VALUE]):
                    attrs.pop(XARRAY_FILL_VALUE)
            except Exception as e:
                # Log a warning with coord_name if provided, or just var_name
                if coord_name:
                    self.LOGGER.debug(f"isnan failed on var: {var_name}, coordinate: {coord_name} due to: {e}")
                else:
                    self.LOGGER.debug(f"isnan failed on var: {var_name} due to: {e}")
