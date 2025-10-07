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

EOStore abstract classes

"""
import enum
from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from types import TracebackType
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Type, Union

from eopf import EOConfiguration, EOProduct
from eopf.common.constants import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.exceptions import StoreNotOpenError
from eopf.exceptions.errors import EOStoreInvalidPathError
from eopf.exceptions.warnings import AlreadyOpen
from eopf.logging import EOLogging

EOConfiguration().register_requested_parameter(
    "product__mask_and_scale",
    True,
    description="Activate default mask and scale on product read/write",
)

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_container import EOContainer
    from eopf.product.eo_object import EOObject


class StorageStatus(enum.Enum):
    """Possible status of an EOProductStore"""

    OPEN = "open"
    CLOSE = "close"


class EOProductStore(MutableMapping[str, "EOObject"]):
    """Abstract store representation to access to a files on the given URL

    Inherit from MutableMapping to indexes objects with there corresponding
    path.

    Parameters
    ----------
    url: str
        path url or the target store

    Attributes
    ----------
    url: str
        url to the target store
    """

    URL_VALIDITY_DESCRIPTION = ""
    PRODUCT_VALIDITY_DESCRIPTION = ""
    EXTENSION = ""

    sep: str = "/"
    # attrs used for conveting form zarr to safe
    _reconversion_attrs: Any = None

    @classmethod
    def create_product(
        cls,
        url: str | AnyPath,
        name: str,
        attrs: Optional[MutableMapping[str, Any]] = None,
        product_type: str = "",
        strict: bool = False,
        **kwargs: Any,
    ) -> "EOProduct":
        return EOProduct(
            name=name,
            storage_driver=cls,
            url=url,
            product_type=product_type,
            strict=strict,
            attrs=attrs,
            **kwargs,
        )

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        self._url: AnyPath = AnyPath.cast(url, **kwargs.get("storage_options", {}))
        self._status = StorageStatus.CLOSE
        self._mode: Optional[OpeningMode] = None
        self._logger = EOLogging().get_logger("eopf.store.safe")
        if not self.is_valid_url(self._url):
            raise EOStoreInvalidPathError(
                f"{str(self._url)} is no a valid filename for store {self.__class__.__name__}"
                f", check filename and extension, requested : {self.URL_VALIDITY_DESCRIPTION}",
            )

    def __del__(self) -> None:
        self.close()

    def __enter__(self) -> "EOProductStore":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.close()

    def __delitem__(self, key: str) -> None:  # pragma: no cover
        raise NotImplementedError()

    def __iter__(self) -> Iterator[str]:
        return self.iter("")

    def open(self, mode: OpeningMode | str = OpeningMode.OPEN, **kwargs: Any) -> "EOProductStore":
        """Open the store in the given mode

        Parameters
        ----------
        mode: str, optional
            mode to open the store
        **kwargs: Any
            extra kwargs of open on library used
        """
        if self._status == StorageStatus.OPEN:
            self._logger.warning(AlreadyOpen())
        self._status = StorageStatus.OPEN
        self._mode = OpeningMode.cast(mode)
        return self

    def is_open(self) -> bool:
        return self.status == StorageStatus.OPEN

    def check_is_opened(self) -> None:
        """
        Check if the store is opened. Raises an exception if not.

        Parameters
        ----------

        Raises
        ------
        StoreNotOpenError
            Trying to use a store before opening it.

        See Also
        --------
        """
        if not self.is_open():
            raise StoreNotOpenError("Store must be opened before accessing it")

    @abstractmethod
    def load(self, name: str = "", **kwargs: Dict[str, Any]) -> Union["EOProduct", "EOContainer"]:
        """
        Load an entire hierarchy of EOObj.
        Since all variables are dask lazy loaded elements this should be fast

        """

    @abstractmethod
    def write_attrs(self, group_path: str, attrs: MutableMapping[str, Any]) -> None:
        """Update attrs in the store

        Parameters
        ----------
        group_path: str
            path of the object to write attributes
        attrs: MutableMapping[str, Any], optional
            dict like representation of attributes to write

        Raises
        ------
        StoreNotOpenError
            If the store is closed
        """
        self.check_is_opened()

    def close(self, cancel_flush: bool = False) -> None:
        """
        Close the store
        cancel_flush: cancel any ongoing operations, used on case of crash on dak for example to cancel the futures
        """
        if hasattr(self, "_status"):
            # errors might araise before the initialisation
            # thus we need to check for the _status existence
            self._status = StorageStatus.CLOSE

    @property
    def is_erasable(self) -> bool:
        """bool: this store can be erased or not"""
        return True

    @property
    def url(self) -> AnyPath:
        return self._url

    @property
    def mode(self) -> Optional[OpeningMode]:
        """
        Get the opening mode
        Returns
        -------
        The opening mode register_requested_parameter by the open call
        """
        return self._mode

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
        StoreNotOpenError
            If the store is closed
        """

    @abstractmethod
    def is_product(self, path: str) -> bool:
        """Check if the given path under root corresponding to a product representation

        Parameters
        ----------
        path: str
            path to check

        Returns
        -------
        bool
            it is a product representation or not

        Raises
        ------
        StoreNotOpenError
            If the store is closed
        """

    @property
    def is_listable(self) -> bool:
        """bool: this store can be list or not"""
        return True

    @property
    def is_readable(self) -> bool:
        """bool: this store can be read or not"""
        return True

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
        StoreNotOpenError
            If the store is closed
        """

    @property
    def is_writeable(self) -> bool:
        """bool: this store can be write or not"""
        return True

    @abstractmethod
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
        StoreNotOpenError
            If the store is closed
        """

    @property
    def status(self) -> StorageStatus:
        """StorageStatus: give the current status (open or close) of this store"""
        return self._status

    @staticmethod
    def guess_can_read(file_path: str | AnyPath, **kwargs: Any) -> bool:
        """The given file path is readable or not by this store

        Parameters
        ----------
        storage_options
        file_path: str
            File path to check

        Returns
        -------
        bool
        """
        return False

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
        file_fspath: AnyPath = AnyPath.cast(file_path, **kwargs.get("storage_options", {}))
        return file_fspath.exists()


class EOReadOnlyStore(EOProductStore, ABC):
    """
    Read only store
    """

    def __setitem__(self, k: str, v: "EOObject") -> None:
        raise NotImplementedError()

    @property
    def is_erasable(self) -> bool:
        """bool: this store can be erase or not"""
        return False

    @property
    def is_writeable(self) -> bool:
        """bool: this store can be write or not"""
        return False

    def open(self, mode: OpeningMode | str = OpeningMode.OPEN, **kwargs: Any) -> "EOProductStore":
        super().open(mode, **kwargs)
        if self._mode != OpeningMode.OPEN:
            raise NotImplementedError("Read only product store")

        return self

    def write_attrs(self, group_path: str, attrs: MutableMapping[str, Any]) -> None:
        raise NotImplementedError()
