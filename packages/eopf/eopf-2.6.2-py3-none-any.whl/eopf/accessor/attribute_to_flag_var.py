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
attribute_to_flag_var.py

Accessor to transform attributes to eovariables

"""


import importlib
import numbers
from collections.abc import MutableMapping
from typing import Any, Iterator, Optional, Union

import xarray

from eopf.accessor import EOAccessor, EOAccessorFactory
from eopf.accessor.abstract import AccessorStatus
from eopf.common.constants import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.common.functions_utils import not_none
from eopf.common.type_utils import Chunk
from eopf.exceptions import AccessorNotOpenError
from eopf.formatting.decorators import formatable_method, unformatable_method
from eopf.product import EOGroup
from eopf.product.eo_object import EOObject
from eopf.product.eo_variable import EOVariable
from eopf.store import EOProductStore, StorageStatus


@EOAccessorFactory.register_accessor("attribute_element_to_float_variable")
class FromAttributesToVariableAccessor(EOAccessor):
    """
    Accessor that wrap a data format accessor to extract
    attribute and map it to an EOVariable.

    Example: accessor("test.zarr").open(store="eopf.store.ZarrStore",attr_name="")

    Parameters
    ----------
    url: str | Anypath
        url path to open the data format accessor

    Attributes
    ----------
    attr_name: str
        attribute name to extract
    store: EOProductStore
        store to use to open the url and extract the data
    index: any, optional
        index to extract on the attribute sequence
    """

    # docstr-coverage: inherited
    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any):
        super().__init__(url, *args, **kwargs)
        self.index: Optional[Any] = None
        self.store: Optional[EOProductStore] = None
        self.attr_name: Optional[str] = None

    @property
    def status(self) -> AccessorStatus:
        return (
            (AccessorStatus.CLOSE if self.store.status == StorageStatus.CLOSE else AccessorStatus.OPEN)
            if self.store is not None
            else AccessorStatus.CLOSE
        )

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        *,
        store_cls: str = "",
        attr_name: str = "",
        index: Optional[Any] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """
        Open the store in the given mode

        Parameters
        ----------
        chunk_sizes: Optional[Chunk]
            Set the chunking of the output data
        mode: OpeningMode | str , optional
            mode to open the store; default to open
        store_cls: str
            full python path to the store class (ex: eopf.store.EOZarrStore) to use to open the url
        attr_name: str
            name of the attribute to convert
        index: any, optional
            index to extract on the attribute sequence
        **kwargs: Any
            extra kwargs of open for wrapped store
        """
        module, _, klass = store_cls.rpartition(".")
        self.store = getattr(importlib.import_module(module), klass)(self.url)
        self.attr_name = attr_name
        self.index = index
        super().open(mode, chunk_sizes, **kwargs)
        self.store.open(self._mode, **kwargs)

        return self

    # docstr-coverage: inherited
    def close(self) -> None:
        if self.store is None:
            raise AccessorNotOpenError()
        self.store.close()
        self.store = None
        super().close()

    @formatable_method()
    def __getitem__(self, key: str) -> EOObject:
        """

        Parameters
        ----------
        key : extract the attributes from the store[key] data

        Returns
        -------
        An EOVariable with data filled with attribute value array
        """
        self.check_is_opened()
        data = self._extract_data(key)
        return EOVariable(data=data)

    @unformatable_method()
    def __setitem__(self, key: str, value: EOObject) -> None:
        """

        Parameters
        ----------
        key : set the attribute value of store[key].attrs_name
        value : value to set

        Returns
        -------

        """

        self.check_is_opened()
        store = not_none(self.store)

        if not isinstance(value, EOVariable):
            raise NotImplementedError()

        if key not in store:
            store[key] = EOGroup()
        base_: Union[list[xarray.DataArray], xarray.DataArray]
        if self.attr_name not in store[key].attrs:
            if self.index is not None:
                base_ = [value._data]
            else:
                base_ = value._data
        else:
            # Added handling when value.data is xarray and should be converted to list
            if isinstance(value._data, xarray.DataArray):
                data = value._data.to_numpy().tolist()
            else:
                data = value._data

            tmp = [store[key].attrs[self.attr_name]]
            try:
                tmp.append(*data)
            except TypeError:
                # temporary fix for S1 L2 OCN
                tmp.append(data)
            base_ = tmp
        if self.attr_name is not None:
            store.write_attrs(key, {self.attr_name: base_})

    def __iter__(self) -> Iterator[str]:
        self.check_is_opened()
        return iter(not_none(self.store))

    # docstr-coverage: inherited
    @unformatable_method()
    def is_group(self, path: str) -> bool:
        # to have an harmonized behavior with is_variable
        self.check_is_opened()
        return False

    # docstr-coverage: inherited
    @unformatable_method()
    def is_variable(self, path: str) -> bool:
        self.check_is_opened()
        return path in not_none(self.store)

    # docstr-coverage: inherited
    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        raise NotImplementedError

    # docstr-coverage: inherited
    @unformatable_method()
    def iter(self, path: str) -> Iterator[str]:
        self.check_is_opened()
        return not_none(self.store).iter(path)

    def __len__(self) -> int:
        self.check_is_opened()
        return len(not_none(self.store))

    def _extract_data(self, key: str) -> list[Any]:
        """Retrieve data from the attribute of the element at the given key.

        Parameters
        ----------
        key: str
            element path where the attribute will be extracted

        Returns
        -------
        list of data
        """
        item = not_none(self.store)[key]
        if self.attr_name is not None:
            data = item.attrs[self.attr_name]
        if self.index is not None:
            data = data[self.index]
        if isinstance(data, (numbers.Number, str)):
            data = [data]
        return data


@EOAccessorFactory.register_accessor("attribute_element_to_flag_variable")
class FromAttributesToFlagValueAccessor(FromAttributesToVariableAccessor):
    """
    Accessor that wrap a data format accessor to extract
    attribute and map it to an EOVariable from corresponding flag values and meanings

    Parameters
    ----------
    url: str
        url path to open the data format accessor

    Attributes
    ----------
    store: EOProductStore
        accessor to extract base element
    attr_name: str
        attribute name to extract
    index: any, optional
        index to extract on the attribute sequence
    flag_meanings: str
        space separated list of flag name use to convert data
    flag_values: list[int]
        list of value corresponding to flag meaning
    """

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any):
        super().__init__(url, args, kwargs)
        self.flag_values: Optional[list[int]] = None
        self.flag_meanings: Optional[list[str]] = None

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        *,
        store_cls: str = "",
        attr_name: str = "",
        index: Optional[Any] = None,
        flag_meanings: str = "",
        flag_values: Optional[list[int]] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """Open the store in the given mode

        Parameters
        ----------
        mode: OpeningMode | str , optional
            mode to open the store, default to OPEN
        chunk_sizes: optional[Chunk]
            chunking to apply
        store_cls: str
            full python path to the store class (ex: eopf.product.store.EOZarrStore)
        attr_name: str
            name of the attribute to convert
        index: any, optional
            index to extract on the attribute sequence
        flag_meanings: str
            space separated list of flag name use to convert data
        flag_values: list[int]
            list of value corresponding to flag meaning
        **kwargs: Any
            extra kwargs of open for wrapped store
        """
        super().open(mode, chunk_sizes, store_cls=store_cls, attr_name=attr_name, index=index, **kwargs)
        self.flag_meanings = flag_meanings.split(" ")
        if flag_values is None:
            self.flag_values = []
        else:
            self.flag_values = flag_values
        return self

    # docstr-coverage: inherited
    @formatable_method()
    def __getitem__(self, key: str) -> EOObject:
        """

        Parameters
        ----------
        key : extract the attributes from the store[key] data and apply the flags

        Returns
        -------
        An EOVariable with data filled with attribute values mapped to flags
        """
        data = self._apply_flags(self._extract_data(key))
        return EOVariable(data=data)

    def _apply_flags(self, data: list[Any]) -> list[str | int]:
        """Map the given data values to flag values

        Parameters
        ----------
        data: list
            list of data to map

        Returns
        -------
        mapped list
        """
        if self.flag_values is not None and self.flag_meanings is not None:
            if all(isinstance(index, str) for index in data):
                # Nominal case, reading global attributes from nc as strings and apply values
                return [self.flag_values[self.flag_meanings.index(str(d))] for d in data]
            # Reconversion case, global attributes are already stored as integers, apply them to flag meanings
            # Note: flag mappings start from 1
            return [self.flag_meanings[index - 1] for index in data]
        return []
