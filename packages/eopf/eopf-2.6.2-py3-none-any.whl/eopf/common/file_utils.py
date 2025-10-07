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
file_utils.py

file handling utilities

"""
import glob
import json
import os
import re
from pathlib import Path, PurePath, PurePosixPath
from typing import Any, MutableMapping, Self, Tuple, Union, cast

import fsspec
import s3fs
import yaml
from fsspec.implementations.local import make_path_posix
from fsspec.implementations.reference import ReferenceFileSystem
from zarr._storage.store import Store
from zarr.storage import FSStore

from eopf.exceptions import JSONParsingError

PROTOCOL_MARK = "://"

PROTOCOL_SEP = "::"


class AnyPath:
    """
    Wrapper of different types of path (local, remote, archives, ...)

    This class relies on fsspec to do most of the job.
    """

    def __init__(
        self,
        url: str,
        *,
        parent: Self | None = None,
        trim_archive_component: bool = True,
        auto_open_archives: bool = True,
        **kwargs: dict[str, Any],
    ):
        """
        Constructor, build the adequate fsspec filesystem. The keyword arguments are passed directly
        to fsspec.

        :param url: Input URL
        :param parent: Parent object, we may depend on its filesystem (None by default)
        :param trim_archive_component: Flag to skip the first component when opening archives. A lot
            of archives are just a "folder" compressed to an archive "folder.zip". When listing, the
            content of the archive, this flag allows to directly skip the first component in a path
            like "folder/some_file.txt".
        """

        path: str = url
        self._path: str = ""
        self._original_url = url
        self._parent: Self | None = None
        self._fs = fsspec.filesystem("file")
        self._auto_open_archives = auto_open_archives
        self._trim_archive_component = trim_archive_component
        self._tmp_dir: Self | None = None

        # start by detecting protocol (default is 'local')
        prefix_size, protocol, protocol_length, protocol_list = AnyPath._resolve_protocols(path)

        # resolve parent protocols first
        if len(protocol_list) > 1:
            self._parent = type(self)(
                path[prefix_size:],
                parent=None,
                trim_archive_component=self._trim_archive_component,
                auto_open_archives=False,
                **kwargs,
            )
        elif isinstance(parent, type(self)):
            self._parent = parent

        # clean path from protocol marks
        if protocol not in ("https", "http"):
            path = path[protocol_length:]

        # resolve current protocol
        self._init_fs_and_path(path, protocol, **kwargs)

        # detect if any sub filesystem has to be done, for example zips
        self._detect_sub_filesystems()

    @staticmethod
    def _resolve_protocols(path: str) -> Tuple[int, str, int, list[str]]:
        # start by detecting protocol (default is 'local')
        protocol = "local"
        prefix_size = 0
        protocol_length = 0
        protocol_list = []
        protocol_sep = path.find(PROTOCOL_MARK)
        if protocol_sep > 0:
            protocol_list = path[:protocol_sep].split(PROTOCOL_SEP)
            protocol_length = protocol_sep + len(PROTOCOL_MARK)
        if len(protocol_list) > 0:
            protocol = protocol_list[0]
            if len(protocol_list) == 1:
                prefix_size = len(protocol + PROTOCOL_MARK)
            else:
                prefix_size = len(protocol + PROTOCOL_SEP)
        elif path.startswith("file:"):
            protocol_length = 5
        elif path.startswith("local:"):
            protocol_length = 6
        elif path.startswith("s3:"):
            protocol_length = 3
            protocol = "s3"
        elif path.startswith("zip::"):
            protocol_length = 5
            protocol = "zip"
        return prefix_size, protocol, protocol_length, protocol_list

    def _init_fs_and_path(
        self,
        path: str,
        protocol: str,
        **kwargs: dict[str, Any],
    ) -> None:
        if protocol == "s3":
            self._fs = s3fs.S3FileSystem(**kwargs)

        elif protocol == "reference":
            path = self._init_reference_fs(path, **kwargs)

        elif protocol == "zip":
            path = self._init_zip_fs(path)

        elif protocol == "local":
            path = make_path_posix(path)
            # remove redundant // or /./
            path = os.path.normpath(path)

        elif protocol == "https":
            self._fs = fsspec.filesystem("https")

        elif protocol == "http":
            self._fs = fsspec.filesystem("http")

        # remove trailing / etc
        self._path = self._clean_path(path)

    def _init_zip_fs(self, path: str) -> str:
        if self._parent is None:
            source_fs = fsspec.filesystem("file")
            source_url = make_path_posix(path)
        else:
            source_fs = self._parent.filesystem
            source_url = self._parent.path
        if source_fs.isfile(source_url):
            # Open archive
            self._fs = fsspec.filesystem("zip", fo=source_fs.open(source_url))
            path = ""
            if self._trim_archive_component:
                path = self._get_archive_component()
        else:
            # missing file coming from source filesystem: we expose source filesystem
            path = source_url
            self._fs = source_fs
            if self._parent is not None:
                # collapse one level
                next_parent = self._parent.parent
                self._parent = next_parent
        return path

    def _init_reference_fs(self, path: str, **kwargs: dict[str, Any]) -> str:
        if self._parent is None:
            source_fs = fsspec.filesystem("file")
            source_url = make_path_posix(path)
            path = ""
        else:
            source_fs = self._parent.filesystem
            source_url = self._parent.path
        if "fo" in kwargs:
            fo = kwargs.pop("fo")
        else:
            fo = source_fs.open(source_url, mode="rb")
        self._fs = ReferenceFileSystem(fo=fo, fs=source_fs, **kwargs)
        return path

    def _clean_path(self, path: str) -> str:
        """
        Clean the path from any unwanted stuff
        Parameters
        ----------
        path

        Returns
        -------

        """

        # remove trailing dot
        if path.endswith("/."):
            path = path[:-1]
        # remove trailing separator
        path = path.rstrip(self._fs.sep) or self._fs.root_marker
        return path

    def _detect_sub_filesystems(self) -> None:
        """
        Will detect sub filesystems and add a new parent to the current AnyPath

        typical example is a zip file found inside an other filesystem

        Parameters
        ----------
        path

        Returns
        -------

        """

        # automatically detect zip filename and add a zip filesystem to it if it is not a zip fs already
        if (
            self.protocol != "zip"
            and self._auto_open_archives
            and self._path.endswith(".zip")
            and self._fs.isfile(self._path)
        ):
            source_fs = self._fs
            source_url = self._path

            next_parent = cast(Self, type(self)(""))
            next_parent._path = self._path
            next_parent._fs = self._fs
            next_parent._parent = self._parent
            self._parent = next_parent

            # Open archive
            self._fs = fsspec.filesystem("zip", fo=source_fs.open(source_url))
            path = ""
            if self._trim_archive_component:
                path = self._get_archive_component()
            self._path = self._clean_path(path)

    def _get_archive_component(self) -> str:
        """
        Return the first component of the archive content
        """
        archive_content = self._fs.ls("", detail=False)
        if len(archive_content) != 1:
            return ""
        return archive_content[0]

    def __str__(self) -> str:
        """
        Extract full path
        """
        return self._path

    def __repr__(self) -> str:
        return (
            f"AnyPath({self.original_url}):"
            f"(fs={type(self._fs)}:{str(self._fs)}, "
            f"protocols={self.protocol_list()},path={self.path})"
        )

    @property
    def original_url(self) -> str:
        """
        Get the original url this anyPath was created with
        """
        return self._original_url

    @property
    def path(self) -> str:
        """
        Get path
        """
        return self._path

    @property
    def parent(self) -> Self | None:
        """
        Get parent filesystem
        """
        return self._parent

    @property
    def basename(self) -> str:
        """
        Return the path basename
        """
        return Path(self.path).name

    @property
    def absolute(self) -> str:
        """
        Return the path basename
        """
        return str(Path(self.path).resolve())

    def dirname(self) -> Self:
        """
        Returns the parent directory as a AnyPath instance
        """

        out = self.copy()
        out._path = os.path.dirname(self._path)

        return out

    @property
    def suffix(self) -> str:
        """
        Return the path suffix (shortest  extension)
        """
        return Path(self._path).suffix

    @property
    def suffixes(self) -> list[str]:
        """
        Return the path suffix (shortest  extension)
        """
        return Path(self._path).suffixes

    @property
    def protocol(self) -> str:
        """
        Return the protocol used by this path
        """
        protocol = self._fs.protocol
        if isinstance(protocol, list | tuple):
            if "local" in protocol:
                protocol = "local"
            else:
                protocol = protocol[0]
        return protocol

    @property
    def filesystem(self) -> Any:
        """
        Return the underlying fsspec filesystem
        Returns
        -------

        """
        return self._fs

    def copy(self) -> Self:
        """
        Return a copy of this object
        """
        out = type(self)("")
        out._original_url = self._original_url
        out._path = self._path
        out._fs = self._fs
        out._parent = self._parent
        out._tmp_dir = self._tmp_dir
        return out

    def rm(self, recursive: bool = False) -> None:
        """
        Delete the file/folders underneath

        """
        self._fs.rm(self._path, recursive=recursive)

    def _join(self, *args: str) -> str:
        """
        Join the given arguments using the filesystem separator. Takes care of trailing separators
        in the arguments.

        :return: Joined path
        """

        parts = [item for item in args if item]
        if len(parts) == 0:
            raise RuntimeError("No arguments to join")
        output = parts[0]
        sep = self.sep
        for item in parts[1:]:
            clean_item = item.strip("/")
            if not clean_item:
                continue
            if not output.endswith(sep):
                output += sep
            output += clean_item
        return output

    @property
    def sep(self) -> str:
        """
        Get separator for this filesystem
        """
        return self._fs.sep

    def exists(self) -> bool:
        """
        Check if path exists

        :return: True if path exists
        """
        return self._fs.exists(self._path)

    def isfile(self) -> bool:
        """
        Check if path is an existing file

        :return: True if path is an existing file
        """
        return self._fs.isfile(self._path)

    def isdir(self) -> bool:
        """
        Check if path is an existing directory

        :return: True if path is an existing directory
        """
        return self._fs.isdir(self._path)

    def iscompressed(self) -> bool:
        """
        Check if this filesystem is compressed
        """
        return self._fs.protocol in fsspec.available_compressions()

    def islocal(self) -> bool:
        """
        Check if the filesystem is local
        """
        return "file" in self._fs.protocol

    def __len__(self) -> int:
        """
        Get number of paths under me (directory entries or archive content)
        """
        if self.isdir():
            return len(self._fs.ls(self._path, detail=False))
        return 0

    def ls(self) -> list[Self]:
        """
        List any file under this path
        """

        output: list[Self] = []
        if self.isdir():
            for path in self._fs.ls(self._path, detail=False):
                item = self.copy()
                item._path = path
                item._detect_sub_filesystems()
                output.append(item)

        return output

    def __truediv__(self, other: Any) -> Self:
        """
        Join the current path with an other path
        """
        if isinstance(other, str):
            out = self.copy()
            out._path = self._join(self._path, other)
            return out
        return NotImplemented

    def mkdir(self, exist_ok: bool = False) -> Self:
        """
        Create the directory where I am pointing
        """
        if self.islocal():
            self._fs.makedirs(self._path, exist_ok=exist_ok)
        else:
            # Create a marker file to ensure the "folder" exists
            keep_file = self / ".keep"
            keep_file.touch()
        return self

    def touch(self) -> Self:
        """
        Create the directory where I am pointing
        """
        if not self.exists():
            self._fs.open(self._path, mode="w", create=True)
        return self

    def find(self, regex: str | None = None) -> list[Self]:
        """
        Find all files under me

        :param regex: Regular expression to filter results. This expression is joined after the current path
        :return: List of paths under me
        """
        output = []
        all_files = self._fs.find(self._path)
        path_regex = None
        if isinstance(regex, str):
            p = (PurePosixPath(self._path) / regex).as_posix()
            try:
                path_regex = re.compile(p)
            except re.error:
                # Windows regex path might fail to make the distinction
                # between the OS separator and regex escape sequences
                p = (Path(self._path) / regex).as_posix()
                path_regex = re.compile(p)

        for path in all_files:
            if path_regex and not path_regex.fullmatch(path):
                continue
            item = self.copy()
            item._path = path
            item._detect_sub_filesystems()
            output.append(item)
            # ~ return [AnyPath(item, parent=self) for item in all_files if path_regex.fullmatch(item)]

        # ~ return [AnyPath(item, parent=self) for item in all_files]
        return output

    def glob(self, pattern: str) -> list[Self]:
        """
        Find all files under me with a given pattern

        :param pattern: Globbing pattern to find files
        :return: List of matching paths
        """
        output = []
        for path in self._fs.glob(self._join(self._path, pattern)):
            item = self.copy()
            item._path = path
            item._detect_sub_filesystems()
            output.append(item)
        return output
        # ~ return [AnyPath(item, parent=self) for item in self._fs.glob(self._join(self._path, pattern))]

    def open(self, mode: str = "rb") -> Any:
        """
        Open the given path

        :param mode: Opening mode, like 'rb', 'w', ...
        :return: file-like object, suitable for 'with' block
        """
        return self._fs.open(self._path, mode=mode)

    def cat(self) -> bytes:
        """
        Read the file content to bytes
        """
        return self._fs.cat(self._path)

    def relpath(self, reference: Self) -> str:
        """
        Return the URL of the current object relative path to a reference

        :param reference: Reference path
        :return: relative path as string
        """
        return os.path.relpath(self._path, start=reference.path)

    def get(self, recursive: bool = False) -> Self:
        """
        Copy files to local storage (if needed) and return a Local Anypath Posix path
        Will unzip files also
        :param recursive: Recursively copy directory content
        :return: Path to local files
        """

        if self.islocal():
            return self

        if not self.exists():
            raise FileNotFoundError(f"Can't get the file  {self._path} as it doesn't exists")

        if self._tmp_dir is None:
            from eopf.common.temp_utils import EOLocalTemporaryFolder

            self._tmp_dir = cast(Self, EOLocalTemporaryFolder().get())

        self._fs.get(self._path, self._tmp_dir.path, recursive=recursive)

        if self.iscompressed():
            # If the file is compressed the get will uncompress it in this folder
            return self._tmp_dir
        return self._tmp_dir / self.basename

    def to_zarr_store(self) -> Store:
        """
        Convert this path object to a zarr.storage.FSStore encapsulated in LRU store to optimize S3 access
        """
        return FSStore(self._path, fs=self._fs)

    @classmethod
    def cast(cls, url: Any, **kwargs: dict[str, Any]) -> Self:
        """
        Cast method to convert any form of path to AnyPath

        :param url: Input path as a string, pathlib.PurePath, or AnyPath
        :param kwargs: Keyword arguments are passed to AnyPath constructor when url is a string,
            pathlib.PurePath is supposed to be local.
        """

        if isinstance(url, cls):
            return url
        if isinstance(url, PurePath):
            return cls(str(url))
        if isinstance(url, str):
            return cls(
                url,
                parent=None,
                trim_archive_component=True,
                auto_open_archives=True,
                **kwargs,
            )
        raise NotImplementedError(f"AnyPath.cast not implemented for {type(url)}")

    def __eq__(self, other: Any) -> bool:
        """
        Equality operator
        """

        obj = self.cast(other)

        return (
            self._path == obj._path
            and self._fs == obj._fs
            and self._original_url == obj._original_url
            and self._parent == obj._parent
        )

    def __hash__(self) -> int:
        """
        Compute the hash of the instance from path and filesystem
        """
        return hash((self._path, self._fs))

    def __lt__(self, other: Any) -> bool:
        """
        Comparison operator
        """
        obj = self.cast(other)
        if not self._fs == obj._fs:
            # Comparing filesystems using fsid would be better, but some implementations don't
            # implemented this property (ex. ZipFileSystem). Alternative could be to compare the hash.
            return self.protocol < obj.protocol
        return self._path < obj._path

    def info(self) -> dict[str, Any]:
        """
        Returns information on this file/folder (has to exist)
        """

        return self._fs.info(self._path)

    def protocol_list(self) -> list[str]:
        """
        Return the list of protocols used to access this path. It will recursively fetch the protocol
        from parent filesystems.
        """
        output = [self.protocol]
        if self._parent is not None:
            output += self._parent.protocol_list()
        return output

    def __add__(self, other: Any) -> Self:
        """
        Join the current path with an other path
        """
        if isinstance(other, str):
            out = self.copy()
            out._path = self._path + other
            return out
        return NotImplemented


def load_json_file(json_path: Union[str, AnyPath]) -> Any:
    """
    Load a json file and raise exception if not correctly read
    """
    json_path = AnyPath.cast(json_path)
    with json_path.open() as json_file:
        try:
            json_data = json.load(json_file)
            return json_data
        except json.JSONDecodeError as e:
            raise JSONParsingError(f"Error parsing json file {json_path} : {e}") from e


def check_for_substring(product_path: Union[str, AnyPath], pattern: str, text: str) -> bool:
    """Check if text is present in file at product/pattern location"""
    path = glob.glob(f"{product_path}/{pattern}")[0]
    with open(path, "r") as f:
        return text in f.read()


def replace_text_in_json(json_obj: Union[list[Any], dict[Any, Any]], text: str, replacement: str) -> Any:
    """Replace string in json object"""
    obj_str = json.dumps(json_obj).replace(text, replacement)
    return json.loads(obj_str)


def compute_json_size(adict: MutableMapping[str, Any]) -> int:
    """
    Compute the octet size of an exported dict to json

    Parameters
    ----------
    adict : dict to compute size of

    Returns
    -------
    Number of Bytes of the dict in json format
    """

    json_bytes = json.dumps(adict).encode("utf-8")

    # Get the size in octets
    size_in_octets = len(json_bytes)

    return size_in_octets


def load_yaml_file(yaml_path: Union[str, AnyPath]) -> Any:
    """
    Load a json file and raise exception if not correctly read
    """
    yaml_path = AnyPath.cast(yaml_path)
    with yaml_path.open() as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
        return yaml_data
