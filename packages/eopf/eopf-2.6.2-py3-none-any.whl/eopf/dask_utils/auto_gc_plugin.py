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
auto_gc_plugin.py

Dask worker plugin to trigger garbage collect

"""
import gc
from typing import TYPE_CHECKING, Any

from dask.typing import Key
from distributed import WorkerPlugin

if TYPE_CHECKING:
    from distributed.worker_state_machine import TaskStateState as WorkerTaskStateState


class AutoGCPlugin(WorkerPlugin):
    """
    Dask worker plugin to automaticcaly garbage collect at end of processing
    """

    def transition(
        self,
        key: Key,
        start: "WorkerTaskStateState",
        finish: "WorkerTaskStateState",
        **kwargs: Any,
    ) -> None:
        """Run GC when tasks move from 'processing' to 'memory' or 'erred'."""
        if start == "processing" and finish in {"memory", "erred"}:
            gc.collect()
