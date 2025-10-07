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
eopf.computing module provide to re-engineered processor developers a
homogeneous API implementing advanced parallelism features whatever the execution context: HPC, Cloud or local.

"""

from eopf.computing.abstract import (
    ADF,
    AuxiliaryDataFile,
    DataType,
    EOProcessingStep,
    EOProcessingUnit,
    MappingAuxiliary,
    MappingDataType,
)
from eopf.computing.breakpoint import declare_as_breakpoint, eopf_breakpoint_decorator
from eopf.computing.overlap import map_overlap

__all__ = [
    "EOProcessingStep",
    "EOProcessingUnit",
    "MappingDataType",
    "DataType",
    "AuxiliaryDataFile",
    "MappingAuxiliary",
    "ADF",
    "eopf_breakpoint_decorator",
    "declare_as_breakpoint",
    "map_overlap",
]
