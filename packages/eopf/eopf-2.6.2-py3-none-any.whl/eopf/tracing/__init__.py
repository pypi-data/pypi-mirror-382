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
"""The objective of the eopf.tracing module is to provide a simple and homogeneous interface to the tracing system.
We further divide tracing in two: function-based tracing and continuous tracing.

For function-based tracing we provide the developers two parameterizable decorators,
which are meant to give parallel processing feedback (through dask) and single thread profiling (through pstats).
Thus, the developer can easily trace the performance of its code in distributed and non-distributed environments.
The dask_profiler generates a dask provided html report which can be saved to a configurable location.
Also, it provides the developer the ability to run on an already defined dask cluster or on a configurable cluster.
The single_thread_profiler generates and returns a pstats object with multiple function-based statistics.
The statistics can be easily manipulated and filtered, for better insight.
The pstats object can also be saved to a configurable location,

Since dask is used as base for all eopf-cpm computations,
we refer the developers and users to the standard dask dashboard as the standard continuous tracing method.
Nevertheless, we also recommended using Prometheus for monitoring dask performance over time.
We provide a default Prometheus configuration file, i.e. prometheus-cpm.yml , within then eopf.tracing folder,
for rapid configuration.
"""

from eopf.dask_utils.profiler import single_thread_profiler
from eopf.tracing.progress import EOProgress, distributed_progress, local_progress

__all__ = ["single_thread_profiler", "local_progress", "distributed_progress", "EOProgress"]
