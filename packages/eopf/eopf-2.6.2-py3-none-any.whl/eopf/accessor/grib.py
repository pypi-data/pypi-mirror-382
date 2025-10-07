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

grib.py

GRIB data accessor implementation

"""

from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Iterator,
    KeysView,
    MutableMapping,
    Optional,
    cast,
)

import xarray as xr

from eopf.accessor import EOAccessorFactory
from eopf.accessor.abstract import EOReadOnlyAccessor
from eopf.common.constants import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.common.functions_utils import not_none
from eopf.common.type_utils import Chunk
from eopf.product import EOVariable
from eopf.product.eo_group import EOGroup
from eopf.product.utils.eopath_utils import downsplit_eo_path

if TYPE_CHECKING:  # pragma: no cover
    from eopf.accessor.abstract import EOAccessor
    from eopf.product.eo_object import EOObject


@EOAccessorFactory.register_accessor("grib")
class EOGribAccessor(EOReadOnlyAccessor):
    """
     GRIB file accessor to extract data from Grib
     File is opened using xarray open dataset using cfgrib

    Examples
     --------
     >>> grib_store = EOGribAccessor("AUX_ECMWFT.grib")
     >>> with open_accessor(grib_store, indexpath=""):
     >>>   grib_store["msl"]

    """

    _DATA_KEY = "values"
    _COORDINATE_0_KEY = "distinctLatitudes"
    _COORDINATE_1_KEY = "distinctLongitudes"

    def __init__(self, url: str | AnyPath, **kwargs: Any) -> None:
        super().__init__(url, **kwargs)
        # open is the file reader class.
        self._ds: Optional[xr.Dataset] = None

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

        # open is a class (constructor).
        if "mask_and_scale" in kwargs:
            kwargs.pop("mask_and_scale")
        local_path: AnyPath = self.url.get()
        kwargs_args = {key: val for key, val in kwargs.items() if key != "chunks"}
        self._ds = xr.open_dataset(local_path.path, engine="cfgrib", chunks=self._chunk_sizes, **kwargs_args)
        # Declare it opened when we know all ressources are allocated
        super().open(mode, chunk_sizes, **kwargs)
        return self

    def close(self) -> None:
        self.check_is_opened()
        not_none(self._ds).close()
        self._ds = None
        super().close()

    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        return path in ["", "/", "coordinates", "/coordinates", "coordinates/", "/coordinates/"]

    def is_variable(self, path: str) -> bool:
        self.check_is_opened()
        group, sub_path = downsplit_eo_path(path)
        if group == "coordinates":
            return sub_path in not_none(self._ds).coords
        return path in not_none(self._ds)

    def iter(self, path: str) -> Iterator[str]:
        self.check_is_opened()
        keys: Iterable[str]
        if path in ["", "/"]:
            keys = ["coordinates", *cast(KeysView[str], not_none(self._ds).keys())]
        elif path in ["coordinates", "/coordinates", "coordinates/", "/coordinates/"]:
            keys = cast(KeysView[str], not_none(self._ds).coords.keys())
        else:
            raise KeyError(f"key {path} not exist")
        return iter(keys)

    def __getitem__(self, key: str) -> "EOObject":
        """

        Parameters
        ----------
        key :
        data name to get from the grib

        Returns
        -------
        EOVariable with data or empty group if the key aims to the group

        """
        self.check_is_opened()
        if self.is_group(key):
            return EOGroup()
        if not self.is_variable(key):
            raise KeyError(f"{key} not found in {self.url}")
        group, sub_path = downsplit_eo_path(key)
        if group == "coordinates":
            data = not_none(self._ds).coords[sub_path]
        else:
            data = not_none(self._ds)[key]
        return EOVariable(data=data)

    def __setitem__(self, key: str, value: "EOObject") -> None:
        raise NotImplementedError()

    def __len__(self) -> int:
        self.check_is_opened()
        # We have one group (coordinates).
        return 1 + len(not_none(self._ds))

    @staticmethod
    def guess_can_read(file_path: str) -> bool:
        return AnyPath(file_path).suffix in [".grib"]

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        raise NotImplementedError()
