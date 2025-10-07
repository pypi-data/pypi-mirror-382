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

path_utils.py

Utilities to hand Path

"""
from typing import List, Optional


def join_path(*subpath: str, sep: str = "/") -> str:
    """Join elements from specific separator

    Parameters
    ----------
    *subpath: str
    sep: str, optional
        separator

    Returns
    -------
    str
    """
    return sep.join(subpath)


def regex_path_append(path1: Optional[str], path2: Optional[str]) -> Optional[str]:
    """Append two (valid) regex path.
    Can use os/eo path append as regex path syntax is different.
    """
    if path1 is not None:
        path1 = path1.removesuffix("/")
    if path2 is None:
        return path1
    path2 = path2.removeprefix("/")
    if path1 is None:
        return path2
    return f"{path1}/{path2}"


def remove_specific_extensions(path: str, exts: List[str]) -> str:
    for suffix in exts:
        path = path.removesuffix(suffix)
    return path


def add_extension(path: str, extension: str) -> str:
    return path + extension
