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

The accessor package provides accessor that allow reading and writing the data from files.

All accessor are based on the main abstract EOAccessor class.
"""
from eopf.accessor.abstract import EOAccessor
from eopf.accessor.accessor_factory import EOAccessorFactory
from eopf.accessor.attribute_to_flag_var import (
    FromAttributesToFlagValueAccessor,
    FromAttributesToVariableAccessor,
)
from eopf.accessor.filename_to_variable import (
    FilenameToVariableAccessor,
    PathToAttrAccessor,
)
from eopf.accessor.grib import EOGribAccessor
from eopf.accessor.memmap_accessors import (
    FixedMemMapAccessor,
    MemMapAccessor,
    MultipleFilesMemMapAccessor,
)
from eopf.accessor.netcdf_accessors import (
    EONetCDFDAttrAccessor,
    EONetCDFDimensionAccessor,
)
from eopf.accessor.rasterio import (
    EOFoldedMultiSourceRasterIOAccessor,
    EOMultiSourceRasterIOAccessor,
    EORasterIOAccessor,
)
from eopf.accessor.xml_accessors import (
    XMLAnglesAccessor,
    XMLManifestAccessor,
    XMLMultipleFilesAccessor,
    XMLTPAccessor,
)

__all__ = [
    "EOAccessor",
    "EOAccessorFactory",
    "EONetCDFDimensionAccessor",
    "XMLManifestAccessor",
    "XMLAnglesAccessor",
    "XMLTPAccessor",
    "EOGribAccessor",
    "EORasterIOAccessor",
    "FromAttributesToVariableAccessor",
    "FromAttributesToFlagValueAccessor",
    "MemMapAccessor",
    "FixedMemMapAccessor",
    "FilenameToVariableAccessor",
    "PathToAttrAccessor",
    "EOMultiSourceRasterIOAccessor",
    "XMLMultipleFilesAccessor",
    "EOFoldedMultiSourceRasterIOAccessor",
    "MultipleFilesMemMapAccessor",
    "EONetCDFDAttrAccessor",
]
