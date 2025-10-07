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
filename_to_variable.py

Accessor to transform the filename to an attribute

"""

import datetime
import re
from typing import TYPE_CHECKING, Any, Iterator, MutableMapping, NamedTuple, Optional

from eopf import EOGroup
from eopf.accessor import EOAccessor, EOAccessorFactory
from eopf.common.constants import OpeningMode
from eopf.common.type_utils import Chunk
from eopf.exceptions.errors import AccessorInvalidRequestError
from eopf.product.eo_variable import EOVariable

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject


class FilePart(NamedTuple):
    """Data class to aggregate file information for :obj:`FilenameToVariableAccessor`"""

    value: int
    start_time: datetime.datetime
    end_time: datetime.datetime

    @classmethod
    def from_string(cls, string: str) -> "FilePart":
        """Create instance of FilePart from the filename as a string"""
        time_format = "%Y%m%dt%H%M%S"
        times = re.findall(
            r"[\d]+t[\d]+",
            string,
        )
        file_type_str = string.split("-")[1]
        value = int(file_type_str[-1]) if len(file_type_str) == 3 else 0
        if len(times) != 2:
            raise ValueError(f"{times} from {string} does not contain two times")
        return cls(
            value,
            datetime.datetime.strptime(times[0], time_format),
            datetime.datetime.strptime(times[1], time_format),
        )


# MB: filenames of a wave mode product have several files in the measurements directory.
# (I though that we have that with image mode already, but it seems this is not true.)
# The information on the sub-swath is the second element of the file name.
# Some are wv1, others are wv2. For an imaging mode the file name contains either iw or ew in this position.
# The filename_to_subswath accessor shall translate the file name into a variable with a
# dimension that is the number of files and with values 0, 1 or 2 depending on the file name of the respective file.
# The accessor shall sort the files by time.


@EOAccessorFactory.register_accessor("filename_to_subswath")
class FilenameToVariableAccessor(EOAccessor):
    """Convert Filename in measurement of legacy product to a specific variable"""

    def __getitem__(self, key: str) -> "EOObject":
        self.check_node(key)

        target = self.url / key
        files_infos = [(f, FilePart.from_string(f.basename)) for f in target.ls()]
        data = [d[0].cat() for d in sorted(files_infos, key=lambda x: x[1].start_time)]
        dim = len(data)
        return EOVariable(data=data, dims=(str(dim),))

    def __len__(self) -> int:
        return 0

    def __setitem__(self, key: str, value: "EOObject") -> None:
        raise NotImplementedError()

    def iter(self, path: str) -> Iterator[str]:
        self.check_node(path)
        return iter([])

    def is_group(self, path: str) -> bool:
        self.check_node(path)
        return False

    def is_variable(self, path: str) -> bool:
        self.check_node(path)
        return True

    def check_node(self, path: str) -> None:
        self.check_is_opened()
        target = self.url / path
        if not target.isdir():
            raise AccessorInvalidRequestError(f"No {path} available in {self.url}")

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        raise NotImplementedError()


@EOAccessorFactory.register_accessor("path_to_attr")
class PathToAttrAccessor(EOAccessor):
    """Return granule name of S2 L0 products"""

    def __init__(self, url: str, **kwargs: Any):
        super().__init__(url, **kwargs)

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        super().open(mode, **kwargs)
        return self

    def __getitem__(self, key: str) -> "EOObject":
        self._check_node(key)

        paths_found = sorted(self.url.glob(key))
        if len(paths_found) == 0:
            raise FileNotFoundError(f"No files found in {self.url}/{key}")

        path_obj = paths_found[0]

        if "GRANULE" in path_obj.path:
            # sentinel 2 granule folder
            group_name = "granule"
        elif "DATASTRIP" in path_obj.path:
            # sentinel 2 datastrip folder
            group_name = "datastrip"
        elif "measurement" in path_obj.path:
            # sentinel 1 level 2 measurement dataset
            group_name = "dataset"
        else:
            raise KeyError(f"No group found for {path_obj!r}")

        return EOGroup(group_name, attrs={group_name: path_obj.basename})

    def __setitem__(self, key: str, value: "EOObject") -> None:
        raise NotImplementedError()

    def __len__(self) -> int:
        return 0

    def iter(self, path: str) -> Iterator[str]:
        self._check_node(path)
        return iter([])

    def is_group(self, path: str) -> bool:
        self._check_node(path)
        return False

    def is_variable(self, path: str) -> bool:
        self._check_node(path)
        return True

    def _check_node(self, path: str) -> None:
        self.check_is_opened()
        if path not in ["", self.url.sep]:
            raise AccessorInvalidRequestError(f"No {path} available in {self.url}")

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        # this a read-only accessor
        pass
