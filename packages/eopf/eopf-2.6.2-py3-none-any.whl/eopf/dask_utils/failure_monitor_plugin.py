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
failure_monitor_plugin.py

Dask worker plugin to detect failures in task


"""
from typing import TYPE_CHECKING, Any, Tuple

from dask.typing import Key
from distributed import SchedulerPlugin

if TYPE_CHECKING:
    from distributed.scheduler import TaskStateState as SchedulerTaskStateState


class FailureMonitorPlugin(SchedulerPlugin):
    """
    Dask scheduler plugin to detect failed task

    Warnings : These failure might not be yours if multiple users of the cluster

    """

    def __init__(self) -> None:
        self.failed_tasks: list[Tuple[Key, Any]] = []

    def transition(
        self,
        key: Key,
        start: "SchedulerTaskStateState",
        finish: "SchedulerTaskStateState",
        *args: Any,
        stimulus_id: str,
        **kwargs: Any,
    ) -> None:
        """
        transition function

        Parameters
        ----------
        key
        start
        finish
        args
        stimulus_id
        kwargs

        Returns
        -------

        """

        if finish == "erred":
            exception = kwargs.get("exception", None)
            self.failed_tasks.append((key, exception))

    def get_failed_tasks(self) -> list[Tuple[Key, Any]]:
        """Return the list of failed tasks."""
        return self.failed_tasks
