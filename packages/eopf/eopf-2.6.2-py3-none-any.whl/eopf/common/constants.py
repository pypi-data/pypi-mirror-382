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
constants.py

hold the constants and enums of the project
"""

from enum import Enum
from typing import Any

import numpy as np
from xarray.backends import zarr

import eopf
from eopf.common.file_utils import AnyPath


class OpeningInfo:
    """
    Opening mode retainer
    """

    def __init__(self, str_mode: str) -> None:
        """
        OpeningInfo enum, kind of useless if using standard r,w etc
        Parameters
        ----------
        str_mode
        """
        self._file_opening_mode: str = str_mode

    def __repr__(self) -> str:
        """
        Representation is the opening mode str
        Returns
        -------

        """
        return self.file_opening_mode

    @property
    def file_opening_mode(self) -> str:
        return self._file_opening_mode


class OpeningMode(Enum):
    """
    Opening mode retainer
    """

    CREATE = OpeningInfo("w")
    CREATE_OVERWRITE = OpeningInfo("w+")
    CREATE_NO_OVERWRITE = OpeningInfo("w-")
    OPEN = OpeningInfo("r")
    UPDATE = OpeningInfo("r+")
    APPEND = OpeningInfo("a")

    @classmethod
    def cast(cls, value: Any) -> "OpeningMode":
        """
        Cast the value to an opening mode
        Transition to go from OpeningMode to simple rw str
        Parameters
        ----------
        value

        Returns
        -------

        """
        if isinstance(value, OpeningMode):
            return value
        if isinstance(value, str):
            return OpeningMode.from_standard_str_mode(value)
        raise NotImplementedError(f"Construction of OpeningMode from {type(value)} is not implemented")

    @classmethod
    def from_standard_str_mode(cls, mode: str) -> "OpeningMode":
        """
        Get the corresponding standard mode
        Parameters
        ----------
        mode : str, r w etc

        Returns
        -------
        The corresponding mode
        """
        for v in OpeningMode:
            if v.value.file_opening_mode == mode:
                return v
        raise ValueError(f"Mode {mode} is not available in OpeningMode")


class ProductType(Enum):
    """
    Product Type enum
    """

    S01SEWGRD = "S01SEWGRD"
    S01SEWRAW = "S01SEWRAW"
    S01SEWSLC = "S01SEWSLC"
    S01SIWGRD = "S01SIWGRD"
    S01SIWOCN = "S01SIWOCN"
    S01SIWRAW = "S01SIWRAW"
    S01SIWSLC = "S01SIWSLC"
    S01SSMGRD = "S01SSMGRD"
    S01SSMOCN = "S01SSMOCN"
    S01SSMRAW = "S01SSMRAW"
    S01SSMSLC = "S01SSMSLC"
    S01SWVGRD = "S01SWVGRD"
    S01SWVRAW = "S01SWVRAW"
    S01SWVSLC = "S01SWVSLC"
    S02MSIL0_ = "S02MSIL0_"
    S02MSIL1C = "S02MSIL1C"
    S02MSIL2A = "S02MSIL2A"
    S03AHRL1B = "S03AHRL1B"
    S03AHRL2H = "S03AHRL2H"
    S03ALTL0_ = "S03ALTL0_"
    S03MWRL0_ = "S03MWRL0_"
    S03OLCEFR = "S03OLCEFR"
    S03OLCERR = "S03OLCERR"
    S03OLCL0_ = "S03OLCL0_"
    S03OLCLFR = "S03OLCLFR"
    S03SLSFRP = "S03SLSFRP"
    S03SLSL0_ = "S03SLSL0_"
    S03SLSLST = "S03SLSLST"
    S03SLSRBT = "S03SLSRBT"
    S03SYNSDR = "S03SYNSDR"


class Style:
    """
    Base class holding the style in rendering text

    inspired by datatree_render in xarray datatree

    """

    def __init__(self) -> None:
        """
        Tree Render Style.
        Args:
            vertical: Sign for vertical line.
            cont: Chars for a continued branch.
            end: Chars for the last branch.
        """
        super().__init__()
        self.vertical = "\u2502   "
        self.cont = "\u251c\u2500\u2500 "
        self.end = "\u2514\u2500\u2500 "
        self.empty = "    "
        if len(self.cont) != len(self.vertical) != len(self.end) != len(self.empty):
            raise ValueError(
                f"'{self.vertical}', '{self.cont}', '{self.empty}' and '{self.end}' need to have equal length",
            )


VALID_MIN = "valid_min"
VALID_MAX = "valid_max"
FILL_VALUE = "fill_value"
ADD_OFFSET = "add_offset"
SCALE_FACTOR = "scale_factor"
DTYPE = "dtype"
LONG_NAME = "long_name"
STANDARD_NAME = "standard_name"
SHORT_NAME = "short_name"
COORDINATES = "coordinates"
UNITS = "units"
FLAG_VALUES = "flag_values"
FLAG_MASKS = "flag_masks"
FLAG_MEANINGS = "flag_meanings"
DIMENSIONS = "dimensions"
# xarray and zarr dimensions must be identical for compatibility.
DIMENSIONS_NAME = zarr.DIMENSION_KEY
# xarray uses _FillValue for fill_value
XARRAY_FILL_VALUE = "_FillValue"
TARGET_DTYPE = "eopf_target_dtype"
EOV_IS_SCALED = "eopf_is_scaled"
EOV_IS_MASKED = "eopf_is_masked"
ZARR_EOV_ATTRS = "_eopf_attrs"
EOPF_CATEGORY_ATTR = "eopf_category"
EOPRODUCT_CATEGORY = "eoproduct"
EOCONTAINER_CATEGORY = "eocontainer"
UNKNOWN_CATEGORY = "unknown"
NO_PATH_MATCH = "NO FILE/DIR MATCH"

EOPF_CPM_PATH = AnyPath.cast(eopf.__path__[0])
EOPF_CPM_DEFAULT_CONFIG_FILE = EOPF_CPM_PATH / "config" / "default" / "eopf.toml"
EOPF_CPM_TESTS_PATH = EOPF_CPM_PATH.dirname() / "tests"

ROOT_PATH_DATATREE = "/"

# Group types together so that differences in types within these groups are ignored when comparring with DeepDiff
DEEP_DIFF_IGNORE_TYPE_IN_GROUPS = [
    # Grouping integer types with int
    (int, np.int_, np.int8, np.int16, np.int32, np.int64),
    # Grouping unsigned integer types with int
    (int, np.uint8, np.uint16, np.uint32, np.uint64),
    # Grouping floating-point types with float
    (float, np.float16, np.float32, np.float64),
    # Grouping complex number types with complex
    (complex, np.complex64, np.complex128),
]

PROCESSING_HISTORY_UNKNOWN_MARKER = "Unknown"
PROCESSING_HISTORY_UNKNOWN_TIME_MARKER = "1970-01-01T00:00:00.000000Z"
PROCESSING_HISTORY_ATTR = "processing_history"
PROCESSING_HISTORY_PROCESSOR_FIELD = "processor"
PROCESSING_HISTORY_VERSION_FIELD = "version"
PROCESSING_HISTORY_FACILITY_FIELD = "facility"
PROCESSING_HISTORY_TIME_FIELD = "time"
PROCESSING_HISTORY_ADFS_FIELD = "adfs"
PROCESSING_HISTORY_INPUTS_FIELD = "inputs"
PROCESSING_HISTORY_OUTPUTS_FIELD = "outputs"
PROCESSING_HISTORY_EXECUTION_PARAMETERS_FIELD = "execution_parameters"
PROCESSING_HISTORY_EOPF_CPM_VERSION_FIELD = "eopf_cpm_version"
PROCESSING_HISTORY_EOPF_ASGARD_VERSION_FIELD = "eopf_asgard_version"
PROCESSING_HISTORY_EOPF_PYTHON_VERSION_FIELD = "eopf_python_version"
PROCESSING_HISTORY_OUTPUT_LEVEL_PATTERN = r"^Level-\d.*Product$"
PROCESSING_HISTORY_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
PROCESSING_HISTORY_MANDATORY_FIELDS = [
    PROCESSING_HISTORY_PROCESSOR_FIELD,
    PROCESSING_HISTORY_VERSION_FIELD,
    PROCESSING_HISTORY_FACILITY_FIELD,
    PROCESSING_HISTORY_TIME_FIELD,
    PROCESSING_HISTORY_INPUTS_FIELD,
    PROCESSING_HISTORY_OUTPUTS_FIELD,
]
PROCESSING_HISTORY_OPTIONAL_FIELDS = [
    PROCESSING_HISTORY_ADFS_FIELD,
    PROCESSING_HISTORY_EOPF_CPM_VERSION_FIELD,
    PROCESSING_HISTORY_EOPF_ASGARD_VERSION_FIELD,
    PROCESSING_HISTORY_EOPF_PYTHON_VERSION_FIELD,
    PROCESSING_HISTORY_EXECUTION_PARAMETERS_FIELD,
]
