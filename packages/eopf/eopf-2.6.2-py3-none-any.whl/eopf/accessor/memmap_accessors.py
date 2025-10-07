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
memmap_accessors.py

Accessors for all the binary data stuff with packet like format


"""
import errno
import os
from ast import literal_eval
from pathlib import PurePath
from typing import TYPE_CHECKING, Any, Dict, Iterator, MutableMapping, Optional

import numpy as np

from eopf import EOGroup
from eopf.accessor import EOAccessorFactory
from eopf.accessor.abstract import AccessorStatus, EOAccessor, EOReadOnlyAccessor
from eopf.accessor.memmap_accessors_impl import FixedMemMap, MemMap, MultipleFileMemMap
from eopf.common.constants import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.common.type_utils import Chunk
from eopf.exceptions.errors import (
    AccessorError,
    AccessorInvalidMappingParameters,
    AccessorRetrieveError,
    MissingArgumentError,
)
from eopf.formatting import EOFormatterFactory
from eopf.formatting.abstract import EOAbstractFormatter
from eopf.formatting.basic_formatters import IsOptional
from eopf.logging.log import EOLogging
from eopf.product import EOVariable

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject


@EOAccessorFactory.register_accessor("MemMap")
class MemMapAccessor(EOAccessor):
    """
    Accessor to read data from binary files organised in packets, for example ISP packets

    Examples:
    =========

    ::

        >>>  memmap_accesssor = MemMapAccessor(
        >>>     "MemMap_s1a-ew-raw-s-hh-20230103t225516-20230103t225554-046625-059698-index.dat",
        >>>     primary_header_length_bytes=6,
        >>>     ancillary_header_length_bytes=0,
        >>>     packet_length_start_position_bytes=4,
        >>>     packet_length_stop_position_bytes=6,
        >>> )
        >>> memmap_accesssor.open(target_type="uint16")
        >>> memmap_accesssor["(352,368,16)"].data.compute()

    """

    _dynamic_params: list[str] = ["target_type"]

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        """

        Parameters
        ----------
        url : file or regex to search for file, if multiple found will take the first of the list
        args :
        kwargs :
            should contain at least these elements used to compute the packets lenghts:
             "primary_header_length_bytes" : length of the primary header
             "ancillary_header_length_bytes" : length of the ancillary header
             "packet_length_start_position_bytes" : packet length info in packets start position
             "packet_length_stop_position_bytes" : packet length info in packets stop position
        """
        super().__init__(url, *args, **kwargs)
        if not self.url.exists():
            # resolve regex, assuming the pattern is inside the basename only
            file_regex = self.url.basename
            existing_urls = self.url.dirname().find(file_regex)
            if len(existing_urls) > 0:
                self.url = existing_urls[0]

        try:
            self._primary_header_length_bytes = kwargs["primary_header_length_bytes"]
            self._ancillary_header_length_bytes = kwargs["ancillary_header_length_bytes"]
            self._packet_length_start_position_bytes = kwargs["packet_length_start_position_bytes"]
            self._packet_length_stop_position_bytes = kwargs["packet_length_stop_position_bytes"]
        except KeyError as e:
            raise MissingArgumentError(f"Missing configuration parameter: {e} in {kwargs} for file {self.url}") from e

        self._memmap: Any = MemMap(
            self.url,
            primary_header_length_bytes=self._primary_header_length_bytes,
            ancillary_header_length_bytes=self._ancillary_header_length_bytes,
            packet_length_start_position_bytes=self._packet_length_start_position_bytes,
            packet_length_stop_position_bytes=self._packet_length_stop_position_bytes,
        )
        self._target_type = None

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """Open the store in the given mode

        Parameters
        ----------
        mode: OpeningMode | str, optional
            mode to open the file, default OPEN
        chunk_sizes: Chunk
            Chunk sizes along each dimension to be applied
        **kwargs: Any
            extra kwargs of open on library used.

        Kwargs
        ======

        Should contain at least "target_type" to specify the target type of get_item value.
        'get_item' will interpret the input slice as (startbit, ..., lengthbit) except in the var_bytearry where it
        take the whole data from start to the end of the packet.
        "target_type" can be one of:
        - var_bytearray : will extract all the packets data from (startbit, ..., packet_length) in
           get_item as array of arrays
        - bytearray : will extract the packets data between (startbit, startbit+lengthbit) in
           get_item as array of arrays
        - numpy_type : will extract the numpy_type(packet[startbit, startbit+lengthbit]) as array of numpy_type,
           one for each packet
        - s_numpy_type : the additional 's_' will trigger a single value get from the first packet of the
           first file with the same characteristics as the numpy_type target_type.
        Same behaviour are implemented when writing to it.

        """
        try:
            self._target_type = kwargs["target_type"]
        except KeyError as e:
            raise MissingArgumentError(f"Missing configuration parameter: {e}") from e

        if self._status == AccessorStatus.OPEN:
            return self

        mode = OpeningMode.cast(mode)
        if mode == OpeningMode.OPEN and not self.url.isfile():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.url)

        super().open(mode=mode, chunk_sizes=chunk_sizes)
        if mode == OpeningMode.OPEN:
            self._memmap.load_buffer_infos()
        elif mode in [OpeningMode.CREATE, OpeningMode.CREATE_OVERWRITE]:
            self._memmap.need_save = True
        else:
            raise AccessorError(f"Unsupported mode : {mode}")
        return self

    def close(self) -> None:
        if self._memmap.need_save:
            self._memmap.save_buffer()
        self._memmap.reset()
        return super().close()

    def set_config(self, conf: dict[str, Any]) -> None:
        super().set_config(conf)
        if "target_type" in conf:
            self._target_type = conf["target_type"]

    @staticmethod
    def strip_config(conf: dict[str, Any]) -> dict[str, Any]:
        new_conf = conf.copy()
        new_conf.pop("target_type", "")
        return new_conf

    def get_data(self, key: str, **kwargs: Any) -> "EOObject":
        """
        This method is used to return eo_variables if parameters value match

        Parameters
        ----------
        key: slice containing the first bit to extract in start and the length in step,
             stop is not used, example (startbits,..., lengthinbits)


        Raise
        -----
        AttributeError, it the given slice is not available in the data

        Return
        ----------
        EOVariable
        """
        self._target_type = kwargs.get("target_type", self._target_type)
        try:
            sl = slice(*literal_eval(key))
        except SyntaxError as e:
            raise AccessorError(f"Bad syntax on key '{key}', expected tuple in str : {e}") from e
        offset_in_bits = sl.start
        length_in_bits = sl.step
        ndarray = self._memmap.parse_key(offset_in_bits, length_in_bits, self._target_type)
        if len(ndarray.shape) == 0:
            raise KeyError(f"{self.url} don't have '{key}' valid array")
        return EOVariable(data=ndarray)

    def __getitem__(self, key: str) -> "EOObject":
        return self.get_data(key, target_type=self._target_type)

    def __iter__(self) -> Iterator[str]:
        """Has no functionality within this store"""
        yield from ()

    def __len__(self) -> int:
        """Has no functionality within this accessor"""
        return 0

    def __setitem__(self, key: str, value: Any) -> None:
        """

        Parameters
        ----------
        key : slice containing the first bit to set in start and the length in step for each packet,
             stop is not used, example (startbits,..., lengthinbits)
        value : values to set to each packet, should be array of array in car of *bytearray target_type

        Returns
        -------
        None

        """
        try:
            sl = slice(*literal_eval(key))
        except SyntaxError as e:
            raise AccessorError(f"Bad syntax on key '{key}', expected tuple in str : {e}") from e
        offset_in_bits = sl.start
        length_in_bits = sl.step

        self._memmap.build_buffer(self._reconversion_attrs)

        self._memmap.write_key(offset_in_bits, length_in_bits, np.asarray(value), self._target_type)

    def is_group(self, path: str) -> bool:
        return False

    def is_variable(self, path: str) -> bool:
        return True

    def iter(self, path: str) -> Iterator[str]:
        """Has no functionality within this store"""
        yield from ()

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        raise NotImplementedError()


@EOAccessorFactory.register_accessor("S2MemMap")
class MultipleFilesMemMapAccessor(EOAccessor):
    """
    Same as MemMapAccessor but with multiple binary files concatenation

    Examples:
        >>>  memmap_accesssor = MultipleFilesMemMapAccessor(
        >>>     "S2MemMap_S2B_OPER_MSI_L0__GR_2BPS_20221223T230531_S20221223T220352_D*_B01.bin",
        >>>     primary_header_length_bytes=6,
        >>>     ancillary_header_length_bytes=20,
        >>>     packet_length_start_position_bytes=10,
        >>>     packet_length_stop_position_bytes=12,
        >>> )
        >>> memmap_accesssor.open(target_type="var_bytearray")
        >>>numpy_array = memmap_accesssor["544,None,-1"].data.compute()
    """

    _dynamic_params: list[str] = ["target_type"]

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        """
        See __init__ of MemMapAccessor

        Parameters
        ----------
        url
        args
        kwargs
        """
        super().__init__(url, *args, **kwargs)
        self._urls = sorted(self.url.glob(""))

        try:
            self._primary_header_length_bytes = kwargs["primary_header_length_bytes"]
            self._ancillary_header_length_bytes = kwargs["ancillary_header_length_bytes"]
            self._packet_length_start_position_bytes = kwargs["packet_length_start_position_bytes"]
            self._packet_length_stop_position_bytes = kwargs["packet_length_stop_position_bytes"]
        except KeyError as e:
            raise MissingArgumentError(f"Missing configuration parameter: {e} in {kwargs} for pattern {url}") from e
        if len(self._urls) == 0:
            self._memmap: MultipleFileMemMap = MultipleFileMemMap(
                [self.url],
                primary_header_length_bytes=self._primary_header_length_bytes,
                ancillary_header_length_bytes=self._ancillary_header_length_bytes,
                packet_length_start_position_bytes=self._packet_length_start_position_bytes,
                packet_length_stop_position_bytes=self._packet_length_stop_position_bytes,
            )
        else:
            self._memmap = MultipleFileMemMap(
                self._urls,
                primary_header_length_bytes=self._primary_header_length_bytes,
                ancillary_header_length_bytes=self._ancillary_header_length_bytes,
                packet_length_start_position_bytes=self._packet_length_start_position_bytes,
                packet_length_stop_position_bytes=self._packet_length_stop_position_bytes,
            )
        self._target_type: Optional[str] = None

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """
        Same as MemMapAccessor but with multiple files to handle

        Parameters
        ----------
        mode
        chunk_sizes
        kwargs

        Returns
        -------

        """
        try:
            self._target_type = kwargs["target_type"]
        except KeyError as e:
            raise MissingArgumentError(f"Missing configuration parameter: {e}") from e

        if self._status == AccessorStatus.OPEN:
            return self

        mode = OpeningMode.cast(mode)
        if len(self._urls) == 0 and mode == OpeningMode.OPEN:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.url)

        for url in self._urls:
            if mode == OpeningMode.OPEN and not url.isfile():
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), url)
        super().open(mode=mode, chunk_sizes=chunk_sizes)
        if mode == OpeningMode.OPEN:
            self._memmap.load_buffer_infos()
        elif mode in [OpeningMode.CREATE, OpeningMode.CREATE_OVERWRITE]:
            self._memmap.need_save = True
        else:
            raise AccessorError(f"Unsupported mode : {mode}")
        return self

    def close(self) -> None:
        if self._memmap.need_save:
            self._memmap.save_buffer()
        self._memmap.reset()
        return super().close()

    def get_data(self, key: str, **kwargs: Any) -> "EOObject":
        """
        This method is used to return eo_variable with an array containing either one array
        or one value for each packet of each file

        Parameters
        ----------
        key: slice containing the first bit to extract in start and the length in step,
             stop is not used, example (startbits,..., lengthinbits), handling depends on the target_type
             ( see MemMapAccessor.open docstring)


        Raise
        ----------
        AttributeError, it the given slice is not available in the data

        Return
        ----------
        EOVariable
        """
        self._target_type = kwargs.get("target_type", self._target_type)
        try:
            sl = slice(*literal_eval(key))
        except SyntaxError as e:
            raise AccessorError(f"Bad syntax on key '{key}', expected tuple in str : {e}") from e
        offset_in_bits = sl.start
        length_in_bits = sl.step

        if self._target_type is None:
            raise AccessorError("target type is not set")
        ndarray = self._memmap.parse_key(offset_in_bits, length_in_bits, self._target_type)
        if len(ndarray.shape) == 0:
            raise KeyError(f"{self.url} don't have {key} valid array")
        return EOVariable(data=ndarray)

    def __getitem__(self, key: str) -> "EOObject":
        return self.get_data(key, target_type=self._target_type)

    def __iter__(self) -> Iterator[str]:
        """Has no functionality within this store"""
        yield from ()

    def __len__(self) -> int:
        """Has no functionality within this accessor"""
        return 0

    def __setitem__(self, key: str, value: Any) -> None:
        """

        Parameters
        ----------
        key : slice containing the first bit to set in start and the length in step for each packet,
             stop is not used, example (startbits,..., lengthinbits)
        value : values to set to each packet, should be array of array in car of *bytearray target_type

        Returns
        -------
        None

        """
        try:
            sl = slice(*literal_eval(key))
        except SyntaxError as e:
            raise AccessorError(f"Bad syntax on key '{key}', expected tuple in str : {e}") from e
        offset_in_bits = sl.start
        length_in_bits = sl.step

        self._memmap.build_buffer(self._reconversion_attrs)
        self._memmap.write_key(offset_in_bits, length_in_bits, np.asarray(value), self._target_type)

    def is_group(self, path: str) -> bool:
        return False

    def is_variable(self, path: str) -> bool:
        return True

    def iter(self, path: str) -> Iterator[str]:
        """Has no functionality within this store"""
        yield from ()

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        raise NotImplementedError()

    @staticmethod
    def strip_config(conf: dict[str, Any]) -> dict[str, Any]:
        new_conf = conf.copy()
        new_conf.pop("target_type", "")
        return new_conf

    def set_config(self, conf: dict[str, Any]) -> None:
        super().set_config(conf)
        if "target_type" in conf:
            self._target_type = conf["target_type"]


@EOAccessorFactory.register_accessor("FixedMemMap")
class FixedMemMapAccessor(EOAccessor):
    """
    Accessor for fixed length binary packet files
    Same behaviour as MemMapAccessor but only the packet_length_bytes kwargs param is requested


    """

    _dynamic_params: list[str] = ["target_type"]

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        """

        Parameters
        ----------
        url : str | Anypath
         file to open
        args :

        kwargs:
            should at least contains 'packet_length_bytes', the fixed length of each packet
        """
        super().__init__(url, *args, **kwargs)
        existing_urls = self.url.glob("")
        if len(existing_urls) > 0:
            self.url = existing_urls[0]

        try:
            self._fixed_packet_length_bytes = kwargs["packet_length_bytes"]
        except KeyError as e:
            raise MissingArgumentError(f"Missing configuration parameter: {e} in {kwargs} for pattern {url}") from e
        self._memmap: Any = FixedMemMap(self.url, fixed_packet_length_bytes=self._fixed_packet_length_bytes)
        self._target_type = None

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """
        See MemMapAccessor open docstring

        Parameters
        ----------
        mode: OpeningMode | str , optional
            mode to open the store; default to open
        chunk_sizes
        kwargs

        Returns
        -------

        """

        try:
            self._target_type = kwargs["target_type"]
        except KeyError as e:
            raise MissingArgumentError(f"Missing configuration parameter: {e}") from e

        if self._status == AccessorStatus.OPEN:
            return self
        mode = OpeningMode.cast(mode)
        if mode == OpeningMode.OPEN and not self.url.isfile():
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.url)

        if mode == OpeningMode.OPEN:
            self._memmap.load_buffer_infos()
        elif mode in [OpeningMode.CREATE, OpeningMode.CREATE_OVERWRITE]:
            self._memmap.need_save = True
        else:
            raise AccessorError(f"Unsupported mode : {mode}")
        super().open(mode=mode, chunk_sizes=chunk_sizes)
        return self

    def close(self) -> None:
        self._memmap.save_buffer()
        self._memmap.reset()
        return super().close()

    def get_data(self, key: str, **kwargs: Any) -> "EOObject":
        """
        This method is used to return eo_variable with an array containing either one array or one value for each packet

        Parameters
        ----------
        key: slice containing the first bit to extract in start and the length in step,
             stop is not used, example (startbits,..., lengthinbits), handling depends on the target_type
             ( see MemMapAccessor.open docstring)


        Raises
        ------
        AttributeError, it the given slice is not available in the data

        Return
        ----------
        EOVariable
        """
        self._target_type = kwargs.get("target_type", self._target_type)
        try:
            sl = slice(*literal_eval(key))
        except SyntaxError as e:
            raise AccessorError(f"Bad syntax on key '{key}', expected tuple in str : {e}") from e

        offset_in_bits = sl.start
        length_in_bits = sl.stop - offset_in_bits

        ndarray = self._memmap.parse_key(offset_in_bits, length_in_bits, self._target_type)
        if len(ndarray.shape) == 0:
            raise KeyError(f"{self.url} don't have '{key}' valid array")
        return EOVariable(data=ndarray)

    def __getitem__(self, key: str) -> "EOObject":
        return self.get_data(key, target_type=self._target_type)

    def __iter__(self) -> Iterator[str]:
        """Has no functionality within this store"""
        yield from ()

    def __len__(self) -> int:
        """Has no functionality within this accessor"""
        return 0

    def __setitem__(self, key: str, value: Any) -> None:
        """

        Parameters
        ----------
        key : slice containing the first bit to set in start and the length in step for each packet,
             stop is not used, example (startbits,..., lengthinbits)
        value : values to set to each packet, should be array of array in car of *bytearray target_type

        Returns
        -------
        None

        """
        try:
            sl = slice(*literal_eval(key))
        except SyntaxError as e:
            raise AccessorError(f"Bad syntax on key '{key}', expected tuple in str : {e}") from e

        offset_in_bits = sl.start
        length_in_bits = sl.stop - offset_in_bits

        self._memmap.build_buffer(self._reconversion_attrs.size)
        self._memmap.write_key(
            offset_in_bits,
            length_in_bits,
            np.asarray(value),
            self._target_type,
        )

    def is_group(self, path: str) -> bool:
        return False

    def is_variable(self, path: str) -> bool:
        return True

    def iter(self, path: str) -> Iterator[str]:
        """Has no functionality within this store"""
        yield from ()

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        raise NotImplementedError()

    @staticmethod
    def strip_config(conf: dict[str, Any]) -> dict[str, Any]:
        new_conf = conf.copy()
        new_conf.pop("target_type", "")
        return new_conf

    def set_config(self, conf: dict[str, Any]) -> None:
        super().set_config(conf)
        if "target_type" in conf:
            self._target_type = conf["target_type"]


class DatAttr:
    """
    .dat attribute extractor

    """

    MAPPING_PATH_DELIMITER = ":"

    def __init__(
        self,
        mapping_path: str,
        attr_path: PurePath,
        types_mapping: Dict[str, Any],
        product_path: AnyPath,
    ) -> None:

        self._formatters: list[EOAbstractFormatter] = []
        self._file_regex: str
        self._file_path: AnyPath
        self._attr_path: PurePath = attr_path
        self._slice: slice
        self._dtype: str

        try:
            # recursively determine the possible formatters
            _, formatter, unformatted_mapping_path = EOFormatterFactory().get_formatter(mapping_path)
            while formatter is not None:
                self._formatters.append(formatter)
                _, formatter, unformatted_mapping_path = EOFormatterFactory().get_formatter(unformatted_mapping_path)

            # split initial config
            self._file_regex, slice_tuple, dtype = unformatted_mapping_path.split(self.MAPPING_PATH_DELIMITER)

            # determine the file matching the regex from the product
            # we only consider the first match, the regex should be specific enough
            # If no match found, we simply join the product path and regex, which yields a non-existing path
            found_files = product_path.find(self._file_regex)
            self._file_path = found_files[0] if found_files else AnyPath("null")

            self._slice = slice(*literal_eval(slice_tuple))
            self._dtype = types_mapping[dtype]
        except Exception as e:
            raise AccessorInvalidMappingParameters(f"Mapping parameter due to: {e}") from e

    @property
    def formatters(self) -> list[EOAbstractFormatter]:
        return self._formatters

    @property
    def file_regex(self) -> str:
        return self._file_regex

    @property
    def file_path(self) -> AnyPath:
        return self._file_path

    @property
    def attr_path(self) -> PurePath:
        return self._attr_path

    @property
    def slice(self) -> slice:
        return self._slice

    @property
    def dtype(self) -> str:
        return self._dtype


@EOAccessorFactory.register_accessor("MemMapToAttrAccessor")
class MemMapToAttrAccessor(EOReadOnlyAccessor):
    """
    Accessor transforming

    """

    DAT_FILE_IDENTIFIER = ".dat"
    MANDATORY_CONFIG_PARAMS = [
        "mapping",
        "types_mapping",
        "primary_header_length_bytes",
        "ancillary_header_length_bytes",
        "packet_length_start_position_bytes",
        "packet_length_stop_position_bytes",
    ]

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        super().__init__(url, *args, **kwargs)
        self.kwargs: Any = None
        self._log = EOLogging().get_logger()

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        # check mandatory config parameterss
        for p in self.MANDATORY_CONFIG_PARAMS:
            if p not in kwargs.keys():
                raise MissingArgumentError(f"Missing configuration parameter: {p}")

        # save kwargs for later user
        self.kwargs = kwargs

        # Will raise an exception in EOReadOnlyAccessor if mode is not Open
        super().open(mode=mode, chunk_sizes=chunk_sizes)
        # check the existence of the product when reading
        if not self.url.exists():
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), self.url)
        return self

    def _extract_dat_attrs(self, dict_attrs: Dict[str, Any], attr_path: PurePath) -> list[DatAttr]:
        """
        This method recursively find dat attrs among the dict of attrs and adds them to a list

        Parameters
        ----------
        dict_attrs: Dict[str, Any]
            dict of attrs containing dat attrs

        attr_path: PurePath
            target path of the attr

        Return
        ----------
        list[DatAttr]
            list of dat attrs
        """

        list_dat_attrs = []
        for k in dict_attrs:
            if isinstance(dict_attrs[k], dict):
                # recursively parse sub dictionaries of attrs
                sub_dict_attrs = self._extract_dat_attrs(dict_attrs[k], attr_path.joinpath(k))
                if len(sub_dict_attrs) > 0:
                    # add subdicts only when the contain some relevant keys
                    list_dat_attrs.extend(sub_dict_attrs)
            elif isinstance(dict_attrs[k], str) and self.DAT_FILE_IDENTIFIER in dict_attrs[k]:
                cur_attr_path = attr_path.joinpath(k)
                dat_attr = DatAttr(dict_attrs[k], cur_attr_path, self.kwargs["types_mapping"], self.url)
                list_dat_attrs.append(dat_attr)

        return list_dat_attrs

    def _dict_update(self, indict: Dict[str, Any], path: PurePath, value: Any) -> Dict[str, Any]:
        """
        This method recursively add a key value pair in dictionary at a specific path

        Parameters
        ----------
        indict: Dict[str, Any]
            input dictionary, modified inplace

        path: PurePath
            a key path

        value: Any
            the value to be added at dict_path

        Return
        ----------
        Dict[str, Any]
            updated dictionary
        """

        if len(path.parts) > 1:
            # key value should be added added in sub dict
            k = path.parts[0]
            sub_path = PurePath()
            for p in path.parts[1:]:
                sub_path = sub_path.joinpath(p)
            if k not in indict:
                indict[k] = {}
            # recurse in sub dict
            indict[k] = self._dict_update(indict[k], sub_path, value)
        elif len(path.parts) == 1:
            # key value should be added at current level
            k = path.parts[0]
            indict[k] = value
        else:
            # no key
            pass

        return indict

    def _index_by_file(self, list_dat_attrs: list[DatAttr]) -> Dict[AnyPath, list[DatAttr]]:
        """
        This method indexes a list of dat attrs per file and returns a dictionary with
        keys beeing files and values as list of dat attrs

        Parameters
        ----------
        list_dat_attrs: list[DatAttr])
            list of dat attrs

        Return
        ----------
        Dict[str, list[DatAttr]]
            a dictionary of dat attrs indexed by file
        """

        file_indexed_dat_attrs: Dict[AnyPath, list[DatAttr]] = {}
        for attr in list_dat_attrs:
            if attr.file_path in file_indexed_dat_attrs.keys():
                file_indexed_dat_attrs[attr.file_path].append(attr)
            else:
                file_indexed_dat_attrs[attr.file_path] = [attr]

        return file_indexed_dat_attrs

    def __getitem__(self, _: Any) -> "EOObject":
        """
        This method is used to return an EOGroup with attrs retrieved from .dat files

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
        # get list of dat attrs
        list_dat_attrs = self._extract_dat_attrs(self.kwargs["mapping"], PurePath())

        # index .dat attrs by file, for efficient memory use
        file_indexed_dat_attrs = self._index_by_file(list_dat_attrs)

        # dictionary of EOG attrs
        eog_attrs: Dict[str, Any] = {}

        # iterate over all files
        for file_path, dat_attrs in file_indexed_dat_attrs.items():
            if not file_path.isfile():
                # iterate over all dat attrs which could not be retrieved
                for dat_attr in dat_attrs:
                    # check if among the formmater we have the is_optional one
                    is_optional = False
                    for formatter in dat_attr.formatters:
                        if isinstance(formatter, IsOptional):
                            is_optional = True

                    if is_optional:
                        # if the file does not exist and is declared as optional add it to attr

                        # just follow the is_optional convetion for specifying no data
                        retrieved_value = IsOptional().format(None)

                        # add retrieved value to eog attrs at the specific attr_path
                        self._dict_update(eog_attrs, dat_attr.attr_path, retrieved_value)
                    else:
                        raise AccessorRetrieveError(
                            f"No file match for {dat_attr.attr_path} with regex {dat_attr.file_regex} under {self.url}",
                            # noqa
                        )
            else:
                # create a memmap for each file and retrieve all requested data from it
                memmap = MemMap(
                    url=file_path,
                    primary_header_length_bytes=self.kwargs["primary_header_length_bytes"],
                    ancillary_header_length_bytes=self.kwargs["ancillary_header_length_bytes"],
                    packet_length_start_position_bytes=self.kwargs["packet_length_start_position_bytes"],
                    packet_length_stop_position_bytes=self.kwargs["packet_length_stop_position_bytes"],
                )
                memmap.load_buffer_infos()
                for dat_attr in file_indexed_dat_attrs[file_path]:
                    # iterate over all .dat attr to be retrieved from currnet file
                    try:
                        retrieved_data = memmap.parse_key(
                            offset_in_bits=dat_attr.slice.start,
                            length_in_bits=dat_attr.slice.stop - dat_attr.slice.start,
                            output_type=dat_attr.dtype,
                        )
                        retrieved_value = retrieved_data[0].compute()
                    except Exception as e:
                        raise AccessorRetrieveError(e) from e

                    # recursively apply formatting when needed
                    while len(dat_attr.formatters) > 0:
                        formatter = dat_attr.formatters.pop()
                        retrieved_value = formatter.format(retrieved_value)

                    # add retrieved value to eog attrs at the specific attr_path
                    self._dict_update(eog_attrs, dat_attr.attr_path, retrieved_value)

                memmap.reset()
                del memmap

        eog: EOGroup = EOGroup("product_metadata", attrs=eog_attrs)
        return eog

    def __iter__(self) -> Iterator[str]:
        """Has no functionality within this store"""
        yield from ()

    def __len__(self) -> int:
        """Has no functionality within this accessor"""
        return 0

    def __setitem__(self, key: Any, value: Any) -> None:
        """Has no functionality within this store
        The writing of the .dat attrs is carried by each individual L0Writer
        """

    def is_group(self, path: str) -> bool:
        return False

    def is_variable(self, path: str) -> bool:
        return True

    def iter(self, path: str) -> Iterator[str]:
        """Has no functionality within this store"""
        yield from ()

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        pass
