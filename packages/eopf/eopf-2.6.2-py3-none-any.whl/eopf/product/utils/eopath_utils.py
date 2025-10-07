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
eopath_utils.py

eopath ( posix path applied to eo objects)

"""
import posixpath
from pathlib import PurePosixPath
from typing import Optional

from eopf.exceptions.errors import EOPathError

# We need to use a mix of posixpath (normpath) and pathlib (partition) in the eo_path methods.
# As we work with strings we use posixpath (the unix path specific implementation of os.path) as much as possible.


def downsplit_eo_path(eo_path: str) -> tuple[str, Optional[str]]:
    """Extract base path and sub path

    Parameters
    ----------
    eo_path: str

    Returns
    -------
    str
        folder name
    str or None
        sub path
    """
    folder_name = partition_eo_path(eo_path)[0]
    sub_path: Optional[str] = posixpath.relpath(eo_path, start=folder_name)
    if sub_path == ".":
        sub_path = None
    return folder_name, sub_path


def is_absolute_eo_path(eo_path: str) -> bool:
    """Check if the given path is absolute or not

    Parameters
    ----------
    eo_path: str

    Returns
    -------
    bool
    """
    eo_path = norm_eo_path(eo_path)
    first_level, _ = downsplit_eo_path(eo_path)
    return first_level in ["/", ".."]


def join_eo_path(*subpaths: str) -> str:
    """Join eo object paths.

    Parameters
    ----------
    *subpaths: str

    Returns
    -------
    str
    """
    return norm_eo_path(posixpath.join(*subpaths))


def join_eo_path_optional(*subpaths: Optional[str]) -> str:
    """Join eo object paths.

    Parameters
    ----------
    *subpaths: str

    Returns
    -------
    str
    """
    valid_subpaths = [path for path in subpaths if path]
    if not valid_subpaths:
        return ""
    return join_eo_path(*valid_subpaths)


def remove_leading_char(in_str: str, chars: str = "/") -> str:
    """
    Remove leading specified character(s) from a string.

    Parameters
    ----------
    in_str : str
        The input string from which leading character(s) need to be removed.
    chars : str, optional
        The specified character(s) to be removed from the beginning of the string.
        Default is '/'.

    Returns
    -------
    str
        The modified string with leading specified character(s) removed.

    Examples
    --------
    >>> remove_leading_char("//example/path", "/")
    'example/path'

    """
    while in_str.startswith(chars):
        in_str = in_str[len(chars) :]
    return in_str


def norm_eo_path(eo_path: str) -> str:
    """Normalize an eo object path.

    Parameters
    ----------
    eo_path: str

    Returns
    -------
    str
    """
    if eo_path == "":
        raise EOPathError("Invalid empty eo_path")
    # Do not use pathlib (does not remove ..)
    eo_path = posixpath.normpath(eo_path)
    # text is a special path so it's not normalised by normpath
    if eo_path.startswith("//"):
        return eo_path[1:]
    return eo_path


def partition_eo_path(eo_path: str) -> tuple[str, ...]:
    """Extract each elements of the eo_path

    Parameters
    ----------
    eo_path: str

    Returns
    -------
    tuple[str, ...]
    """
    return PurePosixPath(eo_path).parts


def product_relative_path(eo_context: str, eo_path: str) -> str:
    """Return eo_path relative to the product (an absolute path without the leading /).

    Parameters
    ----------
    eo_context: str
        base path context
    eo_path: str

    Returns
    -------
    str
    """
    absolute_path = join_eo_path(eo_context, eo_path)
    first_level_relative_path = downsplit_eo_path(absolute_path)[1]
    if first_level_relative_path is None:
        return ""
    return first_level_relative_path


def upsplit_eo_path(eo_path: str) -> tuple[str, ...]:
    """Split the given path

    Parameters
    ----------
    eo_path: str

    Returns
    -------
    tuple[str, ...]
    """
    return posixpath.split(eo_path)
