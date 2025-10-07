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
netcdf_accessors.py

NetCDF EOAccessor implementation

"""
import itertools
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Union

import kerchunk.hdf
import numpy as np
from netCDF4 import Dataset, Group, Variable

from eopf import EOGroup
from eopf.accessor import EOAccessor, EOAccessorFactory
from eopf.accessor.abstract import AccessorStatus, EOReadOnlyAccessor
from eopf.accessor.zarr import EOZarrAccessor
from eopf.common.constants import FILL_VALUE, OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.common.json_utils import decode_all_attrs, encode_all_attrs
from eopf.common.type_utils import Chunk
from eopf.exceptions import AccessorNotOpenError
from eopf.exceptions.errors import (
    AccessorError,
    AccessorInvalidRequestError,
    MissingArgumentError,
    NetcdfIncompatibilityError,
)
from eopf.formatting import EOFormatterFactory
from eopf.formatting.decorators import (
    formatable_method,
    reverse_formatable_method,
    unformatable_method,
)
from eopf.logging.log import EOLogging
from eopf.product import EOVariable

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject


@EOAccessorFactory.register_accessor("netcdf")
class EONetCDFAccessor(EOAccessor):
    """
    Accessor to access NetCDF files of the given URL.
    It uses internally an other accessor depending on the use case:
    - In Open mode is uses kerchunk/zarr
    - In Create is uses Netcdf4Py

    Parameters
    ----------
    url: str | AnyPath
        path to the file (either an url or an AnyPath object)

    Attributes
    ----------
    url: str
        path url or the target store


    Examples:
    ----------

    ::

            >>> netcdf_accessor = EONetCDFAccessor("S3B_SL_1_RBT____20230824T091058_cartesian_an.nc")
            >>> netcdf_accessor.open()
            >>> data = netcdf_accessor["x_an"]
            >>> print(data)

    """

    # docstr-coverage: inherited
    def __init__(self, url: str | AnyPath, **kwargs: Any) -> None:
        super().__init__(url, **kwargs)
        self._sub_accessor: Optional[EOAccessor] = None
        self._logger = EOLogging().get_logger(name="eopf.accessor.netcdf_accessors")

    # docstr-coverage: inherited
    @unformatable_method()
    def __delitem__(self, key: str) -> None:
        if self._sub_accessor is not None:
            del self._sub_accessor[key]

    # docstr-coverage: inherited
    @formatable_method()
    def __getitem__(self, key: str) -> "EOObject":
        """
        Get the netcdf data at [key]
        Parameters
        ----------
        key : str to netcdf variable or coordinates

        Returns
        -------
        EOGroup or EOVariable
        """
        if self._sub_accessor is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        item = self._sub_accessor[key]
        # Netcdf attrs are decoded
        item.attrs.update(decode_all_attrs(item.attrs))
        return item

    # docstr-coverage: inherited
    @reverse_formatable_method()
    def __setitem__(self, key: str, value: "EOObject") -> None:
        """

        Parameters
        ----------
        key : data path to set
        value : value to set

        Returns
        -------

        """
        if self._sub_accessor is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        self._sub_accessor[key] = value

    # docstr-coverage: inherited
    def __len__(self) -> int:
        if self._sub_accessor is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        return len(self._sub_accessor)

    # docstr-coverage: inherited
    def close(self) -> None:
        if self._sub_accessor is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        self._sub_accessor.close()
        super().close()

    # docstr-coverage: inherited
    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        kwargs_args = {key: val for key, val in kwargs.items() if key != "chunks"}
        mode = OpeningMode.cast(mode)
        if mode == OpeningMode.OPEN:
            if not self.url.exists():
                raise FileNotFoundError(f"File {self.url} not Found")
            sub_accessor = self._open_with_zarr(mode, chunk_sizes, **kwargs_args)
            if sub_accessor is not None:
                self._sub_accessor = sub_accessor
        elif mode in [OpeningMode.CREATE, OpeningMode.CREATE_OVERWRITE]:
            self._sub_accessor = self._open_with_netcdf4py(mode, chunk_sizes, **kwargs_args)
        else:
            raise AccessorError(f"Unsupported mode : {mode}")
        super().open(mode, chunk_sizes=chunk_sizes)
        return self

    # docstr-coverage: inherited
    @unformatable_method()
    def is_group(self, path: str) -> bool:
        if self._sub_accessor is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        return self._sub_accessor.is_group(path)

    # docstr-coverage: inherited
    @unformatable_method()
    def is_variable(self, path: str) -> bool:
        if self._sub_accessor is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        return self._sub_accessor.is_variable(path)

    # docstr-coverage: inherited
    @unformatable_method()
    def iter(self, path: str) -> Iterator[str]:
        if self._sub_accessor is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        return self._sub_accessor.iter(path)

    # docstr-coverage: inherited
    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        if self._sub_accessor is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        return self._sub_accessor.write_attrs(group_path, attrs)

    # docstr-coverage: inherited
    @staticmethod
    def guess_can_read(file_path: str | AnyPath) -> bool:
        return AnyPath.cast(file_path).suffix in [".nc"]

    def _open_with_netcdf4py(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        sub_store: EOAccessor = EONetCDFAccessorNCpy(self.url, **kwargs)
        sub_store.open(mode, chunk_sizes=chunk_sizes, **kwargs)
        return sub_store

    def _open_with_zarr(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """Use kerchunk library to generate a json like string that can be used to read the netcdf file like a zarr.
        This allows parallel reading even with files on a S3.
        Parameters
        ----------
        mode
        kwargs

        Returns
        -------

        """
        # kerchunk
        with self.url.open() as open_file:
            # kerchunk convert the netcdf metadata into a zarr compatible mapping.
            # It's obviously read only.
            try:
                zarr_compatible_data = kerchunk.hdf.SingleHdf5ToZarr(open_file, self.url.path).translate()
                # remove prefix _nc4_non_coord_ automatiically appended by hdf5 library
                # to keep the same key name
                # see https://docs.unidata.ucar.edu/netcdf-c/current/file_format_specifications.html
                k_to_change = []
                for k in zarr_compatible_data["refs"].keys():
                    if k.startswith("_nc4_non_coord_"):
                        k_to_change.append(k)
                for k in k_to_change:
                    new_k = k.removeprefix("_nc4_non_coord_")
                    zarr_compatible_data["refs"][new_k] = zarr_compatible_data["refs"].pop(k)

            except (OSError, TypeError):
                # Kerchunk fail on small netcdf files (< 2Kio) with OSError
                # Seems to be caused by it always requesting the first 2kio to parse the matadata.
                # We fall back to netcdf4py store.

                # Kerchunk fail on file containing variable length strings with TypeError
                # cf : https://github.com/fsspec/kerchunk/issues/167

                return self._open_with_netcdf4py(mode, **kwargs)

            zarr_path_obj = AnyPath("reference://", parent=self.url, fo=zarr_compatible_data)
            zarr_store_r = EOZarrAccessor(zarr_path_obj, **self._kwargs)
            zarr_store_r.open(mode, chunk_sizes=chunk_sizes, consolidated=False, **kwargs)
        return zarr_store_r


@EOAccessorFactory.register_accessor("netcdf-dimension")
class EONetCDFDimensionAccessor(EOReadOnlyAccessor):
    """
    Accessor to access NetCDF format of the given URL.
    Specific to extract Dimensions info

    Parameters
    ----------
    url: str
        path url or the target store

    Attributes
    ----------
    url: str
        path url or the target store
    """

    # docstr-coverage: inherited
    def __init__(self, url: str | AnyPath, **kwargs: Any) -> None:
        super().__init__(url, **kwargs)
        self._ds: Optional[Dataset] = None

    # docstr-coverage: inherited
    @formatable_method()
    def __getitem__(self, key: str) -> "EOObject":
        if self._ds is None:
            raise AccessorNotOpenError("Accessor must be open before calls")

        if key in self._ds.dimensions:
            dim = self._ds.dimensions[key]

            eov_dim = EOVariable(name=dim.name, data=list(range(dim.size)), **self._kwargs)
            return eov_dim
        raise KeyError(f"{key} not found in {self.url.path}")

    # docstr-coverage: inherited
    @reverse_formatable_method()
    def __setitem__(self, key: str, value: "EOObject") -> None:
        # FIXME this should be removed and safe store should not check write mode for writing
        return

    # docstr-coverage: inherited
    def __len__(self) -> int:
        if self._ds is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        return len(self._ds.dimensions)

    # docstr-coverage: inherited
    def close(self) -> None:
        if self._ds is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        super().close()
        self._ds.close()
        self._ds = None

    # docstr-coverage: inherited
    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":

        super().open(mode, chunk_sizes)

        # open the netCDF dataset contained in the file
        local_path = self.url.get()
        self._ds = Dataset(local_path.path, mode="r")
        return self

    # docstr-coverage: inherited
    @unformatable_method()
    def is_group(self, path: str) -> bool:
        if self._ds is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        return False

    # docstr-coverage: inherited
    @unformatable_method()
    def is_variable(self, path: str) -> bool:
        if self._ds is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        return True

    # docstr-coverage: inherited
    @unformatable_method()
    def iter(self, path: str) -> Iterator[str]:
        if self._ds is None:
            raise AccessorNotOpenError("Accessor must be open before calls")
        return iter(self._ds.dimensions)

    # docstr-coverage: inherited
    @staticmethod
    def guess_can_read(file_path: str) -> bool:
        """Determines if a given file path can be read with the current store

        Parameters
        ----------
        file_path: str
            Path to netCDF4 file
        Return
        ------
        Boolean
        """
        return False  # We don't want this store to be our default netcdf store.

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        raise NotImplementedError()


@EOAccessorFactory.register_accessor("NcToAttr")
class EONetCDFDAttrAccessor(EOAccessor):
    """
    Accessor representation to access NetCDF format of the given URL to extract attributes.

    Parameters
    ----------
    url: str
        path url or the target store

    Attributes
    ----------
    url: str
        path url or the target store
    """

    # if present then path in the attrs dict should be
    # parsed with this accessor
    NETCDF_PATH_INDETIFIER = ".nc:"

    # docstr-coverage: inherited
    def __init__(self, url: str | AnyPath, **kwargs: Any) -> None:
        super().__init__(url, **kwargs)
        # the outpute dict should only contain the keys retrieved
        # by the current accessor
        self._attrs_mapping: Optional[Dict[str, Any]] = None
        self.nc_attrs: Dict[str, Any] = {}
        self.LOGGER = EOLogging().get_logger(name="eopf.accessor.netcdf_accessors")

    def _parse_attr_dict(self, attrs_mapping: Dict[str, Any]) -> dict[str, Any]:
        """
        Parse the netcdf attr dict to construct the output attribute dict

        Parameters
        ----------
        attrs_mapping : mapping between netcdf attr and variable attribute

        Returns
        -------

        """
        nc_retrieved_attrs: dict[str, Any] = {}
        # loop over the attrs defined in the mapping

        for key, attrs_expr in attrs_mapping.items():
            # identify just the paths that should be reconverd from netcdf files
            if isinstance(attrs_expr, str) and self.NETCDF_PATH_INDETIFIER in attrs_expr:
                attr_value = self._parse_attr(attrs_expr)
                if attr_value is not None:
                    nc_retrieved_attrs[key] = attr_value
                continue
            if isinstance(attrs_expr, dict):
                nc_attrs = self._parse_attr_dict(attrs_expr)
                if len(nc_attrs) > 0:
                    nc_retrieved_attrs[key] = nc_attrs

        return nc_retrieved_attrs

    def _parse_attr(self, attr_expr: str) -> Any:
        """

        Parameters
        ----------
        attr_expr : contains the path to the netcdf file, the attribute name and possible formatters to the result
        of the netcdf request

        Returns
        -------
        formatted attribute or None if not founc
        """
        # check if any formatter is applied
        formatter_name, formatter, mapping_path = EOFormatterFactory().get_formatter(attr_expr)
        # retrieve the data
        file, var = mapping_path.split(":")
        file_path = self.url / file
        local_path = file_path.get()
        try:
            ds = Dataset(local_path, mode="r")
            if var in ds.variables:
                # retrieve data
                if isinstance(ds[var][0], str):
                    data = ds[var][0]
                elif isinstance(ds[var][0], np.ma.core.MaskedConstant):
                    data = ds[var][:].fill_value
                else:
                    data = ds[var][0].tolist()

                # apply formatter if needed
                if formatter_name is not None and formatter is not None:
                    return formatter.format(data)
                return data
            else:
                self.LOGGER.debug(f"Can not find {var} in {file_path}")
                return None
        except Exception as err:
            raise AccessorError(f"Can not retrieve {attr_expr} due to: {err}") from err
        finally:
            ds.close()

    # docstr-coverage: inherited
    @unformatable_method()
    def __getitem__(self, key: str) -> "EOObject":
        if not self.status == AccessorStatus.OPEN:
            raise AccessorNotOpenError("Accessor must be open before access ")
        if self._attrs_mapping is not None:
            self.nc_attrs = self._parse_attr_dict(self._attrs_mapping)
        else:
            self.nc_attrs = {}
        eog: EOGroup = EOGroup("product_metadata", attrs=self.nc_attrs)
        return eog

    # docstr-coverage: inherited
    def __len__(self) -> int:
        if not self.status == AccessorStatus.OPEN:
            raise AccessorNotOpenError("Accessor must be open before access ")
        return len(self.nc_attrs)

    # docstr-coverage: inherited
    def close(self) -> None:
        if not self.status == AccessorStatus.OPEN:
            raise AccessorNotOpenError("Accessor must be open before access ")
        super().close()

    # docstr-coverage: inherited
    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        mode = OpeningMode.cast(mode)
        if mode != OpeningMode.OPEN:
            return self
            # raise NotImplementedError

        # the mapping kwarg identifies the dictionary of attrs to be parsed
        if "mapping" in kwargs:
            self._attrs_mapping = kwargs["mapping"]
        else:
            raise MissingArgumentError("Missing attribute mapping")
        super().open(chunk_sizes=chunk_sizes, mode=mode, **kwargs)
        return self

    # docstr-coverage: inherited
    @unformatable_method()
    def is_group(self, path: str) -> bool:
        return True

    # docstr-coverage: inherited
    @unformatable_method()
    def is_variable(self, path: str) -> bool:
        return False

    # docstr-coverage: inherited
    @unformatable_method()
    def iter(self, path: str) -> Iterator[str]:
        if not self.status == AccessorStatus.OPEN:
            raise AccessorNotOpenError("Accessor must be open before access ")
        return iter([])

    # docstr-coverage: inherited
    @staticmethod
    def guess_can_read(file_path: str | AnyPath) -> bool:
        """Determines if a given file path can be read with the current store

        Parameters
        ----------
        file_path: str
            Path to netCDF4 file
        Return
        ------
        Boolean
        """
        return False  # We don't want this store to be our default netcdf store.

    # docstr-coverage: inherited
    @reverse_formatable_method()
    def __setitem__(self, key: str, value: "EOObject") -> None:
        # FIXME this should be removed and safe store should not check write mode for writing
        return

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        # FIXME this should be removed and safe store should not check write mode for writing
        return


@EOAccessorFactory.register_accessor("netcdf-netCDF4py")
class EONetCDFAccessorNCpy(EOAccessor):
    """
    Accessor to access NetCDF format of the given URL with netCDF4

    Parameters
    ----------
    url: str
        path url or the target store

    Attributes
    ----------
    url: str
        path url or the target store
    compression: integer/string
        Select compression algorithm
    complevel: int [1-9]
        level of the compression
    shuffle: bool
        enable/disable hdf5 shuffle
    """

    def __delitem__(self, key: str) -> None:
        pass

    RESTRICTED_ATTR_KEY = ("_FillValue",)

    # docstr-coverage: inherited
    def __init__(self, url: str | AnyPath, **kwargs: Any) -> None:
        super().__init__(url, **kwargs)
        self._mask_apply = True
        self._scale_apply = True
        self._root: Optional[Dataset] = None
        self.compression: bool = True
        self.complevel: int = 4
        self.shuffle: bool = True

    @formatable_method()
    def __getitem__(self, key: str) -> "EOObject":
        if self._root is None:
            raise AccessorNotOpenError("Store must be open before access to it")

        try:
            obj = self._select_node(key)
        except IndexError as e:  # if key is invalid, netcdf4 raise IndexError ...
            raise KeyError(e) from e
        attrs = decode_all_attrs(obj.__dict__)
        if isinstance(obj, (Dataset, Group)):
            return EOGroup(attrs=attrs)
        raw_eovar = EOVariable(data=obj[:], attrs=attrs, dims=obj.dimensions, **self._kwargs)
        # manually apply msk and scaling
        # is equivalent to netcdf default mask_and_scale behaviour.
        return raw_eovar

    def __iter__(self) -> Iterator[str]:
        if self._root is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        return itertools.chain(iter(self._root.groups), iter(self._root.variables))

    def __len__(self) -> int:
        if self._root is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        return len(self._root.groups) + len(self._root.variables)

    @reverse_formatable_method()
    def __setitem__(self, key: str, value: "EOObject") -> None:
        if self._root is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        if isinstance(value, EOGroup):
            if key == "":
                # currently there is no distinction between the EOG and EOP as type
                # hwoever an empty key signal a product
                pass
            else:
                self._root.createGroup(key)
            self.write_attrs(key, value.attrs)
        elif isinstance(value, EOVariable):
            # Convert to supported data type
            value_conv = EONetCDFAccessorNCpy.dtype_convert_to_netcdf4py(value)
            # Recover / create dimensions from target product
            for idx, dim in enumerate(value_conv.dims):
                if dim not in self._root.dimensions:
                    self._root.createDimension(dim, size=value_conv.data.shape[idx])
                if len(self._root.dimensions[dim]) != value_conv.data.shape[idx]:
                    raise NetcdfIncompatibilityError(
                        "Netdf4 format does not support mutiples dimensions with the same name and different size.",
                    )
            # Manually apply scaling and filling for cross compatibility
            # as while very close there are some subtle difference
            # to default behaviours when writing.
            value_conv.unscale(scale_apply=self._scale_apply, remove_scale_attrs=False)
            data = value_conv.data.data
            dtype = value_conv.dtype
            if np.issubdtype(value_conv.dtype, np.character):
                data = np.asarray(data, dtype="S")
                dtype = f"S{dtype.itemsize}"  # type: ignore[union-attr]
            # Create and write EOVariable
            if FILL_VALUE in value_conv.attrs:
                fill_value = value_conv.attrs[FILL_VALUE]
            else:
                fill_value = None

            variable: Variable[Any] = self._root.createVariable(
                key,
                dtype,  # type: ignore
                dimensions=value_conv.dims,
                zlib=self.compression,
                complevel=self.complevel,
                shuffle=self.shuffle,
                fill_value=fill_value,
            )

            variable.set_auto_maskandscale(False)
            self.write_attrs(key, value_conv.attrs, value_conv.data.dtype)
            variable[:] = data

        else:
            raise AccessorInvalidRequestError("Only EOGroup and EOVariable can be register_requested_parameter")

    # docstr-coverage: inherited
    def close(self) -> None:
        if self._root is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        super().close()
        self._root.close()
        self._root = None

    # docstr-coverage: inherited
    @staticmethod
    def guess_can_read(file_path: str | AnyPath) -> bool:
        """Determines if a given file path can be read with the current store

        Parameters
        ----------
        file_path: str
            Path to netCDF4 file
        Return
        ------
        Boolean
        """
        return False  # We don't want this store to be our default netcdf store.

    # docstr-coverage: inherited
    @unformatable_method()
    def is_group(self, path: str) -> bool:
        if self._root is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        current_node = self._select_node(path)
        return isinstance(current_node, (Group, Dataset))

    # docstr-coverage: inherited
    @unformatable_method()
    def is_variable(self, path: str) -> bool:
        if self._root is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        current_node = self._select_node(path)
        return isinstance(current_node, Variable)

    # docstr-coverage: inherited
    @unformatable_method()
    def iter(self, path: str) -> Iterator[str]:
        if self._root is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        current_node = self._select_node(path)
        return itertools.chain(iter(current_node.groups), iter(current_node.variables))

    # docstr-coverage: inherited
    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        mask_apply: bool = True,
        scale_apply: bool = True,
        **kwargs: Any,
    ) -> "EOAccessor":
        super().open(chunk_sizes=chunk_sizes, mode=mode)
        if self._mode != OpeningMode.OPEN and not self.url.islocal():
            raise AccessorInvalidRequestError("Netcdf Store only writes to local storage")
        local_path = self.url.get()

        # Overwrite compression / scale parameters if given by user
        self.compression = kwargs.pop("netcdf_compression", self.compression)
        self.complevel = kwargs.pop("netcdf_comp_level", self.complevel)
        self.shuffle = kwargs.pop("netcdf_shuffle", self.shuffle)
        try:
            # Type ignored because mode is expected to be as Literal[] by netcdf
            self._root = Dataset(local_path, self._mode.value.file_opening_mode, **kwargs)  # type: ignore
        except PermissionError as err:
            if self.url.exists():
                self._root = Dataset(local_path.path, mode="a", **kwargs)
            else:
                raise FileNotFoundError(self.url.path) from err
        self._root.set_auto_maskandscale(False)
        self._mask_apply = mask_apply
        self._scale_apply = scale_apply
        return self

    def write_attrs(
        self,
        group_path: str,
        attrs: Optional[MutableMapping[str, Any]] = None,
        data_type: Any = int,
    ) -> None:
        """
        This method is used to update attributes in the store

        Raises
        ------
        StoreNotOpenError
            If the store is closed
        """
        if self._root is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        current_node = self._select_node(group_path)
        used_attrs: MutableMapping[str, Any] = attrs if attrs is not None else {}
        if attrs is not None:
            conv_attr = encode_all_attrs(used_attrs)
            current_node.setncatts(conv_attr)

    def _select_node(self, key: str) -> Union[Dataset, Group, Variable]:  # type: ignore
        """Retrieve and return the netcdf4 object corresponding to the node at the given path

        Returns
        ----------
        Union of Dataset, Group, Variable

        Raises
        ------
        StoreNotOpenError
            If the store is closed
        """
        if self._root is None:
            raise AccessorNotOpenError("Store must be open before access to it")
        if key in ["/", ""]:
            return self._root
        return self._root[key]

    @staticmethod
    def dtype_convert_to_netcdf4py(value: "EOVariable") -> "EOVariable":
        """
        NetCDF4 does not support many data types, this conversions have to be carried to supported data types

        Parameters
        ----------
        value: EOVariable

        Returns
        ---------
        EOVariable
        """

        if not isinstance(value, EOVariable):
            raise TypeError("Only EOVariable supported by this function")
        # convert bool to uint8
        if value.dtype == np.dtype("bool"):
            return value.astype(np.uint8)
        # convert datetime to unix time float 32
        if value.dtype == np.dtype("datetime64[us]"):
            return value.astype("datetime64[s]").astype(np.uint32)
        # convert complex numbers to real and imaginary parts
        if value.dtype == np.dtype("complex64"):
            data_computed = value.data.compute()
            data = np.array([np.real(data_computed.data), np.imag(data_computed.data)])
            if hasattr(data_computed, "mask"):
                mask = np.resize(data_computed.mask, data.shape)
            else:
                mask = None
            attrs = value.attrs
            attrs["_ARRAY_DIMENSIONS"] += ("real_imag",)
            val = EOVariable(data=np.ma.masked_array(data=data, mask=mask), attrs=attrs)
            return val
        return value


@EOAccessorFactory.register_accessor("NcMetadata")
class EONetCDFMetadataAccessor(EOReadOnlyAccessor):
    """
    Accessor representation to access NetCDF format of the given URL to extract attributes.

    Parameters
    ----------
    url: str
        path url or the target store

    Attributes
    ----------
    url: str
        path url or the target store
    """

    # if present then path in the attrs dict should be
    # parsed with this accessor
    NETCDF_PATH_INDETIFIER = ".nc:"

    # docstr-coverage: inherited
    def __init__(self, url: str | AnyPath, **kwargs: Any) -> None:
        super().__init__(url, **kwargs)
        # the outpute dict should only contain the keys retrieved
        # by the current accessor
        self._attrs_mapping: Optional[Dict[str, Any]] = None
        self.nc_attrs: Dict[str, Any] = {}
        self.LOGGER = EOLogging().get_logger(name="eopf.accessor.netcdf_accessors")

    def _parse_attr_dict(self, attrs_mapping: Dict[str, Any]) -> None:

        self.nc_attrs = {}
        local_path = self.url.get()
        try:
            ds = Dataset(local_path.path, mode="r")
            # loop over the attrs defined in the mapping
            for key, attr_expr in attrs_mapping.items():
                # identify just the paths that should be reconverd from netcdf files
                if not isinstance(attr_expr, str):
                    continue
                new_attr = self._parse_attr(attr_expr, ds, local_path)
                if new_attr is not None:
                    self.nc_attrs[key] = new_attr
        finally:
            ds.close()

    def _parse_attr(self, attr_expr: str, ds: Dataset, local_path: AnyPath) -> Any:
        # check if any formatter is applied
        formatter_name, formatter, var = EOFormatterFactory().get_formatter(attr_expr)
        do_format = formatter_name is not None and formatter is not None
        # retrieve the data
        try:
            if var in ds.variables:
                if isinstance(ds[var][0], str):
                    data = ds[var][0]
                else:
                    data = ds[var][0].tolist()
                # apply formatter if needed
                if do_format:
                    # ignore type : it doesn't understand the do_format
                    return formatter.format(data)  # type: ignore
                return data
            if var in ds.ncattrs():
                if isinstance(getattr(ds, var), str):
                    data = getattr(ds, var)
                else:
                    data = getattr(ds, var).tolist()
                # apply formatter if needed
                if do_format:
                    # ignore type : it doesn't understand the do_format
                    return formatter.format(data)  # type: ignore
                return data

            if do_format:
                # ignore type : it doesn't understand the do_format
                return formatter.format(var)  # type: ignore

            self.LOGGER.debug(f"Can not find {var} in {local_path}")
            return None
        except Exception as err:
            raise AccessorError(f"Can not retrieve {attr_expr} due to: {err}") from err

    # docstr-coverage: inherited
    @unformatable_method()
    def __getitem__(self, key: str) -> "EOObject":
        if not self.status == AccessorStatus.OPEN:
            raise AccessorNotOpenError("Accessor must be open before access ")
        if self._attrs_mapping is not None:
            self._parse_attr_dict(self._attrs_mapping)
        eog: EOGroup = EOGroup("product_metadata", attrs=self.nc_attrs)
        return eog

    # docstr-coverage: inherited
    def __len__(self) -> int:
        if not self.status == AccessorStatus.OPEN:
            raise AccessorNotOpenError("Accessor must be open before access ")
        return len(self.nc_attrs)

    # docstr-coverage: inherited
    def close(self) -> None:
        if not self.status == AccessorStatus.OPEN:
            raise AccessorNotOpenError("Accessor must be open before access ")
        super().close()

    # docstr-coverage: inherited
    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":

        # the mapping kwarg identifies the dictionary of attrs to be parsed
        if "mapping" in kwargs:
            self._attrs_mapping = kwargs["mapping"]
        else:
            raise MissingArgumentError("Missing attribute mapping")

        super().open(mode, chunk_sizes)
        return self

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        return True

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        return False

    # docstr-coverage: inherited
    @staticmethod
    def guess_can_read(file_path: str | AnyPath) -> bool:
        """Determines if a given file path can be read with the current store

        Parameters
        ----------
        file_path: str
            Path to netCDF4 file
        Return
        ------
        Boolean
        """
        return False  # We don't want this store to be our default netcdf store.
