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
interfaces.py


dataclasses interfaces between parsers and runner

"""


import enum
from dataclasses import dataclass
from typing import Any, List, Optional, Type

from eopf import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.store import EOProductStore


class PathType(enum.Enum):
    Filename = "filename"
    Folder = "folder"
    Regex = "regex"


@dataclass
class EOBreakPointParserResult:
    ids: list[str]
    all: bool
    folder: str
    store_params: dict[str, Any]


@dataclass
class EOExternalModuleImportParserResult:
    """
    External module datatclass
    """

    name: str
    alias: Optional[str]
    nested: bool
    folder: str


@dataclass
class EOOutputProductParserResult:
    """
    Output product dataclass
    """

    id: str
    store_class: Type[EOProductStore]
    path: AnyPath
    type: PathType
    opening_mode: OpeningMode
    store_type: str
    store_params: dict[str, Any]
    apply_eoqc: bool


@dataclass
class EOInputProductParserResult:
    """
    Input product dataclass
    """

    id: str
    store_class: Type[EOProductStore]
    path: AnyPath
    type: PathType
    store_type: str
    store_params: dict[str, Any]


@dataclass
class EOADFStoreParserResult:
    id: str
    path: AnyPath
    store_params: dict[str, Any]


@dataclass
class EOIOParserResult:
    output_products: list[EOOutputProductParserResult]
    input_products: list[EOInputProductParserResult]
    adfs: list[EOADFStoreParserResult]


@dataclass
class EOQCTriggeringConf:
    config_folders: List[str] | None
    parameters: dict[str, Any] | None
    update_attrs: bool
    report_path: str | None
