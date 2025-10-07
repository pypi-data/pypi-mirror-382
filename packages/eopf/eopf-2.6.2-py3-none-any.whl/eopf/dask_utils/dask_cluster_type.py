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
dask_cluster_type.py

List of possible dask cluster type

"""
from enum import Enum


class ClusterType(Enum):
    """
    Cluster type enum
    """

    LOCAL = "local"
    SSH = "ssh"
    KUBERNETES = "kubernetes"
    PBS = "pbs"
    SGE = "sge"
    LSF = "lsf"
    SLURM = "slurm"
    YARN = "yarn"
    GATEWAY = "gateway"
    ADDRESS = "address"
    CUSTOM = "custom"


def get_enum_from_value(value: str) -> ClusterType:
    """
    Get the corresponding enum from value

    Parameters
    ----------
    value

    Returns
    -------
    the cluster type

    Raises
    ---------
    ValueError if not founc

    """
    for member in ClusterType:
        if member.value == value:
            return member
    raise ValueError("Value not found in the enum")
