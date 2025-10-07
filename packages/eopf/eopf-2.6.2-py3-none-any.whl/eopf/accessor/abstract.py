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

abstract.py

abstract classes definition for EOAccessors

"""

import enum
from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from types import TracebackType
from typing import TYPE_CHECKING, Any, Iterator, Optional, Type

from eopf.common.constants import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.common.type_utils import Chunk
from eopf.config.config import EOConfiguration
from eopf.exceptions import AccessorNotOpenError
from eopf.logging import EOLogging

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject


class AccessorStatus(enum.Enum):
    """Possible status of an EOAccessor"""

    OPEN = "open"
    CLOSE = "close"


class EOAccessor(MutableMapping[str, Any]):
    """Abstract accessor representation to access to a data


    Parameters
    ----------

    Attributes
    ----------
    """

    accessor_id = "default"
    # attrs used for conveting form zarr to safe
    _reconversion_attrs: Any = None
    # list of attributes to remove from EOAccessor constructor and
    # to use during the EOAccessor.get_data call as kwargs.
    _dynamic_params: list[str] = []

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        self.url = AnyPath.cast(url, **kwargs.get("storage_options", {}))
        self._status = AccessorStatus.CLOSE
        self._mode: OpeningMode = OpeningMode.OPEN
        self._config: dict[str, Any] = {}
        self._mask_and_scale = True
        self._kwargs = kwargs
        self._logger = EOLogging().get_logger("eopf.accessor.abstract")
        eopf_config = EOConfiguration()

        if "mask_and_scale" not in kwargs:
            self._kwargs["mask_and_scale"] = eopf_config.get("product__mask_and_scale")
        self._chunk_sizes: Optional[Chunk] = None

    def get_data(self, key: str, **kwargs: Any) -> "EOObject":
        return self[key]

    def __del__(self) -> None:
        if hasattr(self, "_status") and self._status != AccessorStatus.CLOSE:
            try:
                self.close()
            except AccessorNotOpenError:
                # Caused by deletion caused by exceptions in the init issues.
                self._status = AccessorStatus.CLOSE

    def __delitem__(self, key: str) -> None:  # pragma: no cover
        raise NotImplementedError()

    def __iter__(self) -> Iterator[str]:
        return self.iter("")

    def __enter__(self) -> "EOAccessor":
        return self

    def __len__(self) -> int:
        return 0

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self._status != AccessorStatus.CLOSE:
            try:
                self.close()
            except AccessorNotOpenError:
                # Caused by deletion caused by exceptions in the init issues.
                self._status = AccessorStatus.CLOSE

    def iter(self, path: str) -> Iterator[str]:
        """Iterate over the given path

        Parameters
        ----------
        path: str
            path to the object to iterate over

        Returns
        -------
        Iterator[str]
            An iterator of the paths inside the given path

        Raises
        ------
        AccessorNotOpenError
            If the store is closed
        """
        yield from ()

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """Open the store in the given mode

        Parameters
        ----------
        mode: OpeningMode | str , optional
            mode to open the store; default to open
        chunk_sizes: Chunk
            Chunk sizes along each dimension
        **kwargs: Any
            extra kwargs of open on library used
        """
        if self._status == AccessorStatus.OPEN:
            self._logger.warning(f"Accessor {self} is already open !!!")
        self._status = AccessorStatus.OPEN
        self._mode = OpeningMode.cast(mode)
        self._chunk_sizes = chunk_sizes
        return self

    @classmethod
    def trim_params(cls, params: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Trim dynamic parameters from the input dictionary.

        This method separates the input dictionary into two dictionaries: one containing the dynamic parameters
        specified in the class attribute `_dynamic_params` and the other containing the remaining parameters.

        Parameters
        ----------
        params : dict[str, Any]
            The input dictionary containing parameters to be processed.

        Returns
        -------
        tuple[dict[str, Any], dict[str, Any]]
            A tuple containing two dictionaries

        Examples
        --------
        ::

                >>> params = {"param1": "value1", "param4": "value4", "param2": "value2"}
                >>> input_params, trimmed_params = MyClass.trim_params(params)
                >>> input_params
                {'param4': 'value4'}
                >>> trimmed_params
                {'param1': 'value1', 'param2': 'value2'}

        """
        input_params = dict(params)
        trimed_params = {
            param_to_pop: input_params.pop(param_to_pop)
            for param_to_pop in cls._dynamic_params
            if param_to_pop in input_params
        }
        return input_params, trimed_params

    def close(self) -> None:
        """Close the store"""
        if self._status == AccessorStatus.CLOSE:
            raise AccessorNotOpenError("Accessor must be open before close it")
        self._status = AccessorStatus.CLOSE

    def write(self) -> None:
        """
        Write non synchronized subgroups, variables to the accessor

        the accessor must be opened to work

        Parameters
        ----------

        Raises
        ------
        AccessorNotOpenError
            Trying to write in a closed store

        See Also
        --------
        """

    @property
    def status(self) -> AccessorStatus:
        """AccessorStatus: give the current status (open or close) of this accessor"""
        return self._status

    @staticmethod
    def guess_can_read(file_path: str) -> bool:
        """The given file path is readable or not by this store

        Parameters
        ----------
        file_path: str
            File path to check

        Returns
        -------
        bool
        """
        return False

    @abstractmethod
    def is_group(self, path: str) -> bool:
        """Check if the given path under root corresponding to a group representation

        Parameters
        ----------
        path: str
            path to check

        Returns
        -------
        bool
            it is a group representation or not

        Raises
        ------
        AccessorNotOpenError
            If the store is closed
        """

    @abstractmethod
    def is_variable(self, path: str) -> bool:
        """Check if the given path under root corresponding to a variable representation

        Parameters
        ----------
        path: str
            path to check

        Returns
        -------
        bool
            it is a variable representation or not

        Raises
        ------
        AccessorNotOpenError
            If the store is closed
        """

    @property
    def is_readable(self) -> bool:
        """bool: this store can be read or not"""
        return True

    @property
    def is_listable(self) -> bool:
        """bool: this store can be list or not"""
        return True

    @property
    def scale_and_mask(self) -> bool:
        """Apply the mask and scale or not"""
        return self._mask_and_scale

    @scale_and_mask.setter
    def scale_and_mask(self, newval: bool) -> None:
        self._mask_and_scale = newval

    @abstractmethod
    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        """Update attrs in the store

        Parameters
        ----------
        group_path: str
            path of the object to write attributes
        attrs: MutableMapping[str, Any], optional
            dict like representation of attributes to write

        Raises
        ------
        AccessorNotOpenError
            If the store is closed
        """

    def set_config(self, conf: dict[str, Any]) -> None:
        """
        Set the current config for data access
        """
        self._config = conf

    def get_config(self) -> dict[str, Any]:
        return self._config

    @staticmethod
    def strip_config(conf: dict[str, Any]) -> dict[str, Any]:
        """
        Remove from this config any elements that can be handled at access time
        for example the target_type in meme_map can be modified at access time

        """
        return conf

    def check_is_opened(self) -> None:
        """
        Check if the accessor is opened. Raises an exception if not.

        Parameters
        ----------

        Raises
        ------
        StoreNotOpenError
            Trying to use an accessor before opening it.

        See Also
        --------
        """
        if self.status is not AccessorStatus.OPEN:
            raise AccessorNotOpenError("Accessor must be opened before using it")


class EOReadOnlyAccessor(EOAccessor, ABC):
    """
    Read only version of accessor

    """

    def __setitem__(self, k: str, v: "EOObject") -> None:
        raise NotImplementedError()

    @property
    def is_erasable(self) -> bool:
        """bool: this store can be erase or not"""
        return False

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":

        super().open(mode, chunk_sizes, **kwargs)
        if self._mode not in [OpeningMode.OPEN, OpeningMode.UPDATE]:
            raise NotImplementedError("Read only accessor, only ")
        return self

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        raise NotImplementedError()
