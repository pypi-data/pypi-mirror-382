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
dask_cluster_monitor.py

cluster state monitor

"""
import time
from enum import Flag, auto
from typing import Any, Dict, Mapping

from eopf import EOLogging
from eopf.common.type_utils import format_bytes
from eopf.dask_utils import dask_helpers


class ClusterState(Flag):
    """
    State flag enum
    """

    RUNNING = auto()
    PAUSED = auto()
    STUCK_SPILL = auto()
    STUCK_PROCESSING = auto()
    STUCK_MEMORY = auto()
    FAILURES = auto()
    NO_WORKERS = auto()
    OFFLINE = auto()


class DaskClusterMonitor:
    """
    Cluster monitor implementation
    """

    def __init__(
        self,
        grace_period: int = 30,
        memory_threshold: int = 90,
        max_cpu_threshold: int = 95,
        idle_threshold: int = 5,
    ) -> None:
        """
        constructor
        Parameters
        ----------
        grace_period : period to ignore state before reporting it to active
        memory_threshold : threshold to consider over ram usage
        max_cpu_threshold : max cpu to consider over cpu usage
        idle_threshold : threshold to declare worker idle stuck
        """
        self._logger = EOLogging().get_logger("eopf.dask_utils.dask_cluster_monitor")
        dask_client = dask_helpers.get_distributed_client()
        if dask_client is None:
            self._logger.info("No distributed client found, nothing to monitor")
        self._dask_client = dask_client
        self._grace_period = grace_period
        self._memory_threshold = memory_threshold
        self._max_cpu_threshold = max_cpu_threshold
        self._idle_threshold = idle_threshold
        self._cluster_state_log: Dict[ClusterState, float] = {}

    def check(self) -> ClusterState:
        """
        Check the current status of the cluster
        Returns
        -------
        The current status

        """
        # if client is none, we are not in a dask env
        if self._dask_client is None:
            return self._update_cluster_state(ClusterState.OFFLINE, 0)

        # if client is not in a running state
        if self._dask_client.status != "running":
            self._logger.warning("Dask client is not in a running state !!!!")

        # Check failures on scheduler
        failures = self._get_failures()
        if len(failures) != 0:
            self._logger.warning(f"Found error in tasks : {failures}")
            return self._update_cluster_state(ClusterState.FAILURES, 0)

        # Starting per worker analysis
        status = ClusterState.RUNNING
        snapshot = self._get_worker_snapshot()

        if len(snapshot) == 0:
            self._logger.warning("No workers found !!!!")
            return self._update_cluster_state(ClusterState.NO_WORKERS, 0)

        # Check paused workers
        status = self._check_paused_workers(snapshot, status)

        # Check stuck spilling
        status = self._check_stuck_spilling_workers(snapshot, status)

        # Check high memory workers
        status = self._check_high_memory_usage(snapshot, status)

        # Check high processing workers
        status = self._check_high_cpu_workers(snapshot, status)

        return self._update_cluster_state(status, self._grace_period)

    def _update_cluster_state(self, new_state: ClusterState, grace_period: int) -> ClusterState:
        """
        Internal routine to update the state

        Parameters
        ----------
        new_state
        grace_period

        Returns
        -------

        """
        # Add new states with current time
        for state in ClusterState:
            if state in new_state and state not in self._cluster_state_log:
                self._cluster_state_log[state] = time.time()
            elif state not in new_state and state in self._cluster_state_log:
                del self._cluster_state_log[state]  # State cleared
        # Cluster state is the combination of those that have been up more than grace period
        final_state = ClusterState.RUNNING
        for state, timestamp in self._cluster_state_log.items():
            if time.time() - timestamp >= grace_period:
                final_state |= state
                # If anything overrides the normal run, you can unset RUNNING
        if final_state != ClusterState.RUNNING:
            final_state &= ~ClusterState.RUNNING
        return final_state

    def _get_failures(self) -> list[Any]:
        """
        Get the list of failed tasks from the scheduler

        warning : if someone else is using the same scheduler you'll also have their errors

        """
        if self._dask_client is not None and self._dask_client.status == "running":
            failed_task = self._dask_client.run_on_scheduler(
                lambda dask_scheduler: (
                    dask_scheduler.plugins["failure-monitor"].failed_tasks
                    if "failure-monitor" in dask_scheduler.plugins
                    else None
                ),
            )
            return failed_task
        return []

    def _get_worker_snapshot(self) -> Mapping[str, Any]:
        """
        Dask worker infos adapter pattern

        Returns
        -------
        The worker infos concatenated
        """
        snapshot = {}

        if self._dask_client is not None:
            info = self._dask_client.scheduler_info().get("workers", {})
            for addr, stats in info.items():
                metrics = stats.get("metrics", {})
                spilled = metrics.get("spilled_bytes", {})
                snapshot[addr] = {
                    "spilled_memory_bytes": spilled.get("memory", 0),
                    "spilled_disk_bytes": spilled.get("disk", 0),
                    "cpu": metrics.get("cpu", 0.0) / stats.get("nthreads", 1.0),
                    "task_counts": metrics.get("task_counts", {}),
                    "memory": metrics.get("memory", 1.0),
                    "memory_limit": stats.get("memory_limit", 1.0),
                    "memory_ratio": metrics.get("memory", 1.0) * 100.0 / stats.get("memory_limit", 1.0),
                    "timestamp": time.time(),
                    "status": stats.get("status"),
                    "event_loop": metrics.get("event_loop_interval", 0),
                    "last_seen": stats.get("last_seen", time.time()),
                }
        return snapshot

    def _check_stuck_spilling_workers(self, snapshot: Mapping[str, Any], prev_status: ClusterState) -> ClusterState:
        """
        Detect stuck workers in spill

        Parameters
        ----------
        snapshot : workers info
        prev_status : previous state

        Returns
        -------
        New state

        """
        stucks = []

        for addr, stats in snapshot.items():
            spilled = stats["spilled_disk_bytes"]
            if (
                spilled > 0
                and stats["task_counts"].get("executing", 0) == 0
                and (stats["cpu"] < self._idle_threshold or stats["status"] == "paused")
            ):
                self._logger.warning(f"Possible stuck spill: {addr} (spilled {format_bytes(spilled)})")
                stucks.append(addr)
        if len(stucks) == len(snapshot):
            self._logger.warning("All workers are stucks !!!!")
            return prev_status | ClusterState.STUCK_SPILL
        return prev_status

    def _check_high_cpu_workers(self, snapshot: Mapping[str, Any], prev_status: ClusterState) -> ClusterState:
        """
        Detect high cpu workers

        Parameters
        ----------
        snapshot: workers  info
        prev_status: previous state

        Returns
        -------
        New state
        """
        highs = []

        for addr, stats in snapshot.items():
            cpu = stats["cpu"]
            if cpu > self._max_cpu_threshold and stats["task_counts"].get("executing", 0) != 0:
                self._logger.warning(f"Possible high cpu usage: {addr} (cpu {cpu})")
                highs.append(addr)
        if len(highs) == len(snapshot):
            self._logger.warning("All workers are in high processing !!!!")
            return prev_status | ClusterState.STUCK_PROCESSING
        return prev_status

    def _check_paused_workers(self, snapshot: Mapping[str, Any], prev_status: ClusterState) -> ClusterState:
        """
        Detect paused workers

        Parameters
        ----------
        snapshot: workers  info
        prev_status: previous state

        Returns
        -------
        New state
        """
        paused = []
        for addr, stats in snapshot.items():
            if stats["status"] == "paused":
                paused.append(addr)
        if len(paused) == len(snapshot):
            self._logger.warning("All workers are paused !!!!")
            return prev_status | ClusterState.PAUSED
        return prev_status

    def _check_high_memory_usage(self, snapshot: Mapping[str, Any], prev_status: ClusterState) -> ClusterState:
        """
        Detect high memory usage on workers

        Parameters
        ----------
        snapshot
        prev_status

        Returns
        -------

        """
        high_mem_workers = []
        for addr, stats in snapshot.items():
            mem_pct = stats.get("memory_ratio", 0)
            if mem_pct > self._memory_threshold:
                self._logger.warning(f"High memory usage: {addr} ({mem_pct:.1f}%)")
                high_mem_workers.append(addr)
        if len(high_mem_workers) == len(snapshot):
            self._logger.warning("All workers are in high memory usage !!!!")
            return prev_status | ClusterState.STUCK_MEMORY
        return prev_status
