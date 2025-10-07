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
dask_utils module

Handles all interactions with dask
"""

from eopf.dask_utils.dask_cluster_type import ClusterType
from eopf.dask_utils.dask_context_manager import DaskContext
from eopf.dask_utils.dask_context_utils import init_from_eo_configuration

__all__ = ["DaskContext", "init_from_eo_configuration", "ClusterType"]
