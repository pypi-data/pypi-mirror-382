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
rasterio.py

EOAccessor implementation for rasterio data access

"""
import logging
import os
import pathlib
import warnings
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Iterator, List, Optional, Union

import dask
import numpy as np
import rasterio
import rioxarray
import xarray

from eopf import EOGroup, EOVariable
from eopf.accessor import EOAccessor, EOAccessorFactory
from eopf.accessor.abstract import AccessorStatus, EOReadOnlyAccessor
from eopf.common import xml_utils
from eopf.common.constants import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.common.type_utils import Chunk
from eopf.exceptions import AccessorNotOpenError
from eopf.exceptions.errors import AccessorInvalidRequestError, MissingArgumentError
from eopf.logging import EOLogging

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject

# since the cog store is non product specific, many variable do not have a geo-reference
# hence we filter out NotGeoreferencedWarning warnings
warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)

# avoid creating aux.xml files for jp2 rastersmyp
os.environ["GDAL_PAM_ENABLED"] = "NO"


@EOAccessorFactory.register_accessor("jp2")
class EORasterIOAccessor(EOAccessor):
    """
    Accessor representation to access Raster like jpg2000 or tiff.

    Parameters
    ----------
    url: str | AnyPath
        path or url to access

    Attributes
    ----------
    url: str
        path or url to access
    """

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        super().__init__(url, *args, **kwargs)
        self._raster: Optional[xarray.Dataset | xarray.DataArray | list[xarray.Dataset]] = None

    def __getitem__(self, key: str) -> Any:
        """
        Get the data from a raster file
        Parameters
        ----------
        key : raster to get

        Returns
        -------
        The EOVariable and EOGroup of the data

        """
        if self._raster is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        node = self._select_node(key)
        if isinstance(node, xarray.Variable):
            return EOVariable(data=node)

        if isinstance(node, xarray.core.coordinates.Coordinates):
            return EOGroup(
                variables={key: EOVariable(data=value.variable.to_base_variable()) for key, value in node.items()},
            )

        group = EOGroup()
        group["value"] = EOVariable(data=node.data)
        group["coordinates"] = EOGroup(
            variables={key: EOVariable(data=value.variable.to_base_variable()) for key, value in node.coords.items()},
        )
        return group

    def __len__(self) -> int:
        if self._raster is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        return 2

    def __setitem__(self, key: str, value: "EOObject") -> None:
        """
        Write a variable to a rasterio raster
        Parameters
        ----------
        key : not used
        value

        Returns
        -------

        """
        if self._mode == "r":
            raise AccessorInvalidRequestError("This function is only available in writing mode")
        if self._raster is None:
            raise AccessorNotOpenError("Store must be open before accessing it")

        # only rasters should be written
        if isinstance(value, EOVariable) and len(value.dims) == 2:
            # unscale values if they were scaled
            if self._mask_and_scale:
                value.unscale()

            da = xarray.DataArray(value._data)
            da.rio.set_spatial_dims(x_dim=value.dims[1], y_dim=value.dims[0])
            da.rio.to_raster(self.url.path, lock=False, compute=True, QUALITY="100", REVERSIBLE="YES")
            da.close()

    # do    cstr-coverage: inherited
    def close(self) -> None:
        if self._raster is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        super().close()
        self._raster = None

    # docstr-coverage: inherited
    @property
    def is_erasable(self) -> bool:
        return False

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        try:
            node = self._select_node(path)
            return isinstance(node, (xarray.core.coordinates.Coordinates, xarray.DataArray))
        except AccessorInvalidRequestError:
            return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        try:
            node = self._select_node(path)
            return isinstance(node, xarray.Variable)
        except AccessorInvalidRequestError:
            return False

    # docstr-coverage: inherited
    @property
    def is_writeable(self) -> bool:
        return True

    # docstr-coverage: inherited
    def iter(self, path: str) -> Iterator[str]:
        node = self._select_node(path)
        if path in ["", "/"]:
            return iter(["value", "coordinates"])

        if isinstance(node, xarray.core.coordinates.Coordinates):
            return iter(node.keys())  # type: ignore

        return iter([])

    # docstr-coverage: inherited
    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """TBD"""
        super().open(mode=mode, chunk_sizes=chunk_sizes)
        if "scale_apply" in kwargs:
            kwargs.pop("scale_apply")
        if "mask_apply" in kwargs:
            kwargs.pop("mask_apply")
        kwargs_args = {key: value for key, value in kwargs.items() if key != "chunks"}
        # If no chunks specified only do one
        if chunk_sizes is None:
            self._chunk_sizes = -1
        if self._mode == OpeningMode.OPEN:
            if self.url.islocal():
                self._raster = rioxarray.open_rasterio(
                    self.url.path,
                    chunks=self._chunk_sizes,  # type: ignore
                    **kwargs_args,
                )
            else:
                # source: https://github.com/corteva/rioxarray/issues/440
                # TODO : not really working with dask see 1.4.0 rasterio with virtual fs or do delayed open
                with self.url.open() as fsh:
                    self._raster = rioxarray.open_rasterio(fsh, chunks=self._chunk_sizes, **kwargs_args)  # type: ignore

        return self

    # docstr-coverage: inherited
    def write_attrs(
        self,
        group_path: str,
        attrs: Optional[MutableMapping[str, Any]] = None,
    ) -> None:  # pragma: no cover
        raise NotImplementedError

    # docstr-coverage: inherited
    @staticmethod
    def guess_can_read(file_path: str) -> bool:
        return pathlib.Path(file_path).suffix in [".tiff", ".tif", ".jp2"]

    def _select_node(self, path: str) -> Union[xarray.DataArray, xarray.Variable, xarray.core.coordinates.Coordinates]:
        self._raster_is_ok()

        if isinstance(self._raster, xarray.Variable) or isinstance(self._raster, xarray.DataArray):
            if path in ["", "/"]:
                return self._raster

            if path in [
                "value",
                "/value",
            ]:
                return self._raster.variable

            if any(path.startswith(key) for key in ["coordinates", "/coordinates"]):
                path = path.partition("coordinates")[-1]
                if not path:
                    return self._raster.coords
                if path.startswith("/"):
                    path = path[1:]
                if path in self._raster.coords:
                    return self._raster.coords[path].variable.to_base_variable()
        raise AccessorInvalidRequestError(f"Not able to fullfill the {path} request on {self.url}")

    def _raster_is_ok(self) -> None:
        if self._raster is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        if isinstance(self._raster, (list, xarray.Dataset)):
            raise NotImplementedError
        if isinstance(self._raster, bool):
            raise NotImplementedError


@EOAccessorFactory.register_accessor("multi_source_raster")
class EOMultiSourceRasterIOAccessor(EOReadOnlyAccessor):
    """Accessor representation to access rasters like jpg2000 or tiff from multiple files and stacking them together.

    Parameters
    ----------
    url: str | Anypath
        path or url to access to list files

    Attributes
    ----------
    url: str
        path or url to access
    """

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        self.LOGGER: logging.Logger = EOLogging().get_logger("eopf.accessor.rasterio")
        super().__init__(url, *args, **kwargs)
        self.urls: List[AnyPath] = [p for p in self.url.glob("")]
        if not self.urls:
            raise FileNotFoundError(f"No file found in : {self.url} {self.urls}")
        self._source_order: List[str] = []
        self._stores: List[EORasterIOAccessor] = []

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """
        Open the files

        Parameters
        ----------
        mode: OpeningMode
        chunk_sizes: Optional[chunk]
        kwargs: Any

        Kwargs
        -------
        Must contains at least the source_order params defining the order to stack files.
        For example if you have *hh*, *hv* *vv* files and source_order = [ "vv", "hh", "hv" ]
        then the files will be concatenated with this order

        Returns
        -------
        self

        """
        mode = OpeningMode.cast(mode)
        if mode != OpeningMode.OPEN:
            raise NotImplementedError()

        try:
            self._source_order = kwargs["source_order"]
        except KeyError as e:
            raise MissingArgumentError(f"Missing configuration parameter: {e}") from e

        if not self.urls:
            raise FileNotFoundError(self.urls)

        self._sort_source_urls()
        self._stores = [EORasterIOAccessor(url) for url in self.urls]
        for store in self._stores:
            self.LOGGER.debug(f"Opening : {store.url}")
            # FIXME: rioxarray fails to open the raster in case of complex data if chunks != None
            store.open(mode)
        super().open(chunk_sizes=chunk_sizes, mode=mode)
        return self

    def close(self) -> None:
        if self.status == AccessorStatus.OPEN:
            for store in self._stores:
                store.close()
        super().close()

    def _get_ndarray_from_stores(self) -> np.typing.NDArray[Any]:
        ndarray_list = [store["value"].data for store in self._stores]
        padded_shape = np.stack([arr.shape for arr in ndarray_list]).max(axis=0)
        # Shortcut with only one raster
        if len(ndarray_list) == 1:
            if sum(abs((padded_shape - ndarray_list[0].shape))) != 0:
                pad_width = []
                pad_width.append([0, padded_shape - ndarray_list[0].shape])
                return dask.array.pad(ndarray_list[0], pad_width, constant_values=np.nan)
            # has_only_zero_padding
            return dask.array.concatenate(ndarray_list[0])

        pad_width_list = []
        has_only_zero_padding: bool = True
        for ndarray in ndarray_list:
            pad_width = []
            for nth_dim_pad, nth_dim_shape in zip(padded_shape, ndarray.shape):
                pad_width.append([0, nth_dim_pad - nth_dim_shape])
                if (nth_dim_pad - nth_dim_shape) != 0:
                    has_only_zero_padding = False
            pad_width_list.append(pad_width)

        # No need to pad, only 0 paddings
        if has_only_zero_padding:
            return dask.array.concatenate(ndarray_list)
        # Most RAM intensive task
        return dask.array.concatenate(
            [
                dask.array.pad(arr, pad_width, constant_values=np.nan)
                for arr, pad_width in zip(ndarray_list, pad_width_list)
            ],
        )

    def __getitem__(self, key: str) -> "EOObject":
        """
        This method is used to return eo_variables if parameters value match

        Parameters
        ----------
        key: str
            xpath

        Return
        ----------
        EOVariable
        """

        ndarray = self._get_ndarray_from_stores()
        return EOVariable(data=ndarray)

    def _sort_source_urls(self) -> None:
        """
        Sort the URLS contained in self.urls according to the priority given in self._source_order
        """
        sorted_urls = []
        for src_id in self._source_order:
            sorted_urls += sorted([matching_url for matching_url in self.urls if src_id in matching_url.path])
        self.urls = sorted_urls

    def __iter__(self) -> Iterator[str]:
        """Has no functionality within this store"""
        yield from ()

    def __len__(self) -> int:
        """Has no functionality within this accessor"""
        return 0

    def __setitem__(self, key: str, value: Any) -> None:
        """Has no functionality within this store"""
        raise NotImplementedError()

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        if path in ["", "/"]:
            return False
        return True

    def iter(self, path: str) -> Iterator[str]:
        """Has no functionality within this store"""
        if not self.is_variable(path):
            raise KeyError(f"{path} is not iterable")
        yield from ()

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        raise NotImplementedError()


@EOAccessorFactory.register_accessor("folded_multi_source_raster")
class EOFoldedMultiSourceRasterIOAccessor(EOMultiSourceRasterIOAccessor):
    """Accessor representation to access rasters like jpg2000 or tiff from multiple files and stacking them together.
    Optionally, one of the dimensions of the N-dimensional raster can be folded to generate a N+1-dimensional raster.

    Parameters
    ----------
    url: str
        path or url to access

    Attributes
    ----------
    url: str
        path or url to access
    """

    def __init__(self, url: str, **kwargs: Any) -> None:
        warnings.warn("Deprecated, use EOMultiSourceRasterIOAccessor instead", DeprecationWarning)
        super().__init__(url, **kwargs)
        self._folded_dimension_size_xpath: str = ""
        self._dimension_to_fold: int = 0

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        super().open(chunk_sizes=chunk_sizes, mode=mode, **kwargs)
        try:
            self._dimension_to_fold = kwargs["dimension_to_fold"]
            self._folded_dimension_size_xpath = kwargs["folded_dimension_size"]
        except KeyError as e:
            raise MissingArgumentError(f"Missing configuration parameter: {e}") from e
        return self

    def _parse_xml_xpath(self, xml_xpath: str) -> str:
        """
        Extracts the value of an xpath from a XML file.

        Parameters
        ----------
        key: str
            String in the form 'xml_file_path:xpath'

        Return
        ----------
        str
        """

        xml_url, xpath = xml_xpath.split(":")
        try:
            curr_dir = self.urls[0].dirname()
            xml_file = curr_dir.glob(xml_url)[0] if curr_dir.glob(xml_url) else None
            if xml_file is None:
                raise AccessorInvalidRequestError(f"Impossible to get {xml_xpath} in {self.urls[0].dirname()}")
            xpath_list = xml_utils.get_xpath_results(xml_utils.parse_xml(str(xml_file)), xpath, namespaces={})
            elem = xpath_list[0]
        except (StopIteration, IndexError) as e:
            raise AccessorInvalidRequestError(f"Impossible to get {xml_xpath} in {self.urls[0].dirname()} : {e}") from e
        return elem.text

    def __getitem__(self, key: str) -> "EOObject":
        """
        This method is used to return the data in an eo_variable with concatenated and folded data

        Parameters
        ----------
        key: str
            xpath

        Raise
        ----------
        AttributeError, it the given key doesn't match

        Return
        ----------
        EOVariable
        """
        if self._folded_dimension_size_xpath is None:
            raise KeyError("Missing configuration parameter: dimension_to_fold")

        ndarray = super()._get_ndarray_from_stores()

        # partition dimension_to_fold into slices based on size at folded_dimension_size xpath
        folded_dimension_size = int(self._parse_xml_xpath(self._folded_dimension_size_xpath))
        ndarray_shape = list(ndarray.shape)
        folded_shape = (
            ndarray_shape[: self._dimension_to_fold]
            + [-1, folded_dimension_size]
            + ndarray_shape[self._dimension_to_fold + 1 :]
        )
        reshaped_ndarray = dask.array.reshape(ndarray, folded_shape)

        # filter based on local path (idx:loc), where idx represents the
        # dimension index and loc the index of the value on that dimension
        if key:
            dim_idx, dim_loc = map(int, key.split(":"))

            # take into account the new dimension
            if dim_idx > self._dimension_to_fold:
                dim_idx += 1

            # overwrite outside filter selection with np.nan
            array_idx = [slice(None)] * len(reshaped_ndarray.shape)
            array_idx[dim_idx] = dim_loc  # type:ignore

            return EOVariable(data=reshaped_ndarray[*array_idx])

        return EOVariable(data=reshaped_ndarray)
