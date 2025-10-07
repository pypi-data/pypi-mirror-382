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
memmap_accessors_impl.py


Actual data access implementation for the memmap_accessors

"""
import ctypes
from typing import Any, List, Optional, Sequence

import dask
import dask.array as da
import numpy as np
from numpy._typing import NDArray
from s3fs import S3File

from eopf.common.file_utils import AnyPath
from eopf.common.numpy_utils import froms3file
from eopf.config.config import EOConfiguration
from eopf.dask_utils.dask_helpers import scatter
from eopf.exceptions.errors import AccessorInvalidRequestError
from eopf.logging import EOLogging

PACKET_CACHE_SIZE_PARAM_NAME: str = "accessors__memmap__packet_cache_size"
PACKET_CACHE_SIZE_DEFAULT: int = 1024

EOConfiguration().register_requested_parameter(
    PACKET_CACHE_SIZE_PARAM_NAME,
    PACKET_CACHE_SIZE_DEFAULT,
    True,
    description="Number of packet kept in cache for dask delayed",
)


def _load_chunk(
    url: AnyPath,
    *,
    length_to_load_bytes: int,
    offset_in_file_bytes: int,
    start_byte: int,
    count_byte: int,
    sl: slice,
    shape: tuple[int],
    output_type: Any,
    packet_length_bytes: List[Any],
    mask: Optional[Any],
    shift: Optional[Any],
    dtype: Any = np.dtype("B"),
) -> Any:
    with url.open("rb") as f:
        # numpy.fromfile doesn't work with non local filehandle
        f.seek(offset_in_file_bytes)
        bytes_read = f.read(length_to_load_bytes)
        buffer = np.frombuffer(bytes_read, dtype=dtype)
    # [] operator is inclusive
    nb_packets = sl.stop - sl.start
    if len(shape) > 1:
        parameter = np.zeros(
            (nb_packets, shape[1]),
            dtype=output_type,
        )
    else:
        parameter = np.zeros(
            nb_packets,
            dtype=output_type,
        )

    offset_buffer = start_byte
    if count_byte < 0:
        for p in range(nb_packets):
            end_byte = int(packet_length_bytes[p])
            count_byte = end_byte - start_byte
            parameter[p, 0:count_byte] = buffer[offset_buffer : (offset_buffer + count_byte)]
            offset_buffer += int(packet_length_bytes[p])
    elif mask is None:
        for p in range(nb_packets):
            # fmt: off
            parameter[p,] = buffer[offset_buffer: (offset_buffer + count_byte)]
            # fmt: on
            offset_buffer += int(packet_length_bytes[p])
    elif shift is not None:
        for p in range(nb_packets):
            data = buffer[offset_buffer : (offset_buffer + count_byte)]
            parameter[p] = (int.from_bytes(data, "big") >> shift) & mask
            offset_buffer += int(packet_length_bytes[p])
    del buffer
    return parameter


class MultipleFileMemMap:
    """
    MemMap concatenating multiple data files

    """

    def __init__(
        self,
        urls: Sequence[str | AnyPath],
        *,
        primary_header_length_bytes: int,
        ancillary_header_length_bytes: int,
        packet_length_start_position_bytes: int,
        packet_length_stop_position_bytes: int,
    ):
        """

        Parameters
        ----------
        urls
        primary_header_length_bytes : length in bytes of the primary header of the file
        ancillary_header_length_bytes : length in bytes of the ancillary header of the file
        packet_length_start_position_bytes : start position of the packet length information
        packet_length_stop_position_bytes : stop position of the packet length information
        """
        # packet length for writing only
        self._size: Optional[int] = None
        self._packet_offset_bytes: Any = None
        self._packet_length_bytes: Any = 0
        self._builtin_open = open
        # Init logger
        self._log = EOLogging().get_logger(name="eopf.accessor.memmap_accessor")
        self._loaded: bool = False
        self._to_be_saved: bool = False
        self._n_packets: int = 0
        self._n_packets_per_file: dict[AnyPath, int] = {}
        self._buffer: Any = None
        self._packet_length_per_file_bytes: dict[AnyPath, Any] = {}
        self._packet_offset_per_file_bytes: dict[AnyPath, Any] = {}
        self.urls: list[AnyPath] = [AnyPath.cast(url) for url in urls]
        self._incr_step: int = 10000
        self._ancillary_header_bytes = ancillary_header_length_bytes
        self._primary_header_bytes = primary_header_length_bytes
        self._packet_length_start_position_bytes: int = packet_length_start_position_bytes
        self._packet_length_stop_position_bytes: int = packet_length_stop_position_bytes

    def reset(self) -> None:
        """
        Reset the internal state

        Returns
        -------

        """
        self._loaded = False
        self._to_be_saved = False
        self._n_packets = 0
        self._n_packets_per_file = {}
        self._buffer = None
        self._packet_length_per_file_bytes = {}
        self._packet_offset_per_file_bytes = {}

    @property
    def loaded(self) -> bool:
        return self._loaded

    @property
    def need_save(self) -> bool:
        return self._to_be_saved

    @need_save.setter
    def need_save(self, inval: bool) -> None:
        self._to_be_saved = inval

    def build_buffer(self, packet_len_bytes: Any) -> None:
        """
        Build the internal data buffer to write in case of open(mode=CREATE)

        Parameters
        ----------
        packet_len_bytes :
            length of the packets

        Returns
        None
        -------

        """
        if self._buffer is None:
            self._packet_length_bytes = packet_len_bytes + self._primary_header_bytes + self._ancillary_header_bytes + 1
            self._n_packets = packet_len_bytes.size
            self._size = np.sum(self._packet_length_bytes)
            # FIXME : how to handle back conversion with multiple files
            self._packet_offset_bytes = np.insert(np.cumsum(self._packet_length_bytes[0:-1]), 0, 0, axis=0)
            self._buffer = np.zeros(self._size, dtype="uint8")
            self._to_be_saved = True

    def load_buffer_infos(self) -> None:
        """
        Loop accross packet to build the buffer infos to read the file

        Returns
        -------

        """
        if self._loaded:
            return

        for url in self.urls:
            if not url.exists():
                raise FileNotFoundError(f"{url} not found")
            try:
                with url.open("rb") as f:
                    bytes_read = f.read()
                    self._buffer = np.frombuffer(bytes_read, np.dtype("B"))
            except IOError as e:
                raise IOError(f"Error While Opening {url}, {e}!") from e

            self._n_packets_per_file[url] = 0
            self._packet_length_per_file_bytes[url] = np.zeros(self._incr_step, dtype="uint16")
            self._packet_offset_per_file_bytes[url] = np.zeros(self._incr_step, dtype="uint64")

            k = 0
            while k < len(self._buffer):
                if self._n_packets_per_file[url] == self._packet_length_per_file_bytes[url].shape[0]:
                    self._packet_length_per_file_bytes[url].resize(
                        self._n_packets_per_file[url] + self._incr_step,
                        refcheck=False,
                    )
                    self._packet_offset_per_file_bytes[url].resize(
                        self._n_packets_per_file[url] + self._incr_step,
                        refcheck=False,
                    )
                self._packet_offset_per_file_bytes[url][self._n_packets_per_file[url]] = k
                self._packet_length_per_file_bytes[url][self._n_packets_per_file[url]] = (
                    int.from_bytes(
                        self._buffer[
                            k + self._packet_length_start_position_bytes : k + self._packet_length_stop_position_bytes
                        ],
                        "big",
                    )  # noqa
                    + self._ancillary_header_bytes
                    + self._primary_header_bytes
                    + 1  # noqa
                )
                k += int(self._packet_length_per_file_bytes[url][self._n_packets_per_file[url]])
                self._n_packets_per_file[url] += 1
                self._n_packets += 1
        # End for each url
        # Clear buffer
        self._buffer = None
        # Mark as loaded
        self._loaded = True

    def save_buffer(self) -> None:
        """
        Save the buffer to file
        Returns
        -------

        """
        if self.need_save:
            try:
                # FIXME : how to handle back conversion with multiple files
                with self.urls[0].open("wb") as f:
                    self._buffer.tofile(f)
            except IOError as e:
                raise IOError(f"Error While Opening {self.urls[0]}, {e}!") from e

    def parse_key(self, offset_in_bits: int, length_in_bits: int, output_type: Any) -> Any:
        """
        Parse a key data packets.

        output type has special trigger:
        - var_bytearray : will get all the data as bits type starting from offset to the end of each packet
        - bytearray : same as var_bytearray but this time don't extract all but to the given lenght
        - s_'type' : extract a single element formatted as 'type' from each packet using the params
        - Any other type : extract the data using the params given

        Parameters
        ----------
        offset_in_bits : start of the data in the packet(s)
        length_in_bits : length of the data to extract in packet(s)
        output_type : type to fit the data to

        Returns
        -------
        Dask array containing the data requested
        """
        if not self._loaded:
            self.load_buffer_infos()

        if output_type == "var_bytearray":
            return self._parse_var_bytearray(offset_in_bits)

        if output_type == "bytearray":
            return self._parse_bytearray(offset_in_bits, length_in_bits)

        # Special case when we want a single value, we take the first file
        if output_type[:2] == "s_":
            return self._parse_single_value(offset_in_bits, length_in_bits, output_type[2:])

        # General purpose call
        return self._parse_array(offset_in_bits, length_in_bits, output_type)

    def _parse_array(self, offset_in_bits: int, length_in_bits: int, output_type: Any) -> Any:
        """
        Parse an array in the output type in each packets using the parameters

        Parameters
        ----------
        offset_in_bits : start of the data in the packet(s)
        length_in_bits : length of the data to extract in packet(s)
        output_type : type to fit the data to

        Returns
        -------
        Dask array containing the data requested
        """
        # General case
        nb_packet_cache: int = EOConfiguration()[PACKET_CACHE_SIZE_PARAM_NAME]
        chunk_delayed_loader = dask.delayed(_load_chunk)
        chunks: List[Any] = []
        output_packets = self._n_packets
        shape_one = (output_packets,)
        start_byte = offset_in_bits // 8
        end_byte = (offset_in_bits + length_in_bits - 1) // 8 + 1
        shift = end_byte * 8 - (offset_in_bits + length_in_bits)
        mask = np.sum(2 ** np.arange(length_in_bits))
        count_byte = end_byte - start_byte
        k_global = 0
        for url in self.urls:
            k = 0
            output_packets = int(self._n_packets_per_file[url])
            while k < output_packets:
                nb_packet_loaded = min(nb_packet_cache, output_packets - k)
                scattered_length = scatter(self._packet_length_per_file_bytes[url][k : k + nb_packet_loaded])
                chunk = da.from_delayed(
                    chunk_delayed_loader(
                        url,
                        length_to_load_bytes=int(
                            np.sum(self._packet_length_per_file_bytes[url][k : k + nb_packet_loaded]),
                        ),
                        offset_in_file_bytes=self._packet_offset_per_file_bytes[url][k],
                        start_byte=start_byte,
                        count_byte=count_byte,
                        sl=slice(k, k + nb_packet_loaded),
                        shape=shape_one,
                        output_type=output_type,
                        packet_length_bytes=scattered_length,
                        mask=mask,
                        shift=shift,
                        dtype=np.dtype("B"),
                    ),
                    shape=(nb_packet_loaded,),
                    dtype=output_type,
                )
                chunks.append(chunk)
                k += nb_packet_loaded
            k_global += self._n_packets_per_file[url]
        return da.concatenate(chunks, axis=0)

    def _parse_single_value(self, offset_in_bits: int, length_in_bits: int, output_type: Any) -> Any:
        """
        Parse a single element in the output type in each packet using the parameters

        Parameters
        ----------
        offset_in_bits : start of the data in the packet(s)
        length_in_bits : length of the data to extract in packet(s)
        output_type : type to fit the data to

        Returns
        -------
        Dask array containing the data requested
        """
        parameter = np.zeros(1, dtype=output_type)
        start_byte = offset_in_bits // 8
        end_byte = (offset_in_bits + length_in_bits - 1) // 8 + 1
        shift = end_byte * 8 - (offset_in_bits + length_in_bits)
        mask = np.sum(2 ** np.arange(length_in_bits))
        offset = start_byte
        count_byte = end_byte - start_byte
        with self.urls[0].open("rb") as f:
            if isinstance(f, S3File):
                data = froms3file(f, dtype=np.dtype("B"), count=count_byte, offset=offset)
            else:
                data = np.fromfile(f, dtype=np.dtype("B"), count=count_byte, offset=offset)
            parameter[0] = (int.from_bytes(data, "big") >> shift) & mask
        return da.from_array(parameter)

    def _parse_bytearray(self, offset_in_bits: int, length_in_bits: int) -> Any:
        """
        Parse an array in Byte type in each packet using the parameters

        Parameters
        ----------
        offset_in_bits : start of the data in the packet(s)
        length_in_bits : length of the data to extract in packet(s)


        Returns
        -------
        Dask array containing the data requested
        """
        nb_packet_cache: int = EOConfiguration()[PACKET_CACHE_SIZE_PARAM_NAME]
        chunk_delayed_loader = dask.delayed(_load_chunk)
        chunks: List[Any] = []
        start_byte = offset_in_bits // 8
        end_byte = length_in_bits // 8 + start_byte
        count_byte = end_byte - start_byte
        shape = (self._n_packets, length_in_bits // 8)
        dtype = np.uint8
        k_global = 0
        for url in self.urls:
            k = 0
            output_packets = int(self._n_packets_per_file[url])
            while k < output_packets:
                nb_packet_loaded = min(nb_packet_cache, output_packets - k)
                scattered_length = scatter(self._packet_length_per_file_bytes[url][k : k + nb_packet_loaded])
                chunk = da.from_delayed(
                    chunk_delayed_loader(
                        url,
                        length_to_load_bytes=int(
                            np.sum(self._packet_length_per_file_bytes[url][k : k + nb_packet_loaded]),
                        ),
                        offset_in_file_bytes=self._packet_offset_per_file_bytes[url][k],
                        start_byte=start_byte,
                        count_byte=count_byte,
                        sl=slice(k, k + nb_packet_loaded),
                        shape=shape,
                        output_type=dtype,
                        packet_length_bytes=scattered_length,
                        mask=None,
                        shift=None,
                        dtype=np.dtype("B"),
                    ),
                    shape=(nb_packet_loaded,) + shape[1:],
                    dtype=dtype,
                )
                chunks.append(chunk)
                k += nb_packet_loaded
            k_global += self._n_packets_per_file[url]
        return da.concatenate(chunks, axis=0)

    def _parse_var_bytearray(self, offset_in_bits: int) -> Any:
        """
        Parse a bytearray starting at offset to the end of the packet to Byte type

        Parameters
        ----------
        offset_in_bits : start of the data in the packet(s)

        Returns
        -------

        """
        nb_packet_cache: int = EOConfiguration()[PACKET_CACHE_SIZE_PARAM_NAME]
        chunk_delayed_loader = dask.delayed(_load_chunk)
        chunks: List[Any] = []
        start_byte = int(offset_in_bits // 8)
        # compute max packet size for output size
        max_packet_length = 0
        for pl in self._packet_length_per_file_bytes.values():
            max_packet_length = max(np.max(pl), max_packet_length)
        shape = (self._n_packets, int(max_packet_length - start_byte))
        dtype = np.uint8
        k_global: int = 0
        for url in self.urls:
            k = 0
            output_packets = int(self._n_packets_per_file[url])
            while k < output_packets:
                nb_packet_loaded = min(nb_packet_cache, output_packets - k)
                scattered_length = scatter(self._packet_length_per_file_bytes[url][k : k + nb_packet_loaded])
                chunk = da.from_delayed(
                    chunk_delayed_loader(
                        url,
                        length_to_load_bytes=int(
                            np.sum(self._packet_length_per_file_bytes[url][k : k + nb_packet_loaded]),
                        ),
                        offset_in_file_bytes=self._packet_offset_per_file_bytes[url][k],
                        start_byte=start_byte,
                        count_byte=-1,
                        sl=slice(k, k + nb_packet_loaded),
                        shape=shape,
                        output_type=dtype,
                        packet_length_bytes=scattered_length,
                        mask=None,
                        shift=None,
                        dtype=np.dtype("B"),
                    ),
                    shape=(nb_packet_loaded,) + shape[1:],
                    dtype=dtype,
                )
                chunks.append(chunk)
                k += nb_packet_loaded
            k_global += int(self._n_packets_per_file[url])
        return da.concatenate(chunks)

    def write_key(self, offset_in_bits: int, length_in_bits: int, parameter: NDArray[Any], output_type: Any) -> None:
        """
        Write a  data key to the buffer

        Parameters
        ----------
        offset_in_bits : start offset of the data to write in packets
        length_in_bits : length of the data to write in packets
        parameter : additional parameters
        output_type : output type to map the data to

        Returns
        -------
        None
        """
        if self._buffer is None:
            raise IOError("Buffer is not initialized !")

        if isinstance(parameter, np.ndarray):
            if parameter.size == 0 and length_in_bits != 0:
                raise AccessorInvalidRequestError("Given data is 0 length while it should not")
        elif len(parameter) == 0 and length_in_bits != 0:
            raise AccessorInvalidRequestError("Given data is 0 length while it should not")

        if output_type == "var_bytearray":
            self._write_var_bytearray(offset_in_bits, parameter)
            return

        if output_type == "bytearray":
            self._write_bytearray(offset_in_bits, length_in_bits, parameter)
            return

        self._write_scalar(offset_in_bits, length_in_bits, parameter, output_type)
        return

    def _write_scalar(
        self,
        offset_in_bits: int,
        length_in_bits: int,
        parameter: NDArray[Any],
        output_type: Any,
    ) -> None:
        """
        Specialization of wrike key for scalar values
        Parameters
        ----------
        offset_in_bits : start offset of the data to write in packets
        length_in_bits : length of the data to write in packets
        parameter : additional parameters
        output_type : output type to map the data to

        Returns
        -------

        """
        if parameter.ndim != 1:
            raise AccessorInvalidRequestError(
                f"Data should be of ndim 1 for single element, given {parameter.ndim}",
            )
        output_packets = self._n_packets
        if output_type[:2] == "s_":
            output_packets = 1
            output_type = output_type[2:]
        start_byte = offset_in_bits // 8
        end_byte = (offset_in_bits + length_in_bits - 1) // 8 + 1
        shift = end_byte * 8 - (offset_in_bits + length_in_bits)
        count_byte = end_byte - start_byte
        if output_packets == 1:
            self._write_single_scalar(count_byte, output_type, parameter, shift, start_byte)
        else:
            for k in range(self._n_packets):
                offset_byte = int(self._packet_offset_bytes[k]) + start_byte
                if output_type == "float":
                    self._buffer[offset_byte : offset_byte + count_byte] |= np.frombuffer(  # noqa
                        int(
                            np.frombuffer(ctypes.c_float(parameter[k]), "uint32") << shift,  # type: ignore # noqa
                        ).to_bytes(
                            count_byte,
                            "big",
                        ),
                        "uint8",
                        count_byte,
                        0,
                    )
                elif output_type == "double":
                    self._buffer[offset_byte : offset_byte + count_byte] |= np.frombuffer(  # noqa
                        int(
                            np.frombuffer(ctypes.c_double(parameter[k]), "uint64") << shift,  # type: ignore # noqa
                        ).to_bytes(
                            count_byte,
                            "big",
                        ),
                        "uint8",
                        count_byte,
                        0,
                    )
                elif output_type == "uint64":
                    self._buffer[offset_byte : offset_byte + count_byte] |= np.frombuffer(  # noqa
                        int(
                            np.frombuffer(ctypes.c_uint64(parameter[k]), "uint64") << shift,  # type: ignore # noqa
                        ).to_bytes(
                            count_byte,
                            "big",
                        ),
                        "uint8",
                        count_byte,
                        0,
                    )
                else:
                    self._buffer[offset_byte : offset_byte + count_byte] |= np.frombuffer(  # noqa
                        int(parameter[k] << shift).to_bytes(count_byte, "big"),
                        "uint8",
                        count_byte,
                        0,
                    )

    def _write_single_scalar(
        self,
        count_byte: int,
        output_type: Any,
        parameter: NDArray[Any],
        shift: int,
        start_byte: int,
    ) -> None:
        """
        Write a single scalar value

        Parameters
        ----------
        count_byte
        output_type
        parameter
        shift
        start_byte

        Returns
        -------

        """
        if output_type == "float":
            arr_to_cast = np.frombuffer(ctypes.c_float(parameter[0]), "uint32")  # type: ignore
        elif output_type == "double":
            arr_to_cast = np.frombuffer(ctypes.c_double(parameter[0]), "uint64")  # type: ignore
            if shift:
                raise AccessorInvalidRequestError("Not possible to have shift on a unint64 type !!!")
        elif output_type == "uint64":
            arr_to_cast = np.array(np.frombuffer(ctypes.c_uint64(parameter[0]), "uint64")[0])  # type: ignore
            if shift:
                raise AccessorInvalidRequestError("Not possible to have shift on a unint64 type !!!")
        else:
            arr_to_cast = np.array(parameter[0])
        data_to_cast = arr_to_cast << shift if shift != 0 else arr_to_cast
        param = np.frombuffer(
            int(data_to_cast).to_bytes(
                count_byte,
                "big",
            ),
            "uint8",
            count_byte,
            0,
        )
        offset_byte = int(self._packet_offset_bytes[0]) + start_byte
        self._buffer[offset_byte : offset_byte + count_byte] |= param  # noqa

    def _write_bytearray(self, offset_in_bits: int, length_in_bits: int, parameter: NDArray[Any]) -> None:
        if parameter.ndim != 2:
            raise AccessorInvalidRequestError(f"Data should be of ndim 2 for bytearray, given {parameter.ndim}")
        start_byte = offset_in_bits // 8
        end_byte = length_in_bits // 8 + start_byte
        count_byte = end_byte - start_byte
        for k in range(self._n_packets):
            offset_byte = int(self._packet_offset_bytes[k]) + start_byte
            self._buffer[offset_byte : offset_byte + count_byte] = parameter[k, 0:count_byte]  # noqa

    def _write_var_bytearray(self, offset_in_bits: int, parameter: NDArray[Any]) -> None:
        if parameter.ndim != 2:
            raise AccessorInvalidRequestError(f"Data should be of ndim 2 for bytearray, given {parameter.ndim}")
        start_byte = int(offset_in_bits // 8)
        for k in range(int(self._n_packets)):
            end_byte = int(self._packet_length_bytes[k])
            offset_byte = int(self._packet_offset_bytes[k]) + start_byte
            count_byte = end_byte - start_byte
            self._buffer[offset_byte : offset_byte + count_byte] = parameter[k, 0:count_byte]  # noqa


class MemMap(MultipleFileMemMap):
    """
    Single file MemMap

    """

    def __init__(
        self,
        url: str | AnyPath,
        primary_header_length_bytes: int,
        ancillary_header_length_bytes: int,
        packet_length_start_position_bytes: int,
        packet_length_stop_position_bytes: int,
    ):
        super().__init__(
            [AnyPath.cast(url)],
            primary_header_length_bytes=primary_header_length_bytes,
            ancillary_header_length_bytes=ancillary_header_length_bytes,
            packet_length_start_position_bytes=packet_length_start_position_bytes,
            packet_length_stop_position_bytes=packet_length_stop_position_bytes,
        )
        if hasattr(self, "url"):
            return
        self.url: AnyPath = AnyPath.cast(url)


class FixedMemMap(MultipleFileMemMap):
    """
    Speicalized multiple file memap for data with fixed lenght packets

    """

    def __init__(
        self,
        url: str | AnyPath,
        fixed_packet_length_bytes: int,
    ):
        super().__init__(
            [AnyPath.cast(url)],
            primary_header_length_bytes=0,
            ancillary_header_length_bytes=0,
            packet_length_start_position_bytes=0,
            packet_length_stop_position_bytes=0,
        )
        self._size: Optional[int] = None
        if hasattr(self, "url"):
            return
        self.url: AnyPath = AnyPath.cast(url)
        self.fixed_packet_length_bytes: int = fixed_packet_length_bytes

    def build_buffer(self, packet_number: int) -> None:
        if self._buffer is None:
            self._n_packets = packet_number
            self._size = self.fixed_packet_length_bytes * self._n_packets
            self._packet_length_bytes = np.full(
                self._n_packets,
                dtype="uint",
                fill_value=self.fixed_packet_length_bytes,
            )
            self._packet_offset_bytes = np.zeros(self._n_packets, dtype="uint")
            for i in range(self._n_packets):
                self._packet_offset_bytes[i] = i * self.fixed_packet_length_bytes
            self._buffer = np.zeros(self._size, dtype="uint8")
            self._to_be_saved = True

    def load_buffer_infos(self) -> None:
        if self._loaded:
            return

        try:
            self._size = int(self.url.info()["size"])
        except IOError as e:
            raise IOError(f"Error While Opening {self.url}, {e}!") from e

        if self._size % self.fixed_packet_length_bytes != 0:
            self._log.warning(
                f"Packet length doesn't match with the file size : {self._size} % "
                f"{self.fixed_packet_length_bytes} != 0 on {self.url}",
            )

        self._n_packets_per_file[self.url] = int(self._size / self.fixed_packet_length_bytes)
        self._n_packets = self._n_packets_per_file[self.url]
        if self.fixed_packet_length_bytes > np.iinfo("uint16").max:
            self._packet_length_per_file_bytes[self.url] = np.full(
                self._n_packets_per_file[self.url],
                dtype="uint16",
                fill_value=self.fixed_packet_length_bytes,
            )
        else:
            self._packet_length_per_file_bytes[self.url] = np.full(
                self._n_packets_per_file[self.url],
                dtype="uint32",
                fill_value=self.fixed_packet_length_bytes,
            )
        self._packet_offset_per_file_bytes[self.url] = np.zeros(self._n_packets_per_file[self.url], dtype="uint")
        self._packet_offset_per_file_bytes[self.url] = range(
            0,
            self._n_packets * self.fixed_packet_length_bytes,
            self.fixed_packet_length_bytes,
        )

        # End for each url
        # Clear buffer
        self._buffer = None
        # Mark as loaded
        self._loaded = True
